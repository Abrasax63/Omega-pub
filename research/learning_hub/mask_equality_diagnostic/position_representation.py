import argparse,hashlib,itertools,json,random,re,time
from collections import Counter
from pathlib import Path
from followup import MODELS
VIEWS=("compact","spaced","indexed")
def dump(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
def encode(s,v):
    if v=="compact":return "".join(s)
    if v=="spaced":return " ".join(s)
    return " ".join(f"{i+1}:{a}" for i,a in enumerate(s))
def decode(s,v):
    if v=="compact":return list(s)
    if v=="spaced":return s.split()
    pairs=[x.split(":") for x in s.split()]
    assert [int(x[0]) for x in pairs]==list(range(1,len(pairs)+1))
    return [x[1] for x in pairs]
def corpus():
    rng=random.Random(202611250537);alpha=list("ABCDEFGH");seen=set();rows=[]
    for n in (6,8):
        a=rng.sample(alpha,8);b=rng.sample(alpha,8)
        while any(x==y for x,y in zip(a,b)):b=rng.sample(alpha,8)
        pp=list(range(n))*(16//n)+rng.sample(range(n),16%n)
        rng.shuffle(pp)
        while any(pp[i]==pp[i+8] for i in range(8)):rng.shuffle(pp)
        for i,(x,y) in enumerate(zip(a,b)):
            p,q=pp[i],pp[i+8]
            for attempt in range(1000):
                s=rng.sample([z for z in alpha if z not in (x,y)],n-2)
                s.insert(min(p,q),x if p<q else y)
                s.insert(max(p,q),y if p<q else x)
                if tuple(s) not in seen:break
            else:raise RuntimeError("duplicate list")
            seen.add(tuple(s))
            assert s[p]==x and s[q]==y
            for v in VIEWS:assert decode(encode(s,v),v)==s
            for pos,gold in ((p,x),(q,y)):
                assert s[pos]==gold==dict(enumerate(s,1))[pos+1]
                rows.append(dict(id=sha(dump([s,pos]))[:24],pair=f"{n}-{i}",n=n,seq=s,p=pos+1,gold=gold))
        assert Counter(r["gold"] for r in rows if r["n"]==n)==Counter(alpha*2)
    assert len(rows)==32 and len(seen)==16 and len({r["id"] for r in rows})==32
    rng.shuffle(rows);return rows
def question(r,v):
    return f'Read the sequence from left to right. Which letter is at position {r["p"]} (count from 1)? Output only the letter. Sequence: '+encode(r["seq"],v)
def first(raw):
    m=re.match(r"^\s*([A-H])\b",raw)
    return m.group(1) if m else None
def score(rows,records):
    by={r["id"]:r for r in rows};res={};hits={}
    for v in VIEWS:
        rr=[r for r in records if r["view"]==v]
        assert len(rr)==32 and {r["id"] for r in rr}==set(by)
        assert all(r["prompt_sha256"]==sha(question(by[r["id"]],v)) for r in rr)
        h={r["id"]:first(r["raw"])==by[r["id"]]["gold"] for r in rr};hits[v]=h
        pairs=sum(all(h[r["id"]] for r in rows if r["pair"]==p) for p in {r["pair"] for r in rows})
        res[v]=dict(primary=sum(h.values()),strict=sum(r["raw"]==by[r["id"]]["gold"] for r in rr),valid=sum(first(r["raw"]) is not None for r in rr),pairs=pairs,by_length={str(n):sum(h[r["id"]] for r in rows if r["n"]==n) for n in (6,8)},by_target=dict(Counter(r["gold"] for r in rows if h[r["id"]])),by_position=dict(Counter(str(r["p"]) for r in rows if h[r["id"]])),output_counts=dict(Counter(r["raw"] for r in rr)),input_tokens=sum(r["input_tokens"] for r in rr),encoded_tokens=sum(len(r["encoded_ids"]) for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr),gate=sum(h.values())>=28 and pairs>=12)
    return dict(views=res,paired_indexed_vs_spaced=dict(Counter("both" if hits["indexed"][i] and hits["spaced"][i] else "indexed_only" if hits["indexed"][i] else "spaced_only" if hits["spaced"][i] else "neither" for i in by)),gain_gate=res["indexed"]["primary"]-res["spaced"]["primary"]>=8 and res["indexed"]["pairs"]-res["spaced"]["pairs"]>=4)
def run(out):
    rows=corpus();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for v,r in itertools.product(VIEWS,rows):
            q=question(r,v);prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
            x=tok(prompt,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];assert n+4<=1024
            start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=4,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            rec=dict(id=r["id"],view=v,raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=sha(q),input_tokens=n,encoded_ids=tok.encode(encode(r["seq"],v),add_special_tokens=False),output_tokens=len(y),seconds=time.monotonic()-start)
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    result=score(rows,records);result.update(model=model_id,revision=rev,training=False,corpus_sha256=digest,constant_correct=4,constant_pairs=0,oracle_correct=32,oracle_pairs=16)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("POSITION_REP_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="positionrep");a=p.parse_args()
    if a.check:print("ORACLE_CHECK",len(corpus()),sha(dump(corpus())))
    else:run(a.output)
