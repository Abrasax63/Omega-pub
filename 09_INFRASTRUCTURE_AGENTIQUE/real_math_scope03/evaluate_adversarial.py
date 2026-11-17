#!/usr/bin/env python3
"""Fixed-engine adversarial rewording check. No changes to the engine permitted.

Manual labels are only read after all predictions have been generated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from engine import ROOT, evaluate_case, verify_sources

HERE = Path(__file__).resolve().parent
INPUT = HERE / "ADVERSARIAL_INPUTS_FROZEN.json"
GOLD = HERE / "ADVERSARIAL_GOLD_FROZEN.json"
IN_BLOB = "61e8a25e1aa120d6479d5760e60a4ba470cb99ee"
GOLD_BLOB = "6453ba472b20aaece97ad240e21d712e06306140"


def load(path: Path, blob: str) -> dict:
    data = path.read_bytes()
    found = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if found != blob:
        raise ValueError("frozen adversarial fixture changed: " + path.name)
    return json.loads(data.decode("utf-8"))


def run() -> dict:
    docs = verify_sources(ROOT)
    inp = load(INPUT, IN_BLOB)
    predictions = {c["id"]: evaluate_case(c, docs) for c in inp["cases"]}
    marks = {c["id"]: c for c in load(GOLD, GOLD_BLOB)["cases"]}
    if len(predictions) != 12 or len(marks) != 12 or set(marks) != set(predictions):
        raise ValueError("adversarial cohort misaligned")
    rows = []
    for item in inp["cases"]:
        id = item["id"]
        observed = predictions[id]
        gold = marks[id]
        if gold["source_id"] != item["source_id"]:
            raise ValueError("source mismatch")
        # A deliberately conservative warning: words written as number names
        # can cause the original engine to read the previous N/h/t as claim.
        number_words = ("un", "deux", "trois", "quatre", "cinq", "six", "sept",
                        "huit", "neuf", "dix", "douze", "seize")
        textual_numbers = sorted({w for w in number_words
                                  if re.search(r"\b"+w+r"\b", item["question"].casefold())})
        rows.append({
            "id": id, "source_id": item["source_id"],
            "question": item["question"], "gold": gold["verdict"],
            "gold_reason": gold["rationale"],
            "engine": observed["verdict"], "engine_reason": observed["reason"],
            "finite_case": observed.get("finite_case"),
            "number_words_diagnostic": textual_numbers,
            "correct": observed["verdict"] == gold["verdict"],
            "confident_error": observed["verdict"] != "ABSTAIN"
                               and observed["verdict"] != gold["verdict"],
        })
    count = sum(r["correct"] for r in rows)
    confident = [r["id"] for r in rows if r["confident_error"]]
    success = count >= 9 and not confident
    return {
        "status": "POSTHOC_SAFETY_PATCH_REPLAY_NOT_HOLDOUT",
        "frozen_engine_version": inp["engine_sha"],
        "engine_source_changed": True,
        "actual_engine_blob": "4e4bf62de81bea0eebe1a7a80562e002698d0cd2",
        "input_blob": IN_BLOB, "gold_blob": GOLD_BLOB,
        "cases": len(rows), "correct": count,
        "incorrect": len(rows)-count, "confident_errors": confident,
        "preregistered_transfer_criterion_met": success,
        "limitations": "Historical adversarial results used to design this patch. Replaying them is POST-HOC regression evidence only, NOT an unseen score. Safety abstentions may decrease raw accuracy.",
        "rows": rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = run()
    output = json.dumps(result, ensure_ascii=False, indent=2)+"\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("write results outside repository")
        dest.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
