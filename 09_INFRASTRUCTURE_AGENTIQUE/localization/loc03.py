"""OMEGA-LOC-03: precommitted two-factor localization & grammar ablation.

NO fixed-source access until a distinct oracle phase. No model calls.
"""
from __future__ import annotations
import argparse
import ast
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"blind_bugsinpy"))
from blind_candidates import freeze_case,candidate_rules,one_line

CASES={
    "tqdm-5":{"bug":"19b08ab34fdbfa0275bc5cb2430436c724c7e759",
        "fixed":"4f340697af69b71850aad496387c9c5aa1904136",
        "test":"tqdm/tests/tests_tqdm.py::test_bool",
        "test_blob":"35e1c70463569b6c9461c9ba91019ee1d011ea56"},
    "tqdm-8":{"bug":"08b8ad1ff3bd003ef8309faaa0cc108ffa40317d",
        "fixed":"cae9d139c6df5614be3bf6e25ccbd600ee3286dc",
        "test":"tqdm/tests/tests_tqdm.py::test_format_meter",
        "test_blob":"6da3e10e9fa95a98ad61788de87de680361b06d0"},
}
ARMS=("S-G0","S-G1","T-G0","T-G1")
SITE_LIMIT=10
FILE_LIMIT=150
PACKAGE="tqdm"
SOURCE_DIRS_EXCLUDE={"tests","test","test_utils","__pycache__"}
DIFF=re.compile(r"^diff --git a/(\S+) b/(\S+)$")
HUNK=re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(x):
    return hashlib.sha256((x if isinstance(x,str) else canonical(x)).encode("utf-8")).hexdigest()
def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def seal(data):
    result=dict(data)
    result["commitment_sha256"]=digest(data)
    return result
def verify(data):
    expected=data.get("commitment_sha256")
    if not expected or digest({k:v for k,v in data.items() if k!="commitment_sha256"})!=expected:
        raise ValueError("frozen artifact was changed")
    if data.get("phase")!="BUGGY_ONLY_FROZEN" or data.get("fixed_code_seen") is not False:
        raise ValueError("invalid oracle boundary")
    if data.get("budget_sites")!=SITE_LIMIT or data["case"] not in CASES:
        raise ValueError("unknown budget or case")
    return True

def all_sites(checkout):
    root=Path(checkout).resolve()
    files=sorted(p for p in (root/PACKAGE).rglob("*.py")
        if not (SOURCE_DIRS_EXCLUDE & set(p.relative_to(root).parts)))
    result=[]
    source={}
    statement={}
    for p in files[:FILE_LIMIT]:
        rel=p.relative_to(root).as_posix()
        raw=p.read_text(encoding="utf-8",errors="replace")
        try:
            tree=ast.parse(raw)
        except SyntaxError:
            continue
        source[rel]=raw
        lines=raw.splitlines()
        byline=defaultdict(list)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Assign,ast.AugAssign,ast.AnnAssign,
               ast.Expr,ast.Return,ast.Raise,ast.If,ast.For,ast.While,
               ast.With,ast.Assert,ast.Try,ast.Delete)):
                if 1<=node.lineno<=len(lines):
                    byline[node.lineno].append(node)
        for lineno in sorted(byline):
            key=(rel,lineno)
            result.append(key)
            statement[key]=byline[lineno]
    return result,source,statement

def chosen_guard(text, nodes, lineno):
    lines=text.splitlines()
    original=lines[lineno-1]
    if not original.strip() or original.rstrip().endswith(":") or ";" in original:
        return None
    if original.lstrip().startswith(("#","@","import ","from ")):
        return None
    ind=original[:len(original)-len(original.lstrip())]
    for node in nodes:
        if not isinstance(node,(ast.Assign,ast.AugAssign,ast.Expr,ast.Return)):
            continue
        if getattr(node,"end_lineno",lineno)!=lineno:
            continue
        name=None
        target=(node.targets[0] if isinstance(node,ast.Assign) else
                node.target if isinstance(node,ast.AugAssign) else None)
        if isinstance(target,ast.Name):
            name=target.id
        if name is None:
            names=sorted({n.id for n in ast.walk(node) if isinstance(n,ast.Name)
                and isinstance(n.ctx,ast.Load)})
            if names:
                name=names[0]
        if not name or not name.isidentifier() or name in ("True","False","None"):
            continue
        replacement=ind+"if "+name+": "+original.strip()
        try:
            modified=one_line(text,lineno,replacement)
        except (ValueError,SyntaxError):
            continue
        return {"replacement":replacement,"rule":"guard-first-variable",
                "modified_sha256":digest(modified)}
    return None

