#!/usr/bin/env python3
"""Dataset integrity and reference truth independent of trainable model."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
FROZEN={
"TRAIN_FROZEN.json":"b293a5db37bb059a7eb4264956e05614a8d08a6a",
"HOLDOUT_PROMPTS_FROZEN.json":"558b5a1e56880ea1880bb697240d9e522440a88a",
"HOLDOUT_GOLD_EVAL_ONLY.json":"a2ca1b62f02eb1b75b202029a7d60d7f20e157b4",
"FINITE_ORACLE_CASES_FROZEN.json":"7bf8e7952e026f4cb3ef00f3d28b064c4d809524",
}
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
SEED=20261119
SYSTEM=("You are a research formalization assistant. Given a well-defined "
        "mathematical task, output exactly one line containing an expression "
        "that preserves its meaning. If outside supported knowledge, "
        "reply exactly ABSTAIN. No markdown, no explanation.")
XOR="EXPR: rank(moves) == rank(moves + [start ^ target])"
PAREN="EXPR: sum_balance(s) == 0 and min_prefix_balance(s) >= 0"
ABSTAIN="ABSTAIN"


def checked(name):
    if name not in FROZEN:
        raise ValueError("UNREGISTERED_FILE")
    raw=(HERE/name).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=FROZEN[name]:
        raise ValueError("FROZEN_SOURCE_DRIFT: "+name)
    return json.loads(raw)


def validate_train():
    data=checked("TRAIN_FROZEN.json")["train"]
    if len(data)!=96 or len({x["prompt"] for x in data})!=96:
        raise AssertionError("TRAIN_SIZE_OR_DUPLICATES")
    domains={"xor_reachability":(48,XOR),
             "parenthesis_balance":(36,PAREN),
             "unsupported":(12,ABSTAIN)}
    counts={}
    for x in data:
        counts[x["domain"]]=counts.get(x["domain"],0)+1
        if x["domain"] not in domains or x["target"]!=domains[x["domain"]][1]:
            raise AssertionError("TRAIN_TARGET_WRONG")
    if any(counts.get(k)!=n for k,(n,_) in domains.items()):
        raise AssertionError("TRAIN_DOMAIN_COUNTS")
    return data


def validate_holdout():
    prompts=checked("HOLDOUT_PROMPTS_FROZEN.json")["prompts"]
    labels=checked("HOLDOUT_GOLD_EVAL_ONLY.json")["labels"]
    train=validate_train()
    if len(prompts)!=24 or len(labels)!=24:
        raise AssertionError("HOLDOUT_SIZE")
    if len({p["prompt"] for p in prompts})!=24:
        raise AssertionError("HOLDOUT_DUPLICATE")
    if {p["prompt"] for p in prompts}&{p["prompt"] for p in train}:
        raise AssertionError("HOLDOUT_EXACT_TEXT_LEAK")
    if [x["id"] for x in prompts]!=[x["id"] for x in labels]:
        raise AssertionError("HOLDOUT_ID_ORDER")
    domain_counts={}
    for x in labels:
        domain_counts[x["domain"]]=domain_counts.get(x["domain"],0)+1
        expected=XOR if x["domain"]=="xor_reachability" else (
            PAREN if x["domain"]=="parenthesis_balance" else ABSTAIN)
        if x["target"]!=expected: raise AssertionError("GOLD_UNEXPECTED_LABEL")
    if domain_counts!={"xor_reachability":6,"parenthesis_balance":6,
                       "unsupported":6,"transfer_unseen":6}:
        raise AssertionError("HOLDOUT_DOMAIN_SPLIT")
    return prompts,labels


def bfs_reachable(c):
    start=c["start"]; target=c["target"]
    seen={start}; queue=[start]
    for x in queue:
        if x==target:return True
        for m in c["moves"]:
            y=x^m
            if y not in seen:
                seen.add(y);queue.append(y)
    return False


def strong_gf2(c):
    basis=[0]*c["n"]
    for w in c["moves"]:
        v=w
        while v:
            bit=v.bit_length()-1
            if basis[bit]:
                v^=basis[bit]
            else:
                basis[bit]=v
                break
    v=c["start"]^c["target"]
    while v:
        bit=v.bit_length()-1
        if not basis[bit]:
            return False
        v^=basis[bit]
    return True


def direct_paren(s):
    stack=0
    for c in s:
        if c not in "()":raise ValueError("NONPAREN")
        stack+=1 if c=="(" else -1
        if stack<0:return False
    return stack==0


def validate_finite_oracles():
    data=checked("FINITE_ORACLE_CASES_FROZEN.json")
    xx=data["xor"]; pp=data["parentheses"]
    assert len(xx)==12 and len(pp)==12
    assert sum(x["reachable"] for x in xx)==6
    assert sum(x["balanced"] for x in pp)==6
    for c in xx:
        if bfs_reachable(c)!=c["reachable"] or strong_gf2(c)!=c["reachable"]:
            raise AssertionError("EXACT_GF2_ORACLE_DISAGREEMENT: "+c["id"])
    for x in pp:
        if direct_paren(x["s"])!=x["balanced"]:
            raise AssertionError("PAREN_ORACLE_DISAGREEMENT: "+x["id"])
    return data


def main():
    train=validate_train()
    held,labels=validate_holdout()
    finite=validate_finite_oracles()
    print(json.dumps({
        "status":"FROZEN_DATA_AND_ORACLES_PASS",
        "train":len(train),"holdout":len(held),
        "xor_oracle":len(finite["xor"]),"parenthesis_oracle":len(finite["parentheses"]),
        "source_git_blobs":FROZEN,
        "weight_update_executed":False,
    },indent=2))


if __name__=="__main__":
    main()
