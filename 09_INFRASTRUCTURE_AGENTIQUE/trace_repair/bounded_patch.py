"""Finite, auditable AST repair exploration for source files ranked by real tests.

At most 20 candidates per bug; each changes at most two EXISTING lines in the
same function. This generator never inspects corrected versions or a test oracle.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

MAX_CANDIDATES=20
MAX_CHANGED_LINES=2
MAX_FILES=2

def sha(s):
    return hashlib.sha256(s.encode("utf8")).hexdigest()

def rewrite(source,changes):
    if not changes or len(changes)>MAX_CHANGED_LINES:
        raise ValueError("invalid number of source edits")
    rows=source.splitlines(keepends=True)
    for line,new in changes.items():
        if line<1 or line>len(rows):
            raise ValueError("invalid line number")
        if "\n" in new or "\r" in new:
            raise ValueError("multiline injection into one line forbidden")
        if new==rows[line-1].rstrip("\r\n"):
            raise ValueError("unchanged line")
        rows[line-1]=new+"\n"
    result="".join(rows)
    ast.parse(result)
    actual=[i for i,(x,y) in enumerate(zip(source.splitlines(),result.splitlines()),1)
            if x!=y]
    if sorted(actual)!=sorted(changes):
        raise ValueError("edits not restricted to expected lines")
    if len(result.splitlines())!=len(source.splitlines()):
        raise ValueError("line count drift")
    return result

def nearest_function(tree,line):
    enclosing=[x for x in ast.walk(tree)
               if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))
               and x.lineno<=line<=x.end_lineno]
    return min(enclosing,key=lambda x:x.end_lineno-x.lineno) if enclosing else None

def proposals_for_source(source):
    try:
        tree=ast.parse(source)
    except SyntaxError:
        return []
    lines=source.splitlines()
    templates=[]
    def add(edit,kind):
        try:
            fns=[nearest_function(tree,i) for i in edit]
            if any(f is None for f in fns) or len({id(f) for f in fns})!=1:
                return
            updated=rewrite(source,edit)
        except (SyntaxError,ValueError):
            return
        templates.append({
            "rule":kind,"lines":sorted(edit),
            "changes":[{"line":i,"before":lines[i-1],"after":edit[i]}
                       for i in sorted(edit)],
            "source_after":updated,"source_sha256":sha(updated)})
    for node in ast.walk(tree):
        if not hasattr(node,"lineno"):
            continue
        i=node.lineno
        if not 1<=i<=len(lines):
            continue
        raw=lines[i-1]
        indent=raw[:len(raw)-len(raw.lstrip())]
        if isinstance(node,ast.If):
            test=ast.get_source_segment(source,node.test)
            if not test or "\n" in test or len(test)>120 or not raw.lstrip().startswith("if "):
                continue
            flip=indent+"if not ("+test+"):"
            add({i:flip},"invert-branch")
            if isinstance(node.test,ast.Compare) and len(node.test.ops)==1:
                opposite={
                    ast.Is: "is not",ast.IsNot:"is",ast.Eq:"!=",ast.NotEq:"==",
                    ast.In:"not in",ast.NotIn:"in"
                }
                op=opposite.get(type(node.test.ops[0]))
                if op and len(node.test.comparators)==1:
                    condition=(ast.unparse(node.test.left)+" "+op+" "+
                               ast.unparse(node.test.comparators[0]))
                    add({i:indent+"if "+condition+":"},"swap-comparison")
            # Only direct child return of the same branch; preserve all other code.
            returns=[n for n in node.body if isinstance(n,ast.Return)]
            for r in returns[:1]:
                if r.lineno<=i or r.lineno>len(lines) or r.value is None:
                    continue
                value=ast.get_source_segment(source,r.value)
                if not value or "\n" in value or len(value)>90:
                    continue
                j=r.lineno
                lead=lines[j-1][:len(lines[j-1])-len(lines[j-1].lstrip())]
                after=lead+"return ["+value+"]"
                add({j:after},"wrap-return-list")
                add({i:flip,j:after},"invert-and-wrap-return")
                if value=="None":
                    add({j:lead+"return []"},"empty-return-list")
                    add({i:flip,j:lead+"return []"},"invert-and-empty-return")
        if isinstance(node,ast.Return) and node.value is not None:
            expr=ast.get_source_segment(source,node.value)
            if not expr or "\n" in expr or len(expr)>90:
                continue
            if isinstance(node.value,ast.List):
                add({i:indent+"return None"},"list-to-none")
            elif expr=="None":
                add({i:indent+"return []"},"none-to-empty-list")
            else:
                add({i:indent+"return ["+expr+"]"},"wrap-return-list")
        if isinstance(node,ast.AugAssign) and isinstance(node.op,(ast.BitOr,ast.BitXor)):
            raw=lines[i-1]
            if "|=" in raw:
                add({i:raw.replace("|=","^=",1)},"toggle-bitwise-merge")
            elif "^=" in raw:
                add({i:raw.replace("^=","|=",1)},"toggle-bitwise-merge")
    unique={}
    for p in templates:
        unique.setdefault(p["source_sha256"],p)
    return list(unique.values())

def select_candidates(root,ranking):
    root=Path(root).resolve()
    if ranking["status"]!="RANKED" or not ranking["top3"]:
        raise ValueError("no source-localization evidence")
    outputs=[]
    for path in ranking["top3"][:MAX_FILES]:
        src=(root/path).resolve()
        if not src.is_relative_to(root) or not src.is_file():
            continue
        content=src.read_text(encoding="utf8",errors="replace")
        for p in proposals_for_source(content):
            if len(outputs)>=MAX_CANDIDATES:
                break
            p={k:v for k,v in p.items() if k!="source_after"}
            p["id"]="R"+str(len(outputs)).zfill(2)
            p["path"]=path
            p["source_before_sha256"]=sha(content)
            outputs.append(p)
        if len(outputs)>=MAX_CANDIDATES:
            break
    return {"candidate_count":len(outputs),"max_lines_per_patch":MAX_CHANGED_LINES,
            "max_cases_to_run":6,"top_file_prior":ranking["top3"][:MAX_FILES],
            "candidates":outputs,"fixed_source_inspected":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--buggy-root",type=Path,required=True)
    ap.add_argument("--ranking",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    ranking=json.loads(args.ranking.read_text(encoding="utf8"))
    out=select_candidates(args.buggy_root,ranking)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"candidates":out["candidate_count"],
                      "top_files":out["top_file_prior"]},ensure_ascii=False))

if __name__=="__main__":
    main()
