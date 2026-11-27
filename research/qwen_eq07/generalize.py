"""EQ07: 3 matched curricula x 3 orders; held-out wording and operation retention.
Direct block 12 only. Public synthetic data; raw unconstrained inference.
"""
import argparse, collections, hashlib, json, math, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq02"))
from equality import MODEL,REVISION
ARMS=("A_two","B_four","C_replay")
SEEDS=(271128,271129,271130)
STEPS=16
TRAIN=(("12","13"),("25","35"),("34","33"),("46","64"),("58","59"),("67","76"),("79","78"),("81","91"))
EXAM=(("147","148"),("263","363"),("395","359"),("647","648"),("bek","bex"),("fom","fam"),("niz","nzi"),("suvu","suv"),("152","153"),("274","374"),("plim","plin"),("zoro","zor"))
def eq(a,b,t,rev,group,i):
    one,zero=("0","1") if rev else ("1","0")
    templates=[
      f'Are "{a}" and "{b}" identical strings? If identical answer {one}; otherwise answer {zero}.',
      f'Compare the text inside brackets: [{a}] versus [{b}]. Return {zero} for different texts and {one} for an exact match.',
      f'First item: {a}. Second item: {b}. Output {one} when the two items match character for character, or {zero} when they do not.',
      f'X = "{a}"; Y = "{b}". Use code {zero} for X and Y being unequal, code {one} for them being equal.',
      f'A clerk receives two labels, "{a}" and "{b}". Choose code {zero} if any character or length differs; choose code {one} if nothing differs.',
      f'Check whether copying the first sequence ({a}) would reproduce the second sequence ({b}) exactly. A successful copy is coded {one}, an unsuccessful copy {zero}.'
    ]
    suffix=" Reply with one digit only."
    return dict(id=f"{group}-{i}-{int(a==b)}-{int(rev)}",group=group,anchor=i,a=a,b=b,same=a==b,reverse=rev,template=t,target=one if a==b else zero,prompt=templates[t]+suffix)
def quartet(pair,t,group,i):
    a,b=pair
    return [eq(a,c,t,rev,group,i) for c in (b,a) for rev in (False,True)]
def operation(op,a,b,style):
    y={"and":a&b,"xor":a^b,"not":1-a}[op]
    x=f"{a}" if op=="not" else f"{a} and {b}"
    if style=="replay":
        q=f"Compute the bit result of {op.upper()} applied to {x}. Output the result."
    elif style=="old":
        q=f"Boolean {op.upper()} of {a}"+(f" and {b}?" if op!="not" else "?")
    elif style=="transfer":
        q={"and":f"Both switches are on exactly when both input bits {a}, {b} are 1. What is the resulting bit?",
           "xor":f"Return 1 if exactly one of the bits {a}, {b} is 1, otherwise 0.",
           "not":f"Flip bit {a}: what is its complement?"}[op]
    else:
        q={"and":f"Evaluate ({a} AND {b}).","xor":f"Evaluate ({a} XOR {b}).","not":f"Evaluate NOT({a})."}[op]
    return dict(id=f"{style}-{op}-{a}-{b}",op=op,target=str(y),prompt=q+" Reply with one digit only.")
