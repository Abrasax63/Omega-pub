"""Frozen contract for Omega ACTIVE-DEBUG01.

The model runner only calls public_view(), which excludes evaluator sources and
hidden observations. The grading runner alone imports evaluator_view().
Git blob digest pins every byte of this source, tests and model prompt.
"""
from __future__ import annotations
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FROZEN=HERE/"FROZEN_BENCHMARK.json"
FROZEN_BLOB="73ba10b629206dd3d771cb03048031157645ab38"
SCHEMA="OMEGA_ACTIVE_DEBUG01_FROZEN"
MODEL="Qwen2.5-Coder-3B-Instruct-Q4_K_M"
MODEL_SHA256="3da3afe6cf5c674ac195803ea0dd6fee7e1c228c2105c1ce8c66890d1d4ab460"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf"
SEED=20261123
MAX_TOKENS_PER_CALL=400
MAX_MODEL_CALLS=18
PUBLIC=2
HIDDEN=5
FAMILIES={
    "palindrome_csv","opening_parentheses_depth","hex_pair_values",
    "alternating_word_case","balanced_bracket_prefix",
    "alternating_digit_checksum",
}
SYSTEM=(
    "You are a Python program repair assistant. Fix only logic errors, not "
    "unrelated behavior. Read the given goal and public input/output examples. "
    "Your answer must contain ONLY a complete Python definition def transform(s) "
    "returning list[str], with no markdown or other top-level statements. "
    "No imports, network, files, eval, subprocess, introspection or dynamic execution."
)

def frozen():
    raw=FROZEN.read_bytes()
    if len(raw)>120000:
        raise ValueError("DATA_TOO_LARGE")
    digest=sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if digest!=FROZEN_BLOB:
        raise ValueError("FROZEN_CONTRACT_DRIFT")
    d=json.loads(raw)
    if d.get("schema")!=SCHEMA or d.get("model")!=MODEL:
        raise ValueError("WRONG_FROZEN_SCHEMA_OR_MODEL")
    rows=d.get("tasks")
    if not isinstance(rows,list) or len(rows)!=6:
        raise ValueError("WRONG_TASK_COUNT")
    families=[x["family"] for x in rows]
    if set(families)!=FAMILIES or len(set(families))!=6:
        raise ValueError("FAMILIES_MISMATCH")
    if len(set(x["id"] for x in rows))!=6:
        raise ValueError("DUPLICATE_TASKS")
    for x in rows:
        if (len(x["public_examples"])!=PUBLIC or len(x["hidden_tests"])!=HIDDEN
                or x.get("source_kind")!="CURATED_NEW_SYNTHETIC_NEVER_TRAINED"
                or x["reference_source_evaluator_only"]==x["broken_source"]
                or x["reference_source_evaluator_only"] in x["model_prompt"]
                or not x["broken_source"] in x["model_prompt"]
                or any("expected" not in j and "output" not in j
                       for j in x["public_examples"])):
            raise ValueError("INVALID_TASK_"+x["id"])
        if {k["input"] for k in x["hidden_tests"]} & {
                k["input"] for k in x["public_examples"]}:
            raise ValueError("VISIBLE_AND_HIDDEN_OVERLAP_"+x["id"])
        if any(len(z["input"])>24 for z in x["public_examples"]+x["hidden_tests"]):
            raise ValueError("INPUT_LIMIT_EXCEEDED")
    return d


def public_view():
    """Only this sanitized representation should be exposed to the model."""
    return [
        {"id":r["id"],"family":r["family"],"broken":r["broken_source"],
         "public":r["public_examples"],"prompt":r["model_prompt"]}
        for r in frozen()["tasks"]
    ]


def evaluator_view():
    """Trusted grading only, AFTER every model generation is written."""
    return frozen()["tasks"]


def hash_json(value):
    return sha256(json.dumps(value,sort_keys=True,
        ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
