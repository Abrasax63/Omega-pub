#!/usr/bin/env python3
"""Posthoc replay after section-Proof fail-closed gate; not a fresh holdout."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from translate import HERE, ROOT, blob
from skeleton09 import run

ENGINE = HERE / "skeleton09.py"
ENGINE_BLOB = "a8d7a1ac8de1d6ead3e144a5325f83b152c7d83f"
GOLD = HERE / "GOLD_SKELETON09_ERRATUM1.json"
GOLD_BLOB = "2e6483ed7c1f914e0076aa25133efb06d3d77fdc"


def evaluate() -> dict:
    if blob(ENGINE.read_bytes()) != ENGINE_BLOB or blob(GOLD.read_bytes()) != GOLD_BLOB:
        raise ValueError("posthoc data or engine changed")
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    summaries = {}
    rows = []
    for d in gold["documents"]:
        path = HERE / "holdout09" / d["file"]
        out = run(path, d["source_blob"])
        original = path.read_text(encoding="utf-8").splitlines()
        captures = 0
        for item in d["items"]:
            ln = item["line"]
            if item["anchor"] not in original[ln-1]:
                raise ValueError("gold broken")
            matches = [p for p in out["items"]
                       if p["line"] == ln and item["anchor"] in p["source_quote"]]
            captures += bool(matches)
            rows.append({"id": item["id"], "source_id": d["id"],
                         "captured": bool(matches), "role": item["kind"],
                         "kinds": [p["kind"] for p in matches]})
        proof_candidates = sum(p["section"].lower().startswith("preuve")
                               for p in out["items"])
        proof_blockers = sum(b["reason"] == "RELATION_IN_NON_THEOREM_OR_LIMIT"
                             and original[b["line"]-1] == b["source_quote"]
                             for b in out["blocked"]
                             if any(x.startswith("## Preuve") for x in original[:b["line"]-1]))
        summaries[d["id"]] = {
            "source_sha": d["source_blob"],
            "source_items": len(d["items"]),
            "captured": captures,
            "syntax_candidates": len(out["items"]),
            "proof_candidates": proof_candidates,
            "proof_blockers": proof_blockers,
            "citations_valid": out["citations_valid"],
            "horn_rule_count": len(out["horn_rules"]),
        }
    return {
        "status": "POSTHOC_PROOF_SECTION_GATE_ONLY",
        "original_holdout_run": "44153288183",
        "not_independent_holdout": True,
        "engine_blob": ENGINE_BLOB, "gold_blob": GOLD_BLOB,
        "per_card": summaries,
        "salient_captured": sum(r["captured"] for r in rows),
        "salient_total": len(rows),
        "no_proof_candidates": all(x["proof_candidates"] == 0 for x in summaries.values()),
        "proof_blocked": sum(x["proof_blockers"] for x in summaries.values()),
        "all_citations_valid": all(x["citations_valid"] for x in summaries.values()),
        "automatic_horn_rules": sum(x["horn_rule_count"] for x in summaries.values()),
        "safety_criterion": all(x["proof_candidates"] == 0 and x["citations_valid"] and
                                x["horn_rule_count"] == 0 for x in summaries.values()),
        "rows": rows,
        "interpretation": "Reused original two math cards after seeing their results. Reduced recall is not a negative generalization score; improved source-context quarantine is posthoc and must be checked again on a new corpus. No theorem was reviewed or certified.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate()
    data = json.dumps(report, ensure_ascii=False, indent=2)+"\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            parser.error("output outside repository")
        target.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
