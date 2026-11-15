"""Omega AutoResearch: an offline, deterministic challenger evaluation gate.

This evaluator does NOT execute candidate code or attest the provenance of inputs.
A positive outcome authorizes human/external review, never publication or merge.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

ABSTAIN = "indetermine"


def digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_manifest(manifest: dict) -> dict[str, dict]:
    require(isinstance(manifest, dict), "manifest must be an object")
    require(isinstance(manifest.get("experiment_id"), str) and manifest["experiment_id"], "experiment_id is required")
    require(isinstance(manifest.get("cost_unit"), str) and manifest["cost_unit"], "cost_unit is required")
    budget = manifest.get("max_cost_per_case")
    require(type(budget) is int and budget >= 0, "max_cost_per_case must be a nonnegative integer")
    training = manifest.get("training_case_ids")
    require(isinstance(training, list) and all(isinstance(x, str) and x for x in training), "training_case_ids must be a list of identifiers")
    require(len(training) == len(set(training)), "duplicate training case IDs")
    holdout = manifest.get("holdout")
    require(isinstance(holdout, list) and bool(holdout), "holdout must be a nonempty list")
    ids: dict[str, dict] = {}
    for row in holdout:
        require(isinstance(row, dict), "holdout row must be an object")
        case_id, domain, expected = row.get("case_id"), row.get("domain"), row.get("expected")
        require(isinstance(case_id, str) and case_id, "invalid holdout case_id")
        require(isinstance(domain, str) and domain, "invalid domain")
        require(isinstance(expected, str) and expected and expected != ABSTAIN, "expected must be known, not abstention")
        require(case_id not in ids, f"duplicate holdout case_id: {case_id}")
        ids[case_id] = row
    require(not set(ids).intersection(training), "training and holdout overlap by case_id")
    domains = manifest.get("required_domains", [])
    require(isinstance(domains, list) and len(domains) == len(set(domains)) and all(isinstance(x, str) and x for x in domains), "required_domains invalid")
    require(set(domains) <= {row["domain"] for row in holdout}, "required domain absent in holdout")
    return ids


def load_arm(arm_name: str, arm: dict, ids: dict[str, dict], max_cost: int) -> dict[str, dict]:
    require(isinstance(arm, dict), f"{arm_name} must be an object")
    for attribute in ("source_commit", "run_url"):
        require(isinstance(arm.get(attribute), str) and bool(arm[attribute]), f"{arm_name}.{attribute} required (metadata, NOT an attestation)")
    rows = arm.get("results")
    require(isinstance(rows, list), f"{arm_name}.results must be a list")
    out: dict[str, dict] = {}
    for row in rows:
        require(isinstance(row, dict), f"{arm_name} result must be an object")
        case_id, prediction, cost = row.get("case_id"), row.get("prediction"), row.get("cost")
        require(isinstance(case_id, str) and case_id in ids, f"{arm_name}: unexpected case_id {case_id}")
        require(case_id not in out, f"{arm_name}: duplicate case_id {case_id}")
        require(isinstance(prediction, str) and prediction, f"{arm_name}: invalid prediction")
        require(type(cost) is int and 0 <= cost <= max_cost, f"{arm_name}: cost outside budget")
        out[case_id] = row
    require(set(out) == set(ids), f"{arm_name}: missing holdout results")
    return out


def evaluate(manifest: dict, observations: dict, expected_sha256: str) -> dict:
    ids = validate_manifest(manifest)
    require(len(expected_sha256) == 64 and all(x in "0123456789abcdef" for x in expected_sha256), "manifest SHA-256 must be lowercase hex")
    require(digest(manifest) == expected_sha256, "manifest does not match preregistered SHA-256")
    require(isinstance(observations, dict) and observations.get("experiment_id") == manifest["experiment_id"], "experiment ID mismatch")
    arms = observations.get("arms")
    require(isinstance(arms, dict) and set(arms) == {"baseline", "candidate"}, "exactly baseline and candidate arms required")
    results = {key: load_arm(key, arms[key], ids, manifest["max_cost_per_case"]) for key in ("baseline", "candidate")}
    metrics: dict[str, dict] = {}
    per_domain: dict[str, dict[str, dict]] = {}
    per_case: list[dict] = []
    domain_names = sorted({row["domain"] for row in ids.values()})
    for domain in domain_names:
        per_domain[domain] = {}
    for arm_name in ("baseline", "candidate"):
        totals = Counter(correct=0, false=0, abstentions=0, cost=0)
        for domain in domain_names:
            per_domain[domain][arm_name] = {"correct": 0, "false": 0, "abstentions": 0, "cost": 0}
        for case_id, gold in ids.items():
            outcome = results[arm_name][case_id]
            prediction = outcome["prediction"]
            classification = "abstentions" if prediction == ABSTAIN else ("correct" if prediction == gold["expected"] else "false")
            totals[classification] += 1
            totals["cost"] += outcome["cost"]
            per_domain[gold["domain"]][arm_name][classification] += 1
            per_domain[gold["domain"]][arm_name]["cost"] += outcome["cost"]
        metrics[arm_name] = dict(totals)

    regressions = []
    for case_id, gold in ids.items():
        base = results["baseline"][case_id]["prediction"]
        new = results["candidate"][case_id]["prediction"]
        if base == gold["expected"] and new != gold["expected"]:
            regressions.append(case_id)
        per_case.append({"case_id": case_id, "domain": gold["domain"], "baseline_correct": base == gold["expected"], "candidate_correct": new == gold["expected"]})
    b, c = metrics["baseline"], metrics["candidate"]
    valid_gain = (c["correct"] > b["correct"] or (c["correct"] == b["correct"] and c["cost"] < b["cost"]))
    domain_regressions = [domain for domain in domain_names if per_domain[domain]["candidate"]["correct"] < per_domain[domain]["baseline"]["correct"]]
    recommend = bool(valid_gain and not regressions and not domain_regressions and c["false"] == 0)
    return {
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": expected_sha256,
        "observations_sha256": digest(observations),
        "holdout_cases": len(ids),
        "cost_unit": manifest["cost_unit"],
        "metrics": metrics,
        "per_domain": per_domain,
        "lost_correct_case_ids": regressions,
        "domain_regressions": domain_regressions,
        "candidate_for_independent_review": recommend,
        "status": "REVIEW_REQUIRED" if recommend else "REJECTED",
        "provenance_status": "UNVERIFIED_EXTERNAL_INPUTS",
        "limitations": [
            "This program checks declared observations, not execution logs or source commit authenticity.",
            "Case-ID separation cannot detect equivalent examples under different IDs.",
            "Preregistering a SHA-256 is only meaningful if it was fixed independently before candidate evaluation.",
            "No code is executed; a positive verdict is not a scientific certificate or authorization to merge.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze", help="Print canonical SHA-256 for a manifest BEFORE experimenting")
    freeze.add_argument("manifest")
    check = sub.add_parser("evaluate", help="Evaluate a frozen manifest and separately recorded predictions")
    check.add_argument("manifest")
    check.add_argument("observations")
    check.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    try:
        manifest = load_json(args.manifest)
        if args.command == "freeze":
            validate_manifest(manifest)
            print(digest(manifest))
        else:
            print(json.dumps(evaluate(manifest, load_json(args.observations), args.manifest_sha256), ensure_ascii=False, indent=2, sort_keys=True))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
