"""Official BugsInPy-1 targeted failing test, with fixed TEST only transplanted.

No fixed production code or historical diff accessed during this phase.
Reuse frozen #120 ranker unchanged except the experiment label / provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"traceback_loc_01"))
from trace_localize import build_manifest

TARGET_TEST="test.test_utils.TestUtil.test_match_str"


def official_rank(root:Path, log:str, exit_code:int)->dict:
    result=build_manifest(root,log,exit_code)
    result["experiment"]="OMEGA-BUGSINPY-OFFICIAL-REPRO-02"
    result["official_test_command"]="python -m unittest -q "+TARGET_TEST
    result["fixed_test_transplanted_to_buggy"]=True
    result["fixed_production_accessed"]=False
    result["known_nonblind_reproducer_development"]=True
    result["fixed_source_accessed"]=False
    result["nonblind_comparison"]=True
    result["claim_generalization"]=False
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--test-log",type=Path,required=True)
    p.add_argument("--exit-code",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=official_rank(args.buggy_checkout,
                         args.test_log.read_text(encoding="utf-8",errors="replace"),
                         args.exit_code)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                      ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"buggy_test_exit_code":args.exit_code,
                      "frames":len(result.get("ordered_unique_mapped_frame_keys",[])),
                      "targets":result.get("total_targets"),
                      "a_top10":result.get("top_a",[])[:10],
                      "b_top10":result.get("top_b",[])[:10],
                      "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()},
                     ensure_ascii=False))


if __name__=="__main__":
    main()
