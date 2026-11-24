"""Guarded pilot runner; fixture workflow does not load pretrained model weights."""
import argparse, hashlib, json, math, random, sys, time
from pathlib import Path
from collections import Counter
import equiv_process01 as proc
import equiv_pilot_freeze as pilot

ARMS=("ordinary","contrast","process")
SEED=20270160
EXPECTED={k+".json":v for k,v in proc.EXPECTED.items()}
EXPECTED.update({"traces.json":"b11c2ff75ba4d5abe7c4a83e30a6dfe3e4e5513585df02e79248389db95bdadf","retention-questions.json":"21582cb76c2a75a6d19d3486ab46d0c29fbfec0d5d41fbf65ac9b075aca53943","retention-labels.json":"47550736816876c27aad82078fac73818a45a1a3c6a21026d9f7e8790820bf91"})
def digest(p):return pilot.sha(Path(p).read_bytes())
def read(p):return json.loads(Path(p).read_text())
def require_files(folder,names):
    folder=Path(folder)
    if {p.name for p in folder.iterdir()}!=set(names):raise ValueError("unexpected or missing input")
    for name in names:
        if name in EXPECTED and digest(folder/name)!=EXPECTED[name]:raise ValueError("frozen hash mismatch "+name)
    return folder
def adapter(model):
    from peft import LoraConfig,get_peft_model
    return get_peft_model(model,LoraConfig(r=8,lora_alpha=16,target_modules=["q_proj","v_proj"],lora_dropout=0,bias="none",task_type="CAUSAL_LM"))
def gather(model,rows):
    import torch
    n=max(len(x) for x,y in rows)
    ids=torch.tensor([x+[0]*(n-len(x)) for x,y in rows])
    mask=torch.tensor([[1]*len(x)+[0]*(n-len(x)) for x,y in rows])
    labels=torch.tensor([y+[-100]*(n-len(y)) for x,y in rows])
    base=model.get_base_model()
    hidden=base.model(input_ids=ids,attention_mask=mask,use_cache=False).last_hidden_state
    logits=[];targets=[]
    for i in range(len(rows)):
        keep=labels[i,1:]!=-100
        logits.append(base.lm_head(hidden[i,:-1][keep]))
        targets.append(labels[i,1:][keep])
    return logits,targets
def batches(train,trace,tok):
    by={}
    for r in train:
        assert pilot.oracle(r["packet"])==r["label"]
        assert proc.trace(r["packet"])==trace[r["id"]]
        by.setdefault(r["pair"],[]).append(r)
    result=[]
    for key,rows in sorted(by.items()):
        pos,neg=sorted(rows,key=lambda x:not x["label"])
        assert pos["label"] and not neg["label"]
        assert len(rows)==2
        binary=[proc.pack(tok,pilot.question(r["packet"],"edges"),"Yes" if r["label"] else "No") for r in (pos,neg)]
        aux=[proc.pack(tok,proc.trace_question(r["packet"]),trace[r["id"]]) for r in (pos,neg)]
        result.append((key,binary+aux))
    return result
def loop(model,data,yes,no,arm,out,epochs=2,kind="fixture"):
    import torch
    out=Path(out);out.mkdir()
    torch.manual_seed(SEED)
    params=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
    assert params and all("lora_" in n for n,p in params)
    before={n:p.detach().clone() for n,p in params}
    opt=torch.optim.AdamW([p for n,p in params],lr=1e-4)
    rng=random.Random(SEED);order=[];losses=[];tokens=0;supervised=0;padded=0
    start=time.monotonic()
    model.train()
    for epoch in range(epochs):
        ix=list(range(len(data)));rng.shuffle(ix)
        for i in ix:
            key,rows=data[i];order.append(key)
            tokens+=sum(len(x) for x,y in rows);padded+=4*max(len(x) for x,y in rows)
            supervised+=sum(sum(v!=-100 for v in y) for x,y in rows[:4 if arm=="process" else 2])
            opt.zero_grad(set_to_none=True)
            ls,ts=gather(model,rows)
            loss,_=proc.objectives(ls,ts,yes,no,arm)
            if not torch.isfinite(loss):raise ValueError("nonfinite loss")
            loss.backward();opt.step();losses.append(float(loss.detach()))
    delta=math.sqrt(sum(float((p.detach()-before[n]).square().sum()) for n,p in params))
    assert delta>0
    assert all(not p.requires_grad and p.grad is None for n,p in model.named_parameters() if "lora_" not in n)
    model.save_pretrained(out/"adapter",safe_serialization=True)
    files={p.name:digest(p) for p in (out/"adapter").iterdir() if p.is_file()}
    manifest=dict(kind=kind,arm=arm,model=pilot.MODEL if kind=="real" else "random_fixture",revision=pilot.REV if kind=="real" else None,seed=SEED,updates=len(order),exposure_sha256=pilot.sha(json.dumps(order).encode()),input_tokens=tokens,padded_tokens=padded,supervised_tokens=supervised,delta_L2=delta,adapter_hashes=files,losses=losses,seconds=time.monotonic()-start,base_frozen=True)
    pilot.dump(out/"manifest.json",manifest)
    return manifest
