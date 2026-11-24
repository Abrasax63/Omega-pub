"""Counterfactual family constructor, no model or evaluation access."""
import random
import itertools
from collections import Counter
from corpus_gate import identities,motif
from atomic_eval import exact

MOTIFS=tuple(format(i,"03b") for i in range(8))
def create(seed,kind):
    if kind not in ("train","eval"):
        raise ValueError("KIND")
    rng=random.Random(seed)
    sizes,per=((4,),16) if kind=="train" else ((5,6),4)
    rows=[]
    used=set()
    for n in sizes:
        for f in range(per):
            for attempt in range(10000):
                names=rng.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),n)
                triple=rng.sample(names,3)
                x,y,z=triple
                varied=((x,y),(y,z),(x,z))
                pairs=[(a,b) for a in names for b in names]
                background={e for e in pairs if e not in varied and rng.getrandbits(1)}
                rng.shuffle(pairs)
                family=[]
                keys=set()
                for m in MOTIFS:
                    es=background|{e for e,v in zip(varied,m) if v=="1"}
                    p={"nodes":names,"edges":[list(e) for e in pairs if e in es],"triple":triple}
                    g,_=identities(p)
                    if g in used or g in keys:
                        break
                    keys.add(g)
                    family.append({"id":f"{kind}-{n}-{f}-{m}","family":f"{kind}-{n}-{f}",
                                   "packet":p,"label":exact(p),"provenance":"CURATED_COUNTERFACTUAL_ORACLE"})
                if len(family)==8:
                    used.update(keys)
                    rows.extend(family)
                    break
            else:
                raise ValueError("FAMILY_GENERATION_BUDGET_EXHAUSTED")
    rng.shuffle(rows)
    return rows

def validate(rows,kind):
    if kind not in ("train","eval"):
        raise ValueError("KIND")
    sizes,per=((4,),16) if kind=="train" else ((5,6),4)
    if len(rows)!=8*len(sizes)*per or len({r["id"] for r in rows})!=len(rows):
        raise ValueError("COUNT")
    families={}
    keys=set()
    for r in rows:
        p=r["packet"]
        g,_=identities(p)
        if g in keys or g[0] not in sizes or len(set(p["triple"]))!=3:
            raise ValueError("GRAPH")
        keys.add(g)
        if r["label"]!=exact(p) or r["provenance"]!="CURATED_COUNTERFACTUAL_ORACLE":
            raise ValueError("LABEL")
        families.setdefault(r["family"],[]).append(r)
    counts=Counter()
    for group in families.values():
        if len(group)!=8 or {motif(r["packet"]) for r in group}!=set(MOTIFS):
            raise ValueError("FAMILY_MOTIFS")
        p=group[0]["packet"]
        counts[len(p["nodes"])]+=1
        x,y,z=p["triple"]
        varied={(x,y),(y,z),(x,z)}
        fixed={tuple(e) for e in p["edges"]}-varied
        for r in group:
            q=r["packet"]
            if q["nodes"]!=p["nodes"] or q["triple"]!=p["triple"] or {tuple(e) for e in q["edges"]}-varied!=fixed:
                raise ValueError("BACKGROUND_CHANGED")
    if counts!={n:per for n in sizes}:
        raise ValueError("FAMILY_COUNTS")
    return {"rows":len(rows),"families":len(families),"unique_graphs":len(keys)}
