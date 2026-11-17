#!/usr/bin/env python3
"""Holdout audit of the frozen syntax skeleton against two new math cards."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from translate import HERE, ROOT, blob
from skeleton09 import run

ENGINE = HERE / "skeleton09.py"
ENGINE_SHA = "4462d120496f9c2743ab4168227d184b5d2e1305"
GOLD = HERE / "GOLD_SKELETON09_FROZEN.json"
GOLD_SHA = "6c5167feee5df47ef7f4896c60e290cbe6728263"
SOURCE = HERE / "holdout09"


def evaluate():
    if blob(ENGINE.read_bytes()) != ENGINE_SHA:
        raise ValueError("engine modified after holdout selection")
    source_refs = (
        ("BR-AFFINE-GROUP-CORE", "BR-AFFINE-GROUP-CORE_BRIQUE.md",
         "6838a2e95ab64ae53406e4fc75abc267e4366745"),
        ("BR-ACC-STATE-COMMUTE-01", "BR-ACC-STATE-COMMUTE-01_BRIQUE.md",
         "c4c89930f075983e085da5e38c956f12dc61186e"),
    )
    # Produce all predictions BEFORE reading gold.
    outputs = {sid: run(SOURCE / file, sha) for sid,file,sha in source_refs}
    if blob(GOLD.read_bytes()) != GOLD_SHA:
        raise ValueError("frozen gold modified")
    manual = json.loads(GOLD.read_text(encoding="utf-8"))
    labels = {x["id"]: x for x in manual["documents"]}
    if set(labels) != set(outputs) or sum(len(x["items"]) for x in labels.values()) != 12:
        raise ValueError("gold case alignment invalid")
    rows, by_card, unsafe = [], {}, []
    for sid, filename, sha in source_refs:
        label, result = labels[sid], outputs[sid]
        if label["file"] != filename or label["source_blob"] != sha:
            raise ValueError("gold source identity mismatch")
        original = (SOURCE / filename).read_text(encoding="utf-8").splitlines()
        card_rows = []
        for item in label["items"]:
            i = item["line"]
            if not 1 <= i <= len(original) or item["anchor"] not in original[i-1]:
                raise ValueError("gold manual span absent in historical source")
            matched = [p for p in result["items"]
                       if p["line"] == i and item["anchor"] in p["source_quote"]]
            kind_match = any(x["kind"] in item["expected_kinds"] for x in matched)
            captured = bool(matched)
            dangerous = any(p.get("promotable") is not False for p in matched)
            row = {
                "id": item["id"], "source_id": sid, "line": i,
                "gold_role": item["kind"], "anchor": item["anchor"],
                "captured": captured, "expected_kind_matched": kind_match,
                "candidate_ids": [x["id"] for x in matched],
                "candidate_types": [x["kind"] for x in matched],
                "promoted_without_review": dangerous,
            }
            card_rows.append(row)
            rows.append(row)
            if dangerous:
                unsafe.append(item["id"])
        by_card[sid] = {
            "important_spans": len(card_rows),
            "captured": sum(x["captured"] for x in card_rows),
            "type_matched": sum(x["expected_kind_matched"] for x in card_rows),
            "parsed_kind_counts": result["summary"],
            "citations_valid": result["citations_valid"],
            "proof_section_candidates": sum(
                p["section"].lower().startswith("preuve") for p in result["items"]
            ),
        }
    n = len(rows)
    count = sum(x["captured"] for x in rows)
    inferred_rules = sum(len(result["horn_rules"]) for result in outputs.values())
    valid = all(result["citations_valid"] for result in outputs.values())
    asserted = all(p.get("promotable") is False and p.get("status") == "REVIEW_REQUIRED"
                   for result in outputs.values() for p in result["items"])
    types = sum(x["expected_kind_matched"] for x in rows)
    candidates = sum(len(x["items"]) for x in outputs.values())
    criterion = (count / n >= .25 and candidates > 0 and valid
                 and not unsafe and inferred_rules == 0 and asserted)
    return {
        "status": "UNSEEN_MATH_SYNTAX_SKELETON_NOT_SEMANTIC_THEOREM_VALIDATION",
        "engine_blob": ENGINE_SHA, "gold_blob": GOLD_SHA,
        "pre_registered_structural_success": criterion,
        "source_count": len(outputs), "salient_gold_count": n,
        "salient_captured": count, "salient_coverage": count/n,
        "salient_type_matched": types, "candidates_total": candidates,
        "citations_valid": valid, "automatic_horn_rules": inferred_rules,
        "unsafe_promotion_ids": unsafe,
        "proof_section_candidates_total": sum(x["proof_section_candidates"]
                                               for x in by_card.values()),
        "per_card": by_card,
        "rows": rows, "source_outputs": outputs,
        "scientific_limitation": "All candidates remain uninterpreted and must be reviewed; even proof-section statements are not promoted. Same-author span labels and simple structural syntax cannot establish logical entailment, mathematical truth, scientific novelty or autonomous reasoning. Earlier pilot #161 negative remains unchanged.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = evaluate()
    data = json.dumps(result, ensure_ascii=False, indent=2)+"\n"
    if a.output:
        target = a.output.resolve()
        if target.is_relative_to(ROOT):
            p.error("report must be outside repo")
        target.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
