"""PROTECT22: four reversible real-Qwen displacement probes, not a learning trial.
Same proposed AdamW step compared to its projected displacement from identical state.
No persistent updates, no dev/holdout gradients, no publication of adapters.
"""
import argparse,copy,json,random,time,tempfile
from pathlib import Path
import numpy as np
import curriculum06 as c
import trainer07 as t
import runner11 as r
import pilot14 as p
import cumulative18 as a
import retention16 as b
import protect21 as k

SEED=2026112522
PROBES=4

def need(ok,msg):
    if not ok:raise ValueError(msg)

def run(budget,original,result,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    out=Path(out);out.mkdir(exist_ok=False);original=Path(original)
    started=time.monotonic();k.selftest();m=a.check_sources(original,result)
    torch.set_num_threads(2);torch.manual_seed(t.SEED)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    train,enc,plans,budgets=p.plan_audit(tok,budget)
    old,new=b.datasets();need(old==train,"OLD_TRAIN")
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    need(model.config._commit_hash==c.REV,"REV");model.config.use_cache=False
    model=get_peft_model(model,t.lora_config())
    named=[(n,w) for n,w in model.named_parameters() if w.requires_grad];params=[w for n,w in named]
    frozen=[(n,w) for n,w in model.named_parameters() if not w.requires_grad]
    need(r.tensor_hash(named)==m["initial_adapter_sha"] and r.tensor_hash(frozen)==m["frozen_base_sha"],"INIT")
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.0);dev=c.build("dev",t.SEED+1)
    for j in (0,1):
        if j:
            model.train()
            for i,ids in enumerate(plans["adaptive"]["batches"]):
                t.optimizer_step(model,opt,params,t.collate(tok,enc,ids),"adaptive")
                if (i+1)%16==0:print("PROTECT22 reproduction",i+1,"/128",flush=True)
        _,trace=r.evaluate_dev(model,tok,dev)
        need(a.rawmap(trace)==a.rawmap(a.load(original/("dev-%d.json"%j))),"DEV_REPRODUCTION")
    need(r.tensor_hash(named)==m["final_transaction_adapter_sha"],"TENSOR_REPRODUCTION")
    with tempfile.TemporaryDirectory() as tmp:
        files=r.save_adapter(model,Path(tmp)/"adapter")
        need(files["adapter_model.safetensors"]==a.EXPECTED,"FILE_REPRODUCTION")
    checkpoint=r.tensor_hash(named)
    saved=[w.detach().clone() for w in params];state=copy.deepcopy(opt.state_dict());rngstate=torch.random.get_rng_state()
    def restore():
        with torch.no_grad():
            for w,v in zip(params,saved):w.copy_(v)
        opt.load_state_dict(copy.deepcopy(state));opt.zero_grad(set_to_none=True);torch.random.set_rng_state(rngstate)
        need(r.tensor_hash(named)==checkpoint,"RESTORE")
    def vector(ts):
        return np.concatenate([v.detach().cpu().reshape(-1).numpy().astype(np.float64) for v in ts])
    def delta():return vector([w.detach()-v for w,v in zip(params,saved)])
    def assign(displacement):
        off=0
        with torch.no_grad():
            for w,v in zip(params,saved):
                n=w.numel();part=torch.from_numpy(displacement[off:off+n].copy()).reshape(w.shape)
                w.copy_((v.double()+part).to(w.dtype));off+=n
        need(off==len(displacement),"DIMENSION")
    def loss(batch,grad=False):
        model.train(grad)
        with torch.set_grad_enabled(grad):
            out=model(input_ids=batch["input_ids"],attention_mask=batch["attention_mask"],use_cache=False)
            value,_,_=t.loss_parts(out.logits,batch["labels"],"adaptive")
            val=float(value.detach())
            need(np.isfinite(val),"LOSS")
            if grad:
                g=torch.autograd.grad(value,params)
                return val,vector(g)
            return val
    # Deterministic samples, chosen without dev or transfer outcomes.
    oldg=b.pairs(old);newg=b.pairs(new);newenc=b.encode(tok,newg)
    rng=random.Random(SEED)
    pool={skill:sorted(q for q,z in oldg.items() if z[0]["kind"]==skill) for skill in c.KINDS}
    anchor={skill:rng.sample(pool[skill],2*PROBES) for skill in c.KINDS}
    fresh=rng.sample(sorted(newg),PROBES)
    reports=[]
    for i,q in enumerate(fresh):
        restore()
        keys={skill:anchor[skill][i] for skill in c.KINDS}
        auditkeys={skill:anchor[skill][PROBES+i] for skill in c.KINDS}
        def oldbatch(pair):return t.collate(tok,enc,[v["id"] for v in oldg[pair]])
        ab={skill:oldbatch(pair) for skill,pair in keys.items()}
        hb={skill:oldbatch(pair) for skill,pair in auditkeys.items()}
        nb=t.collate(tok,newenc,[v["id"] for v in newg[q]])
        # All probes compare the same proposed step and its projection.
        vals=[];grads=[]
        for skill in c.KINDS:
            val,g=loss(ab[skill],True);vals.append(val);grads.append(g)
        g=np.stack(grads)
        def measure():return dict(new=loss(nb),anchor={s:loss(ab[s]) for s in c.KINDS},disjoint_train_audit={s:loss(hb[s]) for s in c.KINDS})
        before=measure()
        need(all(abs(before["anchor"][s]-v)<1e-5 for s,v in zip(c.KINDS,vals)),"ANCHOR_MODE")
        model.train()
        stats=t.optimizer_step(model,opt,params,nb,"adaptive");d=delta()
        need(np.isfinite(d).all() and np.linalg.norm(d)>0,"ZERO_OR_INVALID_PROPOSAL")
        ordinary=measure()
        projected,meta=k.protect(d,g)
        assign(projected);realized=delta()
        norms=np.linalg.norm(g,axis=1);tol=1e-6*np.linalg.norm(d)
        unit=g[norms>0]/norms[norms>0,None]
        rounding_fallback=bool(np.any(unit@realized>tol))
        if rounding_fallback:
            assign(np.zeros_like(d));realized=delta()
        need(np.all(unit@realized<=tol),"REALIZED_INFEASIBLE")
        corrected=measure()
        report=dict(probe=i,new_pair=q,anchor_pairs=keys,disjoint_train_audit_pairs=auditkeys,optimizer_step=stats,projection=meta,rounding_fallback=rounding_fallback,proposed_norm=float(np.linalg.norm(d)),realized_norm=float(np.linalg.norm(realized)),linear_change_proposed=dict(zip(c.KINDS,(g@d).tolist())),linear_change_protected=dict(zip(c.KINDS,(g@realized).tolist())),before=before,ordinary=ordinary,protected=corrected)
        restore();reports.append(report);print("PROTECT22 probe",i+1,json.dumps(report),flush=True)
        r.json_write(out/"probes.json",reports)
    need(r.tensor_hash(frozen)==m["frozen_base_sha"] and r.tensor_hash(named)==checkpoint,"FINAL_RESTORE")
    def increases(which,scope):
        return sum(v[which][scope][s]>v["before"][scope][s]+1e-6 for v in reports for s in c.KINDS)
    def delta_new(which):return [v[which]["new"]-v["before"]["new"] for v in reports]
    summary=dict(status="REAL_QWEN_REVERSIBLE_DISPLACEMENT_DIAGNOSTIC",reproduction_updates=128,proposed_probe_updates=PROBES,retained_probe_updates=0,first_block_adapter_sha=a.EXPECTED,anchor_loss_increases={"ordinary":increases("ordinary","anchor"),"protected":increases("protected","anchor")},disjoint_train_loss_increases={"ordinary":increases("ordinary","disjoint_train_audit"),"protected":increases("protected","disjoint_train_audit")},new_loss_deltas={"ordinary":delta_new("ordinary"),"protected":delta_new("protected")},probes=reports,seconds=time.monotonic()-started,scope="four single-step probes from the same checkpoint, train-only anchors and distinct train audit pairs; not a held-out skill or long-run retention test",optimizer_moments="all probe moments restored, no corrected-step optimizer state retained",independent_curator=False,promotion_authorized=False,weights_published=False)
    r.json_write(out/"result.json",summary);print(json.dumps(summary,indent=2))
if __name__=="__main__":
    q=argparse.ArgumentParser()
    for name in ("budget","original","result","out"):q.add_argument("--"+name,required=True)
    v=q.parse_args();run(v.budget,v.original,v.result,v.out)
