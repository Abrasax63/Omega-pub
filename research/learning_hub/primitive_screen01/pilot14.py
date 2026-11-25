"""PILOT14: matched-budget exploratory learning; no deployment or final exam.
Each arm isolated. Candidate weights stay in temporary runner storage.
Public fixed pilot cohort is distinct from training/dev but not independent.
"""
import argparse, copy, hashlib, json, math, tempfile, time
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import loop09 as l
import runner11 as r
import transfer13 as x

ARMS=("base","supervised","contrastive","adaptive")
PILOT_SEED=2026112514
FORM="pilot14"
BUDGET_FIELDS=("actual_input_tokens","gold_target_tokens","foil_target_tokens")
def need(ok,msg):
    if not ok:raise ValueError(msg)
def write(p,obj):r.json_write(p,obj)
def load(p):return json.loads(Path(p).read_text())
def plan_audit(tok,budget_file):
    b=load(budget_file)
    need(b["status"]=="REAL_DEV_BUDGET_AUDITED" and b["dev_run"]==45658613634,"SOURCE")
    need(b["dev_label_sha"]=="566397279e96838b119dbac29f0b5c4569331b66d8d01036c289e9faebf34444" and b["dev_predictions_sha"]=="62ee2a83732c2aa38caeb1dde87be449bfb4032e421162bcbee713c5a96b83eb","DEV_HASH")
    tr=c.build("train",t.SEED);c.validate(tr,"train")
    enc=t.prepare(tok,tr)
    expected={k:c.schedule(tr,k,1234) for k in ("supervised","contrastive")}
    expected["adaptive"],_=l.match(tr,enc,b["dev_pair_errors"])
    need(expected==b["plans"],"PLAN_PROVENANCE")
    # Same paired batches/order for CE and margin arm: isolate loss, not batching.
    expected["supervised"]=copy.deepcopy(expected["contrastive"])
    expected["supervised"]["strategy"]="supervised"
    budgets={k:t.budget(enc,p) for k,p in expected.items()}
    need(budgets==b["budgets"],"BUDGET_PROVENANCE")
    for k,p in expected.items():r.checked_plan(tok,tr,p,budgets[k])
    need(all(l.within(tuple(v[f] for f in BUDGET_FIELDS),tuple(budgets["supervised"][f] for f in BUDGET_FIELDS)) for v in budgets.values()),"TOKEN_MATCH")
    return tr,enc,expected,budgets
def pilot_questions():
    rows=x.make(PILOT_SEED,FORM)
    return [{"id":v["id"],"prompt":v["prompt"]} for v in rows]
