"""Novel composition probe. Cohort B is frozen but never inferred by this workflow."""
import argparse,json,random,time,itertools
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import format_index_repl01 as fr
import copy_sft01 as c
import position_cumulative01 as pc
import self_representation02 as sr2
import position_representation as pos
ARMS=("base","parent","pilot")
def exclusions():
    ii=fr.ii
    t,e=c.make();out={tuple(r["packet"].split()) for r in t+e}
    out.update(tuple(r["seq"].split()) for r in ii.ct.corpus())
    for m in (ii.cp,ii.pos,ii.sr1,ii.sr2,ii.sr3,ii.rd,ii.fs):
        out.update(tuple(r["seq"]) for r in m.corpus())
    import re
    for r in ii.fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:out.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    out.update(tuple(r["seq"].split()) for r in t+e)
    for m,h in ((ii.ic,"def2f1d550f7ba84c2340fdb3f03c52310ec74b84ae6e6c14b53dbe02580699c"),(ii.depth,"db067e67e4747730cc5a12e9892c75fcee6b05c35b512000401b3c0e3cec14e7"),(ii.si,"d6432ac68869dffb04902ddf36c1ebb3dc3a9643ea9bdd1760b993a5556ae794"),(ii,"1150551a9fbaf4eafabd961ae7b088fc3f743915ebe6e8fd425e51945c49a95d"),(fr,"10d97b76fbb806a3fa8c6f774e3a5451c2c2b41c27b7d44ccaaee511048d1399")):
        rr=m.corpus();assert c.digest(c.canonical(rr))==h
        out.update(tuple(r["seq"].split() if isinstance(r["seq"],str) else r["seq"]) for r in rr)
    t,e=fr.ir.make()
    assert c.digest(c.canonical(t))=="d801879d363455e1b6cbbcfece5264e1f4d0a8f63e543595a25b615270b94d47"
    assert c.digest(c.canonical(e))=="b706a388800a6c14ec58b3e1328adf77314acacab79ee80828dddb8d4e4e8e21"
    out.update(tuple(r["seq"]) for r in t+e)
    out.update([tuple("DFAH"),tuple("LJK")])
    return out
def prompt(s,p,q,v):
    seq=" ".join(s)
    if v==0:return f"Take the letter at position {p}, then the letter at position {q}, counting from 1. Number the resulting two letters 1 and 2, in that order. Return only number:letter pairs separated by one space. Sequence: {seq}"
    return f"From the list, extract symbols numbered {p} and {q}, in the order specified here. Renumber the extracted symbols starting at 1. Write each new number followed by a colon and its symbol, with a single space between pairs. Data: {seq}"
def gold(s,p,q):
    return f"1:{s[p-1]} 2:{s[q-1]}"
