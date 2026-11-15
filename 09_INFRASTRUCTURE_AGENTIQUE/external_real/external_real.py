"""OMEGA-EXTERNAL-REAL-01: source-backed historical bug reproductions.

Not full project suites. Each check compiles the *actual upstream function AST*
from pinned commits with minimal standard-library stubs. Runtime should be a
Docker container with --network none and a read-only mounted checkout.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import re
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
CASES = {
    "E1": {
        "repo": "cool-RR/PySnooper",
        "bug": "PySnooper-3",
        "buggy": "6e3d797be3fa0a746fb5b1b7c7fea78eb926c208",
        "fixed": "15555ed760000b049aff8fecc79d29339c1224c3",
        "path": "pysnooper/pysnooper.py",
        "function": "get_write_function",
        "buggy_blob": "8d0c6a724024b07910ebc2492dc4e53234937d83",
        "fixed_blob": "19139d3a0f6ecfe558ce78ffeffa123ee3caae93",
        "description": "Write trace text to the supplied file path",
    },
    "E2": {
        "repo": "tqdm/tqdm",
        "bug": "tqdm-1",
        "buggy": "8cc777fe8401a05d07f2c97e65d15e4460feab88",
        "fixed": "c0dcf39b046d1b4ff6de14ac99ad9a1b10487512",
        "path": "tqdm/contrib/__init__.py",
        "function": "tenumerate",
        "buggy_blob": "1dddacf45ff6abda47d63ab753b73c4529e7a0ba",
        "fixed_blob": "935ab63be7d8c18801386e2aa81027a7b535da4e",
        "description": "Respect the start index when enumerating a sequence",
    },
    "E3": {
        "repo": "cookiecutter/cookiecutter",
        "bug": "cookiecutter-1",
        "buggy": "c15633745df6abdb24e02746b82aadb20b8cdf8c",
        "fixed": "7f6804c4953a18386809f11faf4d86898570debc",
        "path": "cookiecutter/generate.py",
        "function": "generate_context",
        "buggy_blob": "37365a496f5b03c2ef5c623689db87607e64b377",
        "fixed_blob": "c526b97db5f01f659bd31626fc23abfd007bcf0c",
        "description": "Load non-ASCII JSON text when system encoding is cp1252",
    },
}
MAX_CANDIDATES = 60


def digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def source_file(case_id: str, version: str) -> Path:
    if case_id not in CASES or version not in ("buggy", "fixed"):
        raise ValueError("unrecognized case")
    return HERE / "upstream" / case_id / (version + ".py")


def load_source(case_id: str, version: str) -> str:
    path = source_file(case_id, version)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    text = path.read_text(encoding="utf-8")
    # Git blob hashes are checked by the upstream fetch step and by git hash-object
    # in CI. Do not claim this string SHA256 equals a Git object SHA1.
    ast.parse(text)
    return text


def extract_function(source: str, name: str):
    tree = ast.parse(source)
    found = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name == name]
    if len(found) != 1:
        raise ValueError("upstream named function missing or ambiguous")
    return found[0]


def semantic_function(case_id: str, source: str):
    """Compile the unchanged upstream function AST, not a hand-coded replica."""
    spec = CASES[case_id]
    node = extract_function(source, spec["function"])
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    namespace = {"__builtins__": __builtins__}
    if case_id == "E1":
        namespace.update(
            sys=sys, pycompat=types.SimpleNamespace(PathLike=os.PathLike),
            utils=types.SimpleNamespace(WritableStream=io.IOBase),
        )
    elif case_id == "E2":
        # Intentionally replace tqdm's progress rendering, not its indexing.
        def passthrough(iterable, *args, **kwargs):
            return iterable
        namespace["tqdm_auto"] = passthrough
    else:
        from collections import OrderedDict
        real_open = builtins.open
        def simulated_windows_open(*args, **kwargs):
            kwargs.setdefault("encoding", "cp1252")
            return real_open(*args, **kwargs)
        namespace.update(
            OrderedDict=OrderedDict, json=json, os=os,
            logger=logging.getLogger("external-context-test"),
            open=simulated_windows_open,
            ContextDecodingException=ValueError,
            apply_overwrites_to_context=lambda *args: None,
        )
    exec(compile(module, "<pinned-original-function>", "exec"), namespace)
    return namespace[spec["function"]]


def semantic_cases(case_id: str, phase: str):
    """Frozen development and held-out inputs; no candidate determines them."""
    if phase not in ("public", "reserved"):
        raise ValueError("bad phase")
    if case_id == "E1":
        return [["public trace"]] if phase == "public" else [
            ["first", "réserve éèà"], ["two messages", "second line"]
        ]
    if case_id == "E2":
        return [(list(range(3)), 42)] if phase == "public" else [
            (["a", "b"], 99), ([], 7), ([2, 4], 0)
        ]
    return [{"full_name": "éèà"}] if phase == "public" else [
        {"name": "日本語", "symbol": "Ω"},
        {"name": "Москва", "tag": "π"},
    ]


def execute_semantic(case_id: str, source: str, phase: str) -> dict:
    try:
        fun = semantic_function(case_id, source)
        inputs = semantic_cases(case_id, phase)
        for idx, case in enumerate(inputs):
            if case_id == "E1":
                with tempfile.TemporaryDirectory() as d:
                    target = str(Path(d) / "out.log")
                    writer = fun(target)
                    for text in case:
                        writer(text)
                    got = Path(target).read_text(encoding="utf-8")
                    if got != "".join(case):
                        return {"passed": False, "test": idx, "failure": "WRONG_FILE_CONTENT"}
            elif case_id == "E2":
                sequence, start = case
                def dummy_tqdm(iterable, *args, **kwargs):
                    return iterable
                got = list(fun(sequence, start=start, tqdm_class=dummy_tqdm))
                if got != list(enumerate(sequence, start)):
                    return {"passed": False, "test": idx, "failure": "WRONG_INDEX_START"}
            else:
                with tempfile.TemporaryDirectory() as d:
                    file = Path(d) / "context.json"
                    file.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
                    got = fun(str(file))
                    if got != {"context": case}:
                        return {"passed": False, "test": idx, "failure": "WRONG_UNICODE_DECODING"}
        return {"passed": True, "cases_passed": len(inputs)}
    except Exception as exc:
        return {"passed": False, "failure": type(exc).__name__,
                "message": str(exc)[:140]}


def one_line_change(source: str, line_number: int, new_line: str) -> str:
    rows = source.splitlines(keepends=True)
    if line_number < 1 or line_number > len(rows):
        raise ValueError("wrong patch location")
    old = rows[line_number - 1].rstrip("\r\n")
    if old == new_line:
        raise ValueError("unchanged source")
    rows[line_number - 1] = new_line + "\n"
    updated = "".join(rows)
    ast.parse(updated)
    diff = [i for i, (a, b) in enumerate(zip(
        source.splitlines(), updated.splitlines()), 1) if a != b]
    if diff != [line_number] or len(source.splitlines()) != len(updated.splitlines()):
        raise ValueError("patch outside allowed single-line budget")
    return updated


def find_patches(case_id: str, source: str) -> list[dict]:
    """AST-guided generic rules; receives source only, never historical patch."""
    if case_id not in CASES:
        raise ValueError("bad case")
    spec = CASES[case_id]
    function = extract_function(source, spec["function"])
    rows = source.splitlines()
    changes = []
    def add(node, updated, rule):
        if node.lineno < 1 or node.lineno > len(rows):
            return
        try:
            changed = one_line_change(source, node.lineno, updated)
        except (SyntaxError, ValueError):
            return
        changes.append({
            "line": node.lineno, "rule": rule,
            "old": rows[node.lineno - 1], "new": updated,
            "sha256": digest(changed), "source": changed,
        })

    for node in ast.walk(function):
        if not hasattr(node, "lineno") or node.lineno > len(rows):
            continue
        original_line = rows[node.lineno - 1]
        indentation = original_line[:len(original_line) - len(original_line.lstrip())]

        # Generic unbound-name substitution near open(). The candidate pool
        # is drawn from locally visible arguments, NOT upstream fixed diffs.
        if isinstance(node, ast.With):
            for item in node.items:
                call = item.context_expr
                if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                    continue
                if call.func.id != "open" or not call.args:
                    continue
                first = call.args[0]
                if isinstance(first, ast.Name):
                    var = first.id
                    arg_names = sorted({arg.arg for f in ast.walk(function)
                                        if isinstance(f, ast.FunctionDef)
                                        for arg in f.args.args})
                    if re.search(r"\b" + re.escape(var) + r"\b", original_line):
                        for alt in arg_names:
                            if alt == var:
                                continue
                            for mode in ("a", "w"):
                                replacement = re.sub(
                                    r"\bopen\(" + re.escape(var) + r"\s*,\s*'a'\)",
                                    "open(" + alt + ", '" + mode + "')",
                                    original_line, count=1)
                                if replacement != original_line:
                                    add(node, replacement, "lexical-name-substitution")
                # Generic explicit encoding alternatives for file reads.
                if not any(kw.arg == "encoding" for kw in call.keywords):
                    for enc in ("latin-1", "utf-8", "cp1252", "ascii"):
                        call_src = ast.get_source_segment(source, call)
                        if not call_src:
                            continue
                        replacement = original_line.replace(
                            call_src, call_src[:-1] + ", encoding='" + enc + "')", 1)
                        if replacement != original_line:
                            add(node, replacement, "encoding-explicit")

        # Generic normalization of nested enumerate wrapper's start argument.
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            outer = node.value
            if isinstance(outer.func, ast.Name) and outer.func.id == "enumerate":
                if len(outer.args) == 1 and isinstance(outer.args[0], ast.Call):
                    inner = outer.args[0]
                    if len(inner.args) >= 2:
                        remaining = [ast.unparse(x) for x in inner.args[:1] + inner.args[2:]]
                        remaining += [ast.unparse(k) for k in inner.keywords]
                        inner_out = ast.unparse(inner.func) + "(" + ", ".join(remaining) + ")"
                        start = ast.unparse(inner.args[1])
                        for selected_start in (start, "0", "(" + start + " + 1)"):
                            replacement = indentation + "return enumerate(" + inner_out
                            if selected_start != "0":
                                replacement += ", " + selected_start
                            replacement += ")"
                            add(node, replacement, "nested-enumerate-argument")
    out = []
    seen = set()
    for item in changes:
        if item["sha256"] in seen:
            continue
        seen.add(item["sha256"])
        item["id"] = "P" + str(len(out)).zfill(2)
        out.append(item)
        if len(out) > MAX_CANDIDATES:
            raise RuntimeError("hypothesis budget exceeded")
    return out


def study_case(case_id: str) -> dict:
    old = load_source(case_id, "buggy")
    fixed = load_source(case_id, "fixed")
    buggy_public = execute_semantic(case_id, old, "public")
    fixed_public = execute_semantic(case_id, fixed, "public")
    fixed_reserved = execute_semantic(case_id, fixed, "reserved")
    if buggy_public["passed"] or not fixed_public["passed"] or not fixed_reserved["passed"]:
        return {
            "case": case_id, "status": "REPRODUCER_UNCONFIRMED",
            "buggy_public": buggy_public,
            "fixed_public": fixed_public,
            "fixed_reserved": fixed_reserved,
        }
    patches = find_patches(case_id, old)
    candidates = []
    for p in patches:
        public = execute_semantic(case_id, p["source"], "public")
        candidates.append({k: p[k] for k in ("id","line","rule","old","new","sha256")}
                          | {"public": public})
    shortlist = [p for p in candidates if p["public"]["passed"]]
    return {
        "case": case_id,
        "status": "REPRODUCED_EXTERNAL_HISTORICAL_BUG",
        "repo": CASES[case_id]["repo"], "bug": CASES[case_id]["bug"],
        "buggy_commit": CASES[case_id]["buggy"],
        "fixed_commit": CASES[case_id]["fixed"],
        "path": CASES[case_id]["path"],
        "buggy_source_sha256": digest(old),
        "fixed_source_sha256": digest(fixed),
        "buggy_public": buggy_public,
        "fixed_public": fixed_public,
        "fixed_reserved": fixed_reserved,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "shortlist_ids": [p["id"] for p in shortlist],
        "deterministic_choice": shortlist[0]["id"] if shortlist else None,
        "reserved_score": None,
    }


def run_repro() -> dict:
    rows = [study_case(k) for k in CASES]
    out = {
        "id": "OMEGA-EXTERNAL-REAL-01",
        "phase": "historical-reproduction-and-public-proposal",
        "provenance": {k: CASES[k] for k in CASES},
        "cases": rows,
        "full_upstream_test_suite_executed": False,
        "historical_fixed_diffs_seen_by_experimenter": True,
        "model_called": False,
        "scientific_gain_demonstrated": False,
        "main_modified": False,
    }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_repro()
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "phase": result["phase"],
        "cases": [
            {k: v.get(k) for k in ("case","status","candidate_count","shortlist_ids",
                                   "buggy_public","fixed_public","fixed_reserved")}
            for v in result["cases"]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
