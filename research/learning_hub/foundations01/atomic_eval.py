"""Prospective atomic evaluator. Does not load data, call a model or train.

Inputs must be supplied by the independent curator after predictions are frozen.
Exact JSON booleans only; invalid responses count as incorrect on all metrics.
Not a complete training or promotion gate (retention and budget checks separate).
"""
from collections import Counter
import json
from corpus_gate import identities, quotas

KEYS=("xy","yz","xz","violates")
ARMS=("base","supervised","self_generated")

def exact(packet):
    # Matrix lookup independent of the teacher's set-membership implementation.
    identities(packet)
    names=packet["nodes"]
    mat=[[False]*len(names) for _ in names]
    for a,b in packet["edges"]:
        mat[names.index(a)][names.index(b)]=True
    x,y,z=map(names.index,packet["triple"])
    a,b,c=mat[x][y],mat[y][z],mat[x][z]
    return dict(zip(KEYS,(a,b,c,a and b and not c)))

def render(packet, representation):
    identities(packet)
    if representation=="edges":
        data=packet
    elif representation=="matrix":
        names=packet["nodes"]
        data={"nodes":names,"matrix":[[int([a,b] in packet["edges"]) for b in names] for a in names],
              "triple":packet["triple"]}
    else:
        raise ValueError("UNKNOWN_REPRESENTATION")
    context=("Matrix rows are sources and columns are targets in nodes order. " if representation=="matrix" else
             "Edges are ordered source-target pairs. ")
    return ("Read the relation and return JSON with xy,yz,xz and violates. "+context+
            json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")))

def unique_keys(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[k]=v
    return result

def parse(raw):
    if not isinstance(raw,str) or len(raw)>4096:
        return None
    try:
        doc=json.loads(raw,object_pairs_hook=unique_keys)
    except (ValueError,TypeError,RecursionError):
        return None
    if type(doc) is not dict or set(doc)!=set(KEYS) or any(type(v) is not bool for v in doc.values()):
        return None
    return doc

def score(tasks, predictions):
    if type(predictions) is not dict or not tasks:
        raise ValueError("INVALID_INPUT")
    ids=[t["id"] for t in tasks]
    if len(set(ids))!=len(ids) or set(ids)!=set(predictions):
        raise ValueError("MISSING_OR_DUPLICATE_ID")
    groups={}
    rows=[]
    for t in tasks:
        target=exact(t["packet"])
        prediction=parse(predictions[t["id"]])
        valid=prediction is not None
        reading=valid and all(prediction[k]==target[k] for k in KEYS[:3])
        decision=valid and prediction["violates"]==target["violates"]
        consistent=valid and prediction["violates"]==(prediction["xy"] and prediction["yz"] and not prediction["xz"])
        joint=reading and decision
        motif="".join(str(int(target[k])) for k in KEYS[:3])
        row={"id":t["id"],"motif":motif,"positive":target["violates"],"valid":valid,
             "reading":reading,"decision":decision,"consistent":consistent,"joint":joint}
        rows.append(row)
        for label in ("all","positive" if target["violates"] else "negative",motif):
            counts=groups.setdefault(label,Counter())
            counts["n"]+=1
            for k in ("valid","reading","decision","consistent","joint"):
                counts[k]+=int(row[k])
    return {"groups":{k:dict(v) for k,v in groups.items()},"rows":rows}

def compare_atomic(tasks,predictions):
    """Check preregistered *atomic* gain, not full promotion authorization."""
    if set(predictions)!=set(ARMS) or len(tasks)!=128:
        raise ValueError("WRONG_HOLDOUT_OR_ARMS")
    keys=[identities(t["packet"])[1] for t in tasks]
    if len(set(keys))!=len(keys):
        raise ValueError("DUPLICATE_HOLDOUT_TASK")
    counts=Counter("".join(str(int(exact(t["packet"])[k])) for k in KEYS[:3]) for t in tasks)
    if dict(counts)!=quotas(128):
        raise ValueError("UNBALANCED_HOLDOUT")
    scores={a:score(tasks,predictions[a]) for a in ARMS}
    base=scores["base"]["groups"]
    comparisons={}
    for arm in ARMS[1:]:
        g=scores[arm]["groups"]
        delta=g["all"]["joint"]-base["all"]["joint"]
        # >= 10 percentage points on 128 tasks => at least 13 extra successes.
        both=all(g[c]["joint"]>base[c]["joint"] for c in ("positive","negative"))
        comparisons[arm]={"joint_delta_count":delta,"joint_delta_pp":100*delta/128,
                          "both_classes_improve":both,"atomic_gain":10*delta>=128 and both}
    return {"scores":scores,"comparisons":comparisons,
            "self_minus_supervised_joint":scores["self_generated"]["groups"]["all"]["joint"]-
                scores["supervised"]["groups"]["all"]["joint"],
            "promotion_authorized":False,
            "limitations":"Retention, matched training budget, split isolation, weights and replication not established by this scorer."}