def baseline_edits(source,rows):
    available={}
    for path in sorted(set(p for p,l in rows)):
        if path not in source:
            continue
        candidates=candidate_rules(source[path])
        for cand in candidates:
            key=(path,cand["line"])
            available.setdefault(key,{"replacement":cand["replacement"],
                "rule":cand["rule"],"modified_sha256":cand["modified_sha256"]})
    return available

def parse_original_trace(p):
    from localize import parse_trace
    return parse_trace(p)

def get_freeze(case,checkout,trace_log,pytest_exit):
    if case not in CASES:
        raise ValueError("non preregistered case")
    expected=CASES[case]
    checkout=Path(checkout)
    sha=subprocess.check_output(["git","-C",str(checkout),"rev-parse","HEAD"],text=True).strip()
    if sha!=expected["bug"]:
        raise ValueError("wrong buggy checkout")
    original={"id":"B2","repo":"tqdm/tqdm","buggy_sha":expected["bug"]}
    prioritizer=freeze_case(original,checkout)
    universe,source,nodes=all_sites(checkout)
    allset=set(universe)
    old_priority=[]
    for row in prioritizer["candidates"]:
        key=(row["path"],row["line"])
        if key in allset and key not in old_priority:
            old_priority.append(key)
    order=old_priority+[p for p in universe if p not in set(old_priority)]
    # Fix old priority once, independent of traces.
    trace_status="VALID"
    trace={}
    event_count=None
    duration=None
    try:
        data,trace=parse_original_trace(trace_log)
        event_count=data["event_count"]
        duration=data.get("elapsed_seconds")
    except (ValueError,json.JSONDecodeError):
        trace_status="INVALID_OR_MISSING"
    observed=[(key,i) for i,key in enumerate(order)]
    observed.sort(key=lambda xi:(-int(xi[0] in trace),
          -trace.get(xi[0],{}).get("last",0),
          -trace.get(xi[0],{}).get("count",0),xi[1]))
    static=order[:SITE_LIMIT]
    dynamic=[key for key,i in observed[:SITE_LIMIT]] if trace_status=="VALID" and pytest_exit==1 else []
    selected=set(static)|set(dynamic)
    old_by_site=baseline_edits(source,selected)
    plans={}
    for label,sites in (("S",static),("T",dynamic)):
        for policy in ("G0","G1"):
            rows=[]
            for idx,key in enumerate(sites):
                path,line=key
                raw=source[path]
                edit=old_by_site.get(key)
                if policy=="G1":
                    guard=chosen_guard(raw,nodes[key],line)
                    if guard is not None:
                        edit=guard
                row={"rank":idx+1,"path":path,"line":line,"source_sha256":digest(raw),
                    "rule":edit["rule"] if edit else None,
                    "replacement":edit["replacement"] if edit else None,
                    "modified_sha256":edit["modified_sha256"] if edit else None}
                rows.append(row)
            plans[label+"-"+policy]=rows
    return seal({
        "experiment":"OMEGA-LOC-03","phase":"BUGGY_ONLY_FROZEN",
        "case":case,"bug_commit":expected["bug"],"fixed_code_seen":False,
        "test":expected["test"],"test_blob_sha1":expected["test_blob"],
        "budget_sites":SITE_LIMIT,
        "universe_size":len(order),"universe_sha256":digest(order),
        "baseline_7_rule_priority_count":len(old_priority),
        "trace_status":trace_status,"trace_event_count":event_count,
        "trace_seconds":duration,"trace_log_sha256":hashlib.sha256(Path(trace_log).read_bytes()).hexdigest(),
        "buggy_pytest_exit":pytest_exit,"model_called":False,
        "rankings":{"S":[{"path":p,"line":l} for p,l in static],
                    "T":[{"path":p,"line":l} for p,l in dynamic]},
        "plans":plans,
    })

def stage(frozen,checkout,dest):
    verify(frozen)
    root=Path(checkout).resolve()
    dest=Path(dest).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for label in ARMS:
        for i,row in enumerate(frozen["plans"][label]):
            replacement=row["replacement"]
            if replacement is None:
                manifest.append({"arm":label,"rank":i+1,"status":"ABSTAIN_NO_RULE"})
                continue
            p=(root/row["path"]).resolve()
            if not p.is_relative_to(root):
                raise ValueError("invalid source path")
            raw=p.read_text(encoding="utf-8",errors="replace")
            if digest(raw)!=row["source_sha256"]:
                raise ValueError("original source drift")
            patched=one_line(raw,row["line"],replacement)
            if digest(patched)!=row["modified_sha256"]:
                raise ValueError("candidate changed after freeze")
            row_id=label.replace("-","")+"-"+str(i+1).zfill(2)
            patch_root=dest/row_id
            target=patch_root/row["path"]
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(patched,encoding="utf-8")
            manifest.append({"arm":label,"rank":i+1,"id":row_id,"path":row["path"],
                             "rule":row["rule"],"status":"READY"})
    return manifest

