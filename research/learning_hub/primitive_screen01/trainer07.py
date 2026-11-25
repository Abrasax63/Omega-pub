"""TRAINER07: Qwen-compatible LoRA step and token-budget preflight.
No model-weight download or training entrypoint. Release remains closed.
"""
import argparse, json, math
from collections import defaultdict
import curriculum06 as c
MAX_LENGTH=128
MARGIN=0.25
PAIR_WEIGHT=0.5
SEED=20261125
STRATEGIES=("supervised","contrastive","adaptive")
def need(ok,msg):
    if not ok:raise ValueError(msg)
def loss_parts(logits,labels,strategy):
    """Rows: correct/foil for each example, in alternating order.
    Identical forward work in all strategies; foil is NOT a target for CE.
    """
    import torch
    import torch.nn.functional as F
    need(strategy in STRATEGIES and logits.ndim==3 and labels.shape==logits.shape[:2] and len(labels)%2==0,"SHAPE")
    y=labels[:,1:];mask=y.ne(-100)
    need(bool(mask.any(dim=1).all()),"EMPTY_TARGET")
    safe=y.masked_fill(~mask,0)
    lp=F.log_softmax(logits[:,:-1,:].float(),dim=-1).gather(-1,safe.unsqueeze(-1)).squeeze(-1)
    scores=(lp*mask).sum(1)/mask.sum(1)
    good=scores[::2];bad=scores[1::2]
    ce=-good.mean()
    hinge=torch.relu(MARGIN-(good-bad)).mean()
    total=ce+PAIR_WEIGHT*hinge if strategy=="contrastive" else ce
    need(bool(torch.isfinite(total)),"NONFINITE")
    return total,ce,hinge
def encode(tok,r,foil):
    prefix=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=True,add_generation_prompt=True)
    need(isinstance(prefix,list) and prefix,"CHAT_PREFIX")
    rows=[]
    for answer in (r["gold"],foil):
        suffix=tok(answer,add_special_tokens=False)["input_ids"]+[tok.eos_token_id]
        need(suffix and len(prefix)+len(suffix)<=MAX_LENGTH,"TOKEN_LIMIT")
        ids=prefix+suffix
        rows.append(dict(input_ids=ids,labels=[-100]*len(prefix)+suffix,prompt_tokens=len(prefix),target_tokens=len(suffix)))
    need(rows[0]["input_ids"]!=rows[1]["input_ids"],"IDENTICAL_TARGET")
    return rows
def prepare(tok,train):
    c.validate(train,"train")
    encoded={}
    for group in c.groups(train).values():
        a,b=group
        encoded[a["id"]]=encode(tok,a,b["gold"])
        encoded[b["id"]]=encode(tok,b,a["gold"])
    return encoded
def collate(tok,encoded,ids):
    import torch
    rows=[z for i in ids for z in encoded[i]]
    X=[];Y=[];A=[]
    for z in rows:
        n=len(z["input_ids"]);pad=MAX_LENGTH-n
        X.append(z["input_ids"]+[tok.pad_token_id]*pad);Y.append(z["labels"]+[-100]*pad);A.append([1]*n+[0]*pad)
    return dict(input_ids=torch.tensor(X),attention_mask=torch.tensor(A),labels=torch.tensor(Y))
def optimizer_step(model,opt,params,batch,strategy):
    """Reusable step for a future reviewed trainer; not called by this CLI."""
    import torch
    opt.zero_grad(set_to_none=True)
    out=model(input_ids=batch["input_ids"],attention_mask=batch["attention_mask"],use_cache=False)
    loss,ce,hinge=loss_parts(out.logits,batch["labels"],strategy)
    loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0,error_if_nonfinite=True)
    opt.step()
    return dict(loss=float(loss.detach()),ce=float(ce.detach()),hinge=float(hinge.detach()),grad_norm=float(norm))
def lora_config():
    from peft import LoraConfig
    return LoraConfig(r=8,lora_alpha=16,lora_dropout=0.0,bias="none",target_modules=["q_proj","v_proj"],task_type="CAUSAL_LM")
def budget(encoded,plan):
    selected=[encoded[i] for z in plan["batches"] for i in z]
    flat=[r for pair in selected for r in pair]
    return dict(steps=len(plan["batches"]),examples=len(selected),forward_sequences=len(flat),padded_positions=len(flat)*MAX_LENGTH,actual_input_tokens=sum(len(z["input_ids"]) for z in flat),gold_target_tokens=sum(z[0]["target_tokens"] for z in selected),foil_target_tokens=sum(z[1]["target_tokens"] for z in selected),skill_pairs=plan["skill_pairs"])
