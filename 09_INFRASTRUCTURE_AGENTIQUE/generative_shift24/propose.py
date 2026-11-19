#!/usr/bin/env python3
"""Unscored two-stage real local-model proposal generation.

STRICT INFORMATION FIREWALL: does not read GOLD, CASES or any verifier code.
First output is sealed before the language formalization request. Responses
are data; never treated as code or scientific truth.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback
import urllib.request

URL="http://127.0.0.1:8091/v1/chat/completions"
MODEL="Qwen2.5-Coder-3B-Instruct-Q4_K_M"
WEIGHTS_SHA256="724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
LLAMA_CPP_SHA="5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
PROMPT_IDS=("P1","P2")
BASE_SYSTEM=("You are exploring new representations for a formal finite problem. "
             "The goal is a mathematical alternative viewpoint, not eloquence. "
             "Do not claim a proof from text alone.")
TASK_DESCRIPTION=(
    "Consider the following finite switch game. There are n binary lights. "
    "A state is n bits. A list 'moves' contains bitmasks; executing a move "
    "flips exactly its listed lights, i.e., current_state XOR mask. "
    "You may apply any moves any number of times in any order. "
    "Given arbitrary valid values 'start' and 'target', decide whether "
    "the target is reachable. Do not assume any particular instances. "
)
IDEAS={
    "P1":TASK_DESCRIPTION+(
        "Invent ONE different mathematical representation of the task, "
        "rather than enumerating all reachable states. Name what structural "
        "feature your representation preserves. Explain a possible limitation. "
        "Reply in a brief paragraph, no code."
    ),
    "P2":TASK_DESCRIPTION+(
        "Pretend brute force exploration is impossible because there are many states. "
        "Change the viewpoint from a transition graph to a more concise invariant "
        "without seeing any test cases. Explain what remains invariant and how "
        "it decides reachability; note any assumptions. "
        "Reply in a brief paragraph, no code."
    ),
}
FORMALIZE=(
    "Now try to formalize ONLY YOUR OWN IDEA stated above for the same switch "
    "game. Return a single line, EXPR: <boolean mathematical expression>. "
    "The expression is a restricted safe arithmetic language, NOT executable Python. "
    "Variables: moves (list of integer masks), start (integer), target (integer). "
    "Permitted primitives: rank(list of integer bitvectors over GF(2)), "
    "popcount(integer), len(list); integer xor '^', concatenating lists '+', "
    "singleton list '[x]', integer constants and comparisons "
    "'== != < <= > >=', 'and or not', parentheses. "
    "There is no built-in reachability function. No loops, imports, code blocks, "
    "comments, explanations, function definitions, assignments or extra lines. "
    "If your idea cannot be expressed with these primitives, reply exactly "
    "'EXPR: UNSUPPORTED'. Do not invent mathematical names not in the grammar."
)


def call_model(messages: list[dict], max_tokens: int) -> dict:
    request=urllib.request.Request(URL,method="POST",
        data=json.dumps({"messages":messages,"max_tokens":max_tokens,
                         "temperature":0,"stream":False},
                        ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type":"application/json"})
    start=time.monotonic()
    with urllib.request.urlopen(request,timeout=300) as response:
        data=json.loads(response.read(180000))
    duration=round(time.monotonic()-start,3)
    if not isinstance(data,dict) or not data.get("choices"):
        raise ValueError("LOCAL_MODEL_BAD_RESPONSE")
    choice=data["choices"][0]
    raw=choice["message"].get("content")
    if not isinstance(raw,str) or len(raw)>10000:
        raise ValueError("LOCAL_MODEL_RESPONSE_NOT_BOUNDED_TEXT")
    return {
        "reply":raw,
        "reply_sha256":hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "tokens":data.get("usage"),
        "duration_s":duration,
        "finish_reason":choice.get("finish_reason"),
        "served_model":data.get("model"),
    }


def propose() -> dict:
    records=[]
    for prompt_id in PROMPT_IDS:
        initial=[
            {"role":"system","content":BASE_SYSTEM},
            {"role":"user","content":IDEAS[prompt_id]},
        ]
        idea=call_model(initial,320)
        # Seal this first stage *before* showing names of the DSL primitives.
        sealed_first=idea["reply_sha256"]
        formal=[
            {"role":"system","content":BASE_SYSTEM},
            {"role":"user","content":TASK_DESCRIPTION+IDEAS[prompt_id][len(TASK_DESCRIPTION):]},
            {"role":"assistant","content":idea["reply"]},
            {"role":"user","content":FORMALIZE},
        ]
        expression=call_model(formal,160)
        records.append({
            "prompt_id":prompt_id,
            "idea_prompt_sha256":hashlib.sha256(IDEAS[prompt_id].encode("utf-8")).hexdigest(),
            "idea_before_DSL":idea,
            "first_idea_sealed_sha256":sealed_first,
            "formalization_after_DSL":expression,
            "feedback_from_oracle_seen":False,
            "any_case_or_gold_sent_to_model":False,
        })
        print(prompt_id,"idea_hash",sealed_first,
              "formal_hash",expression["reply_sha256"],flush=True)
    return {
        "experiment":"OMEGA_GEN24_REAL_LOCAL_QWEN_IDEAS_BEFORE_DSL",
        "status":"COMPLETED_REAL_MODEL_INFERENCE",
        "model":MODEL,
        "weights_sha256":WEIGHTS_SHA256,
        "llama_cpp_sha":LLAMA_CPP_SHA,
        "prompt_variations":len(records),
        "model_calls":2*len(records),
        "training_or_weight_update":False,
        "source_promoted_to_theorem":False,
        "paid_api_calls":0,
        "source_cases_provided_to_model":False,
        "gold_labels_provided_to_model":False,
        "results":records,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    opts=p.parse_args()
    try:
        report=propose()
    except Exception:
        report={
            "status":"MODEL_FAILED_OR_NOT_EXECUTED",
            "exception":traceback.format_exc(),
            "source_promoted_to_theorem":False,
            "paid_api_calls":0,
        }
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PROPOSAL",report["status"],flush=True)
    if report["status"]!="COMPLETED_REAL_MODEL_INFERENCE":
        raise SystemExit(1)


if __name__=="__main__":
    main()
