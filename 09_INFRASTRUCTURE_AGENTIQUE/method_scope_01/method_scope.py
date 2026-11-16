"""OMEGA-SCOPE-METHODS-01: preregistered method-scope candidate coverage.

Both arms reuse frozen PR #104 find_patches. This code never opens the fixed
commit and never executes/imports source code from the third-party checkout.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "blind_real_01"))
from blind_scan import candidate_manifest, sha, MAX_CASE_CANDIDATES
from external_real import CASES, find_patches, one_line_change

BUGGY_COMMIT = "c57512fa669e6f6b1b766a7639206a380f0d10ce"
BENCHMARK_COMMIT = "11c5f1eea954a42132cfd06bf257766a7963e0fd"


def _method_fragment(rows: list[str], method: ast.FunctionDef) -> tuple[str, str]:
    """De-indent exactly the method block to a top-level def.

    No AST change or reimplementation of patch rules is allowed.
    """
    start, end = method.lineno - 1, method.end_lineno
    original_def = rows[start]
    prefix = original_def[:len(original_def) - len(original_def.lstrip())]
    if not prefix or not prefix.isspace() or "\t" in prefix:
        raise ValueError("unsupported method indentation")
    chunk = rows[start:end]
    if any(row.strip() and not row.startswith(prefix) for row in chunk):
        raise ValueError("unsupported nonuniform indentation")
    source = "\n".join(row[len(prefix):] if row.strip() else "" for row in chunk) + "\n"
    tree = ast.parse(source)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("method fragment not a single regular function")
    return prefix, source


def scan_methods(source_root: Path, max_candidates: int = MAX_CASE_CANDIDATES) -> dict:
    base = source_root / "scrapy"
    if not base.is_dir():
        return {"status": "SOURCE_UNAVAILABLE", "candidates": [], "scanned_files": 0,
                "methods_seen": 0, "methods_scanned": 0, "decorated_skipped": 0,
                "async_skipped": 0, "errors": []}
    candidates: list[dict] = []
    seen: set[tuple[str, str]] = set()
    errors = []
    files = methods_seen = methods_scanned = decorated_skipped = async_skipped = 0
    for path in sorted(base.rglob("*.py")):
        if path.is_symlink():
            raise RuntimeError("symlink source is out of allowed scope")
        files += 1
        rel = path.relative_to(source_root).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append({"file": rel, "reason": type(exc).__name__})
            continue
        rows = source.splitlines()
        source_sha = sha(source)
        for klass in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            for node in klass.body:
                if isinstance(node, ast.AsyncFunctionDef):
                    async_skipped += 1
                    continue
                if not isinstance(node, ast.FunctionDef):
                    continue
                methods_seen += 1
                if node.decorator_list:
                    decorated_skipped += 1
                    continue
                try:
                    prefix, fragment = _method_fragment(rows, node)
                except (ValueError, SyntaxError) as exc:
                    errors.append({"file": rel, "scope": klass.name + "." + node.name,
                                   "reason": type(exc).__name__})
                    continue
                methods_scanned += 1
                CASES["_BLIND_SCAN"] = {"function": node.name}
                try:
                    patches = find_patches("_BLIND_SCAN", fragment)
                except (ValueError, SyntaxError) as exc:
                    errors.append({"file": rel, "scope": klass.name + "." + node.name,
                                   "reason": type(exc).__name__})
                    continue
                finally:
                    CASES.pop("_BLIND_SCAN", None)
                for candidate in patches:
                    global_line = node.lineno + candidate["line"] - 1
                    new_line = prefix + candidate["new"]
                    try:
                        updated = one_line_change(source, global_line, new_line)
                    except (ValueError, SyntaxError) as exc:
                        errors.append({"file": rel, "scope": klass.name + "." + node.name,
                                       "reason": "candidate_map_" + type(exc).__name__})
                        continue
                    cand_sha = sha(updated)
                    key = (rel, cand_sha)
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append({
                        "id": f"M{len(candidates):03d}",
                        "file": rel,
                        "scope": klass.name + "." + node.name,
                        "line": global_line,
                        "rule": candidate["rule"],
                        "old": rows[global_line - 1],
                        "new": new_line,
                        "buggy_file_sha256": source_sha,
                        "source_sha256": cand_sha,
                    })
                    if len(candidates) > max_candidates:
                        return {
                            "status": "BUDGET_EXCEEDED",
                            "candidates": candidates[:max_candidates],
                            "total_seen_at_least": len(candidates),
                            "scanned_files": files,
                            "methods_seen": methods_seen,
                            "methods_scanned": methods_scanned,
                            "decorated_skipped": decorated_skipped,
                            "async_skipped": async_skipped,
                            "errors": errors,
                        }
    return {
        "status": "CANDIDATES_UNTESTED" if candidates else "NO_CANDIDATE",
        "candidates": candidates,
        "scanned_files": files,
        "methods_seen": methods_seen,
        "methods_scanned": methods_scanned,
        "decorated_skipped": decorated_skipped,
        "async_skipped": async_skipped,
        "errors": errors,
    }


def compare(source_root: Path, max_candidates: int = MAX_CASE_CANDIDATES) -> dict:
    base = candidate_manifest(source_root, max_candidates=max_candidates)
    method = scan_methods(source_root, max_candidates=max_candidates)
    if base["status"] == "SOURCE_UNAVAILABLE":
        status = "SOURCE_UNAVAILABLE"
    elif base["status"] == "BUDGET_EXCEEDED" or method["status"] == "BUDGET_EXCEEDED":
        status = "BUDGET_EXCEEDED"
    elif base.get("parse_errors") or method["errors"]:
        status = "PARTIAL_COVERAGE_WITH_ERRORS"
    else:
        status = "COVERAGE_INCREASED" if method["candidates"] else "NO_INCREMENTAL_CANDIDATE"
    # Do NOT call this repair success, even when syntactically valid proposals exist.
    return {
        "experiment": "OMEGA-SCOPE-METHODS-01",
        "phase": "BUGGY_ONLY_COVERAGE_COMPARISON",
        "case": "scrapy-1",
        "project": "scrapy/scrapy",
        "buggy_commit": BUGGY_COMMIT,
        "benchmark_commit": BENCHMARK_COMMIT,
        "comparison_status": status,
        "rules": "PR-104 external_real.find_patches (unchanged)",
        "candidate_budget_per_arm": max_candidates,
        "arm_a_top_level": base,
        "arm_b_increment_methods": method,
        "arm_b_total_candidate_count_if_within_budget": (
            len(base["candidates"]) + len(method["candidates"])
            if status not in ("BUDGET_EXCEEDED", "SOURCE_UNAVAILABLE") else None
        ),
        "historical_fixed_accessed": False,
        "public_reproducer_executed": False,
        "reserved_tests_executed": False,
        "model_called": False,
        "repair_correctness": None,
        "scientific_gain_demonstrated": False,
        "main_modified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--buggy-checkout", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if not args.buggy_checkout.is_dir() or "fixed" in args.buggy_checkout.name.lower():
        raise ValueError("expected only a buggy checkout")
    result = compare(args.buggy_checkout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False,
                                      indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["comparison_status"],
        "top_level_count": len(result["arm_a_top_level"]["candidates"]),
        "additional_methods_count": len(result["arm_b_increment_methods"]["candidates"]),
        "methods_seen": result["arm_b_increment_methods"]["methods_seen"],
        "methods_scanned": result["arm_b_increment_methods"]["methods_scanned"],
        "scanned_files": result["arm_b_increment_methods"]["scanned_files"],
        "report_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