def data(seed):
    schedule=[]
    rng=random.Random(seed)
    for _ in range(2):
        order=list(range(8));rng.shuffle(order);schedule.extend(order)
    train={}
    for arm in ARMS:
        train[arm]=[quartet(TRAIN[i],i%(2 if arm=="A_two" else 4),"train",i) for i in schedule]
    # Replace four equality batches, keeping total optimizer steps and presentations fixed.
    replay_pool=[operation(op,a,b,"replay") for op in ("and","xor","not") for a in (0,1) for b in ((0,) if op=="not" else (0,1))]
    neg=[r for r in replay_pool if r["target"]=="0"];pos=[r for r in replay_pool if r["target"]=="1"]
    for k,j in enumerate((3,7,11,15)):
        train["C_replay"][j]=[neg[(2*k+i)%len(neg)] for i in range(2)]+[pos[(2*k+i)%len(pos)] for i in range(2)]
    exam=[]
    for i,pair in enumerate(EXAM):
        for t in (4,5):exam.extend(quartet(pair,t,f"unseen_{t}",i))
    for i,pair in enumerate(EXAM[:8]):
        # Seen wording diagnostic, independent of the primary held-out wording metric.
        for t in (0,1,2,3):exam.extend(quartet(pair,t,f"diagnostic_{t}",i))
    retention=[operation(op,a,b,style) for style in ("old","transfer","notation") for op in ("and","xor","not") for a in (0,1) for b in ((0,) if op=="not" else (0,1))]
    assert len(exam)==224 and len({r["prompt"] for r in exam})==224
    assert len(retention)==30 and len({r["prompt"] for r in retention})==30
    assert not {x for p in TRAIN for x in p}&{x for p in EXAM for x in p}
    for arm,batches in train.items():
        assert len(batches)==16 and all(len(b)==4 and sum(r["target"]=="1" for r in b)==2 for b in batches)
        assert not {r["prompt"] for b in batches for r in b}&{r["prompt"] for r in exam+retention}
        assert sum("op" in b[0] for b in batches)==(4 if arm=="C_replay" else 0)
    return train,exam,retention,schedule
def score(rows):
    by=collections.defaultdict(list)
    for r in rows:by[(r["group"],r["anchor"])].append(r)
    assert all(len(s)==4 for s in by.values())
    return dict(n=len(rows),correct=sum(r["correct"] for r in rows),quartets=len(by),quartets_correct=sum(all(r["correct"] for r in s) for s in by.values()),invalid=sum(r["raw"].strip() not in ("0","1") for r in rows))
def fixture():
    for seed in SEEDS:
        train,exam,retention,schedule=data(seed)
        u=[r for r in exam if r["group"].startswith("unseen")]
        assert len(u)==96
        assert score([dict(r,raw="0",correct=r["target"]=="0") for r in u])["quartets_correct"]==0
        assert score([dict(r,raw=r["target"],correct=True) for r in u])["quartets_correct"]==24
    print("Fixture OK: 3 orders, 16 balanced batches each; 96 primary + 128 diagnostic prompts; 30 retention prompts")
