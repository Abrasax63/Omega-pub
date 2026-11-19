#!/usr/bin/env python3
"""Frozen cohort plus two independently implemented exact reference methods.

Only load_holdout() opens the scoring holdout; the inference path never calls it.
A matching finite oracle is a counterexample method, NOT a universal theorem proof.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TRAIN26=ROOT/"train26"

PINS={
    "PROMPTS_FROZEN.json":"054ce546799458a144d172f21b5f511c3a15a613",
    "CALIBRATION_FROZEN.json":"a6c9f6d00237413202c235ba7676cdba816258c1",
    "HOLDOUT_FROZEN.json":"4e53be8e4d0decd2918940d9ccb84b80be0db7ea",
    "ANSWER_KEY_EVAL_ONLY.json":"47652c9201fb55544a5704032e88e00663149337",
}
TRAIN26_BLOB="f6086d9acd70dccd604c60c987df58649fe33f7e"
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
ADAPTER_SHA="4d378c42f491550251d8973fc1344351865d1d41bc6e24fd2d94d6a0d6a3b446"
ORIGINAL_RUN=44512647677
ORIGINAL_ARTIFACT=14525096133
ARMS=("A_BASE_NEUTRAL","B_LORA_NEUTRAL","C_LORA_VERIFIER")
N_PROMPTS=16
SYSTEM=(
 "You are solving a mathematical transformation task. TASK=FORMALIZE: "
 "derive one exact Boolean criterion for every valid input, replacing "
 "naive enumeration with a mathematical invariant. Allowed variables are "
 "those in the task; allowed functions: gcd(x,y), min(x,y), max(x,y). "
 "Allowed arithmetic: +, -, %, integer constants 0..64; comparisons "
 "== != < <= > >=; logical and/or/not and parentheses. "
 "Output exactly one line EXPR: <boolean expression>, or ABSTAIN if "
 "no exact expression can be derived. No markdown, no added text, "
 "no code blocks, no imports. Do not invent mathematical functions."
)
MAX_GENERATED_TOKENS=96


def git_blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


def read_pinned(name:str)->dict:
    if name not in PINS:
        raise ValueError("UNREGISTERED_COHORT_FILE")
    raw=(HERE/name).read_bytes()
    if len(raw)>60000 or git_blob(raw)!=PINS[name]:
        raise ValueError("DRIFT_OR_OVERSIZE: "+name)
    return json.loads(raw)


def load_prompts()->list[dict]:
    j=read_pinned("PROMPTS_FROZEN.json")
    rows=j["items"]
    if len(rows)!=16 or len({x["id"] for x in rows})!=16:
        raise ValueError("MISSING_OR_DUPLICATE_16_PROMPTS")
    if [x["domain"] for x in rows]!=(
        ["modular_orbit"]*6+["closed_interval_overlap"]*6+["unsupported"]*4
    ):
        raise ValueError("PROMPT_ORDER_OR_DOMAINS_CHANGED")
    if len({x["prompt"] for x in rows})!=16:
        raise ValueError("DUPLICATED_PROMPTS")
    for row in rows:
        if any(k in row for k in ("target","formula","answer","gold")):
            raise ValueError("PROMPT_LEAKS_ANSWER_KEY")
    return rows


def mod_orbit_direct(case:dict)->bool:
    m,step,start,target=[case[x] for x in ("modulus","step","start","target")]
    if not 2<=m<=64 or not 0<=step<m or not 0<=start<m or not 0<=target<m:
        raise ValueError("OUT_OF_SCOPE_MODULAR_CASE")
    seen=set()
    cur=start
    while cur not in seen:
        if cur==target:
            return True
        seen.add(cur)
        cur=(cur+step)%m
    return False


def mod_gcd_independent(case:dict)->bool:
    # Euclid's algorithm implemented separately from state-graph traversal.
    a,b=case["step"],case["modulus"]
    while b:
        a,b=b,a%b
    if a<=0:raise AssertionError("ZERO_GCD_UNEXPECTED")
    return (case["target"]-case["start"])%a==0


def overlap_direct(case:dict)->bool:
    a,b,c,d=[case[x] for x in ("a","b","c","d")]
    if not a<=b or not c<=d or any(not -64<=v<=64 for v in (a,b,c,d)):
        raise ValueError("OUT_OF_SCOPE_INTERVAL_CASE")
    return any(c<=x<=d for x in range(a,b+1))


def overlap_limits_independent(case:dict)->bool:
    return max(case["a"],case["c"])<=min(case["b"],case["d"])


def validate_set(name:str)->dict:
    if name not in ("CALIBRATION_FROZEN.json","HOLDOUT_FROZEN.json"):
        raise ValueError("INVALID_CASE_SET")
    d=read_pinned(name)
    expected=24 if name.startswith("CALIBRATION") else 96
    for group,truth,fn1,fn2 in (
        ("modular","reachable",mod_orbit_direct,mod_gcd_independent),
        ("intervals","overlap",overlap_direct,overlap_limits_independent),
    ):
        cases=d[group]
        if len(cases)!=expected or len({x["id"] for x in cases})!=expected:
            raise ValueError("CASE_COUNT_OR_DUPLICATE_"+group)
        if sum(x[truth] for x in cases)!=expected//2:
            raise ValueError("DATASET_IMBALANCED_"+group)
        for c in cases:
            if fn1(c)!=fn2(c) or fn1(c)!=c[truth]:
                raise AssertionError("INDEPENDENT_ORACLES_DISAGREE_"+group+"_"+c["id"])
            if name.startswith("CALIBRATION") and group=="modular" and c["modulus"]>16:
                raise ValueError("CALIBRATION_OVERLAPS_HOLDOUT_MODULUS")
            if name.startswith("HOLDOUT") and group=="modular" and c["modulus"]<17:
                raise ValueError("HOLDOUT_OVERLAPS_CALIBRATION_MODULUS")
            if name.startswith("CALIBRATION") and group=="intervals" and (
                max(c[k] for k in ("a","b","c","d"))>6
            ):
                raise ValueError("CALIBRATION_INTERVAL_OVERLAP")
            if name.startswith("HOLDOUT") and group=="intervals" and (
                min(c[k] for k in ("a","b","c","d"))<8
            ):
                raise ValueError("HOLDOUT_INTERVAL_OVERLAP")
    return d


def load_calibration()->dict:
    return validate_set("CALIBRATION_FROZEN.json")


def load_holdout()->dict:
    return validate_set("HOLDOUT_FROZEN.json")


def check_unseen_training_family()->dict:
    raw=(TRAIN26/"TRAIN_FROZEN.json").read_bytes()
    if git_blob(raw)!=TRAIN26_BLOB:
        raise ValueError("TRAIN26_SOURCE_NOT_IDENTICAL_TO_TRAINED_MODEL")
    text=raw.decode("utf-8").casefold()
    checks=("gcd","modulo","modular","interval","intervalle","overlap")
    present=[word for word in checks if re.search(r"\b"+re.escape(word),text)]
    if present:
        raise ValueError("SUPPOSEDLY_UNSEEN_DOMAIN_PRESENT_IN_TRAIN26:"+repr(present))
    return {"training_examples":320,"train26_blob":TRAIN26_BLOB,
            "searched_markers":list(checks),
            "no_literal_family_mentions_found":True,
            "no_prior_pretraining_absence_claim":True}


def run_offline():
    p=load_prompts()
    c=load_calibration()
    h=load_holdout()
    unseen=check_unseen_training_family()
    if set(x["id"] for x in c["modular"])&set(x["id"] for x in h["modular"]):
        raise ValueError("OVERLAPPING_IDS")
    print(json.dumps({
        "status":"TRANSFER27_PREMODEL_CONTROLS_PASS",
        "prompts":len(p),"calibration_cases":len(c["modular"])+len(c["intervals"]),
        "heldout_cases":len(h["modular"])+len(h["intervals"]),
        "unseen_train26":unseen,
        "strong_reference_successes":len(h["modular"])+len(h["intervals"]),
        "no_model_inference_yet":True,
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    run_offline()