def verify_adapter(folder,kind,arm):
    folder=Path(folder);m=read(folder/"manifest.json")
    if m["kind"]!=kind or m["arm"]!=arm or m["delta_L2"]<=0:raise ValueError("adapter manifest")
    if kind=="real" and (m["model"]!=pilot.MODEL or m["revision"]!=pilot.REV or m["updates"]!=192):raise ValueError("base revision or updates")
    if {p.name:digest(p) for p in (folder/"adapter").iterdir() if p.is_file()}!=m["adapter_hashes"]:raise ValueError("adapter digest")
    return m
def real_model():
    import torch
    from transformers import AutoModelForCausalLM
    m=AutoModelForCausalLM.from_pretrained(pilot.MODEL,revision=pilot.REV,trust_remote_code=False,torch_dtype=torch.float32)
    if m.config._commit_hash!=pilot.REV or m.config.model_type!="llama":raise ValueError("model revision/architecture")
    return m
def tokenizer():
    from transformers import AutoTokenizer
    t=AutoTokenizer.from_pretrained(pilot.MODEL,revision=pilot.REV,trust_remote_code=False)
    return t
def candidates(tok):
    x=[tok.encode(k,add_special_tokens=False) for k in ("Yes","No")]
    assert all(len(v)==1 and tok.decode(v)==k for k,v in zip(("Yes","No"),x))
    return x[0][0],x[1][0]
def train(folder,out,arm,authorization):
    if authorization!="EXPLICIT_USER_GO" or arm not in ARMS:raise ValueError("training not authorized")
    import torch
    torch.set_num_threads(2)
    folder=require_files(folder,("train.json","dev.json","traces.json","process-manifest.json"))
    train=read(folder/"train.json");tr={r["id"]:r["target"] for r in read(folder/"traces.json") if r["split"]=="train"}
    assert len(train)==192 and len(tr)==192
    tok=tokenizer();yes,no=candidates(tok);data=batches(train,tr,tok)
    assert len(data)==96
    torch.manual_seed(SEED);model=adapter(real_model())
    result=loop(model,data,yes,no,arm,out,kind="real")
    assert result["updates"]==192
def prompts(folder):
    folder=require_files(folder,("questions.json","retention-questions.json"))
    q=read(folder/"questions.json");r=read(folder/"retention-questions.json")
    assert len(q)==len(r)==64 and all(set(x)=={"id","packet"} for x in q) and all(set(x)=={"id","question"} for x in r)
    return [("equiv",v,x["id"],pilot.question(x["packet"],v)) for v in ("edges","matrix") for x in q]+[("retention","direct",x["id"],x["question"]) for x in r]
def predict(model,tok,rows,arm):
    import torch
    yes,no=candidates(tok);model.eval();results=[]
    for task,view,i,q in rows:
        text=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
        x=tok(text,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
        assert n+8<=1024
        with torch.inference_mode():
            last=model(**x,use_cache=False).logits[0,-1]
            p=float(torch.softmax(last[[yes,no]].float(),dim=0)[0])
            ids=model.generate(**x,do_sample=False,max_new_tokens=8,pad_token_id=tok.eos_token_id)[0,n:].tolist()
        results.append(dict(arm=arm,task=task,view=view,id=i,raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False),p_yes_binary=p,ids=ids,prompt_sha256=pilot.sha(q.encode()),input_tokens=n))
    return results
def infer(folder,out,arm,adapter_folder=None):
    import torch
    from peft import PeftModel
    torch.set_num_threads(2);rows=prompts(folder);tok=tokenizer()
    if arm!="base":verify_adapter(adapter_folder,"real",arm)
    model=real_model()
    if arm!="base":model=PeftModel.from_pretrained(model,Path(adapter_folder)/"adapter",is_trainable=False)
    pilot.dump(Path(out),predict(model,tok,rows,arm))
