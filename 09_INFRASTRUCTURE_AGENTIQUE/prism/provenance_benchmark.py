"""Deterministic public calibration; no tool traffic or model inference."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter_ns

from provenance_policy import decide

DATA = Path(__file__).with_name("provenance_cases")
ARMS = {
    "A_direct": None,
    "B_fixed": {"fixed": True},
    "C_omega": {"verify": False},
    "D_provenance": {},
    "E_greedy": {"horizon": 1},
}


def _read(name):
    return json.loads((DATA / (name + ".json")).read_text(encoding="utf-8"))


def run():
    tasks, observations = _read("tasks"), _read("observations")
    rows = []
    for task in tasks:
        for arm, settings in ARMS.items():
            start = perf_counter_ns()
            if settings is None:
                result = dict(decision=task["direct"], reason="initial_response", risk=None, trace=[])
            else:
                result = decide(task, observations[task["id"]].__getitem__, budget=2, **settings)
            elapsed = perf_counter_ns() - start
            rows.append(dict(case=task["id"], arm=arm, domain=task["domain"],
                             category=task["category"], consultations=len(result["trace"]),
                             local_ns=elapsed, **result))
    key = _read("answer_key")
    summary = {arm: dict(correct=0, wrong=0, confident_errors=0, justified_abstentions=0,
                         missed_decisions=0, consultations=0, score=0) for arm in ARMS}
    for row in rows:
        truth = key[row["case"]]["decision"]
        decision = row["decision"]
        if decision is None:
            verdict = "justified_abstentions" if truth is None else "missed_decisions"
        else:
            verdict = "correct" if decision == truth else "wrong"
        counts = summary[row["arm"]]
        counts[verdict] += 1
        counts["consultations"] += row["consultations"]
        counts["score"] += verdict in ("correct", "justified_abstentions")
        counts["confident_errors"] += verdict == "wrong" and (
            row["risk"] == "0" or row["arm"] == "A_direct")
        row["verdict"] = verdict
    return dict(status="calibration_publique", python=platform.python_version(),
                model_calls=0, live_calls=0, max_consultations=2, summary=summary,
                task_sha256=hashlib.sha256((DATA / "tasks.json").read_bytes()).hexdigest(),
                cases=rows)


def run_supplement():
    packet = _read("supplement_t3")
    task = packet["task"]
    rows = {}
    for arm, settings in ARMS.items():
        if settings is None:
            rows[arm] = dict(decision=task["direct"], trace=[])
        else:
            rows[arm] = decide(task, packet["observations"].__getitem__, budget=2, **settings)
    expected = packet["expected"]
    for result in rows.values():
        result["correct"] = result["decision"] == expected
    return dict(case=task["id"], expected=expected, arms=rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supplement", action="store_true", help="Replay the separate T3 calibration")
    args = parser.parse_args()
    print(json.dumps(run_supplement() if args.supplement else run(), ensure_ascii=False, indent=2))
