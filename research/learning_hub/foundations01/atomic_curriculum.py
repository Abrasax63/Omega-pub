"""Curated exact atomic curriculum. No model, no training, no hidden files."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
from collections import Counter
from corpus_gate import identities,quotas,motif
from atomic_eval import exact

def create(seed,kind):
    if kind not in ("train","eval"):
        raise ValueError("UNKNOWN_SPLIT")
    rng=random.Random(seed)
    sizes,per=( (3,4),64) if kind=="train" else ((5,6),32)
    rows=[]
    seen=set()
    for n in sizes:
        for target,count in quotas(per).items():
            for _ in range(count):
                for attempt in range(10000):
                    names=rng.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),n)
                    triple=rng.sample(names,3)
                    edges=[[a,b] for a in names for b in names if rng.getrandbits(1)]
                    rng.shuffle(edges)
                    p={"nodes":names,"edges":edges,"triple":triple}
                    if motif(p)!=target:
                        continue
                    graph,_=identities(p)
                    if graph in seen:
                        continue
                    seen.add(graph)
                    label=exact(p)
                    assert "".join(str(int(label[k])) for k in ("xy","yz","xz"))==target
                    rows.append({"id":f"{kind}-{len(rows):03d}","packet":p,"label":label,
                                 "provenance":"CURATED_ORACLE_NOT_MODEL_GENERATED"})
                    break
                else:
                    raise ValueError("GENERATION_BUDGET_EXHAUSTED")
    rng.shuffle(rows)
    return rows

def validate(rows,kind):
    sizes,per=((3,4),64) if kind=="train" else ((5,6),32) if kind=="eval" else ((),0)
    if not sizes or len(rows)!=2*per or len({r["id"] for r in rows})!=len(rows):
        raise ValueError("SIZE_OR_ID")
    graphs=set()
    counts={n:Counter() for n in sizes}
    for row in rows:
        p=row["packet"]
        graph,_=identities(p)
        if graph[0] not in sizes or graph in graphs or len(set(p["triple"]))!=3:
            raise ValueError("GRAPH_OR_TRIPLE")
        graphs.add(graph)
        counts[graph[0]][motif(p)]+=1
        label=row["label"]
        if type(label) is not dict or any(type(v) is not bool for v in label.values()) or label!=exact(p):
            raise ValueError("LABEL")
        if row["provenance"]!="CURATED_ORACLE_NOT_MODEL_GENERATED":
            raise ValueError("PROVENANCE")
    if any(dict(counts[n])!=quotas(per) for n in sizes):
        raise ValueError("MOTIF_QUOTA")
    return {"rows":len(rows),"unique_graphs":len(graphs),"by_size":{str(n):dict(counts[n]) for n in sizes}}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--kind",choices=("train","eval"),required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    rows=create(a.seed,a.kind)
    report=validate(rows,a.kind)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    with a.output.open("xb") as f:
        f.write(raw)
    print(json.dumps(dict(report,sha256=sha256(raw).hexdigest(),kind=a.kind)))
