"""Freeze 3-arm lexical / called / last-call localization on BUGGY source only.

Imports PR119's exact lexical weights and PR122's exact call-event-to-AST
matching. The identical target inventory is shared across all arms.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"mechanism_loc_01"))
import localize as existing_lexical
sys.path.insert(0,str(HERE.parent/"runtime_calltrace_01"))
from profile_rank import locate_event


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def get_case(case_id:str)->dict:
    data=json.loads((HERE/"cases.json").read_text(encoding="utf-8"))
    for c in data["cases"]:
        if c["id"]==case_id:
            return c
    raise ValueError("UNKNOWN_PREREGISTERED_CASE")


def classify(profile:dict)->str:
    if profile.get("status")=="RUNNER_OR_DEPENDENCY_ERROR":
        return "REPRODUCER_UNCONFIRMED"
    if profile.get("profile_truncated"):
        return "TRUNCATED_PROFILE"
    if profile.get("tests_run",0)<1 or not profile.get("failure_in_test_body"):
        return "BUGGY_NOT_REPRODUCED"
    if not profile.get("failed_call_events"):
        return "NO_USABLE_CALL_EVENTS"
    return "BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN"


def rank(case:dict,buggy:Path,profile_bytes:bytes)->dict:
    profile=json.loads(profile_bytes)
    if profile.get("experiment")!="OMEGA-MULTIPROJECT-CALLTRACE-01":
        raise ValueError("PROFILE_IDENTITY_MISMATCH")
    if profile.get("package")!=case["package"] or profile.get("tests")!=case["tests"]:
        raise ValueError("PROFILE_WRONG_CASE")
    if profile.get("fixed_production_accessed"):
        raise ValueError("FIXED_PRODUCTION_LEAK")
    path=buggy/case["test_file"]
    if not path.is_file() or path.is_symlink():
        raise ValueError("TEST_TRANSPLANT_FAILED")
    raw=path.read_bytes()
    # Reuse unchanged PR119 frozen logic on an explicitly fixed case.
    existing_lexical.ROOT_PACKAGE=case["package"]
    existing_lexical.TEST_PATH=case["test_file"]
    signals=existing_lexical.test_signals(raw.decode("utf-8"))
    inventory,hashes,errors=existing_lexical.collect_targets(buggy)
    if errors:
        return {
          "status":"SOURCE_PARSE_ERROR","errors":errors,
          "case":case["id"],"phase":"BUGGY_ONLY",
          "source_hashes":hashes,"targets":[]
        }
    # Preregistered scope addendum: tests nested within a production package
    # are informative only for lexical AST, never candidate functions.
    def production_path(rel):
        parts=Path(rel).parts
        name=Path(rel).name
        return (not any(p in ("test","tests") for p in parts)
                and not name.startswith(("test_","tests_")))
    inventory=[t for t in inventory if production_path(t["file"])]
    hashes={rel:value for rel,value in hashes.items() if production_path(rel)}
    if not inventory:
        return {"status":"NO_FUNCTIONS","case":case["id"],
                "phase":"BUGGY_ONLY","targets":[]}
    source=[]
    for t in inventory:
        s,factors=existing_lexical.score(t,signals)
        source.append(dict(t,score_a=s,factors=factors))
    a=sorted(source,key=lambda t:(-t["score_a"],t["file"],t["line"],t["qualname"]))
    by_file={}
    for t in source:
        by_file.setdefault(t["file"],[]).append(t)
    last_seen={}
    unmatched=0
    events=profile.get("failed_call_events",[])
    for index,event in enumerate(events):
        key=locate_event(event,by_file)
        if key is None:
            unmatched+=1
        else:
            last_seen[key]=index
    ordered=sorted(last_seen,key=lambda key:(last_seen[key],key))
    boost_member={key:1000 for key in ordered}
    boost_recency={key:1000+10*(i+1) for i,key in enumerate(ordered)}
    def ordered_by(bonuses):
        return sorted(source,key=lambda t:(
          -(t["score_a"]+bonuses.get(t["key"],0)),
          t["file"],t["line"],t["qualname"]))
    b=ordered_by(boost_member)
    c=ordered_by(boost_recency)
    a_rank={t["key"]:i+1 for i,t in enumerate(a)}
    b_rank={t["key"]:i+1 for i,t in enumerate(b)}
    c_rank={t["key"]:i+1 for i,t in enumerate(c)}
    base_status=classify(profile)
    if base_status=="BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN" and not ordered:
        base_status="NO_USABLE_CALL_EVENTS"
    frozen=[dict(t,rank_a=a_rank[t["key"]],rank_b_membership=b_rank[t["key"]],
                 rank_c_recency=c_rank[t["key"]]) for t in sorted(source,key=lambda t:t["key"])]
    return {
      "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
      "phase":"BUGGY_ONLY_THREE_ARM_COMMIT_BEFORE_FIXED",
      "status":base_status,
      "case":case["id"],
      "package":case["package"],
      "buggy_commit":case["buggy"],
      "fixed_commit_provenance_only":case["fixed"],
      "test_file":case["test_file"],
      "test_sha256":digest(raw),
      "test_selection":case["tests"],
      "framework":case["framework"],
      "source_hashes":hashes,
      "target_count":len(frozen),
      "signals":signals,
      "profile_sha256":digest(profile_bytes),
      "profile_status":profile.get("status"),
      "profile_tests_run":profile.get("tests_run",0),
      "profile_failures":profile.get("failed_test_count",0),
      "profile_seconds":profile.get("profile_seconds"),
      "profile_observed_calls":profile.get("profile_observed_calls",0),
      "profile_truncated":profile.get("profile_truncated",False),
      "mapped_unique_functions":len(ordered),
      "unmatched_failed_call_events":unmatched,
      "ordered_mapped_functions_last_seen":ordered,
      "passing_test_call_event_count":len(profile.get("passed_call_events",[])),
      "same_inventory_all_arms":True,
      "same_inspection_budget_per_arm":10,
      "different_execution_and_information_budget":True,
      "targets":frozen,
      "top_a":[t["key"] for t in a[:20]],
      "top_b":[t["key"] for t in b[:20]],
      "top_c":[t["key"] for t in c[:20]],
      "fixed_source_accessed":False,
      "oracle_accessed":False,
      "model_called":False,
      "patch_generated":False,
      "repair_correctness":None,
      "main_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",required=True)
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--profile",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=rank(get_case(args.case),args.buggy_checkout,args.profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,
                                     indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":out["status"],"case":out["case"],
      "targets":out.get("target_count"),
      "mapped":out.get("mapped_unique_functions"),
      "top_a":out.get("top_a",[])[:10],
      "top_b":out.get("top_b",[])[:10],
      "top_c":out.get("top_c",[])[:10],
      "sha256":digest(args.output.read_bytes())
    },ensure_ascii=False))


if __name__=="__main__":
    main()
