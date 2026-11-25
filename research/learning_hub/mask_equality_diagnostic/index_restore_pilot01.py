"""One-epoch repair pilot; no deployment or promotion."""
import argparse,json,random,re,time,math
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import index_interference01 as ii
import copy_sft01 as c
import position_cumulative01 as pc
import instruction_control01 as ic
import position_representation as pos
import self_representation02 as sr2
SEED=202611250928
PARENT=ic.NEW
OPS=("copy","index","select")
ARMS=("base","parent","pilot")
def question(s,p,op,v):
    seq=" ".join(s)
    if op=="copy":return c.question(seq,"trained" if v==0 else "paraphrase")
    if op=="index":
        return sr2.prompt(s,"B") if v==0 else "Assign each symbol its one-based position in the list. Return only position:symbol pairs, in order, separated by single spaces. Data: "+seq
    return pc.question(seq,p,"original" if v==0 else "rephrased")
def target(s,p,op):
    return " ".join(s) if op=="copy" else pos.encode(s,"indexed") if op=="index" else s[p-1]
def make():
    rng=random.Random(SEED);t,e=c.make()
    assert c.digest(c.canonical(t))=="40d6230727371fbd3605f8b54464d19386767392a1405aa086036c9ca4c02d91"
    assert c.digest(c.canonical(e))=="34e02262decf0576b69930ef652b0a08c66a14bf827026b59719ebbb6b03b19a"
    excluded={tuple(r["packet"].split()) for r in t+e}
    excluded.update(tuple(r["seq"].split()) for r in ii.ct.corpus())
    for mod in (ii.cp,ii.pos,ii.sr1,ii.sr2,ii.sr3,ii.rd,ii.fs):
        excluded.update(tuple(r["seq"]) for r in mod.corpus())
    for r in ii.fr.corpus():
        m=re.search(r"List: ([A-H](?: [A-H])+)",r["prompt"])
        if m:excluded.add(tuple(m[1].split()))
    t,e=pc.make()
    assert c.digest(c.canonical(t))=="63a17b4f74ec01a441f0a3378998e6f9bb5eb535f591db381edffa2cb4ff5edc"
    assert c.digest(c.canonical(e))=="091dd83532072f36b030b69a0ba66ce4663b749435ba9796ceb6b33e1c492de4"
    excluded.update(tuple(r["seq"].split()) for r in t+e)
    for mod,h in ((ii.ic,"def2f1d550f7ba84c2340fdb3f03c52310ec74b84ae6e6c14b53dbe02580699c"),(ii.depth,"db067e67e4747730cc5a12e9892c75fcee6b05c35b512000401b3c0e3cec14e7"),(ii.si,"d6432ac68869dffb04902ddf36c1ebb3dc3a9643ea9bdd1760b993a5556ae794"),(ii,"1150551a9fbaf4eafabd961ae7b088fc3f743915ebe6e8fd425e51945c49a95d")):
        rows=mod.corpus();assert c.digest(c.canonical(rows))==h
        excluded.update(tuple(r["seq"].split() if isinstance(r["seq"],str) else r["seq"]) for r in rows)
    train=[];test=[]
    def add(dst,g,alpha,n,k,views,late=False):
        pp=list(range(5 if late else 1,n+1))
        pp=pp*(k//len(pp))+rng.sample(pp,k%len(pp));rng.shuffle(pp)
        letters=list(alpha)*(k//len(alpha))+rng.sample(list(alpha),k%len(alpha));rng.shuffle(letters)
        for p,a in zip(pp,letters):
            for _ in range(10000):
                s=rng.sample([x for x in alpha if x!=a],n-1);s.insert(p-1,a)
                if tuple(s) not in excluded:break
            else:raise RuntimeError("exhausted")
            excluded.add(tuple(s));sid=c.digest(c.canonical(s))[:24]
            for op in OPS:
                for v in views:
                    dst.append(dict(id=c.digest(c.canonical([s,p,op,v]))[:24],sid=sid,seq=s,p=p,op=op,view=v,group=g,gold=target(s,p,op),prompt=question(s,p,op,v)))
    for n in (3,4):add(train,"id","ABCDEFGH",n,12,(0,))
    for n in (3,4):add(test,"id","ABCDEFGH",n,8,(0,1))
    for n in (7,8):add(test,"length","ABCDEFGH",n,2,(0,1),True)
    for n in (3,4):add(test,"alphabet","IJKLMNOP",n,2,(0,1))
    rng.shuffle(train);rng.shuffle(test)
    validate(train,"train");validate(test,"test")
    assert not {r["sid"] for r in train}&{r["sid"] for r in test}
    return train,test
def validate(rows,kind):
    assert len(rows)==(72 if kind=="train" else 144)
    assert len({r["id"] for r in rows})==len(rows) and len({r["sid"] for r in rows})==24
    expected={"id":24} if kind=="train" else {"id":16,"length":4,"alphabet":4}
    for op in OPS:
        for v in ((0,) if kind=="train" else (0,1)):
            assert Counter(r["group"] for r in rows if r["op"]==op and r["view"]==v)==expected
    for r in rows:
        s,p,o,v=r["seq"],r["p"],r["op"],r["view"]
        assert 1<=p<=len(s) and len(set(s))==len(s)
        assert r["gold"]==target(s,p,o) and r["prompt"]==question(s,p,o,v)
        assert r["id"]==c.digest(c.canonical([s,p,o,v]))[:24]
        assert len({target(s,p,x) for x in OPS})==3
def freeze(out):
    out=Path(out);out.mkdir(exist_ok=False)
    for k,rows in zip(("train","test"),make()):
        d=out/k;d.mkdir();(d/"data.json").write_bytes(c.canonical(rows))
        h=c.sha_file(d/"data.json");(d/"sha256.txt").write_text(h+"\n")
        print("RESTORE_FROZEN",k,len(rows),h,flush=True)
def read(path,h,kind):
    assert c.sha_file(path)==h
    rows=json.loads(Path(path).read_text());validate(rows,kind);return rows
def load(parent):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2);torch.manual_seed(SEED)
    parent=Path(parent);m=json.loads((parent/"manifest.json").read_text())
    assert m["model"]==c.MODEL and m["revision"]==c.REV and m["steps"]==256
    assert m["adapter_sha256"]["adapter_model.safetensors"]==PARENT
    assert m["old_adapter_sha256"]==pc.OLD
    for k,h in m["adapter_sha256"].items():assert c.sha_file(parent/"adapter"/k)==h
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    base=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    assert base.config._commit_hash==c.REV
    return tok,base
def train(data,h,parent,out):
    import torch
    from peft import PeftModel
    rows=read(data,h,"train");tok,base=load(parent)
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",is_trainable=True)
    model.train();model.config.use_cache=False
    params={k:v for k,v in model.named_parameters() if v.requires_grad}
    assert params and all("lora_" in k for k in params)
    before={k:v.detach().clone() for k,v in params.items()}
    opt=torch.optim.AdamW(params.values(),lr=2e-4,weight_decay=0.0)
    out=Path(out);out.mkdir(exist_ok=False);seen=Counter();losses=[]
    with (out/"steps.jsonl").open("x") as log:
        for r in rows:
            p=pc.prefix(tok,r);s=tok(r["gold"]+tok.eos_token,add_special_tokens=False)["input_ids"]
            assert s and len(p+s)<=192
            x=torch.tensor([p+s]);labels=torch.tensor([[-100]*len(p)+s])
            opt.zero_grad(set_to_none=True);loss=model(input_ids=x,labels=labels).loss
            assert bool(torch.isfinite(loss))
            loss.backward();torch.nn.utils.clip_grad_norm_(params.values(),1.0,error_if_nonfinite=True);opt.step()
            losses.append(float(loss.detach()));seen[r["id"]]+=1
            log.write(json.dumps(dict(step=len(losses),id=r["id"],op=r["op"],loss=losses[-1],tokens=len(p+s)))+"\n");log.flush()
            if len(losses)%12==0:print("RESTORE_STEP",len(losses),losses[-1],flush=True)
    assert len(losses)==72 and len(seen)==72 and set(seen.values())=={1}
    delta=math.sqrt(sum(torch.sum((v.detach()-before[k])**2).item() for k,v in params.items()))
    assert math.isfinite(delta) and delta>0
    model.save_pretrained(out/"adapter",safe_serialization=True)
    hashes={p.name:c.sha_file(p) for p in (out/"adapter").iterdir() if p.is_file()}
    m=dict(model=c.MODEL,revision=c.REV,steps=72,parent_sha256=PARENT,train_sha256=h,weight_delta_L2=delta,trainable_parameters=sum(v.numel() for v in params.values()),adapter_sha256=hashes,steps_sha256=c.sha_file(out/"steps.jsonl"),promotion_authorized=False)
    (out/"manifest.json").write_text(json.dumps(m,indent=2))
    print("RESTORE_TRAIN_COMPLETE",json.dumps(m,sort_keys=True),flush=True)
def score(rows,records):
    by={r["id"]:r for r in rows}
    assert len(records)==432 and {(r["arm"],r["id"]) for r in records}=={(a,i) for a in ARMS for i in by}
    scores={}
    for a in ARMS:
        scores[a]={}
        for g in ("id","length","alphabet"):
            for v in (0,1):
                rr=[r for r in records if r["arm"]==a and by[r["id"]]["group"]==g and by[r["id"]]["view"]==v]
                ops={};trip={}
                for o in OPS:
                    sub=[r for r in rr if by[r["id"]]["op"]==o];conf=Counter();hits=0;faithful=0
                    for r in sub:
                        q=by[r["id"]];assert r["prompt_sha256"]==c.digest(q["prompt"].encode())
                        raw=r["raw"].strip();h=raw==q["gold"];hits+=h
                        matches=[x for x in OPS if raw==target(q["seq"],q["p"],x)]
                        conf[matches[0] if matches else "other"]+=1
                        if o=="index":
                            faithful+=raw.split()==q["gold"].split()
                        trip.setdefault(q["sid"],[]).append(h)
                    ops[o]=dict(n=len(sub),exact=hits,faithful_spacing=faithful if o=="index" else None,confusion=dict(conf),tokens=sum(r["input_tokens"]+r["output_tokens"] for r in sub),seconds=sum(r["seconds"] for r in sub))
                assert all(len(t)==3 for t in trip.values())
                scores[a][g+"_"+str(v)]=dict(ops=ops,triplets=sum(all(t) for t in trip.values()))
    def s(a,g,v,o):return scores[a][g+"_"+str(v)]["ops"][o]["exact"]
    local=all(s("pilot","id",v,"index")>=13 and s("pilot","id",v,"index")-s("parent","id",v,"index")>=8 and all(s("pilot","id",v,o)>=15 and s("pilot","id",v,o)>=s("parent","id",v,o)-1 for o in ("copy","select")) and scores["pilot"]["id_"+str(v)]["triplets"]>=12 for v in (0,1)) and s("pilot","id",0,"index")>=s("base","id",0,"index")-1
    retention=all(s("pilot",g,v,o)>=s("parent",g,v,o)-1 for g in ("length","alphabet") for v in (0,1) for o in ("copy","select"))
    return dict(scores=scores,local_gate=local,transfer_retention_gate=retention,gate=local and retention,promotion_authorized=False)
def evaluate(data,h,parent,new,out):
    import torch
    from peft import PeftModel
    rows=read(data,h,"test");train_rows,test_rows=make();assert rows==test_rows
    tok,base=load(parent);new=Path(new);m=json.loads((new/"manifest.json").read_text())
    assert m["parent_sha256"]==PARENT and m["steps"]==72 and m["weight_delta_L2"]>0 and m["train_sha256"]==c.digest(c.canonical(train_rows))
    for k,d in m["adapter_sha256"].items():assert c.sha_file(new/"adapter"/k)==d
    model=PeftModel.from_pretrained(base,Path(parent)/"adapter",adapter_name="parent",is_trainable=False)
    model.load_adapter(new/"adapter",adapter_name="pilot",is_trainable=False);model.eval();model.config.use_cache=True
    out=Path(out);out.mkdir(exist_ok=False);records=[]
    with (out/"predictions.jsonl").open("x") as log:
        for arm in ARMS:
            model.set_adapter("parent" if arm=="base" else arm);model.requires_grad_(False)
            with model.disable_adapter() if arm=="base" else nullcontext():
                for r in rows:
                    p=pc.prefix(tok,r);x=torch.tensor([p]);start=time.monotonic()
                    with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id)[0,len(p):].tolist()
                    rec=dict(arm=arm,id=r["id"],raw=tok.decode(y,skip_special_tokens=True,clean_up_tokenization_spaces=False),prompt_sha256=c.digest(r["prompt"].encode()),input_tokens=len(p),output_tokens=len(y),seconds=time.monotonic()-start)
                    records.append(rec);log.write(json.dumps(rec)+"\n");log.flush()
            print("RESTORE_EVAL_STAGE",arm,len(records),flush=True)
    result=score(rows,records);result.update(test_sha256=h,train_sha256=m["train_sha256"],training_steps=72)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True));print("INDEX_RESTORE_RESULT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["freeze","train","eval"]);p.add_argument("--data");p.add_argument("--sha");p.add_argument("--parent");p.add_argument("--new");p.add_argument("--out");a=p.parse_args()
    if a.mode=="freeze":freeze(a.out)
    elif a.mode=="train":train(a.data,a.sha,a.parent,a.out)
    else:evaluate(a.data,a.sha,a.parent,a.new,a.out)
