import argparse,itertools,json,random,time
from pathlib import Path
from collections import Counter
from self_representation import parse,reconstruct_prompt
from position_representation import dump,sha
from followup import MODELS
def corpus():
    rng=random.Random(202611250545); rows=[]; seen=set()
    for n in (3,4):
        for i in range(8):
            for attempt in range(1000):
                s=rng.sample(list("ABCDEFGH"),n)
                if tuple(s) not in seen:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s));rows.append(dict(id=sha(dump(s))[:24],seq=s,n=n))
    rng.shuffle(rows)
    assert len(rows)==16 and len({r["id"] for r in rows})==16
    return rows
def prompt(s,arm):
    if arm=="A":return reconstruct_prompt(s)
    return "Number the positions, not the alphabet. Example: L J K -> 1:L 2:J 3:K. Return one line only, no explanation. Input: "+" ".join(s)+"\nOutput:"
def grade(raw,s):
    d=parse(raw,len(s))
    correct=sum(x==y for x,y in zip(d,s)) if d is not None else 0
    faithful=d==s
    assert faithful==(d is not None and correct==len(s))
    return dict(valid=d is not None,faithful=faithful,correct_couples=correct)
def checks():
    assert grade("1:B 2:A 3:C",list("ABC"))==dict(valid=True,faithful=False,correct_couples=1)
    assert grade("1:A 2:B 3:C",list("ABC"))["faithful"]
    assert not grade("1:A 2:B",list("ABC"))["valid"]
    assert not grade("1:A 1:B 3:C",list("ABC"))["valid"]
def run(out):
    checks();rows=corpus();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm,r in itertools.product(("A","B"),rows):
            q=prompt(r["seq"],arm)
            p=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
            x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(arm=arm,id=r["id"],n=r["n"],raw=raw,prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),saturated=len(y)==64,seconds=time.monotonic()-start,**grade(raw,r["seq"]))
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    scores={};hits={}
    for arm in ("A","B"):
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==16 and len({r["id"] for r in rr})==16
        hits[arm]={r["id"]:r["faithful"] for r in rr}
        scores[arm]=dict(valid=sum(r["valid"] for r in rr),faithful=sum(r["faithful"] for r in rr),correct_couples=sum(r["correct_couples"] for r in rr),total_couples=56,saturated=sum(r["saturated"] for r in rr),by_length={str(n):sum(r["faithful"] for r in rr if r["n"]==n) for n in (3,4)},input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    paired=dict(Counter("both" if hits["A"][i] and hits["B"][i] else "A_only" if hits["A"][i] else "B_only" if hits["B"][i] else "neither" for i in hits["A"]))
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,arms=scores,paired=paired,gate=scores["B"]["faithful"]>=12 and scores["B"]["faithful"]-scores["A"]["faithful"]>=6)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("SELF_REP02_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="selfrep02");a=p.parse_args()
    if a.check:checks();print("ORACLE_CHECK",len(corpus()),sha(dump(corpus())))
    else:run(a.output)
