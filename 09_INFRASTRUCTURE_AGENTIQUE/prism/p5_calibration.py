"""Replay one public case through P5 with a simulated provider and blind ratings."""
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from unittest.mock import patch

from analysis import ARMS, analyze_files
from evaluation import DIMENSIONS
from p5_dispatch import DispatchLedger
from planner import ROLE_ORDER, ROLE_QUESTIONS, plan_mission

CASE_ID = "P5V2-FORMAL-001"
EXPERIMENT = "p5-public-calibration-simulated"
BUDGET = {"calls": 2, "tokens": 256, "seconds": 2.0, "tools": 0}


class CalibrationError(ValueError):
    """A budget or dispatch reconciliation check failed."""


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def call_identity(row):
    return tuple(row[field] for field in (
        "experiment_id", "case_id", "arm", "repetition", "operation_id", "attempt", "call_id"
    ))


def reconcile(dispatch, records):
    from telemetry import summarize_calls

    expected = set(dispatch)
    observed = {call_identity(row) for row in records}
    if len(expected) != len(dispatch) or len(observed) != len(records):
        raise CalibrationError("duplicate dispatch or telemetry identity")
    if expected != observed:
        raise CalibrationError(
            f"dispatch mismatch: missing={sorted(expected - observed)}, "
            f"unexpected={sorted(observed - expected)}"
        )
    return summarize_calls(records, by_execution=True)["execution_summaries"]


def run_arm(arm, prompt, route, provider, dispatch, records, *, ledger=None):
    from openai_responses_adapter import build_openai_responses_record

    remaining_tokens = BUDGET["tokens"]
    remaining_seconds = BUDGET["seconds"]
    for attempt in range(1, BUDGET["calls"] + 1):
        if remaining_tokens <= 0 or remaining_seconds <= 0:
            break
        call_id = f"calibration-{arm}-{attempt}"
        identity = (EXPERIMENT, CASE_ID, arm, 1, "generate", attempt, call_id)
        recovered = ledger.recover_payload(identity) if ledger is not None else None
        dispatch.append(identity)
        if recovered is not None:
            record = recovered["row"]
            elapsed, tools = record["elapsed_seconds"], record["tool_calls"]
            if (record["prompt_sha256"] != digest(prompt)
                    or record["routing_decision_sha256"] != digest(route)):
                raise CalibrationError("stored attempt used a different prompt or route")
        else:
            if ledger is not None:
                ledger.reserve(identity)
            response, elapsed, tools = provider(
                arm, attempt, prompt, max_tokens=remaining_tokens,
                timeout=remaining_seconds, max_tools=BUDGET["tools"],
            )
            record = build_openai_responses_record(
                response, experiment_id=EXPERIMENT, case_id=CASE_ID, arm=arm, call_id=call_id,
                started_at="2026-01-01T00:00:00Z", elapsed_seconds=elapsed, tool_calls=tools,
                context={"repetition": 1, "operation_id": "generate", "attempt": attempt,
                         "prompt_sha256": digest(prompt), "routing_decision_sha256": digest(route)},
            )
        records.append(record)
        if record["input_tokens"] is None or record["output_tokens"] is None or tools is None:
            raise CalibrationError("budget consumption unknown")
        remaining_tokens -= record["input_tokens"] + record["output_tokens"]
        remaining_seconds -= elapsed
        if remaining_tokens < 0 or remaining_seconds < 0 or tools > BUDGET["tools"]:
            raise CalibrationError("execution exceeded its budget")
        if ledger is not None and recovered is None:
            payload = response if isinstance(response, dict) else response.model_dump(mode="json")
            ledger.finish_payload(identity, record, payload)
        if record["status"] == "completed":
            return
        if record["status"] != "interrupted":
            raise CalibrationError("unexpected status in simulated execution")
    raise CalibrationError("arm exhausted its budget without a completed output")


def simulated_provider(arm, attempt, prompt, *, max_tokens, timeout, max_tools):
    interrupted = arm == "C" and attempt == 1
    input_tokens = 48 + 8 * len(prompt["perspectives"])
    output_tokens = 4 if interrupted else 20
    if input_tokens + output_tokens > max_tokens or timeout < 0.25 or max_tools != 0:
        raise CalibrationError("simulated provider cannot honor the remaining budget")
    return ({
        "status": "incomplete" if interrupted else "completed",
        "model": "simulated-p5-v1",
        "output_text": None if interrupted else "Réponse synthétique de calibration.",
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }, 0.25, 0)


