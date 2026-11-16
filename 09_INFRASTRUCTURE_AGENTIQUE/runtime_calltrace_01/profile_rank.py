"""Freeze dynamic call-rank from real failure, without reading oracle.

Reuses the exact 2322-target baseline manifest from OMEGA-BUGSINPY-OFFICIAL-
REPRO-02 (GitHub run 43865942146), hash-checked byte-for-byte.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASELINE_SHA256="1c26411c771bb4acbd1f14fba9d55e51ab28bc7e8eebee3290aaeb49ee9e5d23"
BUGGY_COMMIT="99036a1298089068dcf80c0985bfcc3f8c24f281"
FIXED_TEST_SHA256="9f89df328fda10e6249c7fd89d85f62eec7888508c6c1e5c5fc7aefe44949054"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def locate_event(evt, targets_by_file):
    matches=[t for t in targets_by_file.get(evt["file"],[])
             if t["line"] <= evt["firstlineno"] <= t["end_line"]]
    if not matches:
        return None
    exact=[t for t in matches if t["function"] == evt["function"]]
    if exact:
        matches=exact
    matches.sort(key=lambda t:(t["end_line"]-t["line"],t["line"],t["key"]))
    return matches[0]["key"]


def rank(baseline_bytes, profile_bytes):
    if digest(baseline_bytes)!=BASELINE_SHA256:
        raise ValueError("BASELINE_MANIFEST_DRIFT")
    base=json.loads(baseline_bytes)
    if base["buggy_commit"]!=BUGGY_COMMIT or base["total_targets"]!=2322:
        raise ValueError("BASELINE_IDENTITY_MISMATCH")
    prof=json.loads(profile_bytes)
    if prof["experiment"]!="OMEGA-RUNTIME-CALLTRACE-01":
        raise ValueError("PROFILE_IDENTITY_MISMATCH")
    if prof["target_test"]!="test.test_utils.TestUtil.test_match_str":
        raise ValueError("WRONG_REGRESSION_TEST")
    targets=base["target_inventory"]
    by_file={}
    for t in targets:
        by_file.setdefault(t["file"],[]).append(t)
    last_seen={}
    unmapped=0
    for index,evt in enumerate(prof["events"]):
        key=locate_event(evt,by_file)
        if key is None:
            unmapped+=1
        else:
            last_seen[key]=index
    ordered=sorted(last_seen,key=lambda k:(last_seen[k],k))
    boosts={key:1000+10*(i+1) for i,key in enumerate(ordered)}
    is_valid=bool(prof["tests_run"]==1 and not prof["test_passed"]
                  and prof["failures"]+prof["errors"]>=1
                  and not prof["truncated"] and ordered)
    if not (prof["tests_run"]==1 and not prof["test_passed"]):
        status="PROFILE_REPRODUCER_UNCONFIRMED"
    elif prof["truncated"]:
        status="TRUNCATED_PROFILE"
    elif not ordered:
        status="NO_USABLE_CALL_EVENTS"
    else:
        status="PROFILE_CALLS_FROZEN_NOT_YET_ORACLE_EVALUATED"
    scored=[]
    for t in targets:
        s=t["score_a"]+boosts.get(t["key"],0)
        scored.append(dict(t,call_boost=boosts.get(t["key"],0),
                           profile_score=s))
    sorted_b=sorted(scored,key=lambda t:(
        -t["profile_score"],t["file"],t["line"],t["qualname"]))
    branks={t["key"]:i+1 for i,t in enumerate(sorted_b)}
    ranks=[dict(t,rank_b_profile=branks[t["key"]]) for t in
           sorted(scored,key=lambda t:t["key"])]
    # No changes to source inventory or lexical ranks are allowed.
    if len({t["key"] for t in ranks})!=len(ranks):
        raise ValueError("DUPLICATE_TARGETS")
    return {
      "experiment":"OMEGA-RUNTIME-CALLTRACE-01",
      "phase":"BUGGY_PROFILE_RANKS_SEALED_BEFORE_ORACLE",
      "status":status,
      "buggy_commit":BUGGY_COMMIT,
      "baseline_sha256":BASELINE_SHA256,
      "fixed_test_sha256":FIXED_TEST_SHA256,
      "profile_raw_sha256":digest(profile_bytes),
      "profile_test_passed":prof["test_passed"],
      "profile_tests_run":prof["tests_run"],
      "profile_observed_calls":prof["observed_calls"],
      "profile_elapsed_seconds":prof["profiled_seconds"],
      "profile_truncated":prof["truncated"],
      "mapped_unique_functions":len(ordered),
      "unmapped_call_events":unmapped,
      "valid_runtime_profile_for_comparison":is_valid,
      "same_function_inventory":True,
      "same_top10_inspection_budget":True,
      "same_information_and_execution_budget":False,
      "ranks":ranks,
      "top_a":[t["key"] for t in sorted(ranks,key=lambda x:x["rank_a"])[:20]],
      "top_b":[t["key"] for t in sorted(ranks,key=lambda x:x["rank_b_profile"])[:20]],
      "fixed_source_accessed":False,
      "oracle_accessed":False,
      "model_called":False,
      "repair_correctness":None,
      "main_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--profile",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=rank(args.baseline.read_bytes(),args.profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":out["status"],"mapped_unique_functions":out["mapped_unique_functions"],
      "unmapped_events":out["unmapped_call_events"],
      "top_a":out["top_a"][:10],"top_b":out["top_b"][:10],
      "sha256":digest(args.output.read_bytes())},ensure_ascii=False))


if __name__=="__main__":
    main()
