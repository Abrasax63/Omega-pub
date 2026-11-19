#!/usr/bin/env python3
"""Two-call, three-arm real SmolLM2 experiment; no evaluation holdout access.

First stage freezes all 48 unscored raw ideas. Second stage gives only C a
counterexample from the frozen calibration (never the holdout), all other arms
receive a neutral revision instruction. Each arm has 2 calls/item and 96-token
output cap per call. Input-token/CPU totals are recorded, not assumed equal.
"""
from __future__ import annotations
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

from data_guard import (
    MODEL,MODEL_REV,ADAPTER_SHA,TRAIN26_BLOB,ARMS,SYSTEM,
    MAX_GENERATED_TOKENS,load_prompts,load_calibration,
)
from logic import check_on_cases

FIRST_ST="FROZEN_FIRST_IDEAS_ALL_ARMS"
SECOND_ST="FROZEN_SECOND_IDEAS_NO_HOLDOUT_SEEN"
NEUTRAL=("No verifier feedback is available. Reconsider your previous answer "
         "carefully, keeping the exact required EXPR: syntax or ABSTAIN. "
         "Return just the strongest final proposal, no commentary.")


def sha256_bytes(data:bytes):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path:Path):
    return sha256_bytes(path.read_bytes())


def stable_first_digest(rows):
    data=[{"arm":r["arm"],"id":r["id"],"raw":r["raw"]}
          for r in rows]
    return sha256_bytes(json.dumps(data,sort_keys=True,ensure_ascii=False).encode())


def require_adapter(dir:Path):
    manifest=json.loads((dir/"train_manifest.json").read_text(encoding="utf-8"))
    adapter=dir/"adapter"
    if manifest.get("status")!="TRAINED_ACTUAL_WEIGHTS_CHANGED" or (
        manifest.get("steps")!=640
        or manifest.get("training_data_git_blob")!=TRAIN26_BLOB
        or manifest.get("model_revision")!=MODEL_REV
        or manifest.get("model")!=MODEL
    ):
        raise ValueError("NOT_THE_VERIFIED_TRAIN26_ADAPTER")
    if sha256_file(adapter/"adapter_model.safetensors")!=ADAPTER_SHA:
        raise ValueError("HISTORIC_ADAPTER_SHA256_MISMATCH")
    for name,hash_value in manifest["saved_adapter_sha256"].items():
        if sha256_file(adapter/name)!=hash_value:
            raise ValueError("ADAPTER_MANIFEST_SHA256_MISMATCH: "+name)
    return adapter


def load_runtime(adapter_dir:Path):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2)
    torch.manual_seed(20261119)
    tokenizer=AutoTokenizer.from_pretrained(
        MODEL,revision=MODEL_REV,trust_remote_code=False,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    backbone=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False,
    ).to("cpu")
    backbone.config.use_cache=True
    model=PeftModel.from_pretrained(backbone,str(adapter_dir))
    model.eval()
    return torch,tokenizer,model


def generate(torch,tokenizer,model,arm,messages):
    """Exact same greedy decoding for A B C; only adapter enablement differs."""
    full=tokenizer.apply_chat_template(
        messages,tokenize=False,add_generation_prompt=True)
    tokenized=tokenizer(full,return_tensors="pt")
    inputs=tokenized["input_ids"]
    if inputs.shape[1]>800:
        raise ValueError("UNBOUNDED_INFERENCE_INPUT")
    started=time.monotonic()
    context=model.disable_adapter() if arm=="A_BASE_NEUTRAL" else nullcontext()
    with context:
        with torch.no_grad():
            result=model.generate(
                input_ids=inputs,
                max_new_tokens=MAX_GENERATED_TOKENS,
                do_sample=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )
    raw=tokenizer.decode(
        result[0,inputs.shape[1]:],skip_special_tokens=True)
    # Preserve raw output: no strip, rewrite, JSON extraction, or repairs.
    return {
        "raw":raw,
        "raw_sha256":sha256_bytes(raw.encode("utf-8")),
        "input_tokens":int(inputs.shape[1]),
        "generated_tokens":int(result.shape[1]-inputs.shape[1]),
        "wall_seconds":round(time.monotonic()-started,3),
        "served_backbone":MODEL,
        "trained_adapter_enabled":arm!="A_BASE_NEUTRAL",
    }


def build_first(adapter_dir:Path):
    prompts=load_prompts()
    torch,tok,model=load_runtime(adapter_dir)
    rows=[]
    for p in prompts:
        for arm in ARMS:
            messages=[
                {"role":"system","content":SYSTEM},
                {"role":"user","content":"TASK=FORMALIZE\n"+p["prompt"]},
            ]
            result=generate(torch,tok,model,arm,messages)
            rows.append({
                "id":p["id"],"domain":p["domain"],"arm":arm,
                "phase":"FIRST_BEFORE_VERIFIER_FEEDBACK",**result,
            })
            print("FIRST",p["id"],arm,
                  "raw_sha256",result["raw_sha256"],
                  "generated",result["generated_tokens"],flush=True)
    return {
        "experiment":"OMEGA_TRANSFER27_FIRST_BLIND_IDEAS",
        "status":FIRST_ST,"train26_adapter_sha256":ADAPTER_SHA,
        "generation_calls":len(rows),
        "output_cap_per_call":MAX_GENERATED_TOKENS,
        "calibration_loaded":False,"holdout_loaded":False,
        "real_model_calls_made":True,
        "stable_first_ideas_sha256":stable_first_digest(rows),
        "ideas":rows,
        "paid_api_calls":0,"automatic_certifications":0,
    }