def checked_analysis(dispatch, records, notes, key, output, ratings_sha256, *, ledger=None):
    if ledger is not None:
        ledger.verify_results(records)
    summaries = reconcile(dispatch, records)
    report = analyze_files(
        notes, key, output, expected_case_ids={CASE_ID}, ratings_sha256=ratings_sha256,
    )
    return {"mode": "public_calibration_simulated", "budget_per_arm": BUDGET,
            "executions": summaries, "ratings": report}


def exercise(provider=simulated_provider):
    with TemporaryDirectory() as directory:
        return _exercise(provider, DispatchLedger(Path(directory) / "events.jsonl", EXPERIMENT))


def _exercise(provider, ledger):
    cases = Path(__file__).resolve().parents[1] / "evaluation/holdout_v0_2/cases.jsonl"
    case = next(row for row in map(json.loads, cases.read_text(encoding="utf-8").splitlines())
                if row["case_id"] == CASE_ID)
    plan = plan_mission({"question": case["prompt"], "mission_type": "mathematical"})
    routes = {
        "A": [],
        "B": [{"role": role, "question": ROLE_QUESTIONS[role]} for role in ROLE_ORDER],
        "C": plan["tasks"],
    }
    order = list(ARMS)
    Random(505).shuffle(order)
    records, dispatch = [], []
    for arm in order:
        route = routes[arm]
        perspectives = [{field: item[field] for field in ("role", "question")} for item in route]
        run_arm(arm, {"question": case["prompt"], "perspectives": perspectives}, route,
                provider, dispatch, records, ledger=ledger)

    mappings, ratings = [], []
    for index, arm in enumerate(reversed(order)):
        opaque = f"opaque-{index}"
        mappings.append({"case_id": CASE_ID, "blind_output_id": opaque, "arm": arm})
        for evaluator in ("synthetic-1", "synthetic-2"):
            ratings.append({
                "case_id": CASE_ID, "blind_output_id": opaque, "evaluator_id": evaluator,
                "scores": dict.fromkeys(DIMENSIONS, 2), "unsupported_claims": 0,
                "material_errors": 0, "missed_counterexamples": 0,
                "elapsed_seconds": None, "tool_calls": None,
            })

    with TemporaryDirectory() as directory:
        notes, key, output = (Path(directory) / name for name in ("notes.jsonl", "key.json", "report.json"))
        notes.write_text("".join(json.dumps(row) + "\n" for row in ratings), encoding="utf-8")
        key.write_text(json.dumps({"mappings": mappings}), encoding="utf-8")
        args = notes, key, output, sha256(notes.read_bytes()).hexdigest()
        retained = [row for row in records if row["call_id"] != "calibration-C-1"]
        if {row["arm"] for row in retained} != set(ARMS):
            raise CalibrationError("fault injection must retain every arm")
        with patch("analysis.load_blind_key") as read_key:
            try:
                checked_analysis(dispatch, retained, *args)
            except CalibrationError as exc:
                if "calibration-C-1" not in str(exc):
                    raise
            else:
                raise CalibrationError("missing call was accepted")
            read_key.assert_not_called()
        if output.exists():
            raise CalibrationError("analysis was written despite the missing call")
        report = checked_analysis(dispatch, records, *args, ledger=ledger)

    retry = next(row for row in report["executions"] if row["arm"] == "C")
    if retry["status_counts"] != {"completed": 1, "interrupted": 1}:
        raise CalibrationError("retry was not preserved")
    def over_budget(*args, **kwargs):
        response, elapsed, tools = simulated_provider(*args, **kwargs)
        response["usage"]["output_tokens"] = kwargs["max_tokens"] + 1
        return response, elapsed, tools

    for arm in ARMS:
        try:
            run_arm(arm, {"question": case["prompt"], "perspectives": []}, [],
                    over_budget, [], [])
        except CalibrationError as exc:
            if str(exc) != "execution exceeded its budget":
                raise
        else:
            raise CalibrationError(f"{arm} accepted a token budget overrun")

    report["checks"] = {
        "token_overrun_rejected_for_all_arms": True,
        "missing_retry_rejected_before_key": True,
        "roles": {arm: [item["role"] for item in route] for arm, route in routes.items()},
        "order": order,
    }
    return report


if __name__ == "__main__":
    print(json.dumps(exercise(), sort_keys=True, indent=2))
