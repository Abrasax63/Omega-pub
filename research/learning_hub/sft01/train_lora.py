"""OMEGA-PY-SFT-01: actual CPU LoRA update for a separate Python repair task.

Adapts the already validated TRAIN26 recipe (same SmolLM2, pinned stack,
q_proj/v_proj LoRA, supervised causal labels, CPU AdamW, exact weight delta).
The TRAIN26 script itself expects mathematical EXPR labels and is not used.
NO HOLDOUT IMPORT, FILE ACCESS, MODEL EVALUATION OR AUTO-PROMOTION HERE.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import time
import traceback

from data_guard import (load_train,MODEL,MODEL_REV,SEED,SYSTEM,
                        EPOCHS,LR,RANK,ALPHA,MAX_LENGTH,PINS)

def hashfile(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for data in iter(lambda:f.read(1<<20),b""):
            h.update(data)
    return h.hexdigest()


def train(output):
    import torch
    import transformers
    import peft
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import LoraConfig,get_peft_model

    start=time.monotonic()
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    random.seed(SEED)
    samples=load_train()
    tok=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REV,
                                       trust_remote_code=False)
    if tok.pad_token_id is None:
        tok.pad_token=tok.eos_token
    base=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    base.config.use_cache=False
    model=get_peft_model(base,LoraConfig(
        r=RANK,lora_alpha=ALPHA,lora_dropout=0.0,bias="none",
        target_modules=["q_proj","v_proj"],task_type="CAUSAL_LM"))
    trainable={k:v for k,v in model.named_parameters() if v.requires_grad}
    if not trainable:
        raise AssertionError("NO_PARAMETERS_TO_TRAIN")
    before={k:v.detach().cpu().clone() for k,v in trainable.items()}
    opt=torch.optim.AdamW(trainable.values(),lr=LR,weight_decay=0.0)
    model.train()
    losses=[]
    lengths=[]
    seen=Counter()
    for epoch in range(EPOCHS):
        order=list(range(len(samples)))
        random.Random(SEED+epoch).shuffle(order)
        for index in order:
            row=samples[index]
            seen[row["id"]]+=1
            prefix=tok.apply_chat_template(
                [{"role":"system","content":SYSTEM},
                 {"role":"user","content":row["prompt"]}],
                tokenize=False,add_generation_prompt=True)
            prompt_ids=tok(prefix,add_special_tokens=False)["input_ids"]
            target_ids=tok(row["target"]+tok.eos_token,
                           add_special_tokens=False)["input_ids"]
            length=len(prompt_ids)+len(target_ids)
            if length>MAX_LENGTH:
                raise ValueError("TOKEN_BUDGET_EXCEEDED_"+row["id"]+"_"+str(length))
            ids=torch.tensor([prompt_ids+target_ids],dtype=torch.long)
            labels=torch.tensor([[-100]*len(prompt_ids)+target_ids],dtype=torch.long)
            opt.zero_grad(set_to_none=True)
            loss=model(input_ids=ids,labels=labels).loss
            if not bool(torch.isfinite(loss)):
                raise ValueError("NONFINITE_LOSS")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable.values(),1.0)
            opt.step()
            losses.append(float(loss.detach().item()))
            lengths.append(length)
            if len(losses)==1 or len(losses)%16==0 or len(losses)==len(samples)*EPOCHS:
                print("OMEGA_PY_SFT_STEP",len(losses),"of",len(samples)*EPOCHS,
                      "loss",round(losses[-1],5),"tokens",length,flush=True)
    nsteps=len(samples)*EPOCHS
    if (len(losses)!=nsteps or len(seen)!=len(samples) or
        any(v!=EPOCHS for v in seen.values())):
        raise AssertionError("INCOMPLETE_TRAINING_OR_MISSING_EXPOSURES")
    delta=float(sum(
        torch.sum((v.detach().cpu()-before[k]).float()**2).item()
        for k,v in trainable.items()))**0.5
    if not delta>0:
        raise AssertionError("WEIGHTS_DID_NOT_CHANGE")
    adapter=output/"adapter"
    model.save_pretrained(str(adapter),safe_serialization=True)
    sha={f.name:hashfile(f) for f in adapter.iterdir() if f.is_file()}
    if not any(name.endswith(".safetensors") for name in sha):
        raise AssertionError("NO_SAVED_ADAPTER")
    manifest={
        "experiment":"OMEGA-PY-SFT-01","status":"ACTUAL_LORA_WEIGHTS_TRAINED",
        "model":MODEL,"model_revision":MODEL_REV,
        "source_train_git_blob_sha1":PINS["TRAIN_FROZEN.json"],
        "training_examples":len(samples),
        "synthetic_teacher_examples":sum(x["provenance"].startswith("CURATED_")
                                         for x in samples),
        "previously_verified_omega_examples":sum(x["provenance"].startswith("OMEGA_")
                                                   for x in samples),
        "epochs":EPOCHS,"steps":nsteps,"unique_examples_seen":len(seen),
        "all_examples_seen_twice":all(v==EPOCHS for v in seen.values()),
        "learning_rate":LR,"rank":RANK,"alpha":ALPHA,"seed":SEED,
        "max_context_tokens":MAX_LENGTH,
        "trainable_parameters":sum(v.numel() for v in trainable.values()),
        "total_parameters":sum(v.numel() for v in model.parameters()),
        "weight_delta_L2":delta,
        "loss_first":losses[0],"loss_last":losses[-1],
        "losses_all_steps":losses,
        "tokens_min":min(lengths),"tokens_max":max(lengths),
        "training_wall_seconds":round(time.monotonic()-start,3),
        "safetensor_sha256":sha,
        "pytorch":torch.__version__,"transformers":transformers.__version__,
        "peft":peft.__version__,
        "holdout_loaded_by_training_script":False,
        "qwen3b_weights_modified":False,
        "new_scientific_theorem_proved":False,
        "programming_generalization_demonstrated":False,
        "automatic_omega_promotion":False,
        "paid_api_calls":0,
    }
    (output/"train_manifest.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("OMEGA_PY_SFT_TRAIN_COMPLETE","updates",nsteps,
          "delta_l2",delta,"last_loss",losses[-1],flush=True)
    return manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        train(args.output)
    except Exception:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/"train_failure.json").write_text(
            json.dumps({"status":"INDETERMINATE_TECHNICAL_FAILURE",
                        "traceback":traceback.format_exc(),
                        "actual_training_confirmed":False},indent=2))
        raise


if __name__=="__main__":
    main()
