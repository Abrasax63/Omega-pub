#!/usr/bin/env python3
"""Offline independent scoring AFTER both model generation stages are sealed.

This is the only module in TRANSFER27 to load the 192 heldout cases or
formula answer key. It cannot call any language model, change prompts or adapt
weights. Failed formulas yield exact counterexamples rather than promotion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback

from data_guard import (
    ARMS,ADAPTER_SHA,load_prompts,load_holdout,read_pinned,
    mod_orbit_direct,mod_gcd_independent,
    overlap_direct,overlap_limits_independent,
)
from infer import FIRST_ST,SECOND_ST,stable_first_digest,sha256_bytes
from logic import check_on_cases

def _check_record(rows,kind):
    prompts=load_prompts()
    lookup={(r["id"],r["arm"]):r for r in rows}
    if len(lookup)!=48 or len(rows)!=48:
        raise ValueError("INVALID_"+kind+"_RECORD_CARDINALITY")
    for p in prompts:
        for arm in ARMS:
            r=lookup.get((p["id"],arm))
            if r is None or r.get("domain")!=p["domain"]:
                raise ValueError("INVALID_"+kind+"_RECORD_CROSSREFERENCE")
            raw=r["raw"]
            if not isinstance(raw,str) or hashlib.sha256(
                raw.encode("utf-8")).hexdigest()!=r["raw_sha256"]:
                raise ValueError("RAW_INFERENCE_NOT_BYTE_FOR_BYTE")
            if type(r["input_tokens"])!=int or type(r["generated_tokens"])!=int:
                raise ValueError("INVALID_TOKEN_COUNTS")
            if r["generated_tokens"]>96 or r["input_tokens"]>800:
                raise ValueError("DECODE_BUDGET_EXCEEDED")
            if r["trained_adapter_enabled"]!=(arm!="A_BASE_NEUTRAL"):
                raise ValueError("UNFAIR_BASELINE_WEIGHTS")
    return lookup


def _score_raw(row,domain,cases):
    if domain=="unsupported":
        valid=(row["raw"]=="ABSTAIN")
        return {
            "status":"CORRECT_OOD_ABSTENTION" if valid else "UNSUPPORTED_NONABSTENTION",
            "accepted_on_holdout":valid,
            "finite_checked":0,"finite_correct":0,"finite_wrong":0,
            "counterexample":None,
            "unsafe_or_wrong_unverified_claim":not valid,
        }
    r=check_on_cases(row["raw"],domain,cases,max_witnesses=1)
    accepted=(r["status"]=="MATCHES_FINITE_CASES" and r["checked"]==len(cases))
    return {
        "status":r["status"],
        "accepted_on_holdout":accepted,
        "finite_checked":r["checked"],"finite_correct":r["correct"],
        "finite_wrong":r["wrong"],
        "counterexample":r.get("counterexample"),
        "error":r.get("error"),
        "unsafe_or_wrong_unverified_claim":r["status"]=="FALSIFIED",
    }


def verify_reference(cases):
    x=cases["modular"]; y=cases["intervals"]
    a=sum(mod_orbit_direct(c)==c["reachable"] for c in x)
    d=sum(mod_gcd_independent(c)==c["reachable"] for c in x)
    b=sum(overlap_direct(c)==c["overlap"] for c in y)
    e=sum(overlap_limits_independent(c)==c["overlap"] for c in y)
    if (a,d,b,e)!=(96,96,96,96):
        raise AssertionError("INDEPENDENT_REFERENCE_DISAGREEMENT")
    return {
        "reference_A_modular_direct":a,
        "reference_D_modular_gcd":d,
        "reference_A_intervals_enumeration":b,
        "reference_D_intervals_bounds":e,
        "strong_D_correct_cases":d+e,
        "strong_D_total_cases":192,
    }


def score(first,second):
    if (first.get("status")!=FIRST_ST or second.get("status")!=SECOND_ST or
        first.get("generation_calls")!=48 or second.get("generation_calls")!=48):
        raise ValueError("GENERATION_PIPELINE_INCOMPLETE")
    if first.get("train26_adapter_sha256")!=ADAPTER_SHA or (
        second.get("train26_adapter_sha256")!=ADAPTER_SHA
    ):
        raise ValueError("SAVED_ADAPTER_HASH_DIFFERENT")
    if first.get("calibration_loaded") is not False or (
        first.get("holdout_loaded") is not False or second.get("holdout_loaded") is not False
    ):
        raise ValueError("HOLDOUT_IN_PRE_GRADING_STAGE")
    if stable_first_digest(first["ideas"])!=first["stable_first_ideas_sha256"]:
        raise ValueError("FIRST_IDEA_DIGEST_DRIFT")
    if second["first_stage_sha256"]!=first["stable_first_ideas_sha256"]:
        raise ValueError("FINAL_STUDY_NOT_SAME_FIRST_IDEAS")
    old=_check_record(first["ideas"],"FIRST")
    final=_check_record(second["finals"],"FINAL")
    for key,row in final.items():
        if row["first_sha256"]!=old[key]["raw_sha256"]:
            raise ValueError("FINAL_WRONG_FIRST_IDEA")
        if row["feedback_status"]=="NEUTRAL_CONTROL" and key[1]=="C_LORA_VERIFIER" and (
            row["domain"]!="unsupported"
        ):
            raise ValueError("VERIFIER_ARM_WITHOUT_CALIBRATION")
        if row["feedback_status"]!="NEUTRAL_CONTROL" and key[1]!="C_LORA_VERIFIER":
            raise ValueError("CONTROL_ARM_WITH_ORACLE")
        if row["verifier_cases_checked"]>24:
            raise ValueError("VERIFIER_SEES_BEYOND_CALIBRATION")
    prompts=load_prompts()
    # First use of hidden validation values occurs AFTER all 96 calls were made.
    cases=load_holdout()
    reference=verify_reference(cases)
    gold=read_pinned("ANSWER_KEY_EVAL_ONLY.json")
    if gold["learning_corpus_contains_these_targets"]:
        raise ValueError("NOT_A_TRANSFER_EVALUATION")
    details=[]
    stats={}
    for arm in ARMS:
        report={"arm":arm,"total_prompts":16}
        for phase,lookup in (("first",old),("final",final)):
            entries=[]
            for p in prompts:
                row=lookup[(p["id"],arm)]
                cohort=(cases["modular"] if p["domain"]=="modular_orbit" else
                        cases["intervals"] if p["domain"]=="closed_interval_overlap" else [])
                assessment=_score_raw(row,p["domain"],cohort)
                if phase=="final":
                    details.append({
                        "id":p["id"],"domain":p["domain"],"arm":arm,
                        "phase":phase,"raw":row["raw"],"raw_sha256":row["raw_sha256"],
                        "input_tokens":row["input_tokens"],
                        "generated_tokens":row["generated_tokens"],
                        "generation_wall_seconds":row["wall_seconds"],
                        "feedback_status":row["feedback_status"],
                        "verifier_calibration_summary":row["verifier_calibration_summary"],
                        "assessment":assessment,
                    })
                entries.append((p,assessment,row))
            verified=sum(x["accepted_on_holdout"] for _,x,_ in entries)
            valid_math=sum(p["domain"]!="unsupported" and x["accepted_on_holdout"]
                           for p,x,_ in entries)
            ood=sum(p["domain"]=="unsupported" and x["accepted_on_holdout"]
                    for p,x,_ in entries)
            falsified=sum(x["status"]=="FALSIFIED" for _,x,_ in entries)
            parses=sum(x["status"] in ("PARSE_REJECTED","EVALUATION_REJECTED")
                       for _,x,_ in entries)
            abstained_math=sum(p["domain"]!="unsupported" and x["status"]=="ABSTAIN"
                               for p,x,_ in entries)
            wrong=sum(x["finite_wrong"] for _,x,_ in entries)
            totals={
                "verified_tasks_total_of_16":verified,
                "verified_math_representations_of_12":valid_math,
                "ood_correct_abstentions_of_4":ood,
                "falsified_candidates":falsified,
                "rejected_invalid_expressions":parses,
                "math_abstentions":abstained_math,
                "heldout_wrong_boolean_verdicts":wrong,
                "source_outputs_sha256":sha256_bytes(json.dumps(
                    [(p["id"],r["raw"]) for p,_,r in entries],
                    ensure_ascii=False).encode("utf-8")),
                "input_tokens_actual":sum(r["input_tokens"] for _,_,r in entries),
                "generated_tokens_actual":sum(r["generated_tokens"] for _,_,r in entries),
                "model_wall_seconds":round(sum(r["wall_seconds"] for _,_,r in entries),3),
                "verifier_calibration_cases_checked":sum(
                    r.get("verifier_cases_checked",0) for _,_,r in entries),
                "verifier_calibration_wall_seconds":round(sum(
                    r.get("verifier_wall_seconds",0) for _,_,r in entries),5),
            }
            report[phase]=totals
        stats[arm]=report

    A=stats["A_BASE_NEUTRAL"]["final"]["verified_math_representations_of_12"]
    B=stats["B_LORA_NEUTRAL"]["final"]["verified_math_representations_of_12"]
    C=stats["C_LORA_VERIFIER"]["final"]["verified_math_representations_of_12"]
    result={
        "experiment":"OMEGA_TRANSFER27_UNSEEN_MATH_WITH_REAL_SAVED_LORA",
        "status":"SCORED_FROZEN_ALL_THREE_ARMS",
        "source_training_run":44512647677,
        "actual_model_call_count":96,
        "calls_per_arm":32,
        "max_generated_tokens_per_call":96,
        "budget_call_count_and_output_caps_equal":True,
        "budget_total_compute_equal":False,
        "train26_adapter_sha256":ADAPTER_SHA,
        "first_ideas_sha256":first["stable_first_ideas_sha256"],
        "task_count":16,"novel_to_train26_math_task_count":12,
        "heldout_cases":192,
        "calibration_cases_only_used_by_C":48,
        "heldout_never_used_for_model_prompts":True,
        "model_weight_updates_during_transfer_experiment":0,
        "problem_families_not_present_in_320_examples":True,
        "pretraining_contamination_not_excluded":True,
        "grammar_lists_gcd_min_max":True,
        "no_new_theorem_or_creativity_claim":True,
        "strong_reference":reference,
        "arms":stats,
        "status_verdicts":{
            "trained_vs_base":"TRANSFER_OBSERVED_BOUNDED" if B>A else "NO_TRANSFER_GAIN",
            "feedback_vs_trained":"VERIFIER_FEEDBACK_GAIN_BOUNDED" if C>B else "NO_VERIFIER_GAIN",
            "feedback_vs_base":"C_BETTER_THAN_A" if C>A else "NO_C_OVER_A_GAIN",
            "A_verified_math":A,"B_verified_math":B,"C_verified_math":C,
        },
        "raw_final_details":details,
        "model_auto_certifications":0,
        "paid_api_calls":0,
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--first",type=Path,required=True)
    parser.add_argument("--second",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        result=score(
            json.loads(args.first.read_text(encoding="utf-8")),
            json.loads(args.second.read_text(encoding="utf-8")),
        )
    except Exception:
        result={
            "status":"SCORE_FAILED_INVALID_PROVENANCE_OR_INFRA",
            "error":traceback.format_exc(),
            "model_auto_certifications":0,
        }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print("TRANSFER27_GRADING",result["status"],flush=True)
    if result["status"]=="SCORED_FROZEN_ALL_THREE_ARMS":
        print("ARM_RESULTS",[(a,
              result["arms"][a]["first"]["verified_math_representations_of_12"],
              result["arms"][a]["final"]["verified_math_representations_of_12"],
              result["arms"][a]["final"]["ood_correct_abstentions_of_4"])
              for a in ARMS],flush=True)
        print("VERDICTS",result["status_verdicts"],flush=True)
    else:
        raise SystemExit(1)


if __name__=="__main__":
    main()
