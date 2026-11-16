"""Certified test-only fixture tree and historical PySnooper-2 reproduction.

This module can only distinguish a test-harness reconstruction from a real
buggy-fail/fixed-pass. It NEVER changes target code, scores or patches.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"env_repro_01"))
from verify_gate import check as parent_gate
sys.path.insert(0,str(HERE.parent/"multiproject_calltrace_01"))
from freeze_ranks import get_case


def sha256(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()


def exact_tree(root:Path,rel="tests/mini_toolbox")->dict:
    folder=root/rel
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("TEST_FIXTURE_TREE_MISSING")
    result={}
    for p in sorted(folder.rglob("*")):
        if p.is_symlink():
            raise ValueError("TEST_FIXTURE_SYMLINK")
        if p.is_file():
            if "__pycache__" in p.parts or p.suffix==".pyc":
                raise ValueError("UNEXPECTED_COMPILED_TEST_ARTIFACT")
            result[p.relative_to(folder).as_posix()]=sha256(p.read_bytes())
    if not result or "__init__.py" not in result:
        raise ValueError("TEST_FIXTURE_INCOMPLETE")
    return result


def check_fixture(buggy:Path,fixed:Path)->dict:
    a=exact_tree(buggy)
    b=exact_tree(fixed)
    if a!=b:
        raise ValueError("TEST_FIXTURE_MISMATCH")
    test="tests/test_pysnooper.py"
    if sha256((buggy/test).read_bytes())!=sha256((fixed/test).read_bytes()):
        raise ValueError("TRANSPLANTED_TEST_MISMATCH")
    return {
      "auxiliary_test_directory":"tests/mini_toolbox",
      "files":a,
      "file_count":len(a),
      "same_test_fixture_on_buggy_and_fixed":True,
      "shared_target_test_sha256":sha256((buggy/test).read_bytes()),
    }


def evaluate(buggy:Path,fixed:Path,buggy_profile:bytes,fixed_profile:bytes)->dict:
    fixture=check_fixture(buggy,fixed)
    case=get_case("pysnooper-2")
    result=parent_gate(case,buggy_profile,fixed_profile,fixture["shared_target_test_sha256"])
    result.update({
      "experiment":"OMEGA-PYSNOOPER-FIXTURE-02",
      "phase":"RETROSPECTIVE_TEST_FIXTURE_RESTORATION",
      "test_fixture_provenance":fixture,
      "new_test_fixture_outside_original_BugsInPy_checkout":True,
      "all_source_code_scores_and_ranks_unchanged":True,
      "pr124_admissible_cases_remain_one_of_three":True,
      "can_credit_localization_gain_to_omega":False,
    })
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--buggy-checkout",type=Path,required=True)
    ap.add_argument("--fixed-checkout",type=Path,required=True)
    ap.add_argument("--buggy-profile",type=Path,required=True)
    ap.add_argument("--fixed-profile",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=evaluate(args.buggy_checkout,args.fixed_checkout,
                    args.buggy_profile.read_bytes(),args.fixed_profile.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
    args.output.write_bytes(data)
    print(json.dumps({
      "experiment":result["experiment"],
      "status":result["status"],
      "buggy_status":result["buggy_runner_status"],
      "fixed_status":result["fixed_runner_status"],
      "fixture_files_verified":result["test_fixture_provenance"]["file_count"],
      "report_sha256":sha256(data)
    },ensure_ascii=False))


if __name__=="__main__":
    main()
