"""RELIABILITY02: prospective paired prompt/format diagnostic. Frozen Qwen; no training."""
import argparse, hashlib, json, random, secrets, time, re
from pathlib import Path
from collections import Counter
MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REV="c89bee90d9f811437d9735454613c35b4a3c4dc8"
WORDS="acorn bread cloud dance elm frost glove honey ink jar key leaf moss needle ocean plum quartz rose shell trout urn vase wind yarn".split()
KINDS=("copy","select","membership","reverse")
ARMS=("original","minimal")
def require(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,separators=(",",":")))
def prompts(k,items,target=None,pos=None):
    s=" ".join(items)
    if k=="copy":return {"original":"Copy these two words exactly, separated by one space. Output only the words.\n"+s,"minimal":"Copy exactly these words: "+s}
    if k=="reverse":return {"original":"Write these two words in reverse order. Output only the two words separated by one space.\n"+s,"minimal":"Reverse the order of these two words: "+s}
    if k=="select":return {"original":f"Return only word number {pos} from this list, counting from 1.\n{s}","minimal":f"Which is word {pos} (count from 1)? {s}. Answer with one word."}
    return {"original":f"Is the word {target} in this list? Answer exactly Yes or No.\n{s}","minimal":f"Is {target} in this list: {s}? Yes or No."}
def oracle(r):
    k=r["kind"];s=r["items"]
    if k=="copy":return " ".join(s)
    if k=="reverse":return " ".join(s[::-1])
    if k=="select":return s[r["pos"]-1]
    if k=="membership":return "Yes" if r["target"] in s else "No"
    raise ValueError("KIND")
def build(seed):
    rng=random.Random(seed);rows=[];seen=set();used_twos=set()
    for k in KINDS:
        for i in range(32 if k=="membership" else 64):
            for attempt in range(10000):
                if k in ("copy","reverse"):
                    a=rng.sample(WORDS,2)
                    if tuple(sorted(a)) in used_twos:continue
                    batch=[dict(items=a,target=None,pos=None,pair=None)]
                elif k=="select":
                    batch=[dict(items=rng.sample(WORDS,4),target=None,pos=i%4+1,pair=None)]
                else:
                    a,b,c,d=rng.sample(WORDS,4);items=[b,c,d];j=i%3
                    yes=items.copy();yes[j]=a
                    batch=[dict(items=v,target=a,pos=None,pair=f"m{i:02d}") for v in (items,yes)]
                ps=[prompts(k,**{x:z[x] for x in ("items","target","pos")}) for z in batch]
                keys=[p[a] for p in ps for a in ARMS]
                if len(set(keys))!=len(keys) or any(key in seen for key in keys):continue
                seen.update(keys)
                if k in ("copy","reverse"):used_twos.add(tuple(sorted(batch[0]["items"])))
                for j,(z,p) in enumerate(zip(batch,ps)):
                    r=dict(z,id=f"{k}-{i:02d}-{j}",kind=k,prompts=p)
                    r["gold"]=oracle(r);rows.append(r)
                break
            else:raise ValueError("GENERATION_BUDGET")
    rng.shuffle(rows);return rows
def validate(rows):
    require(len(rows)==256 and len({r["id"] for r in rows})==256,"COUNT")
    require(Counter(r["kind"] for r in rows)=={k:64 for k in KINDS},"KIND_COUNTS")
    require(len({p for r in rows for p in r["prompts"].values()})==512,"PROMPT_UNIQUENESS")
    pairs={};positions=Counter()
    for r in rows:
        require(all(x in WORDS for x in r["items"]) and len(set(r["items"]))==len(r["items"]),"ITEMS")
        require(r["gold"]==oracle(r) and r["prompts"]==prompts(r["kind"],r["items"],r["target"],r["pos"]),"ORACLE")
        if r["kind"]=="select":positions[r["pos"]]+=1
        if r["kind"]=="membership":pairs.setdefault(r["pair"],[]).append(r)
    require(positions=={i:16 for i in range(1,5)} and len(pairs)==32,"BALANCE")
    for z in pairs.values():
        require(len(z)==2 and {x["gold"] for x in z}=={"Yes","No"} and z[0]["target"]==z[1]["target"] and len(z[0]["items"])==len(z[1]["items"])==3 and sum(a!=b for a,b in zip(z[0]["items"],z[1]["items"]))==1,"PAIR")
def canonical(raw,k):
    # No case folding, no extraction, no explanations, no multiple punctuation.
    s=raw.strip()
    if s.endswith("."):s=s[:-1]
    if k=="membership":return s if s in ("Yes","No") else None
    parts=s.split(" ")
    return s if len(parts)==(1 if k=="select" else 2) and all(x in WORDS for x in parts) else None
def freeze(root):
    root=Path(root);root.mkdir(exist_ok=False)
    seed=secrets.randbits(64);rows=build(seed);validate(rows)
    tasks=[dict(id=r["id"],arm=a,prompt=r["prompts"][a]) for r in rows for a in ARMS]
    random.Random(seed^991).shuffle(tasks)
    write(root/"questions.json",tasks);write(root/"labels.json",rows)
    # The inference manifest does not contain the private generation seed.
    write(root/"manifest.json",dict(questions_sha=sha(root/"questions.json"),labels_sha=sha(root/"labels.json"),model=MODEL,revision=REV))
    write(root/"curator.json",dict(seed=seed))
