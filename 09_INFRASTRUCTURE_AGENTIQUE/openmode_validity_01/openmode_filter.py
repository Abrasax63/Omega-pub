"""Frozen 40-candidate, source-backed binary-open encoding safety audit.

No third-party modules executed; candidate files are only parsed/hashed.
Raises on drift. Never loads the upstream historical fixed commit.
"""
from __future__ import annotations

import argparse
import ast
import builtins
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "blind_real_01"))
from blind_scan import sha
sys.path.insert(0, str(HERE.parent / "external_real"))
from external_real import one_line_change

FROZEN_MANIFEST_SHA256 = "759ef7231ac1baad6bb4f163db83870c7a417611d7011ca88b827666e6e799b4"
EXPECTED_COUNTS = (8, 32)
EXPECTED_BUGGY_COMMIT = "c57512fa669e6f6b1b766a7639206a380f0d10ce"
MAX_PER_ARM = 60


def _binds_open(n: ast.AST) -> bool:
    """Conservative over-approximation: ambiguous open shadows never rejected."""
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == "open":
        return True
    if isinstance(n, ast.Name) and n.id == "open" and isinstance(n.ctx, (ast.Store, ast.Del)):
        return True
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        for x in n.names:
            if x.asname == "open" or (not x.asname and x.name == "open"):
                return True
    if isinstance(n, ast.arg) and n.arg == "open":
        return True
    if isinstance(n, ast.Global) and "open" in n.names:
        return True
    return False


def extract_open_call(patched: str, line: int) -> tuple[str, str] | tuple[None, str]:
    """Return (mode, encoding) only when patched call clearly resolves to builtin open.

    Keeps conservative UNKNOWN for dynamic modes, nonconstant encodings, aliases,
    multiple open calls and potential rebindings in the enclosing module.
    """
    tree = ast.parse(patched)
    # Global conservative check for any lexical binding named open.
    if any(_binds_open(n) for n in ast.walk(tree)):
        return None, "UNKNOWN_OPEN_BINDING"
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "open" and n.lineno <= line <= n.end_lineno]
    if len(calls) != 1:
        return None, "UNKNOWN_CALLSITE"
    call = calls[0]
    encs = [kw.value for kw in call.keywords if kw.arg == "encoding"]
    if len(encs) != 1 or not isinstance(encs[0], ast.Constant) or not isinstance(encs[0].value, str):
        return None, "UNKNOWN_ENCODING"
    kwmodes = [kw.value for kw in call.keywords if kw.arg == "mode"]
    if len(kwmodes) > 1 or (len(call.args) >= 2 and kwmodes):
        return None, "UNKNOWN_MODE"
    if kwmodes:
        node = kwmodes[0]
    elif len(call.args) >= 2:
        node = call.args[1]
    else:
        node = ast.Constant("r")
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return None, "UNKNOWN_MODE"
    return node.value, encs[0].value


def probe_builtin_open(mode: str, encoding: str) -> dict:
    """Isolated stdlib probe; never imports or runs third-party source."""
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "file"
        # r/rb and r+ require existing file. x/xb must start with no file.
        if "x" not in mode:
            target.write_bytes(b"sample\n")
        try:
            with builtins.open(target, mode, encoding=encoding) as handle:
                if "r" in mode or "+" in mode:
                    handle.read(0)
        except Exception as exc:
            outcome = {"status": "RAISED", "exception": type(exc).__name__}
        else:
            outcome = {"status": "OPEN_OK", "exception": None}
    outcome["duration_ms"] = round((time.perf_counter() - start) * 1000, 4)
    return outcome


