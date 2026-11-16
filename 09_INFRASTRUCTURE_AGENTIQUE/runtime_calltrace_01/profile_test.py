"""Bounded Python-3.7-compatible profiler for a single historical unittest.

Import/construct the test suite before enabling sys.setprofile, then capture
function-call events only from an exact project source root. Never record
arguments, return values, object reprs or secrets. No network required.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

DEFAULT_TEST="test.test_utils.TestUtil.test_match_str"
MAX_EVENTS=100000


def project_profiler(project_root, package_name, events, stats):
    root=os.path.realpath(str(project_root))
    base=os.path.join(root,package_name)+os.sep
    def record(frame,event,arg):
        if event!="call":
            return
        p=os.path.realpath(frame.f_code.co_filename)
        if not p.startswith(base) or not p.endswith(".py"):
            return
        stats["observed_calls"]+=1
        if len(events)>=MAX_EVENTS:
            stats["truncated"]=True
            return
        events.append({
            "file":os.path.relpath(p,root).replace(os.sep,"/"),
            "firstlineno":frame.f_code.co_firstlineno,
            "function":frame.f_code.co_name,
        })
    return record


def profile_test(root, target=DEFAULT_TEST, package="youtube_dl"):
    root=Path(root).resolve()
    if not (root/package).is_dir():
        raise ValueError("PACKAGE_SOURCE_UNAVAILABLE")
    os.chdir(str(root))
    sys.path.insert(0,str(root))
    # Important: import modules and construct suite BEFORE profiling.
    suite=unittest.defaultTestLoader.loadTestsFromName(target)
    n=suite.countTestCases()
    events=[]
    stats={"observed_calls":0,"truncated":False}
    hook=project_profiler(root,package,events,stats)
    start=time.monotonic()
    try:
        sys.setprofile(hook)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        sys.setprofile(None)
    elapsed=round(time.monotonic()-start,6)
    return {
      "experiment":"OMEGA-RUNTIME-CALLTRACE-01",
      "phase":"BUGGY_ONLY_TEST_PROFILE",
      "target_test":target,
      "project_source_root":package,
      "test_count":n,
      "tests_run":result.testsRun,
      "failures":len(result.failures),
      "errors":len(result.errors),
      "test_passed":result.wasSuccessful(),
      "profiled_seconds":elapsed,
      "max_recorded_events":MAX_EVENTS,
      "observed_calls":stats["observed_calls"],
      "truncated":stats["truncated"],
      "events":events,
      "fixed_production_accessed":False,
      "raw_args_or_return_values_recorded":False,
      "model_called":False,
      "repair_attempted":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--test",default=DEFAULT_TEST)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=profile_test(args.repo_root,args.test)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CALL_TRACE_EVIDENCE",json.dumps({
        "test_passed":report["test_passed"],
        "tests_run":report["tests_run"],
        "failures":report["failures"],
        "errors":report["errors"],
        "observed_calls":report["observed_calls"],
        "truncated":report["truncated"],
        "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()
    }),file=sys.stderr)
    sys.exit(0 if report["test_passed"] else 1)


if __name__=="__main__":
    main()
