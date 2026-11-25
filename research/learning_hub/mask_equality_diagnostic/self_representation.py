import argparse,itertools,json,random,re,time
from pathlib import Path
from collections import Counter
from position_representation import dump,sha,first,encode
from followup import MODELS

def corpus():
    rng=random.Random(202611250542); alpha=list("ABCDEFGH"); rows=[]; seen=set()
    for n in (5,7):
        a=rng.sample(alpha,8); b=rng.sample(alpha,8)
        while any(x==y for x,y in zip(a,b)): b=rng.sample(alpha,8)
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
            for pos,gold in ((p,x),(q,y)):
                assert s[pos]==gold==dict(enumerate(s,1))[pos+1]
                rows.append(dict(id=sha(dump([s,pos]))[:24],pair=f"{n}-{i}",n=n,seq=s,p=pos+1,gold=gold))
        assert Counter(r["gold"] for r in rows if r["n"]==n)==Counter(alpha*2)
    assert len(rows)==32 and len(seen)==16 and len({r["id"] for r in rows})==32
    rng.shuffle(rows);return rows
def parse(raw,n):
    parts=raw.strip().split()
    if len(parts)!=n:return None
    matches=[re.fullmatch(r"([1-9]):([A-H])",p) for p in parts]
    if not all(matches):return None
    if [int(m[1]) for m in matches]!=list(range(1,n+1)):return None
    return [m[2] for m in matches]
def reconstruct_prompt(seq):
    return "Number every letter from left to right, starting at 1. Example: J K L becomes 1:J 2:K 3:L. Return only the numbered letters, separated by spaces. Sequence: "+" ".join(seq)
def read_prompt(r,encoded):
    return f'Read the sequence from left to right. Which letter is at position {r["p"]} (count from 1)? Output only the letter. Sequence: '+encoded
def run(out):
    rows=corpus();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    assert parse(" 1:A 2:B ",2)==["A","B"] and parse("1:A 3:B",2) is None and parse("1:A 2:B extra",2) is None
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False)
    def infer(q,limit):
        prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
        x=tok(prompt,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];assert n+limit<=1024
        start=time.monotonic()
        with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=limit,pad_token_id=tok.eos_token_id)[0,n:].tolist()
        return dict(raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start)
    reps={};records=[]
    with (out/"predictions.jsonl").open("x") as log:
        def save(r):log.write(dump(r)+"\n");log.flush()
        for pair in sorted({r["pair"] for r in rows}):
            seq=next(r["seq"] for r in rows if r["pair"]==pair)
            rec=infer(reconstruct_prompt(seq),64);decoded=parse(rec["raw"],len(seq))
            rec.update(stage="reconstruct",pair=pair,valid=decoded is not None,faithful=decoded==seq,correct_couples=sum(x==y for x,y in zip(decoded,seq)) if decoded is not None else 0,n=len(seq))
            reps[pair]=rec;save(rec)
        for arm,r in itertools.product(("D","O","S"),rows):
            if arm=="D":encoded=encode(r["seq"],"spaced")
            elif arm=="O":encoded=encode(r["seq"],"indexed")
            elif reps[r["pair"]]["valid"]:encoded=reps[r["pair"]]["raw"]
            else:encoded=None
            rec=infer(read_prompt(r,encoded),4) if encoded is not None else dict(raw=None,prompt_sha256=None,input_tokens=0,output_tokens=0,seconds=0)
            rec.update(stage="read",arm=arm,id=r["id"],abstain=encoded is None)
            records.append(rec);save(rec)
    def costs(rr):return dict(input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr),calls=sum(r["raw"] is not None for r in rr))
    by={r["id"]:r for r in rows};scores={}
    rep_cost=costs(list(reps.values()))
    for arm in ("D","O","S"):
        rr=[r for r in records if r["arm"]==arm]
        assert len(rr)==32 and {r["id"] for r in rr}==set(by)
        h={r["id"]:r["raw"] is not None and first(r["raw"])==by[r["id"]]["gold"] for r in rr}
        pairs=sum(all(h[r["id"]] for r in rows if r["pair"]==p) for p in reps)
        c=costs(rr)
        scores[arm]=dict(primary=sum(h.values()),strict=sum(r["raw"]==by[r["id"]]["gold"] for r in rr),pairs=pairs,abstentions=sum(r["abstain"] for r in rr),by_length={str(n):sum(h[r["id"]] for r in rows if r["n"]==n) for n in (5,7)},read_cost=c,total_cost={k:c[k]+(rep_cost[k] if arm=="S" else 0) for k in c},gate=sum(h.values())>=28 and pairs>=12)
    fidelity=sum(r["faithful"] for r in reps.values())
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,arms=scores,reconstruction=dict(valid=sum(r["valid"] for r in reps.values()),faithful=fidelity,correct_couples=sum(r["correct_couples"] for r in reps.values()),total_couples=sum(r["n"] for r in reps.values()),cost=rep_cost),self_gate=fidelity>=12 and scores["S"]["primary"]-scores["D"]["primary"]>=8 and scores["S"]["pairs"]-scores["D"]["pairs"]>=4 and scores["S"]["primary"]>=scores["O"]["primary"]-4,constant_correct=4,constant_pairs=0,oracle_correct=32,oracle_pairs=16)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("SELF_REP_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="selfrep");a=p.parse_args()
    if a.check:
        assert parse("1:A 2:B",2)==["A","B"] and parse("1:A 1:B",2) is None and parse("1:A 2:J",2) is None
        print("ORACLE_CHECK",len(corpus()),sha(dump(corpus())))
    else:run(a.output)
