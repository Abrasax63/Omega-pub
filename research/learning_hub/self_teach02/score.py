"""Score immutable SELF-TEACH02 model outputs only AFTER A,P,B were saved.

No model inference; old 242 cases are never loaded here. The new sealed
cohort becomes consumed after the first real score, irrespective of outcome.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runner

SCHEMA="OMEGA_SELF_TEACH02_SCORE_V1"


def check(ok,code):
    if not ok:
        raise ValueError(code)


def score_arm(rows,gold):
    out=[]
    for row,item in zip(rows,gold):
        check(row.get("id")==item["id"] and
              row.get("family")==item["family"],"TASK_MISALIGNED")
        raw=row.get("raw")
        check(isinstance(raw,str) and
              sha256(raw.encode()).hexdigest()==row.get("sha256_raw"),
              "RAW_MODEL_OUTPUT_TAMPERED")
        code,status,strict=runner.parse_and_guard(raw)
        check(row.get("code")==code and row.get("code_status")==status and
              row.get("original_strict_status")==strict,
              "PARSER_REINTERPRETED_AFTER_RUN")
        scored=runner.score_dev(code,item["hidden_cases"])
        strict_code,strict_status=runner.old_pilot.inspect_code(raw)
        strict_scored=runner.score_dev(strict_code,item["hidden_cases"])
        out.append({
            "id":item["id"],"family":item["family"],
            "exact":scored["correct"],"total":scored["total"],
            "strict_exact":strict_scored["correct"],
            "fully_correct":scored["correct"]==scored["total"],
            "strict_fully_correct":strict_scored["correct"]==scored["total"],
            "safe":code is not None,
            "silent_functional_error":code is not None and
                                        scored["correct"]<scored["total"],
            "format_only_recovered":status=="FORMAT_RECOVERED_POST_HOC",
            "raw_sha256":row["sha256_raw"],
        })
    return {
        "exact":sum(r["exact"] for r in out),
        "strict_exact":sum(r["strict_exact"] for r in out),
        "total":sum(r["total"] for r in out),
        "fully_correct":sum(r["fully_correct"] for r in out),
        "strict_fully_correct":sum(r["strict_fully_correct"] for r in out),
        "safe_programs":sum(r["safe"] for r in out),
        "abstentions":sum(not r["safe"] for r in out),
        "silent_functional_errors":sum(r["silent_functional_error"] for r in out),
        "format_only_recovered":sum(r["format_only_recovered"] for r in out),
        "rows":out
    }


def grade(raw):
    check(raw.get("schema")==runner.SCHEMA and
          raw.get("status")=="GENERATED_NOT_SCORED","RAW_REPORT_INVALID")
    check(raw.get("frozen_git_blobs")==runner.PINS,"FROZEN_PIN_MISMATCH")
    check(raw.get("per_task_generation_cap")==runner.GEN_CAP and
          raw.get("evaluation_calls_each")==3,"GENERATION_BUDGET_MISMATCH")
    check(raw.get("C")=={"status":"TRAINING_NOT_AUTHORIZED",
                         "new_weight_updates":0},"ILLEGAL_TRAINING")
    check(raw.get("sealed_gold_imported_during_generation") is False and
          raw.get("paid_api_calls")==0 and
          raw.get("main_modified") is False,"ILLEGAL_SIDE_EFFECT")
    practice=raw.get("practice",{})
    note=practice.get("admitted_memory")
    check(isinstance(note,str) and len(note)<=240,"INVALID_MEMORY")
    check(practice.get("hidden_evaluation_used_in_training") is False and
          practice.get("gradient_updates")==0,"GOLD_OR_WEIGHTS_USED")
    check(practice.get("best_dev_total")==8 and
          0<=practice.get("initial_selected_score",-1)<=8 and
          0<=practice.get("best_dev_correct",-1)<=8,"TRAINING_FEEDBACK_INVALID")
    init=practice.get("initial_scores",[])
    train,public=runner.public_cohorts()
    check(len(init)==2 and [x["id"] for x in init]==
          [x["id"] for x in train],"TRAINING_TASKS_MISALIGNED")
    expected_selected=min(init,key=lambda x:(x["correct"],x["id"]))["id"]
    check(practice.get("self_selected_task")==expected_selected,
          "CHERRY_PICKED_TRAINING_TASK")
    check(len(practice.get("revisions",[]))<=runner.MAX_REVISIONS,
          "TRAINING_REVISIONS_EXCEEDED")
    if note:
        check(practice.get("mastered_practice") is True and
              practice["best_dev_correct"]==8 and
              practice["best_dev_correct"]>practice["initial_selected_score"] and
              practice.get("memory_status")=="ADMITTED_LIMITED_PRACTICE_ONLY",
              "UNVERIFIED_MEMORY_ADMITTED")
    else:
        check(practice.get("memory_status")=="NO_VERIFIED_MEMORY",
              "MEMORY_POLICY_INCONSISTENT")
    # Public and train remain disjoint. The only new gold access is here:
    sealed=runner.read_frozen("EVAL_SEALED_FROZEN.json")
    check(sealed.get("schema")=="OMEGA_SELF_TEACH02_EVAL_SEALED_V1",
          "SEALED_SCHEMA")
    gold=sealed["holdout"]
    check(len(public)==len(gold)==3,"MISSING_TEST_TASK")
    for p,g in zip(public,gold):
        check(p["id"]==g["id"] and p["family"]==g["family"] and
              len(g["hidden_cases"])==6,"HIDDEN_TASK_MISMATCH")
        check(not {x["input"] for x in p["public_examples"]}&
              {x["input"] for x in g["hidden_cases"]},"PUBLIC_HIDDEN_OVERLAP")
    scores={}
    for arm in ("A","P","B"):
        rows=raw.get(arm,[])
        check(isinstance(rows,list) and len(rows)==3,"MISSING_ARM:"+arm)
        for row,task in zip(rows,public):
            note_for_task=(None if arm=="A" else
                           runner.NEUTRAL if arm=="P" or not note else note)
            expected=runner.task_prompt(task,note_for_task)
            check(row.get("prompt_sha256")==sha256(expected.encode()).hexdigest(),
                  "PROMPT_CONTENT_CHANGED:"+arm)
            check(row.get("call_tag")==arm+":"+task["id"] and
                  row.get("note_used") is bool(note_for_task),
                  "PROMPT_PROVENANCE_CHANGED:"+arm)
        scores[arm]=score_arm(rows,gold)
    regressions=sum((a["fully_correct"] or p["fully_correct"]) and
                    not b["fully_correct"]
                    for a,p,b in zip(scores["A"]["rows"],
                                     scores["P"]["rows"],scores["B"]["rows"]))
    delta_a=scores["B"]["exact"]-scores["A"]["exact"]
    delta_p=scores["B"]["exact"]-scores["P"]["exact"]
    established=(bool(note) and delta_a>0 and delta_p>0 and regressions==0)
    # No causal generalization claim, even with better B score.
    return {
        "schema":SCHEMA,
        "status":("EXPLORATORY_VERIFIED_LESSON_TRANSFER" if established
                  else "NO_AUTONOMOUS_TRANSFER_GAIN_DEMONSTRATED"),
        "A":scores["A"],"P":scores["P"],"B":scores["B"],
        "C":raw["C"],
        "memory_admitted":bool(note),
        "lesson_origin_training_task":practice["self_selected_task"],
        "delta_B_minus_A":delta_a,
        "delta_B_minus_prompt_control":delta_p,
        "fully_correct_baseline_tasks_regressed":regressions,
        "number_of_model_calls":raw["total_llm_calls"],
        "inference_wall_seconds":raw["duration_s"],
        "normalizer_version":"242-guarded-escaped-line-only",
        "new_model_weight_updates":0,
        "new_scientific_theorems":0,
        "causal_generalization_proven":False,
        "new_fresh_holdout_now_consumed":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=grade(json.loads(args.raw.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print("SELF_TEACH02_GRADE",report["status"],"A",report["A"]["exact"],
          "P",report["P"]["exact"],"B",report["B"]["exact"],
          "of",report["B"]["total"],flush=True)

if __name__=="__main__":
    main()
