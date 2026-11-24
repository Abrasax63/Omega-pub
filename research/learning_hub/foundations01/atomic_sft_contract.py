"""Frozen interface for the separate supervised atomic feasibility pilot."""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
from atomic_eval import KEYS,render,score
from atomic_curriculum import validate

MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
SEED=20261127
MAX_LENGTH=384

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_frozen(path,expected,kind):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("FROZEN_DIGEST_MISMATCH")
    rows=json.loads(raw)
    validate(rows,kind)
    return rows

def question(packet,view):
    text=render(packet,view).split(". ",1)[1]
    return ("Read the directed relation. For the ordered triple x,y,z, output exactly four bits "
            "in this order: whether x->y exists, whether y->z exists, whether x->z exists, "
            "whether the triple violates transitivity. Use 1 for true and 0 for false. "
            "No spaces or explanation. "+text)

def target(label):
    return "".join(str(int(label[k])) for k in KEYS)

def parse_bits(raw):
    if not isinstance(raw,str) or re.fullmatch("[01]{4}",raw) is None:
        return None
    return dict(zip(KEYS,[c=="1" for c in raw]))

def chat(tok,packet,view):
    return tok.apply_chat_template([{"role":"user","content":question(packet,view)}],
                                   tokenize=False,add_generation_prompt=True)

def score_pair(rows,records):
    validate(rows,"eval")
    expected={(arm,view,r["id"]) for arm in ("base","lora") for view in ("edges","matrix") for r in rows}
    if len(records)!=len(expected) or {(r["arm"],r["view"],r["id"]) for r in records}!=expected:
        raise ValueError("INCOMPLETE_PREDICTIONS")
    byid={r["id"]:r for r in rows}
    scores={}
    for arm in ("base","lora"):
        scores[arm]={}
        for view in ("edges","matrix"):
            predictions={}
            samples=[r for r in records if r["arm"]==arm and r["view"]==view]
            for r in samples:
                if r["prompt_sha256"]!=hashlib.sha256(question(byid[r["id"]]["packet"],view).encode()).hexdigest():
                    raise ValueError("PROMPT_HASH_MISMATCH")
                if type(r["output_tokens"]) is not int or not 0<=r["output_tokens"]<=16:
                    raise ValueError("OUTPUT_TOKEN_LIMIT")
                p=parse_bits(r["raw"])
                predictions[r["id"]]=json.dumps(p) if p is not None else "invalid"
            s=score(rows,predictions)
            s.update(input_tokens=sum(r["input_tokens"] for r in samples),
                     output_tokens=sum(r["output_tokens"] for r in samples),
                     seconds=sum(r["seconds"] for r in samples))
            scores[arm][view]=s
    comparisons={}
    for view in ("edges","matrix"):
        b=scores["base"][view]
        a=scores["lora"][view]
        delta=a["groups"]["all"]["joint"]-b["groups"]["all"]["joint"]
        both=all(a["groups"][c]["joint"]>b["groups"][c]["joint"] for c in ("positive","negative"))
        bmap={r["id"]:r["joint"] for r in b["rows"]}
        amap={r["id"]:r["joint"] for r in a["rows"]}
        paired=Counter(("both" if bmap[k] and amap[k] else "base_only" if bmap[k] else
                        "lora_only" if amap[k] else "neither") for k in bmap)
        comparisons[view]={"joint_delta":delta,"joint_delta_pp":100*delta/64,
                           "both_classes_improve":both,"paired":dict(paired),
                           "exploratory_gain":delta>=7 and both}
    return {"scores":scores,"comparisons":comparisons,
            "status":"EXPLORATORY_SUPERVISED_GAIN" if comparisons["edges"]["exploratory_gain"] else "NO_PREREGISTERED_GAIN",
            "autonomous_learning_demonstrated":False,"promotion_authorized":False,
            "retention_tested":False,"seeds":1}
