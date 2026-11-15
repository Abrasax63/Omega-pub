"""Post-hoc diagnostic runner on frozen historical BugsInPy checkouts.

Real historical pytest runs in no-network Docker. Localizers and patch
generators receive ONLY buggy sources, call traces and the public test AST.
Historical corrected source paths are consulted solely by report(), AFTER
the ranking and patch list have been frozen.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from rank_suspects import parse_call_trace,rank_files
from bounded_patch import select_candidates

HERE=Path(__file__).resolve().parent
CASES={
    "B2":{"package":"tqdm","test_path":"tqdm/tests/tests_tqdm.py",
          "test_name":"test_format_meter",
          "targets":["tqdm/tests/tests_tqdm.py::test_format_meter"]},
    "B3":{"package":"cookiecutter","test_path":"tests/test_hooks.py",
          "test_name":"test_find_hook",
          "targets":["-p","pytest_cov","tests/test_hooks.py::TestFindHooks::test_find_hook",
                     "tests/test_hooks.py::TestExternalHooks::test_run_hook"]},
}
MAX_TESTED_PATCHES=6

def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def run_docker(workspace,case,mode,trace=False):
    meta=CASES[case]
    pkg=meta["package"]
    original=(workspace/case/mode).resolve()
    image="omega-blind-"+case.lower()+":local"
    argv=[
        "docker","run","--rm","--network","none","--read-only",
        "--cap-drop","ALL","--security-opt","no-new-privileges",
        "--memory","1g","--cpus","1","--pids-limit","96",
        "--tmpfs","/tmp:rw,exec,nosuid,size=224m",
        "--mount","type=bind,src="+str(original)+",dst=/origin,readonly",
        "-e","PYTHONDONTWRITEBYTECODE=1",
        "-e","PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        "-e","PYTHONPATH=/tmp/work",
    ]
    if trace:
        probe=(HERE/"sitecustomize.py").resolve()
        argv.extend(["--mount","type=bind,src="+str(probe)+",dst=/probe/sitecustomize.py,readonly",
                     "-e","OMEGA_TRACE_ROOT=/tmp/work/"+pkg,
                     "-e","PYTHONPATH=/probe:/tmp/work"])
    command=("mkdir -p /tmp/work && cp -R /origin/. /tmp/work/ && cd /tmp/work && "
             "python -m pytest -q -p no:cacheprovider --tb=long --maxfail=1 "
             + " ".join(meta["targets"]))
    argv.extend([image,"sh","-c",command])
    try:
        outcome=subprocess.run(argv,text=True,capture_output=True,timeout=130)
        return {"exit":outcome.returncode,
                "combined_log":outcome.stdout+"\n"+outcome.stderr,
                "command":command,"trace_requested":trace}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {"exit":None,"error":type(exc).__name__,
                "combined_log":str(exc),"trace_requested":trace}

def stage_patch(workspace,case,entry):
    src=(workspace/case/"buggy").resolve()
    destination=workspace/case/("trace-"+entry["id"])
    shutil.copytree(src,destination,ignore=shutil.ignore_patterns(".git"))
    file=(destination/entry["path"]).resolve()
    if not file.is_relative_to(destination.resolve()):
        raise ValueError("candidate path traversal")
    before=file.read_text(encoding="utf-8",errors="replace")
    if sha(before)!=entry["source_before_sha256"]:
        raise RuntimeError("source changed since patch freeze")
    rows=before.splitlines(keepends=True)
    for edit in entry["changes"]:
        rows[edit["line"]-1]=edit["after"]+"\n"
    modified="".join(rows)
    if sha(modified)!=entry["source_sha256"]:
        raise RuntimeError("candidate SHA mismatch")
    file.write_text(modified,encoding="utf-8")

def analyze(workspace,oracle,outdir):
    workspace=Path(workspace).resolve()
    outdir=Path(outdir).resolve()
    outdir.mkdir(parents=True,exist_ok=True)
    history={x["id"]:x for x in oracle["cases"]}
    summary={"experiment":"OMEGA-TRACE-REPAIR-01",
             "scientific_status":"POSTHOC_NOT_BLIND",
             "model_called":False,
             "prior_fixed_diffs_seen_by_researcher":True,
             "fixed_code_provided_to_localizer":False,
             "patch_grammar_budget":20,"max_edited_lines":2,
             "max_actual_patch_test_runs_per_case":MAX_TESTED_PATCHES,
             "no_auto_promotion":True,"main_modified":False,"cases":[]}
    for case,meta in CASES.items():
        previous=history.get(case)
        record={"id":case,"status":"BLOCKED","test_from_original_project":True}
        summary["cases"].append(record)
        if not previous or previous["verdict"]!="REPAIR_REFUTED" or not previous["historical_regression_reproduced"]:
            record["status"]="PRIOR_HISTORICAL_BUG_NOT_REPRODUCED"
            continue
        buggy=workspace/case/"buggy"
        testfile=buggy/meta["test_path"]
        traced=run_docker(workspace,case,"buggy",trace=True)
        (outdir/(case+"-trace.log")).write_text(traced["combined_log"],encoding="utf-8")
        record["traced_exit"]=traced["exit"]
        if traced["exit"]!=1:
            record["status"]="TRACED_TEST_NOT_FAILED";continue
        try:
            profiles=parse_call_trace(traced["combined_log"])
        except (ValueError,KeyError,TypeError) as exc:
            record["status"]="TRACE_NOT_VALID"
            record["reason"]=str(exc)[:250]
            continue
        ranking=rank_files(buggy,meta["package"],profiles,
                           testfile.read_text(encoding="utf-8",errors="replace"),
                           meta["test_name"])
        (outdir/(case+"-ranking.json")).write_text(
            json.dumps(ranking,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
        record["ranked_top3"]=ranking["top3"]
        record["executed_source_files"]=ranking["qualified_code_files"]
        if ranking["status"]!="RANKED":
            record["status"]="RANKING_NOT_AVAILABLE";continue
        patches=select_candidates(buggy,ranking)
        (outdir/(case+"-patches.json")).write_text(
            json.dumps(patches,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
        record["generated_patches"]=patches["candidate_count"]
        record["frozen_patches_sha256"]=sha(json.dumps(patches,sort_keys=True,ensure_ascii=False))
        record["patches_tested"]=[]
        record["status"]="RANKED_AND_CANDIDATES_FROZEN"
        for patch in patches["candidates"][:MAX_TESTED_PATCHES]:
            stage_patch(workspace,case,patch)
            result=run_docker(workspace,case,"trace-"+patch["id"])
            (outdir/(case+"-"+patch["id"]+".log")).write_text(result["combined_log"],encoding="utf-8")
            record["patches_tested"].append({
                "id":patch["id"],"path":patch["path"],"lines":patch["lines"],
                "exit":result["exit"],"passes_real_regression":result["exit"]==0,
                "source_sha256":patch["source_sha256"]})
        record["repairs_validated"]=sum(
            p["passes_real_regression"] for p in record["patches_tested"])
        record["status"]="REPAIR_FOUND_IN_BUDGET" if record["repairs_validated"] else "REPAIRS_REFUTED_OR_NO_CANDIDATES"
    # References are only read after every candidate list and evaluation is fixed.
    # These file paths were already made public in an earlier post-hoc audit.
    prior_reference={"B2":"tqdm/std.py","B3":"cookiecutter/hooks.py"}
    for item in summary["cases"]:
        case=item["id"]
        rank_file=outdir/(case+"-ranking.json")
        if not rank_file.is_file():
            continue
        rank=json.loads(rank_file.read_text(encoding="utf8"))
        target=prior_reference[case]
        paths=[x["path"] for x in rank["ranked"]]
        item["posthoc_historic_fixed_file"]=target
        item["posthoc_fixed_file_rank"]=paths.index(target)+1 if target in paths else None
        item["alphabetic_baseline_rank"]=(
            rank["alphabetical_baseline"].index(target)+1
            if target in rank["alphabetical_baseline"] else None)
        item["target_file_in_top3"]=target in rank["top3"]
    summary["ranking_not_blind"]=True
    return summary

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",type=Path,required=True)
    parser.add_argument("--oracle-report",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    oracle=json.loads(args.oracle_report.read_text(encoding="utf8"))
    result=analyze(args.workspace,oracle,args.output_dir)
    (args.output_dir/"summary.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
        "pilot":result["experiment"],
        "status":[{"id":c["id"],"status":c["status"],"top3":c.get("ranked_top3"),
                   "historical_file_rank":c.get("posthoc_fixed_file_rank"),
                   "patches_tested":len(c.get("patches_tested",[])),
                   "repairs":c.get("repairs_validated")}
                  for c in result["cases"]]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
