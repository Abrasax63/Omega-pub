"""PRETRAINED12: bounded technical check on pinned Qwen500, not a learning trial.
Two actual LoRA optimizer updates on one training pair; no dev/holdout or promotion.
"""
import argparse, json, math, time
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import loop09 as l
import runner11 as r

def need(ok,msg):
    if not ok:raise ValueError(msg)

def smoke(out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model,PeftModel
    torch.set_num_threads(2);torch.manual_seed(t.SEED)
    started=time.monotonic()
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    need(base.config._commit_hash==c.REV,"MODEL_PIN")
    base.config.use_cache=False
    model=get_peft_model(base,t.lora_config())
    named=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
    params=[p for _,p in named]
    frozen=[(n,p) for n,p in model.named_parameters() if not p.requires_grad]
    need(named and all("lora_" in n for n,_ in named) and all(p.device.type=="cpu" for p in params),"ADAPTER_SCOPE")
    initial=r.tensor_hash(named);basehash=r.tensor_hash(frozen)
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.0)
    # One deterministic pair from the existing train split only.
    train=c.build("train",t.SEED);c.validate(train,"train")
    pairs=c.groups(train);key=sorted(p for p,z in pairs.items() if z[0]["kind"]=="membership")[0]
    a,b=pairs[key]
    encoded={a["id"]:t.encode(tok,a,b["gold"]),b["id"]:t.encode(tok,b,a["gold"])}
    batch=t.collate(tok,encoded,[a["id"],b["id"]])
    probe=batch["input_ids"][0:1,:24]
    def logits(m):
        m.eval()
        with torch.inference_mode():
            return m(input_ids=probe,use_cache=False).logits[:,-1,:].detach().clone()
    old=logits(model)
    events=[]
    def step(x):
        stats=t.optimizer_step(model,opt,params,x,"contrastive")
        need(all(math.isfinite(v) for v in stats.values()),"FINITE_STEP")
        h=r.tensor_hash(named);need(h!=initial,"NO_ACTUAL_UPDATE")
        events.append(dict(stats=stats,transient_adapter_sha=h))
        return stats
    # Explicitly synthetic transaction decisions, not measured competence.
    before={k:dict(correct=16,both_pairs=4) for k in c.KINDS}
    bad={k:dict(v) for k,v in before.items()};bad["copy"]["correct"]=15
    good={k:dict(v) for k,v in before.items()};good["select"]=dict(correct=18,both_pairs=5)
    seq=iter((before,bad))
    rejected=l.reversible_block(model,opt,params,[batch],step,lambda:next(seq))
    need(rejected["rolled_back"] and r.tensor_hash(named)==initial and not opt.state,"ROLLBACK")
    rollback_logits=logits(model)
    need(torch.equal(old,rollback_logits),"ROLLBACK_LOGITS")
    seq=iter((before,good))
    accepted=l.reversible_block(model,opt,params,[batch],step,lambda:next(seq))
    final=r.tensor_hash(named)
    need(not accepted["rolled_back"] and final!=initial and r.tensor_hash(frozen)==basehash,"UPDATE_OR_FROZEN_BASE")
    out=Path(out);out.mkdir(exist_ok=False)
    files=r.save_adapter(model,out/"adapter")
    expected=logits(model)
    # Reuse the unchanged base to bound RAM; unload without merging.
    unwrapped=model.unload()
    restored=PeftModel.from_pretrained(unwrapped,out/"adapter",is_trainable=False)
    actual=logits(restored)
    diff=float((expected-actual).abs().max())
    need(torch.allclose(expected,actual,atol=1e-6,rtol=1e-6),"RELOAD_LOGITS")
    # Names and frozen-base tensors are unchanged across the adapter reload.
    ref_names={n for n,_ in frozen}
    restored_frozen=[(n,p) for n,p in restored.named_parameters() if n in ref_names]
    need(len(restored_frozen)==len(frozen) and r.tensor_hash(restored_frozen)==basehash,"RELOAD_BASE_HASH")
    report=dict(status="PINNED_QWEN_TECHNICAL_SMOKE_OK",model=c.MODEL,revision=c.REV,trainable_parameters=sum(p.numel() for p in params),optimizer_updates=2,rejected_updates=1,retained_test_updates=1,initial_adapter_sha=initial,final_adapter_sha=final,base_sha=basehash,rollback_exact=True,rollback_logits_exact=True,reload_max_logit_diff=diff,frozen_base_unchanged=True,adapter_sha256=files,events=events,seconds=time.monotonic()-started,decisions_source="synthetic transaction controls",dev_examples=0,holdout_examples=0,learning_demonstrated=False,training_campaign_authorized=False,promotion_authorized=False)
    r.json_write(out/"report.json",report);print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args();smoke(a.out)
