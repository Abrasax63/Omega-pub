"""CUMULATIVE18: reproduce adaptive PILOT14, then conditionally test replay.
No deployment, no published weights. Same-author exploratory evaluation.
"""
import argparse,copy,json,math,time,tempfile
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import loop09 as l
import runner11 as r
import pilot14 as p
import transfer13 as x
import retention15 as a
import retention16 as b

EXPECTED="2f2a769b5aa7482baa96db11b208d66e2b15aae5f28b2d9a00735668561290b8"
OLD_SEED=2026112518
NEW_SEED=2026112519

def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(path):return json.loads(Path(path).read_text())
def records(path):return [json.loads(z) for z in Path(path).read_text().splitlines()]
def rawmap(z):return {v["id"]:v["raw"] for v in z}
def save(out,name,obj):r.json_write(out/name,obj)

def check_sources(original,result):
    m=load(original/"manifest.json");s=load(result)
    need(m["arm"]=="adaptive" and m["revision"]==c.REV and m["candidate_files_sha"]["adapter_model.safetensors"]==EXPECTED,"SOURCE")
    need(m["optimizer_updates"]==128 and not m["transaction"]["rolled_back"],"FIRST_BLOCK")
    need(r.sha(original/"predictions.jsonl")==m["predictions_sha"],"FIRST_PREDICTIONS")
    eligible=[k for k in ("supervised","contrastive","adaptive") if s["comparisons"][k]["exploratory_transfer_gain"] and s["dev_decisions"][k]["accepted"]]
    best=max(eligible,key=lambda k:(sum(v["both_pairs"] for v in s["scores"][k].values()),sum(v["correct"] for v in s["scores"][k].values()),-("supervised","contrastive","adaptive").index(k)))
    need(best=="adaptive","SELECTION")
    need(x.score(x.make(p.PILOT_SEED,p.FORM),records(original/"predictions.jsonl"))==s["scores"]["adaptive"],"FIRST_SCORE")
    return m

def budget_check(tok,old,new,planfile):
    plan=load(planfile);need(plan["revision"]==c.REV and plan["optimality_proved"] and plan["replay_pairs"]==4,"REPLAY_SOURCE")
    g={**b.pairs(old),**b.pairs(new)};enc=b.encode(tok,g)
    idx={z["id"]:z for z in old+new};newids={z["id"] for z in new}
    plans=plan["plans"];need(set(plans)=={"new_only","replay"} and plans["new_only"][:32]==plans["replay"][:32],"PREFIX")
    for arm,z in plans.items():
        ids=[i for batch in z for i in batch]
        need(len(z)==64 and len(ids)==len(set(ids))==128 and set(ids)<=set(idx),"PLAN")
        need(all(len(batch)==2 and idx[batch[0]]["pair"]==idx[batch[1]]["pair"] for batch in z),"PAIR")
        need(all(i in newids for batch in z[:32] for i in batch),"PREFIX_NEW")
        expected=128 if arm=="new_only" else 120
        need(sum(i in newids for i in ids)==expected,"DOSE")
        from collections import Counter
        if arm=="replay":need(Counter(idx[i]["kind"] for i in ids if i not in newids)=={k:2 for k in c.KINDS},"REPLAY_BALANCE")
        vector=l.vector(enc,ids);ref=plan["reference" if arm=="new_only" else "candidate"]
        need(dict(zip(l.FIELDS,vector))==ref,"BUDGET")
    need(l.within(tuple(plan["candidate"][f] for f in l.FIELDS),tuple(plan["reference"][f] for f in l.FIELDS)),"BUDGET_GAP")
    return enc,plans,plan

def eval_fresh(model,tok,oldrows,newrows,out,name):
    # No scores fed to the training or scheduling decisions.
    scores={}
    for label,rows,scorer in (("old",oldrows,x.score),("new",newrows,lambda z,v:a.score(z,v,"fixture"))):
        # separate generic generation, question-only
        import torch
        model.eval();pred=[]
        for q in [{"id":z["id"],"prompt":z["prompt"]} for z in rows]:
            prompt=tok.apply_chat_template([{"role":"user","content":q["prompt"]}],tokenize=False,add_generation_prompt=True)
            inp=tok(prompt,return_tensors="pt",add_special_tokens=False);n=inp["input_ids"].shape[1]
            need(n+16<=t.MAX_LENGTH,"CONTEXT")
            with torch.inference_mode():ids=model.generate(**inp,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            pred.append(dict(id=q["id"],prompt_sha=r.digest(q["prompt"]),raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)))
        save(out,name+"-"+label+".json",pred);scores[label]=scorer(rows,pred)
    return scores

