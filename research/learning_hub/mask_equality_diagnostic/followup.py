import argparse, hashlib, itertools, json, random, re, time
from collections import Counter
from pathlib import Path
import diagnostic as old

MODELS={
"smol":("HuggingFaceTB/SmolLM2-135M-Instruct","ee72e5415c002e8fc0566a191a07c0b2b708875a"),
"qwen":("Qwen/Qwen2.5-0.5B-Instruct","7ae557604adf67be50417f59c2c2f167def9a775")}
VIEWS=("list","bits")
def dump(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
def render(u,a,b,v):
    if v=="list":return old.render(u,a,b,"list")
    return "A="+ "".join(str(int(x in a)) for x in u)+"; B="+ "".join(str(int(x in b)) for x in u)
def corpus():
    rng=random.Random(202611250531)
    old_lists={old.render(r["u"],r["a"],r["b"],"list") for r in old.data()}
    seen=set();rows=[]
    for i in range(12):
        for attempt in range(10000):
            u=rng.sample(list("ABCDEFGH"),8)
            a=rng.sample(u,3+i%2)
            b=rng.sample(a,len(a))
            if b==a:continue
            c=rng.sample(a[1:]+[rng.choice([x for x in u if x not in a])],len(a))
            pairs=[(a,b),(a,c)]
            keys=[(v,render(u,x,y,v)) for x,y in pairs for v in VIEWS]
            if len(set(keys))!=4 or any(k in seen for k in keys) or any(k[0]=="list" and k[1] in old_lists for k in keys):continue
            seen.update(keys)
            for x,y in pairs:
                gold=not bool(set(x)^set(y))
                assert gold==(set(x)==set(y))
                assert gold==("".join(str(int(z in x)) for z in u)=="".join(str(int(z in y)) for z in u))
                assert len(x)==len(y) and len(set(x)^set(y))==(0 if gold else 2)
                rows.append(dict(id=sha(dump([u,x,y]))[:24],pair=i,u=u,a=x,b=y,gold=gold))
            break
        else:raise RuntimeError("generator exhausted")
    rng.shuffle(rows)
    assert len(rows)==24 and len({r["id"] for r in rows})==24 and sum(r["gold"] for r in rows)==12
    for i in range(12):assert sorted(r["gold"] for r in rows if r["pair"]==i)==[False,True]
    return rows
def question(r,v):
    if v=="list":return "Lists describe sets; order does not matter. Do A and B contain exactly the same elements? Answer exactly Yes or No. "+render(r["u"],r["a"],r["b"],v)
    return "Are the two binary strings A and B exactly identical? Answer exactly Yes or No. "+render(r["u"],r["a"],r["b"],v)
def prefix(raw):
    m=re.match(r"^\s*(Yes|No)\b",raw,re.I)
    return m.group(1).lower() if m else None
def score(rows,records):
    by={r["id"]:r for r in rows};res={}
    for model,v in itertools.product(MODELS,VIEWS):
        rr=[r for r in records if r["model"]==model and r["view"]==v]
        assert len(rr)==24 and {r["id"] for r in rr}==set(by)
        assert all(r["prompt_sha256"]==sha(question(by[r["id"]],v)) for r in rr)
        gold=lambda r:"Yes" if by[r["id"]]["gold"] else "No"
        strict={r["id"]:r["raw"]==gold(r) for r in rr}
        relaxed={r["id"]:prefix(r["raw"])==gold(r).lower() for r in rr}
        def complete(h):return sum(all(h[r["id"]] for r in rows if r["pair"]==i) for i in range(12))
        res[model+"_"+v]=dict(strict=sum(strict.values()),prefix=sum(relaxed.values()),valid=sum(r["raw"] in ("Yes","No") for r in rr),strict_pairs=complete(strict),prefix_pairs=complete(relaxed),correct_positive=sum(strict[r["id"]] for r in rows if r["gold"]),correct_negative=sum(strict[r["id"]] for r in rows if not r["gold"]),output_counts=dict(Counter(r["raw"] for r in rr)),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    return {"arms":res,"paired_qwen_vs_smol":{v:dict(Counter(("both_correct" if s and q else "smol_only" if s else "qwen_only" if q else "neither") for s,q in ((next(x["raw"] for x in records if x["model"]=="smol" and x["view"]==v and x["id"]==r["id"])==("Yes" if r["gold"] else "No"),next(x["raw"] for x in records if x["model"]=="qwen" and x["view"]==v and x["id"]==r["id"])==("Yes" if r["gold"] else "No")) for r in rows))) for v in VIEWS},"primary_gate":{m:all(res[m+"_"+v]["strict"]>=18 and res[m+"_"+v]["strict_pairs"]>=8 for v in VIEWS) for m in MODELS}}
def run(out):
    rows=corpus();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2);records=[]
    out=Path(out);out.mkdir(exist_ok=False)
    with (out/"predictions.jsonl").open("x") as log:
        for name,(model_id,rev) in MODELS.items():
            tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
            model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
            assert model.config._commit_hash==rev
            for v,r in itertools.product(VIEWS,rows):
                q=question(r,v)
                prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
                x=tok(prompt,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];assert n+8<=1024
                start=time.monotonic()
                with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=8,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                record=dict(model=name,revision=rev,id=r["id"],view=v,raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start)
                records.append(record);log.write(dump(record)+"\n");log.flush()
            del model,tok
    result=score(rows,records);result.update(corpus_sha256=digest,models=MODELS,training=False,constant_correct=12,constant_pairs=0,oracle_correct=24)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print("DIAG02_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="diag02");a=p.parse_args()
    if a.check:print("ORACLE_CHECK",len(corpus()),sha(dump(corpus())))
    else:run(a.output)
