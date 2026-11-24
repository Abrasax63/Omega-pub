"""EQUIV-PILOT01: matched shortcut controls; corpus freeze only."""
import argparse,hashlib,itertools as it,json,random,time
from pathlib import Path
from collections import Counter
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
VIEWS=("edges","matrix")
def sha(x):return hashlib.sha256(x).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,sort_keys=True,separators=(",",":")))
def feasible(s,e):return not any(a in s and b in s for a,b in e)
def blocked(s,f,e):
    return frozenset(v for v in f if any(tuple(sorted((u,v))) in e for u in s))
def oracle(p):
    e={tuple(sorted(x)) for x in p["edges"]};f=p["future"];a=set(p["a"]);b=set(p["b"])
    assert a!=b and len(a)==len(b)==2 and feasible(a,e) and feasible(b,e)
    def extensions(s):
        return {tuple(q) for k in range(len(f)+1) for q in it.combinations(f,k) if feasible(s|set(q),e)}
    truth=extensions(a)==extensions(b)
    assert truth==(blocked(a,f,e)==blocked(b,f,e))
    return truth
def configs():
    for i,(c,p,q) in enumerate(it.product((.25,.45,.65),(0.,.25),(0.,.25))):yield "train",i,c,p,q,8
    for i,c in enumerate((.35,.55),12):yield "dev",i,c,.10,.35,4
    for i,c in enumerate((.2,.4,.6,.8),14):yield "holdout",i,c,.15,.40,8
def generate():
    import networkx as nx
    rng=random.Random(20270159);rows={k:[] for k in ("train","dev","holdout")};seen={k:{} for k in rows};attempts=Counter()
    for split,f,c,p,q,count in configs():
        found=0
        while found<count:
            attempts[f]+=1
            if attempts[f]>50000:raise RuntimeError("generator exhausted")
            n=rng.choice((8,9) if split=="train" else (12,) if split=="dev" else (13,14))
            k=max(4,n//2);past=set(range(k));future=set(range(k,n))
            e={(a,b) for a,b in it.combinations(range(n),2) if rng.random()<(p if a in past and b in past else q if a in future and b in future else c)}
            choices=[frozenset(x) for x in it.combinations(sorted(past),2) if feasible(x,e)]
            masks={s:blocked(s,future,e) for s in choices}
            valid=[(a,b,d) for a in choices for b in choices for d in choices if a!=b and masks[a]==masks[b] and masks[a]!=masks[d] and len(a&b)==len(a&d) and len(masks[a])==len(masks[d])]
            if not valid:continue
            g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(e)
            key=(n,nx.weisfeiler_lehman_graph_hash(g))
            bucket=seen[split].setdefault(key,[])
            if any(nx.is_isomorphic(g,h) for h in bucket):continue
            bucket.append(g)
            a,b,d=rng.choice(valid)
            names=[f"v{j}" for j in rng.sample(range(10,99),n)]
            nodes=names.copy();rng.shuffle(nodes)
            def rename(s):
                out=[names[v] for v in sorted(s)];rng.shuffle(out);return out
            edges=[rename(x) for x in sorted(e)];rng.shuffle(edges)
            common=dict(nodes=nodes,past=rename(past),future=rename(future),edges=edges,a=rename(a))
            pair=f"{split}-{f}-{found}"
            for label,s in ((True,b),(False,d)):
                packet=dict(common,b=rename(s))
                # IDs are opaque hashes; metadata and labels not in prompts.
                rid=sha(json.dumps(packet,sort_keys=True).encode())[:24]
                assert oracle(packet)==label
                assert len(a&s)==len(a&b) and len(masks[a])==len(masks[s])
                rows[split].append(dict(id=rid,pair=pair,family=f,label=label,packet=packet,provenance="synthetic_exact"))
            found+=1
    for k,r in rows.items():
        rng.shuffle(r);assert len({x["id"] for x in r})==len(r)
        assert sum(x["label"] for x in r)*2==len(r)
        assert all(len(v)==2 and {x["label"] for x in v}=={True,False} for v in ([x for x in r if x["pair"]==p] for p in {x["pair"] for x in r}))
    assert [len(rows[x]) for x in rows]==[192,16,64]
    assert len({x["family"] for x in rows["train"]})==12
    assert len({x["id"] for r in rows.values() for x in r})==272
    for split,r in rows.items():
        for pair in {x["pair"] for x in r}:
            pos,neg=sorted([x for x in r if x["pair"]==pair],key=lambda x:not x["label"])
            pp,nn=pos["packet"],neg["packet"];e={tuple(sorted(x)) for x in pp["edges"]}
            assert all(pp[k]==nn[k] for k in ("nodes","past","future","edges","a"))
            assert len(set(pp["a"])&set(pp["b"]))==len(set(nn["a"])&set(nn["b"]))
            assert len(blocked(pp["b"],pp["future"],e))==len(blocked(nn["b"],nn["future"],e))
            assert blocked(pp["b"],pp["future"],e)!=blocked(nn["b"],nn["future"],e)
    return rows,dict(attempts)
def question(p,view):
    if view=="edges":data={"nodes":p["nodes"],"edges":p["edges"]}
    else:
        e={tuple(sorted(x)) for x in p["edges"]}
        data={"nodes":p["nodes"],"matrix":[[int(tuple(sorted((u,v))) in e) for v in p["nodes"]] for u in p["nodes"]]}
    data.update({k:p[k] for k in ("past","future","a","b")})
    return ("In this undirected graph, a and b are independent sets already selected from past. "
            "A future independent set is admissible if its union with the selected past set is independent. "
            "Do a and b allow exactly the same collection of future independent sets? Answer exactly Yes or No. "
            +("Edges are undirected." if view=="edges" else "Matrix rows and columns follow nodes order.")+" "+json.dumps(data,separators=(",",":")))
def freeze(out):
    out=Path(out);out.mkdir()
    rows,attempts=generate()
    for k in ("train","dev"):dump(out/(k+".json"),rows[k])
    dump(out/"labels.json",rows["holdout"])
    dump(out/"questions.json",[{k:r[k] for k in ("id","packet")} for r in rows["holdout"]])
    manifest={"model":MODEL,"revision":REV,"counts":{k:len(v) for k,v in rows.items()},"families":{k:len({r["family"] for r in v}) for k,v in rows.items()},"attempts":attempts,"hashes":{p.name:sha(p.read_bytes()) for p in out.glob("*.json")},"cross_split_isomorphism":"disjoint_vertex_counts","training_authorized":False,"matched_pair_controls":["same_selected_overlap","same_blocked_cardinality"],"diagnostic_disjoint_sizes":[10,11]}
    dump(out/"manifest.json",manifest);print("EQUIV_PILOT_FREEZE",json.dumps(manifest),flush=True)

if __name__=="__main__":
    import sys
    freeze(sys.argv[1])
