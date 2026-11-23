"""SELF-TEACH-04 — finite self-repair with full SHA-chained raw attempt log.

Generation reads ONLY TRAIN_FROZEN and EVAL_PUBLIC_FROZEN; sealed tests are
used by the separate scorer after generation finishes. AST sandbox reused.
"""
from __future__ import annotations
import argparse
import copy
from hashlib import sha1,sha256
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"self_teach01"))
sys.path.insert(0,str(HERE.parents[1]/"learning_lab"))
import pilot as old
import format_audit

SAFE=old.safe
SCHEMA="OMEGA_SELF_TEACH04_GENERATED_V1"
PINS={
"TRAIN_FROZEN.json":"b9c854ab3dfd2fea03a108d1f14df671b51737db",
"EVAL_PUBLIC_FROZEN.json":"753efdf569bc53e58703da5d73e428345d48a038",
"EVAL_SEALED_FROZEN.json":"40824dd6efdd2abf4f6f54fa37aa76480af7046d",
}
GEN_CAP=660
LESSON_CAP=160
NEUTRAL="Check corner cases, preserve the exact requested output type and return one valid Python function."
MAX_REPAIRS=2
MAX_FEEDBACK=3


def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")


def hexdigest(obj):
    return sha256(canonical(obj)).hexdigest()


