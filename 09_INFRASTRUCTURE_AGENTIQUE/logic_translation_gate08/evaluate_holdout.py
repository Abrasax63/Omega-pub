#!/usr/bin/env python3
"""First held-out outcome of frozen syntax-to-logic bridge; negative preserved."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from translate import HERE, ROOT, blob, run

GOLD = HERE / "GOLD_HOLDOUT_FROZEN.json"
GOLD_SHA = "c177b7b8dd6f5a20fb1ec1e0113944f28d466f19"
ENGINE = HERE / "translate.py"
ENGINE_SHA = "53e356575c9756b5c2e4fed5ed9c8ecdb247418f"
HOLD = HERE / "holdout"


def evaluate() -> dict:
    if blob(ENGINE.read_bytes()) != ENGINE_SHA:
        raise ValueError("engine was modified after selecting heldout cards")
    cases = [
        ("BR-MEALY-HELLY-01", "BR-MEALY-HELLY-01_BRIQUE.md",
         "389957f14632fb253434202a46727ace8688b512"),
        ("BR-CTRL-01", "BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md",
         "3d52e5372f2eaecc6c66d960b0601e727325e2b2"),
    ]
    preds = {}
    for ident, filename, sha in cases:
        preds[ident] = run(HOLD / filename, sha)
    # Gold is loaded AFTER the predictions.
    data = GOLD.read_bytes()
    if blob(data) != GOLD_SHA:
        raise ValueError("frozen holdout gold mutated")
    gold = json.loads(data.decode("utf-8"))
    labels = {x["id"]: x for x in gold["documents"]}
    if len(labels) != 2 or sum(len(x["critical_spans"]) for x in labels.values()) != 8:
        raise ValueError("cohort drift")
    rows = []
    for sid, name, sha in cases:
        ref = labels[sid]
        if ref["source_blob"] != sha or ref["file"] != name:
            raise ValueError("historical document mismatch")
        lines = (HOLD / name).read_text(encoding="utf-8").splitlines()
        pred = preds[sid]
        for item in ref["critical_spans"]:
            n = item["line"]
            if not 1 <= n <= len(lines) or item["anchor"] not in lines[n-1]:
                raise ValueError("gold quote/source line mismatch")
            found = [x["id"] for x in pred["proposals"]
                     if x["line"] == n and item["anchor"] in x["source_quote"]]
            rows.append({
                "id": item["id"], "document": sid, "line": n,
                "kind": item["kind"], "captured": bool(found),
                "proposal_ids": found,
            })
    pair_count = sum(len(p["proposals"]) for p in preds.values())
    integrity = all(p["literal_integrity_passed"] and not p["horn_rules"]
                    for p in preds.values())
    expected = gold["expected_same_line_si_alors_pairs"]
    return {
        "status": ("NOT_EVALUABLE_ZERO_EXPLICIT_IF_THEN_PAIRS"
                   if expected == 0 else "CONDITIONAL_COHORT_EVALUATED"),
        "engine_sha": ENGINE_SHA, "gold_sha": GOLD_SHA,
        "preregistered_extraction_success": bool(
            expected > 0 and pair_count > 0 and integrity),
        "source_docs": len(cases), "explicit_pair_gold": expected,
        "candidate_pairs_extracted": pair_count,
        "critical_math_spans": len(rows),
        "critical_math_spans_as_conditionals": sum(r["captured"] for r in rows),
        "source_quote_integrity": integrity,
        "automatic_horn_rules": sum(len(x["horn_rules"]) for x in preds.values()),
        "rows": rows, "predictions": preds,
        "epistemic_warning": "Syntax-only gate on two selected pre-reading cards. The corpus lacks explicit same-line Si...alors, so extraction transfer cannot be validated; all mathematical claims remain unformalized. Do not count abstention as comprehension.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    r = evaluate()
    s = json.dumps(r, ensure_ascii=False, indent=2)+"\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("report outside repository only")
        dest.write_text(s, encoding="utf-8")
    else:
        print(s, end="")


if __name__ == "__main__":
    main()