def infer(root,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    root=Path(root);m=json.loads((root/"manifest.json").read_text());q=root/"questions.json"
    require(m["model"]==MODEL and m["revision"]==REV and sha(q)==m["questions_sha"],"FREEZE")
    tasks=json.loads(q.read_text())
    require(len(tasks)==512 and len({(r["id"],r["arm"]) for r in tasks})==512 and all(set(r)=={"id","arm","prompt"} and r["arm"] in ARMS for r in tasks),"QUESTIONS_ONLY")
    torch.set_num_threads(2);torch.manual_seed(20261125)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32).eval()
    require(model.config._commit_hash==REV,"MODEL_PIN")
    with Path(out).open("x") as f:
        for r in tasks:
            chat=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
            x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            require(n+16<=384,"BUDGET")
            t=time.monotonic()
            with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(id=r["id"],arm=r["arm"],revision=REV,prompt_sha=digest(r["prompt"]),raw=raw,raw_sha=digest(raw),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-t)
            f.write(json.dumps(rec)+"\n");f.flush()
def assess(rows,records):
    idx={r["id"]:r for r in rows};seen={}
    for z in records:
        key=(z["id"],z["arm"])
        require(key not in seen and z["id"] in idx and z["arm"] in ARMS and z["revision"]==REV,"TRACE_ID")
        require(z["prompt_sha"]==digest(idx[z["id"]]["prompts"][z["arm"]]) and z["raw_sha"]==digest(z["raw"]),"HASH")
        require(0<z["input_tokens"]<=368 and 0<=z["output_tokens"]<=16,"BUDGET")
        seen[key]=z
    require(set(seen)=={(r["id"],a) for r in rows for a in ARMS},"COVERAGE")
    result={}
    for a in ARMS:
        result[a]={}
        for k in KINDS:
            rs=[r for r in rows if r["kind"]==k]
            raw={r["id"]:seen[r["id"],a]["raw"].strip() for r in rs}
            canon={i:canonical(s,k) for i,s in raw.items()}
            strict={r["id"]:raw[r["id"]]==r["gold"] for r in rs}
            ok={r["id"]:canon[r["id"]]==r["gold"] for r in rs}
            n=sum(ok.values());target=58 if k=="reverse" else 61
            d=dict(strict=sum(strict.values()),normalized=n,format_valid=sum(x is not None for x in canon.values()),format_only_rescued=sum(ok[i] and not strict[i] for i in ok),wrong_valid=sum(canon[i] is not None and not ok[i] for i in ok),invalid=sum(x is None for x in canon.values()),screen=n>=48,qualification_target_met=n>=target)
            if k=="membership":
                p={}
                for r in rs:p.setdefault(r["pair"],[]).append(r["id"])
                d.update(yes_correct=sum(ok[r["id"]] for r in rs if r["gold"]=="Yes"),no_correct=sum(ok[r["id"]] for r in rs if r["gold"]=="No"),both_pairs=sum(all(ok[i] for i in z) for z in p.values()))
                d["screen"] &= min(d["yes_correct"],d["no_correct"],d["both_pairs"])>=20
                d["qualification_target_met"] &= min(d["yes_correct"],d["no_correct"],d["both_pairs"])>=31
            result[a][k]=d
    diffs={k:result["minimal"][k]["normalized"]-result["original"][k]["normalized"] for k in KINDS}
    # Improvement is diagnostic only; no proof of learning or promotion.
    signal=all(result["minimal"][k]["screen"] for k in KINDS) and sum(diffs[k]>=8 for k in ("copy","select","membership"))>=2 and diffs["reverse"]>=-3 and result["minimal"]["reverse"]["normalized"]>=58
    return dict(scores=result,differences=diffs,diagnostic_signal=signal,all_targets={a:all(d["qualification_target_met"] for d in result[a].values()) for a in ARMS},input_tokens=sum(z["input_tokens"] for z in records),output_tokens=sum(z["output_tokens"] for z in records),seconds=sum(z["seconds"] for z in records),promotion_authorized=False,training_authorized=False)
def finish(root,pred,out):
    root=Path(root);m=json.loads((root/"manifest.json").read_text());require(sha(root/"labels.json")==m["labels_sha"],"LABEL_SHA")
    rows=json.loads((root/"labels.json").read_text());validate(rows)
    require(rows==build(json.loads((root/"curator.json").read_text())["seed"]),"REGENERATION")
    records=[json.loads(s) for s in Path(pred).read_text().splitlines()]
    result=assess(rows,records);result.update(scope="fresh synthetic same-author diagnostic, not independent confirmation",prediction_sha=sha(pred),labels_sha=m["labels_sha"],revision=REV)
    write(out,result);print(json.dumps(result,indent=2))
def selftest():
    rows=build(1234);validate(rows);require(rows==build(1234) and rows!=build(1235),"SEED")
    for raw,k,expected in [("Yes.","membership","Yes"),("No..","membership",None),("Yes, because","membership",None),(" acorn bread. ","copy","acorn bread"),("acorn  bread","copy",None),("acorn bread!","copy",None),("acorn","select","acorn")]:
        require(canonical(raw,k)==expected,"PARSE")
    records=[dict(id=r["id"],arm=a,revision=REV,prompt_sha=digest(r["prompts"][a]),raw=r["gold"],raw_sha=digest(r["gold"]),input_tokens=1,output_tokens=1,seconds=0) for r in rows for a in ARMS]
    require(all(assess(rows,records)["all_targets"].values()),"ORACLE")
    for zs in (records[:-1],records+[records[0]],[dict(records[0],raw="fake")]+records[1:]):
        try:assess(rows,zs)
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    constant=[dict(z,raw="Yes",raw_sha=digest("Yes")) for z in records]
    require(not any(assess(rows,constant)["all_targets"].values()),"CONSTANT")
    print("SELFTEST OK")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze","infer","score"]);p.add_argument("--root");p.add_argument("--out");p.add_argument("--pred");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="freeze":freeze(a.root)
    elif a.cmd=="infer":infer(a.root,a.out)
    else:finish(a.root,a.pred,a.out)
