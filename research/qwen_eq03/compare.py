"""EQ03: matched-budget direct-weight pilot on equality, no inference correction.
A: CE only. B: CE + relational ranking. C: CE + relational and convention ranking.
All arms see exactly the same four inputs per optimizer step.
"""
import argparse, collections, json, math, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qwen_eq02"))
from equality import MODEL,REVISION,dataset,make_group,score
SEED=271128
ARMS=("A_ce","B_opposition","C_structure")
STEPS=16
LAMBDA=0.5
def data():
    train,old=dataset()
    groups={}
    for r in train: groups.setdefault(r["anchor"],[]).append(r)
    blocks=[sorted(v,key=lambda r:(r["same"],r["reverse"])) for k,v in sorted(groups.items())]
    assert len(blocks)==8 and all(len(b)==4 for b in blocks)
    # New exam disjoint from both previous training and previous evaluation.
    exam=make_group("novel_values",[("10","11"),("20","21"),("30","31"),("40","41")])+make_group("paraphrase",[("50","51"),("60","63"),("70","71"),("80","82")])+make_group("symbol_transfer",[("vex","vox"),("bim","bin"),("zul","zlu"),("pano","pan")])
    vals=lambda rr:{v for r in rr for v in (r["a"],r["b"])}
    assert not vals(exam)&vals(train+old)
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
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--out",default="eq03-results")
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
    block=model.model.layers[-1]
    for x in block.parameters():x.requires_grad_(True)
    params=list(block.parameters());base={k:v.detach().clone() for k,v in block.state_dict().items()}
    ids={s:tok(s,add_special_tokens=False).input_ids for s in ("0","1")}
    assert all(len(v)==1 for v in ids.values())
    z,o=ids["0"][0],ids["1"][0]
    def prompt(q):
        return tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,return_tensors="pt")[0]
    def emit(file,row):
        with (out/file).open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    manifest={"model":MODEL,"revision":REVISION,"seed":SEED,"torch":torch.__version__,"arms":ARMS,"train_blocks":blocks,"exam":exam,
        "schedule":schedule,"steps_per_arm":STEPS,"presentations_per_arm":STEPS*4,"lr":1e-5,"lambda":LAMBDA,
        "trainable":sum(x.numel() for x in params),"total":sum(x.numel() for x in model.parameters()),
        "objectives":"All use mean next-token CE. B adds mean softplus(-rel); C adds mean softplus(-[rel,conv]).",
        "scope":"last transformer block only, one seed, no EOS training; A is matched-batch CE, not exact EQ02 reproduction",
        "criteria":"descriptive pilot: >=36/48 exact, >=8/12 quartets, >=12/16 per exam group, >=4 more correct than matched A; no promotion without independent fresh test and seeds",
        "limitations":"No checkpoints saved, no other-operations retention exam, finite correlated quartets, contrast objectives explicitly supervised, same sample/optimizer budget not identical wall time."}
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
        delta=math.sqrt(sum(float((v.detach()-base[k]).square().sum()) for k,v in block.state_dict().items()))
        info={"arm":arm,"step":step,"delta_l2":delta,"metrics":summary,
              "relation_positive":sum(x>0 for x in rc),"convention_positive":sum(x>0 for x in cc),
              "relation_mean":sum(rc)/len(rc),"convention_mean":sum(cc)/len(cc)}
        emit("checkpoints.jsonl",info);print(json.dumps(info),flush=True)
    eval_("base",0)
    for arm in ARMS:
        block.load_state_dict(base);torch.manual_seed(SEED)
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
            rank=F.softplus(-torch.stack(rel if arm=="B_opposition" else rel+conv)).mean()
            loss=ce if arm=="A_ce" else ce+LAMBDA*rank
            assert torch.isfinite(loss)
            loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0);assert torch.isfinite(norm)
            opt.step()
            emit("train.jsonl",{"arm":arm,"step":step,"anchor":idx,"ids":[r["id"] for r in rr],
                  "ce":float(ce.detach()),"rank":float(rank.detach()),"loss":float(loss.detach()),"grad_norm":float(norm)})
            if step in (8,16):eval_(arm,step)
if __name__=="__main__":main()
