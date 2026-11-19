#!/usr/bin/env python3
"""Reader22: bibliographic metadata audits anchored to known Omega source lines.

Only DOI/title/year metadata. No proof validation, novelty assessment or
autonomous promotion. 3 public Crossref HTTP GETs through Reader21 allowlist.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unicodedata

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"reader_bridge21"))
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
from agent_tools import dispatch
from read import safe_read

FROZEN=HERE/"REFS_FROZEN.json"
EXPECTED="bf10028da39306aedec6c4e1567d501172552258"
MAX_REFERENCES=3
BASELINE="NO_EXTERNAL_METADATA"
MATCH="MATCHED_BIBLIOGRAPHIC_METADATA"
MISSING="NO_EXACT_METADATA_MATCH"
INDETERMINATE="INDETERMINATE_REMOTE"
AMBIGUOUS="AMBIGUOUS_METADATA"


def norm(s: str) -> str:
    d=unicodedata.normalize("NFKD",s).casefold()
    return " ".join("".join(c if c.isalnum() else " " for c in d).split())


def remote_query(title: str) -> str:
    # Only title characters, never source-authored URL; fixed provider controls.
    query=" ".join(re.findall(r"[A-Za-z0-9]+",title))
    if not 3 <= len(query) <= 120:
        raise ValueError("BIB_QUERY_OUTSIDE_SAFE_LIMITS")
    return query


def issued_year(issued) -> int|None:
    if not isinstance(issued,dict):
        return None
    parts=issued.get("date-parts")
    if not isinstance(parts,list) or not parts or not isinstance(parts[0],list) or not parts[0]:
        return None
    n=parts[0][0]
    return n if isinstance(n,int) and not isinstance(n,bool) and 1500<=n<=2100 else None


def compare_metadata(ref: dict, works: list[dict]) -> dict:
    """Crossref metadata-only; exact normalized title and issued year or abstain."""
    hits=[]
    for item in works:
        if not isinstance(item,dict):
            continue
        title=item.get("title")
        doi=item.get("doi")
        if not isinstance(title,str) or not isinstance(doi,str):
            continue
        if norm(title)==norm(ref["title"]) and issued_year(item.get("issued"))==ref["year"]:
            hits.append({"doi":doi,"title":title,"issued_year":ref["year"],
                         "metadata_only":True,"mathematics_verified":False})
    doi_index={x["doi"].casefold():x for x in hits}
    if len(doi_index)==1:
        return {"status":MATCH,"match":next(iter(doi_index.values())),"matching_dois":1,
                "mathematical_theorem_proved":False,"novelty_proved":False}
    if len(doi_index)>1:
        return {"status":AMBIGUOUS,"match":None,"matching_dois":len(doi_index),
                "mathematical_theorem_proved":False,"novelty_proved":False}
    return {"status":MISSING,"match":None,"matching_dois":0,
            "mathematical_theorem_proved":False,"novelty_proved":False}


def read_manifest() -> dict:
    data=json.loads(FROZEN.read_text(encoding="utf-8"))
    if data["source_git_blob"]!=EXPECTED or len(data["references"])!=MAX_REFERENCES:
        raise ValueError("REFERENCE_MANIFEST_DRIFT")
    if data.get("independent_human_annotations") or data.get("mathematical_assertions_verified"):
        raise ValueError("FALSE_SCIENTIFIC_ANNOTATION")
    return data


def source_locs(raw: bytes, refs: list[dict]) -> dict[str,dict]:
    lines=raw.decode("utf-8").splitlines()
    try:
        section=lines.index("## Références clés")
    except ValueError:
        raise ValueError("MISSING_FROZEN_BIBLIOGRAPHIC_SECTION")
    result={}
    for ref in refs:
        matches=[(i+1,line) for i,line in enumerate(lines)
                 if i>section and ref["title"].casefold() in line.casefold()
                 and ref["source_author"].casefold() in line.casefold()
                 and str(ref["year"]) in line]
        if len(matches)!=1:
            raise ValueError("MISSING_OR_AMBIGUOUS_REFERENCE_IN_SOURCE_"+ref["id"])
        n,lit=matches[0]
        result[ref["id"]]={"line":n,"literal":lit}
    return result


def decoy_of(manifest:dict, rule:dict) -> dict:
    original=next(r for r in manifest["references"] if r["id"]==rule["from"])
    fake=deepcopy(original)
    if rule["mutate"]=="year_plus_one":
        fake["year"]=fake["year"]+1
    elif rule["mutate"]=="title":
        fake["title"]=rule["title"]
    else:
        raise ValueError("UNREGISTERED_NEGATIVE_MUTATION")
    return fake


def evaluate(transport=None) -> dict:
    manifest=read_manifest()
    source=ROOT/manifest["source_path"]
    raw=safe_read(source,EXPECTED)
    evidence=source_locs(raw,manifest["references"])
    results=[]; responses={}
    for ref in manifest["references"]:
        query=remote_query(ref["title"])
        outcome=dispatch("search_bibliography",{"query":query},transport=transport)
        if outcome["max_network_calls"]!=1 or not outcome["read_only"] or outcome["theorem_certificate"]:
            raise AssertionError("AGENT_WEB_CAPABILITY_BYPASS")
        result=outcome["result"]
        if result["http_requests_max"]!=1 or len(result["results"])!=1:
            raise AssertionError("WEB_PROVIDER_BUDGET_DRIFT")
        remote=result["results"][0]
        if remote["status"]=="WEB_FETCHED_UNTRUSTED":
            works=remote.get("works",[])
            verdict=compare_metadata(ref,works)
            responses[ref["id"]]=works
        else:
            works=[]
            verdict={"status":INDETERMINATE,"match":None,"matching_dois":0,
                     "mathematical_theorem_proved":False,"novelty_proved":False}
        results.append({
            "ref_id":ref["id"],"source_evidence":evidence[ref["id"]],
            "expected_title":ref["title"],"expected_year":ref["year"],
            "baseline_without_web":BASELINE,
            "web_status":remote["status"],
            "remote_error_type":remote.get("error_type"),
            "remote_error":remote.get("error"),
            "remote_body_sha256":remote.get("body_sha256"),
            "retrieved_utc":remote.get("retrieved_utc"),
            "query_url":remote["url"],
            "returned_candidate_count":len(works),
            "verification":verdict,
            "web_is_untrusted":True,"automatically_certified":False,
        })
    controls=[]
    for rule in manifest["decoys"]:
        fake=decoy_of(manifest,rule)
        if rule["from"] in responses:
            check=compare_metadata(fake,responses[rule["from"]])
            controls.append({"id":rule["id"],"mutation":rule["mutate"],
                             "status":check["status"],"should_reject":check["status"]!=MATCH})
        else:
            controls.append({"id":rule["id"],"mutation":rule["mutate"],
                             "status":INDETERMINATE,"should_reject":None})
    confirmed=sum(r["verification"]["status"]==MATCH for r in results)
    live=sum(r["web_status"]=="WEB_FETCHED_UNTRUSTED" for r in results)
    valid_controls=sum(x["should_reject"] is True for x in controls)
    status=("PASS_METADATA_AND_NEGATIVE_CONTROLS"
            if confirmed>=2 and live==3 and valid_controls==3 else
            "INDETERMINATE_REMOTE"
            if live<3 else "FAIL_OR_INSUFFICIENT_METADATA")
    return {
        "experiment":"OMEGA_READER22_WEB_CROSSREF_BIBLIOGRAPHIC_AUDIT",
        "calibration_posthoc_not_holdout":True,
        "source_git_blob":EXPECTED,"reference_count":len(results),
        "max_http_requests":3,"live_completed":live,
        "metadata_title_year_matches":confirmed,
        "negative_controls_refused":valid_controls,
        "without_web_external_doi_verification":0,
        "novelty_or_priority_established":False,
        "source_theorem_mathematically_verified":False,
        "automatic_scientific_promotions":0,
        "result_status":status,"results":results,"negative_controls":controls,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report={"result_status":"NOT_RUN"}
    try:
        report=evaluate()
    except Exception as e:
        report={"result_status":"TECHNICAL_FAILURE","error":str(e)[:1000],
                "automatic_scientific_promotions":0}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BIB_AUDIT",report["result_status"],
          "matches",report.get("metadata_title_year_matches"),
          "live",report.get("live_completed"),
          "decoy_rejects",report.get("negative_controls_refused"),flush=True)
    for item in report.get("results",[]):
        print(item["ref_id"],item["web_status"],item["verification"]["status"],
              item["verification"].get("match"),flush=True)
    if report["result_status"]!="PASS_METADATA_AND_NEGATIVE_CONTROLS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