def run(budgetfile,planfile,original,result,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    original=Path(original);out=Path(out);out.mkdir(exist_ok=False);started=time.monotonic()
    m=check_sources(original,result)
    torch.set_num_threads(2);torch.manual_seed(t.SEED)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    tr,enc,plans,budgets=p.plan_audit(tok,budgetfile)
    old,new=b.datasets();enc2,plans2,replaybudget=budget_check(tok,old,new,planfile)
    need(tr==old,"OLD_TRAIN")
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    need(model.config._commit_hash==c.REV,"REV");model.config.use_cache=False
    model=get_peft_model(model,t.lora_config());named=[(n,w) for n,w in model.named_parameters() if w.requires_grad];params=[w for n,w in named]
    frozen=[(n,w) for n,w in model.named_parameters() if not w.requires_grad]
    need(r.tensor_hash(named)==m["initial_adapter_sha"] and r.tensor_hash(frozen)==m["frozen_base_sha"],"INIT")
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.0);dev=c.build("dev",t.SEED+1)
    for j in (0,1):
        if j:
            model.train()
            for i,ids in enumerate(plans["adaptive"]["batches"]):
                t.optimizer_step(model,opt,params,t.collate(tok,enc,ids),"adaptive")
                if (i+1)%16==0:print("CUMULATIVE18 reproduction",i+1,"/128",flush=True)
        score,trace=r.evaluate_dev(model,tok,dev);save(out,"reproduced-dev-%d.json"%j,trace)
        need(rawmap(trace)==rawmap(load(original/("dev-%d.json"%j))),"DEV_REPRODUCTION")
    need(r.tensor_hash(named)==m["final_transaction_adapter_sha"],"ADAPTER_TENSOR_REPRODUCTION")
    with tempfile.TemporaryDirectory() as tmp:
        files=r.save_adapter(model,Path(tmp)/"adapter");need(files["adapter_model.safetensors"]==EXPECTED,"ADAPTER_FILE_REPRODUCTION")
    p.evaluate_pilot(model,tok,p.pilot_questions(),out/"reproduced-transfer.jsonl")
    need(rawmap(records(out/"reproduced-transfer.jsonl"))==rawmap(records(original/"predictions.jsonl")),"TRANSFER_REPRODUCTION")
    save(out,"reproduction.json",dict(status="EXACT_REPRODUCTION",optimizer_updates=128,adapter_sha=EXPECTED,original_prediction_sha=m["predictions_sha"],reproduced_prediction_sha=r.sha(out/"reproduced-transfer.jsonl"),promotion_authorized=False))
    print("CUMULATIVE18 exact first-block reproduction passed",flush=True)
    oldrows=x.make(OLD_SEED,"retention18-old");newrows=a.build("fixture",NEW_SEED)
    need(not {z["prompt"] for z in oldrows}&{z["prompt"] for z in x.make(p.PILOT_SEED,p.FORM)},"OLD_EVAL_OVERLAP")
    # Freeze new questions only after the reproduced first-block checkpoint.
    baseline=eval_fresh(model,tok,oldrows,newrows,out,"control")
    def step_range(z):
        model.train()
        for i,ids in enumerate(z):
            t.optimizer_step(model,opt,params,t.collate(tok,enc2,ids),"adaptive")
            if (i+1)%8==0:print("CUMULATIVE18 block",i+1,"/",len(z),flush=True)
    step_range(plans2["new_only"][:32])
    shared=eval_fresh(model,tok,oldrows,newrows,out,"shared")
    snapshot=[w.detach().clone() for w in params];state=copy.deepcopy(opt.state_dict());rng=torch.random.get_rng_state()
    sharedhash=r.tensor_hash(named)
    def restore():
        with torch.no_grad():
            for w,v in zip(params,snapshot):w.copy_(v)
        opt.load_state_dict(copy.deepcopy(state));opt.zero_grad(set_to_none=True);torch.random.set_rng_state(rng)
        need(r.tensor_hash(named)==sharedhash,"FORK_RESTORE")
    scores={"control":baseline,"shared":shared}
    for arm in ("new_only","replay"):
        restore();step_range(plans2[arm][32:]);scores[arm]=eval_fresh(model,tok,oldrows,newrows,out,arm)
    restore();need(r.tensor_hash(frozen)==m["frozen_base_sha"],"BASE_CHANGED")
    report=dict(status="EXPLORATORY_CUMULATIVE_COMPLETE",first_block_reproduced=True,first_block_updates=128,second_block_updates=96,steps_per_candidate_second_block=64,scores=scores,retention={k:a.retention(baseline["old"],scores[k]["old"],scores[k]["new"]) for k in ("shared","new_only","replay")},replay_budget={k:v for k,v in replaybudget.items() if k!="plans"},seconds=time.monotonic()-started,independent_curator=False,final_exam_consumed=False,promotion_authorized=False,weights_published=False)
    save(out,"result.json",report);print(json.dumps(report,indent=2))
if __name__=="__main__":
    q=argparse.ArgumentParser()
    for k in ("budget","plan","original","result","out"):q.add_argument("--"+k,required=True)
    v=q.parse_args();run(v.budget,v.plan,v.original,v.result,v.out)
