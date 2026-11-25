"""Fourth cumulative pilot: multiple selection, no composition training."""
import argparse,json,random,time,itertools,math,re
from collections import Counter
from pathlib import Path
from contextlib import nullcontext
import composition_bottleneck01 as cb
import composition_pilot01 as cp
import format_index_repl01 as fr
import copy_sft01 as c
import position_cumulative01 as pc
import self_representation02 as sr2
import position_representation as pos
SEED=202611251123
PARENT=fr.PILOT
ARMS=("base","parent","pilot")
def question(s,p,q,o,v=0):
    seq=" ".join(s)
    if o=="copy":return c.question(seq,"trained")
    if o=="single":return pc.question(seq,p,"original")
    if o=="index":return sr2.prompt(s,"B")
    if v==0:return f"Take the letter at position {p}, then the letter at position {q}, counting from 1. Output only the two letters in that order, separated by one space. Sequence: {seq}"
    return f"Sequence: {seq}. Counting from 1, return the symbols at positions {p} and {q} in that order. Write just the two symbols separated by one space."
def gold(s,p,q,o):
    if o=="copy":return " ".join(s)
    if o=="single":return s[p-1]
    if o=="index":return pos.encode(s,"indexed")
    return f"{s[p-1]} {s[q-1]}"
def make():
    rng=random.Random(SEED);excluded=cp.exclusions()
    prior=cp.make()
    for k,h in (("A","eea900b4663d058dc2f94b909061cab7a1578f330cfa09ca25f42d4ca2c56071"),("B","11185c76eb457d2789231577663b3f23c0a6efcbe234bf78f87d29c5ef90d398")):
        assert c.digest(c.canonical(prior[k]))==h
        excluded.update(tuple(r["seq"]) for r in prior[k])
    rr=cb.make();assert c.digest(c.canonical(rr))=="171acec13094a000c22dc8f71213d9b505acd76ad6b79e5d2211c0af2707498c"
    excluded.update(tuple(r["seq"]) for r in rr);excluded.update(tuple(r["input_seq"]) for r in rr)
    train=[];test=[]
    def add(rows,s,p,q,o,v,g):
        rows.append(dict(id=c.digest(c.canonical([s,p,q,o,v]))[:24],sid=c.digest(c.canonical(s))[:24],seq=s,p=p,q=q,op=o,view=v,group=g,gold=gold(s,p,q,o),prompt=question(s,p,q,o,v)))
    def choose(n):
        for _ in range(10000):
            s=rng.sample(list("ABCDEFGH"),n)
            if tuple(s) not in excluded:
                excluded.add(tuple(s));return s
        raise RuntimeError("corpus exhausted")
    def pairs(n,k):
        pp=list(itertools.combinations(range(1,n+1),2))
        pp=pp*(k//len(pp))+rng.sample(pp,k%len(pp));rng.shuffle(pp);return pp
    for n in (3,4):
        pp=pairs(n,12);dirs=[0,1]*6;rng.shuffle(dirs)
        reminders=[("copy","single")]*4+[("copy","index")]*4+[("single","index")]*4;rng.shuffle(reminders)
        for (p,q),d,rem in zip(pp,dirs,reminders):
            if d:p,q=q,p
            s=choose(n);add(train,s,p,q,"multi",0,"short")
            for o in rem:add(train,s,p if o=="single" else 0,0,o,0,"short")
    for n,k in ((3,8),(4,8),(5,4),(6,4)):
        for p,q in pairs(n,k):
            s=choose(n);g="short" if n<=4 else "long"
            add(test,s,0,0,"copy",0,g);add(test,s,0,0,"index",0,g)
            for i in (p,q):add(test,s,i,0,"single",0,g)
            for i,j in ((p,q),(q,p)):
                for v in (0,1):add(test,s,i,j,"multi",v,g)
    rng.shuffle(train);rng.shuffle(test);validate(train,"train");validate(test,"test")
    assert not {r["sid"] for r in train}&{r["sid"] for r in test}
    return train,test
def validate(rows,kind):
    assert len(rows)==(72 if kind=="train" else 192)
    assert len({r["id"] for r in rows})==len(rows) and len({r["sid"] for r in rows})==24
    assert Counter(r["op"] for r in rows)==({"multi":24,"copy":16,"single":16,"index":16} if kind=="train" else {"multi":96,"copy":24,"single":48,"index":24})
    for r in rows:
        s,p,q,o,v=r["seq"],r["p"],r["q"],r["op"],r["view"]
        assert len(set(s))==len(s)
        assert r["gold"]==gold(s,p,q,o) and r["prompt"]==question(s,p,q,o,v)
        if o=="multi":assert 1<=p<=len(s) and 1<=q<=len(s) and p!=q and gold(s,p,q,o)!=gold(s,q,p,o)
    if kind=="test":
        for g,k in (("short",16),("long",8)):
            for v in (0,1):assert sum(r["op"]=="multi" and r["group"]==g and r["view"]==v for r in rows)==2*k
def freeze(out):
    out=Path(out);out.mkdir(exist_ok=False)
    for k,rows in zip(("train","test"),make()):
        d=out/k;d.mkdir();(d/"data.json").write_bytes(c.canonical(rows))
        h=c.sha_file(d/"data.json");(d/"sha256.txt").write_text(h+"\n")
        print("MULTI_FROZEN",k,len(rows),h,dict(Counter(r["op"] for r in rows)),flush=True)
def read(path,h,kind):
    assert c.sha_file(path)==h
    rows=json.loads(Path(path).read_text());validate(rows,kind);return rows
def load(parent):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2);torch.manual_seed(SEED)
    parent=Path(parent);m=json.loads((parent/"manifest.json").read_text())
    assert m["model"]==c.MODEL and m["revision"]==c.REV and m["steps"]==72
    assert m["adapter_sha256"]["adapter_model.safetensors"]==PARENT and m["parent_sha256"]==fr.ir.PARENT
    for k,h in m["adapter_sha256"].items():assert c.sha_file(parent/"adapter"/k)==h
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==c.REV
    return tok,base
