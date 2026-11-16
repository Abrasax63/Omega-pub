"""OMEGA-REPAIR-COVERAGE-01: complete pre-frozen candidate pool on real tests.

Diagnostic ONLY, no new patch generation, no changed rank order or selection.
Tests ranks 7-20 AFTER previous 1-6 were verified in the same historical run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from run_diagnostic import CASES,MAX_TESTED_PATCHES,stage_patch,run_docker

EXPERIMENT="OMEGA-REPAIR-COVERAGE-01"
EXPECTED_POOL_SIZE=20
EXPECT_PREVIOUS=6
EXPECTED_REMAINING=EXPECTED_POOL_SIZE-EXPECT_PREVIOUS

def digest(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def verify_manifest(case,oracle,summary,proposals):
    if case not in ("B2","B3") or case not in CASES:
        raise ValueError("unexpected historical case")
    prior=next((x for x in oracle.get("cases",[]) if x.get("id")==case),None)
    if not prior or not prior.get("historical_regression_reproduced"):
        raise ValueError("buggy/fixed control not reproduced")
    if prior.get("verdict")!="REPAIR_REFUTED":
        raise ValueError("unexpected earlier repair verdict")
    scored=next((x for x in summary.get("cases",[]) if x.get("id")==case),None)
    if not scored or scored.get("status")!="REPAIRS_REFUTED_OR_NO_CANDIDATES":
        raise ValueError("prior six tests not confirmed")
    earlier=scored.get("patches_tested",[])
    rows=proposals.get("candidates",[])
    if len(rows)!=EXPECTED_POOL_SIZE or proposals.get("candidate_count")!=EXPECTED_POOL_SIZE:
        raise ValueError("not the exact 20-candidate list")
    if len(earlier)!=EXPECT_PREVIOUS:
        raise ValueError("prior six tests not present")
    ids=[x["id"] for x in rows]
    if len(set(ids))!=EXPECTED_POOL_SIZE or ids!=[
        "R"+str(x).zfill(2) for x in range(EXPECTED_POOL_SIZE)]:
        raise ValueError("candidate IDs/order modified")
    if [x["id"] for x in earlier]!=ids[:EXPECT_PREVIOUS]:
        raise ValueError("prior results do not refer to first six candidates")
    if any(x.get("passes_real_regression") for x in earlier):
        raise ValueError("previous run already had a repair")
    if any(x.get("exit")!=1 for x in earlier):
        raise ValueError("previous tests had non-assertion error")
    for x in rows:
        if len(x.get("lines",[])) not in (1,2):
            raise ValueError("patch must modify one or two lines")
        if len({c.get("line") for c in x.get("changes",[])})!=len(x["lines"]):
            raise ValueError("unmatched changed-line inventory")
        if sorted(x["lines"])!=sorted(c.get("line") for c in x["changes"]):
            raise ValueError("patch lines changed")
        for k in ("path","source_sha256","source_before_sha256","rule"):
            if not x.get(k):
                raise ValueError("missing candidate provenance")
    return earlier,rows

def classify_test(result):
    code=result.get("exit")
    logs=result.get("combined_log","")
    if code==0:
        return "TEST_PASSED"
    if code==1 and re.search(r"(?m)^FAILED\s+",logs):
        return "TEST_FAILED"
    if code in (1,2) and re.search(
            r"(?im)(ERROR collecting|SyntaxError:|ImportError:|ModuleNotFoundError:)",logs):
        return "COLLECTION_OR_PATCH_ERROR"
    if code is None or code not in (0,1):
        return "ENVIRONMENT_OR_EXECUTION_ERROR"
    return "UNCLASSIFIED_FAILURE"

def expand_one(case,workspace,evidence,oracle,summary):
    rows=json.loads((evidence/(case+"-patches.json")).read_text(encoding="utf-8"))
    previous,pool=verify_manifest(case,oracle,summary,rows)
    first_sha=digest(pool)
    result={
        "id":case,"frozen_candidate_pool_sha256":first_sha,
        "fixed_buggy_control_reproduced":True,
        "source_candidates_total":len(pool),
        "previous_six":[{"id":x["id"],"exit":x["exit"],
                         "passes":bool(x["passes_real_regression"])} for x in previous],
        "remaining":[],"source_list_modified":False,
        "same_historical_docker":True,
    }
    for rank,row in enumerate(pool[EXPECT_PREVIOUS:],EXPECT_PREVIOUS+1):
        stage_patch(workspace,case,row)
        outcome=run_docker(workspace,case,"trace-"+row["id"])
        (evidence/(case+"-expanded-"+row["id"]+".log")).write_text(
            outcome.get("combined_log",""),encoding="utf-8")
        result["remaining"].append({
            "rank":rank,"id":row["id"],"path":row["path"],
            "rule":row["rule"],"lines":row["lines"],
            "source_sha256":row["source_sha256"],
            "exit":outcome.get("exit"),
            "classification":classify_test(outcome),
        })
    result["late_passes"]=sum(x["classification"]=="TEST_PASSED"
                              for x in result["remaining"])
    classifications=[x["classification"] for x in result["remaining"]]
    if result["late_passes"]:
        result["verdict"]="LATE_SUCCESS_BUDGET_LIMITATION"
    elif any(x not in ("TEST_FAILED","COLLECTION_OR_PATCH_ERROR")
             for x in classifications):
        result["verdict"]="INDETERMINATE_EXECUTION"
    elif len(classifications)==EXPECTED_REMAINING:
        result["verdict"]="NO_REPAIR_IN_PREDEFINED_20_CANDIDATES"
    else:
        result["verdict"]="INDETERMINATE_INCOMPLETE"
    result["executed_new_tests"]=len(result["remaining"])
    return result

def run(workspace,evidence,oracle_path):
    workspace=Path(workspace).resolve()
    evidence=Path(evidence).resolve()
    oracle=json.loads(Path(oracle_path).read_text(encoding="utf-8"))
    summary=json.loads((evidence/"summary.json").read_text(encoding="utf-8"))
    if summary.get("experiment")!="OMEGA-TRACE-REPAIR-01":
        raise ValueError("wrong historical trace experiment")
    cases=[expand_one(c,workspace,evidence,oracle,summary) for c in ("B2","B3")]
    return {
        "experiment":EXPERIMENT,
        "scope":"POST_HOC_EXPRESSIVITY_AUDIT",
        "cases":cases,
        "total_frozen_candidates":40,
        "previously_tested":12,
        "new_real_regression_tests":sum(c["executed_new_tests"] for c in cases),
        "new_candidates_generated":0,
        "patch_budget_changed":False,
        "scientific_status":"EXPERIMENTAL_NOT_INDEPENDENT",
        "model_called":False,"main_modified":False,"core_promoted":False,
        "limitations":[
            "The two historical fixes had already been inspected by the investigators.",
            "Only targeted authentic upstream tests, not full upstream test suites.",
            "Twenty finite, human-defined AST candidates are not a complete program repair language.",
            "Candidate scoring reuses existing Python 3.6 Docker and its package stubs; timing is noisy.",
            "A late test pass requires a separate independent regression evaluation."
        ],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--oracle-report",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=run(args.workspace,args.evidence_dir,args.oracle_report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
        encoding="utf-8"
    )
    print(json.dumps({
        "experiment":EXPERIMENT,
        "new_actual_test_runs":report["new_real_regression_tests"],
        "cases":[{"id":c["id"],"verdict":c["verdict"],
                  "late_passes":c["late_passes"],
                  "number_tested":c["executed_new_tests"],
                  "candidate_pool_sha256":c["frozen_candidate_pool_sha256"]}
                 for c in report["cases"]]
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
