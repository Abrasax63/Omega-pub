"""CAPACITY-01 frozen corpus and independent scoring, no model imports."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from corpus_gate import identities
from membership_curriculum import create as membership_create,validate as membership_validate
from atomic_curriculum import create as atomic_create
from membership_sft_contract import question as edge_question,prefix

MODELS={"135m":("HuggingFaceTB/SmolLM2-135M-Instruct","ee72e5415c002e8fc0566a191a07c0b2b708875a"),
        "360m":("HuggingFaceTB/SmolLM2-360M-Instruct","a10cc15")}
VIEWS=("edges","adjacency")
SEED=20261130

def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def question(p,view):
    if view=="edges": return edge_question(p,view)
    if view!="adjacency": raise ValueError("VIEW")
    x,y=p["triple"][:2];ns=p["nodes"]
    data={"nodes":ns,"outgoing":{a:[b for b in ns if [a,b] in p["edges"]] for a in ns}}
    return f"In this directed relation, does the edge {x} to {y} exist? Answer exactly Yes or No. Outgoing lists show all targets of each source. "+json.dumps(data,separators=(",",":"),sort_keys=True)

def create():
    # Regenerate known consumed holdouts; check exact byte hashes before exclusion.
    prior=[]
    for rows,h in [(atomic_create(8591958126413765487,"eval"),"489a32cf84079164faf6461ac284526d01e2425b92cb6af64dcb80d65af942ec"),
                   (membership_create(17570745935616618759,"eval"),"ba4c154b6bcd571194bf72d4e33c416c42cbac8c5466059383553eea079d9e52")]:
        raw=json.dumps(rows,sort_keys=True,separators=(",",":"))
        if digest(raw)!=h: raise ValueError("PRIOR_HOLDOUT_HASH")
        prior.extend(rows)
    forbidden={identities(r["packet"])[0] for r in prior}
    candidates=membership_create(SEED,"eval")
    membership_validate(candidates,"eval")
    groups={}
    for r in candidates: groups.setdefault(r["pair"],[]).append(r)
    selected=[];counts=Counter()
    for pair,group in sorted(groups.items()):
        n=len(group[0]["packet"]["nodes"])
        if counts[n]>=8 or any(identities(r["packet"])[0] in forbidden for r in group): continue
        counts[n]+=1
        for r in group:
            # Opaque identifiers contain no answer bit or pair ordering.
            selected.append(dict(id=digest("CAPACITY01/"+r["id"])[:20],pair=digest("CAPACITY01/"+pair)[:20],
                                 packet=r["packet"],label=r["label"]))
    validate(selected)
    return sorted(selected,key=lambda r:r["id"])

def validate(rows):
    if len(rows)!=32 or len({r["id"] for r in rows})!=32: raise ValueError("COUNT")
    keys=set();groups={};counts=Counter()
    for r in rows:
        p=r["packet"];ns=p["nodes"];x,y,z=p["triple"]
        g,_=identities(p)
        if g in keys or len(ns) not in (5,6) or x==y or x!=z: raise ValueError("GRAPH")
        keys.add(g)
        if type(r["label"]) is not bool: raise ValueError("LABEL_TYPE")
        mat=[[False]*len(ns) for _ in ns]
        for a,b in p["edges"]: mat[ns.index(a)][ns.index(b)]=True
        if r["label"]!=mat[ns.index(x)][ns.index(y)]: raise ValueError("LABEL")
        groups.setdefault(r["pair"],[]).append(r)
    for pair in groups.values():
        if len(pair)!=2 or {r["label"] for r in pair}!={False,True}: raise ValueError("PAIR")
        a,b=sorted(pair,key=lambda r:r["label"])
        p,q=a["packet"],b["packet"]
        if p["nodes"]!=q["nodes"] or p["triple"]!=q["triple"]: raise ValueError("PAIR_CONTEXT")
        e,f=({tuple(x) for x in t["edges"]} for t in (p,q))
        if f-e!={tuple(p["triple"][:2])} or e-f: raise ValueError("PAIR_TOGGLE")
        counts[len(p["nodes"])]+=1
    if counts!={5:8,6:8}: raise ValueError("PAIR_COUNTS")
    return {"examples":32,"pairs":16,"distinct_graphs":32}

def score(rows,records,pins):
    validate(rows)
    expected={(a,v,r["id"]) for a in MODELS for v in VIEWS for r in rows}
    if len(records)!=len(expected) or {(r["arm"],r["view"],r["id"]) for r in records}!=expected: raise ValueError("COVERAGE")
    byid={r["id"]:r for r in rows};groups={}
    for r in rows: groups.setdefault(r["pair"],[]).append(r["id"])
    scores={}
    for a in MODELS:
        scores[a]={}
        for v in VIEWS:
            rs=[r for r in records if r["arm"]==a and r["view"]==v]
            hits={};pre={};probs={};binary={};counts=Counter();outputs=Counter()
            for r in rs:
                i=r["id"];t=byid[i];gold="Yes" if t["label"] else "No";raw=r["raw"]
                if r["revision"]!=pins[a]["revision"] or r["prompt"]!=question(t["packet"],v) or r["prompt_sha256"]!=digest(r["prompt"]) or r["raw_sha256"]!=digest(raw): raise ValueError("TRACE")
                if len(r["token_ids"])!=r["output_tokens"] or not 0<=r["output_tokens"]<=8: raise ValueError("TOKEN_LIMIT")
                hits[i]=raw==gold;pre[i]=prefix(raw)==gold
                counts["valid"]+=int(raw in ("Yes","No"))
                counts[gold]+=int(hits[i]);outputs[raw]+=1
                y,n=r["p_yes"],r["p_no"]
                if (y is None)!=(n is None): raise ValueError("PROBABILITY")
                if y is not None:
                    if not 0<=y<=1 or not 0<=n<=1 or not 0<y+n<=1.000001: raise ValueError("PROBABILITY")
                    probs[i]=y/(y+n);binary[i]=("Yes" if y>n else "No")==gold
            if probs and len(probs)!=32: raise ValueError("INCOMPLETE_PROBABILITIES")
            contrasts=[probs[max(ids,key=lambda i:byid[i]["label"])]-probs[min(ids,key=lambda i:byid[i]["label"])] for ids in groups.values()] if probs else []
            pairs=sum(all(hits[i] for i in ids) for ids in groups.values())
            scores[a][v]={"strict_correct":sum(hits.values()),"strict_valid":counts["valid"],"yes_correct":counts["Yes"],"no_correct":counts["No"],
                "pairs_both_correct":pairs,"prefix_correct":sum(pre.values()),"prefix_pairs":sum(all(pre[i] for i in ids) for ids in groups.values()),
                "binary_correct":sum(binary.values()) if binary else None,"mean_toggle_contrast":sum(contrasts)/len(contrasts) if contrasts else None,
                "positive_contrasts":sum(x>0 for x in contrasts) if contrasts else None,"outputs":dict(outputs),
                "input_tokens":sum(r["input_tokens"] for r in rs),"output_tokens":sum(r["output_tokens"] for r in rs),"seconds":sum(r["seconds"] for r in rs),
                "signal":sum(hits.values())>=24 and pairs>=10 and min(counts["Yes"],counts["No"])>=10}
    return {"scores":scores,"exact_reference":{"correct":32,"pairs":16},"constant_reference":{"correct":16,"pairs":0},
            "status":"EXPLORATORY_FEASIBILITY_SIGNAL" if any(s["signal"] for views in scores.values() for s in views.values()) else "NO_FEASIBILITY_SIGNAL",
            "weight_updates":0,"promotion_authorized":False,"autonomous_learning_demonstrated":False}
