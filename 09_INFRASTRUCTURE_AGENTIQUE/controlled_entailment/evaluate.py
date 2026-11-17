#!/usr/bin/env python3
"""Frozen, exact truth-table benchmark for controlled-language implications.

The engine has no access to this module, GOLD_FROZEN.json, or its oracle.
Gold is loaded only after all input-only predictions have been formed.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from engine import evaluate_case, parse_case, verify_certificate

HERE = Path(__file__).resolve().parent
INPUT_PATH = HERE / "INPUTS_FROZEN.json"
GOLD_PATH = HERE / "GOLD_FROZEN.json"
INPUT_BLOB = "6561a010a3a63873c62bdf13852ab07946de1554"
GOLD_BLOB = "8492a039f618712d0151af272d10e0db0406a42d"


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_frozen(path: Path, expected_blob: str) -> dict:
    if git_blob(path) != expected_blob:
        raise ValueError("frozen fixture changed: " + path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def exact_truth_table(case: dict, annotation: dict) -> tuple[str, dict | None]:
    if annotation["expect_abstain"]:
        return "ABSTAIN", None
    rules = annotation["rules"]
    facts = set(case["facts"])
    goal = case["goal"]
    atoms = facts | {goal}
    for rule in rules:
        atoms.update(rule["premises"])
        atoms.add(rule["conclusion"])
    atoms = sorted(atoms)
    if len(atoms) > 8:
        raise ValueError("oracle complexity bound exceeded")
    models = 0
    for values in itertools.product((False, True), repeat=len(atoms)):
        valuation = dict(zip(atoms, values))
        if not all(valuation[fact] for fact in facts):
            continue
        if any(all(valuation[p] for p in rule["premises"])
               and not valuation[rule["conclusion"]] for rule in rules):
            continue
        models += 1
        if not valuation[goal]:
            return "NOT_ENTAILED", valuation
    if models == 0:
        raise ValueError("oracle found no model; invalid corpus")
    return "ENTAILED", None


def score(rows: list[dict], arm: str) -> dict:
    subset = [r for r in rows if r["split"] == "holdout"]
    right = sum(r[arm] == r["oracle"] for r in subset)
    positives = [r for r in subset if r["oracle"] == "ENTAILED"]
    negative = [r for r in subset if r["oracle"] != "ENTAILED"]
    return {
        "total": len(subset),
        "correct": right,
        "accuracy": right / len(subset) if subset else None,
        "entailed_tp": sum(r[arm] == "ENTAILED" for r in positives),
        "entailed_total": len(positives),
        "false_entailed": sum(r[arm] == "ENTAILED" for r in negative),
        "abstentions_expected": sum(r["oracle"] == "ABSTAIN" for r in subset),
        "abstentions_correct": sum(r["oracle"] == r[arm] == "ABSTAIN" for r in subset),
    }


def run() -> dict:
    inputs = load_frozen(INPUT_PATH, INPUT_BLOB)
    # Important: decisions first; annotations become visible to scorer only later.
    predictions = {}
    for case in inputs["cases"]:
        predictions[case["id"]] = {
            "engine": evaluate_case(case),
            "one_pass": evaluate_case(case, one_pass=True),
        }

    gold = load_frozen(GOLD_PATH, GOLD_BLOB)
    annotations = {a["id"]: a for a in gold["cases"]}
    ids = [c["id"] for c in inputs["cases"]]
    if len(ids) != 26 or len(set(ids)) != 26 or len(annotations) != 26 or set(ids) != set(annotations):
        raise ValueError("case count, uniqueness or oracle alignment mismatch")
    if sum(c["split"] == "holdout" for c in inputs["cases"]) != 16:
        raise ValueError("holdout size changed")

    rows = []
    for case in inputs["cases"]:
        ann = annotations[case["id"]]
        if ann["split"] != case["split"]:
            raise ValueError("split mismatch")
        expected, truth_countermodel = exact_truth_table(case, ann)
        pred = predictions[case["id"]]
        cert_ok = verify_certificate(case, pred["engine"])
        if not ann["expect_abstain"]:
            facts, parsed, goal = parse_case(case)
            rules = ann["rules"]
            if parsed != rules:
                raise ValueError("parser does not preserve formal semantics: " + case["id"])
        rows.append({
            "id": case["id"],
            "split": case["split"],
            "oracle": expected,
            "engine": pred["engine"]["verdict"],
            "one_pass": pred["one_pass"]["verdict"],
            "certificate_valid": cert_ok,
            "engine_certificate": pred["engine"]["certificate"],
            "engine_reason": pred["engine"]["reason"],
            "oracle_counterexample": truth_countermodel,
        })
    candidate = score(rows, "engine")
    baseline = score(rows, "one_pass")
    reserved = [r for r in rows if r["split"] == "holdout"]
    criterion = (
        candidate["correct"] > baseline["correct"]
        and candidate["false_entailed"] == 0
        and candidate["entailed_tp"] >= 5
        and candidate["entailed_total"] == 7
        and candidate["abstentions_correct"] == candidate["abstentions_expected"] == 4
        and all(r["certificate_valid"] for r in reserved)
    )
    return {
        "status": "EXACT_CONTROLLED_LANGUAGE_NONBLIND_HOLDOUT",
        "frozen_blobs": {"inputs": INPUT_BLOB, "gold": GOLD_BLOB},
        "total_cases": len(rows),
        "heldout_cases": len(reserved),
        "candidate": candidate,
        "one_pass_baseline": baseline,
        "all_engine_certificates_valid": all(r["certificate_valid"] for r in rows),
        "pre_registered_criterion_met": criterion,
        "limitations": [
            "Synthetic controlled French clauses, not natural scientific theorems.",
            "Human-authored cases and oracle, held out from score but not externally blind.",
            "One-pass baseline is intentionally incomplete and may give false NOT_ENTAILED.",
            "No general semantic understanding, autonomous theorem finding or independent proof audit.",
        ],
        "cases": rows,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    r = run()
    payload = json.dumps(r, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        path = args.output.resolve()
        if path.is_relative_to(HERE.parents[1]):
            p.error("write reports outside repository only")
        path.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