def git_blob(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()


def frozen(name):
    if name not in PINS:
        raise ValueError("UNAUTHORIZED_FROZEN_READ")
    raw=(HERE/name).read_bytes()
    if len(raw)>65000 or git_blob(raw)!=PINS[name]:
        raise ValueError("FROZEN_CONTENT_CHANGED")
    return json.loads(raw)


def public_data():
    train=frozen("TRAIN_FROZEN.json")
    ev=frozen("EVAL_PUBLIC_FROZEN.json")
    if train.get("schema")!="OMEGA_SELF_TEACH04_TRAIN_V1" or ev.get("schema")!="OMEGA_SELF_TEACH04_EVAL_PUBLIC_V1":
        raise ValueError("PUBLIC_SCHEMA")
    t,e=train["train"],ev["evaluation"]
    if len(t)!=2 or len(e)!=3 or len({x["family"] for x in t+e})!=5 or len({x["id"] for x in t+e})!=5:
        raise ValueError("TRAIN_EVAL_OVERLAP_OR_SIZE")
    for task in t:
        if len(task["development_cases"])!=10:
            raise ValueError("EXPECTED_TEN_DEV_CASES")
    for task in t+e:
        if len(task["public_examples"])<2 or not task["goal"]:
            raise ValueError("BAD_PUBLIC_TASK")
    return t,e


def parse(raw):
    strict,strict_status=old.inspect_code(raw)
    if strict is not None:
        return strict,"ORIGINAL_SAFE",strict_status
    normalized,fmt=format_audit.recover_raw(raw)
    if normalized is not None:
        SAFE.validate_program(normalized)
        return normalized,"ESCAPED_LINE_NORMALIZED",strict_status
    return None,"REJECTED:"+fmt,strict_status


def grade_cases(code,cases):
    got=(SAFE.execute_student(code,[c["input"] for c in cases])
         if code is not None else [{"error":"NO_SAFE_CODE"} for _ in cases])
    rows=[]
    for c,r in zip(cases,got):
        rows.append({"input":c["input"],"expected":c["expected"],
                     "observed":r,
                     "correct":r.get("value")==c["expected"],
                     "failure_kind":("none" if r.get("value")==c["expected"]
                                     else "execution_error" if "error" in r
                                     else "wrong_output")})
    return {"correct":sum(x["correct"] for x in rows),
            "total":len(rows),"rows":rows}


def trace_append(log,kind,payload):
    prev=log[-1]["sha256"] if log else "0"*64
    data={"seq":len(log),"previous_sha256":prev,"kind":kind,"payload":payload}
    log.append({**data,"sha256":hexdigest(data)})


def verify_trace(log):
    if not isinstance(log,list) or not log:
        raise ValueError("MISSING_TRACE")
    prev="0"*64
    for i,item in enumerate(log):
        payload={k:v for k,v in item.items() if k!="sha256"}
        if item.get("seq")!=i or item.get("previous_sha256")!=prev or item.get("sha256")!=hexdigest(payload):
            raise ValueError("TRACE_CHAIN_BROKEN")
        prev=item["sha256"]
    return prev


def task_prompt(task,note=None):
    s=("Produce one valid JSON object with fields 'hypothesis' (short English explanation of your intended algorithm) "
       "and 'code' (complete Python def transform(s) returning a list of strings). "
       "No imports/files/network. Respect the exact specification and all examples.\n"
       "TASK: "+task["goal"]+"\nEXAMPLES: "+
       json.dumps(task["public_examples"],ensure_ascii=False))
    if note is not None:
        s+="\nPROGRAMMING_NOTE: "+note
    return s


def ask(client,task,tag,note=None,prompt_override=None):
    prompt=prompt_override if prompt_override is not None else task_prompt(task,note)
    raw=client([{"role":"system","content":SAFE.SYSTEM},
                {"role":"user","content":prompt}],GEN_CAP,tag)
    code,status,strict=parse(raw)
    parsed=SAFE.parse_json(raw)
    hypothesis=parsed.get("hypothesis","") if parsed else ""
    if not isinstance(hypothesis,str):
        hypothesis=""
    return {"id":task["id"],"family":task["family"],
            "raw":raw,"raw_sha256":sha256(raw.encode()).hexdigest(),
            "prompt_sha256":sha256(prompt.encode()).hexdigest(),
            "code":code,"parse_status":status,"original_parse_status":strict,
            "hypothesis":hypothesis[:600],"tag":tag,"note":note}


def feedback_for(dev):
    # Never choose feedback by hidden score. Deterministic smallest failures.
    failures=[x for x in dev["rows"] if not x["correct"]]
    failures.sort(key=lambda x:(len(x["input"]),x["input"]))
    return failures[:MAX_FEEDBACK]


def recorded_trial(log,task,reply,dev,accepted,prior_score):
    trace_append(log,"TRAIN_ATTEMPT",{
        "task_id":task["id"],"family":task["family"],
        "raw":reply["raw"],"raw_sha256":reply["raw_sha256"],
        "prompt_sha256":reply["prompt_sha256"],
        "code":reply["code"],"parse_status":reply["parse_status"],
        "original_parse_status":reply["original_parse_status"],
        "hypothesis":reply["hypothesis"],"tag":reply["tag"],
        "development":dev,"accepted_to_best":accepted,
        "previous_best_correct":prior_score,
        "decision":("ACCEPT_IMPROVEMENT" if accepted else "ROLLBACK_NO_GAIN"),
    })


def practice(client,train,log):
    starts=[]
    for task in train:
        reply=ask(client,task,"train:"+task["id"]+":first")
        dev=grade_cases(reply["code"],task["development_cases"])
        recorded_trial(log,task,reply,dev,True,-1)
        starts.append({"task":task,"reply":reply,"dev":dev})
    chosen=min(starts,key=lambda a:(a["dev"]["correct"],a["task"]["id"]))
    task=chosen["task"]
    score0=chosen["dev"]["correct"]
    best=chosen
    trace_append(log,"SELF_SELECTED_TASK",{
        "policy":"LOWEST_INITIAL_DEVELOPMENT_SCORE",
        "selected_id":task["id"],
        "scores":[{"id":x["task"]["id"],"correct":x["dev"]["correct"]}
                  for x in starts]})
    for attempt in range(MAX_REPAIRS):
        if best["dev"]["correct"]==10:
            break
        feedback=feedback_for(best["dev"])
        prompt=(task_prompt(task)+"\nCURRENT_CODE: "+
                json.dumps(best["reply"]["code"],ensure_ascii=False)+
                "\nDIAGNOSTIC_EXACT_PUBLIC_DEVELOPMENT_CASES: "+
                json.dumps(feedback,ensure_ascii=False)+
                "\nTrace the FIRST failed example character-by-character: track index, current run, decision, expected and observed; identify the first divergent decision. Then infer a general cause, not a patch for one string. "
                "Then return JSON with 'hypothesis' and COMPLETE revised 'code'. "
                "Never claim tests prove universal correctness.")
        trace_append(log,"FEEDBACK_OFFERED",{
            "task_id":task["id"],"attempt":attempt+1,
            "prior_raw_sha256":best["reply"]["raw_sha256"],
            "shown_failed_cases":feedback,"shown_case_count":len(feedback),
            "prompt_sha256":sha256(prompt.encode()).hexdigest(),
            "selection_rule":"3_MINIMAL_DEVELOPMENT_FAILURES_ONLY",
        })
        reply=ask(client,task,"train:"+task["id"]+":repair"+str(attempt+1),
                  prompt_override=prompt)
        dev=grade_cases(reply["code"],task["development_cases"])
        oldscore=best["dev"]["correct"]
        accepted=(reply["code"] is not None and dev["correct"]>oldscore)
        recorded_trial(log,task,reply,dev,accepted,oldscore)
        if accepted:
            best={"task":task,"reply":reply,"dev":dev}
    mastered=(score0<10 and best["dev"]["correct"]==10 and
              best["reply"]["code"] is not None)
    memory=""
    if mastered:
        prompt=("Summarize a general reusable programming lesson from the following verified, "
                "limited practice repair. JSON only {'lesson': string <=240 characters}. "
                "Do not output the task solution or assert universal proof.\nGoal: "+
                task["goal"]+"\nStarting score: "+str(score0)+"/10\nFinal repaired program:\n"+
                best["reply"]["code"])
        raw=client([{"role":"system","content":SAFE.SYSTEM},
                    {"role":"user","content":prompt}],LESSON_CAP,
                   "train:"+task["id"]+":lesson")
        parsed=SAFE.parse_json(raw)
        candidate=parsed.get("lesson") if parsed else None
        if isinstance(candidate,str) and 8<=len(candidate.strip())<=240:
            memory=candidate.strip()
        trace_append(log,"LESSON_CANDIDATE",{
            "task_id":task["id"],"raw":raw,
            "raw_sha256":sha256(raw.encode()).hexdigest(),
            "admitted":bool(memory),"lesson":memory,
            "support_correct":best["dev"]["correct"],"support_total":10,
            "support_initial":score0})
    trace_append(log,"PRACTICE_DECISION",{
        "task_id":task["id"],"initial_score":score0,
        "best_score":best["dev"]["correct"],
        "best_raw_sha256":best["reply"]["raw_sha256"],
        "mastered":mastered,"memory_admitted":bool(memory),
        "memory":memory,"gradients":0,
    })
    return {"selected_id":task["id"],"initial_score":score0,
            "best_score":best["dev"]["correct"],"mastered":mastered,
            "admitted_memory":memory,
            "memory_status":("LIMITED_PRACTICE_MEMORIZED" if memory
                             else "NO_ADMISSIBLE_MEMORY"),
            "best_source_sha256":best["reply"]["raw_sha256"],
            "max_repairs":MAX_REPAIRS,"hidden_gold_used":False,
            "gradient_updates":0}


def run(client):
    start=time.monotonic()
    train,evaluation=public_data()
    log=[]
    A=[ask(client,task,"A:"+task["id"]) for task in evaluation]
    learned=practice(client,train,log)
    P=[ask(client,task,"P:"+task["id"],NEUTRAL) for task in evaluation]
    note=learned["admitted_memory"] or NEUTRAL
    # If no memory was verified, running B with the same P prompt merely
    # samples generation noise. B is an auditable alias of P instead.
    if learned["admitted_memory"]:
        B=[ask(client,task,"B:"+task["id"],note) for task in evaluation]
    else:
        B=[{**copy.deepcopy(x),"tag":"B:"+task["id"]}
           for x,task in zip(P,evaluation)]
    trace_append(log,"RUN_COMPLETE",{
        "A_ids":[x["id"] for x in A],"P_ids":[x["id"] for x in P],
        "B_ids":[x["id"] for x in B],
        "memory_admitted":bool(learned["admitted_memory"]),
        "sealed_gold_used":False})
    client_log=getattr(client,"call_log",None)
    return {"schema":SCHEMA,"status":"GENERATED_NOT_SCORED",
            "frozen_git_blobs":PINS,"model":SAFE.MODEL,
            "A":A,"P":P,"B":B,"practice":learned,
            "B_alias_of_P_without_memory":not bool(learned["admitted_memory"]),
            "B_actual_model_calls":3 if learned["admitted_memory"] else 0,
            "training_trace":log,"training_trace_head":verify_trace(log),
            "C":{"status":"TRAINING_NOT_AUTHORIZED","weight_updates":0},
            "generation_cap_per_eval":GEN_CAP,
            "evaluation_calls_each":3,"max_repairs":MAX_REPAIRS,
            "total_llm_calls":(len(client_log) if client_log is not None else None),
            "client_call_log":client_log,
            "duration_seconds":round(time.monotonic()-start,3),
            "sealed_test_loaded_during_generation":False,
            "paid_apis":0,"main_modified":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--server",required=True)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=run(SAFE.Client(args.server))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print("SELF_TEACH04_GENERATED",
          "trace_events",len(result["training_trace"]),
          "initial",result["practice"]["initial_score"],
          "best",result["practice"]["best_score"],
          "memory",result["practice"]["memory_status"],
          "calls",result["total_llm_calls"],flush=True)

if __name__=="__main__":
    main()
