"""Oracle invoked only AFTER the first job freezes buggy-only AST candidates.

Genuine upstream pytest target execution is done by the GitHub workflow inside
isolated Docker containers. This module checks provenance and assembles results.
"""
import argparse
import json
import hashlib
from pathlib import Path
import subprocess
from blind_candidates import one_line,sha,read_json

CASES=("B1","B2","B3")

def frozen_integrity(cohort,freeze,repo_root):
    if freeze.get("phase")!="CANDIDATES_FROZEN_BUGGY_ONLY":
        raise RuntimeError("not a prospective frozen record")
    commitment=freeze.get("commitment_sha256")
    canonical={k:v for k,v in freeze.items() if k!="commitment_sha256"}
    if sha(json.dumps(canonical,sort_keys=True,ensure_ascii=False))!=commitment:
        raise RuntimeError("freeze commitment mismatch")
    if freeze.get("fixed_source_seen") or freeze.get("fixed_diff_seen"):
        raise RuntimeError("future information was seen by candidate generator")
    if len(cohort["cases"])!=3 or len(freeze["cases"])!=3:
        raise RuntimeError("cohort inventory drift")
    for c,f in zip(cohort["cases"],freeze["cases"]):
        if c["id"]!=f["id"] or c["buggy_sha"]!=f["buggy_commit"]:
            raise RuntimeError("buggy SHA changed after freeze")
        root=repo_root/c["id"]/"buggy"
        for row in f["candidates"]:
            source=(root/row["path"]).resolve()
            if not source.is_relative_to(root.resolve()):
                raise RuntimeError("candidate path traversal")
            text=source.read_text(encoding="utf-8",errors="replace")
            if sha(text)!=row["source_sha256"]:
                raise RuntimeError("original source SHA altered")
            if text.splitlines()[row["line"]-1]!=row["original"]:
                raise RuntimeError("target line altered")
            if sha(one_line(text,row["line"],row["replacement"]))!=row["modified_sha256"]:
                raise RuntimeError("patch content altered")
    return commitment

def prepare(cohort,freeze,root):
    commitment=frozen_integrity(cohort,freeze,root)
    prepared=[]
    for case,f in zip(cohort["cases"],freeze["cases"]):
        ident=case["id"]
        top=f["top1"]
        patch={"id":ident,"top1_id":top,"proposals":len(f["candidates"]),
               "selected_before_fixed":True,"patch_applied":False}
        if top is not None:
            row=next(c for c in f["candidates"] if c["id"]==top)
            path=root/ident/"patched"/row["path"]
            original=path.read_text(encoding="utf-8",errors="replace")
            if sha(original)!=row["source_sha256"]:
                raise RuntimeError("buggy source in patch workspace mutated")
            modified=one_line(original,row["line"],row["replacement"])
            if sha(modified)!=row["modified_sha256"]:
                raise RuntimeError("frozen patch SHA mismatch")
            path.write_text(modified,encoding="utf-8")
            patch.update({"path":row["path"],"line":row["line"],
                          "rule":row["rule"],"new":row["replacement"],
                          "patch_applied":True,"source_sha256":row["modified_sha256"]})
        prepared.append(patch)
    return {"phase":"PATCHES_FROZEN","freeze_sha256":commitment,
            "model_called":False,"cohort_cases":prepared}

def test_exit(root,ident,version):
    log=root/ident/(version+".log")
    status=root/ident/(version+".exit")
    if not status.is_file():
        return {"status":"MISSING_RUN","exit":None,"tail":log.read_text()[-1800:] if log.is_file() else ""}
    try:
        exitcode=int(status.read_text().strip())
    except ValueError:
        raise RuntimeError("noninteger test exit status")
    out=log.read_text(encoding="utf-8",errors="replace")[-2300:] if log.is_file() else ""
    if exitcode==0:
        label="PASS"
    elif any(key in out.lower() for key in ("failed ","assertionerror"," assert ","failures")):
        label="FAIL"
    else:
        label="ERROR_OR_ENVIRONMENT"
    return {"status":label,"exit":exitcode,"tail":out}

def report(cohort,freeze,prepared,root):
    commitment=frozen_integrity(cohort,freeze,root)
    if prepared["phase"]!="PATCHES_FROZEN" or prepared["freeze_sha256"]!=commitment:
        raise RuntimeError("patches not committed before oracle")
    results=[]
    for case,patch in zip(cohort["cases"],prepared["cohort_cases"]):
        ident=case["id"]
        build=test_exit(root,ident,"build")
        fixed=test_exit(root,ident,"fixed")
        buggy=test_exit(root,ident,"buggy")
        attempt=test_exit(root,ident,"patched")
        if build["status"]!="PASS":
            verdict="ENVIRONMENT_BLOCKED"
        elif fixed["status"]!="PASS":
            verdict="FIXED_REFERENCE_NOT_VALIDATED"
        elif buggy["status"]=="PASS":
            verdict="BUG_NOT_REPRODUCED"
        elif buggy["status"]!="FAIL":
            verdict="BUGGY_ENVIRONMENT_UNCERTAIN"
        elif not patch["patch_applied"]:
            verdict="NO_PATCH_PROPOSED"
        elif attempt["status"]=="PASS":
            verdict="REPAIR_VALIDATED_BOUNDED"
        elif attempt["status"]=="FAIL":
            verdict="REPAIR_REFUTED"
        else:
            verdict="PATCH_ENVIRONMENT_UNCERTAIN"
        results.append({
            "id":ident,"repo":case["repo"],"bug_id":case["bug_id"],
            "buggy_commit":case["buggy_sha"],"fixed_commit":case["fixed_sha"],
            "fixed_reference":fixed,"buggy_observation":buggy,
            "candidate_patch":attempt,"dependency_build":build,
            "proposal":patch,"verdict":verdict,
            "historical_regression_reproduced":(
                fixed["status"]=="PASS" and buggy["status"]=="FAIL"
            ),
        })
    return {
        "experiment_id":"OMEGA-BUGSINPY-BLIND-01",
        "phase":"HISTORICAL_ORACLE_AFTER_PRECOMMITTED_PATCHES",
        "freeze_sha256":commitment,
        "cohort_count":len(results),"cases":results,
        "buggy_fixed_reference_confirmed":sum(x["historical_regression_reproduced"] for x in results),
        "repairs_validated":sum(x["verdict"]=="REPAIR_VALIDATED_BOUNDED" for x in results),
        "model_called":False,"full_project_suite_ran":False,
        "masked_fixed_diff_during_generation":True,
        "blind_evaluation_by_external_custodian":False,
        "scientific_generalization_demonstrated":False,
        "main_modified":False,"promoted":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("prepare","report"),required=True)
    p.add_argument("--cohort",type=Path,required=True)
    p.add_argument("--freeze",type=Path,required=True)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--prepared",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    cohort=read_json(args.cohort)
    frozen=read_json(args.freeze)
    if args.mode=="prepare":
        result=prepare(cohort,frozen,args.workspace)
    else:
        if args.prepared is None:
            raise ValueError("--prepared required")
        result=report(cohort,frozen,read_json(args.prepared),args.workspace)
    args.output.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(
        {"phase":result["phase"],"freeze":result["freeze_sha256"],
         "cases":[{"id":x["id"],"status":x.get("verdict"),
                   "proposals":x.get("proposals")} for x in result.get("cases",result.get("cohort_cases",[]))]},
        ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