def score_records(labels,retention,records):
    lookup={}
    for r in labels:
        assert pilot.oracle(r["packet"])==r["label"]
        for v in ("edges","matrix"):
            lookup["equiv",v,r["id"]]=(r,pilot.question(r["packet"],v))
    for r in retention:lookup["retention","direct",r["id"]]=(r,r["question"])
    arms=("base",)+ARMS
    keys={(a,)+k for a in arms for k in lookup}
    if len(records)!=len(keys) or {(r["arm"],r["task"],r["view"],r["id"]) for r in records}!=keys:raise ValueError("prediction coverage")
    out={a:{} for a in arms};grouped={}
    for r in records:
        label,q=lookup[r["task"],r["view"],r["id"]]
        if r["prompt_sha256"]!=pilot.sha(q.encode()) or not 0<=r["p_yes_binary"]<=1 or not 0<=len(r["ids"])<=8:raise ValueError("prediction trace")
        g=r["view"] if r["task"]=="equiv" else label["domain"]
        grouped.setdefault((r["arm"],g),[]).append((label,r))
    for (a,g),rows in grouped.items():
        hits=Counter();pairs={};binary_pairs={};raw=Counter()
        for l,r in rows:
            gold="Yes" if l["label"] else "No";ok=r["raw"]==gold;bk=(r["p_yes_binary"]>.5)==l["label"]
            hits["strict"]+=ok;hits["binary"]+=bk;hits["valid"]+=r["raw"] in ("Yes","No")
            hits["yes" if l["label"] else "no"]+=ok
            pairs.setdefault(l["pair"],[]).append(ok);binary_pairs.setdefault(l["pair"],[]).append(bk)
            raw[r["raw"]]+=1
        assert all(len(v)==2 for v in pairs.values())
        out[a][g]=dict(n=len(rows),**hits,pairs_both=sum(all(x) for x in pairs.values()),binary_pairs_both=sum(all(x) for x in binary_pairs.values()),raw=dict(raw))
        for k in ("strict","binary","valid","yes","no"):out[a][g].setdefault(k,0)
    verdict={}
    for a in ARMS:
        gates={}
        for v in ("edges","matrix"):
            s=out[a][v];b=out["base"][v]
            gates[v]=s["n"]==64 and s["strict"]>=48 and s["strict"]-b["strict"]>=7 and s["pairs_both"]>=20 and min(s["yes"],s["no"])>=24
        for v in ("edge","syntax"):
            s=out[a][v];b=out["base"][v]
            gates["retention_"+v]=s["strict"]>=b["strict"]-.05*s["n"]
        verdict[a]=dict(gates=gates,pass_all=all(gates.values()),strict_delta_vs_ordinary={v:out[a][v]["strict"]-out["ordinary"][v]["strict"] for v in ("edges","matrix")},pair_delta_vs_ordinary={v:out[a][v]["pairs_both"]-out["ordinary"][v]["pairs_both"] for v in ("edges","matrix")})
    return dict(scores=out,verdict=verdict,promotion_authorized=False)
def score(folder,files,out):
    folder=require_files(folder,("labels.json","retention-labels.json"))
    records=[r for f in files for r in read(f)]
    pilot.dump(Path(out),score_records(read(folder/"labels.json"),read(folder/"retention-labels.json"),records))
