"""P5-OBS-03 — empirical GitHub evidence lineage and replay audit.

The 12 PRs were previously analyzed (P5-PR29): not blind holdout.
All live observations come from GITHUB.COM. Repeated endpoint agreement is
same-provider consistency, NOT independently confirmed truth.
No provider-failure labels are invented and no tool call is made at replay.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARTS=tuple(HERE/f"obs03_fresh_pr_part{i}.json" for i in range(3))
FULL=tuple(HERE/f"obs03_real_full_filenames_part{i}.json" for i in range(3))
OLD=HERE/"live_github_pr_gate_observations_2026-11-11.json"
STATUS="REAL_SINGLE_PROVIDER_REOBSERVATION_NO_INDEPENDENT_VALIDATION"
PROVIDER="github.com"


def test_filename(path):
    """The exact syntactic criterion preregistered for P5-PR29."""
    if not isinstance(path,str) or not path:
        raise ValueError("invalid changed filename")
    components=path.split("/")
    last=components[-1]
    return ("test" in components or "tests" in components
            or last.startswith("test_") or last.endswith("_test.py"))


def _load(paths):
    return [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]


def _unique_rows(groups,required_parts):
    seen=set()
    result={}
    for idx,group in enumerate(groups):
        if group.get("protocol")!="P5-OBS-03" or group.get("part")!=idx:
            raise ValueError("bad capture part order or protocol")
        for row in group.get("rows",[]):
            key=(row["repo"],row["number"])
            if key in seen:
                raise ValueError("duplicate PR observation")
            seen.add(key)
            result[key]=row
    if len(result)!=required_parts*4:
        raise ValueError("missing captures; fail closed")
    return result


def provenance_certificate(observed,filenames):
    """Only claim what three GitHub endpoints and a re-read permit us to know."""
    m=observed["metadata"]
    a=observed["alternate"]
    fs=observed["filenames"]
    providers={m.get("provider"),a.get("provider"),fs.get("provider"),
               filenames.get("provider")}
    if providers!={PROVIDER}:
        raise ValueError("unknown provider, cannot infer independence")
    if {m["endpoint"],a["endpoint"],fs["endpoint"]}!={
        "get_pr_info","fetch_pr","list_pr_changed_filenames"}:
        raise ValueError("changed endpoint schema")
    if filenames.get("endpoint")!="list_pr_changed_filenames":
        raise ValueError("changed filename provenance")
    paths=filenames["filenames"]
    if not isinstance(paths,list) or any(not isinstance(p,str) for p in paths):
        raise ValueError("missing original file paths")
    matching=[p for p in paths if test_filename(p)]
    touched=bool(matching)
    if fs.get("count")!=len(paths) or fs.get("touched_tests")!=touched:
        # An intervening change in PR may cause this: no silent reconciliation.
        return {"status":"CROSS_READ_FILE_PATH_DRIFT",
                "independent_providers":1,
                "test_changed_recomputed":touched,
                "matching_test_paths":matching,
                "correctness_certified_independently":False}
    if (m.get("merged") is None or a.get("merged") is None
            or not m.get("head_sha") or not a.get("head_sha")):
        return {"status":"INSUFFICIENT_EVIDENCE",
                "independent_providers":1,
                "test_changed_recomputed":touched,
                "matching_test_paths":matching,
                "correctness_certified_independently":False}
    if m["merged"]!=a["merged"] or m["head_sha"]!=a["head_sha"]:
        return {"status":"CROSS_ENDPOINT_CONFLICT",
                "independent_providers":1,
                "test_changed_recomputed":touched,
                "matching_test_paths":matching,
                "correctness_certified_independently":False}
    expected=bool(m["merged"] and touched)
    return {
        "status":"SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED",
        "independent_providers":1,
        "same_provider_views_agree":True,
        "full_filenames_sha256":sha256(json.dumps(
            paths,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(),
        "test_changed_recomputed":touched,
        "matching_test_paths":matching,
        "merged_from_metadata":m["merged"],
        "observed_decision_from_github_fields":expected,
        "head_sha_same_on_two_metadata_reads":m["head_sha"],
        "correctness_certified_independently":False,
        "race_warning":"file-list endpoint is unpinned; metadata agreed but a concurrent mutation is not ruled out",
    }


def replay_controls(rows):
    """Counterfactual read counts on fully acquired data, no network savings."""
    if any(r["cert"]["status"]!="SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED"
           for r in rows):
        return {"status":"ABSTAIN_SOME_PR_UNRESOLVED"}
    plans=(("merged_first","merged","touched"),("files_first","touched","merged"))
    results={}
    for name,first,second in plans:
        calls=0
        decisions=[]
        for row in rows:
            m=row["cert"]["merged_from_metadata"]
            t=row["cert"]["test_changed_recomputed"]
            vals={"merged":m,"touched":t}
            calls+=1
            verdict=False
            if vals[first]:
                calls+=1
                verdict=bool(vals[second])
            decisions.append(verdict)
        results[name]={"correct":sum(decisions[i]==r["cert"]["observed_decision_from_github_fields"]
                                      for i,r in enumerate(rows)),
                       "logical_calls":calls}
    truth=[r["cert"]["observed_decision_from_github_fields"] for r in rows]
    results["fixed_both"]={"correct":len(rows),"logical_calls":2*len(rows)}
    results["reject_all"]={"correct":sum(not x for x in truth),"logical_calls":0}
    return {"status":"REPLAY_FROM_RECORDED_FIELDS_NOT_ACTUAL_SAVED_CALLS",
            "policies":results}


def run():
    groups=_load(PARTS)
    full=_load(FULL)
    partial=_unique_rows(groups,3)
    complete=_unique_rows(full,3)
    if set(partial)!=set(complete):
        raise ValueError("different PR samples in two readings")
    old=json.loads(OLD.read_text(encoding="utf-8"))
    baseline={(r["repo"],r["number"]):r for r in old["cases"]}
    if set(baseline)!=set(partial):
        raise ValueError("PR cohort was changed")
    rows=[]
    for key in baseline:
        capture=partial[key]
        paths=complete[key]
        if (capture["repo"],capture["number"])!=(paths["repo"],paths["number"]):
            raise ValueError("bad source alignment")
        cert=provenance_certificate(capture,paths)
        hist=baseline[key]
        original=capture["previous"]
        if (original["merged"]!=hist["merged"] or
            original["touched_tests"]!=hist["touched_tests"] or
            original["head_sha"]!=hist["head_sha"]):
            raise ValueError("historical snapshot altered")
        rows.append({
            "repo":key[0],"number":key[1],
            "url":hist["url"],
            "cert":cert,
            "old_merged":hist["merged"],
            "old_touched_tests":hist["touched_tests"],
            "old_head_sha":hist["head_sha"],
            "metadata_merged":capture["metadata"]["merged"],
            "metadata_alt_merged":capture["alternate"]["merged"],
            "head_changed_since_11_nov":(
                capture["metadata"]["head_sha"]!=hist["head_sha"]
                if capture["metadata"]["head_sha"] else None),
            "merged_changed_since_11_nov":(
                capture["metadata"]["merged"]!=hist["merged"]
                if capture["metadata"]["merged"] is not None else None),
            "changed_files_now":paths["filenames"],
        })
    certs=Counter(x["cert"]["status"] for x in rows)
    replays=replay_controls(rows)
    return {
        "protocol":"P5-OBS-03",
        "status":STATUS,
        "prereg_commit":"6f9a63fef351457c0d62f15f9588f2048864d73a",
        "observation_date":"2026-11-12",
        "historical_source":"P5-PR29 observed 2026-11-11, already analyzed",
        "real_prs":len(rows),
        "fresh_github_endpoint_observations":3*len(rows),
        "additional_full_filenames_rereads":len(rows),
        "providers_seen":[PROVIDER],
        "independent_provider_count":1,
        "independent_external_corroborations":0,
        "certificates":dict(certs),
        "head_drift_detected":sum(x["head_changed_since_11_nov"] is True for x in rows),
        "merged_drift_detected":sum(x["merged_changed_since_11_nov"] is True for x in rows),
        "replay_controls":replays,
        "cases":rows,
        "limitations":[
            "Same provider for all three endpoints: agreement is not independent proof",
            "Non-transactional changed-file reads are not commit-SHA pinned",
            "Synthetic provenance_cases fixtures are not real provider errors",
            "Re-reading 12 preselected public PRs is not a fresh holdout",
            "Counterfactual policy read counts do not represent API calls actually avoided",
            "Syntactic test path is not evidence of runnable test quality",
            "No actual independent-provider failures or real model feedback collected",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    opt=parser.parse_args()
    result=run()
    if opt.output:
        opt.output.parent.mkdir(parents=True,exist_ok=True)
        opt.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                             indent=2)+"\n",encoding="utf-8")
    print("P5_OBS03_SOURCE_AUDIT",json.dumps({
        "status":result["status"],"real_prs":result["real_prs"],
        "recorded_observations":result["fresh_github_endpoint_observations"],
        "provider_count":result["independent_provider_count"],
        "independent_external_corroborations":result["independent_external_corroborations"],
        "certificates":result["certificates"],
        "head_drift":result["head_drift_detected"],
        "merged_drift":result["merged_drift_detected"],
        "replayed_policies":result["replay_controls"],
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
