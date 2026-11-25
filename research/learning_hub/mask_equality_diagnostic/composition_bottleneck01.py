"""Matched bottleneck probe: selection, independent indexing, direct and mental composition."""
import argparse,json,random,time,itertools,re
from pathlib import Path
from collections import Counter
from contextlib import nullcontext
import composition_pilot01 as cp
import format_index_repl01 as fr
import copy_sft01 as c
import position_cumulative01 as pc
ARMS=("base","parent","pilot")
OPS=("S","I","D","M")
def make():
    rng=random.Random(202611251114);excluded=cp.exclusions()
    prior=cp.make()
    for k,h in (("A","eea900b4663d058dc2f94b909061cab7a1578f330cfa09ca25f42d4ca2c56071"),("B","11185c76eb457d2789231577663b3f23c0a6efcbe234bf78f87d29c5ef90d398")):
        assert c.digest(c.canonical(prior[k]))==h
        excluded.update(tuple(r["seq"]) for r in prior[k])
    data=[]
    for n in (3,4):
        pp=list(itertools.combinations(range(1,n+1),2))
        pp=pp*(8//len(pp))+rng.sample(pp,8%len(pp));rng.shuffle(pp)
        for p,q in pp:
            for _ in range(10000):
                s=tuple(rng.sample(list("ABCDEFGH"),n))
                if s not in excluded:break
            else:raise RuntimeError("corpus exhausted")
            excluded.add(s);data.append((s,p,q))
    targets={tuple(s[i-1] for i in (p,q)) for s,p,q in data}
    targets|={x[::-1] for x in targets}
    # Independent pairs, no target leakage. Prefer unseen pairs in either direction.
    allpairs=[x for x in itertools.combinations("ABCDEFGH",2) if x not in targets and x[::-1] not in targets]
    fresh=[x for x in allpairs if x not in excluded and x[::-1] not in excluded]
    other=[x for x in allpairs if x not in fresh];rng.shuffle(fresh);rng.shuffle(other)
    pool=fresh+other
    # There are at most 28 unordered pairs; independent controls may recur across lists.
    # If target exclusions leave fewer than 16 pairs, reuse a control across lists only.
    assert pool
    rows=[]
    for k,(s,p,q) in enumerate(data):
        independent=pool[k%len(pool)]
        sid=c.digest(c.canonical(s))[:24];seq=" ".join(s)
        for direction,(i,j) in enumerate(((p,q),(q,p))):
            letters=[s[i-1],s[j-1]]
            short=list(independent if direction==0 else independent[::-1])
            assert tuple(short) not in targets
            direct=f"Take the letter at position {i}, then the letter at position {j}, counting from 1. Number the resulting two letters 1 and 2, in that order. Put one space between each number and its letter and one space between pairs. Output only the pairs. Sequence: {seq}"
            for op in OPS:
                if op=="S":
                    inp=list(s);answer=" ".join(letters)
                    prompt=f"Take the letter at position {i}, then the letter at position {j}, counting from 1. Output only the two letters in that order, separated by one space. Sequence: {seq}"
                elif op=="I":
                    inp=short;answer=f"1 {short[0]} 2 {short[1]}";prompt=fr.question(short,1,"space")
                else:
                    inp=list(s);answer=f"1 {letters[0]} 2 {letters[1]}"
                    prompt=direct if op=="D" else "First mentally select the two letters in the requested order. Then mentally number the selected letters from 1. "+direct
                rows.append(dict(id=c.digest(c.canonical([sid,direction,op]))[:24],sid=sid,seq=list(s),input_seq=inp,p=i,q=j,direction=direction,op=op,gold=answer,prompt=prompt,control_seen=(tuple(short) in excluded) if op=="I" else None))
    rng.shuffle(rows)
    assert len(rows)==128 and len({r["id"] for r in rows})==128
    assert Counter(r["op"] for r in rows)=={o:32 for o in OPS}
    assert len({r["sid"] for r in rows})==16
    for sid in {r["sid"] for r in rows}:
        for op in OPS:
            rr=[r for r in rows if r["sid"]==sid and r["op"]==op]
            assert len(rr)==2 and rr[0]["gold"]!=rr[1]["gold"]
    return rows
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==384 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in ARMS for i in by}
    scores={}
    for a in ARMS:
        scores[a]={}
        for o in OPS:
            rr=[r for r in records if r["arm"]==a and by[r["id"]]["op"]==o]
            assert len(rr)==32
            hits=[];pairs={};errors=Counter();colon=0;letters_ok=0
            for r in rr:
                q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                raw=r["raw"].strip();h=raw==q["gold"];hits.append(h);pairs.setdefault(q["sid"],[]).append(h)
                letters=q["input_seq"] if o=="I" else [q["seq"][q["p"]-1],q["seq"][q["q"]-1]]
                alt=f"1:{letters[0]} 2:{letters[1]}"
                faithful=(h or raw==alt) if o!="S" else h
                colon+=o!="S" and raw==alt
                extracted=re.findall(r"(?<![A-Za-z])[A-H](?![A-Za-z])",raw)
                letters_ok+=extracted==letters
                if not h:errors["colon_format" if o!="S" and raw==alt else "letters_only" if o!="S" and raw==" ".join(letters) else "reverse_letters" if extracted==letters[::-1] else "one_letter" if len(extracted)==1 else "other"]+=1
            assert len(pairs)==16 and all(len(x)==2 for x in pairs.values())
            scores[a][o]=dict(exact=sum(hits),pairs=sum(all(x) for x in pairs.values()),colon=colon,letters_correct=letters_ok,errors=dict(errors),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr),local_gate=sum(hits)>=29 and sum(all(x) for x in pairs.values())>=13)
        scores[a]["mental_gain"]=scores[a]["M"]["exact"]-scores[a]["D"]["exact"]
    return dict(scores=scores,control_seen=sum(r["control_seen"] for r in rows if r["op"]=="I"),unique_control_inputs=len({tuple(r["input_seq"]) for r in rows if r["op"]=="I"}),training=False,validation_authorized=False,cohort_B_inferred=False,promotion_authorized=False)
