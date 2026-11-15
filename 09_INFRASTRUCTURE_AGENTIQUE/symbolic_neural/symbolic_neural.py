"""OMEGA-SYMNEU-01: finite symbolic search and real Qwen shortlist selector.

Trusted 16-item DSL is simulated, never dynamically executed. Only model output
is an identifier; sandboxed executable sources are generated from the DSL.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INFRA=ROOT/"09_INFRASTRUCTURE_AGENTIQUE"
for name in ("auto_research","integrated_cycle","memory_repair",
             "memory_ablation","targeted_patch","prism"):
    sys.path.insert(0,str(INFRA/name))

from targeted_patch import ORIGINAL,FROZEN_ORIGINAL_SHA,apply_patch
from memory_repair import compile_rce_tests
from memory_ablation import _manifest,_gate_for,_all_correct
from integrated_cycle import prepare,known_prior_sources
from runner import graph_case
from model_pilot import score
from reference import walks_exact
from variant_factory import generate
from gate import digest
from execution import start_execution,record_perspective,close_execution
from event_store import lifecycle_events,verify_events

EXP_ID="OMEGA-SYMNEU-01"
PUBLIC_SEEDS=(1101,1102,1103)
N_HOLDOUT=5
N_GRAMMAR=16
MIN_GAIN=.15
MARK="SELECTED_ID: "

def sha(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def grammar():
    """Enumerate exactly 16 signed bit predicates; do NOT inject solution."""
    out=[]
    for family in ("rows","result"):
        for row in ("i","j"):
            for bit in ("i","j"):
                for negate in (False,True):
                    base=family+"["+row+"] & (1 << "+bit+")"
                    out.append({
                        "id":"H"+str(len(out)).zfill(2),
                        "mask":family,"row_index":row,
                        "bit_index":bit,"negated":negate,
                        "expression":"not ("+base+")" if negate else base})
    if len(out)!=N_GRAMMAR or len({x["expression"] for x in out})!=N_GRAMMAR:
        raise RuntimeError("non-frozen or duplicate grammar")
    return out

def simulate(rows,horizon,hypothesis):
    """Independent finite DSL interpreter for the repaired if-line."""
    n=len(rows)
    if n<1 or horizon<0 or any(type(x)!=int or not 0<=x<(1<<n) for x in rows):
        raise ValueError("bad finite relation")
    if horizon==0:
        return [1<<i for i in range(n)]
    current=rows[:]
    for _ in range(horizon-1):
        nxt=[]
        for i in range(n):
            total=0
            for j in range(n):
                src=rows if hypothesis["mask"]=="rows" else current
                ri=i if hypothesis["row_index"]=="i" else j
                bi=i if hypothesis["bit_index"]=="i" else j
                hit=bool(src[ri] & (1<<bi))
                if not hit if hypothesis["negated"] else hit:
                    total|=rows[j]
            nxt.append(total)
        current=nxt
    return current

def public_cases():
    cases=[
        ("identity",[2,1],0),
        ("cycle",[2,1],2),
        ("branching",[6,4,4],2),
        ("long_cycle",[2,4,1],9),
    ]
    cases.extend((f"e2-{a}-{b}-{t}",[a,b],t)
                 for a in range(4) for b in range(4) for t in range(1,5))
    return [{"name":name,"rows":rows,"steps":steps,
             "expected":walks_exact(rows,steps)}
            for name,rows,steps in cases]

def screen(hypothesis,cases):
    for i,case in enumerate(cases,1):
        got=simulate(case["rows"],case["steps"],hypothesis)
        if got!=case["expected"]:
            return {"passed":False,"checks":i,
                    "first_counterexample":{
                        "case":case["name"],"steps":case["steps"],
                        "rows":case["rows"],"expected":case["expected"],
                        "actual":got}}
    return {"passed":True,"checks":len(cases),"first_counterexample":None}

def memory_order(h):
    # PREDEFINED priority, chosen because the known RCE document explains
    # composition through the current relation; not learned from data.
    return (h["mask"]!="result",h["row_index"]!="i",
            h["bit_index"]!="j",h["negated"],h["id"])

def search(cases,guided=False):
    hyps=sorted(grammar(),key=memory_order) if guided else grammar()
    trace=[{"rank":i+1,"id":h["id"],"expression":h["expression"],
            **screen(h,cases)}
           for i,h in enumerate(hyps)]
    passed={r["id"] for r in trace if r["passed"]}
    return {
        "kind":"RCE-guided-priority" if guided else "fixed-unguided-order",
        "num_hypotheses":len(hyps),"trace":trace,
        "first_success_rank":next((r["rank"] for r in trace if r["passed"]),None),
        "survivors":[h for h in grammar() if h["id"] in passed],
        "survivor_ids":sorted(passed),
    }

def verify_rce(root=ROOT):
    record=compile_rce_tests(root)
    src=record["scientific_source"]
    path=(root/src["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise RuntimeError("RCE missing source")
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=src["source_blob_sha256"] or not all(record["matched_source_tags"].values()):
        raise RuntimeError("RCE source hash/tags not verified")
    if sha(ORIGINAL)!=FROZEN_ORIGINAL_SHA:
        raise RuntimeError("historical input changed")
    return {"source_path":src["path"],"source_sha256":actual,
            "line_ranges":src["line_ranges"],
            "search_sha256":src["search_sha256"],
            "tags":record["matched_source_tags"],
            "prior":"hardcoded mask=result,row=i,bit=j,not-negated first"}

def selector_prompt(candidates):
    if not candidates:
        raise ValueError("cannot select empty list")
    catalogue="\n".join(x["id"]+": "+x["expression"] for x in candidates)
    return ("<|im_start|>system\n"
            "Select one pretested symbolic repair by ID only. "
            "No Python source and no explanation.\n"
            "<|im_end|>\n<|im_start|>user\n"
            "A deterministic mathematical checker has tested these candidate "
            "patches against public examples. Choose the most natural Boolean "
            "composition condition. Hidden answers are not provided.\n"
            "Candidates:\n"+catalogue+"\n"
            "Return exactly one ID from the list, such as H03.\n"
            "<|im_end|>\n<|im_start|>assistant\n"+MARK)

def parse_selection(raw,prompt,candidate_ids):
    if prompt in raw:
        tail=raw.rsplit(prompt,1)[1]
    elif "... (truncated)\n" in raw:
        tail=raw.rsplit("... (truncated)\n",1)[1]
    else:
        raise ValueError("no authenticated output boundary")
    tail=tail.split("\n[ Prompt:",1)[0].split("<|im_end|>",1)[0]
    tail=tail.strip()
    if tail.startswith(MARK):
        tail=tail[len(MARK):].strip()
    tail=tail.replace(chr(96),"").strip()
    lines=[s.strip() for s in tail.splitlines() if s.strip()]
    if len(lines)!=1 or not re.fullmatch(r"H[0-9]{2}",lines[0]):
        raise ValueError("not a unique standalone ID")
    if lines[0] not in candidate_ids:
        raise ValueError("ID outside verified candidate list")
    return lines[0]

def qwen_select(cli,model,candidates):
    prompt=selector_prompt(candidates)
    cmd=[str(cli),"-m",str(model),"-p",prompt,
         "-n","64","-c","2048","-t","4","--temp","0"]
    t=time.perf_counter()
    try:
        out=subprocess.run(cmd,text=True,capture_output=True,timeout=180)
    except (OSError,subprocess.TimeoutExpired) as e:
        return {"called":True,"status":"CALL_FAILED","failure":type(e).__name__,
                "prompt_sha256":sha(prompt)}
    record={"called":True,"returncode":out.returncode,
            "prompt_sha256":sha(prompt),"prompt_chars":len(prompt),
            "raw_output_sha256":sha(out.stdout),"raw_tail":out.stdout[-1600:],
            "inference_seconds":round(time.perf_counter()-t,3)}
    if out.returncode:
        return {**record,"status":"CALL_FAILED","failure":out.stderr[-350:]}
    try:
        choice=parse_selection(out.stdout,prompt,{x["id"] for x in candidates})
        return {**record,"status":"VALID_SELECTION","selected_id":choice}
    except ValueError as e:
        return {**record,"status":"INVALID_SELECTION","failure":str(e)}

def qualify(survivors,train):
    result=[]
    for h in survivors:
        source=apply_patch(h["expression"])
        record={"id":h["id"],"expression":h["expression"],
                "source":source,"sha256":sha(source)}
        try:
            detail=score(source,train)  # real network-disabled Docker
            record["checks"]=detail
            record["development_correct"]=_all_correct(detail)
        except (RuntimeError,ValueError,TimeoutError) as e:
            record["development_correct"]=False
            record["failure"]=str(e)[:350]
        result.append(record)
    return result

def run(cli,model,root=ROOT):
    if not Path(cli).is_file() or not Path(model).is_file():
        raise RuntimeError("real pinned Qwen or llama-cli missing")
    plan,bundle=prepare(root)
    rce=verify_rce(root)
    cases=public_cases()
    seeds=[]
    while len(seeds)<N_HOLDOUT:
        n=secrets.randbits(48)
        if n not in seeds and n not in PUBLIC_SEEDS:
            seeds.append(n)
    heldout=[graph_case(x) for x in seeds]
    manifest=_manifest(heldout)
    manifest["experiment_id"]=EXP_ID
    frozen=digest(manifest)
    print("FROZEN_BEFORE_SYMBOLIC_OR_MODEL="+frozen,flush=True)
    print("MODEL_SEES_NO_RESERVED_CASES",flush=True)
    direct=search(cases,False)
    guided=search(cases,True)
    if direct["survivor_ids"]!=guided["survivor_ids"]:
        raise RuntimeError("ordering affected exact survivors")
    train=[graph_case(x) for x in PUBLIC_SEEDS]
    qualified=qualify(guided["survivors"],train)
    eligible=sorted([q for q in qualified if q["development_correct"]],
                    key=lambda q:q["id"])
    symbolic_choice=eligible[0]["id"] if eligible else None
    model_choice=qwen_select(cli,model,eligible) if eligible else {
        "called":False,"status":"NO_QUALIFIED_CANDIDATES"}
    qwen_id=model_choice.get("selected_id") if model_choice["status"]=="VALID_SELECTION" else None
    chosen={"symbolic_only":symbolic_choice,"symbolic_plus_qwen":qwen_id}
    refs=generate()
    classics={name:score(refs[name]["source"],heldout)
              for name in ("square-scan","square-lowbit")}
    if not all(_all_correct(rows) for rows in classics.values()):
        raise RuntimeError("classical oracle failed")
    strongest=min(sum(r["cost"] for r in rs) for rs in classics.values())
    prior_sources={x["source_sha256"] for x in known_prior_sources()}
    prior_sources.add(FROZEN_ORIGINAL_SHA)
    held_scores={}
    arms={}
    for label,ident in chosen.items():
        info={"candidate_id":ident,"holdout_opened":False,"decision":"REJECTED"}
        if ident:
            cand=next(x for x in eligible if x["id"]==ident)
            if ident not in held_scores:
                held_scores[ident]=score(cand["source"],heldout)
            evaluation=held_scores[ident]
            info.update({
                "holdout_opened":True,
                "results":evaluation,
                "correct":_all_correct(evaluation),
                "cost_us":sum(r["cost"] for r in evaluation),
                "source_sha256":cand["sha256"],
                "historical_duplicate":cand["sha256"] in prior_sources,
                "same_source_score_reused":sum(x==ident for x in chosen.values())>1,
            })
            gates={k:_gate_for(manifest,baseline,evaluation,refs[k]["sha256"],cand["sha256"])
                   for k,baseline in classics.items()}
            info["strong_gates"]={k:g["status"] for k,g in gates.items()}
            if (info["correct"] and not info["historical_duplicate"]
                and not info["same_source_score_reused"]
                and all(g["candidate_for_independent_review"] for g in gates.values())
                and info["cost_us"]<=(1-MIN_GAIN)*strongest):
                info["decision"]="REVIEW_REQUIRED"
        arms[label]=info
    execution=start_execution(plan,bundle)
    record_perspective(execution,"computational",status="completed",
        output=json.dumps({"symbolic_choice":symbolic_choice,"model_choice":qwen_id,
                           "Qwen_called":model_choice["called"],"frozen":frozen}),
        evidence_refs=["rce-file-sha256:"+rce["source_sha256"],
                       "heldout-manifest-sha256:"+frozen],
        limitations=["Closed 16-candidate grammar and human-selected faulty line.",
                     "Qwen chooses from already tested candidates, not original source.",
                     "One internally sealed experiment, no independent certification."])
    close_execution(execution)
    events=lifecycle_events(plan,bundle,execution)
    provenance=verify_events(events)
    if not provenance["valid"]:
        raise RuntimeError("local provenance broken")
    report={
        "experiment_id":EXP_ID,"status":"EXPERIMENTAL_NOT_CERTIFIED",
        "historical_source_sha256":FROZEN_ORIGINAL_SHA,
        "model_file_sha256":hashlib.sha256(Path(model).read_bytes()).hexdigest(),
        "rce":rce,"public_cases_count":len(cases),"public_cases_sha256":digest(cases),
        "symbolic_without_rce":direct,"symbolic_with_rce":guided,
        "development":qualified,"qualified_ids":[x["id"] for x in eligible],
        "model_selection":model_choice,
        "reserved_manifest_sha256":frozen,"reserved_manifest":manifest,
        "reserved_seeds_revealed_after_trials":seeds,
        "arms":arms,"classics":{
            k:{"correct":sum(r["correct"] and r["delta_correct"] for r in rows),
               "total_cost_us":sum(r["cost"] for r in rows),"rows":rows}
            for k,rows in classics.items()},
        "comparison":{
            "qwen_selection_differs_from_symbolic":bool(qwen_id and qwen_id!=symbolic_choice),
            "model_gain_demonstrated":False,
            "memory_generalization_demonstrated":False,
            "symbolic_mechanism_preprogrammed":True,
            "same_source_is_not_independent_replication":qwen_id==symbolic_choice,
        },
        "p3_coverage":execution["coverage"],"provenance":provenance,
        "events":events,"main_modified":False,"promotion_to_core":False,
        "limitations":[
            "The true classic patch is within a human-specified 16-expression grammar.",
            "Prioritization uses hardcoded expertise, not knowledge inferred by Qwen.",
            "If only one program is eligible, Qwen has no meaningful selection.",
            "Reserved seeds are internally created and hashed, not externally sealed.",
            "One Qwen call, one task; no statistical generalization.",
            "Docker timings include container startup noise.",
        ],
    }
    report["report_sha256_without_self"]=digest(report)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llama-cli",type=Path,required=True)
    p.add_argument("--model-file",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("symbolic-neural-result.json"))
    args=p.parse_args()
    report=run(args.llama_cli,args.model_file)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment_id":report["experiment_id"],
        "survivors":report["symbolic_with_rce"]["survivor_ids"],
        "first_success_no_rce":report["symbolic_without_rce"]["first_success_rank"],
        "first_success_rce":report["symbolic_with_rce"]["first_success_rank"],
        "model":{k:v for k,v in report["model_selection"].items()
                 if k in ("called","status","selected_id","failure")},
        "arms":{k:{"id":v["candidate_id"],"correct":v.get("correct"),
                   "decision":v["decision"],"holdout_opened":v["holdout_opened"]}
                for k,v in report["arms"].items()},
        "provenance_valid":report["provenance"]["valid"],
        "scientific_gain":False,
    },ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
