"""Posthoc replay of Qwen's THREE ORIGINAL, pre-oracle textual IDs.

The original fixed-code oracle had already run when this parser was repaired.
This is not an independent experiment or retroactive prospective success.
No Qwen calls, no new candidates, no access to corrected production files.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from abc_core import ARMS, extract_llama_cli_id, sha
from abc_fetch import fetch
from abc_oracle import verify_commitment
from abc_runner import build_project_image, test_candidate

ORIGINAL_RUN=43811742090
ORIGINAL_MANIFEST_SHA="80e5a418ec33a831dfc11658f7e3362bfefc5489f73ce13be570bdcd2026ac77"


def replay(cohort_file, frozen_file, output):
    cohort=json.loads(cohort_file.read_text(encoding="utf8"))
    frozen=json.loads(frozen_file.read_text(encoding="utf8"))
    commitment=verify_commitment(frozen,cohort)
    if commitment!=ORIGINAL_MANIFEST_SHA or frozen.get("new_model_calls")!=3:
        raise ValueError("wrong archived pre-oracle source or model-call count")
    selected=[]
    for case,row in zip(cohort["cases"], frozen["cases"]):
        meta=row.get("model_selection",{})
        if not meta.get("model_called"):
            continue
        if meta.get("candidate_id") is not None or meta.get("model_exit")!=0:
            raise ValueError("original decoder unexpectedly selected or model failed")
        allowed=row.get("orders",{}).get(ARMS[2],[])
        ident=extract_llama_cli_id(meta.get("returned_tail",""), allowed)
        if not ident:
            raise ValueError("strict replay cannot retrieve a unique allowed ID")
        by_id={p["id"]:p for p in row["candidates"]}
        if ident not in by_id:
            raise ValueError("Qwen ID not in original candidate pool")
        selected.append((case,row,ident,by_id[ident]))
    if [c["id"] for c,_,_,_ in selected] != ["N1","N2","N4"]:
        raise ValueError("different replayed case inventory")
    from tempfile import TemporaryDirectory
    evidence=[]
    with TemporaryDirectory(prefix="omega-new5-replay-ids-") as temp:
        root=Path(temp)
        buggy=root/"buggy"
        tests=root/"tests"
        fetch(cohort_file, buggy, tests, "buggy-only")
        for case,row,ident,candidate in selected:
            image,build=build_project_image(case,buggy/case["id"])
            item={
                "id":case["id"],"original_model_raw_sha256":row["model_selection"]["raw_sha256"],
                "original_candidate_id":ident,"patch_sha256":candidate["modified_sha256"],
                "original_source_sha256":candidate["source_sha256"],"build":build,
                "original_C_abstained_due_to_cli_decoding":True,
                "new_model_calls":0
            }
            if build["exit"]==0:
                got=test_candidate(image,case,buggy/case["id"],tests/(case["id"]+".py"),candidate)
                item["public_target_replay"]={k:v for k,v in got.items() if k!="trace_log"}
                item["status"]="POSTHOC_PATCH_PASSES_TARGET" if got["status"]=="PASS" else (
                    "POSTHOC_PATCH_FAILS_TARGET" if got["status"]=="FAIL"
                    else "POSTHOC_ENVIRONMENT_BLOCKED")
            else:
                item["status"]="POSTHOC_DEPENDENCY_BUILD_BLOCKED"
            evidence.append(item)
    result={
        "experiment":cohort["experiment"],"phase":"POSTHOC_REPLAY_PREORACLE_QWEN_ID_OUTPUTS",
        "first_run":ORIGINAL_RUN,"original_manifest_sha256":commitment,
        "original_model_calls":3,"additional_model_calls":0,
        "distinct_original_model_choices":len(evidence),
        "additional_patch_tests":sum("public_target_replay" in c for c in evidence),
        "original_verdict_unchanged":"NO_DEMONSTRATED_ADVANTAGE",
        "independent_blind_holdout":False,
        "reason_for_posthoc":"Original CLI footer parser lost valid ID outputs; fixed source already exposed before decoder repair.",
        "case_results":evidence}
    output.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"phase":result["phase"],"additional_model_calls":0,
                      "selected":[{"id":c["id"],"candidate":c["original_candidate_id"],
                                   "status":c["status"]} for c in evidence]},indent=2))
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",required=True,type=Path)
    p.add_argument("--original-freeze",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    replay(a.cohort,a.original_freeze,a.output)


if __name__=="__main__":
    main()
