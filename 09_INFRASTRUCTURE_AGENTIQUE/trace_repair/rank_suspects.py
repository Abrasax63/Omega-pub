"""Rank historical buggy source files using failing-test call traces + test AST.

No corrected sources, diffs or historical fix paths are accepted by this API.
A bug whose buggy/fixed regression contrast is not confirmed is excluded.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import re

MAGIC="OMEGA_CALL_TRACE_V1="
TRACE_SCHEMA="omega-calltrace-v1"
MAX_SUSPECTS=3

def parse_call_trace(log_text):
    lines=[s.split(MAGIC,1)[1].strip()
           for s in log_text.splitlines() if MAGIC in s]
    if len(lines)!=1:
        raise ValueError("expected exactly one stderr call trace")
    raw=json.loads(lines[0])
    if raw.get("schema")!=TRACE_SCHEMA:
        raise ValueError("unsupported trace schema")
    rows=raw.get("files",[])
    if not isinstance(rows,list) or not rows:
        raise ValueError("no project files traced")
    if len({x["path"] for x in rows})!=len(rows):
        raise ValueError("duplicate traced source file")
    for item in rows:
        name=item["path"]
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("unsafe path in trace")
        if not isinstance(item["total_calls"],int) or item["total_calls"]<=0:
            raise ValueError("empty call record")
    return rows

def test_symbols(test_source,test_name):
    tree=ast.parse(test_source)
    named=[x for x in ast.walk(tree)
           if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))
           and x.name==test_name]
    if len(named)!=1:
        raise ValueError("target test definition missing or ambiguous")
    node=named[0]
    tokens={test_name.removeprefix("test_")}
    for n in ast.walk(node):
        if isinstance(n,ast.Attribute):
            tokens.add(n.attr)
        if isinstance(n,ast.Name):
            tokens.add(n.id)
    # Imports within the entire test module are public evidence.
    imports=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.ImportFrom) and n.module:
            imports.add(n.module)
        elif isinstance(n,ast.Import):
            imports.update(x.name for x in n.names)
    return {"symbols":sorted(tokens),"imports":sorted(imports)}

def source_functions(content):
    try:
        tree=ast.parse(content)
    except SyntaxError:
        return set()
    return {n.name for n in ast.walk(tree)
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

def rank_files(buggy_root,package,trace_rows,test_source,test_name):
    root=Path(buggy_root).resolve()
    evidence=test_symbols(test_source,test_name)
    tokens=set(evidence["symbols"])
    imports=set(evidence["imports"])
    scored=[]
    for item in trace_rows:
        rel=Path(package)/item["path"]
        src=(root/rel).resolve()
        if not src.is_relative_to(root) or not src.is_file():
            continue
        if not str(src).endswith(".py"):
            continue
        source=src.read_text(encoding="utf-8",errors="replace")
        defs=source_functions(source)
        matched=sorted(defs & tokens)
        rel_dot=rel.with_suffix("").as_posix().replace("/",".")
        imports_match=sorted(i for i in imports if i==rel_dot)
        basename=rel.stem
        basename_match=basename in tokens
        called=[entry["label"].split("@",1)[0] for entry in item["functions"]]
        invoked_matching=sorted(set(called)&tokens)
        # Fixed, generic rule: test-identifier agreement dominates mere execution.
        score=1+12*len(matched)+7*len(imports_match)+\
              4*int(basename_match)+3*len(invoked_matching)
        reasons={
            "def_names_in_test":matched,
            "direct_module_imports":imports_match,
            "basename_in_test":basename_match,
            "called_def_names_in_test":invoked_matching,
            "executed_function_count":item["total_calls"],
        }
        scored.append({"path":rel.as_posix(),"score":score,"reasons":reasons})
    scored.sort(key=lambda row:(-row["score"],row["path"]))
    return {
        "test_name":test_name,
        "trace_files_seen":len(trace_rows),
        "qualified_code_files":len(scored),
        "test_evidence":evidence,
        "ranked":scored,
        "top3":[row["path"] for row in scored[:MAX_SUSPECTS]],
        "alphabetical_baseline":sorted(r["path"] for r in scored),
        "status":"RANKED" if scored else "NO_EXECUTED_PROJECT_SOURCE",
        "oracle_corrected_source_used":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--buggy-root",type=Path,required=True)
    p.add_argument("--package",required=True)
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--test-file",type=Path,required=True)
    p.add_argument("--test-name",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=rank_files(args.buggy_root,args.package,
                      parse_call_trace(args.log.read_text(encoding="utf-8",errors="replace")),
                      args.test_file.read_text(encoding="utf-8",errors="replace"),
                      args.test_name)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"top3":report["top3"],
                      "file_count":report["qualified_code_files"]},ensure_ascii=False))

if __name__=="__main__":
    main()
