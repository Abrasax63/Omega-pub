#!/usr/bin/env python3
"""Request 3 prospective representation ASTs from a pinned *local* Qwen model.

No holdout/gold examples in the prompt. Raw output is frozen as a separate
GitHub Actions artifact before an independent downstream job grades proposals.
Do not retry, adjust temperature or repair a reply based on evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback
import urllib.request

MODEL="Qwen2.5-Coder-3B-Instruct-Q4_K_M"
GGUF_SHA256="724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
LLAMA_CPP_SHA="5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
URL="http://127.0.0.1:8091/v1/chat/completions"
MAX_OUTPUT=420
SCHEDULE=((11,0.0),(17,0.35),(23,0.7))

# Do not include any solution, source code, case, invariant or correct example.
TASK=(
    "Mathematical problem: a word uses only '(' and ')'. It is valid exactly "
    "when every closing bracket can be matched to an earlier unmatched opening "
    "bracket and no unmatched opening bracket remains at the end. The empty "
    "word is valid. Invent a DIFFERENT NUMERIC REPRESENTATION of this word, "
    "and provide a boolean formula (an AST) that decides validity for all lengths. "
    "Do not provide code. Do not assume that counts alone preserve order. "
    "You may assign an integer weight from -2 to +2 independently to each of "
    "the two bracket characters. The available numeric features of the weighted "
    "word are length, sum, min_prefix, max_prefix, min_suffix, max_suffix, "
    "count_open, count_close, first_weight, last_weight, num_changes. "
    "Prefix and suffix summaries include the empty prefix/suffix with value 0. "
    "Valid numeric AST nodes are {\"const\": integer} or {\"feature\": name}. "
    "Valid boolean AST nodes are comparisons "
    "{\"op\": \"eq|ne|ge|gt|le|lt\", \"left\": numeric-node, "
    "\"right\": numeric-node}, or "
    "{\"op\": \"and|or\", \"args\": [boolean-node,...]}, or "
    "{\"op\": \"not\", \"arg\": boolean-node}. "
    "The boolean root should be under 31 nodes and depth <= 8. "
    "Return ONLY ONE VALID JSON OBJECT with exactly these root keys: "
    "\"weights\" (an object with literal keys '(' and ')' and integer values), "
    "\"predicate\" (boolean AST), and \"idea\" (brief explanation <= 500 chars). "
    "No markdown, no backticks, no prose outside JSON. "
    "No test examples or answers are given."
)
MESSAGES=[
    {"role":"system","content":"You are proposing a formal mathematical representation. Return precisely valid JSON, no commentary."},
    {"role":"user","content":TASK},
]


def call_local(seed:int,temperature:float) -> dict:
    payload={"messages":MESSAGES,"max_tokens":MAX_OUTPUT,
             "temperature":temperature,"seed":seed,"stream":False}
    request=urllib.request.Request(URL,
        data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type":"application/json"},method="POST")
    start=time.monotonic()
    with urllib.request.urlopen(request,timeout=240) as response:
        reply=json.loads(response.read(150000))
    duration=round(time.monotonic()-start,4)
    if not isinstance(reply,dict) or not reply.get("choices"):
        raise ValueError("LOCAL_RESPONSE_LACKS_CHOICES")
    msg=reply["choices"][0].get("message",{}).get("content")
    if not isinstance(msg,str):
        raise ValueError("LOCAL_RESPONSE_NOT_TEXT")
    return {"raw_reply":msg,"raw_sha256":hashlib.sha256(msg.encode("utf-8")).hexdigest(),
            "served_model":reply.get("model"),
            "token_usage":reply.get("usage"),
            "finish_reason":reply["choices"][0].get("finish_reason"),
            "elapsed_s":duration}


def infer_all(caller=call_local) -> dict:
    records=[]
    for i,(seed,temperature) in enumerate(SCHEDULE,1):
        row={"attempt":i,"seed":seed,"temperature":temperature,
             "status":"MODEL_CALL_ATTEMPTED","raw_reply":None,
             "raw_sha256":None}
        try:
            result=caller(seed,temperature)
            row.update(result)
            row["status"]="MODEL_RAW_FROZEN"
        except Exception as e:
            row["status"]="MODEL_INFRASTRUCTURE_ERROR"
            row["error_type"]=type(e).__name__
            row["error"]=str(e)[:300]
        records.append(row)
        print("PROPOSAL",i,row["status"],row.get("raw_sha256"),flush=True)
    return {
        "experiment":"OMEGA_CREATIVE_MODEL02_RAW_UNGRADED_PROPOSALS",
        "model":MODEL,"model_gguf_sha256":GGUF_SHA256,
        "llama_cpp_commit":LLAMA_CPP_SHA,
        "prompt_sha256":hashlib.sha256(json.dumps(MESSAGES,sort_keys=True).encode()).hexdigest(),
        "model_saw_holdout_cases":False,
        "model_saw_candidate_exemplars":False,
        "model_weights_changed":False,"paid_api_calls":0,
        "three_call_schedule_precommitted":True,
        "max_tokens_per_call":MAX_OUTPUT,
        "proposals":records,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=infer_all()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RAW_PROPOSALS_FROZEN",len(result["proposals"]),flush=True)
    if any(x["status"]=="MODEL_INFRASTRUCTURE_ERROR" for x in result["proposals"]):
        # Upload artifacts anyway; the model stage fails closed, not converted
        # to a scientific verdict.
        raise SystemExit(1)


if __name__=="__main__":
    main()
