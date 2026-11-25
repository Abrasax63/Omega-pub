"""CURRICULUM06: offline data and adaptive scheduling gate; never trains."""
import argparse, hashlib, json, random
from pathlib import Path
from collections import Counter, defaultdict
KINDS=("copy","select","membership","reverse")
MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REV="c89bee90d9f811437d9735454613c35b4a3c4dc8"
# Disjoint artificial vocabulary per split. Holdout additionally uses unseen templates.
SPLITS=("train","dev","holdout")
COUNTS={"train":128,"dev":32,"holdout":64}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def vocab(split):
    # Synthetic strings avoid reuse of previous natural-word fixtures.
    prefix={"train":"ba","dev":"di","holdout":"fo"}[split]
    return [prefix+a+b for a in "klmnprst" for b in "aeiou"]
def render(k,items,p,t,split):
    s=" ".join(items)
    if split=="holdout":
        return {"copy":f"Reproduce both words unchanged: {s}","reverse":f"Write the second word followed by the first: {s}","select":f"Identify the item at position {p}, starting at one: {s}","membership":f"Does the list {s} contain the word {t}? Answer Yes or No."}[k]
    return {"copy":f"Copy these words exactly: {s}","reverse":f"Reverse the order of the two words: {s}","select":f"Return word number {p}, counting from 1: {s}","membership":f"Is {t} in the list {s}? Answer Yes or No."}[k]
def gold(r):
    x=r["items"];k=r["kind"]
    return " ".join(x) if k=="copy" else " ".join(x[::-1]) if k=="reverse" else x[r["pos"]-1] if k=="select" else "Yes" if r["target"] in x else "No"
