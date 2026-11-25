"""DEVBASE08: measure actual dev pair errors; no holdout consumption or training."""
import argparse, hashlib, json, time
from pathlib import Path
import curriculum06 as c
import trainer07 as t
SEED=t.SEED
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,sort_keys=True))
def freeze(root):
    root=Path(root);root.mkdir(exist_ok=False)
    rows=c.build("dev",SEED+1);c.validate(rows,"dev")
    write(root/"labels.json",rows)
    write(root/"questions.json",[{k:r[k] for k in ("id","prompt")} for r in rows])
    write(root/"manifest.json",dict(model=c.MODEL,revision=c.REV,questions_sha=sha(root/"questions.json"),labels_sha=sha(root/"labels.json")))
def infer(root,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    root=Path(root);m=json.loads((root/"manifest.json").read_text());q=root/"questions.json"
    need(m["model"]==c.MODEL and m["revision"]==c.REV and sha(q)==m["questions_sha"],"FREEZE")
    rows=json.loads(q.read_text());need(len(rows)==128 and len({r["id"] for r in rows})==128 and all(set(r)=={"id","prompt"} for r in rows),"QUESTIONS_ONLY")
    torch.set_num_threads(2);torch.manual_seed(SEED)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32).eval()
    need(model.config._commit_hash==c.REV,"MODEL_PIN")
    with Path(out).open("x") as f:
        for i,r in enumerate(rows):
            chat=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
            x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            need(n+16<=t.MAX_LENGTH,"CONTEXT_LIMIT");start=time.monotonic()
            with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            z=dict(id=r["id"],revision=c.REV,prompt_sha=digest(r["prompt"]),raw=raw,raw_sha=digest(raw),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
            f.write(json.dumps(z)+"\n");f.flush()
            if (i+1)%16==0:print("DEVBASE08",i+1,"/128",flush=True)
def score(rows,z):
    c.validate(rows,"dev");idx={r["id"]:r for r in rows};seen={}
    for v in z:
        i=v["id"];need(i in idx and i not in seen and v["revision"]==c.REV,"IDENTITY")
        need(v["prompt_sha"]==digest(idx[i]["prompt"]) and v["raw_sha"]==digest(v["raw"]),"HASH")
        need(0<v["input_tokens"]<=t.MAX_LENGTH-16 and 0<=v["output_tokens"]<=16 and v["seconds"]>=0,"BUDGET");seen[i]=v
    need(set(seen)==set(idx),"COVERAGE")
    # Exact autonomous responses only, no semantic extraction or tool answers.
    ok={i:seen[i]["raw"].strip()==r["gold"] for i,r in idx.items()}
    groups=c.groups(rows);scores={}
    for k in c.KINDS:
        rs=[r for r in rows if r["kind"]==k]
        pairs=[p for p in groups.values() if p[0]["kind"]==k]
        d=dict(correct=sum(ok[r["id"]] for r in rs),total=len(rs),both_pairs=sum(all(ok[r["id"]] for r in p) for p in pairs))
        d["pair_errors"]=len(pairs)-d["both_pairs"]
        if k=="membership":d["by_class"]={a:sum(ok[r["id"]] for r in rs if r["gold"]==a) for a in ("Yes","No")}
        if k=="select":d["by_position"]={p:sum(ok[r["id"]] for r in rs if r["pos"]==p) for p in range(1,5)}
        scores[k]=d
    errors={k:d["pair_errors"] for k,d in scores.items()}
    train=c.build("train",SEED)
    plan=c.schedule(train,"adaptive",1234,errors)
    return dict(scores=scores,dev_pair_errors=errors,adaptive_skill_pairs=plan["skill_pairs"],scope="development only, fixed synthetic vocabulary, not independent holdout",input_tokens=sum(v["input_tokens"] for v in z),output_tokens=sum(v["output_tokens"] for v in z),seconds=sum(v["seconds"] for v in z),training_authorized=False)
def finish(root,pred,out):
    root=Path(root);m=json.loads((root/"manifest.json").read_text())
    need(sha(root/"labels.json")==m["labels_sha"],"LABEL_SHA")
    rows=json.loads((root/"labels.json").read_text());need(rows==c.build("dev",SEED+1),"REGEN")
    z=[json.loads(s) for s in Path(pred).read_text().splitlines()];d=score(rows,z);d.update(predictions_sha=sha(pred),labels_sha=m["labels_sha"],revision=c.REV);write(out,d);print(json.dumps(d,indent=2))
def selftest():
    rows=c.build("dev",SEED+1)
    def record(r,raw):return dict(id=r["id"],revision=c.REV,prompt_sha=digest(r["prompt"]),raw=raw,raw_sha=digest(raw),input_tokens=1,output_tokens=1,seconds=0)
    good=[record(r,r["gold"]) for r in rows];d=score(rows,good)
    need(all(v==0 for v in d["dev_pair_errors"].values()),"ORACLE")
    bad=[record(r,"Yes") for r in rows];d=score(rows,bad)
    need(d["scores"]["membership"]["correct"]==16 and d["scores"]["membership"]["both_pairs"]==0 and all(v==16 for v in d["dev_pair_errors"].values()),"CONSTANT")
    for z in (good[:-1],good+[good[0]],[dict(good[0],raw="fake")]+good[1:]):
        try:score(rows,z)
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    print("DEVBASE08 SELFTEST OK")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze","infer","score"]);p.add_argument("--root");p.add_argument("--out");p.add_argument("--pred");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="freeze":freeze(a.root)
    elif a.cmd=="infer":infer(a.root,a.out)
    else:finish(a.root,a.pred,a.out)
