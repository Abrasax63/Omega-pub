"""EQ06 2x2 curriculum factorial, fixed block 12, matched presentations."""
import argparse, collections, json, math, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq02"))
from equality import MODEL,REVISION,dataset,make_group,make
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq03"))
from compare import data as previous_data
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq04"))
from depth import data as eq04_data
SEED=271128
ARMS=("A_numeric_single","B_numeric_varied","C_mixed_single","D_mixed_varied")
LAYERS=(11,11,11,11)
GROUPS=("num_standard","num_alt","num_unseen","symbol_standard","symbol_alt","symbol_unseen")
STEPS=16
LAMBDA=0.5
def data():
    original,old=dataset()
    numeric=[("12","13"),("25","35"),("34","33"),("46","64"),("58","59"),("67","76"),("79","78"),("81","91")]
    mixed=numeric[:4]+[("hx","hy"),("qr","rq"),("ds","dr"),("ut","vt")]
    train_by={}
    for arm in ARMS:
        pairs=mixed if arm.startswith(("C","D")) else numeric
        varied=arm.startswith(("B","D"))
        blocks=[]
        for i,(a,other) in enumerate(pairs):
            style="paraphrase" if varied and i%2 else "train"
            block=[dict(make(a,b,style,i,rev),group="train",id=f"train-{i}-{int(a==b)}-{int(rev)}",template=style)
                   for b in (other,a) for rev in (False,True)]
            assert [r["target"] for r in block]==["0","1","1","0"]
            blocks.append(block)
        train_by[arm]=blocks
    exam=[]
    for typ,pairs in (("num",[("136","137"),("248","348"),("571","517"),("906","907")]),
                      ("symbol",[("tib","tiv"),("lum","rum"),("dax","dxa"),("pofi","pof")])):
        for name,style in (("standard","novel_values"),("alt","paraphrase"),("unseen","symbol_transfer")):
            group=typ+"_"+name
            for i,(a,other) in enumerate(pairs):
                for b in (other,a):
                    for rev in (False,True):
                        r=make(a,b,style,i,rev)
                        exam.append(dict(r,group=group,id=f"{group}-{i}-{int(a==b)}-{int(rev)}",template=style))
    vals=lambda rr:{v for r in rr for v in (r["a"],r["b"])}
    alltrain=[r for blocks in train_by.values() for b in blocks for r in b]
    assert not vals(exam)&vals(alltrain+old+previous_data()[1]+eq04_data()[1])
    assert len({r["prompt"] for r in exam})==len(exam)==96
    for blocks in train_by.values():
        assert len({r["prompt"] for b in blocks for r in b})==32
        assert not {r["prompt"] for b in blocks for r in b}&{r["prompt"] for r in exam}
    assert [r["prompt"] for b in train_by[ARMS[0]] for r in b]==[r["prompt"] for r in sorted(original,key=lambda r:(r["anchor"],r["same"],r["reverse"]))]
    schedule=[]
    rng=random.Random(SEED)
    for epoch in range(2):
        order=list(range(8));rng.shuffle(order);schedule.extend(order)
    assert len(schedule)==STEPS
    return train_by,exam,schedule

def score(rows):
    groups={}
    for group in ("all",)+GROUPS:
        rr=[r for r in rows if group=="all" or r["group"]==group]
        by=collections.defaultdict(list)
        for r in rr:by[(r["group"],r["anchor"])].append(r)
        assert all(len(s)==4 for s in by.values())
        groups[group]={"n":len(rr),"correct":sum(r["correct"] for r in rr),
          "output_0":sum(r["raw"].strip()=="0" for r in rr),
          "output_1":sum(r["raw"].strip()=="1" for r in rr),
          "invalid":sum(r["raw"].strip() not in ("0","1") for r in rr),
          "quartets_all_correct":sum(all(r["correct"] for r in s) for s in by.values()),"quartets":len(by),
          "convention_pairs_both_correct":sum(all(r["correct"] for r in s if r["same"]==eq) for s in by.values() for eq in (False,True)),
          "convention_pairs":2*len(by)}
    return groups
