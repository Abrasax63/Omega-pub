"""Free generation on public questions; labels absent from this stage."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from membership_sft_contract import MODEL,REV,MAX_LENGTH,sha,chat,question

def infer(questions,expected,training,out,arm):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    training=Path(training)
    m=json.loads((training/"manifest.json").read_text())
    if m["status"]!="ACTUAL_PAIRLOSS_TRAINED" or m["steps"]!=128 or m["arm"]!=arm or m["model"]!=MODEL or m["revision"]!=REV or m["weight_delta_L2"]<=0:
        raise ValueError("TRAIN_MANIFEST")
    for name,h in m["adapter_sha256"].items():
        if Path(name).name!=name or sha(training/"adapter"/name)!=h:
            raise ValueError("ADAPTER_DIGEST")
    if sha(questions)!=expected:
        raise ValueError("QUESTIONS_DIGEST")
    rows=json.loads(Path(questions).read_text())
    if len(rows)!=64 or len({r["id"] for r in rows})!=64 or any(set(r)!={"id","packet"} for r in rows):
        raise ValueError("QUESTIONS_ONLY")
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,
                        torch_dtype=torch.float32).to("cpu").eval()
    if model.config._commit_hash!=REV:
        raise ValueError("MODEL_REVISION")
    candidate={k:tok.encode(k,add_special_tokens=False) for k in ("Yes","No")}
    binary=all(len(ids)==1 and tok.decode(ids,skip_special_tokens=False)==k for k,ids in candidate.items())
    model=PeftModel.from_pretrained(model,training/"adapter",is_trainable=False).eval()
    with Path(out).open("x") as log:
        for arm in (arm,):
            for view in ("edges","matrix"):
                for r in rows:
                    prompt=chat(tok,r["packet"],view)
                    inputs=tok(prompt,return_tensors="pt",add_special_tokens=False)
                    if inputs["input_ids"].shape[1]+8>MAX_LENGTH:
                        raise ValueError("EVAL_CONTEXT_LIMIT")
                    start=time.monotonic()
                    with torch.inference_mode():
                        p_yes=p_no=None
                        if binary:
                            probs=torch.softmax(model(**inputs).logits[0,-1].float(),dim=0)
                            p_yes=float(probs[candidate["Yes"][0]])
                            p_no=float(probs[candidate["No"][0]])
                        ids=model.generate(**inputs,do_sample=False,max_new_tokens=8,
                            pad_token_id=tok.eos_token_id)[0,inputs["input_ids"].shape[1]:].tolist()
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                    rec={"arm":arm,"view":view,"id":r["id"],"raw":raw,"token_ids":ids,
                         "input_tokens":int(inputs["input_ids"].shape[1]),"output_tokens":len(ids),
                         "seconds":time.monotonic()-start,"p_yes":p_yes,"p_no":p_no,
                         "prompt_sha256":hashlib.sha256(question(r["packet"],view).encode()).hexdigest()}
                    log.write(json.dumps(rec)+"\n")
                    log.flush()
                print("PAIRLOSS_INFERENCE_COMPLETE",arm,view,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ("questions","sha","training","out","arm"):
        p.add_argument("--"+n,required=True)
    a=p.parse_args()
    infer(a.questions,a.sha,a.training,a.out,a.arm)
