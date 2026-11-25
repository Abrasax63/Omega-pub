import argparse,itertools,random,re,time,json
from pathlib import Path
from collections import Counter
from self_representation import corpus as prior01,read_prompt
from self_representation03 import corpus as prior03
from position_representation import dump,sha,first,encode
from followup import MODELS
ARMS=("A","B","C")
def corpus():
    rng=random.Random(202611250555);alpha=list("ABCDEFGH");rows=[];seen=set()
    excluded={tuple(r["seq"]) for r in prior01()+prior03()}
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
            else:raise RuntimeError("duplicate list")
            seen.add(tuple(s));assert s[p]==x and s[q]==y
            for pos,gold in ((p,x),(q,y)):
                assert s[pos]==gold==dict(enumerate(s,1))[pos+1]
                rows.append(dict(id=sha(dump([s,pos]))[:24],pair=f"{n}-{i}",n=n,seq=s,p=pos+1,gold=gold))
        assert Counter(r["gold"] for r in rows if r["n"]==n)==Counter(alpha*2)
    assert len(rows)==32 and len(seen)==16 and not seen&excluded and len({r["id"] for r in rows})==32
    rng.shuffle(rows);return rows
def prompt(r,arm):
    e=encode(r["seq"],"indexed")
    if arm=="A":return read_prompt(r,e)
    base="Read the key:value table. Return only the letter paired with the requested key."
    example=" Example: 1:L 2:J 3:K. Key 2 -> J." if arm=="C" else ""
    return base+example+f" Table: {e}. Key: {r['p']}. Letter:"
def check(rows):
    for r in rows:
        pairs=[x.split(":") for x in encode(r["seq"],"indexed").split()]
        assert [(int(k),v) for k,v in pairs]==list(enumerate(r["seq"],1))
        assert dict(pairs)[str(r["p"])]==r["gold"]
    for pair in {r["pair"] for r in rows}:
        a,b=[r for r in rows if r["pair"]==pair];assert a["seq"]==b["seq"] and a["p"]!=b["p"] and a["gold"]!=b["gold"]
def run(out):
    rows=corpus();check(rows);digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm,r in itertools.product(ARMS,rows):
            q=prompt(r,arm)
            x=tok(tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True),return_tensors="pt",add_special_tokens=False)
            n=x["input_ids"].shape[1];assert n+4<=1024
            start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=4,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(arm=arm,id=r["id"],raw=raw,prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start)
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    scores={};hits={};by={r["id"]:r for r in rows}
    for arm in ARMS:
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==32 and {r["id"] for r in rr}==set(by)
        h={r["id"]:first(r["raw"])==by[r["id"]]["gold"] for r in rr};hits[arm]=h
        pairs=sum(all(h[r["id"]] for r in rows if r["pair"]==p) for p in {r["pair"] for r in rows})
        scores[arm]=dict(primary=sum(h.values()),strict=sum(r["raw"]==by[r["id"]]["gold"] for r in rr),valid=sum(first(r["raw"]) is not None for r in rr),pairs=pairs,by_length={str(n):sum(h[r["id"]] for r in rows if r["n"]==n) for n in (5,7)},input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr),mastery=sum(h.values())>=28 and pairs>=12)
    def contrast(a,b):return dict(Counter("both" if hits[a][i] and hits[b][i] else a+"_only" if hits[a][i] else b+"_only" if hits[b][i] else "neither" for i in by))
    a,b,c=(scores[k] for k in ARMS)
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,arms=scores,paired_B_A=contrast("B","A"),paired_C_B=contrast("C","B"),short_gate=b["primary"]-a["primary"]>=6 and b["pairs"]-a["pairs"]>=3 and b["seconds"]<=a["seconds"],example_gate=c["primary"]-b["primary"]>=4 and c["pairs"]-b["pairs"]>=2,oracle_correct=32,oracle_pairs=16,constant_correct=4,constant_pairs=0)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("READOUT02_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="readout02");a=p.parse_args()
    if a.check:
        rows=corpus();check(rows);print("ORACLE_CHECK",len(rows),sha(dump(rows)))
    else:run(a.output)
