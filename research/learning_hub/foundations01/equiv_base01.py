"""EQUIV-BASE01: balanced paired boundary equivalence, frozen base inference only."""
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
    for i,(c,p,q) in enumerate(it.product((.25,.45,.65),(0.,.25),(0.,.25))):yield "train",i,c,p,q,4
    for i,c in enumerate((.35,.55),12):yield "dev",i,c,.10,.35,4
    for i,c in enumerate((.2,.4,.6,.8),14):yield "holdout",i,c,.15,.40,8
def generate():
    import networkx as nx
    rng=random.Random(20270157);rows={k:[] for k in ("train","dev","holdout")};seen={k:{} for k in rows};attempts=Counter()
    for split,f,c,p,q,count in configs():
        found=0
        while found<count:
            attempts[f]+=1
            if attempts[f]>50000:raise RuntimeError("generator exhausted")
            n=rng.choice((6,7,8) if split=="train" else (9,) if split=="dev" else (10,11))
            k=max(4,n//2);past=set(range(k));future=set(range(k,n))
            e={(a,b) for a,b in it.combinations(range(n),2) if rng.random()<(p if a in past and b in past else q if a in future and b in future else c)}
            choices=[frozenset(x) for x in it.combinations(sorted(past),2) if feasible(x,e)]
            masks={s:blocked(s,future,e) for s in choices}
            valid=[(a,b,d) for a in choices for b in choices for d in choices if a!=b and masks[a]==masks[b] and masks[a]!=masks[d]]
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
                rows[split].append(dict(id=rid,pair=pair,family=f,label=label,packet=packet,provenance="synthetic_exact"))
            found+=1
    for k,r in rows.items():
        rng.shuffle(r);assert len({x["id"] for x in r})==len(r)
        assert sum(x["label"] for x in r)*2==len(r)
        assert all(len(v)==2 and {x["label"] for x in v}=={True,False} for v in ([x for x in r if x["pair"]==p] for p in {x["pair"] for x in r}))
    assert [len(rows[x]) for x in rows]==[96,16,64]
    assert len({x["family"] for x in rows["train"]})==12
    assert len({x["id"] for r in rows.values() for x in r})==176
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
    manifest={"model":MODEL,"revision":REV,"counts":{k:len(v) for k,v in rows.items()},"families":{k:len({r["family"] for r in v}) for k,v in rows.items()},"attempts":attempts,"hashes":{p.name:sha(p.read_bytes()) for p in out.glob("*.json")},"cross_split_isomorphism":"disjoint_vertex_counts","training_authorized":False}
    dump(out/"manifest.json",manifest);print("EQUIV_FREEZE",json.dumps(manifest),flush=True)
def infer(questions,manifest,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    m=json.loads(Path(manifest).read_text());raw=Path(questions).read_bytes()
    assert sha(raw)==m["hashes"]["questions.json"] and m["revision"]==REV
    rows=json.loads(raw);assert len(rows)==64 and all(set(r)=={"id","packet"} for r in rows)
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==REV
    cand={k:tok.encode(k,add_special_tokens=False) for k in ("Yes","No")}
    binary=all(len(v)==1 and tok.decode(v)==k for k,v in cand.items())
    with Path(out).open("x") as log:
        for view in VIEWS:
            for r in rows:
                q=question(r["packet"],view);prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
                x=tok(prompt,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
                assert n+8<=1024
                start=time.monotonic()
                with torch.inference_mode():
                    prob=None
                    if binary:
                        logits=model(**x).logits[0,-1].float()
                        y,z=(float(logits[cand[k][0]]) for k in ("Yes","No"))
                        prob=float(torch.softmax(torch.tensor([y,z]),dim=0)[0])
                    ids=model.generate(**x,do_sample=False,max_new_tokens=8,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                log.write(json.dumps(dict(id=r["id"],view=view,raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False),ids=ids,input_tokens=n,seconds=time.monotonic()-start,p_yes_binary=prob,prompt_sha256=sha(q.encode())))+"\n");log.flush()
            print("EQUIV_VIEW",view,flush=True)
def score(labels,manifest,pred,out):
    m=json.loads(Path(manifest).read_text());raw=Path(labels).read_bytes();assert sha(raw)==m["hashes"]["labels.json"]
    rows=json.loads(raw);by={r["id"]:r for r in rows};rec=[json.loads(l) for l in Path(pred).read_text().splitlines()]
    assert len(rec)==128 and {(r["id"],r["view"]) for r in rec}==set(it.product(by,VIEWS))
    for r in rows:assert oracle(r["packet"])==r["label"]
    scores={};hits={}
    for v in VIEWS:
        rr=[r for r in rec if r["view"]==v];strict={};binary={};prob={};counts=Counter()
        for r in rr:
            t=by[r["id"]];gold="Yes" if t["label"] else "No"
            assert r["prompt_sha256"]==sha(question(t["packet"],v).encode()) and len(r["ids"])<=8
            strict[r["id"]]=r["raw"]==gold;counts["correct_"+gold]+=strict[r["id"]]
            if r["p_yes_binary"] is not None:
                p=r["p_yes_binary"];assert 0<=p<=1;prob[r["id"]]=p;binary[r["id"]]=(p>.5)==t["label"]
        pairs=[[r for r in rows if r["pair"]==p] for p in sorted({r["pair"] for r in rows})]
        contrasts=[prob[next(r["id"] for r in pair if r["label"])]-prob[next(r["id"] for r in pair if not r["label"])] for pair in pairs] if len(prob)==64 else []
        hits[v]=strict
        scores[v]=dict(correct=sum(strict.values()),valid=sum(r["raw"] in ("Yes","No") for r in rr),correct_yes=counts["correct_Yes"],correct_no=counts["correct_No"],pairs_both=sum(all(strict[r["id"]] for r in pair) for pair in pairs),binary_correct=sum(binary.values()) if binary else None,binary_pairs_both=sum(all(binary[r["id"]] for r in pair) for pair in pairs) if binary else None,positive_contrasts=sum(d>0 for d in contrasts) if contrasts else None,mean_contrast=sum(contrasts)/len(contrasts) if contrasts else None,outputs=dict(Counter(r["raw"] for r in rr)),input_tokens=sum(r["input_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    result=dict(scores=scores,both_views=sum(all(hits[v][i] for v in VIEWS) for i in by),constant_accuracy=.5,constant_pairs_both=0,oracle_accuracy=1,training_authorized=False)
    dump(Path(out),result);print("EQUIV_RESULT",json.dumps(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("stage",choices=("freeze","infer","score"));p.add_argument("paths",nargs="+");a=p.parse_args();globals()[a.stage](*a.paths)
