"""Actual supervised CPU LoRA, training artifact only."""
import argparse
import json
from collections import Counter
from pathlib import Path
import random
import time
import math
from atomic_sft_contract import MODEL,REV,SEED,MAX_LENGTH,sha,read_frozen,chat,target

def train(path,expected,out):
    import torch
    import transformers
    import peft
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import LoraConfig,get_peft_model
    out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    rows=read_frozen(path,expected,"train")
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,
                                            torch_dtype=torch.float32).to("cpu")
    if base.config._commit_hash!=REV:
        raise ValueError("MODEL_REVISION")
    base.config.use_cache=False
    model=get_peft_model(base,LoraConfig(r=8,lora_alpha=16,lora_dropout=0.0,bias="none",
                      target_modules=["q_proj","v_proj"],task_type="CAUSAL_LM"))
    params={k:v for k,v in model.named_parameters() if v.requires_grad}
    if not params:
        raise ValueError("NO_TRAINABLE_WEIGHTS")
    before={k:v.detach().clone() for k,v in params.items()}
    opt=torch.optim.AdamW(params.values(),lr=0.0005,weight_decay=0.0)
    model.train()
    seen=Counter()
    losses=[]
    exposures=0
    supervised=0
    with (out/"steps.jsonl").open("x") as log:
        for epoch in range(2):
            order=list(range(len(rows)))
            random.Random(SEED+epoch).shuffle(order)
            for i in order:
                r=rows[i]
                prefix=tok(chat(tok,r["packet"],"edges"),add_special_tokens=False)["input_ids"]
                suffix=tok(target(r["label"])+tok.eos_token,add_special_tokens=False)["input_ids"]
                if len(prefix)+len(suffix)>MAX_LENGTH or not suffix:
                    raise ValueError("CONTEXT_LIMIT")
                x=torch.tensor([prefix+suffix],dtype=torch.long)
                labels=torch.tensor([[-100]*len(prefix)+suffix],dtype=torch.long)
                opt.zero_grad(set_to_none=True)
                loss=model(input_ids=x,labels=labels).loss
                if not bool(torch.isfinite(loss)):
                    raise ValueError("NONFINITE_LOSS")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params.values(),1.0,error_if_nonfinite=True)
                opt.step()
                seen[r["id"]]+=1
                losses.append(float(loss.detach()))
                exposures+=len(prefix)+len(suffix)
                supervised+=len(suffix)
                log.write(json.dumps({"step":len(losses),"id":r["id"],"loss":losses[-1],
                                      "tokens":len(prefix)+len(suffix),"target_tokens":len(suffix)})+"\n")
                log.flush()
                if len(losses)%16==0:
                    print("ATOMIC_SFT_STEP",len(losses),"/256",losses[-1],flush=True)
    if len(losses)!=256 or len(seen)!=128 or set(seen.values())!={2}:
        raise ValueError("INCOMPLETE_TRAINING")
    delta=math.sqrt(sum(torch.sum((v.detach()-before[k])**2).item() for k,v in params.items()))
    if not math.isfinite(delta) or delta<=0:
        raise ValueError("WEIGHT_DELTA")
    adapter=out/"adapter"
    model.save_pretrained(adapter,safe_serialization=True)
    hashes={p.name:sha(p) for p in adapter.iterdir() if p.is_file()}
    if "adapter_model.safetensors" not in hashes:
        raise ValueError("MISSING_ADAPTER")
    m={"status":"ACTUAL_SUPERVISED_LORA_TRAINED","model":MODEL,"revision":REV,"seed":SEED,
       "train_sha256":expected,"steps":256,"examples":128,"epochs":2,"weight_delta_L2":delta,
       "trainable_parameters":sum(v.numel() for v in params.values()),"token_exposures":exposures,
       "supervised_token_exposures":supervised,"loss_first":losses[0],"loss_last":losses[-1],
       "adapter_sha256":hashes,"steps_sha256":sha(out/"steps.jsonl"),
       "torch":torch.__version__,"transformers":transformers.__version__,"peft":peft.__version__,
       "seconds":time.monotonic()-start,"autonomous":False,"promotion_authorized":False}
    (out/"manifest.json").write_text(json.dumps(m,indent=2))
    print("ATOMIC_SFT_COMPLETE",json.dumps(m),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--train",required=True)
    p.add_argument("--sha",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    train(a.train,a.sha,a.out)
