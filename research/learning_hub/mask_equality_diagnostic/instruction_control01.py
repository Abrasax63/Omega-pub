"""Matched instruction control probe; frozen adapters, no gradients."""
import argparse,json,random,re,time
from pathlib import Path
from collections import Counter
from contextlib import nullcontext
import copy_sft01 as c
import copy_transfer02 as ct
import copy_to_position01 as cp
import position_cumulative01 as pc
import position_representation as pos
import format_skill as fs
import self_representation as sr1
import self_representation03 as sr3
import readout02 as rd
import foundational_readout as fr
OPS=("KEEP","REMOVE","SELECT")
VIEWS=("V1","V2")
NEW="7d19cacc6df22836a1a553a1522ab2ad91fcf4ef00cece82e1f8cc3b47b26c40"
def prompt(seq,p,op,view):
    q={
      ("KEEP","V1"):"Return the sequence exactly, including both brackets.",
      ("REMOVE","V1"):"Return the sequence exactly, excluding both brackets.",
      ("SELECT","V1"):f"Return only the letter at position {p}, counting the first letter as 1.",
      ("KEEP","V2"):"Transcribe all symbols and the enclosing brackets.",
      ("REMOVE","V2"):"Transcribe the letters and their spaces, but omit the enclosing brackets.",
      ("SELECT","V2"):f"Starting with 1 for the first letter inside the brackets, output only letter number {p}."
    }[op,view]
    return q+" Data: ["+seq+"]"
def corpus():
    rng=random.Random(202611250708);alpha=list("ABCDEFGH")
    t,e=c.make();assert c.digest(c.canonical(t))=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert c.digest(c.canonical(e))=="34e02262decf0576b69930ef652b0a08c66a14bf827026b59719ebbb6b03b19a"
    seen={tuple(r["packet"].split()) for r in t+e}
    tt=ct.corpus();assert c.digest(c.canonical(tt))=="c54d51eb79f8ba3452516cd3fb5ed582991788a04913cbbf6d9ad94e61507650"
    seen.update(tuple(r["seq"].split()) for r in tt)
    cc=cp.corpus();assert c.digest(c.canonical(cp.cases(cc)))=="1fbebe8f52bad503b95fa6753a67a390c8d53e67b562c47983cef91589e2a634"
    for rows in (cc,fs.corpus(),pos.corpus(),sr1.corpus(),sr3.corpus(),rd.corpus()):
        seen.update(tuple(r["seq"]) for r in rows)
    for r in fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:seen.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    seen.update(tuple(r["seq"].split()) for r in t+e);seen.add(tuple("ABCD"))
    rows=[]
    for n in (3,4):
        targets=rng.sample(alpha,8);pp=list(range(n))*(8//n)+rng.sample(range(n),8%n);rng.shuffle(pp)
        for a,p in zip(targets,pp):
            for _ in range(10000):
                s=rng.sample([x for x in alpha if x!=a],n-1);s.insert(p,a)
                if tuple(s) not in seen:break
            else:raise RuntimeError("duplicate")
            seen.add(tuple(s));seq=" ".join(s);g={"KEEP":"["+seq+"]","REMOVE":seq,"SELECT":s[p]}
            assert len(set(g.values()))==3 and s[p]==a
            for view in VIEWS:
                for op in OPS:
                    rows.append(dict(id=c.digest(c.canonical([seq,p,op,view]))[:24],seq=seq,p=p+1,view=view,op=op,gold=g[op],targets=g,prompt=prompt(seq,p+1,op,view)))
    assert len(rows)==96 and len({r["id"] for r in rows})==96 and len({r["seq"] for r in rows})==16
    assert Counter(r["gold"] for r in rows if r["view"]=="V1" and r["op"]=="SELECT")==Counter(alpha*2)
    rng.shuffle(rows);return rows
def content_ok(raw,r):
    # Descriptive only: for KEEP/REMOVE distinguish correct interior and enclosing marks.
    s=raw.strip()
    if r["op"]=="SELECT":return s==r["gold"]
    if s.startswith("[") and s.endswith("]"):s=s[1:-1].strip()
    return s==r["seq"]
def classify(raw,r):
    s=raw.strip()
    for op,g in r["targets"].items():
        if s==g:return op
    return "other"
def score(rows,records):
    by={r["id"]:r for r in rows};arms=("base","copy","cumulative")
    assert len(records)==288 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in arms for i in by}
    scores={}
    for a in arms:
        scores[a]={}
        for v in VIEWS:
            recs=[r for r in records if r["arm"]==a and by[r["id"]]["view"]==v]
            groups={};trips={}
            for op in OPS:
                rr=[r for r in recs if by[r["id"]]["op"]==op];assert len(rr)==16
                confusion=Counter();hits=0;content=0
                for r in rr:
                    q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                    cls=classify(r["raw"],q);h=cls==op;hits+=h;confusion[cls]+=1;content+=content_ok(r["raw"],q)
                    trips.setdefault(q["seq"],[]).append(h)
                groups[op]=dict(n=16,exact=hits,content=content,confusion=dict(confusion),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
            assert len(trips)==16 and all(len(x)==3 for x in trips.values())
            full=sum(all(x) for x in trips.values())
            scores[a][v]=dict(ops=groups,triplets=full,mastery=full>=14 and all(x["exact"]>=15 for x in groups.values()))
    delta={v:{op:scores["cumulative"][v]["ops"][op]["exact"]-scores["copy"][v]["ops"][op]["exact"] for op in OPS} for v in VIEWS}
    transfer={v:any(d[op]>=4 and all(d[o]>=-1 for o in OPS if o!=op) for op in ("SELECT","REMOVE")) for v,d in delta.items()}
    return dict(scores=scores,delta=delta,transfer=transfer,training=False,promotion_authorized=False)
def run(old,new,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False);(out/"corpus.json").write_bytes(c.canonical(rows))
    print("INSTRUCTION_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=pc.load(old);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["old_adapter_sha256"]==pc.OLD and m["steps"]==256 and m["weight_delta_L2"]>0
    assert m["train_sha256"]=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert m["adapter_sha256"]["adapter_model.safetensors"]==NEW
    for k,h in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,Path(old)/"adapter",adapter_name="copy",is_trainable=False)
    model.load_adapter(new/"adapter",adapter_name="cumulative",is_trainable=False);model.eval();model.config.use_cache=True
    records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","copy","cumulative"):
            model.set_adapter("copy" if arm=="base" else arm)
            model.requires_grad_(False)
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in rows:
                    p=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
                    x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];start=time.monotonic()
                    with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                    rec=dict(arm=arm,id=r["id"],raw=raw,prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush()
            print("INSTRUCTION_STAGE",arm,len(records),flush=True)
    result=score(rows,records);result["corpus_sha256"]=c.sha_file(out/"corpus.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("INSTRUCTION_CONTROL_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--old");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=corpus()
        assert all(classify(r["targets"][op],r)==op for r in rows for op in OPS)
        print("INSTRUCTION_CHECK",len(rows),c.digest(c.canonical(rows)))
    else:run(a.old,a.new,a.out)
