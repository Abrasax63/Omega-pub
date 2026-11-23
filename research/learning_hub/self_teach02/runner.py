"""OMEGA-SELF-TEACH-02: preregistered, bounded self-tutoring; NO sealed gold access.

Reuses #242's narrow format normalizer + #232's AST sandbox and local CPU
Qwen client. C LoRA is deliberately blocked. Model outputs never touch Git.
"""
from __future__ import annotations
import argparse
from hashlib import sha1,sha256
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"self_teach01"
LAB=HERE.parents[1]/"learning_lab"
sys.path.insert(0,str(OLD))
sys.path.insert(0,str(LAB))
import pilot as old_pilot
import format_audit
import prog_reconstruction_pilot as safe

PINS={
    "TRAIN_FROZEN.json":"515e6b336f9219efe0918d1ffa8f64f83f296ab0",
    "EVAL_PUBLIC_FROZEN.json":"a0cc42fad92282530cf0cf097f070ced32003b86",
    "EVAL_SEALED_FROZEN.json":"1ba510a475523e277619f354175488e74d590408",
}
SCHEMA="OMEGA_SELF_TEACH02_GENERATED_V1"
GEN_CAP=660
LESSON_CAP=160
NEUTRAL="Check edge cases and return the required list of strings. Never assume an input contains only the characters in examples."
MAX_REVISIONS=2


def git_blob(data):
    return sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()


def read_frozen(name):
    if name not in PINS:
        raise ValueError("UNKNOWN_FROZEN_FILE")
    raw=(HERE/name).read_bytes()
    if len(raw)>60000 or git_blob(raw)!=PINS[name]:
        raise ValueError("FROZEN_BLOB_SHA_MISMATCH")
    return json.loads(raw)


def public_cohorts():
    train=read_frozen("TRAIN_FROZEN.json")
    evaluation=read_frozen("EVAL_PUBLIC_FROZEN.json")
    if train.get("schema")!="OMEGA_SELF_TEACH02_TRAIN_V1":
        raise ValueError("INVALID_TRAIN_SCHEMA")
    if evaluation.get("schema")!="OMEGA_SELF_TEACH02_EVAL_PUBLIC_V1":
        raise ValueError("INVALID_PUBLIC_EVAL_SCHEMA")
    t,e=train["train"],evaluation["evaluation"]
    if len(t)!=2 or len(e)!=3 or len({x["family"] for x in t+e})!=5:
        raise ValueError("TRAIN_EVAL_FAMILY_OVERLAP")
    if len({x["id"] for x in t+e})!=5:
        raise ValueError("TRAIN_EVAL_ID_OVERLAP")
    for x in t:
        if len(x["development_cases"])!=8:
            raise ValueError("TRAIN_DEV_COUNT")
    for x in t+e:
        if not x["goal"] or len(x["public_examples"])<2:
            raise ValueError("MISSING_PUBLIC_EXAMPLES")
    return t,e


def parse_and_guard(raw):
    # Original strict parse and then STRICT posthoc-tested format-only normalization.
    direct,strict=old_pilot.inspect_code(raw)
    if direct is not None:
        return direct,"ORIGINAL_SAFE",strict
    recovered,status=format_audit.recover_raw(raw)
    if recovered is None:
        return None,"REJECTED:"+status,strict
    safe.validate_program(recovered)
    return recovered,status,strict


def score_dev(code,cases):
    vals=(safe.execute_student(code,[x["input"] for x in cases])
          if code is not None else [{"error":"NO_CODE"} for x in cases])
    rows=[{"input":case["input"],"expected":case["expected"],"received":got,
           "correct":got.get("value")==case["expected"]}
          for case,got in zip(cases,vals)]
    return {"correct":sum(x["correct"] for x in rows),
            "total":len(rows),"rows":rows}


def task_prompt(task,note=None):
    message=("Infer a Python function from the stated behavior and examples. "
             "Return exactly one JSON object with key 'code', containing a single "
             "complete def transform(s) returning list[str], no imports, no file "
             "access.\\nGOAL: "+task["goal"]+"\\nOBSERVATIONS: "+
             json.dumps(task["public_examples"],ensure_ascii=False))
    # Additional controlled note, identical for the comparator P and B
    # whenever no practice lesson passed its verification gate.
    if note is not None:
        message+="\\nPROGRAMMING_NOTE: "+note
    return message


def ask_code(client,task,tag,note=None,override_prompt=None):
    message=override_prompt if override_prompt is not None else task_prompt(task,note)
    raw=client([{"role":"system","content":safe.SYSTEM},
                {"role":"user","content":message}],GEN_CAP,tag)
    code,status,strict=parse_and_guard(raw)
    return {"id":task["id"],"family":task["family"],
            "raw":raw,"sha256_raw":sha256(raw.encode()).hexdigest(),
            "code":code,"code_status":status,"original_strict_status":strict,
            "prompt_sha256":sha256(message.encode()).hexdigest(),
            "note_used":bool(note),"call_tag":tag}


