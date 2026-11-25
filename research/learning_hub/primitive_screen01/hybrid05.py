"""HYBRID05: bounded mixed-request routing and exact vs neural execution."""
import argparse, hashlib, json, random, secrets, re, time
from pathlib import Path
from collections import Counter
import modular04 as m
WORDS="air amber anvil arch ash attic bank basin bay beam birch blade bolt bridge brook brush buckle bulb cage cape cart cave chain clay cliff coat coil comb creek cube dune dust fan fang farm fin foam fog frame fruit gap gem globe gourd grain grove gum hatch hay heather hedge hive horn ice ivy kiln lace lawn lime lock loom lung marsh mast maze nail net nook oar oven pane path peak pin pipe pond port raft rail ramp reef ring rope rug sail sap shard sled slope snow soil spark spear stem stump swan thorn tile toad tower trail twig veil vine wand web wick wing wood".split()
K=("copy","select","membership","reverse")
R=K+("unknown",)
def need(x,msg): 
    if not x:raise ValueError(msg)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,separators=(",",":")))
def request(k,x,p,t,v):
    s=" ".join(x)
    return {"copy":(f"Transcribe exactly: {s}",f"Keep the words unchanged: {s}"),"reverse":(f"Put the words in opposite order: {s}",f"Swap the order of these words: {s}"),"select":(f"Which word occupies slot {p}? {s}",f"Give the item at position {p} in: {s}"),"membership":(f"Does {t} occur in: {s}?",f"Check whether {t} appears in: {s}?")}[k][v]
