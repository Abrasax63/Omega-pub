"""Prospective static AST search on buggy Git checkouts, no fixed-source read.

This is a deliberately low-capacity pre-fixed baseline: no data-dependent prompt
revision, no model call, no repository test executed in the freeze phase.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
LIMIT=60
INSPECTION_LIMIT=150
PACKAGE={"B1":"pysnooper","B2":"tqdm","B3":"cookiecutter"}
RULES=("unbound-open-path","encoding-explicit","nested-enumerate-start",
       "loop-range-offset","binary-operator","boolean-flip","open-mode")

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def one_line(source,number,replacement):
    lines=source.splitlines(keepends=True)
    if number<1 or number>len(lines):
        raise ValueError("invalid source line")
    was=lines[number-1].rstrip("\r\n")
    if was==replacement:
        raise ValueError("no change")
    lines[number-1]=replacement+"\n"
    candidate="".join(lines)
    ast.parse(candidate)
    if len(lines)!=len(candidate.splitlines(keepends=True)):
        raise ValueError("more than one line")
    return candidate

def candidate_rules(source):
    try:
        root=ast.parse(source)
    except (SyntaxError,UnicodeError):
        return []
    lines=source.splitlines()
    collected=[]
    seen=set()
    def add(node,edit,tag):
        line=node.lineno
        if line<1 or line>len(lines):
            return
        try:
            modified=one_line(source,line,edit)
        except (ValueError,SyntaxError):
            return
        change=(line,edit)
        if change in seen or tag not in RULES:
            return
        seen.add(change)
        collected.append({
            "line":line,"rule":tag,
            "original":lines[line-1],
            "replacement":edit,
            "source_sha256":sha(source),
            "modified_sha256":sha(modified),
        })
    for node in ast.walk(root):
        if not hasattr(node,"lineno"):
            continue
        idx=node.lineno
        if not 1<=idx<=len(lines):
            continue
        original=lines[idx-1]
        ind=original[:len(original)-len(original.lstrip())]
        if isinstance(node,ast.With):
            for item in node.items:
                call=item.context_expr
                if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name):
                    continue
                if call.func.id!="open":
                    continue
                piece=ast.get_source_segment(source,call)
                if not piece or not piece.endswith(")"):
                    continue
                if not any(k.arg=="encoding" for k in call.keywords):
                    for enc in ("utf-8","cp1252"):
                        edit=original.replace(piece,piece[:-1]+", encoding='"+enc+"')",1)
                        add(node,edit,"encoding-explicit")
                if call.args and isinstance(call.args[0],ast.Name):
                    wrong=call.args[0].id
                    # Only variables drawn from the nearest enclosing lexical
                    # function arguments, not repaired diff or hidden oracle.
                    enclosing=[n for n in ast.walk(root)
                               if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
                               and n.lineno<=node.lineno<=n.end_lineno]
                    if enclosing:
                        f=min(enclosing,key=lambda n:n.end_lineno-n.lineno)
                        for arg in f.args.args:
                            if arg.arg==wrong:
                                continue
                            edit=re.sub(r"\b"+re.escape(wrong)+r"\b",arg.arg,original,count=1)
                            add(node,edit,"unbound-open-path")
        if isinstance(node,ast.Return) and isinstance(node.value,ast.Call):
            outer=node.value
            if isinstance(outer.func,ast.Name) and outer.func.id=="enumerate" and len(outer.args)==1:
                inner=outer.args[0]
                if isinstance(inner,ast.Call) and len(inner.args)>=2:
                    for pos in range(1,min(len(inner.args),3)):
                        kept=[ast.unparse(q) for i,q in enumerate(inner.args) if i!=pos]
                        kept.extend(ast.unparse(k) for k in inner.keywords)
                        sub=ast.unparse(inner.func)+"("+", ".join(kept)+")"
                        edit=ind+"return enumerate("+sub+", "+ast.unparse(inner.args[pos])+")"
                        add(node,edit,"nested-enumerate-start")
        if isinstance(node,ast.For) and isinstance(node.iter,ast.Call):
            call=node.iter
            if isinstance(call.func,ast.Name) and call.func.id=="range" and len(call.args)==1:
                expr=ast.get_source_segment(source,call.args[0])
                full=ast.get_source_segment(source,call)
                if expr and full and "\n" not in expr and full in original:
                    for change in ("("+expr+" - 1)","("+expr+" + 1)"):
                        add(node,original.replace(full,"range("+change+")",1),"loop-range-offset")
        if isinstance(node,ast.AugAssign) and isinstance(node.op,(ast.BitXor,ast.BitOr)):
            pattern=r"(\^=|\|=)"
            for op in ("^=","|="):
                add(node,re.sub(pattern,lambda m:op,original,count=1),"binary-operator")
        if isinstance(node,ast.If):
            # Conservative syntax-bound boolean negation; cannot change
            # decorator, imports or more than one line.
            segment=ast.get_source_segment(source,node.test)
            if segment and "\n" not in segment and "if " in original and original.rstrip().endswith(":"):
                if len(segment)<120:
                    add(node,ind+"if not ("+segment+"):", "boolean-flip")
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=="open":
            raw=ast.get_source_segment(source,node)
            if raw and raw in original and "encoding=" not in raw:
                # File write mode changes are deliberately included because
                # the previous external pilot had ambiguous append/overwrite.
                for a,b in (("'a'","'w'"),("'w'","'a'")):
                    if a in raw:
                        add(node,original.replace(raw,raw.replace(a,b,1),1),"open-mode")
    return collected

def freeze_case(case,checkout):
    name=case["id"]
    pkg=PACKAGE[name]
    work=Path(checkout).resolve()
    if not work.is_dir():
        raise RuntimeError("missing pinned buggy checkout "+name)
    sha_checkout=subprocess.check_output(
        ["git","-C",str(work),"rev-parse","HEAD"],text=True).strip()
    if sha_checkout!=case["buggy_sha"]:
        raise RuntimeError("wrong upstream SHA "+name+" "+sha_checkout)
    paths=sorted(p for p in (work/pkg).rglob("*.py")
                 if not any(part.lower() in ("tests","test","test_utils")
                            for part in p.relative_to(work).parts))
    found=[]
    bad_syntax=[]
    for f in paths[:INSPECTION_LIMIT]:
        rel=f.relative_to(work).as_posix()
        source=f.read_text(encoding="utf-8",errors="replace")
        try:
            ast.parse(source)
        except SyntaxError:
            bad_syntax.append(rel)
            continue
        for p in candidate_rules(source):
            p["path"]=rel
            found.append(p)
    priorities={name:i for i,name in enumerate(RULES)}
    found.sort(key=lambda x:(priorities[x["rule"]],x["path"],x["line"],
                            x["replacement"]))
    deduped=[]
    seen=set()
    for p in found:
        if p["modified_sha256"] in seen:
            continue
        seen.add(p["modified_sha256"])
        p["id"]="P"+str(len(deduped)).zfill(2)
        deduped.append(p)
        if len(deduped)>=LIMIT:
            break
    return {
        "id":name,"repo":case["repo"],"buggy_commit":sha_checkout,
        "source_files_scanned":len(paths[:INSPECTION_LIMIT]),
        "syntax_skipped":bad_syntax,
        "generated_before_cap":len(found),
        "candidates":deduped,
        "top1":deduped[0]["id"] if deduped else None,
        "corrected_commit_fetched":False,
    }

def freeze(manifest,base):
    if manifest["experiment_id"]!="OMEGA-BUGSINPY-BLIND-01":
        raise ValueError("unexpected cohort")
    result={
        "experiment_id":manifest["experiment_id"],
        "phase":"CANDIDATES_FROZEN_BUGGY_ONLY",
        "candidate_rule_set":list(RULES),
        "max_candidates_per_case":LIMIT,
        "fixed_source_seen":False,
        "fixed_diff_seen":False,
        "model_called":False,
        "cases":[freeze_case(case,Path(base)/case["id"]) for case in manifest["cases"]],
        "oracle_status":"NOT_OPENED",
        "no_generalization_claim":True,
    }
    result["commitment_sha256"]=sha(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--workdir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    data=freeze(read_json(args.manifest),args.workdir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "phase":data["phase"],"commitment":data["commitment_sha256"],
        "cases":[{"id":c["id"],"scanned":c["source_files_scanned"],
                  "generated":c["generated_before_cap"],
                  "frozen":len(c["candidates"]),"top1":c["top1"]}
                 for c in data["cases"]],
    },ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
