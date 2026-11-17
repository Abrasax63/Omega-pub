#!/usr/bin/env python3
"""Original prospectively selected two-card holdout of Omega fidelity gate 10.

Honors the pre-registered NON-EVALUABLE outcome when no eligible examples are
present. No post-hoc modifications of the grammar or claims of zero-error NLU.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from fidelity import git_blob, ROOT, run

HERE = Path(__file__).resolve().parent
PARSER = HERE / "fidelity.py"
PARSER_BLOB = "3d927dae6b4d90fa1ef8f77b4bc579c944c77cae"
GOLD = HERE / "GOLD_HOLDOUT_FROZEN.json"
GOLD_BLOB = "5a5bfd89c9cbc6a7a4fa99b29d29af989b5d65f0"
HOLD = HERE / "holdout"


def evaluate() -> dict:
    if git_blob(PARSER.read_bytes()) != PARSER_BLOB:
        raise ValueError("extractor changed since calibration and holdout selection")
    sources = [
        ("V7", "NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md",
         "6c482f97345abbb7f3d5bcd5e20da96259b276ce"),
        ("D01", "rapport_spectre_defauts_iteration_1.md",
         "b75f3d610ba73b6c549d212d0606465d9fe947a3")
    ]
    # Frozen program must execute on all sources BEFORE gold is loaded.
    predictions = {sid: run(HOLD / filename, sha)
                   for sid, filename, sha in sources}
    if git_blob(GOLD.read_bytes()) != GOLD_BLOB:
        raise ValueError("original manual gold modified")
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    annotated = {doc["id"]: doc for doc in gold["documents"]}
    if set(annotated) != set(predictions) or sum(len(x["annotations"]) for x in annotated.values()) != 16:
        raise ValueError("holdout cohort mutated")
    rows, reports = [], {}
    for sid, filename, sha in sources:
        label = annotated[sid]
        result = predictions[sid]
        if label["name"] != filename or label["source_blob"] != sha:
            raise ValueError("source identity altered")
        lines = (HOLD/filename).read_text(encoding="utf-8").splitlines()
        local = []
        for claim in label["annotations"]:
            n = claim["line"]
            if type(n) is not int or not 1 <= n <= len(lines) or claim["anchor"] not in lines[n-1]:
                raise ValueError("manual gold anchor differs from source: "+claim["id"])
            matches = [v for v in result["candidates"] if v["line"] == n
                       and claim["anchor"] in v["source_quote"]]
            row = {
                "id": claim["id"], "source_id": sid, "source_line": n,
                "gold_role": claim["role"], "anchor": claim["anchor"],
                "expected": claim["expected"],
                "candidate_count": len(matches),
                "captured": bool(matches),
                "candidate_literals": [x["literal"] for x in matches],
            }
            rows.append(row)
            local.append(row)
        reports[sid] = {
            "source_blob": sha, "source_lines": len(lines),
            "syntax_candidates": len(result["candidates"]),
            "unparsed_backtick_fragments": len(result["abstentions"]),
            "latex_delimiter_lines": sum(
                "\\(" in line or "\\[" in line for line in lines
            ),
            "gold_salient_count": len(local),
            "salient_captured": sum(x["captured"] for x in local),
            "all_candidate_verifications_passed": result["checked_all_candidates"],
            "independent_finite_valuations": result["total_finite_valuations"],
            "horn_rule_count": len(result["horn_rules"]),
            "automatic_promotion_count": result["automatic_promotions"]
        }
    in_grammar = gold["expected_in_grammar"]
    total_candidates = sum(x["syntax_candidates"] for x in reports.values())
    eligible_matched = sum(x["captured"] for x in rows)
    safe = all(x["all_candidate_verifications_passed"]
               and x["horn_rule_count"] == 0 and x["automatic_promotion_count"] == 0
               for x in reports.values())
    return {
        "status": ("NOT_EVALUABLE_NO_IN_GRAMMAR_FORMULAS"
                   if in_grammar == 0 else "EVALUATED_RESTRICTED_FORMAL_GRAMMAR"),
        "original_protocol_frozen": True, "model_program_git_blob": PARSER_BLOB,
        "gold_git_blob": GOLD_BLOB,
        "scientific_success": bool(
            in_grammar > 0 and eligible_matched > 0 and safe),
        "document_count": len(sources),
        "source_blobs_pinned": True,
        "heldout_eligible_formulas": in_grammar,
        "total_machine_candidates": total_candidates,
        "gold_semantically_salient_items": len(rows),
        "salient_items_captured_as_arithmetic_AST": eligible_matched,
        "zero_unreviewed_horn_imports": all(x["horn_rule_count"] == 0
                                           for x in reports.values()),
        "all_presented_candidates_structurally_verified": safe,
        "per_source": reports,
        "rows": rows,
        "scope_warning": "The two prospective files primarily use mathematical LaTeX and explanatory French, not the pinned restricted ASCII-in-backticks grammar. Technical non-hallucination when making zero predictions is NOT correct mathematical semantic extraction. Pre-registered scientific gate is NOT MET.",
        "source_predictor_summary": {
            sid: {"candidates": v["candidates"],
                  "abstentions": v["abstentions"],
                  "verification": v["verification"]}
            for sid,v in predictions.items()
        }
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = evaluate()
    text = json.dumps(report, ensure_ascii=False, indent=2)+"\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("reports must be written outside repository")
        dest.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
