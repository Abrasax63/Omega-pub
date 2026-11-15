"""OMEGA-CYCLE-01: real, auditable wiring of P1/P2/P3 to AutoResearch.

Modes:
  plan      : P1 + read-only P2, no candidate execution;
  templates : audited fixed-template search and strong-classical comparison;
  model     : fresh Qwen inference via original model_pilot, with Docker.

No mode can modify certified content or approve automatic merging.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INFRA = ROOT / "09_INFRASTRUCTURE_AGENTIQUE"
for directory in (INFRA / "prism", INFRA / "auto_research"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from planner import plan_mission
from context import prepare_contexts
from execution import start_execution, record_perspective, close_execution
from event_store import lifecycle_events, verify_events
from gate import digest, evaluate
from runner import graph_case, evaluate_variant
from variant_factory import generate, choose
from model_pilot import run as run_open_model

MISSION = {
    "mission_id": "OMEGA-CYCLE-01",
    "question": (
        "Calculer la relation des chemins de longueur h, Q^h, "
        "et son écart Δ_h avec les trajectoires microscopiques réelles. "
        "Peut-on proposer un programme strictement meilleur que "
        "les méthodes classiques à preuve et coût comparables ?"
    ),
    "mission_type": "mathematical",
    "domain": "finite-dynamical-observability",
    "scope": "relations finies encodées par masques binaires",
    "requires_proof": True,
    "requires_computation": True,
    "requires_literature": False,
    "exploratory": False,
    "claims_to_test": True,
    "known_ids": [],
    "exclusions": [
        "pas de promotion scientifique automatique",
        "pas de confusion entre perspective de rôle et agent indépendant",
        "ne pas exposer les cas réservés au modèle",
    ],
}
STRONG = ("square-scan", "square-lowbit")


def prepare(root: Path = ROOT) -> tuple[dict, dict]:
    plan = plan_mission(dict(MISSION))
    bundle = prepare_contexts(root, plan, max_documents=4)
    if plan["execution_model"]["model_calls_performed"] != 0:
        raise RuntimeError("P1 unexpectedly claims executed models")
    if bundle["execution_model"]["role_tasks_executed"] != 0:
        raise RuntimeError("P2 unexpectedly claims executed tasks")
    if not bundle["packages"] or not bundle["manifest"]["content_hash"]:
        raise RuntimeError("no verifiable context bundle")
    return plan, bundle


def template_trial(inputs: dict) -> dict:
    train_ids, heldout_ids = inputs["seed_development"], inputs["seed_reserved"]
    if set(train_ids) & set(heldout_ids):
        raise ValueError("training/heldout overlap")
    variants = generate()
    train = [graph_case(seed) for seed in train_ids]
    heldout = [graph_case(seed) for seed in heldout_ids]

    training = {}
    for name, variant in sorted(variants.items()):
        rows = evaluate_variant(variant["source"], train)
        training[name] = {
            "correct": all(r["correct"] and r["delta_correct"] for r in rows),
            "errors": sum(not (r["correct"] and r["delta_correct"]) for r in rows),
            "cpu_us_total": sum(r["cost"] for r in rows),
            "source_sha256": variant["sha256"],
        }
    champion = choose(training)
    if champion is None:
        return {
            "status": "NO_VALID_TEMPLATE",
            "source": "fixed audited templates",
            "training": training,
            "holdout_opened": False,
            "decision": "REJECTED",
        }
    # A strong baseline is chosen from development timings only.
    eligible = [n for n in STRONG if training[n]["correct"]]
    if not eligible:
        raise RuntimeError("no valid strong classical baseline")
    classic = min(eligible, key=lambda n: (training[n]["cpu_us_total"], n))
    # No tuning, selection, or source change after this boundary.
    source_candidate = variants[champion]
    source_baseline = variants[classic]
    baseline_rows = evaluate_variant(source_baseline["source"], heldout)
    candidate_rows = evaluate_variant(source_candidate["source"], heldout)
    if not all(r["delta_correct"] for r in candidate_rows + baseline_rows):
        raise RuntimeError("independent Δ_h reference failed")
    manifest = {
        "experiment_id": "OMEGA-CYCLE-01-TEMPLATES",
        "cost_unit": "measured_child_cpu_microseconds",
        "cost_policy": "no_increase",
        "max_cost_per_case": 10_000_000,
        "max_total_cost": 10_000_000 * len(heldout),
        "training_case_ids": [str(x) for x in train_ids],
        "training_group_ids": [x["group_id"] for x in train],
        "previous_holdout_group_ids": [],
        "required_domains": ["finite-observability"],
        "holdout": [
            {
                "case_id": r["case_id"], "group_id": r["group_id"],
                "domain": "finite-observability", "expected": r["expected"],
            }
            for r in baseline_rows
        ],
    }
    def arm(label: str, program: dict, rows: list[dict]) -> dict:
        return {
            "source_commit": "generated-template-sha256:" + program["sha256"],
            "run_url": "UNATTESTED-LOCAL-SUBPROCESS",
            "results": [
                {"case_id": row["case_id"], "prediction": row["prediction"], "cost": row["cost"]}
                for row in rows
            ],
        }
    observations = {
        "experiment_id": manifest["experiment_id"],
        "arms": {
            "baseline": arm(classic, source_baseline, baseline_rows),
            "candidate": arm(champion, source_candidate, candidate_rows),
        },
    }
    gate = evaluate(manifest, observations, digest(manifest))
    # A rule/template search among known classic algorithms is not innovation.
    return {
        "status": "TEMPLATE_ONLY_EXECUTED",
        "strategy": "four fixed, audited program shapes, not model-created",
        "candidate": champion, "strong_baseline": classic,
        "candidate_sha256": source_candidate["sha256"],
        "strong_baseline_sha256": source_baseline["sha256"],
        "same_exact_source": source_candidate["sha256"] == source_baseline["sha256"],
        "same_source_timing_false_review_detected": bool(
            source_candidate["sha256"] == source_baseline["sha256"]
            and gate["candidate_for_independent_review"]
        ),
        "training": training,
        "holdout_opened": True,
        "holdout_cases": len(heldout),
        "manifest_sha256": digest(manifest),
        "observations_sha256": digest(observations),
        "independent_delta_checked": True,
        "gate": gate,
        "decision": "REJECTED_TEMPLATE_ONLY",
        "gain_of_autonomous_intelligence_demonstrated": False,
    }


def known_prior_sources() -> list[dict]:
    """Read the historical source ledger; fail closed if absent or malformed."""
    path = HERE / "HISTORICAL_SOURCES.json"
    history = json.loads(path.read_text(encoding="utf-8"))
    records = history["entries"]
    if not isinstance(records, list) or not records:
        raise ValueError("historical source registry missing or empty")
    for record in records:
        digest_value = record["source_sha256"]
        if (not isinstance(digest_value, str) or len(digest_value) != 64
                or any(ch not in "0123456789abcdef" for ch in digest_value)):
            raise ValueError("invalid historical SHA-256")
    return records


def model_trial(llama_cli: Path, model_file: Path, model_label: str) -> dict:
    history = known_prior_sources()
    outcome = run_open_model(str(llama_cli), str(model_file), model_label)
    attempted = outcome.get("attempts", [])
    if not attempted or all(row.get("model_call_returncode") != 0 for row in attempted):
        raise RuntimeError("model inference infrastructure failed")
    evaluated = outcome.get("status") == "MODEL_CANDIDATE_EVALUATED"
    winner_sha = outcome.get("winner_sha256") if evaluated else None
    matched = [record for record in history if record["source_sha256"] == winner_sha]
    passed_strong = bool(evaluated and outcome.get("strong_baseline_passed"))
    source_identical_to_classic = bool(outcome.get("candidate_equals_classical_source"))
    passed = passed_strong and not matched and not source_identical_to_classic
    reasons = []
    if not evaluated:
        reasons.append("NO_VALID_MODEL_CANDIDATE")
    if evaluated and not passed_strong:
        reasons.append("NO_ADVANTAGE_OVER_BOTH_STRONG_CLASSICS")
    if source_identical_to_classic:
        reasons.append("IDENTICAL_TO_CLASSICAL_SOURCE")
    if matched:
        reasons.append("KNOWN_HISTORICAL_SOURCE_REUSED")
    return {
        **outcome,
        "historical_source_registry_size": len(history),
        "historical_source_matches": matched,
        "known_historical_duplicate": bool(matched),
        "source_novelty": (
            "KNOWN_REUSED" if matched else
            "UNVERIFIED_GLOBAL_NOVELTY" if winner_sha else
            "NO_SELECTED_SOURCE"
        ),
        "decision": "REVIEW_REQUIRED" if passed else "REJECTED",
        "rejection_reasons": reasons,
        "gain_of_autonomous_intelligence_demonstrated": False,
        "promotion_to_core": False,
    }


def integrated_cycle(mode: str, *, root: Path = ROOT, inputs: dict | None = None,
                     llama_cli: Path | None = None,
                     model_file: Path | None = None, model_label: str = "Qwen2.5-Coder-3B") -> dict:
    plan, bundle = prepare(root)
    result = None
    if mode == "templates":
        if inputs is None:
            inputs = json.loads((HERE / "CYCLE_INPUTS.json").read_text(encoding="utf-8"))
        result = template_trial(inputs)
    elif mode == "model":
        if llama_cli is None or model_file is None:
            raise ValueError("real model mode requires both llama-cli and model-file")
        result = model_trial(llama_cli, model_file, model_label)
    elif mode != "plan":
        raise ValueError("unknown mode")
    execution = start_execution(plan, bundle)
    if result is not None:
        role = "computational"
        record_perspective(
            execution, role, status="completed",
            output=json.dumps(
                {"experiment_mode": mode, "experiment_status": result["status"],
                 "decision": result["decision"]}, ensure_ascii=False, sort_keys=True),
            evidence_refs=[
                "experiment-sha256:" + digest(result),
                "context-sha256:" + bundle["manifest"]["content_hash"],
            ],
            limitations=[
                "Execution and role perspectives are not independent researchers",
                "Scientific certification has not been performed",
            ],
        )
    execution = close_execution(execution)
    events = lifecycle_events(plan, bundle, execution)
    audit = verify_events(events)
    if not audit["valid"]:
        raise RuntimeError("provenance chain invalid")
    summary = {
        "cycle_id": MISSION["mission_id"],
        "mode": mode,
        "mission": MISSION,
        "plan_sha256": digest(plan),
        "context_sha256": bundle["manifest"]["content_hash"],
        "context": {
            "package_count": bundle["manifest"]["package_count"],
            "search_calls": bundle["manifest"]["search_calls"],
            "exact_retrieval_calls": bundle["manifest"]["exact_retrieval_calls"],
            "note": "The role context is retrieved and logged; model_pilot uses its frozen public prompt, not an RCE-fed prompt.",
        },
        "p3": execution,
        "events": events,
        "provenance_validation": audit,
        "experiment": result,
        "scientific_status": "INDETERMINATE_NOT_INDEPENDENTLY_CERTIFIED",
        "main_modified": False,
        "promotion_to_core": False,
        "limitations": [
            "RCE is a local lexical read-only search; it does not synthesize scientific evidence.",
            "P1 plans role perspectives, no independent agents are launched.",
            "Event hashes audit local integrity but do not authenticate GitHub or external independence.",
            "Template trial uses published synthetic cases, cannot demonstrate new algorithms.",
            "Model mode uses an in-job frozen holdout and noisy Docker wall time, not an external blind oracle.",
            "No merging of a proposed program is performed.",
        ],
    }
    summary["report_sha256_without_self"] = digest(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["plan", "templates", "model"], default="plan")
    parser.add_argument("--output", type=Path, default=Path("cycle-result.json"))
    parser.add_argument("--llama-cli", type=Path)
    parser.add_argument("--model-file", type=Path)
    parser.add_argument("--model-label", default="Qwen2.5-Coder-3B-Instruct Q4_K_M")
    args = parser.parse_args()
    result = integrated_cycle(
        args.mode, llama_cli=args.llama_cli, model_file=args.model_file,
        model_label=args.model_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "cycle_id": result["cycle_id"], "mode": result["mode"],
        "context_sha256": result["context_sha256"],
        "role_coverage": result["p3"]["coverage"],
        "experiment_status": (result["experiment"] or {}).get("status"),
        "decision": (result["experiment"] or {}).get("decision"),
        "event_count": result["provenance_validation"]["event_count"],
        "event_chain_valid": result["provenance_validation"]["valid"],
        "report_sha256_without_self": result["report_sha256_without_self"],
    }, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
