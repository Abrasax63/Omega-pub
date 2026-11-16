"""Second-phase SOURCE ORACLE only after frozen A/B/C SHA verification.

No repair is generated. A passing test's call trace is used only as a
negative causal control, NEVER to create or re-rank candidate lists.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
from freeze_ranks import get_case,digest


def changed_functions(buggy:Path,fixed:Path,report:dict,package:str)->dict:
    mapping={}
    for t in report["targets"]:
        mapping.setdefault(t["file"],[]).append(t)
    oldfiles=set(report["source_hashes"])
    fixedpkg=fixed/package
    fixedfiles=({p.relative_to(fixed).as_posix()
                 for p in fixedpkg.rglob("*.py")} if fixedpkg.exists() else set())
    modified=set()
    unresolved=[]
    changed=[]
    for rel in sorted(oldfiles|fixedfiles):
        old=buggy/rel
        new=fixed/rel
        if not old.is_file() or not new.is_file():
            unresolved.append({"file":rel,"reason":"ADDED_OR_REMOVED_FILE"})
            continue
        a=old.read_text(encoding="utf-8").splitlines()
        b=new.read_text(encoding="utf-8").splitlines()
        if a==b:
            continue
        local=set()
        hunks=0
        for op,i1,i2,j1,j2 in SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes():
            if op=="equal":
                continue
            hunks+=1
            if op=="insert":
                hits=[t for t in mapping.get(rel,[])
                      if t["line"]<i1+1<t["end_line"]]
            else:
                hits=[t for t in mapping.get(rel,[])
                      if t["line"]<=i2 and t["end_line"]>=i1+1]
            if len(hits)!=1:
                unresolved.append({
                  "file":rel,"reason":"HUNK_NOT_UNIQUELY_IN_FUNCTION",
                  "operation":op,"old_lines":[i1+1,i2],
                  "matched_functions":len(hits)})
            else:
                local.add(hits[0]["key"])
                modified.add(hits[0]["key"])
        changed.append({"file":rel,"hunks":hunks,"functions":sorted(local)})
    return {"changed_files":changed,"unresolved_hunks":unresolved,
            "oracle_keys":sorted(modified)}


def score_ranks(report:dict,oracle:dict)->dict:
    idx={t["key"]:t for t in report["targets"]}
    if len(idx)!=len(report["targets"]):
        raise ValueError("DUPLICATE_TARGETS")
    missing=[key for key in oracle["oracle_keys"] if key not in idx]
    stats={}
    for name,col in (("A_lexical","rank_a"),
                     ("B_called_only","rank_b_membership"),
                     ("C_last_call","rank_c_recency")):
        scores=[idx[k][col] for k in oracle["oracle_keys"] if k in idx]
        top=min(scores) if scores else None
        stats[name]={"best_rank":top,
                     "hit_at_5":top is not None and top<=5,
                     "hit_at_10":top is not None and top<=10,
                     "hit_at_20":top is not None and top<=20}
    return {"scores":stats,"missing_target_keys":missing}


def evaluate(case:dict,frozen_bytes:bytes,expected_sha:str,
             buggy:Path,fixed:Path,buggy_profile_bytes:bytes,
             fixed_profile_bytes:bytes)->dict:
    if digest(frozen_bytes)!=expected_sha:
        raise ValueError("FROZEN_RANK_DRIFT")
    frozen=json.loads(frozen_bytes)
    if frozen.get("phase")!="BUGGY_ONLY_THREE_ARM_COMMIT_BEFORE_FIXED":
        raise ValueError("FROZEN_STATE_MISSING")
    if frozen["case"]!=case["id"] or frozen["buggy_commit"]!=case["buggy"]:
        raise ValueError("CASE_IDENTITY_MISMATCH")
    if digest(buggy_profile_bytes)!=frozen["profile_sha256"]:
        raise ValueError("BUGGY_PROFILE_CHANGED")
    if not frozen["same_inventory_all_arms"] or frozen["same_inspection_budget_per_arm"]!=10:
        raise ValueError("FROZEN_BUDGET_CHANGED")
    for rel,hash_expected in frozen["source_hashes"].items():
        if digest((buggy/rel).read_bytes())!=hash_expected:
            raise ValueError("BUGGY_SOURCE_CHANGED:"+rel)
    old_test=buggy/case["test_file"]
    fixed_test=fixed/case["test_file"]
    if (digest(old_test.read_bytes())!=frozen["test_sha256"] or
        digest(fixed_test.read_bytes())!=frozen["test_sha256"]):
        raise ValueError("TRANSPLANTED_TEST_CHANGED")
    bugprof=json.loads(buggy_profile_bytes)
    fixprof=json.loads(fixed_profile_bytes)
    if (fixprof.get("tests")!=case["tests"] or fixprof.get("package")!=case["package"]):
        raise ValueError("FIXED_PROFILE_WRONG_CASE")
    fixed_success=(fixprof.get("test_passed") is True and
                   fixprof.get("tests_run",0)>=len(case["tests"]) and
                   fixprof.get("failed_test_count",0)==0)
    buggy_failure=(frozen["status"]=="BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN"
                   and bugprof.get("failure_in_test_body") is True
                   and not bugprof.get("import_or_collection_error",False))
    oracle=changed_functions(buggy,fixed,frozen,case["package"])
    rankdata=score_ranks(frozen,oracle)
    eligible=bool(fixed_success and buggy_failure and oracle["oracle_keys"]
                  and not oracle["unresolved_hunks"]
                  and not rankdata["missing_target_keys"])
    if not buggy_failure or not fixed_success:
        verdict="REPRODUCER_UNCONFIRMED"
    elif not oracle["oracle_keys"]:
        verdict="ORACLE_OUT_OF_SCOPE"
    elif oracle["unresolved_hunks"] or rankdata["missing_target_keys"]:
        verdict="ORACLE_PARTIAL_NO_COMPARATIVE_CLAIM"
    else:
        A=rankdata["scores"]["A_lexical"]["hit_at_10"]
        C=rankdata["scores"]["C_last_call"]["hit_at_10"]
        verdict=("LOCAL_IMPROVEMENT_ONE_CASE" if C and not A else
                 "LOCAL_REGRESSION_ONE_CASE" if A and not C else "NO_DIFFERENCE")
    seen_bad={(x["file"],x["function"]) for x in bugprof.get("failed_call_events",[])}
    seen_good={(x["file"],x["function"]) for x in fixprof.get("passed_call_events",[])}
    return {
      "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
      "phase":"POST_FREEZE_FIXED_ORACLE_AND_NEGATIVE_CONTROL",
      "case":case["id"],
      "status":verdict,
      "eligible_for_primary_metric":eligible,
      "buggy_commit":case["buggy"],
      "fixed_commit":case["fixed"],
      "frozen_manifest_sha256":expected_sha,
      "buggy_profile_sha256":digest(buggy_profile_bytes),
      "fixed_profile_sha256":digest(fixed_profile_bytes),
      "test_sha256":frozen["test_sha256"],
      "buggy_test_body_failure":buggy_failure,
      "fixed_test_passed":fixed_success,
      "reproduction_differential_verified":bool(buggy_failure and fixed_success),
      "oracle":oracle,
      "scores_descriptive_even_when_ineligible":rankdata["scores"],
      "scored_missing_target_keys":rankdata["missing_target_keys"],
      "buggy_failed_test_calls":len(bugprof.get("failed_call_events",[])),
      "passing_fixed_test_calls":len(fixprof.get("passed_call_events",[])),
      "shared_failed_buggy_and_passing_fixed_called_names":len(seen_bad&seen_good),
      "passing_fixed_trace_did_not_affect_rankings":True,
      "runtime_seconds_buggy_profile":frozen.get("profile_seconds"),
      "runtime_seconds_fixed_profile":fixprof.get("profile_seconds"),
      "same_function_inspection_budget_10":True,
      "same_runtime_or_information_budget":False,
      "model_called":False,
      "patch_generated":False,
      "real_repair_correctness":None,
      "main_modified":False,
      "known_limitations":[
        "One official test set per bug, not complete upstream test suite.",
        "Target presence in call graph is not causal attribution.",
        "The lexical arm does not pay instrumented runtime cost.",
        "Three cases, even all eligible, do not yield statistical evidence of general superiority.",
      ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",required=True)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--expected-sha256",required=True)
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--fixed-checkout",type=Path,required=True)
    p.add_argument("--buggy-profile",type=Path,required=True)
    p.add_argument("--fixed-profile",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=evaluate(get_case(args.case),args.frozen.read_bytes(),
                 args.expected_sha256,args.buggy_checkout,args.fixed_checkout,
                 args.buggy_profile.read_bytes(),args.fixed_profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
      "case":out["case"],"status":out["status"],
      "eligible":out["eligible_for_primary_metric"],
      "A":out["scores_descriptive_even_when_ineligible"]["A_lexical"],
      "B":out["scores_descriptive_even_when_ineligible"]["B_called_only"],
      "C":out["scores_descriptive_even_when_ineligible"]["C_last_call"],
      "unresolved":len(out["oracle"]["unresolved_hunks"]),
      "sha256":digest(args.output.read_bytes())
    },ensure_ascii=False))


if __name__=="__main__":
    main()