def diff_sites(raw):
    changed=set()
    current=None
    for line in raw.splitlines():
        m=DIFF.match(line)
        if m:
            a,b=m.groups()
            current=a if a==b and a.startswith("tqdm/") and "/tests/" not in a else None
            continue
        m=HUNK.match(line)
        if current and m:
            start=int(m.group(1))
            count=int(m.group(2)) if m.group(2) is not None else 1
            changed.update((current,k) for k in range(start,start+count))
    return changed

def judge(frozen,attempts,diff_raw,buggy_exit,fixed_exit):
    verify(frozen)
    case=CASES[frozen["case"]]
    site_set=diff_sites(diff_raw)
    reproduced=buggy_exit==1 and fixed_exit==0 and frozen["buggy_pytest_exit"]==1
    trace_valid=frozen["trace_status"]=="VALID"
    arms={}
    for label in ARMS:
        site_key=label.split("-")[0]
        ranking=frozen["rankings"][site_key]
        hit=[i+1 for i,row in enumerate(ranking) if (row["path"],row["line"]) in site_set]
        statuses=[r for r in attempts if r["arm"]==label]
        if len(statuses)!=len(frozen["plans"][label]):
            raise ValueError("missing patch evaluations for "+label)
        attempted=[r for r in statuses if r["status"]=="RUN"]
        passing=[r for r in attempted if r["test_exit"]==0]
        arms[label]={
            "sites_inspected":len(ranking),
            "first_exact_modified_line_rank":min(hit) if hit else None,
            "patches_attempted":len(attempted),
            "patch_tests_passed":len(passing),
            "first_passing_patch_rank":min((r["rank"] for r in passing),default=None),
            "abstentions":sum(r["status"]=="ABSTAIN_NO_RULE" for r in statuses),
            "test_environment_errors":sum(r["status"]=="RUN" and r["test_exit"] not in (0,1)
                for r in statuses),
            "bounded_repair_success":bool(passing) if reproduced and trace_valid else None,
            "exact_localization_success":bool(hit) if reproduced and trace_valid else None,
            "attempts":statuses,
        }
    status=("BUG_NOT_REPRODUCED" if buggy_exit==0 and fixed_exit==0 else
        "REFERENCE_OR_BUG_ENVIRONMENT_BLOCKED" if not reproduced else
        "TRACE_UNUSABLE" if not trace_valid else
        "NO_OLD_MODIFIED_LINES" if not site_set else "EVALUATED")
    if status!="EVALUATED":
        for arm in arms.values():
            arm["bounded_repair_success"]=None
            arm["exact_localization_success"]=None
    return {
        "experiment":"OMEGA-LOC-03","case":frozen["case"],
        "phase":"ORACLE_OPENED_AFTER_FROZEN_PATCH_PLANS",
        "freeze_sha256":frozen["commitment_sha256"],
        "historical_diff_sha256":digest(diff_raw),
        "status":status,"buggy_exit":buggy_exit,"fixed_exit":fixed_exit,
        "reproduced":reproduced,"trace_valid":trace_valid,
        "original_changed_site_count":len(site_set),
        "no_paid_api":True,"main_modified":False,"promoted":False,
        "limited_scope":"two historical same-project regressions, no generalization",
        "arms":arms,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=["freeze","stage","judge"],required=True)
    p.add_argument("--case",choices=list(CASES))
    p.add_argument("--checkout",type=Path)
    p.add_argument("--trace-log",type=Path)
    p.add_argument("--buggy-exit",type=Path)
    p.add_argument("--fixed-exit",type=Path)
    p.add_argument("--frozen",type=Path)
    p.add_argument("--patch-root",type=Path)
    p.add_argument("--attempts",type=Path)
    p.add_argument("--diff",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="freeze":
        out=get_freeze(a.case,a.checkout,a.trace_log,int(a.buggy_exit.read_text().strip()))
    elif a.mode=="stage":
        out=stage(read(a.frozen),a.checkout,a.patch_root)
    else:
        out=judge(read(a.frozen),read(a.attempts),a.diff.read_text(encoding="utf-8"),
                 int(a.buggy_exit.read_text().strip()),int(a.fixed_exit.read_text().strip()))
    write(a.output,out)
    summary={"phase":out["phase"] if isinstance(out,dict) else "PATCHES_STAGED",
        "case":out.get("case") if isinstance(out,dict) else None,
        "status":out.get("status") if isinstance(out,dict) else None,
        "freeze":out.get("commitment_sha256",out.get("freeze_sha256")) if isinstance(out,dict) else None,
        "num_staged":len(out) if isinstance(out,list) else None}
    print(canonical(summary))
if __name__=="__main__":
    main()
