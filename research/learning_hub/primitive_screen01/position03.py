"""POSITION03: diagnostic of ordinal selection, explicit keys and copy control."""
import argparse, hashlib, json, random, secrets, time
from pathlib import Path
from collections import Counter
MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REV="c89bee90d9f811437d9735454613c35b4a3c4dc8"
ARMS=("ordinal","numbered","letter","copy_control")
WORDS="ant bell crab deer fern gold harp island jack lake map nut oak pine reed sand tent valley wolf axe book cake door ear flag goat hill iron jam lamp mint note otter pear rake seed table vest wheel yak almond brick canoe daisy ember fig glass hawk iris jade koala lilac melon nylon opal petal rabbit salt token violet walnut arrow basket cedar dolphin engine feather guitar helmet igloo jacket kernel ladder marble nectar orbit pencil radar saddle tulip velvet window yo".split()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,separators=(",",":")))
def prompts(items,pos,keys):
    return {
      "ordinal":f"Return only word number {pos+1} from this list, counting from 1.\n"+" ".join(items),
      "numbered":f"Return only the word labeled {pos+1}.\n"+"\n".join(f"{i+1}: {v}" for i,v in enumerate(items)),
      "letter":f"Return only the word labeled {keys[pos]}.\n"+"\n".join(f"{k}: {v}" for k,v in zip(keys,items)),
      "copy_control":"Copy this word exactly. Output only the word.\n"+items[pos]}
