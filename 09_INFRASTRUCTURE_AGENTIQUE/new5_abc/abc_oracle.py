"""Recheck frozen A/B/C candidates against authentic historical upstream tests.

This script is used only in a SEPARATE GitHub job after the buggy-only selection
artifact is already immutable. Fixed source is NEVER an input to candidate
generation. Public fixed SHA metadata is not a third-party blind holdout.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import os

from abc_core import ARMS, MAX_PER_ARM, sha, verify_manifest
from abc_runner import build_project_image, run_regression, test_candidate


def verify_commitment(record, cohort):
    expected=record.get("selection_sha256")
    if not isinstance(expected,str) or len(expected)!=64:
        raise ValueError("invalid freeze commitment")
    canonical={k:v for k,v in record.items() if k!="selection_sha256"}
    if sha(json.dumps(canonical,sort_keys=True,ensure_ascii=False))!=expected:
        raise ValueError("selection commitment drift")
    if record.get("fixed_source_seen") or record.get("fixed_diff_seen"):
        raise ValueError("fixed source was consulted during selection")
    if record.get("phase")!="ABC_SELECTION_BUGGY_ONLY":
        raise ValueError("wrong phase")
    if record.get("new_model_calls",100)>5:
        raise ValueError("model budget exceeded")
    if record.get("external_oracle_opened") is not False:
        raise ValueError("external reference already opened")
    verify_manifest(record,cohort)
    for item in record["cases"]:
        arms=item.get("arms",{})
        for name in ARMS:
            if name in arms:
                a=arms[name]
                if len(a["actual_attempts"])>MAX_PER_ARM or a["logical_tests_consumed"]>MAX_PER_ARM:
                    raise ValueError("patch test budget exceeded")
                if a["selected_patch_id"] and a["selected_patch_id"] not in {
                        x["id"] for x in item["candidates"]}:
                    raise ValueError("patch outside frozen candidate set")
    return expected


def oracle_verify(cohort_file, selection_file, buggy_dir, fixed_dir, tests_dir, output):
    cohort=json.loads(cohort_file.read_text(encoding="utf8"))
    frozen=json.loads(selection_file.read_text(encoding="utf8"))
    commitment=verify_commitment(frozen,cohort)
    cases=[]
    for case,selected in zip(cohort["cases"],frozen["cases"]):
        ident=case["id"]
        buggy=buggy_dir/ident
        fixed=fixed_dir/ident
        test=tests_dir/(ident+".py")
        for root,sha_req in ((buggy,case["buggy_sha"]),(fixed,case["fixed_sha"])):
            sha_found=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
            if sha_found!=sha_req:
                raise ValueError("reproduction source SHA mismatch for "+ident)
        if sha256(test.read_bytes()).hexdigest()!=selected.get("test_only_sha256"):
            raise ValueError("public test changed after selection")
        image,build=build_project_image(case,buggy)
        audit={
            "id":ident,"project":case["project"],"bug_id":case["bug_id"],
            "buggy_sha":case["buggy_sha"],"fixed_sha":case["fixed_sha"],
            "fixed_read_only_in_oracle_job":True,
            "replay_dependency_build":build,
            "selection_status":selected.get("status"),"model_selection":selected.get("model_selection"),
            "frozen_patch_ids":{k:v.get("selected_patch_id") for k,v in selected.get("arms",{}).items()},
            "arm_results":{}}
        if build["exit"]!=0:
            audit["status"]="ORACLE_ENVIRONMENT_BLOCKED"
            cases.append(audit)
            continue
        fixed_run=run_regression(image,case,fixed,test)
        buggy_run=run_regression(image,case,buggy,test)
        audit["fixed_test"]={k:v for k,v in fixed_run.items() if k!="trace_log"}
        audit["buggy_test"]={k:v for k,v in buggy_run.items() if k!="trace_log"}
        if fixed_run["status"]!="PASS":
            audit["status"]="FIXED_REFERENCE_NOT_REPRODUCED"
        elif buggy_run["status"]=="PASS":
            audit["status"]="BUG_NOT_REPRODUCED"
        elif buggy_run["status"]!="FAIL":
            audit["status"]="ORACLE_ENVIRONMENT_BLOCKED"
        else:
            audit["status"]="AUTHENTIC_HISTORICAL_REGRESSION_REPRODUCED"
        if audit["status"]=="AUTHENTIC_HISTORICAL_REGRESSION_REPRODUCED":
            pool={c["id"]:c for c in selected.get("candidates",[])}
            checked={}
            for arm in ARMS:
                arm_selection=selected.get("arms",{}).get(arm,{})
                ident_patch=arm_selection.get("selected_patch_id")
                if not ident_patch:
                    audit["arm_results"][arm]={"status":"NO_PUBLIC_TEST_PASS_SELECTED",
                                               "patch_id":None}
                    continue
                if ident_patch not in pool:
                    raise RuntimeError("uncommitted candidate chosen after fixed source")
                if ident_patch not in checked:
                    checked[ident_patch]=test_candidate(image,case,buggy,test,pool[ident_patch])
                outcome=checked[ident_patch]
                audit["arm_results"][arm]={
                    "status":"HISTORICAL_TARGET_PASS_REPLAYED" if outcome["status"]=="PASS"
                            else ("REPAIR_REFUTED" if outcome["status"]=="FAIL" else "ENVIRONMENT_BLOCKED"),
                    "patch_id":ident_patch,"candidate_sha256":pool[ident_patch]["modified_sha256"],
                    "run":{k:v for k,v in outcome.items() if k!="trace_log"},
                    "replayed_shared_patch":sum(1 for a in audit["arm_results"].values()
                                                if a.get("patch_id")==ident_patch)>0}
        cases.append(audit)
    confirmed=sum(c["status"]=="AUTHENTIC_HISTORICAL_REGRESSION_REPRODUCED" for c in cases)
    repairs={arm:sum(c.get("arm_results",{}).get(arm,{}).get("status")=="HISTORICAL_TARGET_PASS_REPLAYED"
                     for c in cases) for arm in ARMS}
    report={
        "experiment":cohort["experiment"],"phase":"HISTORICAL_ORACLE_AFTER_FROZEN_ABC",
        "selection_sha256":commitment,"case_count":5,"historically_reproduced":confirmed,
        "repairs_by_arm":repairs,
        "regression_test_budget_per_arm_per_bug":MAX_PER_ARM,
        "llm_calls":frozen["new_model_calls"],
        "llm_token_cap_per_call":128,
        "model_inference_cost_equalized":False,
        "source_provenance":"public pinned BugsInPy buggy/fixed Git commits",
        "whole_project_test_suite_ran":False,
        "independent_external_holdout":False,
        "scientific_status":"EXPLORATORY_NOT_CERTIFIED",
        "main_modified":False,"promoted_to_core":False,
        "cases":cases,
        "limitations":[
            "Same authentic regression test is used during candidate selection and replay: NOT an unseen holdout.",
            "Public historical fixes are available to investigators; procedure masks them, not cryptography.",
            "Only target regressions tested, no whole-suite safety guarantees.",
            "Qwen uses extra inference tokens and CPU beyond matched regression-test caps.",
            "Environment-blocked cases are excluded from reproduced denominator, but shown among all five.",
        ]
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"experiment":report["experiment"],"reproduced":confirmed,
                      "repairs":repairs,"cases":[{"id":c["id"],"status":c["status"]}
                                            for c in cases]},indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",type=Path,required=True)
    p.add_argument("--selection",type=Path,required=True)
    p.add_argument("--buggy-dir",type=Path,required=True)
    p.add_argument("--fixed-dir",type=Path,required=True)
    p.add_argument("--tests-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    oracle_verify(a.cohort,a.selection,a.buggy_dir,a.fixed_dir,a.tests_dir,a.output)


if __name__=="__main__":
    main()
