"""Frozen elementary copy task and narrow adapter to the existing atomic LoRA trainer."""
import argparse,hashlib,json,random,re,sys,time
from collections import Counter
from pathlib import Path

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REV="7ae557604adf67be50417f59c2c2f167def9a775"
SEED=202611250606
MAX_LENGTH=192
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def sha_file(p):return digest(Path(p).read_bytes())
def make():
    rng=random.Random(SEED);seen=set();train=[];test=[]
    def add(dst,group,alpha,n,k):
        for _ in range(k):
            for attempt in range(10000):
                s=tuple(rng.choice(alpha) for _ in range(n))
                if s not in seen:break
            else:raise RuntimeError("exhausted")
            seen.add(s);seq=" ".join(s)
            dst.append(dict(id=digest(seq.encode())[:24],packet=seq,label=seq,group=group,n=n))
    for n,k in [(2,32),(3,48),(4,48)]:add(train,"train","ABCDEFGH",n,k)
    for n,k in [(2,16),(3,24),(4,24)]:add(test,"id","ABCDEFGH",n,k)
    for n in (5,6):add(test,"length","ABCDEFGH",n,16)
    for n in (3,4):add(test,"alphabet","IJKLMNOP",n,16)
    for s in "ABCDEFGHIJKLMNOP":test.append(dict(id=digest(s.encode())[:24],packet=s,label=s,group="singleton",n=1))
    rng.shuffle(train);rng.shuffle(test)
    validate(train,"train");validate(test,"test")
    assert not {r["packet"] for r in train}&{r["packet"] for r in test}
    return train,test
def validate(rows,kind):
    expected={"train":{("train",2):32,("train",3):48,("train",4):48},"test":{("id",2):16,("id",3):24,("id",4):24,("length",5):16,("length",6):16,("alphabet",3):16,("alphabet",4):16,("singleton",1):16}}[kind]
    assert Counter((r["group"],r["n"]) for r in rows)==expected
    assert len({r["id"] for r in rows})==len(rows)
    assert len({r["packet"] for r in rows})==len(rows)
    for r in rows:
        s=r["packet"];alpha="IJKLMNOP" if r["group"]=="alphabet" else "ABCDEFGHIJKLMNOP" if r["group"]=="singleton" else "ABCDEFGH"
        assert s==r["label"] and r["id"]==digest(s.encode())[:24]
        assert len(s.split(" "))==r["n"] and all(len(x)==1 and x in alpha for x in s.split(" "))
def question(seq,view):
    if view=="trained":return "Copy the following sequence exactly. Keep the same letters, order, and spaces. Output only the sequence. Input: "+seq
    if view=="paraphrase":return "Repeat these symbols in their original order, separated by single spaces, without any explanation: "+seq
    raise ValueError(view)
def chat(tok,packet,view):
    # Legacy trainer passes its historical view name; map only this training call.
    if view=="edges":view="trained"
    return tok.apply_chat_template([{"role":"user","content":question(packet,view)}],tokenize=False,add_generation_prompt=True)
def read_frozen(path,expected,kind):
    assert sha_file(path)==expected
    rows=json.loads(Path(path).read_text());validate(rows,kind);return rows
def exact(raw,gold):return raw.strip()==gold
def distance(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        nxt=[i]
        for j,y in enumerate(b,1):nxt.append(min(row[j]+1,nxt[-1]+1,row[j-1]+(x!=y)))
        row=nxt
    return row[-1]
def preflight():
    train,test=make()
    assert exact(" A B ","A B") and not exact("B A","A B") and not exact("A C","A B") and not exact("A  B","A B")
    assert distance(["A","B"],["B","A"])==2
    return train,test
def freeze(out):
    train,test=preflight();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    for kind,rows in (("train",train),("test",test)):
        p=out/kind;p.mkdir();(p/"data.json").write_bytes(canonical(rows))
        h=sha_file(p/"data.json");(p/"sha256.txt").write_text(h+"\n");print("COPY_FROZEN",kind,len(rows),h,flush=True)
def train(path,expected,out):
    # Reuse original implementation; preserve the step count, optimizer, LoRA and audit.
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"foundations01"))
    import atomic_sft_train as legacy
    legacy.MODEL=MODEL;legacy.REV=REV;legacy.SEED=SEED;legacy.MAX_LENGTH=MAX_LENGTH
    legacy.read_frozen=read_frozen;legacy.chat=chat;legacy.target=lambda label:label
    rows=read_frozen(path,expected,"train");assert len(rows)==128
    legacy.train(path,expected,out)
