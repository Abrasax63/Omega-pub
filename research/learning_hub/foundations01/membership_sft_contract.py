"""Membership SFT01 interface and post-inference scorer."""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
from membership_curriculum import validate
from atomic_sft_contract import MODEL,REV,MAX_LENGTH,sha
SEED=20261129

def read_frozen(path,expected,kind):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError("FROZEN_DIGEST")
    rows=json.loads(raw);validate(rows,kind)
    return rows

def question(p,view):
    x,y=p["triple"][:2];ns=p["nodes"]
    if view=="edges":
        data={"nodes":ns,"edges":p["edges"]}
        info="Edges are ordered source-target pairs."
    elif view=="matrix":
        data={"nodes":ns,"matrix":[[int([a,b] in p["edges"]) for b in ns] for a in ns]}
        info="Matrix rows are sources and columns are targets in nodes order."
    else: raise ValueError("VIEW")
    return f"In this directed relation, does the edge {x} to {y} exist? Answer exactly Yes or No. {info} "+json.dumps(data,separators=(",",":"),sort_keys=True)

def chat(tok,p,view):
    return tok.apply_chat_template([{"role":"user","content":question(p,view)}],tokenize=False,add_generation_prompt=True)

def target(label):
    if type(label) is not bool: raise ValueError("LABEL")
    return "Yes" if label else "No"

def prefix(raw):
    m=re.match(r"^(Yes|No)\b",raw,re.IGNORECASE)
    return m.group(1).capitalize() if m else None

def score_pair(rows,records):
    validate(rows,"eval")
    expected={(a,v,r["id"]) for a in ("base","lora") for v in ("edges","matrix") for r in rows}
    if len(records)!=len(expected) or {(r["arm"],r["view"],r["id"]) for r in records}!=expected: raise ValueError("COVERAGE")
    byid={r["id"]:r for r in rows};families={}
    for r in rows: families.setdefault(r["pair"],[]).append(r["id"])
    scores={};hits={}
    for a in ("base","lora"):
        scores[a]={}
        for v in ("edges","matrix"):
            group=[r for r in records if r["arm"]==a and r["view"]==v]
            strict={};pre={};binary={};probs={};counts=Counter();outputs=Counter()
            for r in group:
                i=r["id"];t=byid[i];gold=target(t["label"]);raw=r["raw"]
                if r["prompt_sha256"]!=hashlib.sha256(question(t["packet"],v).encode()).hexdigest(): raise ValueError("PROMPT_HASH")
                if len(r["token_ids"])!=r["output_tokens"] or not 0<=r["output_tokens"]<=8: raise ValueError("TOKEN_TRACE")
                strict[i]=raw==gold;pre[i]=prefix(raw)==gold
                outputs[raw]+=1;counts["valid"]+=int(raw in ("Yes","No"))
                counts["correct_"+gold]+=int(strict[i]);counts["size_"+str(len(t["packet"]["nodes"]))]+=int(strict[i])
                if r.get("p_yes") is not None:
                    y,n=r["p_yes"],r["p_no"]
                    if not 0<=y<=1 or not 0<=n<=1 or not 0<y+n<=1.000001: raise ValueError("PROBABILITY")
                    probs[i]=y/(y+n);binary[i]=("Yes" if y>n else "No")==gold
            if probs and len(probs)!=64: raise ValueError("INCOMPLETE_PROBABILITIES")
            contrasts=[]
            for ids in families.values():
                neg,pos=sorted(ids,key=lambda i:byid[i]["label"])
                if probs: contrasts.append(probs[pos]-probs[neg])
            hits[a,v]=strict
            scores[a][v]={"correct":sum(strict.values()),"valid":counts["valid"],
                "correct_yes":counts["correct_Yes"],"correct_no":counts["correct_No"],
                "pairs_both_correct":sum(all(strict[i] for i in ids) for ids in families.values()),
                "prefix_correct":sum(pre.values()),"prefix_pairs_both_correct":sum(all(pre[i] for i in ids) for ids in families.values()),
                "binary_correct":sum(binary.values()) if binary else None,
                "binary_pairs_both_correct":sum(all(binary[i] for i in ids) for ids in families.values()) if binary else None,
                "mean_toggle_probability_difference":sum(contrasts)/len(contrasts) if contrasts else None,
                "positive_toggle_contrasts":sum(x>0 for x in contrasts) if contrasts else None,
                "outputs":dict(outputs),"correct_size5":counts["size_5"],"correct_size6":counts["size_6"],
                "input_tokens":sum(r["input_tokens"] for r in group),"output_tokens":sum(r["output_tokens"] for r in group),
                "seconds":sum(r["seconds"] for r in group)}
    comparisons={}
    for v in ("edges","matrix"):
        b=hits["base",v];l=hits["lora",v];s=scores["lora"][v];d=s["correct"]-scores["base"][v]["correct"]
        comparisons[v]={"delta":d,"paired":dict(Counter("both" if b[i] and l[i] else "base_only" if b[i] else "lora_only" if l[i] else "neither" for i in b)),
            "signal":s["correct"]>=48 and s["pairs_both_correct"]>=20 and min(s["correct_yes"],s["correct_no"])>=20 and d>=8}
    return {"scores":scores,"comparisons":comparisons,"status":"EXPLORATORY_MEMBERSHIP_GAIN" if comparisons["edges"]["signal"] else "NO_PREREGISTERED_GAIN","promotion_authorized":False,"autonomous_learning_demonstrated":False}
