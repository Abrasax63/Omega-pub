"""SELF05: paired correction with batch vs per-example diagnostic. No sealed reads."""
from __future__ import annotations
import argparse
from hashlib import sha1,sha256
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
import importlib.util
spec=importlib.util.spec_from_file_location("omega_self04_runner",HERE.parent/"self_teach04"/"runner.py")
old=importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
SAFE=old.SAFE
PINS={"PUBLIC_FROZEN.json":"5c9045fd723bbe5cfb6f175a516bef41f49467f3",
      "SEALED_FROZEN.json":"ff9e0cbae6fe5cc9a28d62ffed019ec22a2a3646"}
SCHEMA="OMEGA_SELF05_RAW_V1"
MAX_REPAIRS=2
GEN_CAP=660

def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def frozen(name):
    if name not in PINS: raise ValueError("UNAUTHORIZED_FROZEN")
    b=(HERE/name).read_bytes()
    if sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()!=PINS[name]:
        raise ValueError("PIN_MISMATCH")
    return json.loads(b)

def public():
    x=frozen("PUBLIC_FROZEN.json")
    if x.get("schema")!="OMEGA_SELF_TEACH05_PUBLIC_V1": raise ValueError("PUBLIC_SCHEMA")
    tasks=x["tasks"]
    if len(tasks)!=4 or len({t["id"] for t in tasks})!=4 or len({t["family"] for t in tasks})!=4:
        raise ValueError("PUBLIC_SIZE")
    for t in tasks:
        if len(t["public_examples"])!=2 or len(t["development_cases"])!=8:
            raise ValueError("PUBLIC_CASES")
    return tasks

def grade_dev(code,cases,mode):
    if mode not in ("batch","isolated"): raise ValueError("BAD_MODE")
    start=time.monotonic()
    if code is None:
        obs=[{"error":"NO_CODE"} for _ in cases]
        workers=0
    elif mode=="batch":
        obs=SAFE.execute_student(code,[r["input"] for r in cases])
        workers=1
    else:
        obs=[SAFE.execute_student(code,[r["input"]])[0] for r in cases]
        workers=len(cases)
    rows=[]
    for case,result in zip(cases,obs):
        correct=result.get("value")==case["expected"]
        rows.append({"input":case["input"],"expected":case["expected"],
                     "observed":result,"correct":correct})
    return {"rows":rows,"correct":sum(r["correct"] for r in rows),
            "workers":workers,"seconds":round(time.monotonic()-start,4)}

def feedback(result):
    wrong=[r for r in result["rows"] if not r["correct"]]
    return sorted(wrong,key=lambda r:(len(r["input"]),r["input"]))[:3]

def base_prompt(task):
    return old.task_prompt(task)

def repair_prompt(task,best,errors):
    return (base_prompt(task)+"\nCURRENT_CODE: "+json.dumps(best["code"],ensure_ascii=False)+
            "\nDEVELOPMENT_FEEDBACK: "+json.dumps(errors,ensure_ascii=False)+
            "\nDiagnose the FIRST divergent state, index or loop-progress error. "
            "Infer a rule, not a patch for the shown strings. Return JSON with "
            "hypothesis and a complete safe function, no imports.")

def ask(client,task,prompt,tag):
    raw=client([{"role":"system","content":SAFE.SYSTEM},
                {"role":"user","content":prompt}],GEN_CAP,tag)
    code,status,strict=old.parse(raw)
    return {"id":task["id"],"family":task["family"],"tag":tag,"raw":raw,
            "raw_sha256":sha256(raw.encode()).hexdigest(),
            "prompt_sha256":sha256(prompt.encode()).hexdigest(),
            "code":code,"parse_status":status,"strict_status":strict}

def arm(client,task,initial,mode):
    best=initial
    score=grade_dev(best["code"],task["development_cases"],"isolated")
    events=[]
    workers=score["workers"]
    seconds=score["seconds"]
    for n in range(1,3):
        if score["correct"]==8: break
        observed=grade_dev(best["code"],task["development_cases"],mode)
        cases=feedback(observed)
        workers+=observed["workers"]
        seconds+=observed["seconds"]
        answer=ask(client,task,repair_prompt(task,best,cases),
                   mode.upper()+":"+task["id"]+":repair"+str(n))
        test=grade_dev(answer["code"],task["development_cases"],"isolated")
        workers+=test["workers"]
        seconds+=test["seconds"]
        good=answer["code"] is not None and test["correct"]>score["correct"]
        events.append({"number":n,"shown":cases,"diagnostic_correct":observed["correct"],
                       "candidate":answer,"candidate_correct":test["correct"],
                       "previous_correct":score["correct"],"accepted":good})
        if good: best,score=answer,test
    return {"mode":mode,"initial_sha256":initial["raw_sha256"],
            "best":best,"best_correct":score["correct"],"attempts":events,
            "workers":workers,"seconds":round(seconds,4)}

def run(client):
    start=time.monotonic()
    pairs=[]
    for task in public():
        first=ask(client,task,base_prompt(task),"INIT:"+task["id"])
        pairs.append({"id":task["id"],"initial":first,
                      "batch":arm(client,task,first,"batch"),
                      "isolated":arm(client,task,first,"isolated")})
    calls=getattr(client,"call_log",None)
    out={"schema":SCHEMA,"status":"GENERATED_NOT_SCORED","pins":PINS,
         "pairs":pairs,"generation_cap":GEN_CAP,"model":SAFE.MODEL,
         "calls":len(calls) if calls is not None else None,
         "call_log":calls,"elapsed_seconds":round(time.monotonic()-start,3),
         "sealed_read":False,"weight_updates":0,"paid_apis":0,"main_modified":False}
    out["digest"]=digest(out)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--server",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run(SAFE.Client(a.server))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("SELF05_GENERATED",result["calls"],"calls",result["digest"],flush=True)

if __name__=="__main__": main()