def evaluate(path,expected,adapter,out):
    rows=read_frozen(path,expected,"test")
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2);torch.manual_seed(SEED)
    adapter=Path(adapter);manifest=json.loads((adapter/"manifest.json").read_text())
    assert manifest["model"]==MODEL and manifest["revision"]==REV and manifest["steps"]==256 and manifest["weight_delta_L2"]>0
    for name,h in manifest["adapter_sha256"].items():assert sha_file(adapter/"adapter"/name)==h
    assert sha_file(adapter/"steps.jsonl")==manifest["steps_sha256"]
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==REV
    model=PeftModel.from_pretrained(base,adapter/"adapter",is_trainable=False).eval()
    model.config.use_cache=True
    out=Path(out);out.mkdir(parents=True,exist_ok=False);records=[]
    from contextlib import nullcontext
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ("base","lora"):
            with model.disable_adapter() if arm=="base" else nullcontext():
                for view in ("trained","paraphrase"):
                    for r in rows:
                        p=chat(tok,r["packet"],view)
                        x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
                        assert n+32<=MAX_LENGTH
                        start=time.monotonic()
                        with torch.inference_mode():y=model.generate(**x,do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id)[0,n:].tolist()
                        raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                        rec=dict(arm=arm,view=view,id=r["id"],raw=raw,prompt_sha256=digest(question(r["packet"],view).encode()),input_tokens=n,output_tokens=len(y),seconds=time.monotonic()-start)
                        records.append(rec);log.write(json.dumps(rec,sort_keys=True)+"\n");log.flush()
                    print("COPY_EVAL_STAGE",arm,view,len(records),flush=True)
    result=score(rows,records);result.update(model=MODEL,revision=REV,train_sha256=manifest["train_sha256"],test_sha256=expected,training_steps=manifest["steps"],weight_delta_L2=manifest["weight_delta_L2"],promotion_authorized=False)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("COPY_SFT_RESULT",json.dumps(result,sort_keys=True),flush=True)
def score(rows,records):
    by={r["id"]:r for r in rows};views=("trained","paraphrase");groups=("id","length","alphabet","singleton")
    expected={(a,v,r["id"]) for a in ("base","lora") for v in views for r in rows}
    assert len(records)==len(expected) and {(r["arm"],r["view"],r["id"]) for r in records}==expected
    scores={}
    for arm in ("base","lora"):
        scores[arm]={}
        for view in views:
            scores[arm][view]={}
            for group in groups:
                rr=[r for r in records if r["arm"]==arm and r["view"]==view and by[r["id"]]["group"]==group]
                for r in rr:assert r["prompt_sha256"]==digest(question(by[r["id"]]["packet"],view).encode())
                valid=lambda raw:re.fullmatch(r"[A-P]( [A-P])*",raw.strip()) is not None
                vv=[r for r in rr if valid(r["raw"])]
                scores[arm][view][group]=dict(n=len(rr),exact=sum(exact(r["raw"],by[r["id"]]["label"]) for r in rr),strict=sum(r["raw"]==by[r["id"]]["label"] for r in rr),valid=len(vv),edit_distance_sum_valid=sum(distance(r["raw"].strip().split(),by[r["id"]]["label"].split()) for r in vv),input_tokens=sum(r["input_tokens"] for r in rr),output_tokens=sum(r["output_tokens"] for r in rr),seconds=sum(r["seconds"] for r in rr))
    b,l=scores["base"],scores["lora"]
    gain=l["trained"]["id"]["exact"]-b["trained"]["id"]["exact"]
    gate=all(l[v]["id"]["exact"]>=61 and l[v]["length"]["exact"]>=30 and l[v]["alphabet"]["exact"]>=30 and l[v]["singleton"]["exact"]>=b[v]["singleton"]["exact"]-1 for v in views) and gain>=8
    return dict(scores=scores,id_gain=gain,exploratory_gate=gate,retention_long_term_tested=False,autonomous=False)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["check","freeze","train","eval"]);p.add_argument("--data");p.add_argument("--sha");p.add_argument("--out");p.add_argument("--adapter");a=p.parse_args()
    if a.mode=="check":
        t,e=preflight();print("COPY_CHECK",len(t),len(e),digest(canonical(t)),digest(canonical(e)))
    elif a.mode=="freeze":freeze(a.out)
    elif a.mode=="train":train(a.data,a.sha,a.out)
    else:evaluate(a.data,a.sha,a.adapter,a.out)