def preflight():
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    need(tok.eos_token_id is not None and tok.pad_token_id is not None,"SPECIAL_TOKENS")
    train=c.build("train",SEED);dev=c.build("dev",SEED+1);holdout=c.build("holdout",SEED+2)
    for split,rows in (("train",train),("dev",dev),("holdout",holdout)):c.validate(rows,split)
    enc=prepare(tok,train)
    # Simulated errors exercise scheduling only; never present as measured model errors.
    fixture=dict(copy=2,select=14,membership=16,reverse=1)
    plans={s:c.schedule(train,s,1234,fixture if s=="adaptive" else None) for s in STRATEGIES}
    budgets={s:budget(enc,p) for s,p in plans.items()}
    need(len({(b["steps"],b["examples"],b["forward_sequences"],b["padded_positions"]) for b in budgets.values()})==1,"PADDED_BUDGET")
    need(budgets["supervised"]==budgets["contrastive"],"CONTROL_BUDGET")
    fields=("actual_input_tokens","gold_target_tokens","foil_target_tokens")
    spread={f:(max(b[f] for b in budgets.values())-min(b[f] for b in budgets.values()))/min(b[f] for b in budgets.values()) for f in fields}
    result=dict(status="TOKENIZER_PREFLIGHT",model=c.MODEL,revision=c.REV,budgets=budgets,relative_spread=spread,token_budget_within_2_percent=all(x<=.02 for x in spread.values()),adaptive_errors_source="synthetic fixture, not model results",training_authorized=False,reason="fresh independent holdout, measured dev errors, fair token budget, full trainer audit and release required")
    print(json.dumps(result,indent=2))
def selftest():
    import torch
    torch.manual_seed(SEED)
    # Causal toy logits: correct sequence has target 1, foil target 2.
    labels=torch.tensor([[-100,1],[-100,2],[-100,2],[-100,1]])
    logits=torch.zeros(4,2,3,requires_grad=True)
    ce,_,h=loss_parts(logits,labels,"supervised")
    pair,_,hp=loss_parts(logits,labels,"contrastive")
    need(abs(float(h)-MARGIN)<1e-6 and abs(float(hp)-MARGIN)<1e-6 and float(pair)>float(ce),"CONSTANT_PENALTY")
    pair.backward()
    need(bool(torch.isfinite(logits.grad).all()) and float(logits.grad.abs().sum())>0,"GRADIENT")
    good=torch.zeros(4,2,3);good[0,0,1]=8;good[1,0,1]=8;good[2,0,2]=8;good[3,0,2]=8
    _,_,hgood=loss_parts(good,labels,"contrastive");need(float(hgood)==0,"CORRECT_MARGIN")
    wrong=good.flip(0);_,_,hwrong=loss_parts(wrong,labels,"contrastive");need(float(hwrong)>MARGIN,"WRONG_MARGIN")
    for bad in (labels[:3],torch.full_like(labels,-100)):
        try:loss_parts(good[:len(bad)],bad,"contrastive")
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    # Actual optimizer update on a toy neural network, not Qwen.
    class Toy(torch.nn.Module):
        def __init__(self):
            super().__init__();self.emb=torch.nn.Embedding(3,4);self.head=torch.nn.Linear(4,3)
        def forward(self,input_ids,attention_mask,use_cache):
            from types import SimpleNamespace
            return SimpleNamespace(logits=self.head(self.emb(input_ids)))
    toy=Toy();params=list(toy.parameters());before=[p.detach().clone() for p in params]
    opt=torch.optim.AdamW(params,lr=.001)
    batch=dict(input_ids=torch.tensor([[0,1],[0,2],[2,2],[2,1]]),attention_mask=torch.ones(4,2,dtype=torch.long),labels=labels)
    stats=optimizer_step(toy,opt,params,batch,"contrastive")
    need(any(not torch.equal(a,b) for a,b in zip(before,params)) and all(math.isfinite(v) for v in stats.values()),"TOY_UPDATE")
    print(json.dumps(dict(status="TOY_LOSS_AND_UPDATE_OK",constant_hinge=float(h),correct_hinge=float(hgood),wrong_hinge=float(hwrong),toy_step=stats,training_authorized=False)))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","preflight"]);a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:preflight()