def main():
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--seed",type=int,choices=SEEDS,default=SEEDS[0]);p.add_argument("--out",default="eq07-results")
    args=p.parse_args()
    if args.fixture:fixture();return
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from safetensors.torch import save_file,load_file
    train,exam,retention,schedule=data(args.seed)
    torch.manual_seed(args.seed);torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False,torch_dtype=torch.float32)
    model.config.use_cache=False
    for p0 in model.parameters():p0.requires_grad_(False)
    block=model.model.layers[11];base={k:v.detach().clone() for k,v in block.state_dict().items()}
    params=list(block.parameters())
    ids={s:tok(s,add_special_tokens=False).input_ids for s in ("0","1")}
    assert all(len(v)==1 for v in ids.values())
    z,o=ids["0"][0],ids["1"][0]
    def prompt(q):
        return tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,return_tensors="pt")[0]
    def emit(file,row):
        with (out/file).open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    manifest=dict(model=MODEL,revision=REVISION,seed=args.seed,torch=torch.__version__,block_index=11,
      train=train,exam=exam,retention=retention,schedule=schedule,steps=STEPS,lr=1e-5,lambda_rank=0.5,
      trainable=sum(x.numel() for x in params),criteria="each seed: unseen >=72/96, >=16/24 complete quartets, >=36/48 per unseen template, no loss of initial retention items; B vs A and C vs B descriptive paired differences",
      limitations="same pretrained initialization, 3 order seeds; 12 primary anchors reused across two templates; replay replaces 4 equality batches and uses same logical truth table as retention with new wording; no exact optimizer continuation; public synthetic block weights only; not causal abstraction")
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    def generate(r):
        inp=prompt(r["prompt"]).unsqueeze(0)
        with torch.no_grad():
            g=model.generate(inp,attention_mask=torch.ones_like(inp),do_sample=False,max_new_tokens=8,use_cache=True,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
        suffix=g.sequences[0,inp.shape[1]:];raw=tok.decode(suffix,skip_special_tokens=True)
        lp=g.scores[0][0].float().log_softmax(-1)
        return dict(r,raw=raw,token_ids=suffix.tolist(),first_logp={"0":float(lp[z]),"1":float(lp[o])},correct=raw.strip()==r["target"])
    def evaluate(arm,step,full):
        model.eval();rows=[]
        for r in exam:
            if not full and not r["group"].startswith("unseen"):continue
            v=generate(r);rows.append(v);emit("answers.jsonl",dict(v,arm=arm,step=step))
        rr=[]
        for r in retention:
            v=generate(r);rr.append(v);emit("retention.jsonl",dict(v,arm=arm,step=step))
        groups={g:score([r for r in rows if r["group"]==g]) for g in sorted({r["group"] for r in rows})}
        primary=score([r for r in rows if r["group"].startswith("unseen")])
        delta=math.sqrt(sum(float((v.detach()-base[k]).square().sum()) for k,v in block.state_dict().items()))
        info=dict(arm=arm,step=step,primary=primary,groups=groups,delta_l2=delta,retention_correct_ids=[r["id"] for r in rr if r["correct"]])
        emit("checkpoints.jsonl",info);print(json.dumps(info),flush=True)
    evaluate("base",0,True)
    for arm in ARMS:
        block.load_state_dict(base);assert all(torch.equal(v,base[k]) for k,v in block.state_dict().items())
        for x in params:x.requires_grad_(True)
        torch.manual_seed(args.seed)
        opt=torch.optim.AdamW(params,lr=1e-5,weight_decay=0)
        for step,rr in enumerate(train[arm],1):
            model.train();seq=[prompt(r["prompt"]) for r in rr];length=torch.tensor([len(s) for s in seq])
            batch=torch.nn.utils.rnn.pad_sequence(seq,batch_first=True,padding_value=tok.eos_token_id)
            mask=(torch.arange(batch.shape[1])[None,:]<length[:,None]).long()
            target=torch.tensor([ids[r["target"]][0] for r in rr])
            opt.zero_grad(set_to_none=True)
            logits=model(input_ids=batch,attention_mask=mask,use_cache=False).logits[torch.arange(4),length-1].float()
            ce=F.cross_entropy(logits,target)
            if "op" in rr[0]:rank=ce.new_zeros(())
            else:
                m=logits[:,o]-logits[:,z]
                rank=F.softplus(-torch.stack([m[2]-m[0],m[1]-m[3]])).mean()
            loss=ce+0.5*rank;assert torch.isfinite(loss)
            loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0);assert torch.isfinite(norm)
            opt.step();emit("train.jsonl",dict(arm=arm,step=step,replay="op" in rr[0],ids=[r["id"] for r in rr],loss=float(loss.detach()),ce=float(ce.detach()),rank=float(rank.detach()),grad_norm=float(norm)))
            if step in (8,16):evaluate(arm,step,step==16)
        # Reusable exact block weights; no optimizer state. No model promotion.
        path=out/f"{arm}-block12.safetensors"
        state={k:v.detach().cpu().contiguous() for k,v in block.state_dict().items()}
        save_file(state,str(path),metadata={"model":MODEL,"revision":REVISION,"block_index":"11","seed":str(args.seed),"arm":arm})
        check=load_file(str(path));assert all(torch.equal(v,check[k]) for k,v in state.items())
        emit("weights.jsonl",dict(arm=arm,path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    block.load_state_dict(base);assert all(torch.equal(v,base[k]) for k,v in block.state_dict().items())
    for x in params:x.requires_grad_(False)
    evaluate("restored_base",0,False)
if __name__=="__main__":main()
