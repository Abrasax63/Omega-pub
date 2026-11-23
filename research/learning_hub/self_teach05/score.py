"""SELF05 scored independently after raw paired generations are on disk."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runner

def check(value,reason):
    if not value: raise ValueError(reason)

def candidate(t,item):
    raw=item.get("raw")
    check(isinstance(raw,str) and sha256(raw.encode()).hexdigest()==item.get("raw_sha256"),
          "CHANGED_RAW")
    code,status,strict=runner.old.parse(raw)
    check(code==item.get("code") and status==item.get("parse_status") and
          strict==item.get("strict_status") and
          item.get("id")==t["id"] and item.get("family")==t["family"],
          "CHANGED_CODE")
    return code

def validate(raw):
    unsealed=dict(raw)
    stamp=unsealed.pop("digest",None)
    check(stamp==runner.digest(unsealed),"CHANGED_RUN_DIGEST")
    check(raw.get("schema")==runner.SCHEMA and raw.get("status")=="GENERATED_NOT_SCORED" and
          raw.get("pins")==runner.PINS and raw.get("sealed_read") is False and
          raw.get("weight_updates")==0 and raw.get("paid_apis")==0 and
          raw.get("main_modified") is False and raw.get("generation_cap")==runner.GEN_CAP,
          "INVALID_RUN_CONTRACT")
    tasks=runner.public()
    check(len(raw.get("pairs",[]))==len(tasks),"PAIR_COUNT")
    call_count=0
    for task,pair in zip(tasks,raw["pairs"]):
        check(task["id"]==pair.get("id"),"TASK_ORDER")
        initial=pair["initial"]
        candidate(task,initial)
        check(initial.get("tag")=="INIT:"+task["id"] and
              initial.get("prompt_sha256")==sha256(runner.base_prompt(task).encode()).hexdigest(),
              "CHANGED_INITIAL_PROMPT")
        call_count+=1
        for mode in ("batch","isolated"):
            arm=pair[mode]
            check(arm.get("mode")==mode and
                  arm.get("initial_sha256")==initial["raw_sha256"] and
                  len(arm["attempts"])<=2,"UNPAIRED_START_OR_REPAIRS")
            best=initial
            initial_score=runner.grade_dev(best["code"],task["development_cases"],"isolated")["correct"]
            best_score=initial_score
            for n,e in enumerate(arm["attempts"],1):
                check(e["number"]==n and best_score<8,"UNEXPECTED_REVISION")
                dev=runner.grade_dev(best["code"],task["development_cases"],mode)
                shown=runner.feedback(dev)
                check(e["shown"]==shown and e["diagnostic_correct"]==dev["correct"],
                      "FALSE_FEEDBACK_OR_GOLD_LEAK")
                gen=e["candidate"]
                candidate(task,gen)
                check(gen["tag"]==mode.upper()+":"+task["id"]+":repair"+str(n) and
                      gen["prompt_sha256"]==
                      sha256(runner.repair_prompt(task,best,shown).encode()).hexdigest(),
                      "REVISION_PROMPT_CHANGED")
                grade=runner.grade_dev(gen["code"],task["development_cases"],"isolated")
                improved=gen["code"] is not None and grade["correct"]>best_score
                check(e["candidate_correct"]==grade["correct"] and
                      e["previous_correct"]==best_score and
                      e["accepted"] is improved,"UNJUSTIFIED_ACCEPTANCE")
                if improved: best,best_score=gen,grade["correct"]
                call_count+=1
            check(best==arm["best"] and best_score==arm["best_correct"],
                  "BEST_NOT_PRESERVED")
    check(call_count==raw.get("calls") and len(raw.get("call_log") or [])==call_count and
          call_count<=20,"MODEL_CALL_BUDGET")
    return tasks

def results(rows,holdout):
    out=[]
    for src,gold in zip(rows,holdout):
        observations=runner.grade_dev(src["code"],gold["hidden_cases"],"isolated")
        out.append({"id":gold["id"],"exact":observations["correct"],"total":6,
                    "full":observations["correct"]==6,
                    "safe":src["code"] is not None,
                    "raw_sha256":src["raw_sha256"],
                    "seconds":observations["seconds"]})
    return {"exact":sum(x["exact"] for x in out),"total":24,
            "full":sum(x["full"] for x in out),
            "safe":sum(x["safe"] for x in out),"rows":out}

def grade(raw):
    tasks=validate(raw)
    hold=runner.frozen("SEALED_FROZEN.json")
    check(hold.get("schema")=="OMEGA_SELF_TEACH05_SEALED_V1" and
          len(hold.get("tasks",[]))==4,"SEALED_SCHEMA")
    gold=hold["tasks"]
    for task,h in zip(tasks,gold):
        check(task["id"]==h["id"] and task["family"]==h["family"] and
              len(h["hidden_cases"])==6,"SEALED_TASK_ALIGNMENT")
        known={z["input"] for z in task["public_examples"]+task["development_cases"]}
        check(not known.intersection(z["input"] for z in h["hidden_cases"]),
              "SEALED_OVERLAP")
    paired=raw["pairs"]
    initial=results([x["initial"] for x in paired],gold)
    batch=results([x["batch"]["best"] for x in paired],gold)
    isolated=results([x["isolated"]["best"] for x in paired],gold)
    regress=sum((a["full"] or b["full"]) and not i["full"]
                for a,b,i in zip(initial["rows"],batch["rows"],isolated["rows"]))
    delta=isolated["exact"]-batch["exact"]
    accept=delta>=2 and regress==0 and isolated["safe"]>=batch["safe"]
    return {"schema":"OMEGA_SELF05_SCORED_V1",
            "status":"EXPLORATORY_ISOLATED_FEEDBACK_GAIN" if accept else
                     "NO_VERIFIED_ISOLATED_FEEDBACK_GAIN",
            "INITIAL":initial,"BATCH":batch,"ISOLATED":isolated,
            "delta_iso_minus_batch":delta,"regressed_full_tasks":regress,
            "calls":raw["calls"],"generation_seconds":raw["elapsed_seconds"],
            "workers":{k:sum(x[k]["workers"] for x in paired) for k in ("batch","isolated")},
            "diagnostic_seconds":{k:round(sum(x[k]["seconds"] for x in paired),4)
                                  for k in ("batch","isolated")},
            "consumed_sealed":True,"new_weights":0,"durable_learning_proven":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=grade(json.loads(args.raw.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("SELF05_RESULT",out["status"],"INIT",out["INITIAL"]["exact"],
          "BATCH",out["BATCH"]["exact"],"ISOLATED",out["ISOLATED"]["exact"],
          "of",out["BATCH"]["total"],flush=True)

if __name__=="__main__": main()
