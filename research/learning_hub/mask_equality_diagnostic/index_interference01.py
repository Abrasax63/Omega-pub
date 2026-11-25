"""Paired copy versus index construction at three frozen checkpoints."""
import argparse,json,random,re,time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import copy_sft01 as c
import copy_transfer02 as ct
import copy_to_position01 as cp
import position_cumulative01 as pc
import position_representation as pos
import position_depth01 as depth
import instruction_control01 as ic
import self_representation as sr1
import self_representation02 as sr2
import self_representation03 as sr3
import self_index_cumulative01 as si
import readout02 as rd
import format_skill as fs
import foundational_readout as fr
ARMS=("base","copy","cumulative")
OPS=("copy","index")
def corpus():
    rng=random.Random(202611250825)
    t,e=c.make()
    assert c.digest(c.canonical(t))=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert c.digest(c.canonical(e))=="34e02262decf0576b69930ef652b0a08c66a14bf827026b59719ebbb6b03b19a"
    excluded={tuple(r["packet"].split()) for r in t+e}
    excluded.update(tuple(r["seq"].split()) for r in ct.corpus())
    for mod in (cp,pos,sr1,sr2,sr3,rd,fs):
        excluded.update(tuple(r["seq"]) for r in mod.corpus())
    for r in fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:excluded.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    excluded.update(tuple(r["seq"].split()) for r in t+e)
    for mod,h in ((ic,"def2f1d550f7ba84c2340fdb3f03c52310ec74b84ae6e6c14b53dbe02580699c"),(depth,"db067e67e4747730cc5a12e9892c75fcee6b05c35b512000401b3c0e3cec14e7"),(si,"d6432ac68869dffb04902ddf36c1ebb3dc3a9643ea9bdd1760b993a5556ae794")):
        rows=mod.corpus();assert c.digest(c.canonical(rows))==h
        excluded.update(tuple(r["seq"].split() if isinstance(r["seq"],str) else r["seq"]) for r in rows)
    rows=[]
    for n in (3,4,8):
        for _ in range(8):
            for attempt in range(10000):
                s=tuple(rng.sample(list("ABCDEFGH"),n))
                if s not in excluded:break
            else:raise RuntimeError("exhausted")
            excluded.add(s)
            seq=list(s)
            rows.append(dict(id=c.digest(c.canonical(seq))[:24],n=n,seq=seq))
    rng.shuffle(rows)
    assert len(rows)==24 and len({r["id"] for r in rows})==24
    return rows
def prompt(r,op):
    return c.question(" ".join(r["seq"]),"trained") if op=="copy" else sr2.prompt(r["seq"],"B")
def classify(raw,r):
    s=r["seq"];v=raw.strip()
    if v==" ".join(s):return "copy"
    if v==pos.encode(s,"indexed"):return "index_exact"
    if sr1.parse(v,len(s)) is not None:
        return "index_faithful_spacing" if sr1.parse(v,len(s))==s else "index_unfaithful"
    return "other"
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==144 and {(r["arm"],r["op"],r["id"]) for r in records}=={(a,o,i) for a in ARMS for o in OPS for i in by}
    hits={}
    for r in records:
        q=by[r["id"]]
        assert r["prompt_sha256"]==c.digest(prompt(q,r["op"]).encode())
        hits[r["arm"],r["op"],r["id"]]=classify(r["raw"],q)
    scores={}
    for arm in ARMS:
        scores[arm]={}
        for n in (3,4,8):
            for op in OPS:
                rr=[r for r in records if r["arm"]==arm and r["op"]==op and by[r["id"]]["n"]==n]
                assert len(rr)==8
                counts=Counter(hits[arm,op,r["id"]] for r in rr)
                scores[arm][f"{n}_{op}"]=dict(counts=dict(counts),exact=counts["copy" if op=="copy" else "index_exact"],tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    short=[r["id"] for r in rows if r["n"] in (3,4)]
    contrasts={}
    for arm in ("copy","cumulative"):
        pairs=Counter(f"{hits['base','index',i]}->{hits[arm,'index',i]}" for i in short)
        loss=sum(hits["base","index",i]=="index_exact" for i in short)-sum(hits[arm,"index",i]=="index_exact" for i in short)
        substitution=sum(hits[arm,"index",i]=="copy" for i in short)-sum(hits["base","index",i]=="copy" for i in short)
        retention=sum(hits[arm,"copy",i]=="copy" for i in short)
        contrasts[arm]=dict(loss=loss,copy_increase=substitution,copy_control=retention,paired=dict(pairs),interference_gate=loss>=4 and substitution>=4 and retention>=15)
    return dict(scores=scores,contrasts=contrasts,training=False,promotion_authorized=False)
def run(old,new,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False)
    (out/"corpus.json").write_bytes(c.canonical(rows))
    print("INTERFERENCE_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=pc.load(old);new=Path(new)
    m=json.loads((new/"manifest.json").read_text())
    assert m["adapter_sha256"]["adapter_model.safetensors"]==ic.NEW and m["old_adapter_sha256"]==pc.OLD and m["steps"]==256
    assert m["train_sha256"]=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    for k,h in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,Path(old)/"adapter",adapter_name="copy",is_trainable=False)
    model.load_adapter(new/"adapter",adapter_name="cumulative",is_trainable=False)
    model.eval();model.config.use_cache=True
    records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ARMS:
            model.set_adapter("copy" if arm=="base" else arm);model.requires_grad_(False)
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in rows:
                    for op in OPS:
                        q=prompt(r,op);p=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
                        x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];start=time.monotonic()
                        with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                        raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                        rec=dict(arm=arm,op=op,id=r["id"],raw=raw,prompt_sha256=c.digest(q.encode()),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
                        records.append(rec);log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush()
            print("INTERFERENCE_STAGE",arm,len(records),flush=True)
    result=score(rows,records);result["corpus_sha256"]=c.sha_file(out/"corpus.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print("INDEX_INTERFERENCE_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--old");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=corpus()
        for r in rows:
            assert classify(" ".join(r["seq"]),r)=="copy"
            assert classify(pos.encode(r["seq"],"indexed"),r)=="index_exact"
            assert prompt(r,"copy")!=prompt(r,"index")
        print("INTERFERENCE_CHECK",len(rows),c.digest(c.canonical(rows)))
    else:run(a.old,a.new,a.out)
