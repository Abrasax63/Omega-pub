#!/usr/bin/env python3
"""Post-hoc model-scope repair audit; not an independent holdout."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from bridge import HERE, ROOT, load_bridge, run
from oracle import exact_boolean_verdict

RULE_PATH = HERE / "RULES_SCOPE_V2.json"
RULE_SHA = "7d1070f0f03d092d6e9678f2e2c2981e748f64d4"
INPUT = HERE / "QUERIES_SCOPE_V2.json"
INPUT_SHA = "0adf5495d15563a0d9c4f0f5dfc9e9f754a07cae"
GOLD = HERE / "GOLD_SCOPE_V2.json"
GOLD_SHA = "eef5a69da7882a0fd16dcd6f31efa8bf48559ddc"


def frozen(path: Path, expected: str) -> dict:
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()
    if actual != expected:
        raise ValueError("posthoc scope input changed: " + path.name)
    return json.loads(data.decode("utf-8"))


def evaluate() -> dict:
    queries = frozen(INPUT, INPUT_SHA)["queries"]
    report = run(queries, rule_path=RULE_PATH, expected_blob=RULE_SHA)
    _, rules = load_bridge(rule_path=RULE_PATH, expected_rule_blob=RULE_SHA)
    independent = {q["id"]: exact_boolean_verdict(q, rules.get(q["source_id"], []))
                   for q in queries}
    labels = {g["id"]: g["verdict"] for g in frozen(GOLD, GOLD_SHA)["targets"]}
    if len(queries) != 16 or len(labels) != 16 or set(labels) != {q["id"] for q in queries}:
        raise ValueError("scope v2 case alignment invalid")
    rows = []
    for answer in report["answers"]:
        id = answer["query_id"]
        rows.append({
            "id": id, "verdict": answer["verdict"], "expected": labels[id],
            "independent_oracle": independent[id]["verdict"],
            "proof_verified": answer["certificate_valid"],
            "reason": answer["reason"],
            "missing_assumptions": answer["missing_assumptions"],
        })
    accepted = all(r["verdict"] == r["expected"] == r["independent_oracle"]
                   and r["proof_verified"] for r in rows)
    controls = all(next(r for r in rows if r["id"] == id)["verdict"] == "ABSTAIN"
                   and "reference_model" in next(r for r in rows if r["id"] == id)["missing_assumptions"]
                   for id in ("Q15", "Q16"))
    return {
        "status": "POSTHOC_MODEL_SCOPE_REPAIR_STRUCTURAL_ONLY",
        "rules_v2_blob": RULE_SHA,
        "preserved_v1_rules_blob": "34e32f63beb90e5dd0528148141b650ba8d9d848",
        "input_blob": INPUT_SHA, "gold_blob": GOLD_SHA,
        "count": len(rows), "matching_gold_and_independent_oracle": sum(
            r["verdict"] == r["expected"] == r["independent_oracle"] for r in rows),
        "reference_model_guard_cases_abstain": controls,
        "certificates_all_valid": all(r["proof_verified"] for r in rows),
        "posthoc_safety_criterion": bool(accepted and controls),
        "limitations": "V2 introduced after an identified human-rule overgeneralization; 16 cases are a posthoc conformance test, NOT an unseen scientific benchmark. Interpreted rules remain unreviewed.",
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate()
    content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            parser.error("write reports outside repository")
        target.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
