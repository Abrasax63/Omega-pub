"""Post-freeze comparison using #121's already-published oracle.

A descriptive, nonblind single-case comparison, not a proof of causality or
generalization. Source and weights frozen in earlier artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASELINE_ORACLE_SHA256="25f212a267670e2bfe945d4eaabc91cea5c95cbc269b1ffdeefcccc497d5bc18"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def evaluate(profile_ranks_bytes,expected_sha,oracle_bytes):
    if digest(profile_ranks_bytes)!=expected_sha:
        raise ValueError("PROFILE_RANKS_DRIFT")
    if digest(oracle_bytes)!=BASELINE_ORACLE_SHA256:
        raise ValueError("HISTORICAL_ORACLE_DRIFT")
    ranks=json.loads(profile_ranks_bytes)
    oracle=json.loads(oracle_bytes)
    if ranks.get("phase")!="BUGGY_PROFILE_RANKS_SEALED_BEFORE_ORACLE":
        raise ValueError("NOT_SEALED")
    if oracle.get("experiment")!="OMEGA-BUGSINPY-OFFICIAL-REPRO-02":
        raise ValueError("WRONG_HISTORICAL_ORACLE")
    inventory={x["key"]:x for x in ranks["ranks"]}
    modified=oracle["oracle"]["oracle_targets"]
    missing=[x for x in modified if x not in inventory]
    records={}
    for label,rank_key in (("A_lexical","rank_a"),("B_profile","rank_b_profile")):
        vals=[inventory[k][rank_key] for k in modified if k in inventory]
        best=min(vals) if vals else None
        records[label]={
          "best_rank":best,
          "hit_at_5":best is not None and best<=5,
          "hit_at_10":best is not None and best<=10,
          "hit_at_20":best is not None and best<=20,
          "matched_oracle_targets":len(vals),
        }
    if not ranks["valid_runtime_profile_for_comparison"]:
        status="PROFILE_UNUSABLE"
    elif not oracle.get("historical_regression_test_buggy_fail_fixed_pass"):
        status="HISTORICAL_TEST_NOT_VERIFIED"
    elif oracle["oracle"]["unresolved"] or missing or not modified:
        status="ORACLE_PARTIAL_OR_OUT_OF_SCOPE"
    else:
        a=records["A_lexical"]["hit_at_10"]
        b=records["B_profile"]["hit_at_10"]
        status=("LOCAL_IMPROVEMENT_ONE_KNOWN_CASE" if b and not a else
                "LOCAL_REGRESSION_ONE_KNOWN_CASE" if a and not b else
                "NO_DIFFERENCE")
    return {
      "experiment":"OMEGA-RUNTIME-CALLTRACE-01",
      "phase":"POST_FREEZE_KNOWN_ORACLE_DESCRIPTIVE_COMPARISON",
      "status":status,
      "profile_rank_manifest_sha256":expected_sha,
      "historical_oracle_sha256":BASELINE_ORACLE_SHA256,
      "historical_test_buggy_fail_fixed_pass":bool(oracle.get("historical_regression_test_buggy_fail_fixed_pass")),
      "profile_usable":ranks["valid_runtime_profile_for_comparison"],
      "oracle_target_count":len(modified),
      "oracle_unresolved":oracle["oracle"]["unresolved"],
      "oracle_inventory_missing":missing,
      "scores":records,
      "calls_observed":ranks["profile_observed_calls"],
      "mapped_functions":ranks["mapped_unique_functions"],
      "profile_seconds":ranks["profile_elapsed_seconds"],
      "same_inspection_budget":True,
      "same_information_and_runtime_budget":False,
      "known_nonblind_case":True,
      "generalization_demonstrated":False,
      "model_called":False,
      "patch_generated":False,
      "repair_correctness":None,
      "main_modified":False,
      "limitations":[
        "A function call observed during a failing test is not proof of root cause.",
        "Historical oracle used in this pilot was already known from PR #121.",
        "Profiler adds runtime and data unavailable to lexical arm A.",
        "One case is insufficient for scientific generalization or statistical superiority.",
      ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--profile-ranks",type=Path,required=True)
    p.add_argument("--expected-sha256",required=True)
    p.add_argument("--historical-oracle",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=evaluate(args.profile_ranks.read_bytes(),args.expected_sha256,
                 args.historical_oracle.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,
                                    indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":out["status"],"calls":out["calls_observed"],
      "mapped_functions":out["mapped_functions"],
      "scores":out["scores"],"sha256":digest(args.output.read_bytes())
    },ensure_ascii=False))


if __name__=="__main__":
    main()