def make():
    excluded=exclusions();cohorts={}
    for name,seed in (("A",202611251026),("B",202611251027)):
        rng=random.Random(seed);rows=[]
        for n in (3,4):
            pp=list(itertools.combinations(range(1,n+1),2))
            pp=pp*(8//len(pp))+rng.sample(pp,8%len(pp));rng.shuffle(pp)
            a=rng.sample(list("ABCDEFGH"),8);b=rng.sample(list("ABCDEFGH"),8)
            while any(x==y for x,y in zip(a,b)):b=rng.sample(list("ABCDEFGH"),8)
            for (p,q),x,y in zip(pp,a,b):
                for _ in range(10000):
                    s=rng.sample([z for z in "ABCDEFGH" if z not in (x,y)],n-2)
                    s.insert(p-1,x);s.insert(q-1,y)
                    if tuple(s) not in excluded:break
                else:raise RuntimeError("exhausted")
                excluded.add(tuple(s));sid=c.digest(c.canonical(s))[:24]
                def add(op,p,q,v,g,question):
                    rows.append(dict(id=c.digest(c.canonical([s,op,p,q,v]))[:24],sid=sid,seq=s,op=op,p=p,q=q,view=v,gold=g,prompt=question))
                add("copy",0,0,0," ".join(s),c.question(" ".join(s),"trained"))
                add("index",0,0,0,pos.encode(s,"indexed"),sr2.prompt(s,"B"))
                for i in (p,q):add("select",i,0,0,s[i-1],pc.question(" ".join(s),i,"original"))
                for i,j in ((p,q),(q,p)):
                    g=gold(s,i,j)
                    assert g!=gold(s,j,i) and g!=" ".join(s)
                    orig=f"{i}:{s[i-1]} {j}:{s[j-1]}"
                    if (i,j)!=(1,2):assert orig!=g
                    for v in (0,1):add("compose",i,j,v,g,prompt(s,i,j,v))
        assert len(rows)==128 and len({r["id"] for r in rows})==128
        assert len({r["sid"] for r in rows})==16
        for v in (0,1):
            rr=[r for r in rows if r["op"]=="compose" and r["view"]==v]
            assert len(rr)==32 and Counter(r["seq"][r["p"]-1] for r in rr)==Counter({x:4 for x in "ABCDEFGH"})
        rng.shuffle(rows);cohorts[name]=rows
    assert not {r["sid"] for r in cohorts["A"]}&{r["sid"] for r in cohorts["B"]}
    return cohorts
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==384 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in ARMS for i in by}
    hits={};scores={}
    for a in ARMS:
        scores[a]={}
        for op,v in (("copy",0),("index",0),("select",0),("compose",0),("compose",1)):
            rr=[r for r in records if r["arm"]==a and by[r["id"]]["op"]==op and by[r["id"]]["view"]==v]
            errors=Counter();pairs={};correct=0;faithful=0;nontrivial=0;nontrivial_correct=0
            for r in rr:
                q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                raw=r["raw"].strip();h=raw==q["gold"];hits[a,q["id"]]=h;correct+=h
                if op=="compose":
                    p,j,s=q["p"],q["q"],q["seq"];space=f"1 {s[p-1]} 2 {s[j-1]}"
                    faithful+=h or raw==space
                    pairs.setdefault(q["sid"],[]).append(h)
                    if (p,j)!=(1,2):nontrivial+=1;nontrivial_correct+=h
                    if not h:
                        reverse=gold(s,j,p);orig=f"{p}:{s[p-1]} {j}:{s[j-1]}"
                        errors["format_only" if raw==space else "reversed" if raw==reverse else "original_indices" if raw==orig else "unindexed_selection" if raw==f"{s[p-1]} {s[j-1]}" else "other"]+=1
            scores[a][op+str(v)]=dict(n=len(rr),exact=correct,faithful=faithful if op=="compose" else correct,pairs=sum(all(x) for x in pairs.values()) if op=="compose" else None,nontrivial=nontrivial,nontrivial_correct=nontrivial_correct,errors=dict(errors),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    s=scores["pilot"];p=scores["parent"];b=scores["base"]
    gate=s["copy0"]["exact"]>=15 and s["index0"]["exact"]>=15 and s["select0"]["exact"]>=29 and all(s[k]["exact"]>=26 and s[k]["pairs"]>=13 and s[k]["exact"]-b[k]["exact"]>=4 for k in ("compose0","compose1")) and all(s[k]["exact"]>=p[k]["exact"]-1 for k in ("copy0","select0"))
    return dict(scores=scores,exploratory_numeric_gate=gate,consolidation_gate=False,validation_authorized=False,cohort_B_consumed=False,promotion_authorized=False,training=False)
def run(parent,pilot,out):
    cohorts=make();out=Path(out);out.mkdir(exist_ok=False)
    rows=cohorts["A"]
    for k,rr in cohorts.items():
        (out/f"cohort_{k}.json").write_bytes(c.canonical(rr))
        print("COMPOSITION_FROZEN",k,c.sha_file(out/f"cohort_{k}.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=fr.ir.load(parent);pilot=Path(pilot);m=json.loads((pilot/"manifest.json").read_text())
    assert m["adapter_sha256"]["adapter_model.safetensors"]==fr.PILOT and m["parent_sha256"]==fr.ir.PARENT and m["steps"]==72
    for k,h in m["adapter_sha256"].items():assert c.sha_file(pilot/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",adapter_name="parent",is_trainable=False)
    model.load_adapter(pilot/"adapter",adapter_name="pilot",is_trainable=False);model.eval();model.config.use_cache=True
    records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for a in ARMS:
            model.set_adapter("parent" if a=="base" else a);model.requires_grad_(False)
            with model.disable_adapter() if a=="base" else nullcontext():
                for r in rows:
                    p=pc.prefix(tok,r);x=torch.tensor([p]);start=time.monotonic()
                    with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,len(p):].tolist()
                    rec=dict(arm=a,id=r["id"],raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=len(p),output_tokens=len(y),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("COMPOSITION_STAGE",a,len(records),flush=True)
    result=score(rows,records);result["cohort_A_sha256"]=c.sha_file(out/"cohort_A.json")
    result["cohort_B_sha256"]=c.sha_file(out/"cohort_B.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print("COMPOSITION_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--parent");p.add_argument("--pilot");p.add_argument("--out");a=p.parse_args()
    if a.check:
        for k,rr in make().items():print("COMPOSITION_CHECK",k,len(rr),c.digest(c.canonical(rr)))
    else:run(a.parent,a.pilot,a.out)
