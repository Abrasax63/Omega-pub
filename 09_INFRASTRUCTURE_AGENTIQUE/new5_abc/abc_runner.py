"""Real buggy-only A/B/C patch selection, with no access to corrected source.

Prerequisite: five exact buggy Git checkouts and the public regression test FILES,
fetched individually from fixed SHAs. Fetching an entire corrected repository is
forbidden until AFTER this manifest and the candidate choices are frozen.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from abc_core import ARMS, CASE_IDS, MAX_PER_ARM, freeze_case, final_model_order, extract_llama_cli_id, verify_manifest
from abc_core import rewrite, sha

MODEL_HASH = "724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
MODEL_CALLS_PER_REPRODUCED_BUG = 1
MODEL_NEW_TOKENS = 128
MAX_PATCH_EXEC_SECONDS = 75
PROJECT_EXTRA = {"tqdm":("nose",), "cookiecutter":("pytest-cov<4",),
                 "httpie":("requests","pytest-httpbin==1.0.2")}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def build_project_image(case, buggy_root):
    ident=case["id"]
    tag="omega-new5-"+ident.lower()+":local"
    with tempfile.TemporaryDirectory(prefix="omega-new5-builder-") as tmp:
        df=Path(tmp)/"Dockerfile"
        df.write_text(
            "FROM python:"+case["python"]+"-slim\n"
            "WORKDIR /src\n"
            "COPY . /src\n"
            "RUN python -m pip install --disable-pip-version-check --no-cache-dir "
            "'pip<22' 'setuptools<60' 'wheel<1' && "
            "python -m pip install --disable-pip-version-check --no-cache-dir "
            "'pytest<7' " + " ".join("'"+req+"'" for req in PROJECT_EXTRA[case["project"]]) + " -e /src\n"
            "ENV PYTHONDONTWRITEBYTECODE=1\n",encoding="utf8")
        command=["docker","build","--pull=false","-f",str(df),"-t",tag,str(buggy_root)]
        try:
            proc=subprocess.run(command,capture_output=True,text=True,timeout=420)
            return tag, {"exit":proc.returncode,
                         "sha256":sha_bytes((proc.stdout+proc.stderr).encode()),
                         "tail":(proc.stdout+proc.stderr)[-2000:]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            return tag, {"exit":-1,"tail":str(exc),"sha256":None}


def run_regression(image, case, source_root, test_file, profile_file=None, patch_file=None):
    """Execute the authentic upstream test, never on the host Python interpreter."""
    source_root=Path(source_root).resolve()
    test_file=Path(test_file).resolve()
    cmd=[
        "docker","run","--rm","--network","none","--read-only",
        "--cap-drop","ALL","--security-opt","no-new-privileges",
        "--pids-limit","96","--memory","1024m","--memory-swap","1024m",
        "--cpus","1","--user","65534:65534",
        "--tmpfs","/tmp:rw,exec,nosuid,nodev,size=256m,mode=1777",
        "--mount",f"type=bind,src={source_root},dst=/origin,readonly",
        "--mount",f"type=bind,src={test_file},dst=/omega-test.py,readonly",
    ]
    if profile_file:
        cmd.extend(["--mount",f"type=bind,src={Path(profile_file).resolve()},dst=/opt/sitecustomize.py,readonly",
                    "-e","PYTHONPATH=/opt:/tmp/work"])
        cmd.extend(["-e","OMEGA_TRACE_ROOT=/tmp/work/"+case["project"]])
    else:
        cmd.extend(["-e","PYTHONPATH=/tmp/work"])
    if patch_file is not None:
        # MountedPatch intentionally wraps its path; Path(MountedPatch) has no __fspath__.
        actual_patch_path = patch_file.resolve() if isinstance(patch_file, MountedPatch) else Path(patch_file).resolve()
        cmd.extend(["--mount",f"type=bind,src={actual_patch_path},dst=/omega-patch.py,readonly"])
    cmd.extend(["-e","HOME=/tmp","-e","PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                "-e","PYTHONDONTWRITEBYTECODE=1",image])
    # Every path here originates from the preregistered case or verified patch
    # and must be restricted to a relative path (no shell metacharacters).
    reltest=case["test_file"]
    pytest_target=case["test_id"]
    if not re.fullmatch(r"[a-zA-Z0-9_./-]+",reltest):
        raise ValueError("invalid registered test path")
    if not re.fullmatch(r"[a-zA-Z0-9_./:-]+",pytest_target):
        raise ValueError("invalid registered pytest node")
    script=("set -eu; mkdir -p /tmp/work; cp -R /origin/. /tmp/work/; "
            "mkdir -p /tmp/work/$(dirname "+reltest+"); "
            "cp /omega-test.py /tmp/work/"+reltest+"; "
            "cd /tmp/work; ")
    if patch_file:
        patchrel=patch_file.registered_patch_path
        if not re.fullmatch(r"[a-zA-Z0-9_./-]+",patchrel) or ".." in Path(patchrel).parts:
            raise ValueError("invalid patch path")
        script+="cp /omega-patch.py /tmp/work/"+patchrel+"; "
    # pytest's automatic plugin loading is disabled for determinism. Enable
    # only required, already-installed historical plugins explicitly.
    explicit_plugins = ("-p pytest_cov " if case["project"]=="cookiecutter" else "")
    script+="python -m pytest -q -s -p no:cacheprovider "+explicit_plugins+"--maxfail=1 "+pytest_target
    cmd.extend(["sh","-c",script])
    started=time.perf_counter_ns()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=MAX_PATCH_EXEC_SECONDS)
        combined=p.stdout+"\n"+p.stderr
        # The profiler appends potentially huge JSON. Keep full trace privately
        # for ranking but never submit the trace blob as the LLM failure message.
        from abc_core import parse_call_trace
        trace_marker = "OMEGA_CALL_TRACE_V1="
        diagnostic = combined.split(trace_marker, 1)[0] if profile_file else combined
        duration=max(1,(time.perf_counter_ns()-started)//1_000_000)
        # Pytest error vs authentic assertion FAIL are different statuses.
        if p.returncode==0:
            status="PASS"
        elif re.search(r"(?m)([1-9]\d* failed(?:,|\s)|FAILED\s+[\w/.:]+|AssertionError)",combined):
            status="FAIL"
        elif p.returncode==5:
            status="NO_TEST_COLLECTED"
        else:
            status="ENVIRONMENT_ERROR"
        return {"status":status,"exit":p.returncode,"duration_ms":duration,
                "log_sha256":sha_bytes(combined.encode()),"log_tail":diagnostic[-1800:],
                "trace_log":combined if profile_file else None}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {"status":"ENVIRONMENT_ERROR","error":str(exc)[:400],
                "duration_ms":max(1,(time.perf_counter_ns()-started)//1_000_000),
                "log_sha256":None,"trace_log":None}


class MountedPatch:
    """Path object carrying the validated repository-relative source pathname."""
    def __init__(self, local_file, registered_patch_path):
        self.local_file=Path(local_file)
        self.registered_patch_path=registered_patch_path
    def resolve(self):
        return self.local_file.resolve()


def test_candidate(image,case,buggy_root,test_file,candidate):
    rel=candidate["path"]
    source_path=(Path(buggy_root)/rel).resolve()
    if not source_path.is_relative_to(Path(buggy_root).resolve()):
        raise ValueError("unsafe patch path")
    original=source_path.read_text(encoding="utf8",errors="replace")
    if sha(original)!=candidate["source_sha256"]:
        raise RuntimeError("changed buggy source SHA")
    edited=rewrite(original,{x["line"]:x["after"] for x in candidate["changes"]})
    if sha(edited)!=candidate["modified_sha256"]:
        raise RuntimeError("changed candidate source SHA")
    with tempfile.TemporaryDirectory(prefix="omega-new5-source-") as tmp:
        patch=Path(tmp)/"patch.py"
        patch.write_text(edited,encoding="utf8")
        os.chmod(tmp,0o755)
        os.chmod(patch,0o644)
        return run_regression(image,case,buggy_root,test_file,
                              patch_file=MountedPatch(patch,rel))


def ask_qwen(cli,weights,case,row,public_failure):
    shortlist=row["orders"]["C_trace_symbolic_plus_qwen"]
    if not shortlist:
        return {"status":"NO_TRACE_NO_MODEL_CALL","model_called":False,"candidate_id":None}
    by_id={c["id"]:c for c in row["candidates"]}
    examples=[]
    for cid in shortlist:
        c=by_id[cid]
        change="; ".join(x["before"].strip()[:90]+" -> "+x["after"].strip()[:90]
                         for x in c["changes"])
        examples.append(cid+" "+c["path"]+" "+c["function"]+" "+change)
    prompt=("<|im_start|>system\nYou are a code repair candidate selector, "
            "not a code generator. Return ONLY one ID from the proposed list. "
            "No explanation, no other characters.\n<|im_end|>\n"
            "<|im_start|>user\nSelect the most plausible one-line/two-line patch "
            "for the following public failing test. The historical repaired "
            "source is unavailable. You have exactly the same candidates as "
            "the symbolic reference.\nFailure:\n"+public_failure[-500:]
            +"\nCandidates:\n"+"\n".join(examples)
            +"\nReturn one exact ID.\n<|im_end|>\n<|im_start|>assistant\n")
    command=[str(cli),"-m",str(weights),"-p",prompt,"-n",str(MODEL_NEW_TOKENS),
             "-c","4096","-t","4","--temp","0","--seed","1626"]
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=250)
    except (OSError,subprocess.TimeoutExpired) as e:
        return {"status":"MODEL_INFRA_ERROR","model_called":True,
                "error":str(e)[:300],"candidate_id":None,
                "prompt_sha256":sha_bytes(prompt.encode())}
    raw=result.stdout
    # CLI prints the prompt and a performance/status footer. Do not confuse
    # the footer with model chatter; validate one answer against frozen IDs.
    choice=extract_llama_cli_id(raw,shortlist) if result.returncode==0 else None
    tail=raw[-500:].strip()
    return {"status":"SELECTED" if choice else "ABSTAINED_OR_ERROR",
            "model_called":True,"model_exit":result.returncode,
            "candidate_id":choice,
            "prompt_sha256":sha_bytes(prompt.encode()),
            "raw_sha256":sha_bytes(raw.encode()),
            "returned_tail":tail[-500:],
            "max_output_tokens":MODEL_NEW_TOKENS}


def evaluate_orders(image,case,buggy_root,test_file,row,model_choice):
    answers={}
    executed={}
    pool={p["id"]:p for p in row["candidates"]}
    orders=dict(row["orders"])
    orders[ARMS[2]]=final_model_order(orders[ARMS[1]],
                                      orders[ARMS[2]],model_choice)
    for arm in ARMS:
        rows=[]
        chosen=None
        for cid in orders.get(arm,[])[:MAX_PER_ARM]:
            if cid in executed:
                result=dict(executed[cid],reused_run=True)
            else:
                result=test_candidate(image,case,buggy_root,test_file,pool[cid])
                executed[cid]=result
                result=dict(result,reused_run=False)
            rows.append({"candidate_id":cid,"test_status":result["status"],
                         "duration_ms":result.get("duration_ms"),
                         "reused_run":result["reused_run"],
                         "log_sha256":result.get("log_sha256")})
            if result["status"]=="PASS":
                chosen=cid
                break
            if result["status"] in ("ENVIRONMENT_ERROR","NO_TEST_COLLECTED"):
                break
        answers[arm]={"ranked_patch_ids":orders.get(arm,[]),
                      "actual_attempts":rows,"logical_tests_consumed":len(rows),
                      "selected_patch_id":chosen,
                      "status":"PUBLIC_TEST_PASS_PENDING_ORACLE" if chosen
                      else ("NO_PATCH_VALIDATED" if rows else "ABSTAINED")}
    return answers, {"distinct_pytest_runs":len(executed),
                     "per_candidate_status":{k:v["status"] for k,v in executed.items()}}


def run_freeze(cohort_path,buggy_dir,tests_dir,out,cli=None,weights=None):
    cohort=json.loads(cohort_path.read_text(encoding="utf8"))
    if len(cohort["cases"])!=5:
        raise ValueError("incorrect frozen cohort length")
    if weights:
        if sha_bytes(Path(weights).read_bytes())!=MODEL_HASH:
            raise ValueError("unpinned model weights")
    results=[]
    for case in cohort["cases"]:
        ident=case["id"]
        root=(buggy_dir/ident).resolve()
        test=tests_dir/(ident+".py")
        actual_sha=subprocess.check_output(
            ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
        if actual_sha!=case["buggy_sha"]:
            raise RuntimeError("wrong buggy SHA for "+ident)
        test_sha=sha_bytes(test.read_bytes())
        image,build=build_project_image(case,root)
        item={"id":ident,"buggy_sha":actual_sha,"test_only_sha256":test_sha,
              "dependency_build":build,"fixed_source_seen":False,
              "candidates":[],"candidate_count":0,"orders":{},
              "model_selection":{"model_called":False},"arms":{}}
        if build["exit"]!=0:
            item["status"]="ENVIRONMENT_BLOCKED"
            results.append(item)
            continue
        trace_file=Path(__file__).resolve().parents[1]/"trace_repair"/"sitecustomize.py"
        bug_test=run_regression(image,case,root,test,profile_file=trace_file)
        item["buggy_test"]={k:v for k,v in bug_test.items() if k!="trace_log"}
        if bug_test["status"]!="FAIL":
            item["status"]="BUG_NOT_REPRODUCED" if bug_test["status"]=="PASS" else "ENVIRONMENT_BLOCKED"
            results.append(item)
            continue
        freeze=freeze_case(case,root,bug_test.get("trace_log") or "",
                           test.read_text(encoding="utf8",errors="replace"))
        item.update({k:v for k,v in freeze.items() if k not in ("id","buggy_sha")})
        if not freeze.get("candidate_count") or not freeze.get("trace_verified"):
            item["status"]="NO_CANDIDATES_OR_TRACE"
            results.append(item)
            continue
        if cli and weights:
            model=ask_qwen(cli,weights,case,freeze,bug_test["log_tail"])
        else:
            model={"status":"NO_MODEL_CONFIGURED","model_called":False,"candidate_id":None}
        item["model_selection"]=model
        answers,execution=evaluate_orders(image,case,root,test,freeze,
                                           model.get("candidate_id"))
        item["arms"]=answers
        item["executions"]=execution
        item["status"]="CANDIDATES_FROZEN_BEFORE_FIXED_SOURCE"
        results.append(item)
    report={"experiment":cohort["experiment"],
            "phase":"ABC_SELECTION_BUGGY_ONLY",
            "cases":results,"fixed_source_seen":False,"fixed_diff_seen":False,
            "model_weight_sha256":MODEL_HASH if weights else None,
            "new_model_calls":sum(c["model_selection"].get("model_called",False)
                                  for c in results),
            "external_oracle_opened":False,
            "selection_budget_max_per_arm":MAX_PER_ARM,
            "source_commit":os.environ.get("GITHUB_SHA","LOCAL")}
    report["selection_sha256"]=sha(json.dumps(report,sort_keys=True,ensure_ascii=False))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
                   encoding="utf8")
    print(json.dumps({"selection_sha256":report["selection_sha256"],
                      "cases":[{"id":c["id"],"status":c.get("status"),
                                "candidate_count":c.get("candidate_count"),
                                "A":c.get("arms",{}).get(ARMS[0],{}).get("selected_patch_id"),
                                "B":c.get("arms",{}).get(ARMS[1],{}).get("selected_patch_id"),
                                "C":c.get("arms",{}).get(ARMS[2],{}).get("selected_patch_id")}
                               for c in results]},indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",type=Path,required=True)
    p.add_argument("--buggy-dir",type=Path,required=True)
    p.add_argument("--tests-dir",type=Path,required=True)
    p.add_argument("--llama-cli",type=Path)
    p.add_argument("--model-file",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    run_freeze(args.cohort,args.buggy_dir,args.tests_dir,args.output,
               cli=args.llama_cli,weights=args.model_file)


if __name__=="__main__":
    main()
