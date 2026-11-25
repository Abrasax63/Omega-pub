"""Fresh transfer cohort, frozen COPY-SFT01 adapter, no gradient."""
import argparse,hashlib,json,random,re,time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import copy_sft01 as prior
def corpus():
    t,e=prior.make()
    assert prior.digest(prior.canonical(t))=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert prior.digest(prior.canonical(e))=="34e02262decf0576b69930ef652b0a08c66a14bf827026b59719ebbb6b03b19a"
    seen={r["packet"] for r in t+e};rng=random.Random(202611250637);rows=[]
    for group,alphabet,lengths in [("new","ABCDEFGH",(3,4)),("long","ABCDEFGH",(7,8)),("new_alphabet","QRSTUVWXYZ",(3,4)),("digits","0123456789",(3,4))]:
        for n in lengths:
            for _ in range(8):
                for attempt in range(10000):
                    seq=" ".join(rng.choice(alphabet) for i in range(n))
                    if seq not in seen:break
                else:raise RuntimeError("duplicate")
                seen.add(seq);rows.append(dict(id=prior.digest(seq.encode())[:24],seq=seq,group=group,alphabet=alphabet,n=n))
    rng.shuffle(rows);assert len(rows)==64 and len(seen)==336 and len({r["id"] for r in rows})==64
    assert set(Counter(r["group"] for r in rows).values())=={16}
    return rows
def prompt(seq,view):
    if view=="brackets":return "Return the symbols between the brackets, in exactly the same order and separated by single spaces. Do not include brackets. ["+seq+"]"
    if view=="verbatim":return "Transcribe this sequence verbatim, preserving every symbol and single space. Sequence: "+seq
    raise ValueError(view)
def sep_only(raw,r):
    if not re.fullmatch("["+r["alphabet"]+r"\s_,;:\-]+",raw):return False
    return re.sub(r"[\s_,;:\-]","",raw)==r["seq"].replace(" ","")
def run(adapter,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False);(out/"corpus.json").write_bytes(prior.canonical(rows))
    print("TRANSFER_CORPUS",prior.sha_file(out/"corpus.json"),flush=True)
    adapter=Path(adapter);manifest=json.loads((adapter/"manifest.json").read_text())
    assert manifest["train_sha256"]=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert manifest["steps"]==256 and manifest["model"]==prior.MODEL and manifest["revision"]==prior.REV
    assert prior.sha_file(adapter/"adapter"/"adapter_model.safetensors")=="1015e47946deaad5a3ab9f072f16a30d116bbf111c2b1fc2cb5ea6f8bb5d0fef"
    for k,h in manifest["adapter_sha256"].items():assert prior.sha_file(adapter/"adapter"/k)==h
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(prior.MODEL,revision=prior.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(prior.MODEL,revision=prior.REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==prior.REV
    model=PeftModel.from_pretrained(base,adapter/"adapter",is_trainable=False).eval();model.config.use_cache=True
    assert not any(p.requires_grad for p in model.parameters())
    scores={};records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","lora"):
            scores[arm]={}
            with model.disable_adapter() if arm=="base" else nullcontext():
                for view in ("brackets","verbatim"):
                    scores[arm][view]={}
                    for r in rows:
                        q=prompt(r["seq"],view)
                        p=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
                        x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
                        start=time.monotonic()
                        with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                        raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                        rec=dict(arm=arm,view=view,id=r["id"],raw=raw,prompt_sha256=prior.digest(q.encode()),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
                        log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush();records.append(rec)
                        s=scores[arm][view].setdefault(r["group"],dict(n=0,exact=0,strict=0,separator_only=0,input_tokens=0,output_tokens=0,seconds=0))
                        s["n"]+=1;s["exact"]+=int(raw.strip()==r["seq"]);s["strict"]+=int(raw==r["seq"]);s["separator_only"]+=int(sep_only(raw,r))
                        for k in ("input_tokens","output_tokens","seconds"):s[k]+=rec[k]
                    print("TRANSFER_STAGE",arm,view,len(records),flush=True)
    assert len(records)==256 and len({(r["arm"],r["view"],r["id"]) for r in records})==256
    b,l=scores["base"],scores["lora"]
    total=lambda a:sum(s["exact"] for v in a.values() for s in v.values())
    gain=total(l)-total(b)
    gate=gain>=8 and all(sum(s["exact"] for s in l[v].values())>=61 and all(s["exact"]>=15 and s["exact"]>=b[v][g]["exact"]-1 for g,s in l[v].items()) for v in l)
    result=dict(scores=scores,base_exact=total(b),lora_exact=total(l),gain=gain,replication_gate=gate,training=False,promotion_authorized=False,corpus_sha256=prior.sha_file(out/"corpus.json"))
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("COPY_TRANSFER_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--adapter");p.add_argument("--out");a=p.parse_args()
    if a.check:print("TRANSFER_CHECK",len(corpus()),prior.digest(prior.canonical(corpus())))
    else:run(a.adapter,a.out)
