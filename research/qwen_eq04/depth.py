"""EQ04 matched-depth pilot. Fixed EQ03 B objective, only block index changes."""
import argparse, collections, json, math, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq02"))
from equality import MODEL,REVISION,dataset,make_group,score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq03"))
from compare import data as previous_data
SEED=271128
ARMS=("block_01","block_12","block_24")
LAYERS=(0,11,23)
STEPS=16
LAMBDA=0.5
def data():
    train,old=dataset()
    groups={}
    for r in train: groups.setdefault(r["anchor"],[]).append(r)
    blocks=[sorted(v,key=lambda r:(r["same"],r["reverse"])) for k,v in sorted(groups.items())]
    assert len(blocks)==8 and all(len(b)==4 for b in blocks)
    # New exam disjoint from both previous training and previous evaluation.
    exam=make_group("novel_values",[("102","103"),("205","305"),("340","304"),("461","462")])+make_group("paraphrase",[("501","510"),("602","603"),("710","711"),("801","802")])+make_group("symbol_transfer",[("feg","fag"),("wim","win"),("jup","jpu"),("salo","sal")])
    vals=lambda rr:{v for r in rr for v in (r["a"],r["b"])}
    assert not vals(exam)&vals(train+old+previous_data()[1])
    assert len({r["prompt"] for r in exam})==len(exam)==48
    for b in blocks:
        assert [(r["same"],r["reverse"]) for r in b]==[(False,False),(False,True),(True,False),(True,True)]
        assert [r["target"] for r in b]==["0","1","1","0"]
    schedule=[]
    rng=random.Random(SEED)
    for epoch in range(2):
        order=list(range(8));rng.shuffle(order);schedule.extend(order)
    assert len(schedule)==STEPS
    return blocks,exam,schedule

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
    assert score([dict(r,raw=r["target"],correct=True) for r in exam])["all"]["quartets_all_correct"]==12
    print("Fixture OK: same 64 presentations per arm; 48 new evaluation prompts; contrast signs checked")
def main():
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--out",default="eq04-results")
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
        "scope":"one block only, direct weights, one seed, no EOS training; earlier blocks require gradients through frozen downstream layers",
        "criteria":"pilot: >=36/48 exact, >=8/12 quartets, >=12/16 per group; improvement of >=4 answers over block_24, and no loss of initially correct retention answers; descriptive only",
        "limitations":"No checkpoints saved; retention screen is tiny; three-digit exam numbers change difficulty; finite correlated quartets, explicitly supervised contrasts; matched trainable parameters, presentations and steps, not FLOPs."}
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
            for x in block.parameters():x.requires_grad_(False)
        block=model.model.layers[layer]
        base={k:v.detach().clone() for k,v in block.state_dict().items()}
        params=list(block.parameters())
        for x in params:x.requires_grad_(True)
        assert sum(x.numel() for x in model.parameters() if x.requires_grad)==counts[0]
        torch.manual_seed(SEED)
        opt=torch.optim.AdamW(params,lr=1e-5,weight_decay=0)
        for step,idx in enumerate(schedule,1):
            model.train();rr=blocks[idx];seq=[prompt(r["prompt"]) for r in rr]
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
if __name__=="__main__":main()
