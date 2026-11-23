"""Forensic-only reader for *consumed* SELF-TEACH-01 outputs.

The original raw output, score and test partition remain immutable. This module
does not run a model, train parameters, or create new generalization evidence.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot
import score

SOURCE_RUN = 45118652661
ARCHIVED_RAW_SHA256 = "7e7088093f4401ab13a6338fe21297bf046c8ef2de535619d3ec5e393edbfa9d"
ARCHIVED_ORIGINAL_SCORE_SHA256 = "cd5f9a3678995c68b7e45300908ceaceb24741af50896a3f520d5153fc99c99a"


def decode_line_delimiters_only(source: str) -> tuple[str | None, str]:
    """Decode literal backslash-n only OUTSIDE Python single/double strings.

    Strict forensic bridge: only if the whole function is on a single physical
    line and begins with the escaped line break after the function signature.
    Never turn literal backslash-n inside Python strings into newlines. Reject
    ambiguous/malformed/triple-quoted code. Always apply the original AST guard.
    """
    if (not isinstance(source, str) or len(source) > pilot.safe.MAX_CODE_CHARS
            or "\n" in source or "\r" in source
            or not source.startswith("def transform(s):\\n")
            or source.count("\\n") > 100
            or "'''" in source or '"""' in source):
        return None, "NOT_NARROW_ESCAPED_LINE_FORMAT"
    out = []
    quote = None
    i = 0
    n = len(source)
    converted = 0
    while i < n:
        c = source[i]
        if quote is not None:
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(source[i+1])
                i += 2
                continue
            if c == quote:
                quote = None
            out.append(c)
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n and source[i+1] == "n":
            out.append("\n")
            converted += 1
            i += 2
            continue
        out.append(c)
        i += 1
    if quote is not None or converted == 0:
        return None, "AMBIGUOUS_ESCAPED_LINE_FORMAT"
    repaired = "".join(out)
    try:
        pilot.safe.validate_program(repaired)
    except ValueError as exc:
        return None, "AST_GUARD_REJECTED:" + str(exc)
    return repaired, "FORMAT_RECOVERED_POST_HOC"


def recover_raw(raw: str) -> tuple[str | None, str]:
    initial, status = pilot.inspect_code(raw)
    if initial is not None:
        return initial, "ORIGINAL_SAFE_NO_CHANGE"
    if status != "UNSAFE_OR_INVALID_CODE:INVALID_PYTHON_SYNTAX":
        return None, status
    parsed = pilot.safe.parse_json(raw)
    code = parsed.get("code") if parsed else None
    if not isinstance(code, str):
        return None, "INVALID_JSON_OR_CODE"
    repaired, marker = decode_line_delimiters_only(code)
    if repaired is None:
        return None, marker
    # NEVER rewrite the model's raw output or claim the model emitted this code.
    return repaired, marker


def posthoc_audit(original_raw: dict, original_score: dict) -> dict:
    if original_raw.get("schema") != pilot.SCHEMA:
        raise ValueError("ORIGINAL_REPORT_INVALID")
    if original_score.get("schema") != "OMEGA_SELF_TEACH_SCORE_01":
        raise ValueError("ORIGINAL_SCORE_INVALID")
    if (original_score.get("A", {}).get("tests_exact") != 0 or
            original_score.get("B", {}).get("tests_exact") != 0):
        raise ValueError("ORIGINAL_SCORE_WAS_NOT_ZERO")
    reconstructed_score = score.score_report(original_raw)
    if (reconstructed_score["A"]["tests_exact"] != 0 or
            reconstructed_score["B"]["tests_exact"] != 0):
        raise ValueError("ORIGINAL_SCORE_MISMATCH")
    gold = pilot.load_frozen("EVAL_SEALED_FROZEN.json")["holdout"]
    arms = {}
    for arm in ("A", "B"):
        rows = []
        for old, target in zip(original_raw[arm], gold):
            if old.get("id") != target["id"] or old.get("family") != target["family"]:
                raise ValueError("ROW_MISMATCH")
            raw = old["raw"]
            if sha256(raw.encode()).hexdigest() != old["sha256_raw"]:
                raise ValueError("UNTRUSTED_RAW_OUTPUT")
            repaired, status = recover_raw(raw)
            if repaired is not None:
                count = pilot.score_public(repaired, target["hidden_cases"])["correct"]
            else:
                count = 0
            rows.append({
                "id": old["id"],
                "origin_raw_sha256": old["sha256_raw"],
                "format_status": status,
                "posthoc_tests_exact": count,
                "tests_total": len(target["hidden_cases"]),
                "repair_provenance": ("FORENSIC_FORMAT_ONLY_NOT_MODEL_LEARNING"
                                      if status == "FORMAT_RECOVERED_POST_HOC"
                                      else "ORIGINAL_OR_REJECTED"),
            })
        arms[arm] = {
            "posthoc_exact": sum(x["posthoc_tests_exact"] for x in rows),
            "format_recovered": sum(x["format_status"] == "FORMAT_RECOVERED_POST_HOC"
                                    for x in rows),
            "rows": rows
        }
    return {
        "schema": "OMEGA_SELF_TEACH_FORMAT_AUDIT_01",
        "status": "RETROSPECTIVE_ON_CONSUMED_TEST_SET",
        "source_run": SOURCE_RUN,
        "original_strict": {"A": 0, "B": 0},
        "forensic_format_normalization": arms,
        "posthoc_delta_B_minus_A": arms["B"]["posthoc_exact"] - arms["A"]["posthoc_exact"],
        "new_llm_calls": 0,
        "new_gradients": 0,
        "new_blind_holdout": False,
        "new_learning_or_generalization_demonstrated": False,
        "original_outputs_unchanged": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--original-score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for path, expected in ((args.raw, ARCHIVED_RAW_SHA256),
                           (args.original_score, ARCHIVED_ORIGINAL_SCORE_SHA256)):
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("ARCHIVED_SOURCE_HASH_MISMATCH")
    report = posthoc_audit(json.loads(args.raw.read_text()),
                           json.loads(args.original_score.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print("POSTHOC_FORMAT_DIAGNOSTIC_NOT_NEW_BENCHMARK",
          "A", report["forensic_format_normalization"]["A"]["posthoc_exact"],
          "B", report["forensic_format_normalization"]["B"]["posthoc_exact"])


if __name__ == "__main__":
    main()
