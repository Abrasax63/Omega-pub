"""RETENTION16: matched-budget replay design. Tokenizer-only; no training.
Both arms share the first 32 new-skill pairs. The second 32 pairs are
either balanced old-skill replay or additional new-skill examples.
Intermediate evaluation can isolate the effect of the additional block.
"""
import argparse, json, random
from collections import defaultdict, Counter
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import retention15 as r
import loop09 as l

SEED=2026112516
TRIALS=2048
FIELDS=l.FIELDS
def need(ok,msg):
    if not ok:raise ValueError(msg)
def pairs(rows):
    g=defaultdict(list)
    for z in rows:g[z["pair"]].append(z)
    need(all(len(z)==2 for z in g.values()),"PAIR")
    return dict(sorted(g.items()))
def encode(tok,g):
    out={}
    for p,z in g.items():
        a,b=z
        out[a["id"]]=t.encode(tok,a,b["gold"])
        out[b["id"]]=t.encode(tok,b,a["gold"])
    return out
def vec(enc,g,p):
    return l.vector(enc,[z["id"] for z in g[p]])
def add(*vs):
    return tuple(sum(x) for x in zip(*vs))
def spread(a,b):
    return tuple(abs(x-y)/min(x,y) for x,y in zip(a,b))
def design(old,new,enc,trials=TRIALS):
    c.validate(old,"train");r.validate(new,"train")
    go,gn=pairs(old),pairs(new)
    need(not set(go)&set(gn),"PAIR_IDS")
    need(not {z["id"] for z in old}&{z["id"] for z in new},"EXAMPLE_IDS")
    rng=random.Random(SEED)
    # Fixed shared prefix, same exact order in both arms.
    newkeys=list(gn);rng.shuffle(newkeys);shared=newkeys[:32];extra=newkeys[32:]
    v={p:vec(enc,g,p) for g in (go,gn) for p in g}
    common=add(*(v[p] for p in shared))
    target=add(common,*(v[p] for p in extra))
    by={k:[p for p,z in go.items() if z[0]["kind"]==k] for k in c.KINDS}
    best=None
    for _ in range(trials):
        replay=[p for k in c.KINDS for p in rng.sample(by[k],8)]
        candidate=add(common,*(v[p] for p in replay))
        gaps=spread(candidate,target)
        key=(max(gaps),sum(gaps),tuple(sorted(replay)))
        if best is None or key<best[0]:best=(key,replay,candidate,gaps)
    _,replay,candidate,gaps=best;rng.shuffle(replay)
    need(len(set(shared+extra))==64 and len(set(shared+replay))==64,"UNIQUE")
    need(Counter(go[p][0]["kind"] for p in replay)=={k:8 for k in c.KINDS},"REPLAY_BALANCE")
    allg={**go,**gn}
    plans={k:[[z["id"] for z in allg[p]] for p in ps] for k,ps in (("new_only",shared+extra),("replay",shared+replay))}
    need(plans["new_only"][:32]==plans["replay"][:32],"COMMON_PREFIX")
    return dict(plans=plans,shared_steps=32,steps_per_arm=64,examples_per_arm=128,forward_sequences_per_arm=256,padded_positions_per_arm=256*t.MAX_LENGTH,new_examples={"new_only":128,"replay":64},old_examples={"new_only":0,"replay":64},replay_pairs_per_old_skill=8,budgets={"new_only":dict(zip(FIELDS,target)),"replay":dict(zip(FIELDS,candidate))},relative_spread=dict(zip(FIELDS,gaps)),budget_within_2_percent=max(gaps)<=l.TOL,search_trials=trials,search_is_exhaustive=False,training_authorized=False,interpretation="equal steps, different new-skill exposure by design; checkpoint at shared prefix is dose-matched reference")
def datasets():
    return c.build("train",t.SEED),r.build("train",20261125)
def selftest():
    old,new=datasets()
    enc={z["id"]:[dict(input_ids=[0]*40,target_tokens=4),dict(input_ids=[0]*40,target_tokens=4)] for z in old+new}
    d=design(old,new,enc,32);need(d["budget_within_2_percent"],"EQUAL_FIXTURE")
    need(design(old,new,enc,32)==d,"DETERMINISM")
    # Infeasible fixture: all old examples have much shorter target sequences.
    for z in old:
        for q in enc[z["id"]]:q["target_tokens"]=1
    bad=design(old,new,enc,32);need(not bad["budget_within_2_percent"] and not bad["training_authorized"],"INFEASIBLE_FIXTURE")
    print("RETENTION16 scheduling and fail-closed controls passed")
def preflight(out):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    old,new=datasets()
    enc={**encode(tok,pairs(old)),**encode(tok,pairs(new))}
    d=design(old,new,enc)
    d.update(status="TOKENIZER_BUDGET_AUDIT",revision=c.REV,scope="same-author training fixtures; no model execution or independent exam")
    Path(out).write_text(json.dumps(d,indent=2))
    print(json.dumps({k:v for k,v in d.items() if k!="plans"},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","preflight"]);p.add_argument("--out");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:preflight(a.out)
