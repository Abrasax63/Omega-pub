#!/usr/bin/env python3
"""First held-out source assessment, using a frozen extractor unchanged since calibration.

The manually labeled eight source spans describe facts a science reader should
not miss. They are not automatically available as syntax-only clauses here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from extract import ROOT, git_blob, run

HERE = Path(__file__).resolve().parent
HOLDOUT = HERE / "holdout/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md"
HOLDOUT_BLOB = "3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7"
EXTRACTOR_BLOB = "10dcd6b9a0ca3fad8291bb178a05177df54e6ff6"
GOLD = HERE / "GOLD_HOLDOUT_FROZEN.json"
GOLD_BLOB = "42ade9bde3296a08eb60f66250b3d9c402470059"


def assess() -> dict:
    extractor = HERE / "extract.py"
    if git_blob(extractor.read_bytes()) != EXTRACTOR_BLOB:
        raise ValueError("engine changed after holdout selection: invalid holdout")
    report = run(HOLDOUT, HOLDOUT_BLOB)
    # Manual labels are only read after the frozen extractor has produced predictions.
    data = GOLD.read_bytes()
    if git_blob(data) != GOLD_BLOB:
        raise ValueError("gold changed after freeze")
    gold = json.loads(data.decode("utf-8"))
    source_lines = HOLDOUT.read_text(encoding="utf-8").splitlines()
    assert len(gold["notable_spans"]) == 8
    notable = []
    for g in gold["notable_spans"]:
        ln = g["line"]
        if not 1 <= ln <= len(source_lines) or g["anchor"] not in source_lines[ln-1]:
            raise ValueError("gold source anchor missing or mistranscribed: " + g["id"])
        matched = [c["id"] for c in report["candidates"]
                   if c["start_line"] <= ln <= c["end_line"]
                   and g["anchor"] in c["source_quote"]]
        notable.append({**g, "captured_candidate_ids": matched, "captured": bool(matched)})
    clauses = [x for x in report["candidates"] if x["kind"] == "CONDITIONAL_CANDIDATE"]
    expected_pairs = gold["expected_marked_pairs"]
    score = 0
    if expected_pairs == 0:
        scientific_status = "NOT_EVALUABLE_ZERO_EXPLICIT_IF_THEN_PAIRS"
        passes = False
    else:
        scientific_status = "SCOPE_TESTED_WITH_MARKED_PAIRS"
        passes = len(clauses) > 0 and report["cited_output_integrity"]
    return {
        "status": "UNSEEN_MATH_CARD_SYNTAX_EXTRACTION_V1",
        "scientific_status": scientific_status,
        "preregistered_success_achieved": passes,
        "frozen_engine_blob": EXTRACTOR_BLOB,
        "holdout_source_blob": HOLDOUT_BLOB,
        "gold_blob": GOLD_BLOB,
        "conditional_extraction_count": len(clauses),
        "expected_marked_pairs": expected_pairs,
        "all_literal_citations_valid": report["cited_output_integrity"],
        "source_grounded_important_spans": len(notable),
        "important_spans_captured": sum(x["captured"] for x in notable),
        "coverage": sum(x["captured"] for x in notable) / len(notable),
        "items": notable,
        "output": report,
        "limitation": "Selected before viewing holdout. Extractor only recognizes explicit conditional cues and a literal 'Limites' section; it cannot recognize the unnamed theorem, non-theorem and caveats here. No claim of semantic comprehension or mathematical validation.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = assess()
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            p.error("report must be outside repository")
        target.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
