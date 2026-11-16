"""Separate AFTER-FREEZE oracle for youtube-dl-2 calltrace experiment.

Reads fixed production only in second CI job after checking SHA256 of frozen
A/B rankings. A passing fixed-call trace is a *negative causal control*, not
a source of evidence for B.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
from rank_new import BUGGY_COMMIT,FIXED_COMMIT,PKG,TEST_PATH,OFFICIAL_TEST,sha


def changed_functions(buggy:Path,fixed:Path,manifest:dict)->dict:
    targets={}
    for item in manifest["targets"]:
        targets.setdefault(item["file"],[]).append(item)
    known_files=set(manifest["source_hashes"])
    fixed_files={p.relative_to(fixed).as_posix() for p in (fixed/PKG).rglob("*.py")}
    changed=[]
    unresolved=[]
    keys=set()
    for rel in sorted(known_files|fixed_files):
        old=buggy/rel
        new=fixed/rel
        if not old.is_file() or not new.is_file():
            unresolved.append({"file":rel,"reason":"SOURCE_ADDED_OR_REMOVED"})
            continue
        a=old.read_text(encoding="utf-8").splitlines()
        b=new.read_text(encoding="utf-8").splitlines()
        if a==b:
            continue
        n_hunks=0
        file_targets=set()
        for op,i1,i2,j1,j2 in SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
            if op=="equal":
                continue
            n_hunks+=1
            if op=="insert":
                # A strict interior insertion belongs to one function, not
                # a boundary insertion that could be attributed post hoc.
                possibles=[t for t in targets.get(rel,[])
                           if t["line"] < i1+1 < t["end_line"]]
                if len(possibles)!=1:
                    unresolved.append({"file":rel,"reason":"UNRESOLVED_INSERTION",
                                       "old_position":i1+1})
                    continue
            else:
                possibles=[t for t in targets.get(rel,[])
                           if t["line"] <= i2 and t["end_line"] >= i1+1]
                if len(possibles)!=1:
                    unresolved.append({"file":rel,"reason":"UNRESOLVED_HUNK_SCOPE",
                                       "old_interval":[i1+1,i2],
                                       "matches":len(possibles)})
                    continue
            key=possibles[0]["key"]
            file_targets.add(key)
            keys.add(key)
        changed.append({"file":rel,"hunks":n_hunks,
                        "identified_targets":sorted(file_targets)})
    return {"changed_files":changed,"unresolved":unresolved,
            "oracle_target_keys":sorted(keys)}


def evaluate(frozen_bytes:bytes,expected_hash:str,buggy:Path,fixed:Path,
             fixed_profile_bytes:bytes,buggy_profile_bytes:bytes)->dict:
    if sha(frozen_bytes)!=expected_hash:
        raise ValueError("FROZEN_RANK_DRIFT")
    report=json.loads(frozen_bytes)
    if report.get("phase")!="BUGGY_ONLY_RANKS_SEALED_BEFORE_PRODUCTION_FIXED":
        raise ValueError("INVALID_FROZEN_PHASE")
    if report.get("buggy_commit")!=BUGGY_COMMIT or report.get("case")!="youtube-dl-2":
        raise ValueError("BUG_CASE_IDENTITY_MISMATCH")
    if report.get("profile_sha256")!=sha(buggy_profile_bytes):
        raise ValueError("BUGGY_PROFILE_DRIFT")
    fixed_profile=json.loads(fixed_profile_bytes)
    if fixed_profile.get("target_test")!=OFFICIAL_TEST or fixed_profile.get("project_source_root")!=PKG:
        raise ValueError("FIXED_PROFILE_IDENTITY_MISMATCH")
    if sha((buggy/TEST_PATH).read_bytes())!=report["test_sha256"]:
        raise ValueError("BUGGY_TEST_SHA_MISMATCH")
    if sha((fixed/TEST_PATH).read_bytes())!=report["test_sha256"]:
        raise ValueError("FIXED_TEST_SHA_MISMATCH")
    for path,expected in report["source_hashes"].items():
        if sha((buggy/path).read_bytes())!=expected:
            raise ValueError("BUGGY_FILE_SHA_MISMATCH:"+path)
    raw_targets=report["targets"]
    targets={x["key"]:x for x in raw_targets}
    if len(targets)!=len(raw_targets):
        raise ValueError("DUPLICATE_TARGETS")
    if not all(set(("rank_a","rank_b")).issubset(x) for x in raw_targets):
        raise ValueError("INVALID_RANKS")
    oracle=changed_functions(buggy,fixed,report)
    good_fixed=(fixed_profile.get("test_count")==1
                and fixed_profile.get("tests_run")==1
                and fixed_profile.get("test_passed") is True
                and fixed_profile.get("failures")==0 and fixed_profile.get("errors")==0)
    good_buggy=bool(report.get("valid_profile_gate"))
    targetkeys=oracle["oracle_target_keys"]
    stats={}
    for name,rankcol in (("A_lexical","rank_a"),("B_buggy_calltrace","rank_b")):
        best=min((targets[k][rankcol] for k in targetkeys),default=None)
        stats[name]={
           "best_rank":best,
           "hit_at_5":bool(best and best<=5),
           "hit_at_10":bool(best and best<=10),
           "hit_at_20":bool(best and best<=20),
        }
    if not good_buggy or not good_fixed:
        status="REPRODUCER_UNCONFIRMED"
    elif not targetkeys:
        status="ORACLE_OUT_OF_SCOPE"
    elif oracle["unresolved"]:
        status="ORACLE_PARTIAL_NO_COMPARATIVE_CLAIM"
    else:
        a=stats["A_lexical"]["hit_at_10"]
        b=stats["B_buggy_calltrace"]["hit_at_10"]
        status=("LOCAL_IMPROVEMENT_ONE_NEW_BUG" if b and not a else
                "LOCAL_REGRESSION_ONE_NEW_BUG" if a and not b else
                "NO_DIFFERENCE")
    buggy_events=json.loads(buggy_profile_bytes).get("events",[])
    fixed_events=fixed_profile.get("events",[])
    buggy_seen={(x["file"],x["function"]) for x in buggy_events}
    fixed_seen={(x["file"],x["function"]) for x in fixed_events}
    return {
      "experiment":"OMEGA-NEWBUG-CALLTRACE-01",
      "phase":"POST_FREEZE_DIFFERENTIAL_ORACLE_EVALUATION",
      "status":status,
      "buggy_commit":BUGGY_COMMIT,
      "fixed_commit":FIXED_COMMIT,
      "frozen_ranks_sha256":expected_hash,
      "buggy_test_failure_confirmed":good_buggy,
      "fixed_test_passed_confirmed":good_fixed,
      "same_test_sha256":report["test_sha256"],
      "historical_reproduction_confirmed":bool(good_buggy and good_fixed),
      "oracle":oracle,
      "scores":stats,
      "profile_total_calls_buggy":report["profile_calls"],
      "profile_total_calls_fixed":fixed_profile.get("observed_calls"),
      "unique_name_file_pairs_in_both_profiles":len(buggy_seen&fixed_seen),
      "passing_fixed_calls_not_used_for_ranking":True,
      "same_function_inspection_budget_10":True,
      "same_information_and_execution_budget":False,
      "case_selection_fixed_before_pilot":True,
      "only_one_new_case":True,
      "independent_generalization_demonstrated":False,
      "model_called":False,
      "patch_generated":False,
      "repair_correctness":None,
      "main_modified":False,
      "limitations":[
        "A call in both failing and passing profiles is not automatically the root cause.",
        "One new bug gives no statistically powered generalization inference.",
        "B receives runtime information and bears instrumentation cost absent from A.",
        "Only one official test is used; no full project suite or repair patch executed.",
        "Historical test transplant derives from the public fixed revision of the benchmark.",
      ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--fixed-checkout",type=Path,required=True)
    p.add_argument("--frozen-ranks",type=Path,required=True)
    p.add_argument("--expected-sha256",required=True)
    p.add_argument("--buggy-profile",type=Path,required=True)
    p.add_argument("--fixed-profile",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=evaluate(args.frozen_ranks.read_bytes(),args.expected_sha256,
                 args.buggy_checkout,args.fixed_checkout,
                 args.fixed_profile.read_bytes(),args.buggy_profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":out["status"],"gate":out["historical_reproduction_confirmed"],
       "unresolved":len(out["oracle"]["unresolved"]),
       "oracle_targets":len(out["oracle"]["oracle_target_keys"]),
       "scores":out["scores"],
       "shared_call_names":out["unique_name_file_pairs_in_both_profiles"],
       "sha256":sha(args.output.read_bytes())
    },ensure_ascii=False))


if __name__=="__main__":
    main()
