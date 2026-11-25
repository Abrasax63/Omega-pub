import argparse, hashlib, itertools, json, random, time
from collections import Counter
from pathlib import Path

MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
SEED=202611250523
VIEWS=("list","mask")
ARMS=("D","P")
def sha(x): return hashlib.sha256(x.encode()).hexdigest()
def data():
    rng=random.Random(SEED)
    alphabet=list("ABCDEFGH")
    rows=[]; seen=set()
    for i in range(12):
        for attempt in range(1000):
            u=rng.sample(alphabet,8)
            a=rng.sample(u,3+i%2)
            pos=rng.sample(a,len(a))
            if pos==a: continue
            neg=rng.sample([x for x in a if x!=a[0]]+[rng.choice([x for x in u if x not in a])],len(a))
            pairs=[(a,pos),(a,neg)]
            if len(set(neg))!=len(a): continue
            keys=[(v,render(u,x,y,v)) for x,y in pairs for v in VIEWS]
            if len(set(keys))!=4 or any(k in seen for k in keys): continue
            seen.update(keys)
            for a,b in pairs:
                gold=set(a)==set(b)
                assert gold==(len(set(a)^set(b))==0)
                rows.append(dict(id=sha(json.dumps([u,a,b]))[:24],pair=i,u=u,a=a,b=b,gold=gold))
            break
        else: raise RuntimeError("generator exhausted")
    rng.shuffle(rows)
    assert len(rows)==24 and len({r["id"] for r in rows})==24
    assert sum(r["gold"] for r in rows)==12
    for i in range(12):
        p=[r for r in rows if r["pair"]==i]
        assert len(p)==2 and {r["gold"] for r in p}=={True,False}
        assert all(len(r["a"])==len(r["b"]) for r in p)
        assert all(len(set(r["a"])^set(r["b"]))==(0 if r["gold"] else 2) for r in p)
    return rows
def render(u,a,b,view):
    if view=="list":
        return json.dumps({"A":a,"B":b},separators=(",",":"))
    return json.dumps({"order":u,"A":[int(x in a) for x in u],"B":[int(x in b) for x in u]},separators=(",",":"))
def question(r,view,arm):
    v="Lists describe sets; order does not matter." if view=="list" else "The vectors are membership masks over the same ordered universe."
    h=" Compare membership of each element in A and B." if arm=="P" else ""
    return v+" Do A and B contain exactly the same elements?"+h+" Answer exactly Yes or No. "+render(r["u"],r["a"],r["b"],view)
def run(out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    rows=data()
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==REV
    ids={k:tok.encode(k,add_special_tokens=False) for k in ("Yes","No")}
    assert all(len(x)==1 for x in ids.values())
    result={"model":MODEL,"revision":REV,"corpus_sha256":sha(json.dumps(rows,sort_keys=True)),"n":24,"pairs":12,"constant_correct":12,"constant_pairs":0,"oracle_correct":24,"training":False,"arms":{}}
    for view,arm in itertools.product(VIEWS,ARMS):
        predictions={}
        total_in=total_out=0; seconds=0.
        for r in rows:
            q=question(r,view,arm)
            prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
            x=tok(prompt,return_tensors="pt",add_special_tokens=False)
            n=x["input_ids"].shape[1]; assert n+8<=1024
            start=time.monotonic()
            with torch.inference_mode():
                logits=model(**x).logits[0,-1].float()
                b=float(logits[ids["Yes"][0]])>float(logits[ids["No"][0]])
                y=model.generate(**x,do_sample=False,max_new_tokens=8,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            seconds+=time.monotonic()-start
            total_in+=n; total_out+=len(y)
            raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            predictions[r["id"]]=(raw,b)
        strict={r["id"]:predictions[r["id"]][0]==("Yes" if r["gold"] else "No") for r in rows}
        binary={r["id"]:predictions[r["id"]][1]==r["gold"] for r in rows}
        def complete(h):return sum(all(h[r["id"]] for r in rows if r["pair"]==i) for i in range(12))
        result["arms"][view+"_"+arm]=dict(strict=sum(strict.values()),valid=sum(raw in ("Yes","No") for raw,_ in predictions.values()),binary=sum(binary.values()),strict_pairs=complete(strict),binary_pairs=complete(binary),correct_positive=sum(strict[r["id"]] for r in rows if r["gold"]),correct_negative=sum(strict[r["id"]] for r in rows if not r["gold"]),input_tokens=total_in,output_tokens=total_out,seconds=seconds)
        print(view,arm,json.dumps(result["arms"][view+"_"+arm]),flush=True)
    result["direct_gate"]=all(result["arms"][v+"_D"]["strict"]>=18 and result["arms"][v+"_D"]["strict_pairs"]>=8 for v in VIEWS)
    result["aid_gate"]=all(result["arms"][v+"_P"]["strict"]-result["arms"][v+"_D"]["strict"]>=3 and result["arms"][v+"_P"]["strict_pairs"]-result["arms"][v+"_D"]["strict_pairs"]>=2 for v in VIEWS)
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="mask_result.json");a=p.parse_args()
    if a.check:
        rows=data();print("ORACLE_CHECK",len(rows),sum(r["gold"] for r in rows),sha(json.dumps(rows,sort_keys=True)))
    else:run(a.output)
