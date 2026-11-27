"""EQ02: single-model, direct-weight equality pilot, paired label reversals.
No correction, constrained decoding, tools, peer input, or training on exam.
"""
import argparse, hashlib, json, math, random
from pathlib import Path

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REVISION="7ae557604adf67be50417f59c2c2f167def9a775"
SEED=271127
def make(a,b,group,anchor,reverse):
    same=a==b
    one,zero=("0","1") if reverse else ("1","0")
    if group in ("train","novel_values"):
        q=f'Are "{a}" and "{b}" identical strings? If identical answer {one}; otherwise answer {zero}.'
    elif group=="paraphrase":
        q=f'Compare the text inside brackets: [{a}] versus [{b}]. Return {zero} for different texts and {one} for an exact match.'
    else:
        q=f'Two labels are <{a}> and <{b}>. If their characters match exactly write {one}, else write {zero}.'
    return dict(id=f"{group}-{anchor}-{int(same)}-{int(reverse)}",group=group,anchor=anchor,a=a,b=b,same=same,reverse=reverse,
                target=one if same else zero,prompt=q+" Reply with one digit only.")
def make_group(group,pairs):
    return [make(a,b,group,i,rev) for i,(a,other) in enumerate(pairs) for b in (a,other) for rev in (False,True)]
def dataset():
    train=make_group("train",[("12","13"),("25","35"),("34","33"),("46","64"),
                              ("58","59"),("67","76"),("79","78"),("81","91")])
    exam=make_group("novel_values",[("14","15"),("26","36"),("42","24"),("57","56")])+make_group("paraphrase",[("18","19"),("29","39"),("43","44"),("62","61")])+make_group("symbol_transfer",[("kav","kax"),("mep","mop"),("tuz","tzu"),("rino","rinoo")])
    for s in (train,exam):
        assert len({r["id"] for r in s})==len(s)==len({r["prompt"] for r in s})
    assert not ({v for r in train for v in (r["a"],r["b"])} & {v for r in exam for v in (r["a"],r["b"])})
    assert not ({r["prompt"] for r in train}&{r["prompt"] for r in exam})
    rng=random.Random(SEED)
    for i in range(0,len(train),8):
        chunk=train[i:i+8];rng.shuffle(chunk);train[i:i+8]=chunk
        assert sum(r["same"] for r in chunk)==sum(r["reverse"] for r in chunk)==sum(r["target"]=="1" for r in chunk)==4
    for g in ("novel_values","paraphrase","symbol_transfer"):
        s=[r for r in exam if r["group"]==g]
        assert len(s)==16 and sum(r["target"]=="1" for r in s)==8
    return train,exam
def score(rows):
    groups={}
    for group in ("all","novel_values","paraphrase","symbol_transfer"):
        rr=[r for r in rows if group=="all" or r["group"]==group]
        by={}
        for r in rr: by.setdefault((r["group"],r["anchor"]),[]).append(r)
        assert all(len(s)==4 for s in by.values())
        groups[group]={"n":len(rr),"correct":sum(r["correct"] for r in rr),
          "output_0":sum(r["raw"].strip()=="0" for r in rr),
          "output_1":sum(r["raw"].strip()=="1" for r in rr),
          "invalid":sum(r["raw"].strip() not in ("0","1") for r in rr),
          "same_correct":sum(r["same"] and r["correct"] for r in rr),
          "different_correct":sum(not r["same"] and r["correct"] for r in rr),
          "quartets_all_correct":sum(all(r["correct"] for r in s) for s in by.values()),"quartets":len(by),
          "convention_pairs_both_correct":sum(all(r["correct"] for r in s if r["same"]==eq) for s in by.values() for eq in (False,True)),
          "convention_pairs":2*len(by)}
    return groups
def main():
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--out",default="eq02-results")
    args=p.parse_args();train,exam=dataset()
    if args.fixture:
        perfect=[dict(r,raw=r["target"],correct=True) for r in exam]
        constant=[dict(r,raw="0",correct=r["target"]=="0") for r in exam]
        assert score(perfect)["all"]["quartets_all_correct"]==12
        assert score(constant)["all"]["correct"]==24 and score(constant)["all"]["quartets_all_correct"]==0
        print("Fixture OK: 32 unique train prompts, 48 unique exam prompts, 12 paired quartets")
        return
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.manual_seed(SEED);torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False,torch_dtype=torch.float32)
    model.config.use_cache=False
    for p0 in model.parameters():p0.requires_grad_(False)
    block=model.model.layers[-1]
    for p0 in block.parameters():p0.requires_grad_(True)
    params=list(block.parameters());base=[p0.detach().clone() for p0 in params]
    opt=torch.optim.AdamW(params,lr=1e-5,weight_decay=0)
    label_ids={s:tok(s,add_special_tokens=False).input_ids for s in ("0","1")}
    assert all(len(v)==1 for v in label_ids.values())
    manifest={"model":MODEL,"revision":REVISION,"seed":SEED,"torch":torch.__version__,"train":train,"exam":exam,
              "trainable":sum(p0.numel() for p0 in params),"total":sum(p0.numel() for p0 in model.parameters()),
              "checkpoints":[0,8,16,24,32],"lr":1e-5,"scope":"direct last transformer block only",
              "limitations":"one seed; paired prompts not independent; transfer confounds format and representation; no saved weights; no evidence of internal causal abstraction"}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    def emit(file,row):
        with (out/file).open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    def prompt(q):
        return tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,return_tensors="pt")
    def evaluate(step):
        model.eval();rows=[]
        for r in exam:
            ids=prompt(r["prompt"])
            with torch.no_grad():
                g=model.generate(ids,attention_mask=torch.ones_like(ids),do_sample=False,max_new_tokens=8,use_cache=True,
                    pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
            suffix=g.sequences[0,ids.shape[1]:]
            raw=tok.decode(suffix,skip_special_tokens=True)
            logp=g.scores[0][0].float().log_softmax(-1)
            lp={s:float(logp[v[0]]) for s,v in label_ids.items()}
            row=dict(r,step=step,raw=raw,token_ids=suffix.tolist(),first_logp=lp,
                target_margin=lp[r["target"]]-lp[str(1-int(r["target"]))],correct=raw.strip()==r["target"])
            rows.append(row);emit("answers.jsonl",row)
        summary=score(rows)
        delta=math.sqrt(sum(float((p0.detach()-b).square().sum()) for p0,b in zip(params,base)))
        assert step==0 or delta>0
        info={"step":step,"delta_l2":delta,"metrics":summary}
        emit("checkpoints.jsonl",info);print(json.dumps(info),flush=True)
    evaluate(0)
    for i,r in enumerate(train,1):
        model.train()
        prefix=prompt(r["prompt"])
        target=tok(r["target"],add_special_tokens=False,return_tensors="pt").input_ids
        ids=torch.cat((prefix,target,torch.tensor([[tok.eos_token_id]])),dim=1)
        labels=ids.clone();labels[:,:prefix.shape[1]]=-100
        opt.zero_grad(set_to_none=True)
        loss=model(input_ids=ids,labels=labels,use_cache=False).loss
        assert torch.isfinite(loss)
        loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0);assert torch.isfinite(norm)
        opt.step()
        emit("train.jsonl",{"step":i,"id":r["id"],"loss":float(loss),"grad_norm":float(norm)})
        if i%8==0:evaluate(i)
if __name__=="__main__":main()
