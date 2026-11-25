"""PRIMITIVES01: frozen-model diagnostic, no training or promotion."""
import argparse, hashlib, json, random, secrets, time
from pathlib import Path
from collections import Counter

MODELS={
 "smol135":("HuggingFaceTB/SmolLM2-135M-Instruct","ee72e5415c002e8fc0566a191a07c0b2b708875a"),
 "qwen500":("Qwen/Qwen2.5-0.5B-Instruct","c89bee90d9f811437d9735454613c35b4a3c4dc8")}
KINDS=("copy","select","membership","reverse")
WORDS="apple boat chair drum eagle flame grape house ivory jewel kite lemon moon nest olive peach queen river stone tiger uncle violin whale zebra".split()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,sort_keys=True,separators=(",",":")))
def build(seed):
    rng=random.Random(seed);rows=[];seen=set()
    for kind in KINDS:
        for i in range(32 if kind=="membership" else 64):
            while True:
                a,b,c,d,e=rng.sample(WORDS,5)
                if kind=="copy":
                    # Different two-word strings; no JSON, no punctuation output.
                    p=f"Copy these two words exactly, separated by one space. Output only the words.\n{a} {b}"
                    batch=[(p,f"{a} {b}",None)]
                elif kind=="select":
                    k=rng.randrange(1,5);items=[a,b,c,d]
                    p=f"Return only word number {k} from this list, counting from 1.\n"+" ".join(items)
                    batch=[(p,items[k-1],None)]
                elif kind=="reverse":
                    p=f"Write these two words in reverse order. Output only the two words separated by one space.\n{a} {b}"
                    batch=[(p,f"{b} {a}",None)]
                else:
                    items=[b,c,d];pos=rng.randrange(3)
                    yes=items.copy();yes[pos]=a
                    rng.shuffle(items)
                    # Keep identical order and distractors except one replacement.
                    yes=items.copy();yes[items.index([b,c,d][pos])]=a
                    tmpl=lambda xs:f"Is the word {a} in this list? Answer exactly Yes or No.\n"+" ".join(xs)
                    pair=f"pair-{i:02d}"
                    batch=[(tmpl(items),"No",pair),(tmpl(yes),"Yes",pair)]
                if len({p for p,_,_ in batch})==len(batch) and all(p not in seen for p,_,_ in batch):break
            for j,(p,g,pair) in enumerate(batch):
                seen.add(p);rows.append(dict(id=f"{kind}-{i:02d}-{j}",kind=kind,prompt=p,gold=g,pair=pair))
    rng.shuffle(rows);return rows
def oracle(r):
    p=r["prompt"]; line=p.split("\n")[-1].split();kind=r["kind"]
    if kind=="copy":return " ".join(line)
    if kind=="select":return line[int(p.split("word number ")[1].split()[0])-1]
    if kind=="reverse":return " ".join(reversed(line))
    if kind=="membership":return "Yes" if p.split("Is the word ")[1].split()[0] in line else "No"
    raise ValueError("KIND")
def validate(rows):
    require(len(rows)==256 and len({r["id"] for r in rows})==256 and len({r["prompt"] for r in rows})==256,"COVERAGE")
    require(Counter(r["kind"] for r in rows)=={k:64 for k in KINDS},"KIND_COUNTS")
    pairs={}
    for r in rows:
        require(r["gold"]==oracle(r),"ORACLE")
        if r["kind"]=="membership":pairs.setdefault(r["pair"],[]).append(r)
    require(len(pairs)==32,"PAIR_COUNT")
    for a in pairs.values():
        require(len(a)==2 and {x["gold"] for x in a}=={"Yes","No"},"PAIR_LABELS")
        p,q=[x["prompt"].split("\n") for x in a]
        require(p[0]==q[0] and len(p[1].split())==len(q[1].split())==3 and sum(x!=y for x,y in zip(p[1].split(),q[1].split()))==1,"PAIR_TOGGLE")
def freeze(out):
    out=Path(out);out.mkdir(exist_ok=False);seed=secrets.randbits(64);rows=build(seed);validate(rows)
    questions=[{k:r[k] for k in ("id","kind","prompt")} for r in rows]
    write(out/"questions.json",questions);write(out/"labels.json",rows)
    write(out/"manifest.json",dict(seed=seed,questions_sha=sha(out/"questions.json"),labels_sha=sha(out/"labels.json"),models=MODELS))
