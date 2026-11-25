import argparse,itertools,json,random,time
from pathlib import Path
from atomic_composition import EXAMPLES,corpus as old_atomic
from self_representation02 import corpus as old_rep,grade,checks
from position_representation import dump,sha
from followup import MODELS
ORDERS=["".join(map(str,p)) for p in itertools.permutations((1,2,3))]+["1","2","3"]
def corpus():
    rng=random.Random(202611250552);seen={tuple(r["seq"]) for r in old_atomic()+old_rep()};rows=[]
    for n in (3,4):
        for _ in range(8):
            for attempt in range(1000):
                s=rng.sample(list("ABCDEFGH"),n)
                if tuple(s) not in seen:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s));rows.append(dict(id=sha(dump(s))[:24],seq=s,n=n))
    rng.shuffle(rows);assert len(rows)==16 and len({r["id"] for r in rows})==16
    return rows
def prompt(r,order):
    return "Number positions from left to right, starting at 1, not alphabet ranks. Write all pairs number:letter, separated by spaces. Return only the pairs.\nExamples:\n"+"\n".join(EXAMPLES[int(i)-1] for i in order)+"\nInput: "+" ".join(r["seq"])+"\nOutput:"
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
        for order,r in itertools.product(ORDERS,rows):
            q=prompt(r,order);x=tok(tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True),return_tensors="pt",add_special_tokens=False)
            n=x["input_ids"].shape[1];assert n+64<=1024
            start=time.monotonic()
            with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(arm=order,id=r["id"],n=r["n"],raw=raw,prompt_sha256=sha(q),input_tokens=n,output_tokens=len(y),saturated=len(y)==64,seconds=time.monotonic()-start,**grade(raw,r["seq"]))
            records.append(rec);log.write(dump(rec)+"\n");log.flush()
    scores={}
    for arm in ORDERS:
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==16 and len({r["id"] for r in rr})==16
        scores[arm]=dict(faithful=sum(r["faithful"] for r in rr),valid=sum(r["valid"] for r in rr),correct_couples=sum(r["correct_couples"] for r in rr),saturated=sum(r["saturated"] for r in rr),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    f={a:scores[a]["faithful"] for a in ORDERS}
    last={str(i):sum(f[a] for a in ORDERS if len(a)==3 and a[-1]==str(i))/2 for i in (1,2,3)}
    result=dict(model=model_id,revision=rev,training=False,corpus_sha256=digest,arms=scores,last_example_mean=last,reverse_replication=f["321"]>=12 and f["321"]-f["123"]>=4,recency_gate=last["1"]-last["3"]>=4,same_last_contrast=f["321"]-f["231"],single_simple_near_reverse=f["1"]>=f["321"]-1)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("EXAMPLE_ORDER_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="exampleorder");a=p.parse_args()
    if a.check:
        checks();rows=corpus();assert len(ORDERS)==9;print("ORACLE_CHECK",len(rows),sha(dump(rows)))
    else:run(a.output)
