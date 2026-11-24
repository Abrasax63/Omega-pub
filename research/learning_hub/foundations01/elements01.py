"""ELEMENTS-01: frozen base diagnostic; no training or holdout access."""
import argparse
from collections import Counter
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random
import time
from proposal02 import digits_for
from proposal_pilot import MODEL,REV

SEED=20261128
def digest(s): return sha256(s.encode()).hexdigest()

def tasks():
    rng=random.Random(SEED)
    rows=[]
    for i in range(16):
        nodes=rng.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),4)
        x,y=rng.sample(nodes,2)
        all_edges=list(itertools.product(nodes,repeat=2))
        rng.shuffle(all_edges)
        bg={e for e in all_edges if e!=(x,y) and rng.getrandbits(1)}
        for truth in (0,1):
            es=bg|({(x,y)} if truth else set())
            packet={"nodes":nodes,"edges":[list(e) for e in all_edges if e in es]}
            prompt=("In the following directed relation, does the ordered edge "+x+" to "+y+
                    " exist? Output exactly one digit: 1 for yes, 0 for no. "+
                    json.dumps(packet,separators=(",",":")))
            rows.append(dict(id=f"M{i:02d}-{truth}",kind="membership",pair=i,truth=truth,prompt=prompt))
    for i in range(8):
        a,b,c=map(int,format(i,"03b"))
        prompt=(f"For a distinct ordered triple x,y,z, the presence bits of directed edges "
                f"x to y, y to z, and x to z are respectively {a}, {b}, {c}. "
                "Does this triple violate transitivity? Output exactly one digit: 1 for yes, 0 for no.")
        rows.append(dict(id=f"L{i}",kind="logic",truth=int(a and b and not c),prompt=prompt))
    return rows

def summarize(rows,records):
    keys={(a,r["id"]) for a in ("free","binary") for r in rows}
    if len(records)!=len(keys) or {(r["arm"],r["id"]) for r in records}!=keys:
        raise ValueError("COVERAGE")
    byid={r["id"]:r for r in rows}
    report={}
    for arm in ("free","binary"):
        scores={}
        hits={}
        for kind in ("membership","logic"):
            counts=Counter()
            outputs=Counter()
            for r in records:
                task=byid[r["id"]]
                if r["arm"]!=arm or task["kind"]!=kind: continue
                if r["prompt_sha256"]!=digest(task["prompt"]) or r["raw_sha256"]!=digest(r["raw"]):
                    raise ValueError("DIGEST")
                valid=r["raw"] in ("0","1")
                if arm=="binary" and (not valid or len(r["token_ids"])!=1):
                    raise ValueError("BINARY_CONTRACT")
                if len(r["token_ids"])>8 or not 0<=r["allowed_mass"]<=1.000001:
                    raise ValueError("TRACE")
                hit=valid and int(r["raw"])==task["truth"]
                hits[r["id"]]=hit
                c=str(task["truth"])
                counts["n"]+=1
                counts["valid"]+=int(valid)
                counts["correct"]+=int(hit)
                counts["n_"+c]+=1
                counts["correct_"+c]+=int(hit)
                outputs[r["raw"] if valid else "INVALID"]+=1
            s=dict(counts)
            s["outputs"]=dict(outputs)
            if kind=="membership":
                s["pairs_both_correct"]=sum(hits[f"M{i:02d}-0"] and hits[f"M{i:02d}-1"] for i in range(16))
                s["signal"]=s["correct"]>=24 and s["pairs_both_correct"]>=10
            else:
                s["by_motif"]={format(i,"03b"):hits[f"L{i}"] for i in range(8)}
                s["balanced_accuracy"]=(s["correct_0"]/s["n_0"]+s["correct_1"]/s["n_1"])/2
                s["signal"]=s["correct_1"]==1 and s["correct_0"]>=5
            scores[kind]=s
        report[arm]=scores
    return {"arms":report,"weight_updates":0,"promotion_authorized":False,"holdout_accessed":False}

def run(output):
    import torch
    import transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,
                    torch_dtype=torch.float32).to("cpu").eval()
    if model.config._commit_hash!=REV: raise ValueError("REVISION")
    digits=digits_for(tok)
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    rows=tasks()
    (out/"diagnostic_tasks.json").write_text(json.dumps(rows,indent=2))
    records=[]
    with (out/"raw.jsonl").open("x") as log:
        for task in rows:
            text=tok.apply_chat_template([{"role":"user","content":task["prompt"]}],
                      tokenize=False,add_generation_prompt=True)
            inputs=tok(text,return_tensors="pt",add_special_tokens=False)
            with torch.inference_mode():
                logits=model(**inputs).logits[0,-1].float()
                probs=torch.softmax(logits,dim=0)
                p0,p1=(float(probs[digits[k]]) for k in "01")
            for arm in ("free","binary"):
                start=time.monotonic()
                if arm=="free":
                    with torch.inference_mode():
                        ids=model.generate(**inputs,do_sample=False,max_new_tokens=8,
                            pad_token_id=tok.eos_token_id)[0,inputs["input_ids"].shape[1]:].tolist()
                else:
                    ids=[digits["1" if p1>p0 else "0"]]
                raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                rec=dict(arm=arm,id=task["id"],raw=raw,raw_sha256=digest(raw),
                    prompt_sha256=digest(task["prompt"]),token_ids=ids,allowed_mass=p0+p1,
                    p0=p0,p1=p1,input_tokens=int(inputs["input_ids"].shape[1]),
                    seconds=time.monotonic()-start)
                log.write(json.dumps(rec)+"\n");log.flush();records.append(rec)
            print("ELEMENTS01",task["id"],flush=True)
    report=summarize(rows,records)
    report.update(model=MODEL,revision=REV,transformers=transformers.__version__,
        torch=torch.__version__,digit_token_ids=digits,raw_sha256=sha256((out/"raw.jsonl").read_bytes()).hexdigest(),
        limitation="Binary decision shares the first forward pass; timing not a matched compute comparison.")
    (out/"report.json").write_text(json.dumps(report,indent=2))
    print("ELEMENTS_RESULT",json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args();run(a.output)
