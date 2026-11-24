"""Bounded real proposal feasibility experiment, no training or holdout."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
from corpus_gate import identities, motif, MOTIFS
from proposer import PROMPT, collect

MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"
N=32
SEED=20261124
MAX_NEW=192

def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def summarize(rows, sensor):
    if len(rows)!=N or [r["seed"] for r in rows]!=list(range(SEED,SEED+N)):
        raise ValueError("INCOMPLETE_OR_DUPLICATE_ATTEMPTS")
    for r in rows:
        if r["raw_sha256"]!=digest(r["raw"]) or r["prompt_sha256"]!=digest(PROMPT):
            raise ValueError("RAW_OR_PROMPT_DIGEST_MISMATCH")
        if len(r["output_token_ids"])!=r["output_tokens"] or not 0<=r["output_tokens"]<=MAX_NEW:
            raise ValueError("TOKEN_BUDGET_MISMATCH")
    admitted=collect([r["raw"] for r in rows],sensor)
    counts=Counter({m:0 for m in MOTIFS})
    graphs=set()
    for r in admitted["accepted"]:
        packet=json.loads(rows[r["proposal_index"]]["raw"])
        counts[motif(packet)]+=1
        graphs.add(identities(packet)[0])
    unique=len(admitted["accepted"])
    signal=unique>=16 and sum(v>0 for v in counts.values())>=4 and counts["110"]>=4
    return {"status":"EXPLORATORY_PROPOSAL_FEASIBILITY_SIGNAL" if signal else "PROPOSAL_FEASIBILITY_NOT_DEMONSTRATED",
            "accepted_unique":unique,"unique_graphs":len(graphs),"motifs":dict(counts),
            "rejection_counts":dict(Counter(r["reason"] for r in admitted["rejected"])),
            "accepted":admitted["accepted"],"rejected":admitted["rejected"],
            "input_tokens":sum(r["input_tokens"] for r in rows),
            "output_tokens":sum(r["output_tokens"] for r in rows),
            "training_authorized":False,"weight_updates":0,"holdout_accessed":False}

def run(output):
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import omega_hybrid_exact_sensor as sensor
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    raw_path=output/"raw.jsonl"
    # Do not overwrite a partial or complete run.
    with raw_path.open("x",encoding="utf-8") as log:
        torch.set_num_threads(2)
        tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
        model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,
            trust_remote_code=False,torch_dtype=torch.float32).to("cpu").eval()
        if model.config._commit_hash != REV:
            raise ValueError("MODEL_REVISION_NOT_CONFIRMED")
        rendered=tok.apply_chat_template([{"role":"user","content":PROMPT}],
            tokenize=False,add_generation_prompt=True)
        inputs=tok(rendered,return_tensors="pt",add_special_tokens=False)
        rows=[]
        for i in range(N):
            seed=SEED+i
            torch.manual_seed(seed)
            started=time.monotonic()
            with torch.inference_mode():
                out=model.generate(**inputs,max_new_tokens=MAX_NEW,do_sample=True,
                    temperature=0.8,top_p=0.95,top_k=0,pad_token_id=tok.eos_token_id)
            ids=out[0,inputs["input_ids"].shape[1]:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True)
            row={"seed":seed,"raw":raw,"raw_sha256":digest(raw),
                 "prompt_sha256":digest(PROMPT),"rendered_prompt_sha256":digest(rendered),
                 "input_tokens":int(inputs["input_ids"].shape[1]),"output_tokens":len(ids),
                 "output_token_ids":ids,"seconds":round(time.monotonic()-started,3)}
            log.write(json.dumps(row,ensure_ascii=False)+"\n")
            log.flush()
            rows.append(row)
            print("PROPOSAL",i+1,"of",N,"tokens",len(ids),flush=True)
    report=summarize(rows,sensor)
    report.update(model=MODEL,revision=REV,torch=torch.__version__,
        transformers=transformers.__version__,attempts=N,raw_file_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest())
    (output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(report["status"],"unique",report["accepted_unique"],"motifs",report["motifs"],flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