def evaluate_pilot(model,tok,questions,out):
    import torch
    need(len(questions)==256 and len({q["id"] for q in questions})==256 and all(set(q)=={"id","prompt"} for q in questions),"QUESTION_ONLY")
    model.eval();start=time.monotonic()
    with Path(out).open("x") as f:
        for i,q in enumerate(questions):
            prompt=tok.apply_chat_template([{"role":"user","content":q["prompt"]}],tokenize=False,add_generation_prompt=True)
            inp=tok(prompt,return_tensors="pt",add_special_tokens=False);n=inp["input_ids"].shape[1]
            need(n+16<=t.MAX_LENGTH,"CONTEXT")
            with torch.inference_mode():ids=model.generate(**inp,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            f.write(json.dumps(dict(id=q["id"],prompt_sha=r.digest(q["prompt"]),raw=raw))+"\n");f.flush()
            if (i+1)%32==0:print("PILOT14 transfer",i+1,"/256",flush=True)
    return time.monotonic()-start
def run(arm,budget_file,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model,PeftModel
    need(arm in ARMS,"ARM")
    out=Path(out);out.mkdir(exist_ok=False);torch.set_num_threads(2);torch.manual_seed(t.SEED)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    tr,enc,plans,budgets=plan_audit(tok,budget_file)
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    need(model.config._commit_hash==c.REV,"MODEL_PIN");model.config.use_cache=False
    report=dict(arm=arm,model=c.MODEL,revision=c.REV,budget_file_sha=r.sha(budget_file),seed=t.SEED,scope="exploratory public-seed transfer, same-author, not qualification",promotion_authorized=False)
    if arm=="base":
        report.update(optimizer_updates=0,transfer_seconds=evaluate_pilot(model,tok,pilot_questions(),out/"predictions.jsonl"))
    else:
        model=get_peft_model(model,t.lora_config())
        named=[(n,p) for n,p in model.named_parameters() if p.requires_grad];params=[p for n,p in named]
        frozen=[(n,p) for n,p in model.named_parameters() if not p.requires_grad]
        need(named and all("lora_" in n for n,p in named),"PARAM_SCOPE")
        initial=r.tensor_hash(named);base_hash=r.tensor_hash(frozen)
        opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.0)
        dev=c.build("dev",t.SEED+1);plan=plans[arm];batches=[t.collate(tok,enc,z) for z in plan["batches"]]
        observations=[];nsteps=0;start=time.monotonic()
        with tempfile.TemporaryDirectory(prefix="omega-pilot14-") as tmp:
            checkpoint=Path(tmp)/"candidate"
            def ev():
                scores,records=r.evaluate_dev(model,tok,dev)
                write(out/("dev-%d.json"%len(observations)),records)
                observations.append(scores)
                if len(observations)==2:
                    need(r.tensor_hash(named)!=initial,"NO_ADAPTER_CHANGE")
                    r.save_adapter(model,checkpoint)
                return scores
            def step(batch):
                nonlocal nsteps
                stats=t.optimizer_step(model,opt,params,batch,arm);nsteps+=1
                need(all(math.isfinite(v) for v in stats.values()),"NONFINITE")
                if nsteps%8==0:print("PILOT14",arm,nsteps,"/128",stats,flush=True)
                return stats
            tx=l.reversible_block(model,opt,params,batches,step,ev)
            need(nsteps==128 and r.tensor_hash(frozen)==base_hash,"UPDATE_INTEGRITY")
            final=r.tensor_hash(named)
            if tx["rolled_back"]:need(final==initial and not opt.state,"ROLLBACK")
            else:need(final!=initial,"NO_ACCEPTED_UPDATE")
            files={p.name:r.sha(p) for p in checkpoint.iterdir() if p.is_file()}
            # Test the frozen experimental candidate even if rejected on dev;
            # it cannot be promoted, and transfer scores never affect training.
            base=model.unload()
            candidate=PeftModel.from_pretrained(base,checkpoint,is_trainable=False)
            report.update(optimizer_updates=nsteps,trainable_parameters=sum(p.numel() for p in params),budget=budgets[arm],initial_adapter_sha=initial,final_transaction_adapter_sha=final,frozen_base_sha=base_hash,candidate_files_sha=files,transaction=tx,train_and_dev_seconds=time.monotonic()-start,transfer_seconds=evaluate_pilot(candidate,tok,pilot_questions(),out/"predictions.jsonl"),candidate_retained_for_deployment=False)
    report["predictions_sha"]=r.sha(out/"predictions.jsonl")
    write(out/"manifest.json",report)
def score(root,out):
    root=Path(root);rows=x.make(PILOT_SEED,FORM);scores={};reports={}
    for arm in ARMS:
        p=root/("pilot14-"+arm);m=load(p/"manifest.json");pred=p/"predictions.jsonl"
        need(m["arm"]==arm and m["revision"]==c.REV and r.sha(pred)==m["predictions_sha"],"ARTIFACT")
        need(m["optimizer_updates"]==(0 if arm=="base" else 128),"STEPS")
        scores[arm]=x.score(rows,[json.loads(v) for v in pred.read_text().splitlines()])
        reports[arm]=m
    need(len({m["budget_file_sha"] for m in reports.values()})==1,"BUDGET_SOURCE")
    need(reports["supervised"]["budget"]==reports["contrastive"]["budget"],"CONTROL_BUDGET")
    need(len({reports[k]["initial_adapter_sha"] for k in ARMS[1:]})==1,"SAME_INIT")
    need(len({reports[k]["frozen_base_sha"] for k in ARMS[1:]})==1,"SAME_BASE")
    comparisons={k:x.compare(scores["base"],scores[k]) for k in ARMS[1:]}
    obj=dict(status="EXPLORATORY_PILOT_COMPLETE",scores=scores,comparisons=comparisons,dev_decisions={k:reports[k]["transaction"]["verdict"] for k in ARMS[1:]},budgets={k:reports[k]["budget"] for k in ARMS[1:]},training_seconds={k:reports[k]["train_and_dev_seconds"] for k in ARMS[1:]},independent_curator=False,final_exam_consumed=False,cumulative_multiblock_tested=False,promotion_authorized=False,adapter_weights_published=False)
    write(out,obj);print(json.dumps(obj,indent=2))
def selftest():
    q=pilot_questions();need(len(q)==256 and all(set(v)=={"id","prompt"} for v in q),"QUESTIONS")
    rows=x.make(PILOT_SEED,FORM);need(x.score(rows,[dict(id=v["id"],prompt_sha=r.digest(v["prompt"]),raw=v["gold"]) for v in rows])["membership"]["both_pairs"]==32,"ORACLE")
    print("PILOT14 offline controls passed")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","run","score"]);p.add_argument("--arm",choices=ARMS);p.add_argument("--budget");p.add_argument("--out");p.add_argument("--root");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="run":run(a.arm,a.budget,a.out)
    else:score(a.root,a.out)
