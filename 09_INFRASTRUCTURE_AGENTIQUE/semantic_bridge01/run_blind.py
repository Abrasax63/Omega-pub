#!/usr/bin/env python3
"""Prospective blind semantic *diagnostic* on a frozen, disjoint ProofNet cohort.

No data-dependent rule tuning, no automatic theorem certification, no Lean
proof compiles. The upstream same-file NL↔Lean association is used as an
evaluation label ONLY AFTER all predictions are fixed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback

HERE=Path(__file__).resolve().parent
INFRA=HERE.parent
sys.path.insert(0,str(INFRA/"external_memory01"))
sys.path.insert(0,str(INFRA/"cycle01"))
from run_external import (
    parse_source,fetch_source,build_messages,parse_label,
)
from single_resident import SingleResidentGovernor,ModelProfile,LocalLlamaBackend
from cycle import query_server,canonical,sha_bytes
from structural_bridge import match,guarded_proposal,MIN_SCORE,MIN_MARGIN

MANIFEST=HERE/"BLIND_HOLDOUT.json"
PINNED=HERE/"SOURCE_BLOBS.json"
UPSTREAM="marcusm117/ProofNet-Verified"
COMMIT="b7ca411a2abaa6caf3580192b30d865e5bd10bc4"
ORIGINAL_OLD=frozenset((1,2,3,6,10,22,40,80,120,160,200,240,280,320,350,367,11,17,34,55,77,99,141,181))
EXPECTED_IDS=(12,18,35,56,78,100,142,182,23,43,153,263)

def get_manifest():
    data=json.loads(MANIFEST.read_text(encoding="utf8"))
    if (data.get("status")!="BLIND_HOLDOUT_FROZEN_BEFORE_SEMANTIC_PARSER_CODE_OR_SOURCE_VIEW"
        or data.get("upstream_repo")!=UPSTREAM or data.get("upstream_commit")!=COMMIT
        or tuple(data.get("holdout_ids",[]))!=EXPECTED_IDS):
        raise ValueError("HOLDOUT_WAS_CHANGED_OR_NOT_PREREGISTERED")
    if set(EXPECTED_IDS)&ORIGINAL_OLD:
        raise AssertionError("HOLDOUT_COLLIDES_WITH_OLDER_OMEGA_CASES")
    questions=data.get("tasks",[])
    if len(questions)!=18 or Counter(t.get("gold") for t in questions)!={"A":6,"B":6,"NONE":6}:
        raise ValueError("BLIND_TASK_BALANCE_WAS_CHANGED")
    ids=set(EXPECTED_IDS)
    seen=set()
    for t in questions:
        if (set(("task","id","a","b","gold"))-set(t) or
            t["id"] not in ids or t["a"] not in ids or t["b"] not in ids or
            t["a"]==t["b"] or t["task"] in seen):
            raise ValueError("INVALID_OR_DUPLICATE_HOLDOUT_TASK")
        seen.add(t["task"])
        expected=("A" if t["a"]==t["id"] else
                  "B" if t["b"]==t["id"] else "NONE")
        if t["gold"]!=expected:
            raise ValueError("UPSTREAM_IDENTITY_GOLD_CHANGED")
    return data


def source_pins(manifest):
    data=json.loads(PINNED.read_text(encoding="utf8"))
    if (data.get("source_commit")!=COMMIT or
        data.get("upstream_repo")!=UPSTREAM or
        tuple(x.get("id") for x in data.get("sources",[]))!=EXPECTED_IDS):
        raise ValueError("HOLDOUT_SOURCE_PIN_SET_CHANGED")
    if len({x["git_blob"] for x in data["sources"]})!=12:
        raise ValueError("REPEATED_OR_MISSING_GIT_BLOB")
    for p in data["sources"]:
        if (p["path"]!=f"proofnet-verified-latest/proofnet-{p['id']}.lean"
            or len(p["git_blob"])!=40
            or any(c not in "0123456789abcdef" for c in p["git_blob"])):
            raise ValueError("UNTRUSTED_UNPINNED_SOURCE")
    return data["sources"]


def get_pinned_sources(manifest,folder):
    folder.mkdir(parents=True,exist_ok=True)
    pins=source_pins(manifest)
    out={}
    for p in pins:
        dest=folder/f"proofnet-{p['id']}.lean"
        if dest.exists():
            raw=dest.read_bytes()
        else:
            raw=fetch_source(p)
            dest.write_bytes(raw)
        out[p["id"]]=parse_source(raw,p) # two independent NL/Lean extractors + Git blob
    if tuple(out)!=EXPECTED_IDS:
        raise ValueError("SOURCES_MISSING_OR_REORDERED")
    return out


def freeze_inputs(manifest,sources):
    """Only statement and two candidates reach the engines, never the gold."""
    frozen=[]
    for t in manifest["tasks"]:
        a,b= sources[t["a"]],sources[t["b"]]
        s=sources[t["id"]]
        inputs={
            "task_id":t["task"],
            "natural":s["informal_exact"],
            "formal_a":a["lean_reference_exact"],
            "formal_b":b["lean_reference_exact"],
            "source_blob":s["raw_git_blob"],
            "candidate_blobs":(a["raw_git_blob"],b["raw_git_blob"]),
        }
        frozen.append(inputs)
    return frozen


def run_structural(inputs):
    results=[]
    for x in inputs:
        t0=perf_counter()
        decision=match(x["natural"],x["formal_a"],x["formal_b"])
        results.append({
            "task_id":x["task_id"],
            "source_blob":x["source_blob"],
            "candidate_blobs":x["candidate_blobs"],
            "input_sha256":sha_bytes(canonical({
                "nl":x["natural"],"a":x["formal_a"],"b":x["formal_b"]})),
            "prediction":decision["prediction"],
            "structural_status":decision["status"],
            "evidence":decision,
            "compute_seconds":round(perf_counter()-t0,6),
            "source_semantics_proved":False
        })
    return results


def run_qwen(inputs,manifest,sources,governor,profile):
    results=[]
    t0=perf_counter()
    governor.activate(profile)
    try:
        for input_data,task in zip(inputs,manifest["tasks"]):
            # Reuse the previously frozen baseline prompt text from EXTERNAL01.
            nongold={k:task[k] for k in ("task","id","a","b")}
            messages=build_messages(nongold,sources)
            rendered,templ_dt=query_server(governor.backend.port,"/apply-template",{"messages":messages})
            prompt=rendered.get("prompt")
            if not isinstance(prompt,str) or not prompt:
                raise ValueError("LLAMA_NATIVE_CHAT_RENDER_MISSING")
            native,call_dt=query_server(governor.backend.port,"/completion",{
                "prompt":prompt,"cache_prompt":False,"id_slot":0,
                "n_predict":12,"temperature":0,"seed":42,
                "stream":False,"stop":["<|im_end|>","<|im_start|>"]
            })
            answer=native.get("content")
            if not isinstance(answer,str):
                raise ValueError("MODEL_REPLY_MISSING")
            tm=native.get("timings")
            if not isinstance(tm,dict):tm={}
            results.append({
                "task_id":input_data["task_id"],
                "source_blob":input_data["source_blob"],
                "input_sha256":sha_bytes(canonical({
                    "nl":input_data["natural"],"a":input_data["formal_a"],
                    "b":input_data["formal_b"]})),
                "rendered_prompt_sha256":sha_bytes(prompt.encode("utf8")),
                "raw_reply":answer,
                "prediction":parse_label(answer),
                "model_format_valid":parse_label(answer) is not None,
                "source_semantics_proved":False,
                "cache_prompt":False,
                "timings":{k:tm.get(k) for k in
                    ("prompt_n","cache_n","prompt_ms","predicted_n","predicted_ms")},
                "template_http_seconds":templ_dt,
                "completion_http_seconds":call_dt
            })
        peak=governor.backend.peak_rss_kib()
    finally:
        governor.release()
    return results,{"duration_including_start_stop_seconds":round(perf_counter()-t0,3),
                   "server_peak_rss_kib":peak,
                   "model_verified_sha256":profile.sha256_expected}


def analyse(manifest,inputs,heuristic,raw_model):
    n=len(manifest["tasks"])
    if len(inputs)!=n or len(heuristic)!=n or len(raw_model)!=n:
        raise ValueError("MISSING_BLIND_PREDICTIONS")
    outputs=[]
    for t,x,h,model in zip(manifest["tasks"],inputs,heuristic,raw_model):
        if t["task"]!=x["task_id"] or t["task"]!=h["task_id"] or t["task"]!=model["task_id"]:
            raise ValueError("WRONG_BLIND_CASE_PAIRING")
        frozen_sha=sha_bytes(canonical({
            "nl":x["natural"],"a":x["formal_a"],"b":x["formal_b"]}))
        if (frozen_sha!=h["input_sha256"] or frozen_sha!=model["input_sha256"]):
            raise ValueError("SEMANTIC_SOURCE_CHANGED_AFTER_PREDICTION")
        ir_guard=guarded_proposal(model["raw_reply"],h["evidence"])
        outputs.append({
            "task":t["task"],
            "original_upstream_pairing_gold":t["gold"],
            "upstream_pairing_is_semantic_gold":False,
            "model_label":model["prediction"],
            "signature_label":h["prediction"],
            "guarded_label":ir_guard["prediction"],
            "guard_reason":ir_guard["reason"],
            "confidence_kind":"HEURISTIC_UNCALIBRATED_NO_PROOF",
            "source_blob":h["source_blob"],
            "match_status":h["structural_status"]
        })
    def stats(name):
        rows=outputs
        preds=[r[name] for r in rows]
        chosen=sum(x in ("A","B") for x in preds)
        true_chosen=sum(r[name]==r["original_upstream_pairing_gold"]
            and r[name] in ("A","B") for r in rows)
        return {
            "total":n,
            "correct":sum(r[name]==r["original_upstream_pairing_gold"] for r in rows),
            "positive_correct":sum(r[name]==r["original_upstream_pairing_gold"]
                                   for r in rows if r["original_upstream_pairing_gold"]!="NONE"),
            "positive_total":12,
            "none_correct":sum(r[name]=="NONE" and r["original_upstream_pairing_gold"]=="NONE"
                               for r in rows),
            "none_total":6,
            "format_rejections":sum(x is None for x in preds),
            "positive_predictions":chosen,
            "positive_prediction_precision":None if not chosen else round(true_chosen/chosen,4),
            "abstained_none_on_positives":sum(r[name]=="NONE" and r["original_upstream_pairing_gold"]!="NONE" for r in rows),
            "false_positive_on_none":sum(r[name] in ("A","B") and r["original_upstream_pairing_gold"]=="NONE" for r in rows),
            "ambiguous":sum(r["match_status"]=="AMBIGUOUS_ABSTAIN" for r in rows) if name!="model_label" else None,
        }
    return {
        "status":"BLIND_EXTERNAL_PAIRING_EVALUATED",
        "n_unseen_to_Omega_test_sources":12,
        "tasks":18,"label_definition":"UPSTREAM_SAME_FILE_PAIRING_ONLY",
        "statistical_generalization_proven":False,
        "semantic_equivalence_proven":False,
        "lean_proofs_compiled":0,
        "compare":{
            "raw_qwen_0p5b_cache_off":stats("model_label"),
            "structural_signature":stats("signature_label"),
            "structural_guarded_qwen":stats("guarded_label"),
        },
        "rows":outputs,
        "ir_thresholds_frozen":{"min_score":MIN_SCORE,"min_margin":MIN_MARGIN},
        "post_holdout_rule_changes":0,
        "no_model_training":True,
        "paid_api_calls":0
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile",type=Path,required=True)
    ap.add_argument("--model",type=Path,required=True)
    ap.add_argument("--server",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={"status":"STARTED","prereg_manifest_sha256":sha_bytes(MANIFEST.read_bytes()),
            "ir_code_sha256":sha_bytes((HERE/"structural_bridge.py").read_bytes()),
            "model_cache_mode":"OFF_ONLY","no_main_write":True}
    try:
        manifest=get_manifest()
        sources=get_pinned_sources(manifest,args.output_dir/"external_sources")
        inputs=freeze_inputs(manifest,sources)
        structural=run_structural(inputs)
        report["source_audit"]={
            "source_count":len(sources),
            "all_sources_blobs_and_extractions_agree":True,
            "sources":[{"id":id,"git_blob":s["raw_git_blob"],"original_url":s["source_url"],
                        "nl_sha256":s["informal_sha256"],
                        "lean_statement_sha256":s["formal_sha256"],
                        "source_contains_sorry":s["lean_contains_sorry"]}
                       for id,s in sources.items()],
            "source_references_not_Lean_proofs":True
        }
        report["structural_prediction_sha256"]=sha_bytes(canonical(structural))
        report["structural_precomputed_before_llm":True
        profile_bytes=args.profile.read_bytes()
        if sha_bytes(profile_bytes)!="f6f1fae5cae5c79a6c0145496f5f2456311ba76f3b8b7ce22bd3a7a464a34996":
            raise ValueError("REAL_SCALE_PROFILE_SHA_CHANGED")
        profile=ModelProfile.from_scale_report(json.loads(profile_bytes),args.model)
        gov=SingleResidentGovernor(LocalLlamaBackend(args.server,port=8143),
                                   budget_kib=6*1024*1024,reserve_kib=512*1024)
        raw_model,usage=run_qwen(inputs,manifest,sources,gov,profile)
        report["model_runtime"]=usage
        report["evaluation"]=analyse(manifest,inputs,structural,raw_model)
        report["status"]="EXECUTED_WITH_UNVERIFIED_SEMANTIC_CLAIMS_QUARANTINED"
    except Exception as exc:
        report["status"]="FAILED_OR_INDETERMINATE"
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)
        report["traceback"]=traceback.format_exc()
        raise
    finally:
        report_path=args.output_dir/"report.json"
        report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        if "structural" in locals():
            (args.output_dir/"ir_predictions.jsonl").write_text(
                "".join(canonical(x).decode("utf8")+"\n" for x in structural),encoding="utf8")
        if "raw_model" in locals():
            (args.output_dir/"model_quarantine.jsonl").write_text(
                "".join(canonical(x).decode("utf8")+"\n" for x in raw_model),encoding="utf8")
        print("SEM_BRIDGE_STATUS",report["status"],flush=True)
        if "evaluation" in report:
            print("SEM_BRIDGE_SUMMARY",json.dumps(report["evaluation"]["compare"]),flush=True)


if __name__=="__main__":
    main()
