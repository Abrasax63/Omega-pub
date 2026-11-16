"""Conservative environment-only differential gate. NO patch/ranking/oracle."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"multiproject_calltrace_01"))
from freeze_ranks import get_case,digest


def check(case,buggy_data,fixed_data,test_sha):
    a=json.loads(buggy_data)
    b=json.loads(fixed_data)
    for data in (a,b):
        if data.get("experiment")!="OMEGA-MULTIPROJECT-CALLTRACE-01":
            raise ValueError("PROFILE_IDENTITY_MISMATCH")
        if data.get("package")!=case["package"] or data.get("tests")!=case["tests"]:
            raise ValueError("CASE_OR_TEST_CHANGED")
    bug_ok=(a.get("status")=="TEST_FAILED" and
            a.get("failure_in_test_body") is True and
            a.get("tests_run",0)>=1 and
            a.get("failed_test_count",0)>=1 and
            not a.get("import_or_collection_error",False))
    fixed_ok=(b.get("status")=="TEST_PASSED" and
              b.get("test_passed") is True and
              b.get("tests_run",0)>=len(case["tests"]) and
              b.get("failed_test_count",0)==0)
    status="BUGGY_FAIL_FIXED_PASS" if bug_ok and fixed_ok else "REPRODUCER_UNCONFIRMED"
    return {
      "experiment":"OMEGA-ENV-REPRO-01",
      "phase":"POSTHOC_ENVIRONMENT_ONLY_REPRODUCTION",
      "case":case["id"],
      "status":status,
      "historical_bug_reproduced":status=="BUGGY_FAIL_FIXED_PASS",
      "buggy_code_commit":case["buggy"],
      "fixed_code_commit":case["fixed"],
      "test_sha256_identical":test_sha,
      "test_specs":case["tests"],
      "buggy_test_body_failed":bug_ok,
      "fixed_test_passed":fixed_ok,
      "buggy_profile_sha256":digest(buggy_data),
      "fixed_profile_sha256":digest(fixed_data),
      "buggy_runner_status":a.get("status"),
      "fixed_runner_status":b.get("status"),
      "buggy_tests_run":a.get("tests_run",0),
      "fixed_tests_run":b.get("tests_run",0),
      "buggy_failed_test_count":a.get("failed_test_count",0),
      "fixed_failed_test_count":b.get("failed_test_count",0),
      "buggy_observed_calls":a.get("profile_observed_calls",0),
      "fixed_observed_calls":b.get("profile_observed_calls",0),
      "ranks_not_computed":True,
      "new_holdout_blindness":False,
      "original_pr124_results_unchanged":True,
      "model_called":False,
      "patch_generated":False,
      "main_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",required=True)
    p.add_argument("--buggy-profile",type=Path,required=True)
    p.add_argument("--fixed-profile",type=Path,required=True)
    p.add_argument("--shared-test-sha256",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=check(get_case(args.case),args.buggy_profile.read_bytes(),
                 args.fixed_profile.read_bytes(),args.shared_test_sha256)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "case":result["case"],"status":result["status"],
      "buggy_runner":result["buggy_runner_status"],
      "fixed_runner":result["fixed_runner_status"],
      "buggy_calls":result["buggy_observed_calls"],
      "fixed_calls":result["fixed_observed_calls"]
    }))


if __name__=="__main__":
    main()
