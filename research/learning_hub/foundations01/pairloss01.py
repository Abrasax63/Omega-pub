"""PAIRLOSS01: matched pair batching and counterfactual margin objective."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import time
from corpus_gate import identities
from membership_curriculum import create,validate
from atomic_curriculum import create as atomic_create
from capacity01_contract import create as capacity_create
from membership_sft_contract import MODEL,REV,MAX_LENGTH,SEED,sha,chat,target,score_pair
TRAIN_SHA="bd67b38d0eab09654fe8d58eac22b72e3d63a23dc25c961f843cde90926f26d7"

def frozen_train():
    rows=create(SEED,"train");validate(rows,"train")
    if hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=TRAIN_SHA:
        raise ValueError("TRAIN_DIGEST")
    return rows

def families(rows):
    groups={}
    for r in rows: groups.setdefault(r["pair"],[]).append(r)
    result=[]
    for k in sorted(groups):
        pair=sorted(groups[k],key=lambda r:r["label"])
        if len(pair)!=2 or [r["label"] for r in pair]!=[False,True]: raise ValueError("PAIR")
        result.append(pair)
    return result

def fresh_eval():
    old=atomic_create(8591958126413765487,"eval")+create(17570745935616618759,"eval")+capacity_create()
    used={identities(r["packet"])[0] for r in old}
    rows=[];counts=Counter()
    for i in range(10):
        for pair in families(create(20261201+i,"eval")):
            n=len(pair[0]["packet"]["nodes"])
            keys={identities(r["packet"])[0] for r in pair}
            if counts[n]>=16 or keys & used: continue
            used.update(keys);counts[n]+=1
            p=f"pairloss-{n}-{counts[n]}"
            for r in pair:
                rid=hashlib.sha256((p+str(r["label"])).encode()).hexdigest()[:20]
                rows.append(dict(r,id=rid,pair=p))
        if counts=={5:16,6:16}: break
    validate(rows,"eval")
    return sorted(rows,key=lambda r:r["id"])

def freeze(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    train=frozen_train();ev=fresh_eval()
    for k,rows in (("train",train),("eval",ev),("questions",[dict(id=r["id"],packet=r["packet"]) for r in ev])):
        (out/(k+".json")).write_text(json.dumps(rows,sort_keys=True,separators=(",",":")))
    m={k+"_sha":sha(out/(k+".json")) for k in ("train","eval","questions")}
    (out/"manifest.json").write_text(json.dumps(m))
    return m

def train(path,expected,arm,out):
    import torch
    import transformers,peft
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import LoraConfig,get_peft_model
    if arm not in ("ce","pair") or expected!=TRAIN_SHA or sha(path)!=expected: raise ValueError("TRAIN_CONTRACT")
    rows=json.loads(Path(path).read_text());validate(rows,"train")
    pairs=families(rows);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(2);torch.manual_seed(SEED)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    digits={s:tok.encode(s,add_special_tokens=False) for s in ("Yes","No")}
    if not all(len(ids)==1 and tok.decode(ids,skip_special_tokens=False)==s for s,ids in digits.items()): raise ValueError("TOKEN_ROUNDTRIP")
    y,n=digits["Yes"][0],digits["No"][0]
    base=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32).to("cpu")
    if base.config._commit_hash!=REV: raise ValueError("MODEL_REVISION")
    base.config.use_cache=False
    model=get_peft_model(base,LoraConfig(r=8,lora_alpha=16,lora_dropout=0.0,bias="none",target_modules=["q_proj","v_proj"],task_type="CAUSAL_LM"))
    params={k:v for k,v in model.named_parameters() if v.requires_grad}
    before={k:v.detach().clone() for k,v in params.items()}
    opt=torch.optim.AdamW(params.values(),lr=.0005,weight_decay=0.0)
    model.train();steps=0;exposures=0;supervised=0;seen=Counter();start=time.monotonic()
    with (out/"steps.jsonl").open("x") as log:
        for epoch in range(2):
            order=list(range(len(pairs)));random.Random(SEED+epoch).shuffle(order)
            for i in order:
                pair=pairs[i];xs=[];ls=[];positions=[]
                for r in pair:
                    p=tok(chat(tok,r["packet"],"edges"),add_special_tokens=False)["input_ids"]
                    t=tok(target(r["label"])+tok.eos_token,add_special_tokens=False)["input_ids"]
                    if not p or len(p)+len(t)>MAX_LENGTH or t[0] != digits[target(r["label"])][0]: raise ValueError("CONTEXT_OR_TARGET")
                    positions.append(len(p)-1);xs.append(p+t);ls.append([-100]*len(p)+t)
                    exposures+=len(p)+len(t);supervised+=len(t);seen[r["id"]]+=1
                length=max(map(len,xs));mask=[[1]*len(x)+[0]*(length-len(x)) for x in xs]
                x=torch.tensor([a+[tok.eos_token_id]*(length-len(a)) for a in xs])
                labels=torch.tensor([a+[-100]*(length-len(a)) for a in ls])
                opt.zero_grad(set_to_none=True)
                result=model(input_ids=x,attention_mask=torch.tensor(mask),labels=labels)
                logits=result.logits[torch.arange(2),torch.tensor(positions),:].float()
                s=logits[:,y]-logits[:,n];margin=s[1]-s[0]
                penalty=torch.nn.functional.softplus(1-margin)
                loss=result.loss+penalty if arm=="pair" else result.loss
                if not bool(torch.isfinite(loss)): raise ValueError("NONFINITE_LOSS")
                loss.backward();torch.nn.utils.clip_grad_norm_(params.values(),1.0,error_if_nonfinite=True);opt.step()
                steps+=1;rec=dict(step=steps,pair=pair[0]["pair"],ids=[r["id"] for r in pair],ce=float(result.loss.detach()),margin=float(margin.detach()),penalty=float(penalty.detach()),loss=float(loss.detach()))
                log.write(json.dumps(rec)+"\n");log.flush()
                if steps%16==0: print("PAIRLOSS_STEP",arm,steps,rec,flush=True)
    if steps!=128 or len(seen)!=128 or set(seen.values())!={2}: raise ValueError("INCOMPLETE")
    delta=math.sqrt(sum(torch.sum((v.detach()-before[k])**2).item() for k,v in params.items()))
    if not math.isfinite(delta) or delta<=0: raise ValueError("DELTA")
    adapter=out/"adapter";model.save_pretrained(adapter,safe_serialization=True)
    hashes={p.name:sha(p) for p in adapter.iterdir() if p.is_file()}
    if "adapter_model.safetensors" not in hashes: raise ValueError("ADAPTER")
    m=dict(status="ACTUAL_PAIRLOSS_TRAINED",arm=arm,model=MODEL,revision=REV,seed=SEED,steps=steps,examples=128,epochs=2,train_sha256=expected,weight_delta_L2=delta,trainable_parameters=sum(v.numel() for v in params.values()),token_exposures=exposures,supervised_token_exposures=supervised,adapter_sha256=hashes,steps_sha256=sha(out/"steps.jsonl"),seconds=time.monotonic()-start,torch=torch.__version__,transformers=transformers.__version__,peft=peft.__version__,promotion_authorized=False)
    (out/"manifest.json").write_text(json.dumps(m,indent=2));print("PAIRLOSS_TRAIN_COMPLETE",json.dumps(m),flush=True)

def finish(labels,expected,ce,pair,out):
    if sha(labels)!=expected: raise ValueError("LABEL_DIGEST")
    rows=json.loads(Path(labels).read_text())
    rec=[]
    for a,p in (("base",ce),("lora",pair)):
        for line in Path(p).read_text().splitlines():
            r=json.loads(line)
            if r["arm"]!=("ce" if a=="base" else "pair"): raise ValueError("ARM")
            rec.append(dict(r,arm=a))
    report=score_pair(rows,rec)
    report["scores"]={"ce":report["scores"]["base"],"pair":report["scores"]["lora"]}
    report["arm_mapping"]={"ce":"matched cross entropy","pair":"cross entropy plus pair margin"}
    report["prediction_sha256"]={"ce":sha(ce),"pair":sha(pair)}
    report["eval_sha256"]=expected
    with Path(out).open("x") as f: json.dump(report,f,indent=2)
    print("PAIRLOSS_RESULT",report["status"],json.dumps(report["comparisons"]),flush=True)
    for a,views in report["scores"].items():
        for v,s in views.items():print(a,v,s["correct"],s["pairs_both_correct"],s["mean_toggle_probability_difference"],flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    for name,keys in (("freeze",("out",)),("train",("train","sha","arm","out")),("score",("labels","sha","ce","pair","out"))):
        s=sub.add_parser(name)
        for k in keys:s.add_argument("--"+k,required=True)
    a=p.parse_args()
    if a.cmd=="freeze":
        import os
        m=freeze(a.out);print("PAIRLOSS_FREEZE",json.dumps(m))
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"],"a") as f:
                for k,v in m.items():f.write(k+"="+v+"\n")
    elif a.cmd=="train":train(a.train,a.sha,a.arm,a.out)
    else:finish(a.labels,a.sha,a.ce,a.pair,a.out)