def classify_candidate(root: Path, candidate: dict) -> dict:
    rel = candidate["file"]
    path = root / rel
    if path.is_symlink() or not path.is_file() or path.resolve() != (root.resolve() / rel):
        raise ValueError("SOURCE_MISMATCH: missing or symlink source: " + rel)
    source = path.read_text(encoding="utf-8")
    if sha(source) != candidate["buggy_file_sha256"]:
        raise ValueError("SOURCE_MISMATCH: original SHA: " + rel)
    line = candidate["line"]
    rows = source.splitlines()
    if not (1 <= line <= len(rows)) or rows[line - 1] != candidate["old"]:
        raise ValueError("SOURCE_MISMATCH: original line: " + rel)
    updated = one_line_change(source, line, candidate["new"])
    if sha(updated) != candidate["source_sha256"]:
        raise ValueError("SOURCE_MISMATCH: candidate SHA: " + rel)
    extracted = extract_open_call(updated, line)
    if extracted[0] is None:
        return {"status": "UNKNOWN", "reason": extracted[1], "probe": None}
    mode, enc = extracted
    is_binary = "b" in mode
    result = {"status": "REJECT_CERTAIN_BINARY_ENCODING" if is_binary
              else "NOT_REJECTED_STATIC",
              "mode": mode, "encoding": enc}
    result["probe"] = probe_builtin_open(mode, enc)
    if is_binary and (result["probe"]["status"] != "RAISED"
                      or result["probe"]["exception"] != "ValueError"):
        raise AssertionError("FILTER_FALSE_POSITIVE: builtin open did not raise ValueError")
    return result


def audit(root: Path, manifest_bytes: bytes) -> dict:
    if hashlib.sha256(manifest_bytes).hexdigest() != FROZEN_MANIFEST_SHA256:
        raise ValueError("MANIFEST_DRIFT")
    manifest = json.loads(manifest_bytes)
    if manifest.get("buggy_commit") != EXPECTED_BUGGY_COMMIT:
        raise ValueError("MANIFEST_DRIFT: buggy commit")
    arms = [manifest["arm_a_top_level"]["candidates"],
            manifest["arm_b_increment_methods"]["candidates"]]
    if tuple(map(len, arms)) != EXPECTED_COUNTS:
        raise ValueError("MANIFEST_DRIFT: counts")
    if any(len(a) > MAX_PER_ARM for a in arms):
        raise ValueError("BUDGET_EXCEEDED")
    rows = []
    for arm_name, candidates in zip(("top_level", "methods"), arms):
        for item in candidates:
            status = classify_candidate(root, item)
            rows.append({"arm": arm_name, "id": item["id"],
                         "file": item["file"], "line": item["line"],
                         "rule": item["rule"],
                         "source_sha256": item["source_sha256"],
                         **status})
    totals = Counter(r["status"] for r in rows)
    by_arm = {name: Counter(r["status"] for r in rows if r["arm"] == name)
              for name in ("top_level", "methods")}
    return {
        "experiment": "OMEGA-OPENMODE-VALIDITY-01",
        "phase": "RETROSPECTIVE_SAME_CANDIDATES_STATIC_AND_MICROPROBE",
        "source_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "prior_scope_status": manifest["comparison_status"],
        "initial_candidate_count": len(rows),
        "candidate_budget_same": True,
        "generation_rules_modified": False,
        "controls_A": len(rows),
        "controls_B": len(rows),
        "static_filter_rejected_count": totals["REJECT_CERTAIN_BINARY_ENCODING"],
        "static_filter_retained_count": len(rows) - totals["REJECT_CERTAIN_BINARY_ENCODING"],
        "static_filter_unknown_count": totals["UNKNOWN"],
        "by_arm": {k: dict(v) for k, v in by_arm.items()},
        "classifications": rows,
        "reproduction_of_real_bug_executed": False,
        "real_repair_correctness": None,
        "qwen_called": False,
        "scientific_gain_demonstrated": False,
        "main_modified": False,
        "limitations": [
          "Retrospective analysis of candidates already inspected in PR 117.",
          "Stdlib open microprobes do not execute the historical Scrapy bug.",
          "Nonrejected static candidates are not proven executable or correct.",
          "PR 117 method extraction error and excluded scopes remain unresolved.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--buggy-checkout", type=Path, required=True)
    p.add_argument("--frozen-manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if not args.buggy_checkout.is_dir() or "fixed" in args.buggy_checkout.name.lower():
        raise ValueError("SOURCE_UNAVAILABLE")
    result = audit(args.buggy_checkout, args.frozen_manifest.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False,
                                      indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
      "rejected": result["static_filter_rejected_count"],
      "retained": result["static_filter_retained_count"],
      "unknown": result["static_filter_unknown_count"],
      "controls_each": result["controls_A"],
      "status": "STATIC_FILTER_AUDITED_NOT_REAL_BUG_REPAIRED",
      "report_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