def fixture(train_folder,questions_folder,labels_folder,out):
    import torch
    from transformers import LlamaConfig,LlamaForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2);out=Path(out);out.mkdir()
    tr=require_files(train_folder,("train.json","dev.json","traces.json","process-manifest.json"))
    rows=prompts(questions_folder)
    labels_folder=require_files(labels_folder,("labels.json","retention-labels.json"))
    labels=read(labels_folder/"labels.json");ret=read(labels_folder/"retention-labels.json")
    tok=tokenizer()
    maxlen=max(len(tok.encode(tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True),add_special_tokens=False)) for _,_,_,q in rows)
    assert maxlen+8<=1024
    data=batches(read(tr/"train.json"),{r["id"]:r["target"] for r in read(tr/"traces.json") if r["split"]=="train"},tok)
    assert len(data)==96
    def fresh():
        torch.manual_seed(SEED);return LlamaForCausalLM(LlamaConfig(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=2,max_position_embeddings=64))
    fixture_rows=[([7,8,9,1,3],[-100,-100,-100,1,3]),([7,9,8,2,3],[-100,-100,-100,2,3]),([8,9,4,5,3],[-100,-100,4,5,3]),([9,8,5,4,3],[-100,-100,5,4,3])]
    m=adapter(fresh()).eval()
    x,t=gather(m,fixture_rows);y,u=proc.gather(m,fixture_rows)
    assert all(torch.allclose(a,b,atol=1e-6) for a,b in zip(x,y))
    assert all(torch.equal(a,b) for a,b in zip(t,u))
    for a,b in zip(x,y):assert a.shape==b.shape
    params=[p for p in m.parameters() if p.requires_grad]
    gx=torch.autograd.grad(proc.objectives(x,t,1,2,"process")[0],params)
    gy=torch.autograd.grad(proc.objectives(y,u,1,2,"process")[0],params)
    assert all(torch.allclose(a,b,atol=1e-6) for a,b in zip(gx,gy))
    manifests={}
    for arm in ARMS:
        m=adapter(fresh());folder=out/arm
        manifests[arm]=loop(m,[("p0",fixture_rows),("p1",fixture_rows)],1,2,arm,folder)
        verify_adapter(folder,"fixture",arm)
        reload=PeftModel.from_pretrained(fresh(),folder/"adapter",is_trainable=False).eval();m.eval()
        with torch.no_grad():
            inp=torch.tensor([[7,8,9]])
            assert torch.allclose(m(inp).logits,reload(inp).logits,atol=1e-6)
            assert torch.equal(m.generate(inp,max_new_tokens=2,do_sample=False,pad_token_id=0),reload.generate(inp,max_new_tokens=2,do_sample=False,pad_token_id=0))
    assert len({(m["updates"],m["exposure_sha256"],m["input_tokens"],m["padded_tokens"]) for m in manifests.values()})==1
    # Full scorer exercised with synthetic constant and oracle predictions, not model scores.
    answers={r["id"]:r["label"] for r in labels+ret}
    fake=[]
    for arm in ("base",)+ARMS:
        for task,v,i,q in rows:
            yes=True if arm=="base" else answers[i]
            fake.append(dict(arm=arm,task=task,view=v,id=i,raw="Yes" if yes else "No",p_yes_binary=float(yes),ids=[1],prompt_sha256=pilot.sha(q.encode())))
    s=score_records(labels,ret,fake)
    assert s["scores"]["base"]["edges"]["strict"]==32 and s["scores"]["base"]["edges"]["pairs_both"]==0
    assert all(s["verdict"][a]["pass_all"] for a in ARMS)
    rejects=0
    def rejected(fn):
        nonlocal rejects
        try:fn()
        except (ValueError,AssertionError):rejects+=1
        else:raise AssertionError("accepted invalid input")
    rejected(lambda:score_records(labels,ret,fake[:-1]))
    rejected(lambda:require_files(labels_folder,("questions.json","retention-questions.json")))
    rejected(lambda:require_files(questions_folder,("train.json","dev.json","traces.json","process-manifest.json")))
    rejected(lambda:verify_adapter(out/"ordinary","real","ordinary"))
    f=out/"ordinary"/"adapter"/"adapter_config.json";raw=f.read_bytes();f.write_bytes(raw+b" ")
    rejected(lambda:verify_adapter(out/"ordinary","fixture","ordinary"));f.write_bytes(raw)
    rejected(lambda:train(train_folder,out/"forbidden","ordinary","NO"))
    result=dict(max_eval_prompt_tokens=maxlen,train_pairs=len(data),prediction_contract_rows=len(fake),rejected_invalid_cases=rejects,logit_gradient_match=True,adapter_reload_match=True,fixture={a:{k:v for k,v in m.items() if k in ("updates","input_tokens","padded_tokens","delta_L2","exposure_sha256")} for a,m in manifests.items()},pretrained_weights_loaded=False,training_authorized=False)
    pilot.dump(out/"result.json",result);print("RUNNER_FIXTURE",json.dumps(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("stage");p.add_argument("args",nargs="+");a=p.parse_args()
    if a.stage=="score":score(a.args[0],a.args[2:],a.args[1])
    elif a.stage in ("fixture","train","infer"):globals()[a.stage](*a.args)
    else:raise ValueError("stage")