def train(data,h,parent,out):
    import torch
    from peft import PeftModel
    rows=read(data,h,"train");tok,base=load(parent)
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",is_trainable=True);model.train();model.config.use_cache=False
    params={k:v for k,v in model.named_parameters() if v.requires_grad}
    assert params and all("lora_" in k for k in params)
    before={k:v.detach().clone() for k,v in params.items()}
    opt=torch.optim.AdamW(params.values(),lr=2e-4,weight_decay=0.0)
    out=Path(out);out.mkdir(exist_ok=False);seen=Counter();losses=[]
    with (out/"steps.jsonl").open("x") as log:
        for r in rows:
            p=pc.prefix(tok,r);s=tok(r["gold"]+tok.eos_token,add_special_tokens=False)["input_ids"];assert s and len(p+s)<=192
            x=torch.tensor([p+s]);labels=torch.tensor([[-100]*len(p)+s])
            opt.zero_grad(set_to_none=True);loss=model(input_ids=x,labels=labels).loss;assert bool(torch.isfinite(loss))
            loss.backward();torch.nn.utils.clip_grad_norm_(params.values(),1.0,error_if_nonfinite=True);opt.step()
            losses.append(float(loss.detach()));seen[r["id"]]+=1
            log.write(json.dumps(dict(step=len(losses),id=r["id"],op=r["op"],loss=losses[-1],tokens=len(p+s)))+"\n");log.flush()
            if len(losses)%12==0:print("MULTI_STEP",len(losses),losses[-1],flush=True)
    assert len(losses)==72 and len(seen)==72 and set(seen.values())=={1}
    delta=math.sqrt(sum(torch.sum((v.detach()-before[k])**2).item() for k,v in params.items()));assert math.isfinite(delta) and delta>0
    model.save_pretrained(out/"adapter",safe_serialization=True)
    hashes={p.name:c.sha_file(p) for p in (out/"adapter").iterdir() if p.is_file()}
    m=dict(model=c.MODEL,revision=c.REV,steps=72,parent_sha256=PARENT,train_sha256=h,weight_delta_L2=delta,trainable_parameters=sum(v.numel() for v in params.values()),adapter_sha256=hashes,steps_sha256=c.sha_file(out/"steps.jsonl"),promotion_authorized=False)
    (out/"manifest.json").write_text(json.dumps(m,indent=2));print("MULTI_TRAIN_COMPLETE",json.dumps(m,sort_keys=True),flush=True)
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==576 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in ARMS for i in by}
    scores={};hits={}
    for a in ARMS:
        scores[a]={}
        for g in ("short","long"):
            for o,v in (("copy",0),("single",0),("index",0),("multi",0),("multi",1)):
                rr=[r for r in records if r["arm"]==a and by[r["id"]]["group"]==g and by[r["id"]]["op"]==o and by[r["id"]]["view"]==v]
                k=16 if g=="short" else 8;assert len(rr)==k*(2 if o in ("single","multi") else 1)
                pairs={};correct=0;errors=Counter()
                for r in rr:
                    q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                    raw=r["raw"].strip();hit=raw==q["gold"];hits[a,q["id"]]=hit;correct+=hit;pairs.setdefault(q["sid"],[]).append(hit)
                    if not hit and o=="multi":
                        errors["reverse" if raw==gold(q["seq"],q["q"],q["p"],o) else "one_letter" if re.fullmatch("[A-H]",raw) else "other"]+=1
                scores[a][f"{g}_{o}{v}"]=dict(n=len(rr),exact=correct,pairs=sum(all(x) for x in pairs.values()) if o in ("single","multi") else None,errors=dict(errors),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    p=scores["parent"];s=scores["pilot"]
    gate=all(s[f"short_multi{v}"]["exact"]>=29 and s[f"short_multi{v}"]["pairs"]>=13 and s[f"short_multi{v}"]["exact"]-p[f"short_multi{v}"]["exact"]>=8 for v in (0,1))
    retention=all(s[f"{g}_{o}0"]["exact"]>=p[f"{g}_{o}0"]["exact"]-1 for g in ("short","long") for o in ("copy","single","index")) and all(s[f"short_{o}0"]["exact"]>=k for o,k in (("copy",15),("index",15),("single",29)))
    transitions={}
    for g in ("short","long"):
        for o,v in (("copy",0),("single",0),("index",0),("multi",0),("multi",1)):
            transitions[f"{g}_{o}{v}"]=dict(Counter(f"{int(hits['parent',r['id']])}{int(hits['pilot',r['id']])}" for r in rows if r["group"]==g and r["op"]==o and r["view"]==v))
    return dict(scores=scores,transitions=transitions,acquisition_gate=gate,retention_gate=retention,gate=gate and retention,promotion_authorized=False,cohort_B_consumed=False)
def evaluate(data,h,parent,new,out):
    import torch
    from peft import PeftModel
    rows=read(data,h,"test");t,e=make();assert rows==e
    tok,base=load(parent);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["parent_sha256"]==PARENT and m["steps"]==72 and m["weight_delta_L2"]>0 and m["train_sha256"]==c.digest(c.canonical(t))
    for k,d in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==d
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",adapter_name="parent",is_trainable=False)
    model.load_adapter(new/"adapter",adapter_name="pilot",is_trainable=False);model.eval();model.config.use_cache=True
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for a in ARMS:
            model.set_adapter("parent" if a=="base" else a);model.requires_grad_(False)
            with model.disable_adapter() if a=="base" else nullcontext():
                for r in rows:
                    p=pc.prefix(tok,r);x=torch.tensor([p]);start=time.monotonic()
                    with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,len(p):].tolist()
                    rec=dict(arm=a,id=r["id"],raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=len(p),output_tokens=len(y),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("MULTI_EVAL_STAGE",a,len(records),flush=True)
    result=score(rows,records);result.update(test_sha256=h,train_sha256=m["train_sha256"],training_steps=72)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("MULTI_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["freeze","train","eval"]);p.add_argument("--data");p.add_argument("--sha");p.add_argument("--parent");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.mode=="freeze":freeze(a.out)
    elif a.mode=="train":train(a.data,a.sha,a.parent,a.out)
    else:evaluate(a.data,a.sha,a.parent,a.new,a.out)
