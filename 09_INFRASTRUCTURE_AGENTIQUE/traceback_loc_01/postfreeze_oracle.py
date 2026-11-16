"""Post-freeze oracle check for OMEGA-TRACEBACK-LOC-01.

Loads committed rankings by SHA and only then checks historical fixed source
and runtime. May report partial oracle or failed reproduction; no repair claims.
"""
from __future__ import annotations
import argparse
import ast
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
from trace_localize import BUGGY_COMMIT,FIXED_COMMIT,PKG,TEST_PATH

def digest(content:bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def changed_functions(oldroot:Path, newroot:Path, data:dict) -> dict:
    by_file={}
    for entry in data["target_inventory"]:
        by_file.setdefault(entry["file"],[]).append(entry)
    bfiles=set(data["source_hashes"])
    ffiles={p.relative_to(newroot).as_posix()
            for p in (newroot/PKG).rglob("*.py")}
    modifications=[]
    unresolved=[]
    touched=set()
    for rel in sorted(bfiles|ffiles):
        p=oldroot/rel
        q=newroot/rel
        if not p.is_file() or not q.is_file():
            unresolved.append({"file":rel,"reason":"ADDED_OR_REMOVED"})
            continue
        old=p.read_text(encoding="utf-8").splitlines()
        fixed=q.read_text(encoding="utf-8").splitlines()
        if old==fixed:
            continue
        hunkcount=0
        targets_file=set()
        for op,i1,i2,j1,j2 in SequenceMatcher(
            a=old,b=fixed,autojunk=False).get_opcodes():
            if op=="equal":
                continue
            hunkcount+=1
            # Insertion at exact method entry/exit is intentionally ambiguous.
            if op=="insert":
                matched=[t for t in by_file.get(rel,[])
                         if t["line"] < (i1+1) < t["end_line"]]
                if len(matched)!=1:
                    unresolved.append({"file":rel,"reason":"INSERTION_AT_UNRESOLVED_BOUNDARY",
                                      "old_position":i1+1})
                    continue
            else:
                matched=[t for t in by_file.get(rel,[])
                         if t["line"]<=i2 and t["end_line"]>=i1+1]
                if len(matched)!=1:
                    unresolved.append({"file":rel,"reason":"MODIFICATION_UNRESOLVED_SCOPE",
                                       "old_interval":[i1+1,i2]})
                    continue
            key=matched[0]["key"]
            touched.add(key)
            targets_file.add(key)
        modifications.append({"file":rel,"hunks":hunkcount,
                              "identified_targets":sorted(targets_file)})
    return {"changed_files":modifications,"unresolved":unresolved,
            "oracle_targets":sorted(touched)}


def evaluate(manifest_bytes:bytes,expected_sha:str,
             buggy:Path,fixed:Path,fixed_log:str,fixed_exit:int)->dict:
    if digest(manifest_bytes)!=expected_sha:
        raise ValueError("RANK_MANIFEST_DRIFT")
    data=json.loads(manifest_bytes)
    if data.get("phase")!="BUGGY_ONLY_RANKING_FROZEN_BEFORE_FIXED":
        raise ValueError("UNFROZEN_RANKING")
    if data["buggy_commit"]!=BUGGY_COMMIT:
        raise ValueError("BUGGY_COMMIT_MISMATCH")
    if digest((buggy/TEST_PATH).read_bytes())!=data["test_sha256"]:
        raise ValueError("BUGGY_TEST_CHANGED")
    for file,expected in data["source_hashes"].items():
        if digest((buggy/file).read_bytes())!=expected:
            raise ValueError("BUGGY_SOURCE_CHANGED:"+file)
    targets=data["target_inventory"]
    if len({t["key"] for t in targets})!=len(targets):
        raise ValueError("RANK_INVENTORY_DUPLICATED")
    target_idx={x["key"]:x for x in targets}
    oracle=changed_functions(buggy,fixed,data)
    keys=oracle["oracle_targets"]
    scores={}
    for letter,attr in (("A_lexical","rank_a"),("B_trace","rank_b")):
        ranks=[target_idx[k][attr] for k in keys]
        best=min(ranks) if ranks else None
        scores[letter]={
          "best_rank":best,
          "hit_at_5":best is not None and best<=5,
          "hit_at_10":best is not None and best<=10,
          "hit_at_20":best is not None and best<=20,
        }
    tests=re.findall(r"Ran (\d+) tests? in ",fixed_log,re.I)
    fixed_ok=(fixed_exit==0 and bool(tests) and int(tests[-1])>0)
    buggy_has_verified_failure=(
        data["status"]=="BUGGY_TRACE_OBSERVED_NOT_YET_ORACLE_VERIFIED"
        and data["test_exit_code"]!=0
        and bool(data["ordered_unique_mapped_frame_keys"]))
    validated=bool(fixed_ok and buggy_has_verified_failure)
    if not validated:
        status="REPRODUCER_UNCONFIRMED"
    elif not keys:
        status="ORACLE_OUT_OF_SCOPE"
    elif oracle["unresolved"]:
        status="ORACLE_PARTIAL_NO_COMPARATIVE_CLAIM"
    else:
        a=scores["A_lexical"]["hit_at_10"]
        b=scores["B_trace"]["hit_at_10"]
        status=("LOCAL_IMPROVEMENT_ONE_CASE" if b and not a else
                "LOCAL_REGRESSION_ONE_CASE" if a and not b else
                "NO_DIFFERENCE")
    return {
      "experiment":"OMEGA-TRACEBACK-LOC-01",
      "phase":"POST_FREEZE_FIXED_RUNTIME_AND_SOURCE_ORACLE",
      "status":status,
      "buggy_commit":BUGGY_COMMIT,
      "fixed_commit":FIXED_COMMIT,
      "manifest_sha256":expected_sha,
      "frozen_buggy_status":data["status"],
      "buggy_test_exit_code":data["test_exit_code"],
      "fixed_test_exit_code":fixed_exit,
      "fixed_reported_test_counts":[int(v) for v in tests],
      "fixed_log_sha256":digest(fixed_log.encode("utf-8")),
      "differential_test_gate":validated,
      "oracle":oracle,
      "scores":scores,
      "target_count":len(targets),
      "same_top10_budget":True,
      "same_information_budget":False,
      "extra_runtime_evidence_for_B":True,
      "patch_generated":False,
      "model_called":False,
      "repair_correctness":None,
      "blind_generalization_demonstrated":False,
      "main_modified":False,
      "limitations":[
        "Differential full test module outcome is not necessarily the unique historical bug.",
        "Python 3.7-slim is not a reconstruction of all original dependencies.",
        "Traceback frames locate execution, not necessarily root cause.",
        "Any ambiguous oracle hunk precludes a certified win.",
        "Single case does not establish statistically general localization improvement.",
      ],
    }


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
    log=args.fixed_log.read_text(encoding="utf-8",errors="replace")
    result=evaluate(args.frozen_manifest.read_bytes(),args.expected_sha256,
                    args.buggy_checkout,args.fixed_checkout,log,args.fixed_exit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                      indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "gate":result["differential_test_gate"],
                      "oracle_targets":len(result["oracle"]["oracle_targets"]),
                      "unresolved":len(result["oracle"]["unresolved"]),
                      "scores":result["scores"],
                      "sha256":digest(args.output.read_bytes())},sort_keys=True))


if __name__=="__main__":
    main()
