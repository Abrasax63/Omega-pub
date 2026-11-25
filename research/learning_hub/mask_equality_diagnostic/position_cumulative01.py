"""Cumulative elementary selection, with copy rehearsal and frozen evaluations."""
import argparse,json,random,time,math,re
from pathlib import Path
from collections import Counter
from contextlib import nullcontext
import copy_sft01 as c
import copy_transfer02 as ct
import copy_to_position01 as cp
import format_skill as fs
import position_representation as pos
import self_representation as sr1
import self_representation03 as sr3
import readout02 as rd
import foundational_readout as fr
SEED=202611250657
OLD="1015e47946deaad5a3ab9f072f16a30d116bbf111c2b1fc2cb5ea6f8bb5d0fef"
def question(seq,p,view):
    if view=="original":return f"Read the sequence from left to right. Which letter is at position {p} (count from 1)? Output only the letter. Sequence: {seq}"
    if view=="rephrased":return f"Sequence: {seq}. Starting with 1 for the first symbol, return only the symbol numbered {p}."
    return c.question(seq,view)
def make():
    rng=random.Random(SEED);t,e=c.make();seen={tuple(r["packet"].split()) for r in t+e}
    seen.update(tuple(r["seq"].split()) for r in ct.corpus())
    for mod in (cp,fs,pos,sr1,sr3,rd):seen.update(tuple(r["seq"]) for r in mod.corpus())
    for r in fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:seen.add(tuple(m[1].split()))
    train=[];test=[]
    def sample(alpha,n,fixed):
        for _ in range(10000):
            s=rng.sample([x for x in alpha if x not in fixed.values()],n-len(fixed))
            for p,a in sorted(fixed.items()):s.insert(p,a)
            if tuple(s) not in seen:
                seen.add(tuple(s));return " ".join(s)
        raise RuntimeError("exhausted corpus")
    def add(dst,seq,group,p,view,pair):
        gold=seq.split()[p-1] if p else seq
        dst.append(dict(id=c.digest(c.canonical([seq,p,view]))[:24],seq=seq,group=group,p=p,view=view,pair=pair,gold=gold,prompt=question(seq,p,view)))
    for n in (3,4):
        targets=list("ABCDEFGH")*4;rng.shuffle(targets)
        pp=list(range(n))*(32//n)+rng.sample(range(n),32%n);rng.shuffle(pp)
        for a,p in zip(targets,pp):
            s=sample("ABCDEFGH",n,{p:a});add(train,s,"position",p+1,"original",None)
        for _ in range(32):
            s=sample("ABCDEFGH",n,{});add(train,s,"copy",0,"trained",None)
    for group,alpha,lens in (("id","ABCDEFGH",(3,4)),("length","ABCDEFGH",(5,7)),("alphabet","IJKLMNOP",(3,4))):
        for n in lens:
            a=rng.sample(list(alpha),8);b=rng.sample(list(alpha),8)
            while any(x==y for x,y in zip(a,b)):b=rng.sample(list(alpha),8)
            pp=list(range(n))*(16//n)+rng.sample(range(n),16%n);rng.shuffle(pp)
            while any(pp[i]==pp[i+8] for i in range(8)):rng.shuffle(pp)
            for i,(x,y) in enumerate(zip(a,b)):
                p,q=pp[i],pp[i+8];s=sample(alpha,n,{p:x,q:y})
                for j in (p,q):
                    for v in ("original","rephrased"):add(test,s,group,j+1,v,f"{group}-{n}-{i}")
    for n in (3,4,5,7):
        for _ in range(4):
            s=sample("ABCDEFGH",n,{})
            for v in ("trained","paraphrase"):add(test,s,"copy",0,v,None)
    rng.shuffle(train);rng.shuffle(test)
    assert len(train)==128 and len(test)==224
    assert len({r["seq"] for r in train})==128 and len({r["seq"] for r in test})==64
    assert not {r["seq"] for r in train}&{r["seq"] for r in test}
    assert Counter(r["gold"] for r in train if r["group"]=="position")==Counter(list("ABCDEFGH")*8)
    for g,alpha in (("id","ABCDEFGH"),("length","ABCDEFGH"),("alphabet","IJKLMNOP")):
        for v in ("original","rephrased"):assert Counter(r["gold"] for r in test if r["group"]==g and r["view"]==v)==Counter(list(alpha)*4)
    for rows in (train,test):
        assert len({r["id"] for r in rows})==len(rows)
        assert all(r["gold"]==(r["seq"].split()[r["p"]-1] if r["p"] else r["seq"]) for r in rows)
    return train,test
def freeze(out):
    out=Path(out);out.mkdir(exist_ok=False)
    for k,rows in zip(("train","test"),make()):
        d=out/k;d.mkdir();(d/"data.json").write_bytes(c.canonical(rows));h=c.sha_file(d/"data.json");(d/"sha256.txt").write_text(h+"\n");print("CUMULATIVE_FROZEN",k,len(rows),h,flush=True)
def read(path,sha,kind):
    assert c.sha_file(path)==sha
    rows=json.loads(Path(path).read_text());assert rows==make()[0 if kind=="train" else 1]
    return rows
def load(old):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2);torch.manual_seed(SEED)
    old=Path(old);m=json.loads((old/"manifest.json").read_text())
    assert m["model"]==c.MODEL and m["revision"]==c.REV and m["steps"]==256
    assert m["adapter_sha256"]["adapter_model.safetensors"]==OLD
    for k,h in m["adapter_sha256"].items():assert c.sha_file(old/"adapter"/k)==h
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==c.REV
    return tok,base
def prefix(tok,r):
    p=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
    return tok(p,add_special_tokens=False)["input_ids"]
def train(data,sha,old,out):
    import torch
    from peft import PeftModel
    rows=read(data,sha,"train");tok,base=load(old)
    model=PeftModel.from_pretrained(base,Path(old)/"adapter",is_trainable=True)
    model.config.use_cache=False;model.train()
    params={k:v for k,v in model.named_parameters() if v.requires_grad}
    assert params and all("lora_" in k for k in params)
    before={k:v.detach().clone() for k,v in params.items()}
    opt=torch.optim.AdamW(params.values(),lr=5e-4,weight_decay=0.0)
    out=Path(out);out.mkdir(exist_ok=False);seen=Counter();losses=[];tokens=0
    with (out/"steps.jsonl").open("x") as log:
        for epoch in range(2):
            order=list(range(len(rows)));random.Random(SEED+epoch).shuffle(order)
            for i in order:
                r=rows[i];p=prefix(tok,r);s=tok(r["gold"]+tok.eos_token,add_special_tokens=False)["input_ids"]
                assert s and len(p+s)<=192
                x=torch.tensor([p+s]);labels=torch.tensor([[-100]*len(p)+s])
                opt.zero_grad(set_to_none=True);loss=model(input_ids=x,labels=labels).loss
                assert bool(torch.isfinite(loss))
                loss.backward();torch.nn.utils.clip_grad_norm_(params.values(),1.0,error_if_nonfinite=True);opt.step()
                losses.append(float(loss.detach()));tokens+=len(p+s);seen[r["id"]]+=1
                log.write(json.dumps(dict(step=len(losses),id=r["id"],group=r["group"],loss=losses[-1],tokens=len(p+s)))+"\n");log.flush()
                if len(losses)%16==0:print("CUMULATIVE_STEP",len(losses),losses[-1],flush=True)
    assert len(losses)==256 and len(seen)==128 and set(seen.values())=={2}
    delta=math.sqrt(sum(torch.sum((v.detach()-before[k])**2).item() for k,v in params.items()));assert math.isfinite(delta) and delta>0
    model.save_pretrained(out/"adapter",safe_serialization=True)
    hashes={p.name:c.sha_file(p) for p in (out/"adapter").iterdir() if p.is_file()}
    m=dict(model=c.MODEL,revision=c.REV,steps=256,old_adapter_sha256=OLD,train_sha256=sha,weight_delta_L2=delta,trainable_parameters=sum(v.numel() for v in params.values()),token_exposures=tokens,adapter_sha256=hashes,steps_sha256=c.sha_file(out/"steps.jsonl"),promotion_authorized=False)
    (out/"manifest.json").write_text(json.dumps(m,indent=2));print("CUMULATIVE_TRAIN_COMPLETE",json.dumps(m),flush=True)
def evaluate(data,sha,old,new,out):
    import torch
    from peft import PeftModel
    rows=read(data,sha,"test");tok,base=load(old);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["old_adapter_sha256"]==OLD and m["steps"]==256 and m["weight_delta_L2"]>0
    assert m["train_sha256"]==c.digest(c.canonical(make()[0]))
    for k,h in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,Path(old)/"adapter",adapter_name="copy",is_trainable=False)
    model.load_adapter(new/"adapter",adapter_name="cumulative",is_trainable=False);model.eval();model.config.use_cache=True
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","copy","cumulative"):
            model.set_adapter("copy" if arm=="base" else arm)
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in rows:
                    p=prefix(tok,r);x=torch.tensor([p]);start=time.monotonic()
                    with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,len(p):].tolist()
                    raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                    rec=dict(arm=arm,id=r["id"],raw=raw,prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=len(p),output_tokens=len(y),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("CUMULATIVE_EVAL_STAGE",arm,len(records),flush=True)
    by={r["id"]:r for r in rows};assert len(records)==672 and len({(r["arm"],r["id"]) for r in records})==672
    scores={}
    for arm in ("base","copy","cumulative"):
        scores[arm]={}
        for g in ("id","length","alphabet","copy"):
            for v in (("trained","paraphrase") if g=="copy" else ("original","rephrased")):
                rr=[r for r in records if r["arm"]==arm and by[r["id"]]["group"]==g and by[r["id"]]["view"]==v]
                hits=[];pairs={};valid=0
                for r in rr:
                    q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                    s=r["raw"].strip();hit=s==q["gold"];hits.append(hit);pairs.setdefault(q["pair"],[]).append(hit)
                    valid+=bool(re.fullmatch("[A-P]( [A-P])*" if g=="copy" else "[A-P]",s))
                assert len(rr)==(16 if g=="copy" else 32)
                scores[arm][g+"_"+v]=dict(n=len(rr),exact=sum(hits),valid=valid,pairs=None if g=="copy" else sum(all(p) for p in pairs.values()),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    a,b=scores["copy"],scores["cumulative"]
    gate=all(b["id_"+v]["exact"]>=30 and b["id_"+v]["pairs"]>=14 for v in ("original","rephrased")) and b["id_original"]["exact"]-a["id_original"]["exact"]>=8 and all(b[g+"_"+v]["exact"]>=28 and b[g+"_"+v]["pairs"]>=12 for g in ("length","alphabet") for v in ("original","rephrased")) and all(b["copy_"+v]["exact"]>=15 and b["copy_"+v]["exact"]>=a["copy_"+v]["exact"]-1 for v in ("trained","paraphrase"))
    result=dict(scores=scores,exploratory_gate=gate,training_steps=256,train_sha256=m["train_sha256"],test_sha256=sha,promotion_authorized=False)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("POSITION_CUMULATIVE_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["freeze","train","eval"]);p.add_argument("--data");p.add_argument("--sha");p.add_argument("--old");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.mode=="freeze":freeze(a.out)
    elif a.mode=="train":train(a.data,a.sha,a.old,a.out)
    else:evaluate(a.data,a.sha,a.old,a.new,a.out)