def contrasts(m):
    # m = logit(1)-logit(0), ordered [different normal, different reversed, same normal, same reversed].
    rel=[m[2]-m[0],m[1]-m[3]]
    conv=[m[1]-m[0],m[2]-m[3]]
    return rel,conv

def fixture():
    blocks,exam,schedule=data()
    assert contrasts([-1,1,1,-1])==([2,2],[2,2])
    assert contrasts([3,3,3,3])==([0,0],[0,0])
    assert contrasts([1,-1,-1,1])==([-2,-2],[-2,-2])
    assert score([dict(r,raw="0",correct=r["target"]=="0") for r in exam])["all"]["quartets_all_correct"]==0
    assert score([dict(r,raw=r["target"],correct=True) for r in exam])["all"]["quartets_all_correct"]==24
    print("Fixture OK: same 64 presentations per arm; 96 new evaluation prompts; contrast signs checked")
def main():
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--out",default="eq06-results")
    args=p.parse_args()
    if args.fixture: fixture();return
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM,AutoTokenizer
    blocks,exam,schedule=data()
    torch.manual_seed(SEED);torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False,torch_dtype=torch.float32)
    model.config.use_cache=False
    for x in model.parameters():x.requires_grad_(False)
    assert len(model.model.layers)==24
    counts=[sum(x.numel() for x in model.model.layers[i].parameters()) for i in LAYERS]
    assert len(set(counts))==1
    block=None;base=None
    retention=[dict(id=f"retain-{op}-{a}-{b}",prompt=q+" Reply with one digit only.",target=str(y)) for op in ("and","xor","not") for a in (0,1) for b in ((0,) if op=="not" else (0,1)) for q,y in [(f"Boolean {op.upper()} of {a}"+(f" and {b}?" if op!="not" else "?"), {"and":a&b,"xor":a^b,"not":1-a}[op])]]
    ids={s:tok(s,add_special_tokens=False).input_ids for s in ("0","1")}
    assert all(len(v)==1 for v in ids.values())
    z,o=ids["0"][0],ids["1"][0]
    def prompt(q):
        return tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,return_tensors="pt")[0]
    def emit(file,row):
        with (out/file).open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    manifest={"model":MODEL,"revision":REVISION,"seed":SEED,"torch":torch.__version__,"arms":ARMS,"train_blocks":blocks,"exam":exam,
        "schedule":schedule,"steps_per_arm":STEPS,"presentations_per_arm":STEPS*4,"lr":1e-5,"lambda":LAMBDA,
        "trainable":counts[0],"layer_indices":LAYERS,"retention":retention,"total":sum(x.numel() for x in model.parameters()),
        "objectives":"All use EQ03 B: CE plus mean softplus(-rel), lambda 0.5.",
        "scope":"fixed block 12, direct weights, one seed, no EOS training; four matched curricula, two factors",
        "criteria":"pilot: >=72/96 exact, >=16/24 quartets, >=12/16 per group, no loss of initially correct retention answers; report B-A, C-A, D-B-C+A at step 16, no promotion without replication.",
        "limitations":"No checkpoints saved; tiny retention screen; same exam anchors reused across templates, only eight independent anchors; curriculum factors change tokenization and training examples, not just abstract representation; matched presentations not FLOPs."}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    def eval_(arm,step):
        model.eval();rows=[]
        for r in exam:
            inp=prompt(r["prompt"]).unsqueeze(0)
            with torch.no_grad():
                g=model.generate(inp,attention_mask=torch.ones_like(inp),do_sample=False,max_new_tokens=8,use_cache=True,
                    pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
            suffix=g.sequences[0,inp.shape[1]:]
            raw=tok.decode(suffix,skip_special_tokens=True)
            lp=g.scores[0][0].float().log_softmax(-1)
            row=dict(r,arm=arm,step=step,raw=raw,token_ids=suffix.tolist(),first_logp={"0":float(lp[z]),"1":float(lp[o])},
                     margin=float(lp[o]-lp[z]),correct=raw.strip()==r["target"])
            rows.append(row);emit("answers.jsonl",row)
        summary=score(rows);grouped=collections.defaultdict(list)
        for r in rows:grouped[(r["group"],r["anchor"])].append(r)
        rc=[];cc=[]
        for rr in grouped.values():
            rel,conv=contrasts([r["margin"] for r in sorted(rr,key=lambda r:(r["same"],r["reverse"]))]);rc.extend(rel);cc.extend(conv)
        delta=0.0 if block is None else math.sqrt(sum(float((v.detach()-base[k]).square().sum()) for k,v in block.state_dict().items()))
        retain_correct=[]
        for r in retention:
            inp=prompt(r["prompt"]).unsqueeze(0)
            with torch.no_grad():
                g=model.generate(inp,attention_mask=torch.ones_like(inp),do_sample=False,max_new_tokens=8,use_cache=True,pad_token_id=tok.eos_token_id)
            raw=tok.decode(g[0,inp.shape[1]:],skip_special_tokens=True)
            correct=raw.strip()==r["target"]
            if correct:retain_correct.append(r["id"])
            emit("retention.jsonl",dict(r,arm=arm,step=step,raw=raw,correct=correct))
        info={"arm":arm,"step":step,"delta_l2":delta,"metrics":summary,
              "relation_positive":sum(x>0 for x in rc),"convention_positive":sum(x>0 for x in cc),
              "joint_interaction_mean":sum(rc)/len(rc),"retention_correct_ids":retain_correct}
        emit("checkpoints.jsonl",info);print(json.dumps(info),flush=True)
    eval_("base",0)
    for arm,layer in zip(ARMS,LAYERS):
        if block is not None:
            block.load_state_dict(base)
            assert all(torch.equal(v,base[k]) for k,v in block.state_dict().items())
            for x in block.parameters():x.requires_grad_(False)
        block=model.model.layers[layer]
        base={k:v.detach().clone() for k,v in block.state_dict().items()}
        params=list(block.parameters())
        for x in params:x.requires_grad_(True)
        assert sum(x.numel() for x in model.parameters() if x.requires_grad)==counts[0]
        torch.manual_seed(SEED)
        opt=torch.optim.AdamW(params,lr=1e-5,weight_decay=0)
        for step,idx in enumerate(schedule,1):
            model.train();rr=blocks[arm][idx];seq=[prompt(r["prompt"]) for r in rr]
            length=torch.tensor([len(s) for s in seq])
            batch=torch.nn.utils.rnn.pad_sequence(seq,batch_first=True,padding_value=tok.eos_token_id)
            mask=(torch.arange(batch.shape[1])[None,:]<length[:,None]).long()
            target=torch.tensor([ids[r["target"]][0] for r in rr])
            opt.zero_grad(set_to_none=True)
            logits=model(input_ids=batch,attention_mask=mask,use_cache=False).logits[torch.arange(4),length-1].float()
            ce=F.cross_entropy(logits,target)
            rel,conv=contrasts(logits[:,o]-logits[:,z])
            rank=F.softplus(-torch.stack(rel)).mean()
            loss=ce+LAMBDA*rank
            assert torch.isfinite(loss)
            loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0);assert torch.isfinite(norm)
            opt.step()
            emit("train.jsonl",{"arm":arm,"step":step,"anchor":idx,"ids":[r["id"] for r in rr],
                  "ce":float(ce.detach()),"rank":float(rank.detach()),"loss":float(loss.detach()),"grad_norm":float(norm)})
            if step in (8,16):eval_(arm,step)
    # Audit final restore too; no model checkpoint is promoted.
    block.load_state_dict(base)
    assert all(torch.equal(v,base[k]) for k,v in block.state_dict().items())
    for x in block.parameters():x.requires_grad_(False)
    eval_("restored_base",0)
if __name__=="__main__":main()
