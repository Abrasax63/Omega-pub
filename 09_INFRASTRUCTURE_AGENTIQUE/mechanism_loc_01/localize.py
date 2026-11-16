"""OMEGA-MECHANISM-LOC-01: frozen static test-to-code function localization.

Phase A only: source inspection of the pinned BUGGY revision and its PUBLIC test.
This module does not access the historical fixed revision or import target code.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

BUGGY_COMMIT = "001bda19450ad85c91345eea3cfa3991e1d492ba"
CORPUS_COMMIT = "11c5f1eea954a42132cfd06bf257766a7963e0fd"
MAX_REVIEWED_RANK = 20
TEST_PATH = "tests/test_downloads.py"
ROOT_PACKAGE = "httpie"


def sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalized_tokens(value: str) -> set[str]:
    # No NLP model, no stemming except splitting; deterministic case-insensitive.
    return {t for t in re.split(r"[^a-z0-9]+", value.lower()) if t}


def test_signals(raw: str) -> dict:
    tree = ast.parse(raw, filename=TEST_PATH)
    calls, referenced, imports = set(), set(), set()
    test_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id.lower())
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr.lower())
        elif isinstance(node, ast.Name):
            referenced.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            referenced.add(node.attr.lower())
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.update(alias.name.lower().split("."))
                if alias.asname:
                    referenced.add(alias.asname.lower())
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.update(node.module.lower().split("."))
            for alias in node.names:
                imports.add(alias.name.lower())
                if alias.asname:
                    referenced.add(alias.asname.lower())
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.lower().startswith("test_"):
                test_names.add(node.name.lower())
    return {
      "call_names": sorted(calls),
      "referenced_names": sorted(referenced),
      "import_segments": sorted(imports),
      "test_names": sorted(test_names),
    }


def collect_targets(checkout: Path) -> tuple[list[dict], dict, list[str]]:
    package = checkout / ROOT_PACKAGE
    if not package.is_dir():
        return [], {}, ["SOURCE_UNAVAILABLE: httpie package missing"]
    found, hashes, errors = [], {}, []
    for path in sorted(package.rglob("*.py")):
        if path.is_symlink():
            errors.append("SYMLINK_REJECTED:" + str(path.relative_to(checkout)))
            continue
        rel = path.relative_to(checkout).as_posix()
        try:
            raw = path.read_bytes()
            code = raw.decode("utf-8")
            tree = ast.parse(code, filename=rel)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            errors.append(rel + ":" + type(exc).__name__)
            continue
        hashes[rel] = sha(raw)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.append(_target(rel, "", node, "top_level"))
            elif isinstance(node, ast.ClassDef):
                for m in node.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        found.append(_target(rel, node.name, m, "method"))
    return found, hashes, errors


def _target(rel: str, class_name: str, node: ast.AST, kind: str) -> dict:
    qn = (class_name + "." if class_name else "") + node.name
    return {
      "key": rel + "::" + qn + "@" + str(node.lineno),
      "file": rel,
      "function": node.name,
      "class_name": class_name,
      "qualname": qn,
      "kind": kind,
      "line": node.lineno,
      "end_line": node.end_lineno,
    }


def score(t: dict, signals: dict) -> tuple[int, dict]:
    calls = set(signals["call_names"])
    referenced = set(signals["referenced_names"])
    imports = set(signals["import_segments"])
    fname = t["function"].lower()
    cls = t["class_name"].lower()
    module = Path(t["file"]).stem.lower()
    call_tokens = set().union(*(normalized_tokens(name) for name in calls)) if calls else set()
    qtokens = normalized_tokens(t["qualname"])
    test_stem = Path(TEST_PATH).stem.lower()
    signals_found = {
      "direct_call": 5 if fname in calls else 0,
      "class_mentioned": 3 if cls and cls in referenced else 0,
      "module_imported": 2 if module in imports else 0,
      "common_tokens": min(3, len(qtokens & call_tokens)),
      "download_stem": 1 if "download" in module and "download" in test_stem else 0,
    }
    return sum(signals_found.values()), signals_found


def rank(checkout: Path) -> dict:
    test_file = checkout / TEST_PATH
    if not test_file.is_file() or test_file.is_symlink():
        return {"status": "NO_TEST_SOURCE", "targets": [], "error": TEST_PATH}
    try:
        raw = test_file.read_bytes()
        public_signals = test_signals(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        return {"status": "SOURCE_PARSE_ERROR", "targets": [],
                "error": "TEST:" + type(error).__name__}
    targets, hashes, errors = collect_targets(checkout)
    if errors:
        return {"status": "SOURCE_PARSE_ERROR", "targets": [],
                "errors": errors, "source_hashes": hashes}
    if not targets:
        return {"status": "NO_FUNCTIONS", "targets": [], "source_hashes": hashes}
    scored = []
    for t in targets:
        value, factors = score(t, public_signals)
        scored.append(dict(t, score_b=value, factors=factors))
    a_sorted = sorted(scored, key=lambda x: (
        0 if x["kind"] == "top_level" else 1, x["file"], x["line"], x["qualname"]))
    b_sorted = sorted(scored, key=lambda x: (
        -x["score_b"], x["file"], x["line"], x["qualname"]))
    rank_a = {t["key"]: i + 1 for i,t in enumerate(a_sorted)}
    rank_b = {t["key"]: i + 1 for i,t in enumerate(b_sorted)}
    final = [dict(t, rank_a=rank_a[t["key"]], rank_b=rank_b[t["key"]])
             for t in sorted(scored, key=lambda t: t["key"])]
    return {
      "status": "CHOICES_FROZEN",
      "experiment": "OMEGA-MECHANISM-LOC-01",
      "phase": "BUGGY_ONLY_TEST_AST_LOCALIZATION",
      "bugsinpy_case": "httpie-1",
      "project": "jakubroztocil/httpie",
      "buggy_commit": BUGGY_COMMIT,
      "corpus_commit": CORPUS_COMMIT,
      "test_file": TEST_PATH,
      "test_sha256": sha(raw),
      "source_file_hashes": hashes,
      "signals": public_signals,
      "total_targets": len(targets),
      "budget_primary": 10,
      "secondary_budgets": [5, 20],
      "targets": final,
      "top_a": [dict(key=t["key"], rank=rank_a[t["key"]]) for t in a_sorted[:MAX_REVIEWED_RANK]],
      "top_b": [dict(key=t["key"], rank=rank_b[t["key"]], score=t["score_b"])
                for t in b_sorted[:MAX_REVIEWED_RANK]],
      "historic_fixed_accessed": False,
      "fixed_diff_accessed": False,
      "actual_test_executed": False,
      "model_called": False,
      "repair_attempted": False,
      "main_modified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--buggy-checkout", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = rank(args.buggy_checkout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2)
                           + "\n", encoding="utf-8")
    print(json.dumps({
      "status": result["status"], "target_count": result.get("total_targets"),
      "a_top10": [x["key"] for x in result.get("top_a", [])[:10]],
      "b_top10": [x["key"] for x in result.get("top_b", [])[:10]],
      "sha256": sha(args.output.read_bytes()),
    }, ensure_ascii=False))
    if result["status"] != "CHOICES_FROZEN":
        raise SystemExit("SOURCE_OR_TEST_UNAVAILABLE")


if __name__ == "__main__":
    main()
