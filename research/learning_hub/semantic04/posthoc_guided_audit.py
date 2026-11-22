"""Post-hoc diagnosis on consumed SEMANTIC04 cohort. ZERO new model calls.

This does not generate new independent learning evidence. It compares the
original 11/12 one-edit search with an all-occurrence, ambiguity-aware
candidate search. Hidden cases are touched only in this diagnostic grader,
never in execution_guided.resolve() or candidate selection.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

import core
import execution_guided as eg

def evaluate(old_report):
    if (old_report.get("protocol")!=core.PROTOCOL
            or old_report.get("source_adapter_run")!=core.SOURCE_RUN
            or old_report.get("holdout_git_blob")!=core.FROZEN_BLOB):
        raise ValueError("WRONG_ORIGINAL_RUN_OR_FROZEN_HOLDOUT")
    rows=core.frozen_cases()
    original=old_report["results"]
    for arm in ("base","lora","symbolic"):
        if len(original.get(arm,[]))!=12:
            raise ValueError("WRONG_ORIGINAL_REPORT_COUNTS")

    record=[]
    for i,row in enumerate(rows):
        old_sym=original["symbolic"][i]
        model_raw=original["lora"][i]["raw"]
        if (old_sym["id"]!=row["id"] or
                original["lora"][i]["id"]!=row["id"]):
            raise ValueError("REPORT_ID_ALIGNMENT_FAILURE")
        matches,trials=eg.collect_agreeing(
            row["broken_source"],row["public_examples"])
        # This scoring is post-hoc: never pass these hidden inputs to
        # the candidate generator or to the public selector.
        correct_count=sum(core.grade(x["code"],row["hidden_cases"])
                          ["all_correct"] for x in matches)
        decision=eg.resolve(row["broken_source"],
                            row["public_examples"],model_text=model_raw)
        record.append({
            "id":row["id"],
            "old_symbolic_exact":old_sym["strict"]["all_correct"],
            "public_matching_candidates":len(matches),
            "old_symbolic_attempts":old_sym["attempts"],
            "new_candidate_search_trials":trials,
            "candidate_recall_any_exact_on_consumed_cases":bool(correct_count),
            "new_true_program_candidates_within_public_matching_set":correct_count,
            "unique_public_solution_found":len(matches)==1,
            "safe_resolution_status":decision["status"],
            "new_oracle_probe_required":decision["status"]=="NEEDS_ORACLE_RESPONSE",
            "new_model_calls":0,"old_hidden_inputs_not_used_in_selection":True
        })
    score={
        "protocol":"OMEGA_EXECUTION_GUIDED_POSTHOC_01",
        "status":"POSTHOC_CONSUMED_HOLDOUT_NOT_GENERALIZATION",
        "prior_run":45074827572,
        "prior_frozen_holdout_blob":core.FROZEN_BLOB,
        "previous_symbolic_exact":sum(r["old_symbolic_exact"] for r in record),
        "new_candidate_recall_any_exact":sum(
            r["candidate_recall_any_exact_on_consumed_cases"] for r in record),
        "strictly_selected_unique_correct":sum(
            r["unique_public_solution_found"] and
            r["candidate_recall_any_exact_on_consumed_cases"] for r in record),
        "ambiguous_or_abstained":sum(
            r["safe_resolution_status"]!="UNIQUE_PUBLIC_CANDIDATE_NEEDS_INDEPENDENT_TEST"
            for r in record),
        "new_oracle_probes_needed":sum(r["new_oracle_probe_required"] for r in record),
        "new_model_calls":0,
        "new_training_steps":0,
        "independent_new_benchmark":False,
        "candidate_recall_not_actual_solver_accuracy":True,
        "do_not_compare_to_prior_as_fresh_evidence":True,
        "rows":record,
    }
    return score


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--old-report",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    raw=args.old_report.read_bytes()
    if len(raw)>1500000:
        raise ValueError("OLD_REPORT_TOO_LARGE")
    d=json.loads(raw)
    result=evaluate(d)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print("GUIDED_POSTHOC",json.dumps({
        k:v for k,v in result.items() if isinstance(v,(str,int,bool))
    },ensure_ascii=False))


if __name__=="__main__":
    main()