def build(seed):
    rng=random.Random(seed);rows=[]
    for k in K:
        for i in range(16 if k in ("select","membership") else 32):
            p=i%4+1;t=None
            if k=="select":
                x=rng.sample(WORDS,4);y=x.copy();q=(p+i//4)%4
                if q==p-1:q=(q+1)%4
                y[p-1],y[q]=y[q],y[p-1];xs=[x,y]
            elif k=="membership":
                t,*x=rng.sample(WORDS,4);y=x.copy();y[i%3]=t;xs=[x,y]
            else:xs=[rng.sample(WORDS,2)]
            for j,x in enumerate(xs):
                g=" ".join(x) if k=="copy" else " ".join(x[::-1]) if k=="reverse" else x[p-1] if k=="select" else "Yes" if t in x else "No"
                rows.append(dict(id=f"{k}-{i}-{j}",kind=k,pair=f"{k}-{i}" if len(xs)==2 else None,pos=p if k=="select" else None,gold=g,user=request(k,x,p,t,i%2)))
    for i in range(32):
        a,b,c=rng.sample(WORDS,3)
        s=[f"Translate into French: {a} {b}",f"Which word occupies slot 5? {a} {b} {c}",f"Transcribe exactly: {a} {b} {c}",f"Swap and translate: {a} {b}"][i%4]
        rows.append(dict(id=f"unknown-{i}",kind="unknown",pair=None,pos=None,gold=None,user=s))
    rng.shuffle(rows);return rows
def route(s):
    rules=[("copy",r"(?:Transcribe exactly|Keep the words unchanged): ([a-z]+ [a-z]+)"),("reverse",r"(?:Put the words in opposite order|Swap the order of these words): ([a-z]+ [a-z]+)"),("select",r"(?:Which word occupies slot ([1-4])\? |Give the item at position ([1-4]) in: )([a-z]+ [a-z]+ [a-z]+ [a-z]+)"),("membership",r"(?:Does ([a-z]+) occur in: |Check whether ([a-z]+) appears in: )([a-z]+ [a-z]+ [a-z]+)\?")]
    for k,pat in rules:
        a=re.fullmatch(pat,s)
        if not a:continue
        if k in ("copy","reverse"):x=a[1].split();p=t=None
        else:
            value=a[1] or a[2];x=a[3].split();p=int(value) if k=="select" else None;t=value if k=="membership" else None
        if len(set(x))!=len(x) or any(w not in WORDS for w in x) or (t is not None and t not in WORDS):return None
        return k,x,p,t
    return None
def exact(a):
    if a is None:return None
    k,x,p,t=a
    return " ".join(x) if k=="copy" else " ".join(x[::-1]) if k=="reverse" else x[p-1] if k=="select" else "Yes" if t in x else "No"
def adapt(a):
    k,x,p,t=a
    return m.prompts(k,x,t,p)["minimal" if k in ("copy","select") else "original"]
def parse(raw,k,p=None):
    s=raw.strip()
    if k=="select":
        z=re.fullmatch(r'The word labeled '+str(p)+r' is "([a-z]+)"\.',s)
        if z:s=z[1]
    if s.endswith("."):s=s[:-1]
    if k=="membership":return s if s in ("Yes","No") else None
    if k=="unknown":return None
    return s if len(s.split(" "))==(1 if k=="select" else 2) and all(w in WORDS for w in s.split(" ")) else None
def validate(rows):
    need(len(rows)==160 and len({r["id"] for r in rows})==160 and Counter(r["kind"] for r in rows)=={k:32 for k in R},"COUNTS")
    need(len({r["user"] for r in rows})==160,"DUPLICATE")
    pairs={}
    for r in rows:
        a=route(r["user"]);need((a[0] if a else "unknown")==r["kind"] and exact(a)==r["gold"],"ORACLE")
        if r["pair"]:pairs.setdefault(r["pair"],[]).append(r)
    need(len(pairs)==32 and all(len(z)==2 and z[0]["gold"]!=z[1]["gold"] for z in pairs.values()),"PAIRS")
    need(Counter(r["pos"] for r in rows if r["kind"]=="select")=={i:8 for i in range(1,5)},"POSITIONS")
def freeze(root):
    root=Path(root);root.mkdir(exist_ok=False)
    for _ in range(100):
        seed=secrets.randbits(64);rows=build(seed)
        if len({r["user"] for r in rows})==160:break
    validate(rows);write(root/"labels.json",rows);write(root/"questions.json",[{k:r[k] for k in ("id","user")} for r in rows]);write(root/"curator.json",{"seed":seed})
    write(root/"manifest.json",dict(model=m.MODEL,revision=m.REV,questions_sha=sha(root/"questions.json"),labels_sha=sha(root/"labels.json")))
def routing_prompt(s):
    return "Classify this request as exactly one of COPY, SELECT, MEMBERSHIP, REVERSE, UNKNOWN. UNKNOWN means outside these supported operations or invalid arguments. Output the category only.\nRequest: "+s
def infer(root,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    root=Path(root);mf=json.loads((root/"manifest.json").read_text());q=root/"questions.json"
    need(mf["model"]==m.MODEL and mf["revision"]==m.REV and sha(q)==mf["questions_sha"],"FREEZE")
    rows=json.loads(q.read_text());need(len(rows)==160 and all(set(r)=={"id","user"} for r in rows),"QUESTIONS")
    torch.set_num_threads(2);torch.manual_seed(20261125)
    tok=AutoTokenizer.from_pretrained(m.MODEL,revision=m.REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(m.MODEL,revision=m.REV,trust_remote_code=False,torch_dtype=torch.float32).eval();need(model.config._commit_hash==m.REV,"PIN")
    def gen(p):
        chat=tok.apply_chat_template([{"role":"user","content":p}],tokenize=False,add_generation_prompt=True)
        x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1];need(n+16<=384,"BUDGET");t=time.monotonic()
        with torch.inference_mode():ids=model.generate(**x,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
        raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
        return dict(raw=raw,raw_sha=digest(raw),prompt_sha=digest(p),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-t)
    with Path(out).open("x") as f:
        for r in rows:
            a=route(r["user"]);z=dict(id=r["id"],revision=m.REV,user_sha=digest(r["user"]),route=a[0] if a else "unknown",exact=exact(a),router=gen(routing_prompt(r["user"])),direct=None,adapted=None)
            if a:
                z["direct"]=gen(r["user"]);z["adapted"]=gen(adapt(a))
            f.write(json.dumps(z)+"\n");f.flush()
def assess(rows,records):
    idx={r["id"]:r for r in rows};seen={}
    for z in records:
        r=idx[z["id"]];a=route(r["user"]);need(z["id"] not in seen and z["revision"]==m.REV and z["user_sha"]==digest(r["user"]),"IDENTITY")
        need(z["route"]==(a[0] if a else "unknown") and z["exact"]==exact(a),"ROUTE_TRACE")
        for key,p in (("router",routing_prompt(r["user"])),("direct",r["user"] if a else None),("adapted",adapt(a) if a else None)):
            v=z[key]
            if p is None:need(v is None,"UNSUPPORTED_DISPATCH");continue
            need(v["raw_sha"]==digest(v["raw"]) and v["prompt_sha"]==digest(p) and 0<v["input_tokens"]<=368 and 0<=v["output_tokens"]<=16,"TRACE")
        seen[r["id"]]=z
    need(set(seen)==set(idx),"COVERAGE")
    result={};conf={k:Counter() for k in R}
    for r in rows:
        z=seen[r["id"]];v=z["router"]["raw"].strip().removesuffix(".").lower()
        conf[r["kind"]][v if v in R else "invalid"]+=1
    for k in R:
        rs=[r for r in rows if r["kind"]==k];d={}
        for arm in ("direct","adapted","hybrid","exact"):
            if k=="unknown":continue
            ok={}
            for r in rs:
                z=seen[r["id"]]
                pred=z["exact"] if arm=="exact" or (arm=="hybrid" and k in ("select","membership")) else parse(z["direct" if arm=="direct" else "adapted"]["raw"],k,r["pos"])
                ok[r["id"]]=pred==r["gold"]
            n=sum(ok.values());d[arm]=dict(correct=n,total=32,qualification=n>=(29 if k=="reverse" else 31))
            if k in ("membership","select"):
                pairs={}
                for r in rs:pairs.setdefault(r["pair"],[]).append(r["id"])
                d[arm]["both_pairs"]=sum(all(ok[i] for i in z) for z in pairs.values())
                d[arm]["qualification"] &= d[arm]["both_pairs"]==16
        result[k]=d
    return dict(scores=result,neural_router_confusion={k:dict(v) for k,v in conf.items()},rule_router_correct=sum(seen[r["id"]]["route"]==r["kind"] for r in rows),rule_abstention=sum(seen[r["id"]]["route"]=="unknown" for r in rows if r["kind"]=="unknown"),scope="bounded same-author grammar; exact tools are not learned skills; neural routing measured independently",promotion_authorized=False,training_authorized=False)
def finish(root,pred,out):
    root=Path(root);mf=json.loads((root/"manifest.json").read_text());need(sha(root/"labels.json")==mf["labels_sha"],"LABEL_HASH")
    rows=json.loads((root/"labels.json").read_text());validate(rows);need(rows==build(json.loads((root/"curator.json").read_text())["seed"]),"REGEN")
    records=[json.loads(s) for s in Path(pred).read_text().splitlines()];res=assess(rows,records);res.update(prediction_sha=sha(pred),labels_sha=mf["labels_sha"]);write(out,res);print(json.dumps(res,indent=2))
def selftest():
    rows=build(1234);validate(rows)
    need(route("Transcribe exactly: air amber anvil") is None and route("Which word occupies slot 5? air amber arch ash") is None and route("Swap and translate: air amber") is None,"ABSTENTION")
    need(parse('The word labeled 1 is "air".',"select",2) is None,"WRONG_KEY")
    def v(p,raw):return dict(raw=raw,raw_sha=digest(raw),prompt_sha=digest(p),input_tokens=1,output_tokens=1,seconds=0)
    z=[]
    for r in rows:
        a=route(r["user"]);z.append(dict(id=r["id"],revision=m.REV,user_sha=digest(r["user"]),route=r["kind"],exact=exact(a),router=v(routing_prompt(r["user"]),r["kind"].upper()),direct=v(r["user"],r["gold"]) if a else None,adapted=v(adapt(a),r["gold"]) if a else None))
    res=assess(rows,z);need(res["rule_router_correct"]==160 and res["rule_abstention"]==32 and all(res["scores"][k]["hybrid"]["qualification"] for k in K),"ORACLE")
    for bad in (z[:-1],z+[z[0]]):
        try:assess(rows,bad)
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    print("SELFTEST OK")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze","infer","score"]);p.add_argument("--root");p.add_argument("--out");p.add_argument("--pred");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="freeze":freeze(a.root)
    elif a.cmd=="infer":infer(a.root,a.out)
    else:finish(a.root,a.pred,a.out)