def infer(root,arm,out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    root=Path(root);m=json.loads((root/"manifest.json").read_text());q=root/"questions.json"
    require(sha(q)==m["questions_sha"],"QUESTION_SHA");rows=json.loads(q.read_text())
    require(len(rows)==256 and len({r["id"] for r in rows})==256 and all(set(r)=={"id","kind","prompt"} for r in rows),"QUESTIONS_ONLY")
    model_id,rev=MODELS[arm];torch.set_num_threads(2);torch.manual_seed(20261125)
    tok=AutoTokenizer.from_pretrained(model_id,revision=rev,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(model_id,revision=rev,trust_remote_code=False,torch_dtype=torch.float32).eval()
    require(model.config._commit_hash==rev,"MODEL_PIN")
    with Path(out).open("x") as f:
        for r in rows:
            chat=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
            x=tok(chat,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            require(n+16<=384,"CONTEXT")
            t=time.monotonic()
            with torch.inference_mode():
                ids=model.generate(**x,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            rec=dict(id=r["id"],arm=arm,revision=rev,prompt_sha=digest(r["prompt"]),raw=raw,raw_sha=digest(raw),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-t)
            f.write(json.dumps(rec)+"\n");f.flush()
def assess(rows,records,arm):
    idx={r["id"]:r for r in rows};seen={}
    for r in records:
        require(r["id"] in idx and r["id"] not in seen and r["arm"]==arm and r["revision"]==MODELS[arm][1],"IDENTITY")
        require(r["prompt_sha"]==digest(idx[r["id"]]["prompt"]) and r["raw_sha"]==digest(r["raw"]),"HASH")
        require(0<r["input_tokens"]<=368 and 0<=r["output_tokens"]<=16,"BUDGET");seen[r["id"]]=r
    require(set(seen)==set(idx),"MISSING")
    results={}
    for k in KINDS:
        subset=[r for r in rows if r["kind"]==k]
        # Exact after removing outer whitespace only; no extracting a plausible answer from prose.
        pred={r["id"]:seen[r["id"]]["raw"].strip() for r in subset}
        ok={r["id"]:pred[r["id"]]==r["gold"] for r in subset}
        def valid(x):
            w=x.split(" ")
            return x in ("Yes","No") if k=="membership" else len(w)==(1 if k=="select" else 2) and all(v in WORDS for v in w)
        a=dict(correct=sum(ok.values()),format_valid=sum(valid(x) for x in pred.values()),total=64,screen=sum(ok.values())>=48)
        if k=="membership":
            pairs={}
            for r in subset:pairs.setdefault(r["pair"],[]).append(r["id"])
            a.update(yes_correct=sum(ok[r["id"]] for r in subset if r["gold"]=="Yes"),no_correct=sum(ok[r["id"]] for r in subset if r["gold"]=="No"),pairs_both=sum(all(ok[i] for i in ids) for ids in pairs.values()))
            a["screen"]=a["screen"] and min(a["yes_correct"],a["no_correct"],a["pairs_both"])>=20
        results[k]=a
    return dict(scores=results,all_primitive_screens=all(x["screen"] for x in results.values()),input_tokens=sum(r["input_tokens"] for r in records),output_tokens=sum(r["output_tokens"] for r in records),seconds=sum(r["seconds"] for r in records))
def score(root,paths,out):
    root=Path(root);m=json.loads((root/"manifest.json").read_text());p=root/"labels.json";require(sha(p)==m["labels_sha"],"LABEL_SHA")
    rows=json.loads(p.read_text());validate(rows)
    require(rows==build(m["seed"]),"REGENERATION")
    arms={a:assess(rows,[json.loads(s) for s in Path(f).read_text().splitlines()],a) for a,f in zip(MODELS,paths)}
    # A prospective useful difference requires >=8 additional correct answers
    # for at least two primitives, all screens for alternative, no drop >3.
    diffs={k:arms["qwen500"]["scores"][k]["correct"]-arms["smol135"]["scores"][k]["correct"] for k in KINDS}
    result=dict(scope="new synthetic public-run screening cohort; not independent curator confirmation",arms=arms,alternative_signal=arms["qwen500"]["all_primitive_screens"] and sum(d>=8 for d in diffs.values())>=2 and min(diffs.values())>=-3,differences=diffs,prediction_sha={a:sha(f) for a,f in zip(MODELS,paths)},labels_sha=m["labels_sha"],training_authorized=False,promotion_authorized=False)
    write(out,result);print(json.dumps(result,indent=2))
def selftest():
    rows=build(1234);validate(rows)
    require(rows==build(1234) and rows!=build(1235),"SEED")
    for arm in MODELS:
        records=[dict(id=r["id"],arm=arm,revision=MODELS[arm][1],prompt_sha=digest(r["prompt"]),raw=r["gold"],raw_sha=digest(r["gold"]),input_tokens=1,output_tokens=1,seconds=0) for r in rows]
        require(assess(rows,records,arm)["all_primitive_screens"],"ORACLE_SCREEN")
        bad=[dict(r) for r in records];bad[0]["raw"]="wrong"
        for test in (bad,records[:-1],records+[records[0]]):
            try:assess(rows,test,arm)
            except ValueError:pass
            else:raise ValueError("NEGATIVE_CONTROL")
        constant=[dict(r,raw="Yes",raw_sha=digest("Yes")) for r in records]
        require(not assess(rows,constant,arm)["all_primitive_screens"],"CONSTANT_CONTROL")
    print("SELFTEST OK")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","freeze","infer","score"]);p.add_argument("--root");p.add_argument("--arm");p.add_argument("--out");p.add_argument("--paths",nargs=2);a=p.parse_args()
    if a.cmd=="selftest":selftest()
    elif a.cmd=="freeze":freeze(a.root)
    elif a.cmd=="infer":infer(a.root,a.arm,a.out)
    else:score(a.root,a.paths,a.out)
