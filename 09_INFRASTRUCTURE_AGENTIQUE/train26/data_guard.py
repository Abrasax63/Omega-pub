#!/usr/bin/env python3
"""TRAIN26 immutable corpus and independent finite mathematical oracles.

Training imports load_training() only. This module does not read any holdout
unless the evaluation or offline test explicitly invokes load_holdout().
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from collections import Counter

HERE=Path(__file__).resolve().parent
PINS={
 "TRAIN_FROZEN.json":"f6086d9acd70dccd604c60c987df58649fe33f7e",
 "HOLDOUT_PROMPTS_FROZEN.json":"3009151a2a59ffa8059c7af5cc49862e4f4f22a4",
 "HOLDOUT_GOLD_EVAL_ONLY.json":"4dcc78e197e3d692c5a9baaa268cc2e2a198c09c",
 "ORACLE_CASES_FROZEN.json":"c99d815456f917cd43bb2989b48cbda231810aae",
}
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
SEED=20261119
SYSTEM=("You translate and check mathematical representation proposals. "
        "Follow the user's TASK marker. For FORMALIZE or REPAIR, produce one "
        "exact EXPR: expression using only rank(moves), sum_balance(s), "
        "min_prefix_balance(s), partition_code(T, pi, h, state), xor ^, "
        "integer constants, lists, comparisons and conjunctions. "
        "For CRITIQUE output only ACCEPT if correct for every input or "
        "REJECT if a counterexample exists. If unsupported, output ABSTAIN. "
        "No markdown, commentary, hidden assumptions or invented functions.")
FORMULAS={
 "xor":"EXPR: rank(moves) == rank(moves + [start ^ target])",
 "paren":"EXPR: sum_balance(s) == 0 and min_prefix_balance(s) >= 0",
 "obs":"EXPR: partition_code(T, pi, h, x) == partition_code(T, pi, h, y)",
}
TASKS=frozenset({"FORMALIZE","REPAIR","CRITIQUE","ABSTAIN"})


def read_pinned(file: str)->dict:
    if file not in PINS:
        raise ValueError("UNREGISTERED_DATA")
    path=HERE/file
    raw=path.read_bytes()
    if len(raw)>500000:
        raise ValueError("DATA_UNBOUNDED")
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if blob!=PINS[file]:
        raise ValueError("FROZEN_GIT_BLOB_CHANGED: "+file)
    return json.loads(raw)


def load_training()->list[dict]:
    data=read_pinned("TRAIN_FROZEN.json")
    rows=data["examples"]
    if len(rows)!=320 or len({x["prompt"] for x in rows})!=320:
        raise ValueError("TRAINING_COUNT_OR_DUPLICATES")
    expected={
        ("xor","FORMALIZE"):40,("xor","REPAIR"):28,("xor","CRITIQUE"):28,
        ("paren","FORMALIZE"):40,("paren","REPAIR"):28,("paren","CRITIQUE"):28,
        ("obs","FORMALIZE"):40,("obs","REPAIR"):28,("obs","CRITIQUE"):28,
        ("unsupported","ABSTAIN"):32,
    }
    groups=Counter((r["domain"],r["task"]) for r in rows)
    if dict(groups)!=expected:
        raise ValueError("TRAINING_COUNTS_CHANGED")
    for row in rows:
        task=row["task"]; domain=row["domain"]
        if task not in TASKS or not row["prompt"].startswith("TASK="):
            raise ValueError("UNRECOGNIZED_TASK")
        if domain in FORMULAS and task in ("FORMALIZE","REPAIR"):
            correct=FORMULAS[domain]
        elif domain=="unsupported":
            correct="ABSTAIN"
        elif task=="CRITIQUE":
            correct="ACCEPT" if row["candidate_class"]=="VALID" else "REJECT"
        else:
            raise ValueError("UNREGISTERED_TRAIN_LABEL")
        if row["target"]!=correct:
            raise ValueError("WRONG_TRAIN_TARGET")
    return rows


def load_holdout():
    prompts=read_pinned("HOLDOUT_PROMPTS_FROZEN.json")["prompts"]
    gold=read_pinned("HOLDOUT_GOLD_EVAL_ONLY.json")["labels"]
    if len(prompts)!=48 or len(gold)!=48:
        raise ValueError("HOLDOUT_LENGTH_MISMATCH")
    if len({r["prompt"] for r in prompts})!=48:
        raise ValueError("HOLDOUT_PROMPT_DUPLICATE")
    seen={r["prompt"] for r in load_training()}
    if seen & {r["prompt"] for r in prompts}:
        raise ValueError("EXACT_TRAIN_HOLDOUT_PROMPT_LEAK")
    if [r["id"] for r in prompts]!=[r["id"] for r in gold]:
        raise ValueError("HOLDOUT_ORDER_MISMATCH")
    task_counts=Counter(x["task"] for x in prompts)
    if dict(task_counts)!={"FORMALIZE":12,"REPAIR":12,"CRITIQUE":12,"ABSTAIN":12}:
        raise ValueError("HOLDOUT_TASK_COUNTS_CHANGED")
    for p,g in zip(prompts,gold):
        if p["task"]!=g["task"] or p["domain"]!=g["domain"]:
            raise ValueError("HOLDOUT_DOMAIN_TASK_MISMATCH")
        if p["task"] in ("FORMALIZE","REPAIR"):
            target=FORMULAS[p["domain"]]
        elif p["task"]=="CRITIQUE":
            target=g["target"]  # separately cross-checked with actual oracle.
            if target not in ("ACCEPT","REJECT"):
                raise ValueError("CRITIQUE_LABEL_OUT_OF_SCOPE")
        else:
            target="ABSTAIN"
        if target!=g["target"]:
            raise ValueError("HOLDOUT_TARGET_WRONG")
    return prompts,gold


def direct_xor(case):
    visited={case["start"]}
    queue=[case["start"]]
    for curr in queue:
        if curr==case["target"]:
            return True
        for m in case["moves"]:
            nxt=curr^m
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return False


def gaussian_xor(case):
    basis=[0]*case["n"]
    for mask in case["moves"]:
        v=mask
        while v:
            bit=v.bit_length()-1
            if basis[bit]:v^=basis[bit]
            else:basis[bit]=v;break
    rem=case["start"]^case["target"]
    while rem:
        bit=rem.bit_length()-1
        if basis[bit]:rem^=basis[bit]
        else:return False
    return True


def stack_parens(s):
    count=0
    for c in s:
        if c not in "()":raise ValueError("PARENTHESES_ONLY")
        count+=1 if c=="(" else -1
        if count<0:return False
    return count==0


def direct_trace(case):
    a,b=case["x"],case["y"]
    for _ in range(case["h"]):
        if case["pi"][a]!=case["pi"][b]:
            return False
        a=case["T"][a];b=case["T"][b]
    return True


def codes(T,pi,h):
    if len(T)!=len(pi) or not 1<=len(T)<=8 or not 0<=h<=16:
        raise ValueError("BAD_PARTITION_DOMAIN")
    n=len(T)
    if any(type(x)!=int or x<0 or x>=n for x in T):
        raise ValueError("BAD_TRANSITION_MAP")
    if any(type(x)!=int or x not in (0,1) for x in pi):
        raise ValueError("BINARY_ALPHABET_REQUIRED")
    current=[0]*n
    for _ in range(h):
        seen={}; nxt=[]
        for x in range(n):
            sig=(pi[x],current[T[x]])
            if sig not in seen:
                seen[sig]=len(seen)
            nxt.append(seen[sig])
        current=nxt
    return current


def partition_trace(case):
    c=codes(case["T"],case["pi"],case["h"])
    return c[case["x"]]==c[case["y"]]


def load_oracles():
    data=read_pinned("ORACLE_CASES_FROZEN.json")
    if any(len(data[d])!=32 for d in ("xor","paren","obs")):
        raise ValueError("ORACLE_WRONG_CASE_COUNTS")
    for c in data["xor"]:
        if direct_xor(c)!=c["reachable"] or gaussian_xor(c)!=c["reachable"]:
            raise AssertionError("XOR_TWO_INDEPENDENT_ORACLES_DISAGREE")
    for c in data["paren"]:
        if stack_parens(c["s"])!=c["balanced"]:
            raise AssertionError("BRACKET_STACK_ORACLE_DISAGREES")
    for c in data["obs"]:
        if direct_trace(c)!=c["equivalent"] or partition_trace(c)!=c["equivalent"]:
            raise AssertionError("OBS_TRACE_PARTITION_ORACLES_DISAGREE")
    for domain,label in (("xor","reachable"),("paren","balanced"),("obs","equivalent")):
        hits=Counter(c[label] for c in data[domain])
        if hits[True]<12 or hits[False]<12:
            raise ValueError("ORACLE_IMBALANCED_TOO_FAR")
    return data


def main():
    rows=load_training()
    prompts,gold=load_holdout()
    oracle=load_oracles()
    print(json.dumps({
        "status":"TRAIN26_FROZEN_DATA_AND_INDEPENDENT_ORACLES_PASS",
        "training":len(rows),"holdout_prompts":len(prompts),
        "holdout_gold":len(gold),
        "finite_cases":sum(len(oracle[k]) for k in ("xor","paren","obs")),
        "git_blobs":PINS,
        "training_performed":False,
        "new_scientific_discoveries":0,
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
