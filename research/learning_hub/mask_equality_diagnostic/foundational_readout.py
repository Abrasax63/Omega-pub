import argparse, hashlib, itertools, json, random, re, time
from pathlib import Path
from collections import Counter
from followup import MODELS

LEVELS=("copy","position","equal")
def dump(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
def corpus():
    rng=random.Random(202611250533); alphabet=list("ABCDEFGH"); rows=[]; seen=set()
    def add(level,prompt,gold,pair=None):
        assert prompt not in seen;seen.add(prompt)
        rows.append(dict(level=level,prompt=prompt,gold=gold,pair=pair,id=sha(prompt)[:24]))
    for a in alphabet:
        add("copy",f"Copy the single letter {a}. Output only that letter.",a)
        add("copy",f"Input: [{a}]. Return its letter only.",a)
    targets=alphabet*2;rng.shuffle(targets)
    for i,a in enumerate(targets):
        p=i%4
        while True:
            seq=rng.sample([x for x in alphabet if x!=a],3);seq.insert(p,a)
            q=f"List: {' '.join(seq)}. Which letter is at position {p+1} (count from 1)? Output only the letter."
            if q not in seen:break
        assert seq[p]==a and len(set(seq))==4
        add("position",q,a)
    for i,a in enumerate(alphabet):
        b=rng.choice([x for x in alphabet if x!=a])
        for c in (a,b):
            add("equal",f"First letter: {a}. Second letter: {c}. Are the letters identical? Answer exactly Yes or No.","Yes" if a==c else "No",i)
    assert len(rows)==48 and len({r["id"] for r in rows})==48
    for level in ("copy","position"):assert Counter(r["gold"] for r in rows if r["level"]==level)==Counter(alphabet*2)
    assert all({r["gold"] for r in rows if r["pair"]==i}=={"Yes","No"} for i in range(8))
    rng.shuffle(rows);return rows
def score(rows,records):
    by={r["id"]:r for r in rows};res={}
    for model,level in itertools.product(MODELS,LEVELS):
        rr=[r for r in records if r["model"]==model and by[r["id"]]["level"]==level]
        assert len(rr)==16 and len({r["id"] for r in rr})==16
        strict={r["id"]:r["raw"]==by[r["id"]]["gold"] for r in rr}
        allowed={"Yes","No"} if level=="equal" else set("ABCDEFGH")
        def first(raw):
            m=re.match(r"^\s*([A-Za-z]+)\b",raw)
            return m.group(1) if m else None
        paired=sum(all(strict[r["id"]] for r in rows if r["pair"]==i) for i in range(8)) if level=="equal" else None
        res[model+"_"+level]=dict(strict=sum(strict.values()),stripped=sum(r["raw"].strip()==by[r["id"]]["gold"] for r in rr),prefix=sum(first(r["raw"])==by[r["id"]]["gold"] for r in rr),valid=sum(r["raw"] in allowed for r in rr),pairs=paired,output_counts=dict(Counter(r["raw"] for r in rr)),correct_by_target=dict(Counter(by[r["id"]]["gold"] for r in rr if strict[r["id"]])),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr),gate=sum(strict.values())>=14 and (paired is None or paired>=6))
    return res
def run(out):
    rows=corpus();digest=sha(dump(rows));print("CORPUS_FROZEN",digest,flush=True)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2);records=[];out=Path(out);out.mkdir(exist_ok=False)
    with (out/"predictions.jsonl").open("x") as log:
        for name,(model_id,rev) in MODELS.items():
            tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
            model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
            assert model.config._commit_hash==rev
            for r in rows:
                prompt=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
                x=tok(prompt,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];assert n+4<=1024
                start=time.monotonic()
                with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=4,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                rec=dict(model=name,revision=rev,id=r["id"],raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=sha(r["prompt"]),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start)
                records.append(rec);log.write(dump(rec)+"\n");log.flush()
            del model,tok
    result=dict(corpus_sha256=digest,models=MODELS,training=False,arms=score(rows,records))
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("FOUNDATIONAL_RESULT",dump(result),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="readout");a=p.parse_args()
    if a.check:print("ORACLE_CHECK",len(corpus()),sha(dump(corpus())))
    else:run(a.output)
