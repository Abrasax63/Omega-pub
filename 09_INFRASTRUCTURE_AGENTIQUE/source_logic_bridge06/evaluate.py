#!/usr/bin/env python3
"""Reproducible, frozen structured-claim validation of source-logic bridge 06.

This verifies structural coherence of the manually annotated mini-contract.
It is NOT a benchmark of natural-language understanding, proof discovery, or
independent mathematical verification of the source theorem statements.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from bridge import HERE, ROOT, RULES_BLOB, RULES_PATH, run

INPUT = HERE / "QUERIES_FROZEN.json"
GOLD = HERE / "GOLD_FROZEN.json"
INPUT_BLOB = "81f6837d01cdd71ea9ceee9eb6b75973472ca1d2"
GOLD_BLOB = "5ee7fad018e076128851710b38bbc7e85a60c906"


def load_frozen(path: Path, blob: str) -> dict:
    data = path.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if sha != blob:
        raise ValueError("frozen fixture changed: " + path.name)
    return json.loads(data.decode("utf-8"))


def evaluate() -> dict:
    data = load_frozen(INPUT, INPUT_BLOB)
    questions = data["queries"]
    if len(questions) != 14 or len({q["id"] for q in questions}) != 14:
        raise ValueError("query set size or ID uniqueness changed")
    # The solver is called BEFORE loading the gold.
    report = run(questions)
    raw = load_frozen(GOLD, GOLD_BLOB)
    labels = {x["id"]: x["verdict"] for x in raw["targets"]}
    if len(labels) != 14 or set(labels) != {q["id"] for q in questions}:
        raise ValueError("gold alignment changed")
    rows = []
    for answer in report["answers"]:
        label = labels[answer["query_id"]]
        rows.append({
            "id": answer["query_id"], "source_id": answer["source_id"],
            "goal": answer["goal"], "verdict": answer["verdict"],
            "gold": label, "correct": answer["verdict"] == label,
            "certificate_valid": answer["certificate_valid"],
            "reason": answer["reason"],
            "proof_rule_ids": [step["rule_id"] for step in answer["proof"]],
            "missing_assumptions": answer["missing_assumptions"],
        })
    correct = sum(row["correct"] for row in rows)
    assert report["source_count"] >= 5
    assert report["annotated_sources"] == 4
    return {
        "status": "GENERIC_SOURCE_LOGIC_BRIDGE_STRUCTURAL_COHERENCE_NOT_NLU",
        "frozen_rule_blob": RULES_BLOB,
        "frozen_input_blob": INPUT_BLOB,
        "frozen_gold_blob": GOLD_BLOB,
        "cases": len(rows),
        "correct": correct,
        "confident_errors": [
            x["id"] for x in rows if x["verdict"] != "ABSTAIN" and not x["correct"]
        ],
        "all_certificates_valid": all(x["certificate_valid"] for x in rows),
        "five_sources_discovered": report["source_count"] == 5,
        "fifth_unannotated_and_not_promoted": (
            any(x["id"] == "BR-OBS-CAP-01" and
                x["representation"] == "DISCOVERED_DOCUMENT_ONLY"
                for x in report["inventory"])
            and any(x["id"] == "Q14" and x["verdict"] == "ABSTAIN" for x in rows)
        ),
        "multi_step_with_citations": any(x["id"] == "Q05" and
                                         x["verdict"] == "CONTRADICTED" and
                                         len(x["proof_rule_ids"]) >= 2 for x in rows),
        "protocol_success": correct == 14 and
            all(x["certificate_valid"] for x in rows)
            and not any(x["verdict"] != "ABSTAIN" and not x["correct"] for x in rows)
            and report["source_count"] == 5
            and report["annotated_sources"] == 4,
        "inventory": report["inventory"],
        "source_logic_output_sha256": report["content_sha256"],
        "rows": rows,
        "interpretation_limit": (
            "Gold was authored from the same manual rule contract. Success tests"
            " deterministic serialization, provenance checks and rule semantics,"
            " NOT learning to read source Markdown nor correctness of scientific proofs."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = evaluate()
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            p.error("write report only outside repository")
        target.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
