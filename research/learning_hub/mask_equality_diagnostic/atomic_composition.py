import argparse,json,random,re,time,itertools
from pathlib import Path
from self_representation02 import corpus as previous,grade,checks
from position_representation import dump,sha
from followup import MODELS
EXAMPLES=["J -> 1:J","M L -> 1:M 2:L","P K N -> 1:P 2:K 3:N"]
def corpus():
    rng=random.Random(202611250548);seen={tuple(r["seq"]) for r in previous()};rows=[]
    for n in (3,4):
        for i in range(8):
            for attempt in range(1000):
                s=rng.sample(list("ABCDEFGH"),n)
                if tuple(s) not in seen:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s));p=i%n+1
            rows.append(dict(id=sha(dump(s))[:24],seq=s,n=n,p=p))
    rng.shuffle(rows);assert len(rows)==16 and len({r["id"] for r in rows})==16
    return rows
def prompt(r,arm):
    s=" ".join(r["seq"])
    if arm=="atomic":return f"Position means place from left to right, starting at 1. Input: {s}. Write only the pair for position {r['p']}, using number:letter. Output:"
    base="Number positions from left to right, starting at 1, not alphabet ranks. Write all pairs number:letter, separated by spaces. Return only the pairs."
    examples=[] if arm=="D" else EXAMPLES if arm=="P" else EXAMPLES[::-1]
    return base+("\nExamples:\n"+"\n".join(examples) if examples else "")+"\nInput: "+s+"\nOutput:"
def evaluate(raw,r,arm):
    if arm=="atomic":
        expected=f"{r['p']}:{r['seq'][r['p']-1]}"
        valid=bool(re.fullmatch(r"[1-9]:[A-H]",raw.strip()))
        hit=raw.strip()==expected
        return dict(valid=valid,faithful=hit,correct_couples=int(hit))
    return grade(raw,r["seq"])
def run(out):
    rows=corpus();checks();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    model_id,rev=MODELS["qwen"];torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    assert model.config._commit_hash==rev
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm,r in itertools.product(("atomic","D","P","R"),rows):
            q=prompt(r,arm);limit=16 if arm=="atomic" else 64
            x=tok(tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True),return_tensors="pt",add_special_tokens=False)
            n=x["input_ids"].shape[1];start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=limit,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(arm=arm,id=r["id"],n=r["n"],raw=raw,prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),saturated=len(y)==limit,seconds=time.monotonic()-start,**evaluate(raw,r,arm))
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    scores={}
    for arm in ("atomic","D","P","R"):
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==16 and len({r["id"] for r in rr})==16
        scores[arm]=dict(faithful=sum(r["faithful"] for r in rr),valid=sum(r["valid"] for r in rr),correct_couples=sum(r["correct_couples"] for r in rr),saturated=sum(r["saturated"] for r in rr),by_length={str(n):sum(r["faithful"] for r in rr if r["n"]==n) for n in (3,4)},input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    p,d,r=(scores[x]["faithful"] for x in ("P","D","R"))
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,arms=scores,atomic_gate=scores["atomic"]["faithful"]>=14,progression_gate=p>=12 and p-d>=6 and p-r>=3)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("ATOMIC_COMP_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="atomiccomp");a=p.parse_args()
    if a.check:
        checks();rows=corpus();assert evaluate("2:B",dict(p=2,seq=list("AB")),"atomic")["faithful"];print("ORACLE_CHECK",len(rows),sha(dump(rows)))
    else:run(a.output)
