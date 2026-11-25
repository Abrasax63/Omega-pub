"""Independent index punctuation and structural fidelity probe, no gradients."""
import argparse,json,random,re,time
from pathlib import Path
from collections import Counter
from contextlib import nullcontext
import index_restore_pilot01 as ir
import index_interference01 as ii
import copy_sft01 as c
import position_cumulative01 as pc
import position_representation as pos
import self_representation02 as sr2
SEED=202611251019
PILOT="dd5dfc665b109acaeded266d5c3cc29d1b3348e84e5fa3f52ff64689c85292d1"
ARMS=("base","parent","pilot")
OPS=("copy","select","example","colon","space")
def question(s,p,o):
    seq=" ".join(s)
    if o=="copy":return c.question(seq,"trained")
    if o=="select":return pc.question(seq,p,"original")
    if o=="example":return sr2.prompt(s,"B")
    sep="a colon" if o=="colon" else "one space"
    return "Assign each symbol its one-based position in the list. Put "+sep+" between each position number and its symbol. Separate pairs with one space. Output only the pairs. Data: "+seq
def target(s,p,o):
    if o=="copy":return " ".join(s)
    if o=="select":return s[p-1]
    sep=" " if o=="space" else ":"
    return " ".join(f"{i}{sep}{x}" for i,x in enumerate(s,1))
def corpus():
    rng=random.Random(SEED);t,e=c.make()
    assert c.digest(c.canonical(t))=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert c.digest(c.canonical(e))=="34e02262decf0576b69930ef652b0a08c66a14bf827026b59719ebbb6b03b19a"
    excluded={tuple(r["packet"].split()) for r in t+e}
    excluded.update(tuple(r["seq"].split()) for r in ii.ct.corpus())
    for mod in (ii.cp,ii.pos,ii.sr1,ii.sr2,ii.sr3,ii.rd,ii.fs):
        excluded.update(tuple(r["seq"]) for r in mod.corpus())
    for r in ii.fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:excluded.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    excluded.update(tuple(r["seq"].split()) for r in t+e)
    for mod,h in ((ii.ic,"def2f1d550f7ba84c2340fdb3f03c52310ec74b84ae6e6c14b53dbe02580699c"),(ii.depth,"db067e67e4747730cc5a12e9892c75fcee6b05c35b512000401b3c0e3cec14e7"),(ii.si,"d6432ac68869dffb04902ddf36c1ebb3dc3a9643ea9bdd1760b993a5556ae794"),(ii,"1150551a9fbaf4eafabd961ae7b088fc3f743915ebe6e8fd425e51945c49a95d")):
        rr=mod.corpus();assert c.digest(c.canonical(rr))==h
        excluded.update(tuple(r["seq"].split() if isinstance(r["seq"],str) else r["seq"]) for r in rr)
    t,e=ir.make()
    assert c.digest(c.canonical(t))=="d801879d363455e1b6cbbcfece5264e1f4d0a8f63e543595a25b615270b94d47"
    assert c.digest(c.canonical(e))=="b706a388800a6c14ec58b3e1328adf77314acacab79ee80828dddb8d4e4e8e21"
    excluded.update(tuple(r["seq"]) for r in t+e)
    rows=[]
    for g,alpha,n,k in (("id","ABCDEFGH",3,8),("id","ABCDEFGH",4,8),("length","ABCDEFGH",7,2),("length","ABCDEFGH",8,2),("alphabet","IJKLMNOP",3,2),("alphabet","IJKLMNOP",4,2)):
        pp=list(range(5 if g=="length" else 1,n+1))
        pp=pp*(k//len(pp))+rng.sample(pp,k%len(pp));rng.shuffle(pp)
        for p in pp:
            for _ in range(10000):
                s=rng.sample(list(alpha),n)
                if tuple(s) not in excluded:break
            else:raise RuntimeError("exhausted")
            excluded.add(tuple(s));sid=c.digest(c.canonical(s))[:24]
            assert target(s,p,"colon")!=target(s,p,"space")
            for o in OPS:
                rows.append(dict(id=c.digest(c.canonical([s,p,o]))[:24],sid=sid,seq=s,p=p,op=o,group=g,gold=target(s,p,o),prompt=question(s,p,o)))
    rng.shuffle(rows)
    assert len(rows)==120 and len({r["id"] for r in rows})==120 and len({r["sid"] for r in rows})==24
    for o in OPS:assert Counter(r["group"] for r in rows if r["op"]==o)=={"id":16,"length":4,"alphabet":4}
    return rows
def classify(raw,r):
    s,p=r["seq"],r["p"]
    if raw==target(s,p,"colon"):return "colon"
    if raw==target(s,p,"space"):return "space"
    if raw==target(s,p,"copy"):return "copy"
    if raw==target(s,p,"select"):return "select"
    return "other"
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==360 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in ARMS for i in by}
    hits={};scores={}
    for a in ARMS:
        scores[a]={}
        for o in OPS:
            rr=[r for r in records if r["arm"]==a and by[r["id"]]["op"]==o];assert len(rr)==24
            conf=Counter();groups=Counter();exact=0;faithful=0;others=[]
            for r in rr:
                q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                raw=r["raw"].strip();h=raw==q["gold"];hits[a,q["id"]]=h;exact+=h
                cls=classify(raw,q);conf[cls]+=1
                faithful+=cls in ("colon","space") if o in ("example","colon","space") else h
                groups[q["group"]]+=h
                if o in ("example","colon","space") and cls=="other":others.append(dict(id=q["id"],raw=raw,gold=q["gold"]))
            scores[a][o]=dict(exact=exact,faithful=faithful,confusion=dict(conf),by_group=dict(groups),other_index_outputs=others,tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
        sid={r["sid"] for r in rows}
        scores[a]["format_pairs"]=sum(all(hits[a,r["id"]] for r in rows if r["sid"]==i and r["op"] in ("colon","space")) for i in sid)
    transitions={o:dict(Counter(f"{int(hits['parent',r['id']])}{int(hits['pilot',r['id']])}" for r in rows if r["op"]==o)) for o in OPS}
    s=scores["pilot"];p=scores["parent"]
    gate=all(s[o]["exact"]>=22 and s[o]["faithful"]>=22 for o in ("example","colon","space")) and s["format_pairs"]>=20 and all(s[o]["exact"]>=p[o]["exact"]-1 for o in ("copy","select"))
    return dict(scores=scores,transitions=transitions,gate=gate,training=False,promotion_authorized=False)
def run(parent,pilot,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False)
    (out/"corpus.json").write_bytes(c.canonical(rows));print("FORMAT_REPL_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=ir.load(parent);pilot=Path(pilot);m=json.loads((pilot/"manifest.json").read_text())
    assert m["adapter_sha256"]["adapter_model.safetensors"]==PILOT and m["parent_sha256"]==ir.PARENT and m["steps"]==72
    assert m["train_sha256"]=="d801879d363455e1b6cbbcfece5264e1f4d0a8f63e543595a25b615270b94d47"
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
            print("FORMAT_REPL_STAGE",a,len(records),flush=True)
    result=score(rows,records);result["corpus_sha256"]=c.sha_file(out/"corpus.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print("FORMAT_REPL_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--parent");p.add_argument("--pilot");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=corpus()
        for r in rows:
            assert classify(target(r["seq"],r["p"],"colon"),r)=="colon"
            assert classify(target(r["seq"],r["p"],"space"),r)=="space"
        print("FORMAT_REPL_CHECK",len(rows),c.digest(c.canonical(rows)))
    else:run(a.parent,a.pilot,a.out)