def run(parent,pilot,out):
    rows=make();out=Path(out);out.mkdir(exist_ok=False)
    (out/"corpus.json").write_bytes(c.canonical(rows));print("BOTTLENECK_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=fr.ir.load(parent);pilot=Path(pilot);m=json.loads((pilot/"manifest.json").read_text())
    assert m["adapter_sha256"]["adapter_model.safetensors"]==fr.PILOT and m["parent_sha256"]==fr.ir.PARENT and m["steps"]==72
    for k,h in m["adapter_sha256"].items():assert c.sha_file(pilot/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",adapter_name="parent",is_trainable=False)
    model.load_adapter(pilot/"adapter",adapter_name="pilot",is_trainable=False);model.eval();model.config.use_cache=True
    records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for a in ARMS:
            model.set_adapter("parent" if a=="base" else a);model.requires_grad_(False)
            with model.disable_adapter() if a=="base" else nullcontext():
                for r in rows:
                    p=pc.prefix(tok,r);x=torch.tensor([p]);start=time.monotonic()
                    with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,len(p):].tolist()
                    rec=dict(arm=a,id=r["id"],raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=len(p),output_tokens=len(y),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("BOTTLENECK_STAGE",a,len(records),flush=True)
    result=score(rows,records);result["corpus_sha256"]=c.sha_file(out/"corpus.json")
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print("BOTTLENECK_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--parent");p.add_argument("--pilot");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=make();print("BOTTLENECK_CHECK",len(rows),c.digest(c.canonical(rows)),sum(r["control_seen"] for r in rows if r["op"]=="I"),len({tuple(r["input_seq"]) for r in rows if r["op"]=="I"}))
    else:run(a.parent,a.pilot,a.out)
