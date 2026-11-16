"""Post-freeze oracle wrapper for the canonical BugsInPy-1 test transplant."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"traceback_loc_01"))
from postfreeze_oracle import evaluate


def official_evaluate(manifest_bytes:bytes, manifest_sha:str, buggy:Path,
                      fixed:Path, fixed_log:str, fixed_exit:int)->dict:
    base=evaluate(manifest_bytes,manifest_sha,buggy,fixed,fixed_log,fixed_exit)
    base["experiment"]="OMEGA-BUGSINPY-OFFICIAL-REPRO-02"
    base["official_test_command"]="python -m unittest -q test.test_utils.TestUtil.test_match_str"
    base["transplanted_fixed_test_only"]=True
    base["claim_independent_blind_generalization"]=False
    base["nonblind_reproducer_development"]=True
    return base


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--fixed-checkout",type=Path,required=True)
    p.add_argument("--frozen-manifest",type=Path,required=True)
    p.add_argument("--expected-sha256",required=True)
    p.add_argument("--fixed-log",type=Path,required=True)
    p.add_argument("--fixed-exit",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=official_evaluate(
        args.frozen_manifest.read_bytes(),args.expected_sha256,
        args.buggy_checkout,args.fixed_checkout,
        args.fixed_log.read_text(encoding="utf-8",errors="replace"),
        args.fixed_exit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,
                           ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "differential_gate":result["differential_test_gate"],
                      "oracle_targets":len(result["oracle"]["oracle_targets"]),
                      "unresolved":len(result["oracle"]["unresolved"]),
                      "scores":result["scores"],
                      "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()},
                     ensure_ascii=False))


if __name__=="__main__":
    main()
