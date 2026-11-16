"""Frozen PR #104 AST grammar applied to an unseen buggy checkout.

Phase A only. Never reads a historical fixed checkout, test oracle or model output.
No import/execution of third-party project code.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "external_real"))
from external_real import CASES, find_patches  # frozen engine from PR #104

MAX_CASE_CANDIDATES = 60
BUGGY_SHA = "766157bfb4e7dfccba09ab398e8ec444d14e947c"
BENCHMARK_SHA = "11c5f1eea954a42132cfd06bf257766a7963e0fd"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def candidate_manifest(source_root: Path, max_candidates: int = MAX_CASE_CANDIDATES) -> dict:
    """Inspect only root/fastapi/*.py, never any fixed tree or test oracle."""
    base = source_root / "fastapi"
    if not base.is_dir():
        return {"status": "SOURCE_UNAVAILABLE", "reason": "missing fastapi source package",
                "candidates": [], "scanned_files": 0, "parse_errors": []}
    proposals = []
    errors = []
    examined = 0
    try:
        for path in sorted(base.rglob("*.py")):
            if path.is_symlink():
                raise RuntimeError("untrusted symlink")
            examined += 1
            rel = path.relative_to(source_root).as_posix()
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (UnicodeError, SyntaxError, OSError) as error:
                errors.append({"file": rel, "reason": type(error).__name__})
                continue
            # The frozen generator only acts on top-level functions.
            names = sorted({node.name for node in tree.body if isinstance(node, ast.FunctionDef)})
            for name in names:
                # Ambiguous names are not silently resolved.
                if sum(1 for node in tree.body
                       if isinstance(node, ast.FunctionDef) and node.name == name) != 1:
                    continue
                # Temporary metadata selects the function; rules themselves are unchanged.
                CASES["_BLIND_SCAN"] = {"function": name}
                try:
                    found = find_patches("_BLIND_SCAN", source)
                except (ValueError, SyntaxError) as error:
                    errors.append({"file": rel, "function": name,
                                   "reason": type(error).__name__})
                    continue
                finally:
                    CASES.pop("_BLIND_SCAN", None)
                for patch in found:
                    proposals.append({
                        "id": f"P{len(proposals):02d}",
                        "file": rel,
                        "function": name,
                        "line": patch["line"],
                        "rule": patch["rule"],
                        "old": patch["old"],
                        "new": patch["new"],
                        "source_sha256": patch["sha256"],
                        "buggy_file_sha256": sha(source),
                    })
                    if len(proposals) > max_candidates:
                        return {"status": "BUDGET_EXCEEDED",
                                "candidates": proposals[:max_candidates],
                                "total_seen_at_least": len(proposals),
                                "scanned_files": examined, "parse_errors": errors,
                                "max_candidates": max_candidates}
    finally:
        CASES.pop("_BLIND_SCAN", None)
    return {
        "status": "NO_CANDIDATE" if not proposals else "CANDIDATES_UNTESTED",
        "candidates": proposals,
        "scanned_files": examined,
        "parse_errors": errors,
        "max_candidates": max_candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--buggy-checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # An attacker-controlled fixed source path must never be accepted.
    if not args.buggy_checkout.is_dir() or "fixed" in args.buggy_checkout.name.lower():
        raise ValueError("must provide a buggy-only checkout")
    result = candidate_manifest(args.buggy_checkout)
    result.update({
        "experiment": "OMEGA-BLIND-REAL-01",
        "phase": "BUGGY_ONLY_GENERATION",
        "upstream_project": "tiangolo/fastapi",
        "bugsinpy_case": "fastapi-1",
        "buggy_commit": BUGGY_SHA,
        "benchmark_commit": BENCHMARK_SHA,
        "frozen_grammar": "PR-104 external_real.find_patches",
        "historical_fixed_accessed": False,
        "model_called": False,
        "public_reproducer_executed": False,
        "reserved_tests_executed": False,
        "repair_correctness": None,
        "model_advantage_demonstrated": False,
        "main_modified": False,
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                      ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "phase": result["phase"], "status": result["status"],
        "candidate_count": len(result["candidates"]),
        "scanned_files": result["scanned_files"],
        "parse_error_count": len(result["parse_errors"]),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
