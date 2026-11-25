"""RELATION20: reproduce PILOT14 adaptive checkpoint, compare RELATION19.
Only original training examples enter optimizer. No checkpoint publication.
"""
import argparse,json,tempfile,time
from pathlib import Path
from collections import defaultdict
import curriculum06 as c
import trainer07 as t
import runner11 as r
import pilot14 as p
import cumulative18 as a
import relation19 as z

def run(budget,original,result,baseline,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model,PeftModel
    original=Path(original);baseline=Path(baseline);out=Path(out);out.mkdir(exist_ok=False)
    m=a.check_sources(original,result)
    rows=z.build();basepred=a.load(baseline/"predictions.json");base=a.load(baseline/"result.json")
    a.need(base["revision"]==c.REV and base["optimizer_updates"]==0 and z.score(rows,basepred)==base["score"],"BASELINE_SCORE")
    torch.set_num_threads(2);torch.manual_seed(t.SEED)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    train,enc,plans,budgets=p.plan_audit(tok,budget)
    a.need(not {q["prompt"] for q in rows}&{q["prompt"] for q in train},"EXAM_OVERLAP")
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    a.need(model.config._commit_hash==c.REV,"REV");model.config.use_cache=False
    model=get_peft_model(model,t.lora_config())
    named=[(n,w) for n,w in model.named_parameters() if w.requires_grad];params=[w for n,w in named]
    frozen=[(n,w) for n,w in model.named_parameters() if not w.requires_grad]
    a.need(r.tensor_hash(named)==m["initial_adapter_sha"] and r.tensor_hash(frozen)==m["frozen_base_sha"],"INIT")
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.0);dev=c.build("dev",t.SEED+1)
    for j in (0,1):
        if j:
            model.train()
            for i,ids in enumerate(plans["adaptive"]["batches"]):
                t.optimizer_step(model,opt,params,t.collate(tok,enc,ids),"adaptive")
                if (i+1)%16==0:print("RELATION20 reproduction",i+1,"/128",flush=True)
        _,trace=r.evaluate_dev(model,tok,dev)
        a.need(a.rawmap(trace)==a.rawmap(a.load(original/("dev-%d.json"%j))),"DEV_REPRODUCTION")
    a.need(r.tensor_hash(named)==m["final_transaction_adapter_sha"] and r.tensor_hash(frozen)==m["frozen_base_sha"],"TENSOR_REPRODUCTION")
    with tempfile.TemporaryDirectory() as tmp:
        checkpoint=Path(tmp)/"adapter";files=r.save_adapter(model,checkpoint)
        a.need(files["adapter_model.safetensors"]==a.EXPECTED,"FILE_REPRODUCTION")
        unwrapped=model.unload()
        model=PeftModel.from_pretrained(unwrapped,checkpoint,is_trainable=False)
        model.eval();pred=[]
        for i,q in enumerate([{"id":v["id"],"prompt":v["prompt"]} for v in rows]):
            txt=tok.apply_chat_template([{"role":"user","content":q["prompt"]}],tokenize=False,add_generation_prompt=True)
            inp=tok(txt,return_tensors="pt",add_special_tokens=False);n=inp["input_ids"].shape[1]
            with torch.inference_mode():ids=model.generate(**inp,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id,use_cache=False)[0,n:].tolist()
            pred.append(dict(id=q["id"],prompt_sha=z.digest(q["prompt"]),raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)))
            if (i+1)%32==0:print("RELATION20 evaluation",i+1,"/128",flush=True)
    scores=z.score(rows,pred);groups=defaultdict(list)
    for row in rows:groups[row["pair"]].append(row)
    before=a.rawmap(basepred);after=a.rawmap(pred)
    transitions={}
    for kind in ("position","direction"):
        flags=[(all(before[v["id"]].strip()==v["gold"] for v in pair),all(after[v["id"]].strip()==v["gold"] for v in pair)) for pair in groups.values() if pair[0]["kind"]==kind]
        transitions[kind]=dict(gained=sum(not b and c for b,c in flags),lost=sum(b and not c for b,c in flags),both_correct_delta=scores[kind]["both_pairs"]-base["score"][kind]["both_pairs"],correct_delta=scores[kind]["correct"]-base["score"][kind]["correct"])
    report=dict(status="RELATION20_EXPLORATORY_COMPARISON",reproduced_adapter_sha=a.EXPECTED,reproduction_updates=128,new_training_examples=0,baseline=base["score"],candidate=scores,paired_transitions=transitions,scope="public same-author diagnostic, same training seed, no independent qualification",promotion_authorized=False,weights_published=False)
    r.json_write(out/"predictions.json",pred);r.json_write(out/"result.json",report);print(json.dumps(report,indent=2))
if __name__=="__main__":
    q=argparse.ArgumentParser()
    for k in ("budget","original","result","baseline","out"):q.add_argument("--"+k,required=True)
    v=q.parse_args();run(v.budget,v.original,v.result,v.baseline,v.out)
