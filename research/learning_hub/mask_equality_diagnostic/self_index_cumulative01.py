"""Compare direct reading, external index, and self-generated index."""
import argparse,json,random,time
from collections import Counter
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
import readout02 as rd
import format_skill as fs
def corpus():
    rng=random.Random(202611250814)
    t,e=c.make();excluded={tuple(r["packet"].split()) for r in t+e}
    excluded.update(tuple(r["seq"].split()) for r in ct.corpus())
    for mod in (cp,pos,sr1,sr2,sr3,rd,fs):
        excluded.update(tuple(r["seq"]) for r in mod.corpus())
    t,e=pc.make();excluded.update(tuple(r["seq"].split()) for r in t+e)
    excluded.update(tuple(r["seq"].split()) for r in ic.corpus())
    d=depth.corpus()
    assert c.digest(c.canonical(d))=="db067e67e4747730cc5a12e9892c75fcee6b05c35b512000401b3c0e3cec14e7"
    excluded.update(tuple(r["seq"]) for r in d)
    for _ in range(10000):
        a=rng.sample(list("ABCDEFGH"),8);rr=rng.sample(range(8),8);cc=rng.sample(range(8),8)
        seqs=[tuple(a[(i+j)%8] for j in cc) for i in rr]
        if len(set(seqs))==8 and not set(seqs)&excluded:break
    else:raise RuntimeError("duplicate corpus")
    rows=[dict(id=c.digest(c.canonical(s))[:24],seq=list(s)) for s in seqs]
    assert all(Counter(r["seq"][p-1] for r in rows)==Counter("ABCDEFGH") for p in (2,4,6,8))
    return rows
def read_prompt(p,encoded):
    return f"Read the sequence from left to right. Which letter is at position {p} (count from 1)? Output only the letter. Sequence: "+encoded
def run(old,new,out):
    rows=corpus();out=Path(out);out.mkdir(exist_ok=False)
    (out/"corpus.json").write_bytes(c.canonical(rows))
    print("SELF_INDEX_FROZEN",c.sha_file(out/"corpus.json"),flush=True)
    import torch
    from peft import PeftModel
    tok,base=pc.load(old);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["adapter_sha256"]["adapter_model.safetensors"]==ic.NEW
    assert m["old_adapter_sha256"]==pc.OLD and m["steps"]==256
    for k,h in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==h
    model=PeftModel.from_pretrained(base,new/"adapter",is_trainable=False).eval()
    model.requires_grad_(False);model.config.use_cache=True
    def gen(q,limit):
        chat=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
        x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];start=time.monotonic()
        with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=limit,pad_token_id=tok.eos_token_id)[0,n:].tolist()
        return dict(raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start,prompt_sha256=c.digest(q.encode()))
    recon=[];records=[]
    with (out/"reconstructions.jsonl").open("x") as rl,(out/"predictions.jsonl").open("x") as log:
        for r in rows:
            s=r["seq"];z=gen(sr2.prompt(s,"B"),64);decoded=sr1.parse(z["raw"],8)
            valid=decoded is not None and len(set(decoded))==8
            faithful=valid and decoded==s
            x=dict(id=r["id"],valid=valid,faithful=faithful,**z);recon.append(x);rl.write(json.dumps(x)+"\n");rl.flush()
            for arm,encoded in (("D",pos.encode(s,"spaced")),("O",pos.encode(s,"indexed")),("S",z["raw"].strip() if valid else None)):
                for p in (2,4,6,8):
                    v=gen(read_prompt(p,encoded),32) if encoded is not None else dict(raw="",input_tokens=0,output_tokens=0,seconds=0,prompt_sha256=None)
                    rec=dict(arm=arm,id=r["id"],p=p,abstain=encoded is None,**v)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("SELF_INDEX_STAGE",r["id"],valid,faithful,flush=True)
    assert len(recon)==8 and len(records)==96
    by={r["id"]:r for r in rows};rf={r["id"]:r for r in recon}
    scores={}
    for arm in ("D","O","S"):
        rr=[r for r in records if r["arm"]==arm];assert len(rr)==32 and len({(r["id"],r["p"]) for r in rr})==32
        def hit(r):return not r["abstain"] and r["raw"].strip()==by[r["id"]]["seq"][r["p"]-1]
        scores[arm]=dict(exact=sum(map(hit,rr)),near=sum(hit(r) for r in rr if r["p"]<=4),far=sum(hit(r) for r in rr if r["p"]>=6),abstentions=sum(r["abstain"] for r in rr),calls=sum(not r["abstain"] for r in rr),on_faithful=sum(hit(r) for r in rr if rf[r["id"]]["faithful"]),on_unfaithful=sum(hit(r) for r in rr if not rf[r["id"]]["faithful"]),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
        if arm=="S":
            scores[arm]["calls"]+=8
            for k in ("input_tokens","output_tokens","seconds"):scores[arm][k]+=sum(r[k] for r in recon)
    d,o,s=(scores[a] for a in ("D","O","S"));faithful=sum(r["faithful"] for r in recon)
    result=dict(scores=scores,recon_valid=sum(r["valid"] for r in recon),recon_faithful=faithful,gate=faithful>=7 and s["far"]>=12 and s["far"]-d["far"]>=4 and s["near"]>=d["near"]-1 and s["exact"]>=o["exact"]-2,training=False,promotion_authorized=False,corpus_sha256=c.sha_file(out/"corpus.json"))
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("SELF_INDEX_CUMULATIVE_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--old");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.check:
        rows=corpus();assert sr1.parse("1:A 2:B 3:C 4:D 5:E 6:F 7:G 8:H",8)==list("ABCDEFGH")
        print("SELF_INDEX_CHECK",len(rows),c.digest(c.canonical(rows)))
    else:run(a.old,a.new,a.out)
