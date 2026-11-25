"""LOOP09: budget-constrained adaptive blocks and reversible training.
No Qwen weights loaded by CLI. No release path; candidate functions only.
"""
import argparse, copy, json, random
from collections import Counter, defaultdict
import curriculum06 as c
import trainer07 as t
FIELDS=("actual_input_tokens","gold_target_tokens","foil_target_tokens")
TOL=.02
def need(ok,msg):
    if not ok:raise ValueError(msg)
def vector(enc,ids):
    a=[enc[i] for i in ids]
    return (sum(len(z["input_ids"]) for pair in a for z in pair),
            sum(z[0]["target_tokens"] for z in a),
            sum(z[1]["target_tokens"] for z in a))
def within(v,ref):
    return all(b>0 and abs(a-b)/min(a,b)<=TOL for a,b in zip(v,ref))
def match(train,enc,errors,seed=1234):
    """Move toward adaptive quota only via budget-safe whole-pair swaps.
    Balanced starting plan is always feasible; residual unmet demand reported.
    """
    c.validate(train,"train")
    groups=c.groups(train);index={r["id"]:r for r in train}
    pairids={p:[r["id"] for r in z] for p,z in groups.items()}
    pk={p:z[0]["kind"] for p,z in groups.items()}
    pv={p:vector(enc,ids) for p,ids in pairids.items()}
    base=c.schedule(train,"contrastive",seed)
    goal=c.schedule(train,"adaptive",seed,errors)["skill_pairs"]
    selected=[index[z[0]]["pair"] for z in base["batches"]]
    counts=Counter(pk[p] for p in selected)
    ref=tuple(t.budget(enc,base)[f] for f in FIELDS);cur=ref
    rng=random.Random(seed^9009)
    swaps=0
    while True:
        donors=[i for i,p in enumerate(selected) if counts[pk[p]]>goal[pk[p]] and counts[pk[p]]>16]
        receivers=[p for p in pairids if counts[pk[p]]<goal[pk[p]]]
        if not donors or not receivers:break
        rng.shuffle(donors);rng.shuffle(receivers);best=None
        for i in donors:
            old=selected[i]
            for p in receivers:
                if p in selected:continue
                nxt=tuple(a-b+d for a,b,d in zip(cur,pv[old],pv[p]))
                if not within(nxt,ref):continue
                cost=sum(abs(a-b)/b for a,b in zip(nxt,ref))
                if best is None or cost<best[0]:best=(cost,i,p,nxt)
        if best is None:break
        _,i,p,cur=best;counts[pk[selected[i]]]-=1;selected[i]=p;counts[pk[p]]+=1;swaps+=1
    # Order hard skills first, within a deterministic shuffled tie break.
    rng.shuffle(selected);selected.sort(key=lambda p:-errors[pk[p]])
    plan=dict(strategy="adaptive",batches=[pairids[p] for p in selected],skill_pairs=dict(counts),examples=256,optimizer_steps=128)
    b=t.budget(enc,plan);need(within(tuple(b[f] for f in FIELDS),ref),"TOKEN_MATCH")
    need(len(set(selected))==len(selected)==128 and min(counts.values())>=16,"REPLAY")
    need(all(b[f]==t.budget(enc,base)[f] for f in ("steps","examples","forward_sequences","padded_positions")),"COMPUTE")
    return plan,dict(requested=goal,achieved=dict(counts),swaps=swaps,remaining_quota_gap=sum(abs(counts[k]-goal[k]) for k in c.KINDS)//2,budget=b,reference=t.budget(enc,base),token_match=True)
def decide(before,after):
    """Dev-only acceptance; not evidence of independent generalization."""
    need(set(before)==set(after)==set(c.KINDS),"SKILLS")
    for s in (before,after):
        for d in s.values():
            need(type(d["correct"]) is int and type(d["both_pairs"]) is int and 0<=d["both_pairs"]<=16 and 2*d["both_pairs"]<=d["correct"]<=16+d["both_pairs"],"DEV_COUNTS")
    dc={k:after[k]["correct"]-before[k]["correct"] for k in c.KINDS}
    dp={k:after[k]["both_pairs"]-before[k]["both_pairs"] for k in c.KINDS}
    # No skill loses an exact answer or complete pair; at least one new pair
    # and two additional correct answers in total. Conservative exploratory gate.
    accepted=min(dc.values())>=0 and min(dp.values())>=0 and sum(dc.values())>=2 and sum(dp.values())>=1
    return dict(accepted=accepted,correct_delta=dc,pair_delta=dp,scope="dev-only; independent evaluation still mandatory")
def reversible_block(model,opt,params,batches,step,evaluate):
    """Candidate block transaction. Only trainable tensors and optimizer changed.
    Caller must provide isolated model/optimizer and dev evaluation, never holdout.
    """
    import torch
    params=list(params);need(params and all(p.requires_grad for p in params),"PARAMETERS")
    need(len(batches)>0,"NO_BATCH")
    saved=[p.detach().clone() for p in params];state=copy.deepcopy(opt.state_dict());rng=torch.random.get_rng_state();mode=model.training
    def restore():
        with torch.no_grad():
            for p,v in zip(params,saved):p.copy_(v)
        opt.load_state_dict(state);opt.zero_grad(set_to_none=True);torch.random.set_rng_state(rng)
    try:
        before=evaluate();model.train()
        stats=[step(batch) for batch in batches];after=evaluate();verdict=decide(before,after)
        if not verdict["accepted"]:restore()
        return dict(before=before,after=after,verdict=verdict,steps=len(stats),stats=stats,rolled_back=not verdict["accepted"])
    except BaseException:
        restore();raise
    finally:model.train(mode)
def candidate_qwen_block(model,tok,opt,train,plan,evaluate_dev):
    """Callable implementation; deliberately inaccessible from CLI/release gate.
    evaluate_dev must return four skill scores from independent frozen dev inference.
    """
    enc=t.prepare(tok,train);params=[p for p in model.parameters() if p.requires_grad]
    need(plan["strategy"] in t.STRATEGIES and len(plan["batches"])==128,"PLAN")
    batches=[t.collate(tok,enc,ids) for ids in plan["batches"]]
    return reversible_block(model,opt,params,batches,lambda b:t.optimizer_step(model,opt,params,b,plan["strategy"]),evaluate_dev)
def preflight():
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    train=c.build("train",t.SEED);enc=t.prepare(tok,train)
    fixtures=[dict(copy=2,select=14,membership=16,reverse=1),dict.fromkeys(c.KINDS,16),dict(copy=16,select=0,membership=0,reverse=0)]
    result=[]
    for errors in fixtures:
        _,report=match(train,enc,errors);result.append(dict(errors=errors,**report))
    print(json.dumps(dict(status="BUDGET_PREFLIGHT",fixture_results=result,training_authorized=False,real_dev_errors_used=False),indent=2))
def selftest():
    import torch
    train=c.build("train",t.SEED)
    # Mock tokens; real tokenizer is tested separately.
    enc={r["id"]:[dict(input_ids=[0]*40,target_tokens=4),dict(input_ids=[0]*40,target_tokens=4)] for r in train}
    errors=dict(copy=2,select=14,membership=16,reverse=1)
    p,b=match(train,enc,errors);need(b["remaining_quota_gap"]==0 and b["token_match"],"MOCK_MATCH")
    need(match(train,enc,errors)==(p,b),"DETERMINISM")
    before={k:dict(correct=16,both_pairs=4) for k in c.KINDS}
    good=copy.deepcopy(before);good["membership"]=dict(correct=18,both_pairs=5)
    bad=copy.deepcopy(good);bad["reverse"]=dict(correct=15,both_pairs=4)
    need(decide(before,good)["accepted"] and not decide(before,bad)["accepted"] and not decide(before,before)["accepted"],"DECISION")
    torch.manual_seed(9);model=torch.nn.Linear(1,1);opt=torch.optim.AdamW(model.parameters(),lr=.1)
    params=list(model.parameters());orig=[p.detach().clone() for p in params]
    def step(_):
        opt.zero_grad();loss=model(torch.ones(1,1)).square().sum();loss.backward();opt.step();return float(loss.detach())
    seq=iter([before,bad]);r=reversible_block(model,opt,params,[1],step,lambda:next(seq))
    need(r["rolled_back"] and all(torch.equal(a,p) for a,p in zip(orig,params)) and not opt.state,"ROLLBACK")
    seq=iter([before,good]);r=reversible_block(model,opt,params,[1],step,lambda:next(seq))
    need(not r["rolled_back"] and any(not torch.equal(a,p) for a,p in zip(orig,params)),"COMMIT")
    snapshot=[p.detach().clone() for p in params]
    def broken(x):step(x);raise RuntimeError("synthetic failure")
    try:reversible_block(model,opt,params,[1],broken,lambda:before)
    except RuntimeError:pass
    else:raise ValueError("EXCEPTION_NOT_RAISED")
    need(all(torch.equal(a,p) for a,p in zip(snapshot,params)),"EXCEPTION_ROLLBACK")
    print("LOOP09 toy rollback and schedule controls passed; no Qwen training")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","preflight"]);a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:preflight()
