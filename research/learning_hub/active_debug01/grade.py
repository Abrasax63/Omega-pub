"""Trust boundary: score *after* all public-only candidates and all model calls.

The model runner must finish and archive inference.json before this script is
invoked. Hidden test inputs and teacher reference code remain here; never
incorporated into a prompt, a candidate mutation selector, or gradient data.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from hashlib import sha256
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"semantic04"))
import core
import contract

ARMS=("initial","direct2","feedback2","symbolic","guarded_hybrid")

def grade(code,examples):
    if code is None:
        outputs=[{"error":"ABSTAINED_OR_REJECTED_CODE"} for _ in examples]
    else:
        outputs=core.sandbox.execute_student(code,[x["input"] for x in examples])
    details=[{"input":x["input"],"expected":x["output"],"actual":got,
              "correct":got.get("value")==x["output"]}
             for x,got in zip(examples,outputs)]
    correct=sum(x["correct"] for x in details)
    errors=sum("error" in x["actual"] for x in details)
    return {"correct_cases":correct,"total_cases":len(examples),
            "all_correct":correct==len(examples),
            "runtime_errors":errors,
            "silent_wrong_values":sum(not x["correct"] and
                                      "value" in x["actual"] for x in details),
            "details":details}

def run(input_path,output_path):
    raw=Path(input_path).read_bytes()
    if len(raw)>250000:
        raise ValueError("INFERENCE_REPORT_TOO_LARGE")
    record=json.loads(raw)
    if (record.get("protocol")!="OMEGA_ACTIVE_DEBUG01_INFERENCE"
            or record.get("status")!="GENERATION_AND_PUBLIC_SELECTION_COMPLETE_NO_HIDDEN_SCORING"
            or record.get("frozen_git_blob")!=contract.FROZEN_BLOB
            or record.get("model")!=contract.MODEL
            or record.get("model_sha256")!=contract.MODEL_SHA256
            or record.get("max_model_calls")!=contract.MAX_MODEL_CALLS
            or len(record.get("calls",[]))!=contract.MAX_MODEL_CALLS
            or record.get("hidden_tests_sent_to_model") is not False
            or record.get("model_weights_modified") is not False):
        raise ValueError("UNVERIFIED_OR_PARTIAL_INFERENCE_REPORT")
    reference=contract.evaluator_view()
    expected_ids={x["id"] for x in reference}
    if set(record["tasks"])!=expected_ids:
        raise ValueError("WRONG_INFERENCE_IDS")
    details={key:[] for key in ARMS}
    for task in reference:
        ident=task["id"]
        record_item=record["tasks"][ident]
        for arm in ARMS:
            c=record_item["candidates"][arm]
            code=c.get("code")
            if code is not None:
                core.sandbox.validate_program(code)
            score=grade(code,task["hidden_tests"])
            details[arm].append({
                "id":ident,"family":task["family"],
                "candidate_sha256":sha256(code.encode()).hexdigest() if code else None,
                "candidate_admitted_by_ast":code is not None,
                "public_status":c.get("status",c.get("code_status")),
                "public_tests_correct":c.get("public_feedback",{}).get("correct"),
                "public_candidate_count":c.get("matching_public_count"),
                "candidate_trials":c.get("candidates_examined"),
                "hidden_score":score})
    totals={}
    for arm,rows in details.items():
        totals[arm]={
            "fully_correct_programs":sum(x["hidden_score"]["all_correct"] for x in rows),
            "cases_correct":sum(x["hidden_score"]["correct_cases"] for x in rows),
            "cases_total":sum(x["hidden_score"]["total_cases"] for x in rows),
            "admitted_by_ast":sum(x["candidate_admitted_by_ast"] for x in rows),
            "runtime_errors":sum(x["hidden_score"]["runtime_errors"] for x in rows),
            "silent_wrong_values":sum(x["hidden_score"]["silent_wrong_values"] for x in rows),
            "abstained_or_rejected":sum(not x["candidate_admitted_by_ast"] for x in rows),
            "tasks_total":len(rows)}
    usage={
        "physical_model_calls":len(record["calls"]),
        "call_caps":[x["max_output_tokens"] for x in record["calls"]],
        "output_token_count_reported":sum(x["completion_tokens"] for x in record["calls"]
                                          if isinstance(x["completion_tokens"],int)),
        "output_token_usage_missing":sum(not isinstance(x["completion_tokens"],int)
                                         for x in record["calls"]),
        "prompt_token_count_reported":sum(x["prompt_tokens"] for x in record["calls"]
                                          if isinstance(x["prompt_tokens"],int)),
        "model_elapsed_seconds":round(sum(x["elapsed_seconds"] for x in record["calls"]),3),
        "first_generation_shared":True,
        "model_calls_per_direct_2_arm":2,
        "model_calls_per_feedback_2_arm":2,
        "same_output_cap_per_request":True,
        "same_prompt_tokens_per_arm":False,
        "difference":"Feedback arm receives execution feedback, direct revision does not."
    }
    report={
        "protocol":"OMEGA_ACTIVE_DEBUG01_FINAL",
        "status":"EVALUATED_EXPLORATORY_FROZEN_BENCHMARK_CONSUMED",
        "model":contract.MODEL,"model_sha256":contract.MODEL_SHA256,
        "original_inference_sha256":sha256(raw).hexdigest(),
        "frozen_git_blob":contract.FROZEN_BLOB,
        "no_model_weight_training":True,"paid_api_calls":0,
        "frozen_new_family_count":len(reference),
        "previous_sft_or_semantic_holdouts_reused_as_new":False,
        "hidden_tests_used_to_select_correction":False,
        "heldout_cases_now_consumed":True,
        "general_programming_ability_not_proven":True,
        "initial_shared_across_direct_and_feedback":True,
        "scores":totals,"details":details,"cost":usage,
        "paired_comparison":{
            "feedback2_minus_direct2_exact":
                totals["feedback2"]["fully_correct_programs"]-
                totals["direct2"]["fully_correct_programs"],
            "feedback2_minus_initial_exact":
                totals["feedback2"]["fully_correct_programs"]-
                totals["initial"]["fully_correct_programs"],
            "hybrid_minus_symbolic_exact":
                totals["guarded_hybrid"]["fully_correct_programs"]-
                totals["symbolic"]["fully_correct_programs"],
            "same_holdout_per_arm":True,
            "small_sample_causal_or_generalization_proof":False
        }}
    output_path=Path(output_path)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print("OMEGA_ACTIVE_DEBUG01_SCORES",
        json.dumps({a:{"exact":totals[a]["fully_correct_programs"],
                      "cases":totals[a]["cases_correct"],
                      "valid":totals[a]["admitted_by_ast"]}
                    for a in ARMS},ensure_ascii=False),flush=True)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inference",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.inference,a.output)

if __name__=="__main__":
    main()
