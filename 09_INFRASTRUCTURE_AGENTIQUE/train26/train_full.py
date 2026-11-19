#!/usr/bin/env python3
"""TRAIN26 actual complete-data, two-epoch LoRA CPU adaptation.

Only TRAIN_FROZEN is opened; NO holdout, labels or oracle case files are
referenced. 640 optimizer steps = 320 distinct examples × 2 complete epochs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time
import traceback

from data_guard import load_training,MODEL,MODEL_REV,SEED,SYSTEM,PINS

N_SAMPLES=320
EPOCHS=2
STEPS=640
MAX_LENGTH=384
LR=0.0005
RANK=8
ALPHA=16
TARGET_MODULES=["q_proj","v_proj"]


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def main_train(output:Path)->dict:
    import torch
    import transformers
    import peft
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model

    begin=time.monotonic()
    output.mkdir(parents=True,exist_ok=True)
    torch.manual_seed(SEED)
    random.seed(SEED)
    torch.set_num_threads(2)
    training=load_training()
    if len(training)!=N_SAMPLES:
        raise ValueError("REGISTERED_CORPUS_SIZE_MISMATCH")

    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REV,
                                            trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    model.config.use_cache=False
    model=get_peft_model(model,LoraConfig(
        r=RANK,lora_alpha=ALPHA,lora_dropout=0.0,bias="none",
        target_modules=TARGET_MODULES,task_type="CAUSAL_LM"
    ))
    trained={name:p for name,p in model.named_parameters() if p.requires_grad}
    if not trained:
        raise AssertionError("NO_LORA_TRAINABLE_PARAMETERS")
    baseline={name:p.detach().clone().cpu() for name,p in trained.items()}
    n_trainable=sum(p.numel() for p in trained.values())
    n_total=sum(p.numel() for p in model.parameters())
    optimizer=torch.optim.AdamW(trained.values(),lr=LR,weight_decay=0.0)

    losses=[]
    lengths=[]
    exposures={}
    model.train()
    for epoch in range(EPOCHS):
        order=list(range(N_SAMPLES))
        random.Random(SEED+epoch).shuffle(order)
        if len(set(order))!=N_SAMPLES:
            raise AssertionError("MISSING_CORPUS_EXPOSURES")
        for pos,index in enumerate(order):
            sample=training[index]
            exposures[sample["id"]]=exposures.get(sample["id"],0)+1
            prefix=tokenizer.apply_chat_template(
                [{"role":"system","content":SYSTEM},
                 {"role":"user","content":sample["prompt"]}],
                tokenize=False,add_generation_prompt=True
            )
            prompt_ids=tokenizer(prefix,add_special_tokens=False)["input_ids"]
            target_ids=tokenizer(sample["target"]+tokenizer.eos_token,
                                 add_special_tokens=False)["input_ids"]
            length=len(prompt_ids)+len(target_ids)
            if length>MAX_LENGTH:
                raise ValueError("TRAIN26_SEQUENCE_EXCEEDS_PREREG_384:"
                                 +str(sample["id"])+":"+str(length))
            tokens=torch.tensor([prompt_ids+target_ids],dtype=torch.long)
            labels=torch.tensor([[-100]*len(prompt_ids)+target_ids],dtype=torch.long)
            optimizer.zero_grad(set_to_none=True)
            loss=model(input_ids=tokens,labels=labels).loss
            if not bool(torch.isfinite(loss)):
                raise ValueError("NONFINITE_LOSS_STEP_"+str(len(losses)+1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trained.values(),1.0)
            optimizer.step()
            losses.append(float(loss.detach().item()))
            lengths.append(length)
            if len(losses)==1 or len(losses)%20==0 or len(losses)==STEPS:
                print("TRAIN26_STEP",len(losses),"epoch",epoch+1,
                      "loss",round(losses[-1],5),"tokens",length,flush=True)

    if len(losses)!=STEPS or len(exposures)!=N_SAMPLES or any(
        v!=EPOCHS for v in exposures.values()
    ):
        raise AssertionError("INCOMPLETE_TWO_FULL_EPOCHS")
    delta_squared=sum(
        float(torch.sum((p.detach().cpu()-baseline[name]).float()**2).item())
        for name,p in trained.items()
    )
    delta_l2=delta_squared**0.5
    if not delta_l2>0:
        raise AssertionError("ADAPTER_WEIGHTS_UNCHANGED")

    folder=output/"adapter"
    model.save_pretrained(str(folder),safe_serialization=True)
    saved={p.name:sha256_file(p) for p in folder.iterdir() if p.is_file()}
    if not any(name.endswith(".safetensors") for name in saved):
        raise AssertionError("ADAPTER_NOT_SAVED")
    manifest={
        "experiment":"OMEGA_TRAIN26_REASONING_CORRECTION_SUPERVISED",
        "status":"TRAINED_ACTUAL_WEIGHTS_CHANGED",
        "training_data_git_blob":PINS["TRAIN_FROZEN.json"],
        "model":MODEL,"model_revision":MODEL_REV,
        "seed":SEED,"steps":len(losses),"epochs":EPOCHS,
        "unique_examples_seen":len(exposures),
        "examples_seen_exactly_twice":sum(v==2 for v in exposures.values()),
        "trainable_parameters":n_trainable,
        "total_parameters":n_total,
        "adapter_delta_L2":delta_l2,
        "optimizer":"AdamW","learning_rate":LR,
        "rank":RANK,"alpha":ALPHA,"dropout":0.0,
        "modules":TARGET_MODULES,"max_tokens":MAX_LENGTH,
        "token_length_min":min(lengths),"token_length_max":max(lengths),
        "token_length_mean":sum(lengths)/len(lengths),
        "loss_step1":losses[0],"loss_step640":losses[-1],
        "mean_loss_epoch1":sum(losses[:N_SAMPLES])/N_SAMPLES,
        "mean_loss_epoch2":sum(losses[N_SAMPLES:])/N_SAMPLES,
        "losses_all_steps":losses,
        "elapsed_training_s":round(time.monotonic()-begin,3),
        "torch_version":torch.__version__,
        "transformers_version":transformers.__version__,
        "peft_version":peft.__version__,
        "saved_adapter_sha256":saved,
        "holdout_seen_by_trainer":False,
        "model_creativity_demonstrated":False,
        "qwen3b_weights_unchanged":True,
        "paid_api_calls":0,
        "auto_promotion":0,
    }
    (output/"train_manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRAIN26_COMPLETE","delta",delta_l2,
          "parameters",n_trainable,"steps",len(losses),
          "unique",len(exposures),flush=True)
    return manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        main_train(args.output)
    except Exception:
        args.output.mkdir(parents=True,exist_ok=True)
        incident={"status":"INDETERMINATE_TRAINING_TECHNICAL_FAILURE",
                  "error":traceback.format_exc(),
                  "auto_promotion":0,
                  "real_training_complete":False}
        (args.output/"failure.json").write_text(
            json.dumps(incident,ensure_ascii=False,indent=2)+"\n")
        print("TRAIN26_TECHNICAL_FAILURE",incident["error"],flush=True)
        raise SystemExit(1)


if __name__=="__main__":
    main()
