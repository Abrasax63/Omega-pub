"""EQUIV-DIAG01: read-only inference, isolated contexts, no optimizer."""
import argparse, hashlib, json, math, time
from pathlib import Path

ARMS=("base","ordinary","contrast","process")
SEED=318079423
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def require(x,msg):
    if not x: raise ValueError(msg)
def load_questions(path):
    rows=read(path)
    require(len(rows)==448 and len({x["id"] for x in rows})==448,"coverage")
    for x in rows:
        require(set(x)=={"id","prompt","prompt_sha256"} and sha(x["prompt"].encode())==x["prompt_sha256"],"question contract")
    return rows
def run(qfile,out,arm,adapter_dir=None):
    import torch
    from peft import PeftModel
    import equiv_real01 as old
    import equiv_pilot_freeze as pilot
    torch.set_num_threads(2)
    rows=load_questions(qfile)
    tok=old.tokenizer()
    yes,no=old.candidates(tok)
    def is_binary(x): return "Answer exactly Yes or No." in x["prompt"]
    def budget(x): return 8 if is_binary(x) else 64
    # Tokenize every item before any forward pass. No truncation, no retry.
    prepared=[]
    for r in rows:
        prompt=r["prompt"]
        s=tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True)
        x=tok(s,return_tensors="pt",add_special_tokens=False)
        n=x["input_ids"].shape[1]
        require(n+budget(r)<=1024,"context budget exceeded")
        prepared.append((r,x,n))
    m=old.real_model()
    manifest=None
    if arm!="base":
        require(adapter_dir is not None,"missing adapter")
        manifest=old.verify_adapter(adapter_dir,"real",arm)
        m=PeftModel.from_pretrained(m,Path(adapter_dir)/"adapter",is_trainable=False)
    else: require(adapter_dir is None,"unexpected adapter")
    m.requires_grad_(False);m.eval()
    require(not any(p.requires_grad for p in m.parameters()),"weights not frozen")
    records=[];start=time.monotonic()
    with torch.inference_mode():
        for r,x,n in prepared:
            binary=is_binary(r)
            p=None
            if binary:
                logits=m(**x,use_cache=False).logits[0,-1]
                p=float(torch.softmax(logits[[yes,no]].float(),dim=0)[0])
                require(math.isfinite(p) and 0<=p<=1,"nonfinite binary probability")
            ids=m.generate(**x,do_sample=False,max_new_tokens=budget(r),pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            records.append(dict(id=r["id"],raw=raw,prompt_sha256=sha(r["prompt"].encode()),p_yes_binary=p,ids=ids,input_tokens=n,output_tokens=len(ids),budget=budget(r),budget_reached=len(ids)==budget(r)))
            if len(records)%32==0: print("DIAG_PROGRESS",arm,len(records),448,flush=True)
    require(len(records)==448,"incomplete inference")
    out=Path(out);out.mkdir()
    (out/"predictions.json").write_text(json.dumps(records,indent=2))
    (out/"inference-manifest.json").write_text(json.dumps(dict(arm=arm,model=pilot.MODEL,revision=pilot.REV,adapter_hashes=manifest["adapter_hashes"] if manifest else None,question_sha256=sha(Path(qfile).read_bytes()),rows=len(records),elapsed_seconds=time.monotonic()-start,weights_frozen=True,training_updates=0),indent=2))
def extra(frozen,predfile):
    frozen=Path(frozen);labels=read(frozen/"labels.json");qs=load_questions(frozen/"questions.json");rec=read(predfile)
    require(len(rec)==448 and len({r["id"] for r in rec})==448,"coverage")
    lookup={x["id"]:x for x in rec}; qmap={x["id"]:x for x in qs}
    groups={}
    for l in labels:
        r=lookup[l["id"]]
        require(r["prompt_sha256"]==qmap[l["id"]]["prompt_sha256"],"prompt hash")
        require(type(r["input_tokens"]) is int and 0<r["input_tokens"] and r["input_tokens"]+r["budget"]<=1024 and len(r["ids"])==r["output_tokens"]<=r["budget"],"token trace")
        binary=isinstance(l["truth"],str)
        require(r["budget"]==(8 if binary else 64),"budget")
        g=groups.setdefault(l["task"]+"/"+l["view"],dict(n=0,format_valid=0,binary_correct=0,binary_ties=0,budget_reached=0,pairs={}))
        g["n"]+=1;g["budget_reached"]+=r["budget_reached"]
        if binary:
            p=r["p_yes_binary"];require(type(p) in (int,float) and math.isfinite(p) and 0<=p<=1,"binary trace")
            g["format_valid"]+=r["raw"] in ("Yes","No")
            hit=(p>.5)==(l["truth"]=="Yes");g["binary_correct"]+=hit;g["binary_ties"]+=p==.5
            g["pairs"].setdefault(l["pair"],[]).append(hit)
        else:
            require(r["p_yes_binary"] is None,"unexpected probability")
            try:
                v=json.loads(r["raw"])
                valid=isinstance(v,list) and len(v)==2 and all(isinstance(a,list) and all(isinstance(t,str) for t in a) and len(set(a))==len(a) for a in v)
            except (ValueError,TypeError):valid=False
            g["format_valid"]+=valid
    for k,g in groups.items():
        pairs=g.pop("pairs")
        g["binary_pairs_both"]=sum(all(p) for p in pairs.values()) if pairs else None
        if not pairs:g["binary_correct"]=g["binary_ties"]=None
    return groups
if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    i=sub.add_parser("infer");i.add_argument("questions");i.add_argument("out");i.add_argument("arm",choices=ARMS);i.add_argument("--adapter")
    s=sub.add_parser("extra");s.add_argument("frozen");s.add_argument("predictions");a=p.parse_args()
    if a.cmd=="infer":run(a.questions,a.out,a.arm,a.adapter)
    else: print(json.dumps(extra(a.frozen,a.predictions),indent=2))