def build(seed):
    rng=random.Random(seed);rows=[]
    require(len(set(WORDS))==len(WORDS) and len(WORDS)>=64,"VOCABULARY")
    targets=rng.sample(WORDS,64)
    for i in range(32):
        pos=i%4;other=(pos+1+(i//4)%3)%4
        a,b=targets[2*i:2*i+2]
        distractors=rng.sample([w for w in WORDS if w not in (a,b)],2)
        items=[None]*4;items[pos]=a;items[other]=b
        for j,v in zip([j for j in range(4) if j not in (pos,other)],distractors):items[j]=v
        swapped=items.copy();swapped[pos],swapped[other]=swapped[other],swapped[pos]
        keys=rng.sample(list("K M R T".split()),4)
        for j,v in enumerate((items,swapped)):
            rows.append(dict(id=f"p{i:02d}-{j}",pair=f"p{i:02d}",pos=pos,other=other,items=v,keys=keys,gold=v[pos],prompts=prompts(v,pos,keys)))
    rng.shuffle(rows);return rows
def oracle(prompt,arm):
    lines=prompt.splitlines()
    if arm=="ordinal":return lines[1].split()[int(lines[0].split("word number ")[1].split()[0])-1]
    if arm=="copy_control":return lines[1]
    label=lines[0].split("labeled ")[1].removesuffix(".")
    return dict(line.split(": ",1) for line in lines[1:])[label]
def validate(rows):
    require(len(rows)==64 and len({r["id"] for r in rows})==64,"COUNT")
    require(Counter(r["pos"] for r in rows)=={i:16 for i in range(4)},"POSITION_BALANCE")
    require(len({r["gold"] for r in rows})==64,"GOLD_UNIQUE")
    require(len({p for r in rows for p in r["prompts"].values()})==256,"PROMPT_UNIQUE")
    groups={}
    for r in rows:
        require(len(r["items"])==4 and len(set(r["items"]))==4 and set(r["items"])<=set(WORDS),"ITEMS")
        require(set(r["keys"])==set("K M R T".split()) and r["pos"]!=r["other"],"KEYS")
        require(r["gold"]==r["items"][r["pos"]] and r["prompts"]==prompts(r["items"],r["pos"],r["keys"]),"GOLD")
        require(all(oracle(r["prompts"][a],a)==r["gold"] for a in ARMS),"ORACLE")
        groups.setdefault(r["pair"],[]).append(r)
    require(len(groups)==32,"PAIR_COUNT")
    for z in groups.values():
        require(len(z)==2,"PAIR_SIZE");a,b=z
        require(a["pos"]==b["pos"] and a["other"]==b["other"] and a["keys"]==b["keys"],"PAIR_CONTEXT")
        x=a["items"].copy();p,q=a["pos"],a["other"];x[p],x[q]=x[q],x[p]
        require(x==b["items"] and a["gold"]!=b["gold"],"PAIR_SWAP")
def normalize(raw):
    s=raw.strip()
    if s.endswith("."):s=s[:-1]
    return s if s in WORDS else None
def freeze(root):
    root=Path(root);root.mkdir(exist_ok=False);seed=secrets.randbits(64);rows=build(seed);validate(rows)
    tasks=[dict(id=r["id"],arm=a,prompt=r["prompts"][a]) for r in rows for a in ARMS]
    random.Random(seed^301).shuffle(tasks)
    write(root/"questions.json",tasks);write(root/"labels.json",rows)
    write(root/"manifest.json",dict(model=MODEL,revision=REV,questions_sha=sha(root/"questions.json"),labels_sha=sha(root/"labels.json")))
    write(root/"curator.json",dict(seed=seed))
def infer(root,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    root=Path(root);m=json.loads((root/"manifest.json").read_text());q=root/"questions.json"
    require(m["model"]==MODEL and m["revision"]==REV and sha(q)==m["questions_sha"],"FREEZE")
    tasks=json.loads(q.read_text())
    require(len(tasks)==256 and len({(r["id"],r["arm"]) for r in tasks})==256 and all(set(r)=={"id","arm","prompt"} and r["arm"] in ARMS for r in tasks),"QUESTIONS_ONLY")
    torch.set_num_threads(2);torch.manual_seed(20261125)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32).eval()
    require(model.config._commit_hash==REV,"MODEL_PIN")
    with Path(out).open("x") as f:
        for r in tasks:
            chat=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
            x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            require(n+16<=384,"BUDGET");t=time.monotonic()
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
        require(0<z["input_tokens"]<=368 and 0<=z["output_tokens"]<=16,"BUDGET");seen[key]=z
    require(set(seen)=={(r["id"],a) for r in rows for a in ARMS},"COVERAGE")
    groups={}
    for r in rows:groups.setdefault(r["pair"],[]).append(r["id"])
    scores={}
    for a in ARMS:
        matrix=[[0]*6 for _ in range(4)];ok={};strict=0;valid=0;outside=0
        for r in rows:
            raw=seen[r["id"],a]["raw"];p=normalize(raw);ok[r["id"]]=p==r["gold"];strict+=raw.strip()==r["gold"];valid+=p is not None
            col=5 if p is None else (r["items"].index(p) if p in r["items"] else 4)
            outside+=col==4;matrix[r["pos"]][col]+=1
        n=sum(ok.values());pos=[matrix[i][i] for i in range(4)];pairs=sum(all(ok[j] for j in z) for z in groups.values())
        scores[a]=dict(strict=strict,normalized=n,format_valid=valid,off_list=outside,by_position=pos,both_pairs=pairs,confusion=matrix,screen=n>=48 and min(pos)>=12 and pairs>=20,qualification_target=n>=61 and min(pos)>=15 and pairs>=31)
    candidate={a:scores[a]["screen"] and scores[a]["normalized"]-scores["ordinal"]["normalized"]>=8 for a in ("numbered","letter")}
    return dict(scores=scores,candidate_signal=candidate,scope="fresh same-author synthetic diagnostic, not independent qualification",input_tokens=sum(z["input_tokens"] for z in records),output_tokens=sum(z["output_tokens"] for z in records),seconds=sum(z["seconds"] for z in records),promotion_authorized=False,training_authorized=False)
def finish(root,pred,out):
    root=Path(root);m=json.loads((root/"manifest.json").read_text());require(sha(root/"labels.json")==m["labels_sha"],"LABEL_SHA")
    rows=json.loads((root/"labels.json").read_text());validate(rows)
    require(rows==build(json.loads((root/"curator.json").read_text())["seed"]),"REGENERATION")
    rec=[json.loads(s) for s in Path(pred).read_text().splitlines()]
    res=assess(rows,rec);res.update(prediction_sha=sha(pred),labels_sha=m["labels_sha"],revision=REV);write(out,res);print(json.dumps(res,indent=2))
def selftest():
    rows=build(1234);validate(rows);require(rows==build(1234) and rows!=build(1235),"SEED")
    require(normalize("ant.")=="ant" and normalize(" ant ")=="ant" and normalize("ant..") is None and normalize("ant because") is None,"PARSE")
    def mock(fn):
        return [dict(id=r["id"],arm=a,revision=REV,prompt_sha=digest(r["prompts"][a]),raw=fn(r),raw_sha=digest(fn(r)),input_tokens=1,output_tokens=1,seconds=0) for r in rows for a in ARMS]
    good=mock(lambda r:r["gold"]);require(all(s["qualification_target"] for s in assess(rows,good)["scores"].values()),"ORACLE")
    first=mock(lambda r:r["items"][0]);require(all(s["normalized"]==16 and not s["screen"] for s in assess(rows,first)["scores"].values()),"FIRST_POSITION_CONTROL")
    for z in (good[:-1],good+[good[0]],[dict(good[0],raw="wrong")]+good[1:]):
        try:assess(rows,z)
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    print("SELFTEST OK")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze","infer","score"]);p.add_argument("--root");p.add_argument("--out");p.add_argument("--pred");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="freeze":freeze(a.root)
    elif a.cmd=="infer":infer(a.root,a.out)
    else:finish(a.root,a.pred,a.out)
