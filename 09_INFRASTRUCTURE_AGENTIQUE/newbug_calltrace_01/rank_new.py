"""Holdout youtube-dl-2: exact #119 lexical score and #122 last-call boost.

Reads only BUGGY production, FIXED public test (BugsInPy transplant), and the
BUGGY runtime call profile. Never reads the FIXED production or historical diff.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"mechanism_loc_01"))
import localize as frozen_lexical
sys.path.insert(0,str(HERE.parent/"runtime_calltrace_01"))
from profile_rank import locate_event

BUGGY_COMMIT="84f085d4bdb66ee025fb337bcd571eab7469da97"
FIXED_COMMIT="9d6ac71c27b1dfb662c795ef598dbfd0286682da"
PKG="youtube_dl"
TEST_PATH="test/test_InfoExtractor.py"
OFFICIAL_TEST="test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats"
fixed_grammar="PR119 lexical score, PR122 last-call boost"
frozen_lexical.ROOT_PACKAGE=PKG
frozen_lexical.TEST_PATH=TEST_PATH


def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()


def rank(root:Path,profile_raw:bytes) -> dict:
    profile=json.loads(profile_raw)
    if profile.get("experiment")!="OMEGA-RUNTIME-CALLTRACE-01" or profile.get("target_test")!=OFFICIAL_TEST:
        raise ValueError("WRONG_PROFILE_OR_TEST")
    if profile.get("project_source_root")!=PKG or profile.get("fixed_production_accessed"):
        raise ValueError("UNSAFE_PROFILE")
    test_file=root/TEST_PATH
    if not test_file.is_file() or test_file.is_symlink():
        return {"status":"TEST_TRANSPLANT_FAILED","targets":[]}
    raw=test_file.read_bytes()
    signals=frozen_lexical.test_signals(raw.decode("utf-8"))
    inv,hashes,errors=frozen_lexical.collect_targets(root)
    if errors:
        return {"status":"SOURCE_PARSE_ERROR","errors":errors,"targets":[]}
    if not inv:
        return {"status":"NO_FUNCTIONS","targets":[]}
    lexical=[]
    for item in inv:
        score,factors=frozen_lexical.score(item,signals)
        lexical.append(dict(item,score_a=score,factors=factors))
    a=sorted(lexical,key=lambda t:(-t["score_a"],t["file"],t["line"],t["qualname"]))
    a_rank={t["key"]:n+1 for n,t in enumerate(a)}
    lookup={}
    for t in lexical:
        lookup.setdefault(t["file"],[]).append(t)
    last_seen={}
    unmapped=0
    for n,event in enumerate(profile.get("events",[])):
        key=locate_event(event,lookup)
        if key is None:
            unmapped+=1
        else:
            last_seen[key]=n
    ordered=sorted(last_seen,key=lambda k:(last_seen[k],k))
    bonuses={key:1000+10*(i+1) for i,key in enumerate(ordered)}
    b=sorted(lexical,key=lambda t:(
        -(t["score_a"]+bonuses.get(t["key"],0)),t["file"],t["line"],t["qualname"]))
    b_rank={t["key"]:n+1 for n,t in enumerate(b)}
    run_failed=(profile.get("test_count")==1 and profile.get("tests_run")==1
                and not profile.get("test_passed",True)
                and profile.get("failures",0)+profile.get("errors",0)>=1)
    if not run_failed:
        status="REPRODUCER_UNCONFIRMED"
    elif profile.get("truncated"):
        status="TRUNCATED_PROFILE"
    elif not ordered:
        status="NO_USABLE_CALL_EVENTS"
    else:
        status="BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN"
    targets=[dict(t,rank_a=a_rank[t["key"]],rank_b=b_rank[t["key"]],
                  profile_boost=bonuses.get(t["key"],0))
             for t in sorted(lexical,key=lambda x:x["key"])]
    return {
      "experiment":"OMEGA-NEWBUG-CALLTRACE-01",
      "phase":"BUGGY_ONLY_RANKS_SEALED_BEFORE_PRODUCTION_FIXED",
      "status":status,
      "case":"youtube-dl-2",
      "buggy_commit":BUGGY_COMMIT,
      "fixed_commit_provenance_only":FIXED_COMMIT,
      "test_file":TEST_PATH,
      "test_sha256":sha(raw),
      "official_test":OFFICIAL_TEST,
      "source_hashes":hashes,
      "target_count":len(targets),
      "signals":signals,
      "profile_sha256":sha(profile_raw),
      "profile_calls":profile["observed_calls"],
      "profile_tests_run":profile["tests_run"],
      "profile_failures":profile["failures"],
      "profile_errors":profile["errors"],
      "profile_passed":profile["test_passed"],
      "profile_seconds":profile["profiled_seconds"],
      "profile_truncated":profile["truncated"],
      "mapped_functions":len(ordered),
      "unmapped_events":unmapped,
      "profiled_function_order_last_seen":ordered,
      "same_inventory":True,
      "same_top10_inspection_budget":True,
      "same_information_and_runtime_budget":False,
      "valid_profile_gate":status=="BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN",
      "targets":targets,
      "top_a":[t["key"] for t in a[:20]],
      "top_b":[t["key"] for t in b[:20]],
      "production_fixed_accessed":False,
      "source_diff_accessed":False,
      "oracle_accessed":False,
      "model_called":False,
      "repair_correctness":None,
      "main_modified":False,
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--profile",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=rank(args.buggy_checkout,args.profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,
                                     indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],
                      "targets":out.get("target_count"),
                      "observed_calls":out.get("profile_calls"),
                      "mapped_functions":out.get("mapped_functions"),
                      "top_a":out.get("top_a",[])[:10],
                      "top_b":out.get("top_b",[])[:10],
                      "sha256":sha(args.output.read_bytes())},ensure_ascii=False))


if __name__=="__main__":
    main()