def build(split,seed):
    rng=random.Random(seed);words=vocab(split);rows=[];seen=set();n=COUNTS[split]
    for k in KINDS:
        for i in range(n//2):
            for _ in range(10000):
                p=i%4+1;t=None
                if k in ("copy","reverse"):
                    x=rng.sample(words,2);xs=[x,x[::-1]]
                elif k=="select":
                    x=rng.sample(words,4);y=x.copy();q=(p+i//4)%4
                    if q==p-1:q=(q+1)%4
                    y[p-1],y[q]=y[q],y[p-1];xs=[x,y]
                else:
                    t,*x=rng.sample(words,4);y=x.copy();y[i%3]=t;xs=[x,y]
                ps=[render(k,x,p,t,split) for x in xs]
                if len(set(ps))==2 and not set(ps)&seen:break
            else:raise ValueError("GENERATION_BUDGET")
            seen.update(ps)
            for j,x in enumerate(xs):
                r=dict(id=f"{split}-{k}-{i}-{j}",split=split,kind=k,pair=f"{split}-{k}-{i}",items=x,pos=p if k=="select" else None,target=t if k=="membership" else None,prompt=ps[j]);r["gold"]=gold(r);rows.append(r)
    rng.shuffle(rows);return rows
def groups(rows):
    g=defaultdict(list)
    for r in rows:g[r["pair"]].append(r)
    return g
def validate(rows,split):
    n=COUNTS[split];need(len(rows)==n*4 and len({r["id"] for r in rows})==len(rows) and len({r["prompt"] for r in rows})==len(rows),"COVERAGE")
    need(Counter(r["kind"] for r in rows)=={k:n for k in KINDS},"BALANCE")
    need(Counter(r["pos"] for r in rows if r["kind"]=="select")=={i:n//4 for i in range(1,5)},"POSITION")
    for r in rows:
        need(r["split"]==split and set(r["items"])<=set(vocab(split)) and len(r["items"])==len(set(r["items"])),"SPLIT")
        need(r["target"] is None or r["target"] in vocab(split),"TARGET")
        need(r["gold"]==gold(r) and r["prompt"]==render(r["kind"],r["items"],r["pos"],r["target"],split),"ORACLE")
    for z in groups(rows).values():
        need(len(z)==2 and z[0]["kind"]==z[1]["kind"] and z[0]["gold"]!=z[1]["gold"],"PAIR")
        a,b=z;k=a["kind"]
        if k in ("copy","reverse"):need(a["items"]==b["items"][::-1],"REVERSE_PAIR")
        elif k=="select":need(a["pos"]==b["pos"] and sorted(a["items"])==sorted(b["items"]) and sum(x!=y for x,y in zip(a["items"],b["items"]))==2,"SWAP")
        else:need(a["target"]==b["target"] and {a["gold"],b["gold"]}=={"Yes","No"} and sum(x!=y for x,y in zip(a["items"],b["items"]))==1,"MEMBERSHIP_PAIR")
def schedule(train,strategy,seed,dev_pair_errors=None):
    validate(train,"train");rng=random.Random(seed);g=groups(train);by=defaultdict(list)
    for p,z in g.items():by[z[0]["kind"]].append(p)
    # Every arm gets 128 pairs = 256 examples per block.
    # Adaptive uses dev error rates aggregated by skill, never dev examples.
    weights={k:32 for k in KINDS}
    if strategy=="adaptive":
        need(isinstance(dev_pair_errors,dict) and set(dev_pair_errors)==set(KINDS) and all(type(v)==int and 0<=v<=16 for v in dev_pair_errors.values()),"DEV_ERRORS")
        weights={k:16 for k in KINDS}
        for _ in range(64):
            k=max(KINDS,key=lambda k:((dev_pair_errors[k]+1)/(weights[k]+1),-KINDS.index(k)));weights[k]+=1
    elif strategy not in ("supervised","contrastive"):raise ValueError("STRATEGY")
    chosen=[]
    for k in KINDS:
        pool=by[k][:];rng.shuffle(pool)
        chosen.extend(pool[i%len(pool)] for i in range(weights[k]))
    rng.shuffle(chosen)
    if strategy=="supervised":
        ids=[r["id"] for p in chosen for r in g[p]];rng.shuffle(ids)
        batches=[ids[i:i+2] for i in range(0,len(ids),2)]
    else:batches=[[r["id"] for r in g[p]] for p in chosen]
    need(len(batches)==128 and all(len(z)==2 for z in batches),"BUDGET")
    return dict(strategy=strategy,batches=batches,skill_pairs=weights,examples=256,optimizer_steps=128,loss="cross_entropy" if strategy=="supervised" else "cross_entropy_plus_pair_margin_PROPOSED_NOT_IMPLEMENTED" if strategy=="contrastive" else "cross_entropy")
def gate():
    # This artifact is deliberately not an execution authorizer.
    return dict(training_authorized=False,reason="HYBRID05 evidence, independent curator, actual tokenizer budget matching, trainer/contrastive loss tests and explicit release gate still required")
def selftest():
    data={s:build(s,20261125+i) for i,s in enumerate(SPLITS)}
    for s,z in data.items():validate(z,s)
    for i,a in enumerate(SPLITS):
        for b in SPLITS[i+1:]:need(not set(vocab(a))&set(vocab(b)) and not {r["prompt"] for r in data[a]}&{r["prompt"] for r in data[b]},"LEAK")
    tr=data["train"];ids={r["id"]:r for r in tr}
    errors=dict(copy=2,select=14,membership=16,reverse=1)
    plans=[schedule(tr,s,1234,errors if s=="adaptive" else None) for s in ("supervised","contrastive","adaptive")]
    for p in plans:
        need(all(i in ids for z in p["batches"] for i in z) and p["examples"]==256 and min(p["skill_pairs"].values())>=16,"REPLAY")
        if p["strategy"]!="supervised":need(all(ids[z[0]]["pair"]==ids[z[1]]["pair"] for z in p["batches"]),"PAIR_BATCH")
    need(plans[2]["skill_pairs"]["membership"]>plans[2]["skill_pairs"]["copy"],"ADAPTATION")
    need(schedule(tr,"adaptive",1234,errors)==plans[2],"DETERMINISM")
    for bad in (tr[:-1],[dict(tr[0],gold="fake")]+tr[1:]):
        try:validate(bad,"train")
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    need(not gate()["training_authorized"],"GATE")
    print(json.dumps(dict(status="OFFLINE_SELFTEST_OK",rows={s:len(z) for s,z in data.items()},plans=[{k:v for k,v in p.items() if k!="batches"} for p in plans],gate=gate()),indent=2))
def freeze(out,seed):
    out=Path(out);out.mkdir(exist_ok=False)
    data={s:build(s,seed+i) for i,s in enumerate(SPLITS)}
    for s,z in data.items():validate(z,s);(out/(s+".json")).write_text(json.dumps(z,sort_keys=True))
    (out/"manifest.json").write_text(json.dumps(dict(model=MODEL,revision=REV,hashes={s:digest(z) for s,z in data.items()},gate=gate()),indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze"]);p.add_argument("--out");p.add_argument("--seed",type=int,default=20261125);a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:freeze(a.out,a.seed)