def learn(client,train):
    initial=[]
    for x in train:
        candidate=ask_code(client,x,"train:"+x["id"]+":initial")
        dev=score_dev(candidate["code"],x["development_cases"])
        initial.append({"candidate":candidate,"dev":dev})
    chosen=min(range(len(train)),
               key=lambda i:(initial[i]["dev"]["correct"],train[i]["id"]))
    task=train[chosen]
    best=initial[chosen]
    best_score=best["dev"]["correct"]
    start_score=best_score
    trials=[]
    for r in range(MAX_REVISIONS):
        if best_score==len(task["development_cases"]):
            break
        failures=[x for x in best["dev"]["rows"] if not x["correct"]][:4]
        repair_prompt=(task_prompt(task)+"\\nCURRENT_SOLUTION: "+
                       json.dumps(best["candidate"]["code"])+
                       "\\nDEVELOPMENT_ERRORS_ONLY: "+
                       json.dumps(failures,ensure_ascii=False)+
                       "\\nCorrect the code based only on these practice errors. "
                       "Return a JSON object with 'code' as the complete function. "
                       "Do not claim proof based on finitely many tests.")
        candidate=ask_code(client,task,"train:"+task["id"]+":repair"+str(r+1),
                           override_prompt=repair_prompt)
        dev=score_dev(candidate["code"],task["development_cases"])
        accepted=dev["correct"]>best_score and candidate["code"] is not None
        trials.append({"attempt":r+1,"correct":dev["correct"],
                       "total":dev["total"],"format_status":candidate["code_status"],
                       "better_than_best":accepted})
        if accepted:
            best={"candidate":candidate,"dev":dev}
            best_score=dev["correct"]
    mastered=(start_score<8 and best_score==8 and
              best["candidate"]["code"] is not None)
    memory=""
    lesson_raw=None
    if mastered:
        prompt=(
            "Summarize one reusable programming lesson learned from the "
            "following successfully repaired task. Do NOT include code, a "
            "solution to an unknown task, or overclaim beyond the eight "
            "development examples. Return JSON {'lesson':str}, at most 240 "
            "characters. Practice task: "+task["goal"]+
            "\\nFirst attempt correct: "+str(start_score)+"/8."+
            "\\nFinal candidate code: "+best["candidate"]["code"])
        lesson_raw=client([{"role":"system","content":safe.SYSTEM},
                           {"role":"user","content":prompt}],
                          LESSON_CAP,"train:"+task["id"]+":lesson")
        decoded=safe.parse_json(lesson_raw)
        note=decoded.get("lesson") if decoded else None
        if isinstance(note,str) and 8<=len(note.strip())<=240:
            memory=note.strip()
    return {
        "self_selected_task":task["id"],
        "policy":"WEAKEST_INITIAL_SCORE_THEN_MAX_TWO_REPAIRS",
        "initial_scores":[{"id":x["id"],"correct":y["dev"]["correct"],
                           "total":y["dev"]["total"]}
                          for x,y in zip(train,initial)],
        "initial_selected_score":start_score,
        "best_dev_correct":best_score,"best_dev_total":8,
        "revisions":trials,
        "mastered_practice":mastered,
        "lesson_raw":lesson_raw,
        "admitted_memory":memory,
        "memory_status":("ADMITTED_LIMITED_PRACTICE_ONLY" if memory
                          else "NO_VERIFIED_MEMORY"),
        "hidden_evaluation_used_in_training":False,
        "gradient_updates":0,
    }


def run(client):
    start=time.monotonic()
    train,evals=public_cohorts()
    direct=[ask_code(client,x,"A:"+x["id"]) for x in evals]
    practice=learn(client,train)
    control=[ask_code(client,x,"P:"+x["id"],NEUTRAL) for x in evals]
    note=practice["admitted_memory"] or NEUTRAL
    learned=[ask_code(client,x,"B:"+x["id"],note) for x in evals]
    calls=getattr(client,"call_log",None)
    return {
        "schema":SCHEMA,"status":"GENERATED_NOT_SCORED",
        "frozen_git_blobs":PINS,"model":safe.MODEL,
        "read_only_on_github":True,
        "A":direct,"P":control,"B":learned,
        "practice":practice,
        "C":{"status":"TRAINING_NOT_AUTHORIZED","new_weight_updates":0},
        "per_task_generation_cap":GEN_CAP,
        "evaluation_calls_each":len(evals),
        "total_llm_calls":len(calls) if calls is not None else None,
        "client_call_log":calls,
        "duration_s":round(time.monotonic()-start,3),
        "sealed_gold_imported_during_generation":False,
        "paid_api_calls":0,"main_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--server",required=True)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=run(safe.Client(args.server))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print("SELF_TEACH02_GENERATED",result["practice"]["memory_status"],
          "calls",result["total_llm_calls"],flush=True)


if __name__=="__main__":
    main()
