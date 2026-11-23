"""SELF-TEACH-04 blind scoring and independent revalidation of the FULL training trace."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runner

SCHEMA="OMEGA_SELF_TEACH04_SCORED_V1"


def require(ok,reason):
    if not ok:
        raise ValueError(reason)


def validate_training_trace(raw):
    trace=raw.get("training_trace")
    head=runner.verify_trace(trace)
    require(head==raw.get("training_trace_head"),"TRACE_HEAD_MISMATCH")
    train,_=runner.public_data()
    by_id={x["id"]:x for x in train}
    current={}
    initials={}
    repaired=0
    pending=None
    lesson=None
    selection=None
    decision=None
    for e in trace:
        kind,p=e["kind"],e["payload"]
        if kind=="TRAIN_ATTEMPT":
            require(p.get("task_id") in by_id and
                    p.get("family")==by_id[p["task_id"]]["family"],
                    "TRACE_TASK_ID_MISMATCH")
            task=by_id[p["task_id"]]
            rawtext=p.get("raw")
            require(isinstance(rawtext,str) and
                    sha256(rawtext.encode()).hexdigest()==p.get("raw_sha256"),
                    "TRACE_RAW_TAMPERED")
            code,status,strict=runner.parse(rawtext)
            require(code==p.get("code") and status==p.get("parse_status") and
                    strict==p.get("original_parse_status"),
                    "TRACE_CODE_OR_FORMAT_TAMPERED")
            recomputed=runner.grade_cases(code,task["development_cases"])
            require(recomputed==p.get("development"),"TRACE_DEV_RESULTS_TAMPERED")
            tag=p.get("tag")
            if tag=="train:"+task["id"]+":first":
                require(task["id"] not in initials and
                        p.get("previous_best_correct")==-1 and
                        p.get("accepted_to_best") is True,
                        "INVALID_INITIAL_ATTEMPT")
                initials[task["id"]]=recomputed["correct"]
                current[task["id"]]={"score":recomputed["correct"],
                                      "dev":recomputed,"raw_sha256":p["raw_sha256"]}
            else:
                require(selection is not None and tag==
                        "train:"+selection+":repair"+str(repaired+1) and
                        pending is not None and
                        pending["task_id"]==selection and
                        pending["attempt"]==repaired+1,
                        "REPAIR_WITHOUT_FEEDBACK")
                before=current[selection]["score"]
                better=code is not None and recomputed["correct"]>before
                require(p.get("accepted_to_best") is better and
                        p.get("previous_best_correct")==before,
                        "FALSE_ACCEPT_OR_ROLLBACK")
                if better:
                    current[selection]={"score":recomputed["correct"],
                                        "dev":recomputed,"raw_sha256":p["raw_sha256"]}
                repaired+=1
                pending=None
        elif kind=="SELF_SELECTED_TASK":
            require(selection is None and len(initials)==2 and
                    set(initials)==set(by_id),"INCOMPLETE_SELECTION")
            expected=min(initials,key=lambda k:(initials[k],k))
            require(p.get("selected_id")==expected and
                    p.get("policy")=="LOWEST_INITIAL_DEVELOPMENT_SCORE",
                    "CHERRY_PICKED_TASK")
            selection=expected
        elif kind=="FEEDBACK_OFFERED":
            require(selection is not None and pending is None and
                    repaired<runner.MAX_REPAIRS and
                    current[selection]["score"]<10 and
                    p.get("task_id")==selection and
                    p.get("attempt")==repaired+1,
                    "UNAUTHORIZED_FEEDBACK")
            expected=runner.feedback_for(current[selection]["dev"])
            require(p.get("shown_failed_cases")==expected and
                    p.get("shown_case_count")==len(expected) and
                    p.get("prior_raw_sha256")==current[selection]["raw_sha256"] and
                    p.get("selection_rule")=="3_MINIMAL_DEVELOPMENT_FAILURES_ONLY",
                    "FEEDBACK_ORACLE_LEAK_OR_TAMPER")
            pending=p
        elif kind=="LESSON_CANDIDATE":
            require(selection is not None and lesson is None and
                    current[selection]["score"]==10 and
                    initials[selection]<10 and
                    p.get("task_id")==selection,"LESSON_WITHOUT_MASTERY")
            txt=p.get("raw")
            require(isinstance(txt,str) and
                    sha256(txt.encode()).hexdigest()==p.get("raw_sha256"),
                    "LESSON_RAW_TAMPERED")
            parsed=runner.SAFE.parse_json(txt)
            found=parsed.get("lesson") if parsed else None
            admitted=(found.strip() if isinstance(found,str)
                      and 8<=len(found.strip())<=240 else "")
            require(p.get("lesson")==admitted and
                    p.get("admitted") is bool(admitted) and
                    p.get("support_correct")==10 and
                    p.get("support_total")==10 and
                    p.get("support_initial")==initials[selection],
                    "FALSE_LESSON_ADMISSION")
            lesson=admitted
        elif kind=="PRACTICE_DECISION":
            require(selection is not None and decision is None and
                    pending is None and p.get("task_id")==selection,
                    "INVALID_PRACTICE_DECISION")
            best=current[selection]
            require(p.get("initial_score")==initials[selection] and
                    p.get("best_score")==best["score"] and
                    p.get("best_raw_sha256")==best["raw_sha256"] and
                    p.get("mastered") is (initials[selection]<10 and best["score"]==10) and
                    p.get("memory_admitted") is bool(lesson) and
                    p.get("memory")==(" " if False else (lesson or "")) and
                    p.get("gradients")==0,
                    "PRACTICE_DECISION_TAMPERED")
            decision=p
        elif kind=="RUN_COMPLETE":
            require(e is trace[-1] and decision is not None and
                    p.get("sealed_gold_used") is False,
                    "RUN_COMPLETION_TAMPERED")
        else:
            raise ValueError("UNKNOWN_TRACE_EVENT")
    require(decision is not None and selection is not None and pending is None and
            len(initials)==2 and repaired<=runner.MAX_REPAIRS,
            "INCOMPLETE_TRAINING_TRACE")
    view=raw.get("practice",{})
    require(view.get("selected_id")==selection and
            view.get("initial_score")==initials[selection] and
            view.get("best_score")==current[selection]["score"] and
            view.get("best_source_sha256")==current[selection]["raw_sha256"] and
            view.get("admitted_memory")==(" " if False else (lesson or "")) and
            view.get("mastered") is (initials[selection]<10 and current[selection]["score"]==10) and
            view.get("hidden_gold_used") is False and
            view.get("gradient_updates")==0 and
            view.get("max_repairs")==runner.MAX_REPAIRS,
            "PRACTICE_SUMMARY_MISMATCH")
    return {"selection":selection,"initial_score":initials[selection],
            "best_score":current[selection]["score"],"repairs":repaired,
            "trace_events":len(trace),"memory_admitted":bool(lesson)}


def score_arm(rows,gold):
    scored=[]
    for row,item in zip(rows,gold):
        require(row.get("id")==item["id"] and
                row.get("family")==item["family"],"EVALUATION_TASK_MISALIGNED")
        text=row.get("raw")
        require(isinstance(text,str) and
                sha256(text.encode()).hexdigest()==row.get("raw_sha256"),
                "MODEL_OUTPUT_CHANGED")
        code,status,strict=runner.parse(text)
        require(row.get("code")==code and
                row.get("parse_status")==status and
                row.get("original_parse_status")==strict,
                "MODEL_OUTPUT_REINTERPRETED")
        result=runner.grade_cases(code,item["hidden_cases"])
        oldstrict,_=runner.old.inspect_code(text)
        strict_result=runner.grade_cases(oldstrict,item["hidden_cases"])
        scored.append({"id":item["id"],"family":item["family"],
                       "exact":result["correct"],"total":result["total"],
                       "full":result["correct"]==result["total"],
                       "strict_exact":strict_result["correct"],
                       "safe":code is not None,
                       "silent_error":code is not None and result["correct"]<result["total"],
                       "format_recovered":status=="ESCAPED_LINE_NORMALIZED",
                       "raw_sha256":row["raw_sha256"]})
    return {"exact":sum(x["exact"] for x in scored),
            "total":sum(x["total"] for x in scored),
            "full":sum(x["full"] for x in scored),
            "strict_exact":sum(x["strict_exact"] for x in scored),
            "safe":sum(x["safe"] for x in scored),
            "silent_errors":sum(x["silent_error"] for x in scored),
            "format_recovered":sum(x["format_recovered"] for x in scored),
            "rows":scored}


def grade(report):
    require(report.get("schema")==runner.SCHEMA and
            report.get("status")=="GENERATED_NOT_SCORED" and
            report.get("frozen_git_blobs")==runner.PINS,
            "UNTRUSTED_RUN")
    require(report.get("C")=={"status":"TRAINING_NOT_AUTHORIZED",
                              "weight_updates":0} and
            report.get("sealed_test_loaded_during_generation") is False and
            report.get("paid_apis")==0 and report.get("main_modified") is False,
            "ILLEGAL_AUTONOMOUS_SIDE_EFFECT")
    require(report.get("generation_cap_per_eval")==runner.GEN_CAP and
            report.get("evaluation_calls_each")==3 and
            report.get("max_repairs")==runner.MAX_REPAIRS,
            "UNFAIR_OR_EXCESSIVE_BUDGET")
    training=validate_training_trace(report)
    _,public=runner.public_data()
    # **Only this scorer** opens the NEW sealed cohort.
    sealed=runner.frozen("EVAL_SEALED_FROZEN.json")
    require(sealed.get("schema")=="OMEGA_SELF_TEACH04_EVAL_SEALED_V1",
            "SEALED_SCHEMA")
    gold=sealed["holdout"]
    require(len(gold)==len(public)==3,"INVALID_NEW_HOLDOUT")
    for p,h in zip(public,gold):
        require(p["id"]==h["id"] and p["family"]==h["family"] and
                len(h["hidden_cases"])==6,
                "HIDDEN_TEST_TASK_MISMATCH")
        require(not {x["input"] for x in p["public_examples"]}&
                {x["input"] for x in h["hidden_cases"]},
                "HIDDEN_PUBLIC_OVERLAP")
    note=report["practice"]["admitted_memory"]
    if note:
        require(report.get("B_alias_of_P_without_memory") is False and
                report.get("B_actual_model_calls")==3,
                "INVALID_MEMORY_B_EXECUTION_COUNT")
    else:
        require(report.get("B_alias_of_P_without_memory") is True and
                report.get("B_actual_model_calls")==0,
                "FALSE_INDEPENDENT_B_REPLAY")
        for p,b in zip(report.get("P",[]),report.get("B",[])):
            require({k:v for k,v in b.items() if k!="tag"}==
                    {k:v for k,v in p.items() if k!="tag"} and
                    b.get("tag")=="B:"+p.get("id",""),
                    "NO_MEMORY_B_MUST_EQUAL_P")
    arms={}
    for name in ("A","P","B"):
        rows=report.get(name,[])
        require(isinstance(rows,list) and len(rows)==3,
                "INCOMPLETE_EVALUATION_ARM")
        for row,task in zip(rows,public):
            spec_note=(None if name=="A" else
                       runner.NEUTRAL if name=="P" or not note else note)
            prompt=runner.task_prompt(task,spec_note)
            require(row.get("prompt_sha256")==sha256(prompt.encode()).hexdigest()
                    and row.get("tag")==name+":"+task["id"]
                    and row.get("note")==spec_note,
                    "EVALUATION_PROMPT_TAMPERED")
        arms[name]=score_arm(rows,gold)
    regression=sum((a["full"] or p["full"]) and not b["full"]
                   for a,p,b in zip(arms["A"]["rows"],
                                    arms["P"]["rows"],arms["B"]["rows"]))
    deltaA=arms["B"]["exact"]-arms["A"]["exact"]
    deltaP=arms["B"]["exact"]-arms["P"]["exact"]
    exploratory=(bool(note) and deltaA>0 and deltaP>0 and regression==0)
    return {"schema":SCHEMA,
            "status":("EXPLORATORY_LESSON_TRANSFER_ONLY" if exploratory else
                      "NO_AUTONOMOUS_LEARNING_GAIN_DEMONSTRATED"),
            **arms,"C":report["C"],
            "training":training,
            "delta_B_minus_A":deltaA,"delta_B_minus_P":deltaP,
            "baseline_full_tasks_regressed":regression,
            "total_llm_calls":report.get("total_llm_calls"),
            "duration_seconds":report.get("duration_seconds"),
            "new_blind_holdout_now_consumed":True,
            "causal_generalization_proven":False,
            "new_model_parameters_updated":False,
            "B_alias_of_P_without_memory":report["B_alias_of_P_without_memory"],
            "B_actual_model_calls":report["B_actual_model_calls"]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    raw=json.loads(args.raw.read_text())
    result=grade(raw)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("SELF_TEACH04_SCORE",result["status"],
          "A",result["A"]["exact"],"P",result["P"]["exact"],
          "B",result["B"]["exact"],"of 18",
          "train",result["training"]["initial_score"],"to",
          result["training"]["best_score"],flush=True)

if __name__=="__main__":
    main()
