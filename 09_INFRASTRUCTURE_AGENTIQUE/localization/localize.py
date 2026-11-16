"""OMEGA-LOC-01: freeze identical AST site pools before fixed-source oracle.

Does NOT generate or execute new patches, alter the #105 baseline, or call a model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"blind_bugsinpy"))
from blind_candidates import freeze_case  # unchanged existing #105 grammar

BUGGY="c2599e3cd6087429f48bae34347ec5d2473c8392"
FIXED="73962a47026dd980ac0758820efc9c41cbf938e0"
CASE={"id":"B2","repo":"tqdm/tqdm","buggy_sha":BUGGY}
INSPECT=10
TAG="OMEGA_TRACE_JSON="
HUNK=re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")
DIFF=re.compile(r"^diff --git a/(\S+) b/(\S+)$")

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def sha(obj):
    return hashlib.sha256((obj if isinstance(obj,str) else canonical(obj)).encode("utf-8")).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path,obj):
    dest=Path(path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")

def parse_trace(log):
    raw=Path(log).read_text(encoding="utf-8",errors="replace")
    matches=[s[len(TAG):] for s in raw.splitlines() if s.startswith(TAG)]
    if len(matches)!=1:
        raise ValueError("expected one complete trace record")
    record=json.loads(matches[0])
    if record.get("truncated") or record.get("event_count",0)<=0:
        raise ValueError("no complete executed-line evidence")
    sites={}
    for x in record.get("lines",[]):
        p=x.get("path","")
        line=x.get("line",0)
        if not p.startswith("tqdm/") or "/tests/" in p or p.startswith("/") or ".." in p.split("/"):
            raise ValueError("invalid trace source")
        if not isinstance(line,int) or line<1:
            raise ValueError("invalid trace line")
        if not isinstance(x.get("last"),int) or not isinstance(x.get("count"),int) or x["last"]<1 or x["count"]<1:
            raise ValueError("invalid trace counts")
        k=(p,line)
        if k in sites:
            raise ValueError("duplicate trace site")
        sites[k]={"last":x["last"],"count":x["count"]}
    if not sites:
        raise ValueError("empty package trace")
    return record,sites

def unique_sites(candidates):
    seen=set()
    sites=[]
    for cand in candidates:
        key=(cand["path"],cand["line"])
        if key not in seen:
            seen.add(key)
            sites.append({"path":key[0],"line":key[1],"first_candidate":cand["id"]})
    return sites

def rank_sites(sites,trace):
    ordered=list(enumerate(sites))
    ordered.sort(key=lambda ix:(
        -(1 if (ix[1]["path"],ix[1]["line"]) in trace else 0),
        -trace.get((ix[1]["path"],ix[1]["line"]),{}).get("last",0),
        -trace.get((ix[1]["path"],ix[1]["line"]),{}).get("count",0),
        ix[0]))
    return [site for i,site in ordered]

def seal(data):
    if "commitment_sha256" in data:
        raise ValueError("already sealed")
    out=dict(data)
    out["commitment_sha256"]=sha(out)
    return out

def verify_seal(data):
    commitment=data.get("commitment_sha256")
    if not commitment or sha({k:v for k,v in data.items() if k!="commitment_sha256"})!=commitment:
        raise ValueError("candidate freeze integrity mismatch")
    if data.get("phase")!="BUGGY_ONLY_FROZEN" or data.get("fixed_source_seen") is not False:
        raise ValueError("fixed-source boundary or phase violated")
    return True

def freeze(checkout,log,pytest_exit,output):
    baseline=freeze_case(CASE,checkout)
    sites=unique_sites(baseline["candidates"])
    trace_status="VALID"
    record=None
    trace={}
    try:
        record,trace=parse_trace(log)
    except (ValueError,json.JSONDecodeError):
        trace_status="INVALID_OR_MISSING"
    static=sites[:INSPECT]
    dynamic=rank_sites(sites,trace)[:INSPECT] if trace_status=="VALID" and pytest_exit!=0 else []
    result=seal({
        "experiment":"OMEGA-LOC-01",
        "phase":"BUGGY_ONLY_FROZEN",
        "bug_id":"tqdm-3",
        "source_commit":BUGGY,
        "fixed_source_seen":False,
        "model_called":False,
        "budget_unique_sites":INSPECT,
        "candidate_count":len(baseline["candidates"]),
        "candidate_sites":sites,
        "candidate_pool_sha256":sha(baseline["candidates"]),
        "baseline_grammar":"unchanged blind_candidates.freeze_case (PR #105)",
        "static_top10":static,
        "trace_top10":dynamic,
        "trace_status":trace_status,
        "trace_log_sha256":hashlib.sha256(Path(log).read_bytes()).hexdigest(),
        "trace_line_count":len(trace),
        "trace_events":record["event_count"] if record else None,
        "pytest_buggy_exit":pytest_exit,
        "buggy_test_failed":pytest_exit!=0,
        "trace_overhead_is_not_cost_matched":True,
    })
    write(output,result)
    return result

def diff_old_sites(diff_text):
    """Return old-source changed positions, without treating pure insertions as a hit."""
    current=None
    positions=set()
    insertions=[]
    for row in diff_text.splitlines():
        m=DIFF.match(row)
        if m:
            a,b=m.groups()
            current=a if a==b and a.startswith("tqdm/") and "/tests/" not in a else None
            continue
        m=HUNK.match(row)
        if current and m:
            start=int(m.group(1))
            count=int(m.group(2)) if m.group(2) is not None else 1
            if count:
                positions.update((current,i) for i in range(start,start+count))
            else:
                insertions.append({"path":current,"before_old_line":start})
    return positions,insertions

def evaluate(frozen,diff_text,buggy_exit,fixed_exit):
    verify_seal(frozen)
    if frozen["source_commit"]!=BUGGY or frozen["budget_unique_sites"]!=INSPECT:
        raise ValueError("unexpected cohort")
    sites,insertions=diff_old_sites(diff_text)
    pool={(x["path"],x["line"]) for x in frozen["candidate_sites"]}
    eligible=buggy_exit!=0 and fixed_exit==0 and frozen["buggy_test_failed"] and frozen["trace_status"]=="VALID"
    report={
        "experiment":"OMEGA-LOC-01",
        "phase":"HISTORICAL_ORACLE_AFTER_FREEZE",
        "freeze_sha256":frozen["commitment_sha256"],
        "historical_diff_sha256":sha(diff_text),
        "buggy_exit":buggy_exit,"fixed_exit":fixed_exit,
        "bug_reproduced":buggy_exit!=0 and fixed_exit==0,
        "old_modified_site_count":len(sites),
        "pure_insertions":insertions,
        "candidate_pool_hits_any":len(pool&sites),
        "trace_added_cost":"one additional instrumented original pytest run; not cost matched in runtime",
        "main_modified":False,"model_called":False,
        "promoted":False,
        "independent_external_blind":False,
        "arms":{},
    }
    for name,key in (("static","static_top10"),("trace","trace_top10")):
        ranked=frozen[key]
        hits=[i+1 for i,s in enumerate(ranked) if (s["path"],s["line"]) in sites]
        near=[i+1 for i,s in enumerate(ranked) if any(
            s["path"]==p and abs(s["line"]-line)<=2 for p,line in sites)]
        report["arms"][name]={
            "inspected":len(ranked),
            "first_exact_rank":min(hits) if hits else None,
            "exact_hit_top10":bool(hits),
            "nearby_rank_diagnostic_only":min(near) if near else None,
        }
    if not (buggy_exit!=0 and fixed_exit==0):
        report["status"]="BUG_NOT_REPRODUCED" if buggy_exit==0 and fixed_exit==0 else "ENVIRONMENT_OR_REFERENCE_BLOCKED"
    elif frozen["trace_status"]!="VALID":
        report["status"]="TRACE_UNUSABLE"
    elif not sites:
        report["status"]="NO_MODIFIED_OLD_LINES"
    elif not(pool&sites):
        report["status"]="GRAMMAR_COVERAGE_MISSING"
    else:
        report["status"]="LOCALIZATION_EVALUATED"
    if report["status"]!="LOCALIZATION_EVALUATED":
        for arm in report["arms"].values():
            arm["scientific_success"]=None
    else:
        for arm in report["arms"].values():
            arm["scientific_success"]=arm["exact_hit_top10"]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=["freeze","oracle"],required=True)
    p.add_argument("--checkout",type=Path)
    p.add_argument("--trace-log",type=Path)
    p.add_argument("--buggy-exit",type=Path)
    p.add_argument("--fixed-exit",type=Path)
    p.add_argument("--freeze-file",type=Path)
    p.add_argument("--diff",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="freeze":
        if not a.checkout or not a.trace_log or not a.buggy_exit:
            p.error("freeze needs checkout, trace-log, buggy-exit")
        x=freeze(a.checkout,a.trace_log,int(a.buggy_exit.read_text().strip()),a.output)
    else:
        if not a.freeze_file or not a.diff or not a.buggy_exit or not a.fixed_exit:
            p.error("oracle needs freeze-file, diff, buggy-exit, fixed-exit")
        x=evaluate(read(a.freeze_file),a.diff.read_text(encoding="utf-8"),
                   int(a.buggy_exit.read_text().strip()),
                   int(a.fixed_exit.read_text().strip()))
        write(a.output,x)
    print(json.dumps({"phase":x["phase"],"status":x.get("status",x.get("trace_status")),
        "sha":x.get("commitment_sha256",x.get("freeze_sha256")),
        "arms":x.get("arms"),"candidate_sites":len(x.get("candidate_sites",[]))},
        sort_keys=True))
if __name__=="__main__":
    main()
