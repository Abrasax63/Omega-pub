"""Frozen model probe: sequence extension, depth and indexed representation."""
import argparse,json,random,re,time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import copy_sft01 as c
import copy_transfer02 as ct
import copy_to_position01 as cp
import position_cumulative01 as pc
import position_representation as pos
import instruction_control01 as ic
import format_skill as fs
import self_representation as sr1
import self_representation03 as sr3
import readout02 as rd
import foundational_readout as fr
VIEWS=("spaced","indexed")
def corpus():
    rng=random.Random(202611250745)
    t,e=c.make()
    excluded={tuple(r["packet"].split()) for r in t+e}
    excluded.update(tuple(r["seq"].split()) for r in ct.corpus())
    for mod in (cp,fs,pos,sr1,sr3,rd):
        excluded.update(tuple(r["seq"]) for r in mod.corpus())
    for r in fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:excluded.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    excluded.update(tuple(r["seq"].split()) for r in t+e)
    ii=ic.corpus()
    assert c.digest(c.canonical(ii))=="def2f1d550f7ba84c2340fdb3f03c52310ec74b84ae6e6c14b53dbe02580699c"
    excluded.update(tuple(r["seq"].split()) for r in ii)
    for _ in range(10000):
        a=rng.sample(list("ABCDEFGH"),8)
        rr=rng.sample(range(8),8);cc=rng.sample(range(8),8)
        full=[tuple(a[(i+j)%8] for j in cc) for i in rr]
        allseq=set(full+[s[:4] for s in full])
        if len(allseq)==16 and not allseq&excluded:break
    else:raise RuntimeError("No disjoint Latin square")
    rows=[]
    for i,s in enumerate(full):
        for n,pp in ((4,(2,4)),(8,(2,4,6,8))):
            for p in pp:
                seq=list(s[:n]);g=seq[p-1]
                for v in VIEWS:
                    assert pos.decode(pos.encode(seq,v),v)==seq
                    q=pos.question(dict(seq=seq,p=p),v)
                    rows.append(dict(id=c.digest(c.canonical([i,n,p,v,seq]))[:24],pair=i,seq=seq,n=n,p=p,view=v,gold=g,prompt=q))
    assert len(rows)==96 and len({r["id"] for r in rows})==96
    for n,pp in ((4,(2,4)),(8,(2,4,6,8))):
        for p in pp:
            for v in VIEWS:
                assert Counter(r["gold"] for r in rows if (r["n"],r["p"],r["view"])==(n,p,v))==Counter("ABCDEFGH")
    for i in range(8):
        for p in (2,4):
            assert len({r["gold"] for r in rows if r["pair"]==i and r["p"]==p})==1
    rng.shuffle(rows);return rows
def score(rows,records):
    by={r["id"]:r for r in rows};arms=("base","cumulative")
    assert len(records)==192 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in arms for i in by}
    scores={}
    for arm in arms:
        scores[arm]={}
        for v in VIEWS:
            rr=[r for r in records if r["arm"]==arm and by[r["id"]]["view"]==v]
            groups={};cells={};shifts=Counter()
            for r in rr:
                q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                raw=r["raw"].strip();hit=raw==q["gold"];n,p=q["n"],q["p"]
                k=f"n{n}_p{p}";g=groups.setdefault(k,dict(n=0,exact=0,invalid=0,wrong_in_sequence=0))
                g["n"]+=1;g["exact"]+=hit;g["invalid"]+=int(raw not in list("ABCDEFGH"))
                if not hit and raw in q["seq"]:
                    g["wrong_in_sequence"]+=1;shifts[str(q["seq"].index(raw)+1-p)]+=1
                cells[q["pair"],n,p]=hit
            assert all(x["n"]==8 for x in groups.values())
            short=sum(groups[f"n4_p{p}"]["exact"] for p in (2,4))
            early=sum(groups[f"n8_p{p}"]["exact"] for p in (2,4))
            late=sum(groups[f"n8_p{p}"]["exact"] for p in (6,8))
            matched=Counter()
            for i in range(8):
                for p in (2,4):
                    matched[f"{int(cells[i,4,p])}{int(cells[i,8,p])}"]+=1
            scores[arm][v]=dict(cells=groups,short=short,early=early,late=late,matched_prefixes=dict(matched),wrong_shifts=dict(shifts),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    s=scores["cumulative"]["spaced"];i=scores["cumulative"]["indexed"]
    contrasts=dict(length_loss=s["short"]-s["early"],depth_loss=s["early"]-s["late"],indexed_late_gain=i["late"]-s["late"])
    return dict(scores=scores,contrasts=contrasts,gates={k:v>=4 for k,v in contrasts.items()},training=False,promotion_authorized=False)
def run(old,new,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False);(out/"corpus.json").write_bytes(c.canonical(rows))
    print("DEPTH_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=pc.load(old);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["old_adapter_sha256"]==pc.OLD and m["steps"]==256 and m["weight_delta_L2"]>0
    assert m["train_sha256"]=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert m["adapter_sha256"]["adapter_model.safetensors"]==ic.NEW
    for k,h in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,new/"adapter",is_trainable=False).eval()
    model.config.use_cache=True;model.requires_grad_(False)
    records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","cumulative"):
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in rows:
                    p=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
                    x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];start=time.monotonic()
                    with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                    rec=dict(arm=arm,id=r["id"],raw=raw,prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush()
            print("DEPTH_STAGE",arm,len(records),flush=True)
    result=score(rows,records);result["corpus_sha256"]=c.sha_file(out/"corpus.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("POSITION_DEPTH_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--old");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=corpus();print("DEPTH_CHECK",len(rows),c.digest(c.canonical(rows)))
    else:run(a.old,a.new,a.out)
