"""Independent elementary edge-membership pairs, no model or inference."""
from collections import Counter
import itertools
import random
from corpus_gate import identities

def create(seed,kind):
    if kind not in ("train","eval"): raise ValueError("KIND")
    rng=random.Random(seed)
    sizes,per=((4,),64) if kind=="train" else ((5,6),16)
    seen=set(); rows=[]
    for n in sizes:
        for i in range(per):
            for _ in range(10000):
                nodes=rng.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),n)
                x,y=rng.sample(nodes,2)
                edges=list(itertools.product(nodes,repeat=2))
                rng.shuffle(edges)
                bg={e for e in edges if e!=(x,y) and rng.getrandbits(1)}
                family=[];keys=set()
                for label in (False,True):
                    es=bg|({(x,y)} if label else set())
                    p={"nodes":nodes,"edges":[list(e) for e in edges if e in es],"triple":[x,y,x]}
                    key,_=identities(p)
                    if key in seen or key in keys: break
                    keys.add(key)
                    family.append({"id":f"{kind}-{n}-{i}-{int(label)}","pair":f"{kind}-{n}-{i}",
                                   "packet":p,"label":label,"provenance":"CURATED_MEMBERSHIP"})
                if len(family)==2:
                    seen.update(keys);rows.extend(family);break
            else: raise ValueError("GENERATION_BUDGET")
    rng.shuffle(rows)
    return rows

def validate(rows,kind):
    if kind not in ("train","eval"): raise ValueError("KIND")
    sizes,per=((4,),64) if kind=="train" else ((5,6),16)
    if len(rows)!=2*per*len(sizes) or len({r["id"] for r in rows})!=len(rows): raise ValueError("COUNT")
    seen=set();groups={};counts=Counter()
    for r in rows:
        p=r["packet"];x,y,z=p["triple"];g,_=identities(p)
        if x==y or x!=z or g[0] not in sizes or g in seen: raise ValueError("GRAPH")
        seen.add(g)
        if type(r["label"]) is not bool or r["provenance"]!="CURATED_MEMBERSHIP": raise ValueError("LABEL")
        ns=p["nodes"]
        matrix=[[False]*len(ns) for _ in ns]
        for a,b in p["edges"]: matrix[ns.index(a)][ns.index(b)]=True
        if r["label"]!=matrix[ns.index(x)][ns.index(y)]: raise ValueError("LABEL")
        groups.setdefault(r["pair"],[]).append(r)
    for family in groups.values():
        if len(family)!=2 or {r["label"] for r in family}!={False,True}: raise ValueError("PAIR")
        a,b=sorted(family,key=lambda r:r["label"]); p,q=a["packet"],b["packet"]
        if p["nodes"]!=q["nodes"] or p["triple"]!=q["triple"]: raise ValueError("PAIR_CONTEXT")
        e={tuple(x) for x in p["edges"]};f={tuple(x) for x in q["edges"]}
        if f-e!={tuple(p["triple"][:2])} or e-f: raise ValueError("PAIR_TOGGLE")
        counts[len(p["nodes"])]+=1
    if counts!={n:per for n in sizes}: raise ValueError("PAIR_COUNTS")
    return {"examples":len(rows),"pairs":len(groups),"unique_graphs":len(seen)}
