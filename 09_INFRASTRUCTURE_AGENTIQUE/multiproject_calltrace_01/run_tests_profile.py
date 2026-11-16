"""Python >=3.6, no third-party source changes: collect real call events during tests.

The target test module is imported/collected BEFORE installing sys.setprofile.
No function arguments, values, locals or user data are retained.  The pytest
plugin profiles only the 'call' phase; a test failing during setup is NOT a
confirmed historical failure.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

MAX_EVENTS=100000


def function_hook(root,package,target,stats):
    base=os.path.join(os.path.realpath(str(root)),package)+os.sep
    def hook(frame,event,arg):
        if event!="call":
            return
        path=os.path.realpath(frame.f_code.co_filename)
        if not path.startswith(base) or not path.endswith(".py"):
            return
        stats["count"]+=1
        if len(target)>=MAX_EVENTS:
            stats["truncated"]=True
            return
        target.append({
          "file":os.path.relpath(path,root).replace(os.sep,"/"),
          "firstlineno":frame.f_code.co_firstlineno,
          "function":frame.f_code.co_name,
        })
    return hook


def run_unittest(root,package,tests):
    suite=unittest.TestSuite()
    for spec in tests:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(spec))
    events=[]
    stats={"count":0,"truncated":False}
    n=suite.countTestCases()
    hook=function_hook(root,package,events,stats)
    start=time.monotonic()
    previous=sys.getprofile()
    try:
        sys.setprofile(hook)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        sys.setprofile(previous)
    elapsed=time.monotonic()-start
    failed=bool(result.failures or result.errors)
    return {
      "framework":"unittest",
      "test_count":n,"tests_run":result.testsRun,
      "failed_test_count":len(result.failures)+len(result.errors),
      "pass_count":max(0,result.testsRun-len(result.failures)-len(result.errors)),
      "failure_in_test_body":bool(failed and n==1 and result.testsRun==1),
      "test_passed":result.wasSuccessful() and n>0,
      "test_outcomes":[{"test":str(item),"outcome":"FAILED"}
                       for item,_ in result.failures+result.errors],
      "profile_seconds":round(elapsed,6),
      "profile_observed_calls":stats["count"],
      "profile_truncated":stats["truncated"],
      "failed_call_events":events if failed else [],
      "passed_call_events":events if not failed else [],
      "import_or_collection_error":bool(result.errors and not events),
    }


def run_pytest(root,package,tests):
    import pytest  # installed from pinned offline wheelhouse before sandbox
    collected={}
    records={}
    failures_in_setup=[]
    stats={"count":0,"truncated":False}
    class Plugin:
        @pytest.hookimpl(hookwrapper=True,tryfirst=True)
        def pytest_runtest_call(self,item):
            events=[]
            previous=sys.getprofile()
            try:
                sys.setprofile(function_hook(root,package,events,stats))
                yield
            finally:
                sys.setprofile(previous)
                collected[item.nodeid]=events
        def pytest_runtest_logreport(self,report):
            if report.when=="call":
                records[report.nodeid]=report.outcome
            elif report.failed and report.when in ("setup","teardown"):
                failures_in_setup.append({"test":report.nodeid,"phase":report.when})
    start=time.monotonic()
    result_code=int(pytest.main(["-q","-s"]+tests,plugins=[Plugin()]))
    elapsed=time.monotonic()-start
    errors=sum(1 for x in records.values() if x=="failed")
    passed=sum(1 for x in records.values() if x=="passed")
    skipped=sum(1 for x in records.values() if x=="skipped")
    failed=[]
    passing=[]
    for name,events in collected.items():
        if records.get(name)=="failed":
            failed+=events
        elif records.get(name)=="passed":
            passing+=events
    return {
      "framework":"pytest","test_count":len(tests),"tests_run":len(records),
      "failed_test_count":errors,"pass_count":passed,"skipped_count":skipped,
      "failure_in_test_body":errors>0,
      "test_passed":result_code==0 and len(records)==len(tests) and errors==0 and not failures_in_setup,
      "test_outcomes":[{"test":k,"outcome":v} for k,v in sorted(records.items())],
      "test_setup_teardown_errors":failures_in_setup,
      "pytest_exit_code":result_code,
      "profile_seconds":round(elapsed,6),
      "profile_observed_calls":stats["count"],
      "profile_truncated":stats["truncated"],
      "failed_call_events":failed,
      "passed_call_events":passing,
      "import_or_collection_error":bool(failures_in_setup or result_code in (2,3,4,5) or not records),
    }


def execute(root,package,framework,tests):
    root=Path(root).resolve()
    if not (root/package).is_dir():
        return {"status":"SOURCE_UNAVAILABLE","test_passed":False,
                "tests_run":0,"failed_call_events":[],"passed_call_events":[]}
    if not tests:
        return {"status":"NO_TESTS_SELECTED","test_passed":False,
                "tests_run":0,"failed_call_events":[],"passed_call_events":[]}
    os.chdir(str(root))
    sys.path.insert(0,str(root))
    try:
        result=(run_pytest(root,package,tests) if framework=="pytest"
                else run_unittest(root,package,tests))
        status=("TEST_PASSED" if result["test_passed"] else
                "RUNNER_OR_DEPENDENCY_ERROR" if result["import_or_collection_error"] else
                "TEST_FAILED" if result["failure_in_test_body"] else
                "TEST_RESULT_UNCONFIRMED")
    except Exception as error:
        status="RUNNER_OR_DEPENDENCY_ERROR"
        result={"test_passed":False,"tests_run":0,"failed_call_events":[],
                "passed_call_events":[],"failure_in_test_body":False,
                "import_or_collection_error":True,
                "exception_type":type(error).__name__,
                "exception_message":str(error)[:220]}
    return {
      "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
      "phase":"RUNTIME_TEST_CALLS",
      "status":status,
      "package":package,
      "framework":framework,
      "tests":tests,
      "max_events":MAX_EVENTS,
      "sensitive_values_recorded":False,
      "fixed_production_accessed":False,
      **result
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--package",required=True)
    p.add_argument("--framework",choices=("unittest","pytest"),required=True)
    p.add_argument("--tests-json",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=execute(args.repo_root,args.package,args.framework,
                   json.loads(args.tests_json))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode("utf-8")
    args.output.write_bytes(raw)
    print("TEST_EXECUTION_EVIDENCE",json.dumps({
      "status":result["status"],
      "tests_run":result.get("tests_run",0),
      "failed":result.get("failed_test_count",0),
      "package_calls":result.get("profile_observed_calls",0),
      "failed_call_events":len(result.get("failed_call_events",[])),
      "sha256":hashlib.sha256(raw).hexdigest()
    }),file=sys.stderr)


if __name__=="__main__":
    main()
