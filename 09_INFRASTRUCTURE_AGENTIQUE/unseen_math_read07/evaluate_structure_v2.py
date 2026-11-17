#!/usr/bin/env python3
"""First holdout on two never-read math cards, extractor v2 frozen before source access."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from extract import ROOT, git_blob
from structure_v2 import run

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "structure_v2.py"
ENGINE_BLOB = "32478220a199430cb9a8dc2c5f8f1db6affa72b9"
GOLD = HERE / "GOLD_STRUCTURE_V2_FROZEN.json"
GOLD_BLOB = "ff7669de952fa06da1d21661992b836aa75e38fc"
SOURCE_ROOT = HERE / "holdout_v2"


def evaluate() -> dict:
    if git_blob(ENGINE.read_bytes()) != ENGINE_BLOB:
        raise ValueError("parser has changed since source selection")
    # Parse both reserved cards before loading the manually authored gold.
    docs = {
        "BR-STATE-01": SOURCE_ROOT / "BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md",
        "BR-OBS-01": SOURCE_ROOT / "BR-OBS-01_ADAPTATIF_VS_PREDEFINI.md",
    }
    output = {sid: run(p) for sid, p in docs.items()}
    if git_blob(GOLD.read_bytes()) != GOLD_BLOB:
        raise ValueError("holdout gold altered")
    g = json.loads(GOLD.read_text(encoding="utf-8"))
    gold = {d["id"]: d for d in g["documents"]}
    if set(gold) != set(docs) or sum(len(d["items"]) for d in gold.values()) != 16:
        raise ValueError("gold cohort was modified")
    rows, summary = [], {}
    for sid, doc in output.items():
        target = gold[sid]
        if target["source_blob"] != doc["source_blob"]:
            raise ValueError("source changed since historical pin")
        source_lines = docs[sid].read_text(encoding="utf-8").splitlines()
        per = []
        for label in target["items"]:
            n = label["line"]
            if not 1 <= n <= len(source_lines) or label["anchor"] not in source_lines[n-1]:
                raise ValueError("manual gold phrase absent from pinned document: " + label["id"])
            captured = [item for item in doc["items"]
                        if item["start_line"] <= n <= item["end_line"]
                        and label["anchor"] in item["source_quote"]]
            recognized = bool(captured)
            right_type = any(x["kind"] in label["acceptable_kinds"] for x in captured)
            bad_promote = label["role"] == "LIMITATION" and any(
                x["kind"] == "THEOREM_STATEMENT_LITERAL" for x in captured
            )
            per.append({
                "id": label["id"], "line": n, "role": label["role"],
                "anchor": label["anchor"],
                "captured": recognized, "correct_type": right_type,
                "dangerous_theorem_promotion": bad_promote,
                "candidate_ids": [x["id"] for x in captured],
                "candidate_kinds": [x["kind"] for x in captured],
            })
        rows.extend({"source_id": sid, **x} for x in per)
        summary[sid] = {
            "salient_gold_items": len(per),
            "captured": sum(x["captured"] for x in per),
            "correctly_typed": sum(x["correct_type"] for x in per),
            "candidate_counts": doc["counts"],
            "citations_valid": doc["citations_valid"],
            "dangerous_promotions": [x["id"] for x in per
                                     if x["dangerous_theorem_promotion"]],
        }
    n = len(rows)
    captured = sum(r["captured"] for r in rows)
    typed = sum(r["correct_type"] for r in rows)
    bad = [r["id"] for r in rows if r["dangerous_theorem_promotion"]]
    cited = all(d["citations_valid"] for d in output.values())
    theorem = sum(d["counts"]["THEOREM_STATEMENT_LITERAL"] for d in output.values())
    ok = theorem >= 1 and captured/n >= .25 and not bad and cited
    return {
        "status": "V2_UNSEEN_TWO_CARD_STRUCTURAL_EXTRACTION_NOT_SEMANTIC_REASONING",
        "engine_blob_before_holdout": ENGINE_BLOB,
        "gold_blob": GOLD_BLOB,
        "pre_registered_local_success": ok,
        "two_sources": summary,
        "salient_total": n, "salient_captured": captured,
        "salient_correctly_typed": typed,
        "salient_coverage": captured/n,
        "type_coverage": typed/n,
        "theorem_heading_candidates": theorem,
        "false_warning_promotions": bad,
        "all_citations_valid": cited,
        "rows": rows,
        "source_outputs": output,
        "limits": "Gold salient spans annotated by same experimenter; source heading recognition not formal understanding or proof. Conditions not automatically translated to Horn clauses. Calibration B02 used after previous failure; only B-STATE and B-OBS are prospective, not independently adjudicated by an external expert.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = evaluate()
    content = json.dumps(report, indent=2, ensure_ascii=False)+"\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            p.error("reports outside repository")
        target.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