def feedback(domain:str,raw:str,calibration:dict):
    if domain=="unsupported":
        return {
            "status":"UNSUPPORTED_NO_CHECK",
            "reply":NEUTRAL,
            "oracle_cases_checked":0,
            "oracle_wall_seconds":0.0,
            "calibration_summary":None,
        }
    cases=(calibration["modular"] if domain=="modular_orbit"
           else calibration["intervals"])
    start=time.monotonic()
    result=check_on_cases(raw,domain,cases)
    took=round(time.monotonic()-start,5)
    if result["status"]=="FALSIFIED":
        w=result["counterexample"]
        message=(
            "Exact independent verifier feedback on training-free calibration: "
            "your proposal fails on this one example. "
            "Inputs: "+json.dumps(w["inputs"],sort_keys=True)+
            " ; predicted: "+str(w["observed"])+
            " ; correct: "+str(w["expected"])+
            ". Revise to an invariant for ALL valid inputs, not just this example."
        )
    elif result["status"]=="MATCHES_FINITE_CASES":
        message=(
            "A separate exact verifier saw no mismatches across "+
            str(result["checked"])+
            " small calibration cases. This is NOT proof of a universal "
            "formula; critically inspect missing assumptions and respond."
        )
    else:
        message=(
            "The separate checker rejected your proposed formula: "+
            result["status"]+" / "+str(result.get("error"))+
            ". The candidate was not executed. Respect the exact allowed "
            "formal grammar; no invented functions, or output ABSTAIN."
        )
    return {
        "status":result["status"],"reply":message,
        "oracle_cases_checked":result["checked"],
        "oracle_wall_seconds":took,
        "calibration_summary":result,
    }


def build_second(adapter_dir:Path,first:dict):
    if first.get("status")!=FIRST_ST or first.get("generation_calls")!=48:
        raise ValueError("FIRST_STAGE_NOT_SEALED")
    prompts=load_prompts()
    original=first["ideas"]
    if stable_first_digest(original)!=first.get("stable_first_ideas_sha256"):
        raise ValueError("FIRST_STAGE_RAW_DATA_TAMPERED")
    if len({(r["id"],r["arm"]) for r in original})!=48:
        raise ValueError("DUPLICATE_FIRST_IDEAS")
    original_lookup={(r["id"],r["arm"]):r for r in original}
    calibration=load_calibration()
    torch,tok,model=load_runtime(adapter_dir)
    rows=[]
    for p in prompts:
        for arm in ARMS:
            old=original_lookup[(p["id"],arm)]
            inform=feedback(p["domain"],old["raw"],calibration) if (
                arm=="C_LORA_VERIFIER"
            ) else {
                "status":"NEUTRAL_CONTROL","reply":NEUTRAL,
                "oracle_cases_checked":0,"oracle_wall_seconds":0.0,
                "calibration_summary":None,
            }
            messages=[
                {"role":"system","content":SYSTEM},
                {"role":"user","content":"TASK=FORMALIZE\n"+p["prompt"]},
                {"role":"assistant","content":old["raw"]},
                {"role":"user","content":inform["reply"]+
                 " Output one new final line only: EXPR: <boolean> or ABSTAIN."},
            ]
            output=generate(torch,tok,model,arm,messages)
            rows.append({
                "id":p["id"],"domain":p["domain"],"arm":arm,
                "phase":"FINAL_AFTER_NEUTRAL_OR_CALIBRATION_ONLY",
                "first_sha256":old["raw_sha256"],
                "feedback_status":inform["status"],
                "feedback_text":inform["reply"],
                "verifier_calibration_summary":inform["calibration_summary"],
                "verifier_cases_checked":inform["oracle_cases_checked"],
                "verifier_wall_seconds":inform["oracle_wall_seconds"],
                **output,
            })
            print("SECOND",p["id"],arm,"feedback",inform["status"],
                  "raw_sha256",output["raw_sha256"],flush=True)
    return {
        "experiment":"OMEGA_TRANSFER27_FINAL_BLIND_IDEAS",
        "status":SECOND_ST,
        "train26_adapter_sha256":ADAPTER_SHA,
        "first_stage_sha256":first["stable_first_ideas_sha256"],
        "generation_calls":len(rows),
        "output_cap_per_call":MAX_GENERATED_TOKENS,
        "calibration_used_only_by_arm_C":True,
        "holdout_loaded":False,
        "finals":rows,
        "paid_api_calls":0,"automatic_certifications":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("first","second"),required=True)
    p.add_argument("--trained",type=Path,required=True)
    p.add_argument("--first",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        adapter=require_adapter(args.trained)
        if args.stage=="first":
            report=build_first(adapter)
        else:
            if args.first is None:
                raise ValueError("FIRST_STAGE_INPUT_REQUIRED")
            report=build_second(adapter,json.loads(
                args.first.read_text(encoding="utf-8")))
    except Exception:
        report={
            "status":"MODEL_OR_PROVENANCE_FAILED",
            "error":traceback.format_exc(),
            "no_scientific_claim_confirmed":True,
            "automatic_certifications":0,
        }
    args.output.write_text(json.dumps(
        report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRANSFER27",args.stage,report["status"],flush=True)
    if report["status"] not in (FIRST_ST,SECOND_ST):
        raise SystemExit(1)


if __name__=="__main__":
    main()
