"""Probe instruction interference from frozen COPY-SFT01; no training."""
import argparse,json,random,re,time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import copy_sft01 as copy
import copy_transfer02 as transfer
import format_skill as fmt
import position_representation as pos
import self_representation as sr1
import self_representation03 as sr3
import readout02 as rd
def corpus():
    rng=random.Random(202611250639);alpha=list("ABCDEFGH");rows=[];seen=set()
    train,test=copy.make()
    excluded={tuple(r["packet"].split()) for r in train+test}
    excluded.update(tuple(r["seq"].split()) for r in transfer.corpus())
    for module in (fmt,pos,sr1,sr3,rd):
        excluded.update(tuple(r["seq"]) for r in module.corpus())
    for n in (5,7):
        a=rng.sample(alpha,8);b=rng.sample(alpha,8)
        while any(x==y for x,y in zip(a,b)):b=rng.sample(alpha,8)
        pp=list(range(n))*(16//n)+rng.sample(range(n),16%n);rng.shuffle(pp)
        while any(pp[i]==pp[i+8] for i in range(8)):rng.shuffle(pp)
        for i,(x,y) in enumerate(zip(a,b)):
            p,q=pp[i],pp[i+8]
            for attempt in range(1000):
                s=rng.sample([z for z in alpha if z not in (x,y)],n-2)
                s.insert(min(p,q),x if p<q else y);s.insert(max(p,q),y if p<q else x)
                if tuple(s) not in seen|excluded:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s))
            for j,g in ((p,x),(q,y)):
                assert s[j]==g
                rows.append(dict(id=pos.sha(pos.dump([s,j]))[:24],pair=f"{n}-{i}",seq=s,p=j+1,gold=g))
    assert len(seen)==16 and len(rows)==32 and not seen&excluded
    assert Counter(r["gold"] for r in rows)==Counter(alpha*4)
    rd.check(rows)
    rng.shuffle(rows);return rows
def cases(rows):
    out=[]
    for view in ("spaced","indexed"):
        for r in rows:
            out.append(dict(id=r["id"],pair=r["pair"],view=view,seq=" ".join(r["seq"]),prompt=pos.question(r,view),gold=r["gold"]))
    for pair in sorted({r["pair"] for r in rows}):
        seq=next(" ".join(r["seq"]) for r in rows if r["pair"]==pair)
        out.append(dict(id=pos.sha(seq)[:24],pair=pair,view="copy",seq=seq,prompt=copy.question(seq,"trained"),gold=seq))
    assert len(out)==80 and len({(r["id"],r["view"]) for r in out})==80
    return out
def run(adapter,out):
    rows=corpus();tasks=cases(rows);out=Path(out);out.mkdir(exist_ok=False)
    (out/"corpus.json").write_bytes(copy.canonical(tasks));print("POSITION_FROZEN",copy.sha_file(out/"corpus.json"),flush=True)
    adapter=Path(adapter);m=json.loads((adapter/"manifest.json").read_text())
    assert m["train_sha256"]=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert m["steps"]==256 and m["model"]==copy.MODEL and m["revision"]==copy.REV
    assert copy.sha_file(adapter/"adapter"/"adapter_model.safetensors")=="1015e47946deaad5a3ab9f072f16a30d116bbf111c2b1fc2cb5ea6f8bb5d0fef"
    for k,h in m["adapter_sha256"].items():assert copy.sha_file(adapter/"adapter"/k)==h
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(copy.MODEL,revision=copy.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(copy.MODEL,revision=copy.REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==copy.REV
    model=PeftModel.from_pretrained(base,adapter/"adapter",is_trainable=False).eval();model.config.use_cache=True
    assert not any(p.requires_grad for p in model.parameters())
    recs=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","lora"):
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in tasks:
                    p=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
                    x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];start=time.monotonic()
                    with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                    rec=dict(arm=arm,view=r["view"],id=r["id"],raw=raw,prompt_sha256=pos.sha(r["prompt"]),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
                    recs.append(rec);log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush()
            print("POSITION_STAGE",arm,len(recs),flush=True)
    result=score(tasks,recs);result.update(training=False,promotion_authorized=False,corpus_sha256=copy.sha_file(out/"corpus.json"))
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("COPY_POSITION_RESULT",json.dumps(result,sort_keys=True),flush=True)
def score(tasks,recs):
    by={(r["view"],r["id"]):r for r in tasks}
    assert len(recs)==160 and {(r["arm"],r["view"],r["id"]) for r in recs}=={(a,v,i) for a in ("base","lora") for v,i in by}
    scores={}
    for arm in ("base","lora"):
        scores[arm]={}
        for view in ("spaced","indexed","copy"):
            rr=[r for r in recs if r["arm"]==arm and r["view"]==view]
            hits={};pairs={};permissive=recopy=invalid=wrong=0
            for r in rr:
                q=by[view,r["id"]];assert r["prompt_sha256"]==pos.sha(q["prompt"])
                raw=r["raw"].strip();good=raw==q["gold"];hits[r["id"]]=good
                pairs.setdefault(q["pair"],[]).append(good)
                permissive+=int((raw if view=="copy" else fmt.extract_long(raw))==q["gold"])
                recopy+=int(view!="copy" and raw==q["seq"])
                valid=bool(re.fullmatch("[A-H]" if view!="copy" else "[A-H]( [A-H])*",raw))
                invalid+=int(not valid);wrong+=int(valid and not good)
            scores[arm][view]=dict(n=len(rr),exact=sum(hits.values()),permissive=permissive,pairs=sum(all(p) for p in pairs.values()) if view!="copy" else None,recopy=recopy,invalid=invalid,wrong=wrong,input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    b,l=scores["base"],scores["lora"];vs=("spaced","indexed")
    delta={v:{"exact":l[v]["exact"]-b[v]["exact"],"pairs":l[v]["pairs"]-b[v]["pairs"]} for v in vs}
    return dict(scores=scores,delta=delta,interference=any(d["exact"]<=-8 or d["pairs"]<=-4 for d in delta.values()),transfer=any(d["exact"]>=8 and d["pairs"]>=4 for d in delta.values()) and l["copy"]["exact"]>=b["copy"]["exact"]-1,mastery=all(l[v]["exact"]>=31 and l[v]["pairs"]>=15 for v in vs))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--adapter");p.add_argument("--out");a=p.parse_args()
    if a.check:
        t=cases(corpus());print("POSITION_CHECK",len(t),copy.digest(copy.canonical(t)))
    else:run(a.adapter,a.out)
