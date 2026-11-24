"""Freeze before inference; inference receives only questions and revision pins."""
import argparse
import json
import re
from pathlib import Path
import time
from capacity01_contract import MODELS,VIEWS,create,validate,question,digest,sha,score

def freeze(out):
    from huggingface_hub import HfApi
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    rows=create();validate(rows)
    pins={}
    for arm,(model,rev) in MODELS.items():
        full=HfApi().model_info(model,revision=rev).sha
        if not full or not re.fullmatch("[0-9a-f]{40}",full) or not full.startswith(rev): raise ValueError("REVISION_RESOLUTION")
        pins[arm]={"model":model,"revision":full}
    for name,data in (("labels",rows),("questions",[{"id":r["id"],"packet":r["packet"]} for r in rows]),("pins",pins)):
        (out/(name+".json")).write_text(json.dumps(data,sort_keys=True,separators=(",",":")))
    m={k+"_sha":sha(out/(k+".json")) for k in ("labels","questions","pins")}
    (out/"manifest.json").write_text(json.dumps(m,indent=2))
    print("CAPACITY_FREEZE",json.dumps(dict(m,pins=pins)),flush=True)
    return m

def infer(questions,pins_path,questions_sha,pins_sha,arm,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    if sha(questions)!=questions_sha or sha(pins_path)!=pins_sha: raise ValueError("FROZEN_DIGEST")
    pins=json.loads(Path(pins_path).read_text());rows=json.loads(Path(questions).read_text())
    if len(rows)!=32 or len({r["id"] for r in rows})!=32 or any(set(r)!={"id","packet"} for r in rows): raise ValueError("QUESTIONS_ONLY")
    model_id,rev=pins[arm]["model"],pins[arm]["revision"]
    if model_id!=MODELS[arm][0] or not rev.startswith(MODELS[arm][1]): raise ValueError("MODEL_PIN")
    torch.set_num_threads(2);torch.manual_seed(20261130)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).to("cpu").eval()
    if model.config._commit_hash!=rev: raise ValueError("REVISION")
    candidate={k:tok.encode(k,add_special_tokens=False) for k in ("Yes","No")}
    binary=all(len(ids)==1 and tok.decode(ids,skip_special_tokens=False)==k for k,ids in candidate.items())
    with Path(out).open("x") as log:
        for view in VIEWS:
            for r in rows:
                p=question(r["packet"],view)
                chat=tok.apply_chat_template([{"role":"user","content":p}],tokenize=False,add_generation_prompt=True)
                inputs=tok(chat,return_tensors="pt",add_special_tokens=False)
                if inputs["input_ids"].shape[1]+8>384: raise ValueError("CONTEXT")
                start=time.monotonic()
                with torch.inference_mode():
                    y=n=None
                    if binary:
                        probs=torch.softmax(model(**inputs).logits[0,-1].float(),dim=0)
                        y=float(probs[candidate["Yes"][0]]);n=float(probs[candidate["No"][0]])
                    ids=model.generate(**inputs,do_sample=False,max_new_tokens=8,pad_token_id=tok.eos_token_id)[0,inputs["input_ids"].shape[1]:].tolist()
                raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                rec=dict(arm=arm,view=view,id=r["id"],revision=rev,prompt=p,prompt_sha256=digest(p),raw=raw,raw_sha256=digest(raw),
                         token_ids=ids,input_tokens=int(inputs["input_ids"].shape[1]),output_tokens=len(ids),p_yes=y,p_no=n,seconds=time.monotonic()-start)
                log.write(json.dumps(rec)+"\n");log.flush()
            print("CAPACITY_INFER",arm,view,flush=True)

def finish(labels,pins_path,labels_sha,pins_sha,pred135,pred360,out):
    if sha(labels)!=labels_sha or sha(pins_path)!=pins_sha: raise ValueError("FROZEN_DIGEST")
    rows=json.loads(Path(labels).read_text());pins=json.loads(Path(pins_path).read_text())
    records=[]
    for path in (pred135,pred360): records.extend(json.loads(s) for s in Path(path).read_text().splitlines())
    report=score(rows,records,pins)
    report.update(pins=pins,labels_sha256=labels_sha,prediction_sha256={"135m":sha(pred135),"360m":sha(pred360)})
    with Path(out).open("x") as f: json.dump(report,f,indent=2)
    print("CAPACITY_RESULT",json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    f=sub.add_parser("freeze");f.add_argument("--out",required=True)
    i=sub.add_parser("infer")
    for k in ("questions","pins","questions-sha","pins-sha","arm","out"): i.add_argument("--"+k,required=True)
    s=sub.add_parser("score")
    for k in ("labels","pins","labels-sha","pins-sha","pred135","pred360","out"): s.add_argument("--"+k,required=True)
    a=p.parse_args()
    if a.cmd=="freeze":
        import os
        m=freeze(a.out)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"],"a") as f:
                for k,v in m.items(): f.write(k+"="+v+"\n")
    elif a.cmd=="infer": infer(a.questions,a.pins,a.questions_sha,a.pins_sha,a.arm,a.out)
    else: finish(a.labels,a.pins,a.labels_sha,a.pins_sha,a.pred135,a.pred360,a.out)
