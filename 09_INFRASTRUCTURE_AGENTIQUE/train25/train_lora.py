#!/usr/bin/env python3
"""Actual CPU LoRA update of a small public language model.

This stage imports only TRAIN_FROZEN, not evaluation cases or holdout labels.
No reward-model gaming: fixed seed/order/hyperparameters/steps, no early stopping.
The adapter is a TRAINED formalization component, not a new reasoning theory.
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

from data_guard import MODEL,MODEL_REV,SEED,SYSTEM,validate_train,FROZEN


def checksum(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as source:
        while True:
            v=source.read(1<<20)
            if not v:break
            h.update(v)
    return h.hexdigest()


def train(output:Path):
    import torch
    import transformers
    import peft
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model

    output.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    random.seed(SEED)
    begin=time.monotonic()
    data=validate_train()
    # Data access declaration: this module does not read any holdout file.
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REV,
                                            trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    foundation=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False)
    foundation.config.use_cache=False
    foundation.to("cpu")
    cfg=LoraConfig(r=8,lora_alpha=16,lora_dropout=0.0,
                   bias="none",target_modules=["q_proj","v_proj"],
                   task_type="CAUSAL_LM")
    model=get_peft_model(foundation,cfg)
    learnable={name:p for name,p in model.named_parameters() if p.requires_grad}
    if not learnable:
        raise AssertionError("LORA_NO_TRAINABLE_WEIGHTS")
    before={name:p.detach().clone().cpu() for name,p in learnable.items()}
    trainable_params=sum(p.numel() for p in learnable.values())
    total_params=sum(p.numel() for p in model.parameters())

    optimizer=torch.optim.AdamW(learnable.values(),lr=0.001,weight_decay=0.0)
    losses=[]; sequence_lengths=[]
    order=list(range(len(data)))
    random.Random(SEED).shuffle(order)
    model.train()
    for step in range(24):
        sample=data[order[step]]
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":sample["prompt"]}]
        prefix=tokenizer.apply_chat_template(messages,tokenize=False,
                                              add_generation_prompt=True)
        ids=tokenizer(prefix,add_special_tokens=False)["input_ids"]
        target_ids=tokenizer(sample["target"]+tokenizer.eos_token,
                             add_special_tokens=False)["input_ids"]
        if len(ids)+len(target_ids)>128:
            raise ValueError("TRAIN_SAMPLE_TOKEN_LENGTH_EXCEEDS_PREREG_128")
        tokens=torch.tensor([ids+target_ids],dtype=torch.long)
        labels=torch.tensor([[-100]*len(ids)+target_ids],dtype=torch.long)
        optimizer.zero_grad(set_to_none=True)
        loss=model(input_ids=tokens,labels=labels).loss
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_LOSS")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(learnable.values(),1.0)
        optimizer.step()
        losses.append(float(loss.detach().item()))
        sequence_lengths.append(int(tokens.shape[1]))
        print("TRAIN25_STEP",step+1,"loss",round(losses[-1],5),
              "n_tokens",sequence_lengths[-1],flush=True)

    after_delta=sum(float(torch.sum((p.detach().cpu()-before[name]).float()**2).item())
                    for name,p in learnable.items())
    after_delta=after_delta**0.5
    if not after_delta>0:
        raise AssertionError("NO_ACTUAL_WEIGHT_CHANGE")
    adapter=output/"adapter"
    model.save_pretrained(str(adapter),safe_serialization=True)
    files=[x for x in adapter.iterdir() if x.is_file()]
    if not any(x.name.endswith(".safetensors") for x in files):
        raise AssertionError("MISSING_SAVED_LORA_SAFETENSORS")
    manifest={
        "experiment":"OMEGA_TRAIN25_ACTUAL_CPU_LORA",
        "status":"TRAINED_ACTUAL_LORA_PARAMETERS_CHANGED",
        "model_name":MODEL,"model_revision":MODEL_REV,
        "train_data_git_blob":FROZEN["TRAIN_FROZEN.json"],
        "seed":SEED,"steps":24,"learning_rate":0.001,
        "lora_rank":8,"lora_alpha":16,"lora_target_modules":["q_proj","v_proj"],
        "trained_parameters":trainable_params,
        "total_model_parameters_with_adapter":total_params,
        "weight_delta_L2":after_delta,
        "loss_per_step":losses,"sequence_lengths":sequence_lengths,
        "train_wall_seconds":round(time.monotonic()-begin,3),
        "pytorch_version":torch.__version__,
        "transformers_version":transformers.__version__,
        "peft_version":peft.__version__,
        "adapter_file_sha256":{p.name:checksum(p) for p in files},
        "source_weights_qwen3b_modified":False,
        "holdout_read_by_training_script":False,
        "independent_creativity_demonstrated":False,
        "automatic_scientific_promotions":0,
        "paid_api_calls":0,
    }
    (output/"train_manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRAIN25_FINISHED",manifest["status"],
          "trainable",trainable_params,"delta_L2",after_delta,flush=True)
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    try:
        train(a.output)
    except Exception:
        report={"status":"INDETERMINATE_INFRA_OR_TRAINING_FAILURE",
                "error":traceback.format_exc(),
                "actual_weights_updated_confirmed":False,
                "automatic_scientific_promotions":0}
        (a.output/"train_failure.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        print(report["status"],report["error"],flush=True)
        raise SystemExit(1)


if __name__=="__main__":
    main()
