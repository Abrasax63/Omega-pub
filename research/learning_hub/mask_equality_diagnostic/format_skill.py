import argparse,itertools,json,random,re,time
from pathlib import Path
from collections import Counter
from self_representation import corpus as old1
from self_representation03 import corpus as old3
from readout02 import corpus as oldread,prompt,check
from position_representation import dump,sha,first
from followup import MODELS
ALPHA="ABCDEFGH"
def corpus():
    rng=random.Random(202611250602);rows=[];seen=set()
    excluded={tuple(r["seq"]) for r in old1()+old3()+oldread()}
    for n in (5,7):
        a=rng.sample(list(ALPHA),8);b=rng.sample(list(ALPHA),8)
        while any(x==y for x,y in zip(a,b)):b=rng.sample(list(ALPHA),8)
        pp=list(range(n))*(16//n)+rng.sample(range(n),16%n);rng.shuffle(pp)
        while any(pp[i]==pp[i+8] for i in range(8)):rng.shuffle(pp)
        for i,(x,y) in enumerate(zip(a,b)):
            p,q=pp[i],pp[i+8]
            for attempt in range(1000):
                s=rng.sample([z for z in ALPHA if z not in (x,y)],n-2)
                s.insert(min(p,q),x if p<q else y);s.insert(max(p,q),y if p<q else x)
                if tuple(s) not in seen|excluded:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s));assert s[p]==x and s[q]==y
            for pos,gold in ((p,x),(q,y)):
                rows.append(dict(id=sha(dump([s,pos]))[:24],pair=f"{n}-{i}",n=n,seq=s,p=pos+1,gold=gold))
        assert Counter(r["gold"] for r in rows if r["n"]==n)==Counter(list(ALPHA)*2)
    assert len(rows)==32 and len(seen)==16 and not seen&excluded and len({r["id"] for r in rows})==32
    rng.shuffle(rows);check(rows);return rows
def extract_long(raw):
    m=re.fullmatch(r"\s*([A-H])[.!?]?\s*",raw)
    if m:return m[1]
    letters=re.findall(r"\b[A-H]\b",raw)
    return letters[0] if len(letters)==1 else None
def preflight():
    rows=corpus()
    assert extract_long("The letter is D.")=="D"
    assert extract_long("A or D") is None
    assert extract_long("D.")=="D" and extract_long("letter") is None
    return rows
def run(out):
    rows=preflight();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    groups={}
    for letter in ALPHA:
        ids=set()
        for text in (letter," "+letter):
            enc=tok.encode(text,add_special_tokens=False)
            if len(enc)==1 and tok.decode(enc,skip_special_tokens=False,clean_up_tokenization_spaces=False)==text:ids.add(enc[0])
        assert ids;groups[letter]=sorted(ids)
    assert len({len(v) for v in groups.values()})==1 and len(set(itertools.chain.from_iterable(groups.values())))==sum(map(len,groups.values()))
    print("CANDIDATE_TOKENS",dump(groups),flush=True)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm,r in itertools.product(("A","B"),rows):
            q=prompt(r,arm);chat=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
            x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];assert n+32<=1024
            start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            gen_seconds=time.monotonic()-start
            decode=lambda ids:tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            short,long=decode(y[:4]),decode(y)
            start=time.monotonic()
            with torch.inference_mode():logits=model(**x).logits[0,-1].float()
            forward_seconds=time.monotonic()-start
            raw_logits={k:[float(logits[i]) for i in ids] for k,ids in groups.items()}
            scores={k:float(torch.logsumexp(logits[ids],dim=0)) for k,ids in groups.items()}
            rank=sorted(scores,key=lambda k:(-scores[k],k));winner=rank[0]
            rec=dict(arm=arm,id=r["id"],prompt_sha256=sha(q),raw4=short,raw32=long,ids=y,short=first(short),long=extract_long(long),constrained=winner,candidate_logits=raw_logits,letter_scores=scores,margin=scores[winner]-scores[rank[1]],input_tokens=n,output_tokens=len(y),gen_seconds=gen_seconds,forward_seconds=forward_seconds,saturated=len(y)==32)
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    scores={};hits={}
    for arm in ("A","B"):
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==32 and len({r["id"] for r in rr})==32
        by={r["id"]:r for r in rows}
        metrics={}
        for mode in ("short","long","constrained"):
            h={r["id"]:r[mode]==by[r["id"]]["gold"] for r in rr};hits[arm,mode]=h
            pairs=sum(all(h[r["id"]] for r in rows if r["pair"]==p) for p in {r["pair"] for r in rows})
            metrics[mode]=dict(correct=sum(h.values()),pairs=pairs,valid=sum(r[mode] is not None for r in rr),by_length={str(n):sum(h[r["id"]] for r in rows if r["n"]==n) for n in (5,7)},mastery=sum(h.values())>=28 and pairs>=12)
        scores[arm]=dict(modes=metrics,strict4=sum(r["raw4"]==by[r["id"]]["gold"] for r in rr),strict32=sum(r["raw32"]==by[r["id"]]["gold"] for r in rr),saturated=sum(r["saturated"] for r in rr),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),gen_seconds=sum(r["gen_seconds"] for r in rr),forward_seconds=sum(r["forward_seconds"] for r in rr))
    b=scores["B"]["modes"]
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,candidate_tokens=groups,arms=scores,format_gate=b["long"]["correct"]-b["short"]["correct"]>=8 and b["long"]["pairs"]-b["short"]["pairs"]>=4,discrimination_gate=b["constrained"]["mastery"],oracle_correct=32,oracle_pairs=16,constant_correct=4,constant_pairs=0)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("FORMAT_SKILL_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="formatskill");a=p.parse_args()
    if a.check:
        rows=preflight();print("ORACLE_CHECK",len(rows),sha(dump(rows)))
    else:run(a.output)
