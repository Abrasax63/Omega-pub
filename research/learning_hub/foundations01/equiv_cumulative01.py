"""Cumulative curriculum preparation only, no model calls."""
import itertools as it, json, random, sys
from collections import Counter
from pathlib import Path
import networkx as nx
import equiv_pilot_freeze as p
def configs():
    for i,(c,d) in enumerate(it.product((.25,.45,.65),(.1,.3))):yield "train",i,c,d,8
    for i,c in enumerate((.35,.55),6):yield "dev",i,c,.2,4
    for split in ("test","retention"):
        for i,c in enumerate((.2,.4,.6,.8),8):yield split,i,c,.25,8
def truth(packet):
    e={tuple(sorted(x)) for x in packet["edges"]};a=set(packet["a"]);b=set(packet["b"]);f=packet["future"]
    assert a!=b and len(a)==len(b)==2 and p.feasible(a,e) and p.feasible(b,e)
    if "vertex" in packet:
        v=packet["vertex"];assert v in f
        z=p.feasible(a|{v},e) and not p.feasible(b|{v},e)
        assert z==(v not in p.blocked(a,f,e) and v in p.blocked(b,f,e))
        return z
    return p.oracle(packet)
def generate():
    rng=random.Random(20270165);rows={k:[] for k in ("train","dev","test","retention")};seen={};attempts=Counter()
    for split,f,c,d,count in configs():
        for j in range(count):
            key=f"{split}-{f}"
            while True:
                attempts[key]+=1
                if attempts[key]>10000:raise RuntimeError("generation exhausted "+key)
                n=rng.choice((15,16) if split=="train" else (17,) if split=="dev" else (18,19))
                past=set(range(n//2));future=set(range(n//2,n))
                edges={(a,b) for a,b in it.combinations(range(n),2) if rng.random()<(d if (a in past)==(b in past) else c)}
                choices=[frozenset(s) for s in it.combinations(sorted(past),2) if p.feasible(s,edges)]
                masks={s:p.blocked(s,future,edges) for s in choices}
                if split=="retention":
                    valid=[(a,b,z) for a,b,z in it.product(choices,repeat=3) if a!=b and masks[a]==masks[b] and masks[a]!=masks[z] and len(a&b)==len(a&z) and len(masks[a])==len(masks[z])]
                else:
                    valid=[(a,b) for a,b in it.permutations(choices,2) if len(masks[a])==len(masks[b]) and masks[a]!=masks[b]]
                if not valid:continue
                g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(edges)
                h=(n,nx.weisfeiler_lehman_graph_hash(g));bucket=seen.setdefault(h,[])
                if any(nx.is_isomorphic(g,x) for x in bucket):continue
                bucket.append(g);selected=rng.choice(valid);break
            names=["v"+str(x) for x in rng.sample(range(10,999),n)]
            def rename(s):
                a=[names[x] for x in sorted(s)];rng.shuffle(a);return a
            es=[rename(x) for x in sorted(edges)];rng.shuffle(es)
            a,b=selected[:2]
            common=dict(nodes=rename(range(n)),past=rename(past),future=rename(future),edges=es,a=rename(a))
            if split=="retention":
                positive=dict(common,b=rename(b));negative=dict(common,b=rename(selected[2]))
            else:
                common["b"]=rename(b)
                pos=rng.choice(sorted(masks[b]-masks[a]));neg=rng.choice(sorted(masks[a]-masks[b]))
                positive=dict(common,vertex=names[pos]);negative=dict(common,vertex=names[neg])
            for label,packet in ((True,positive),(False,negative)):
                assert truth(packet)==label
                rows[split].append(dict(id=p.sha(json.dumps(packet,sort_keys=True).encode())[:24],pair=f"{key}-{j}",family=f,label=label,packet=packet,provenance="synthetic_exact",task="equivalence" if split=="retention" else "witness"))
    assert [len(x) for x in rows.values()]==[96,16,64,64]
    ids=set()
    for split,rs in rows.items():
        by={}
        for r in rs:
            assert r["id"] not in ids;ids.add(r["id"]);by.setdefault(r["pair"],[]).append(r)
        for pair in by.values():
            a,b=sorted(pair,key=lambda r:not r["label"]);assert len(pair)==2 and a["label"] and not b["label"]
            x,y=a["packet"],b["packet"];e={tuple(sorted(z)) for z in x["edges"]}
            change="b" if split=="retention" else "vertex"
            assert all(x[k]==y[k] for k in x if k!=change)
            assert len(p.blocked(x["a"],x["future"],e))==len(p.blocked(x["b"],x["future"],e))==len(p.blocked(y["b"],y["future"],e))
            if split=="retention":assert len(set(x["a"])&set(x["b"]))==len(set(y["a"])&set(y["b"]))
            else:assert x["vertex"]!=y["vertex"]
        rng.shuffle(rs)
    return rows,dict(attempts)
def freeze(out):
    out=Path(out);out.mkdir()
    rows,attempts=generate()
    for k in ("train","dev"):p.dump(out/(k+".json"),rows[k])
    labels=rows["test"]+rows["retention"]
    p.dump(out/"labels.json",labels)
    p.dump(out/"questions.json",[{k:r[k] for k in ("id","packet","task")} for r in labels])
    manifest=dict(counts={k:len(v) for k,v in rows.items()},pairs={k:len(v)//2 for k,v in rows.items()},attempts=attempts,hashes={f.name:p.sha(f.read_bytes()) for f in out.glob("*.json")},cross_split_graph_isomorphism_screen=True,training_authorized=False)
    p.dump(out/"manifest.json",manifest);print("CUMULATIVE_FREEZE",json.dumps(manifest),flush=True)
if __name__=="__main__":freeze(sys.argv[1])
