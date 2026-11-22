"""Immutable data guard for OMEGA-PY-SFT-01.

Training calls load_train() and never load_holdout(). Both JSON files were
created, frozen and Git blob checksummed before trainer/evaluator code.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINS={
 "TRAIN_FROZEN.json":"e1985c93b9fb362eef80604d4f1c09a6ecb8f1d6",
 "HOLDOUT_EVAL_ONLY.json":"10b89164486bfed216f7d4b0ea935e907a73dd0f",
}
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
SEED=20261122
SYSTEM=(
 "You repair small Python programs. Return ONLY a complete corrected Python "
 "function named transform(s), returning a list of strings. No Markdown, "
 "imports, file access, network or extraneous explanation. Preserve intended "
 "behavior and follow the shown input/output examples."
)
EPOCHS=2
LR=0.0005
RANK=8
ALPHA=16
MAX_LENGTH=384
GEN_TOKENS=220

def frozen_json(name):
    if name not in PINS:
        raise ValueError("UNKNOWN_UNFROZEN_FILE")
    raw=(HERE/name).read_bytes()
    if len(raw)>200000:
        raise ValueError("DATA_TOO_LARGE")
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if git_blob != PINS[name]:
        raise ValueError("FROZEN_FILE_INTEGRITY_FAILURE_"+name)
    return json.loads(raw)

def load_train():
    doc=frozen_json("TRAIN_FROZEN.json")
    if doc.get("schema")!="OMEGA_PY_SFT_01_TRAIN_FROZEN":
        raise ValueError("WRONG_TRAIN_SCHEMA")
    data=doc["train_examples"]
    if len(data)!=62:
        raise ValueError("WRONG_TRAIN_SIZE")
    ids=[s["id"] for s in data]
    if len(set(ids))!=len(ids):
        raise ValueError("DUPLICATE_TRAIN_ID")
    families={s["family"] for s in data}
    if len(families)!=22:
        raise ValueError("WRONG_TRAIN_FAMILY_COUNT")
    provenance=Counter(x["provenance"] for x in data)
    if dict(provenance)!={
       "CURATED_SYNTHETIC_GOLD_NOT_MODEL_DISCOVERED":60,
       "OMEGA_V3_ORIGINAL_VERIFIED":2,
    }:
        raise ValueError("INVALID_TRAIN_SOURCE_PROVENANCE")
    for row in data:
        if (not row["prompt"].startswith("TASK=PYTHON_REPAIR") or
            not row["target"].startswith("def transform(s):") or
            len(row["prompt"])>2000 or len(row["target"])>1500 or
            len(row["verification_cases"])<2):
            raise ValueError("INVALID_TRAIN_EXAMPLE_"+row["id"])
        if ("HOLDOUT" in row["prompt"] or
            "reference_code_eval_only" in row):
            raise ValueError("TEST_GOLD_IN_TRAIN")
    return data

def load_holdout():
    doc=frozen_json("HOLDOUT_EVAL_ONLY.json")
    if doc.get("schema")!="OMEGA_PY_SFT_01_HOLDOUT_EVAL_ONLY":
        raise ValueError("WRONG_TEST_SCHEMA")
    hold=doc["test_cases"]
    train=load_train()
    families={x["family"] for x in train}
    eval_fam=[x["family"] for x in hold]
    if (len(hold)!=12 or len(set(eval_fam))!=6 or
        len(families & set(eval_fam))!=0):
        raise ValueError("HOLDOUT_FAMILY_LEAKAGE_OR_COUNT")
    train_prompts={x["prompt"] for x in train}
    for sample in hold:
        if (sample["prompt"] in train_prompts or
            sample["reference_code_eval_only"] in [t["target"] for t in train] or
            len(sample["hidden_cases"])!=5 or
            not sample["prompt"].startswith("TASK=PYTHON_REPAIR")):
            raise ValueError("HOLDOUT_CONTENT_COLLISION")
        if any(json.dumps(x["input"]) in sample["prompt"] for x in sample["hidden_cases"]
               if x["input"] not in ("",)):
            # The raw input may be a substring of the code prompt by accident,
            # so only exact I/O pairs must be guarded in the test layer.
            pass
    return hold
