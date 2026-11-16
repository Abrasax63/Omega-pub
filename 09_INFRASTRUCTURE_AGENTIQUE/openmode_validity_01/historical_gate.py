"""Post-freeze real historical bug semantic gate for Scrapy-1.

Not upstream integration tests. Extracts and executes original *unmodified* AST
method get_host_regex from both pinned upstream commits with stdlib-only stubs.
NO generated third-party patch is executed here. All source checking is read-only.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import warnings

FIXED_FILTER_REPORT_SHA256 = "ff7a3c0bce08c890a0f2a7bc23cffe01c87690b29d0ad48543f74d68d67aa9f3"
BUGGY_BLOB = "232e96cbb2df4311767fc168a0d494190e780b83"
FIXED_BLOB = "36f809699d5ad31aae759a79731b5ad29ae8885a"
HISTORICAL_CHANGED_FILE = "scrapy/spidermiddlewares/offsite.py"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def upstream_method(path: Path, expected_blob: str):
    raw = path.read_bytes()
    if git_blob(raw) != expected_blob:
        raise ValueError("HISTORICAL_BLOB_DRIFT")
    tree = ast.parse(raw.decode("utf-8"))
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "OffsiteMiddleware"]
    if len(classes) != 1:
        raise ValueError("HISTORICAL_METHOD_UNAVAILABLE")
    methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef)
               and n.name == "get_host_regex"]
    if len(methods) != 1:
        raise ValueError("HISTORICAL_METHOD_UNAVAILABLE")
    module = ast.fix_missing_locations(ast.Module(body=[methods[0]], type_ignores=[]))
    class URLWarning(Warning):
        pass
    scope = {"re": re, "warnings": warnings, "URLWarning": URLWarning}
    exec(compile(module, "<pinned-upstream-method>", "exec"), scope)
    return scope["get_host_regex"]


def semantic_input(func, domains: list) -> dict:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pattern = func(None, SimpleNamespace(allowed_domains=domains))
        correct = (bool(pattern.fullmatch("scrapytest.org"))
                   and bool(pattern.fullmatch("sub.scrapytest.org"))
                   and not bool(pattern.fullmatch("irrelevant.example")))
        return {"passed": correct,
                "failure": None if correct else "WRONG_DOMAIN_BEHAVIOR"}
    except Exception as error:
        return {"passed": False, "failure": type(error).__name__,
                "message": str(error)[:160]}


def gate(buggy_file: Path, fixed_file: Path, report_bytes: bytes) -> dict:
    if hashlib.sha256(report_bytes).hexdigest() != FIXED_FILTER_REPORT_SHA256:
        raise ValueError("FILTER_REPORT_DRIFT")
    report = json.loads(report_bytes)
    if report["initial_candidate_count"] != 40:
        raise ValueError("FILTER_REPORT_DRIFT")
    if report["static_filter_rejected_count"] != 24:
        raise ValueError("FILTER_REPORT_DRIFT")
    buggy = upstream_method(buggy_file, BUGGY_BLOB)
    fixed = upstream_method(fixed_file, FIXED_BLOB)
    public_domains = ["scrapytest.org", None, None]
    control_domains = ["scrapytest.org"]
    buggy_public = semantic_input(buggy, public_domains)
    fixed_public = semantic_input(fixed, public_domains)
    buggy_control = semantic_input(buggy, control_domains)
    fixed_control = semantic_input(fixed, control_domains)
    confirmed = (not buggy_public["passed"] and buggy_public["failure"] == "TypeError"
                 and fixed_public["passed"] and buggy_control["passed"]
                 and fixed_control["passed"])
    entries = report["classifications"]
    direct = [r["id"] for r in entries if r["file"] == HISTORICAL_CHANGED_FILE]
    filtered_direct = [
        r["id"] for r in entries if r["file"] == HISTORICAL_CHANGED_FILE
        and r["status"] != "REJECT_CERTAIN_BINARY_ENCODING"]
    return {
        "experiment": "OMEGA-OPENMODE-VALIDITY-01",
        "phase": "POST_FREEZE_ORIGINAL_UPSTREAM_SEMANTIC_REPRODUCTION",
        "case": "scrapy-1",
        "buggy_commit": "c57512fa669e6f6b1b766a7639206a380f0d10ce",
        "fixed_commit": "9d9dea0d69709ef0f7aef67ddba1bd7bda25d273",
        "buggy_blob": BUGGY_BLOB, "fixed_blob": FIXED_BLOB,
        "filter_report_sha256": FIXED_FILTER_REPORT_SHA256,
        "historical_method": "OffsiteMiddleware.get_host_regex",
        "historical_changed_file": HISTORICAL_CHANGED_FILE,
        "semantic_reproduction_verified": confirmed,
        "buggy_public": buggy_public, "fixed_public": fixed_public,
        "buggy_control": buggy_control, "fixed_control": fixed_control,
        "raw_candidate_count": len(entries),
        "filtered_candidate_count": report["static_filter_retained_count"],
        "raw_direct_changed_file_candidates": direct,
        "filtered_direct_changed_file_candidates": filtered_direct,
        "raw_direct_changed_file_count": len(direct),
        "filtered_direct_changed_file_count": len(filtered_direct),
        "candidate_repair_executed": False,
        "full_historical_upstream_suite_executed": False,
        "historical_python_3_8_3_executed": False,
        "actual_python_runtime": sys.version.split()[0],
        "reserved_evaluation_executed": False,
        "model_called": False,
        "evidence_limitations": [
          "Original upstream get_host_regex AST executed on small stdlib-only inputs.",
          "No complete Scrapy project dependencies, no official BugsInPy suite, no original Python 3.8.3 environment.",
          "Candidates in other files could in principle change integrated behavior; not tested here.",
          "Only absence of direct patches at the historically changed file is proven.",
        ],
        "scientific_gain_demonstrated": False,
        "main_modified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--buggy-file", type=Path, required=True)
    p.add_argument("--fixed-file", type=Path, required=True)
    p.add_argument("--filter-report", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    out = gate(args.buggy_file, args.fixed_file, args.filter_report.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False,
                                      sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "semantic_reproduced": out["semantic_reproduction_verified"],
        "buggy_public": out["buggy_public"],
        "fixed_public": out["fixed_public"],
        "raw_direct_patches": out["raw_direct_changed_file_count"],
        "filtered_direct_patches": out["filtered_direct_changed_file_count"],
        "full_upstream_tests": False,
        "report_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))
    if not out["semantic_reproduction_verified"]:
        raise SystemExit("REPRODUCER_UNCONFIRMED")


if __name__ == "__main__":
    main()
