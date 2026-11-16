"""Bounded, source-only A/B/C patch candidate construction for five real defects.

This program never fetches fixed source or its diff. Selection uses buggy source,
possibly genuine failing-test traces, and the public regression test AST.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "trace_repair"))
from bounded_patch import proposals_for_source, rewrite, sha
from rank_suspects import parse_call_trace, test_symbols

MAX_POOL = 90
MAX_PER_ARM = 4
MAX_FILES = 120
PACKAGES = {"tqdm": "tqdm", "cookiecutter": "cookiecutter", "httpie": "httpie"}
CASE_IDS = ("N1", "N2", "N3", "N4", "N5")
ARMS = ("A_lexical_symbolic", "B_trace_symbolic", "C_trace_symbolic_plus_qwen")


def _candidate_pool(buggy_root: Path, package: str, traces=None, tokens=None):
    """Same pool for all arms: union top-45 lexical and top-45 trace-guided."""
    root = Path(buggy_root).resolve()
    package_dir = root / PACKAGES[package]
    if not package_dir.is_dir():
        raise RuntimeError("package not found in buggy checkout: " + package)
    files = sorted(p for p in package_dir.rglob("*.py")
                   if not any(part.lower() in ("tests", "test", "__pycache__")
                              for part in p.relative_to(root).parts))[:MAX_FILES]
    file_hits = {}
    function_hits = {}
    for item in traces or []:
        rel = f"{PACKAGES[package]}/{item['path']}"
        file_hits[rel] = int(item["total_calls"])
        for fn in item.get("functions", []):
            function_hits[(rel, fn["label"].split("@", 1)[0])] = fn["calls"]
    token_set = set(tokens or [])
    pool = []
    seen = set()
    for file in files:
        rel = file.relative_to(root).as_posix()
        source = file.read_text(encoding="utf-8", errors="replace")
        for cand in proposals_for_source(source):
            if cand["source_sha256"] in seen:
                continue
            seen.add(cand["source_sha256"])
            change = {row["line"]: row["after"] for row in cand["changes"]}
            if len(change) > 2 or len(set(change)) != len(change):
                raise ValueError("patch exceeds frozen grammar")
            if sha(rewrite(source, change)) != cand["source_sha256"]:
                raise RuntimeError("patch SHA cannot be reproduced")
            trace_score = (30 if rel in file_hits else 0)
            trace_score += (10 if cand["function_name"] in token_set else 0)
            trace_score += (5 if (rel, cand["function_name"]) in function_hits else 0)
            pool.append({
                "path": rel, "line": min(cand["lines"]),
                "function": cand["function_name"],
                "function_start_line": cand["function_start_line"],
                "rule": cand["rule"], "changes": cand["changes"],
                "source_sha256": sha(source),
                "modified_sha256": cand["source_sha256"],
                "trace_score": trace_score,
            })
    lexical = sorted(pool, key=lambda x: (x["path"], x["line"], x["rule"], x["modified_sha256"]))
    guided = sorted(pool, key=lambda x: (-x["trace_score"], x["path"], x["line"], x["modified_sha256"]))
    if traces:
        common = lexical[:45] + guided[:45]
    else:
        common = lexical[:MAX_POOL]
    unique = {}
    for item in common:
        unique.setdefault((item["path"], item["modified_sha256"]), item)
    selected = sorted(unique.values(), key=lambda x: (x["path"], x["line"], x["modified_sha256"]))
    for idx, row in enumerate(selected):
        row["id"] = f"P{idx:03d}"
    return selected


def frozen_orders(candidates, trace_verified):
    if len(candidates) > MAX_POOL or len({x["id"] for x in candidates}) != len(candidates):
        raise ValueError("candidate pool limit or ID duplication")
    a = sorted(candidates, key=lambda x: (x["path"], x["line"], x["modified_sha256"]))
    b = sorted(candidates, key=lambda x: (-x["trace_score"], x["path"], x["line"], x["modified_sha256"]))
    if not trace_verified:
        return {"A_lexical_symbolic": [x["id"] for x in a[:MAX_PER_ARM]],
                "B_trace_symbolic": [], "C_trace_symbolic_plus_qwen": []}
    return {"A_lexical_symbolic": [x["id"] for x in a[:MAX_PER_ARM]],
            "B_trace_symbolic": [x["id"] for x in b[:MAX_PER_ARM]],
            "C_trace_symbolic_plus_qwen": [x["id"] for x in b[:12]]}


def model_select(raw_response, allowed):
    """Select one exact candidate ID from a fixed 12-item shortlist, or abstain."""
    if len(raw_response) > 2000:
        return None
    s = raw_response.strip()
    # Prompt echo/extra commentary is NOT accepted. No silent fallback.
    if not re.fullmatch(r"P[0-9]{3}", s):
        return None
    return s if s in allowed else None


def final_model_order(b_order, shortlist, selected_id):
    """Reorder at most the original four symbolic trials; do not expand budget."""
    if selected_id is None or selected_id not in shortlist:
        return []
    return [selected_id] + [i for i in b_order if i != selected_id][:MAX_PER_ARM - 1]


def freeze_case(case, buggy_root, traceback_text="", test_source=""):
    root = Path(buggy_root).resolve()
    if case["id"] not in CASE_IDS:
        raise ValueError("case not part of frozen five")
    if not test_source:
        return {"id": case["id"], "status": "MISSING_PUBLIC_TEST",
                "candidates": [], "orders": {}, "buggy_only": True}
    try:
        test_name = case["test_id"].split("::")[-1]
        evidence = test_symbols(test_source, test_name)
        tokens = evidence["symbols"]
    except (ValueError, SyntaxError) as e:
        return {"id": case["id"], "status": "TEST_AST_UNAVAILABLE",
                "error": str(e), "candidates": [], "orders": {}, "buggy_only": True}
    try:
        trace = parse_call_trace(traceback_text)
        trace_verified = True
    except (ValueError, KeyError, json.JSONDecodeError):
        trace, trace_verified = [], False
    pool = _candidate_pool(root, case["project"], trace, tokens)
    orders = frozen_orders(pool, trace_verified)
    return {
        "id": case["id"], "status": "TRACE_AVAILABLE" if trace_verified else "TRACE_UNAVAILABLE",
        "buggy_sha": case["buggy_sha"], "source_files_scanned_limit": MAX_FILES,
        "candidate_count": len(pool), "trace_verified": trace_verified,
        "test_symbols": tokens, "candidate_pool_sha256": sha(
            json.dumps(pool, sort_keys=True, ensure_ascii=False)),
        "candidates": pool, "orders": orders,
        "buggy_only": True, "fixed_source_seen": False,
    }


def verify_manifest(manifest, cohort):
    if manifest.get("experiment") != cohort["experiment"] or len(manifest.get("cases", [])) != 5:
        raise ValueError("cohort mismatch")
    for row, cas in zip(manifest["cases"], cohort["cases"]):
        if row["id"] != cas["id"] or row.get("buggy_sha") != cas["buggy_sha"]:
            raise ValueError("source SHA mismatch")
        if row["candidate_count"] > MAX_POOL or row.get("fixed_source_seen"):
            raise ValueError("invalid blind-patch commitment")
        cids = {x["id"] for x in row["candidates"]}
        for arm, ids in row["orders"].items():
            if arm not in ARMS or len(ids) > (12 if arm == ARMS[2] else 4):
                raise ValueError("unknown arm or budget exceeded")
            if not set(ids) <= cids:
                raise ValueError("selected candidate not in frozen pool")
    return True
