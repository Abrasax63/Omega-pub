"""Conservative 3-case cohort report. Never drop failures or change denominator."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def summarize(results_root:Path)->dict:
    config=json.loads((HERE/"cases.json").read_text(encoding="utf-8"))
    declared=config["cases"]
    rows=[]
    for c in declared:
        path=results_root/("cohort-fixed-"+c["id"])/"oracle.json"
        if not path.is_file():
            rows.append({"case":c["id"],"project":c["project"],
                         "status":"MISSING_CI_ORACLE","eligible":False,
                         "reproduced":False,"scores":None})
            continue
        try:
            report=json.loads(path.read_text(encoding="utf-8"))
            if report["case"]!=c["id"]:
                raise ValueError("CASE_REPORT_ID_MISMATCH")
            eligible=report["eligible_for_primary_metric"]
            rows.append({
              "case":c["id"],"project":c["project"],
              "status":report["status"],
              "eligible":eligible,
              "reproduced":report["reproduction_differential_verified"],
              "scores":report["scores_descriptive_even_when_ineligible"] if eligible else None,
              "descriptive_ranks_unscored":report["scores_descriptive_even_when_ineligible"] if not eligible else None,
              "oracle_unresolved_hunks":len(report["oracle"]["unresolved_hunks"]),
              "profile_seconds":report["runtime_seconds_buggy_profile"],
              "fixed_profile_seconds":report["runtime_seconds_fixed_profile"],
              "shared_called_names_in_fail_and_pass":report["shared_failed_buggy_and_passing_fixed_called_names"],
            })
        except (OSError,ValueError,KeyError,json.JSONDecodeError) as ex:
            rows.append({"case":c["id"],"project":c["project"],
                         "status":"INVALID_ORACLE_REPORT_"+type(ex).__name__,
                         "eligible":False,"reproduced":False,"scores":None})
    eligible=[x for x in rows if x["eligible"]]
    by_arm={}
    for key in ("A_lexical","B_called_only","C_last_call"):
        by_arm[key]={
          "hit_at_10":sum(1 for r in eligible if r["scores"][key]["hit_at_10"]),
          "hit_at_5":sum(1 for r in eligible if r["scores"][key]["hit_at_5"]),
          "best_ranks":[r["scores"][key]["best_rank"] for r in eligible],
        }
    n=len(eligible)
    distinct=len({x["project"] for x in eligible})
    if n<2 or distinct<2:
        status="INSUFFICIENT_REPRODUCERS"
    elif by_arm["C_last_call"]["hit_at_10"]==by_arm["A_lexical"]["hit_at_10"]:
        status="NO_PRIMARY_COHORT_DIFFERENCE_OBSERVED"
    elif by_arm["C_last_call"]["hit_at_10"]>by_arm["A_lexical"]["hit_at_10"]:
        status="DESCRIPTIVE_COHORT_IMPROVEMENT_NOT_PROVEN"
    else:
        status="DESCRIPTIVE_COHORT_REGRESSION_NOT_PROVEN"
    return {
      "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
      "status":status,
      "preregistered_cases":len(declared),
      "cases_with_valid_reproducer_and_full_oracle":n,
      "cases_indeterminate":len(declared)-n,
      "distinct_projects_eligible":distinct,
      "case_results":rows,
      "by_arm_counts_conditional_on_eligible":by_arm,
      "primary_hit_at_10_difference_C_minus_A":(
        by_arm["C_last_call"]["hit_at_10"]-by_arm["A_lexical"]["hit_at_10"]),
      "secondary_hit_at_10_difference_C_minus_B":(
        by_arm["C_last_call"]["hit_at_10"]-by_arm["B_called_only"]["hit_at_10"]),
      "inspection_budget_equal":True,
      "information_and_compute_budget_equal":False,
      "no_case_replacement":True,
      "data_excluded_from_denominator":False,
      "statistical_generalization_demonstrated":False,
      "models_called":0,
      "repairs_generated":0,
      "main_modified":False,
      "caveats":[
        "All three selected cases remain visible even when reproductions fail.",
        "Eligibility is strictly conditioned on buggy fail/fixed pass and complete AST oracle.",
        "C uses additional runtime information; it is not an equal-compute benchmark.",
        "Passing and failing calls can overlap, so rank is not proof of causality.",
        "N <= 3 is inadequate for scientific generalization.",
      ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--results-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=summarize(args.results_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,
                                      sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":result["status"],
      "selected":result["preregistered_cases"],
      "eligible":result["cases_with_valid_reproducer_and_full_oracle"],
      "primary_delta":result["primary_hit_at_10_difference_C_minus_A"],
      "case_statuses":{x["case"]:x["status"] for x in result["case_results"]},
    },ensure_ascii=False))


if __name__=="__main__":
    main()
