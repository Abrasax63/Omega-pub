"""EQUIV-PROCESS01: verified trace targets and dry-run objectives, no pretrained weight load."""
import ast,hashlib,itertools as it,json,random,sys
from collections import Counter
from pathlib import Path
import equiv_pilot_freeze as pilot
EXPECTED={"train":"5dc05b88010d320134f8a9547135875a9c23e5d6bb6b8f7ea896a2820d302947","dev":"cf43023061c3c73f4e83917a98637c9e6a76d66d3380a06adce8b59d9ae5fa6e","questions":"6c8312439e8106b22c7350a68a5d8c9ce687a03d53702034b9ba0b6cda22c45f","labels":"886a1d3f860487f4d1bd391e572dc8155d9b269768374422e7157663e9f8f0ae"}
def trace(p):
    e={tuple(sorted(x)) for x in p["edges"]};f=p["future"]
    masks=[]
    for k in ("a","b"):
        s=set(p[k]);b=pilot.blocked(s,f,e)
        bits="".join("1" if not pilot.feasible(s|{v},e) else "0" for v in f)
        assert bits=="".join("1" if v in b else "0" for v in f)
        masks.append(bits)
    return "/".join(masks)
def trace_question(p):
    q=pilot.question(p,"edges")
    old="Do a and b allow exactly the same collection of future independent sets? Answer exactly Yes or No."
    assert old in q
    return q.replace(old,"For a and b, output the blocked future vertices as two bit strings separated by a slash. Follow future list order; 1 means adding that vertex is forbidden, 0 means allowed. Output only the two strings.")
def retention():
    rng=random.Random(20270162);rows=[]
    for i in range(16):
        n=15+i%4;nodes=["v"+str(x) for x in rng.sample(range(100,999),n)]
        pairs=list(it.permutations(nodes,2));a,b=rng.choice(pairs)
        pool=[x for x in pairs if x!=(a,b)]
        e=rng.sample(pool,2*n);replacement=rng.choice([x for x in pool if x not in e])
        for label in (True,False):
            es=e[:-1]+[(a,b) if label else replacement];rng.shuffle(es)
            q="In this directed graph, does the edge "+a+" to "+b+" exist? Answer exactly Yes or No. "+json.dumps(dict(nodes=nodes,edges=es),separators=(",",":"))
            assert ((a,b) in es)==label
            rows.append(dict(domain="edge",pair="edge-"+str(i),label=label,question=q))
    # Syntax-only paired controls, no execution. Different names and literals.
    for i in range(16):
        name="f_"+str(rng.randrange(10000,99999));k=rng.randrange(2,99)
        variants=[
          (f"def {name}(x):\n    return x + {k}",f"def {name}(x)\n    return x + {k}"),
          (f"{name} = [{k}, {k+1}]",f"{name} = [{k}, {k+1})"),
          (f"if {name} > {k}:\n    pass",f"if {name} > {k}:\npass"),
          (f"{name} = ({k} + 3) * 2",f"{name} = ({k} + 3] * 2")]
        good,bad=variants[i%4]
        for label,src in ((True,good),(False,bad)):
            try:ast.parse(src);actual=True
            except SyntaxError:actual=False
            assert actual==label
            rows.append(dict(domain="syntax",pair="syntax-"+str(i),label=label,question="Is the following Python 3 code syntactically valid? Answer exactly Yes or No.\n"+src))
    for r in rows:r["id"]=pilot.sha(r["question"].encode())[:24]
    rng.shuffle(rows);assert len({r["id"] for r in rows})==64
    assert Counter((r["domain"],r["label"]) for r in rows)=={(d,l):16 for d in ("edge","syntax") for l in (True,False)}
    return rows
def freeze(out):
    out=Path(out);out.mkdir()
    rows,_=pilot.generate()
    files={"train":rows["train"],"dev":rows["dev"],"labels":rows["holdout"],"questions":[{k:r[k] for k in ("id","packet")} for r in rows["holdout"]]}
    for k,x in files.items():
        p=out/(k+".json");pilot.dump(p,x);assert pilot.sha(p.read_bytes())==EXPECTED[k]
    traces=[]
    for r in rows["train"]+rows["dev"]:
        t=trace(r["packet"])
        assert (t.split("/")[0]==t.split("/")[1])==r["label"]==pilot.oracle(r["packet"])
        traces.append(dict(id=r["id"],split="train" if r in rows["train"] else "dev",target=t))
    pilot.dump(out/"traces.json",traces)
    rr=retention();pilot.dump(out/"retention-labels.json",rr)
    pilot.dump(out/"retention-questions.json",[{k:r[k] for k in ("id","question")} for r in rr])
    manifest=dict(hashes={p.name:pilot.sha(p.read_bytes()) for p in out.glob("*.json")},trace_rows=len(traces),trace_bits=sum(len(r["target"])-1 for r in traces),retention_questions=len(rr),retention_pairs=32,training_authorized=False)
    pilot.dump(out/"process-manifest.json",manifest);print("PROCESS_FREEZE",json.dumps(manifest),flush=True)
def pack(tok,prompt,target):
    text=tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True)
    prefix=tok.encode(text,add_special_tokens=False);tail=tok.encode(target,add_special_tokens=False)+[tok.eos_token_id]
    assert prefix and tail and len(prefix)+len(tail)<=1024
    return prefix+tail,[-100]*len(prefix)+tail
def objectives(logits,targets,yes,no,arm):
    import torch
    import torch.nn.functional as F
    # Four rows: positive, negative, auxiliary positive, auxiliary negative.
    assert len(logits)==len(targets)==4 and arm in ("ordinary","contrast","process")
    def ce(indices):
        x=torch.cat([logits[i] for i in indices]);y=torch.cat([targets[i] for i in indices])
        return F.cross_entropy(x,y)
    binary=ce((0,1));aux=ce((2,3))
    odds=[logits[i][0,yes]-logits[i][0,no] for i in (0,1)]
    contrast=F.softplus(1-(odds[0]-odds[1]))
    loss=binary+(.5*contrast if arm=="contrast" else 0*contrast)+(.5*aux if arm=="process" else 0*aux)
    return loss,dict(binary=binary,aux=aux,contrast=contrast)
def gather(model,rows):
    import torch
    maxlen=max(len(ids) for ids,lab in rows)
    ids=torch.tensor([ids+[0]*(maxlen-len(ids)) for ids,lab in rows])
    mask=torch.tensor([[1]*len(ids)+[0]*(maxlen-len(ids)) for ids,lab in rows])
    labels=torch.tensor([lab+[-100]*(maxlen-len(lab)) for ids,lab in rows])
    out=model(input_ids=ids,attention_mask=mask).logits
    logits=[];targets=[]
    for i in range(len(rows)):
        keep=labels[i,1:]!=-100
        logits.append(out[i,:-1][keep]);targets.append(labels[i,1:][keep])
    return logits,targets
def dryrun(folder,out):
    import torch
    from transformers import AutoTokenizer,LlamaConfig,LlamaForCausalLM
    from peft import LoraConfig,get_peft_model
    folder=Path(folder);m=json.loads((folder/"process-manifest.json").read_text())
    for name,h in m["hashes"].items():
        # Training dry run intentionally only receives train/dev/traces/manifest.
        p=folder/name
        if p.exists():assert pilot.sha(p.read_bytes())==h
    assert not (folder/"labels.json").exists() and not (folder/"questions.json").exists()
    assert not (folder/"retention-labels.json").exists()
    tok=AutoTokenizer.from_pretrained(pilot.MODEL,revision=pilot.REV,trust_remote_code=False)
    cand={k:tok.encode(k,add_special_tokens=False) for k in ("Yes","No")}
    assert all(len(v)==1 and tok.decode(v)==k for k,v in cand.items())
    train=json.loads((folder/"train.json").read_text());dev=json.loads((folder/"dev.json").read_text())
    traces={r["id"]:r["target"] for r in json.loads((folder/"traces.json").read_text())}
    lengths=Counter();pairs=Counter()
    for r in train+dev:
        p=r["packet"];gold="Yes" if r["label"] else "No"
        for k,q,t in (("binary",pilot.question(p,"edges"),gold),("aux",trace_question(p),traces[r["id"]])):
            ids,labels=pack(tok,q,t);keep=[x for x in labels if x!=-100]
            assert keep==tok.encode(t,add_special_tokens=False)+[tok.eos_token_id]
            if k=="binary":assert keep[0]==cand[gold][0]
            lengths[k+"_input"]+=len(ids);lengths[k+"_target"]+=len(keep);lengths["max"]=max(lengths["max"],len(ids))
        pairs[r["pair"]]+=1
    assert len(pairs)==104 and set(pairs.values())=={2}
    torch.set_num_threads(2)
    # Test exact objective gradients without training any pretrained model.
    y=[torch.tensor([1,3]),torch.tensor([2,3]),torch.tensor([4,5,3]),torch.tensor([5,4,3])]
    grads={}
    for arm in ("ordinary","contrast","process"):
        x=[torch.zeros(len(t),8,requires_grad=True) for t in y]
        loss,parts=objectives(x,y,1,2,arm);loss.backward()
        aux=sum(float(t.grad.abs().sum()) for t in x[2:])
        assert torch.isfinite(loss) and (aux>0)==(arm=="process")
        grads[arm]=dict(loss=float(loss),aux_grad=aux,positive_yes_grad=float(x[0].grad[0,1]),negative_yes_grad=float(x[1].grad[0,1]))
    assert grads["contrast"]["positive_yes_grad"]<grads["ordinary"]["positive_yes_grad"]
    assert grads["contrast"]["negative_yes_grad"]>grads["ordinary"]["negative_yes_grad"]
    # Tiny RANDOM model only; exercise real PEFT and causal alignment.
    fixture=[([7,8,9,1,3],[-100,-100,-100,1,3]),([7,9,8,2,3],[-100,-100,-100,2,3]),([8,9,4,5,3],[-100,-100,4,5,3]),([9,8,5,4,3],[-100,-100,5,4,3])]
    tiny={}
    for arm in ("ordinary","contrast","process"):
        torch.manual_seed(20270160)
        cfg=LlamaConfig(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=2,max_position_embeddings=64)
        model=get_peft_model(LlamaForCausalLM(cfg),LoraConfig(r=8,lora_alpha=16,target_modules=["q_proj","v_proj"],lora_dropout=0,bias="none",task_type="CAUSAL_LM"))
        before={n:p.detach().clone() for n,p in model.named_parameters()};params=[p for p in model.parameters() if p.requires_grad]
        opt=torch.optim.AdamW(params,lr=1e-4);ls,ts=gather(model,fixture)
        assert all(torch.equal(t,z) for t,z in zip(ts,y))
        loss,_=objectives(ls,ts,1,2,arm);loss.backward();opt.step()
        change=sum(float((p.detach()-before[n]).square().sum()) for n,p in model.named_parameters() if p.requires_grad)
        assert change>0 and all(torch.equal(p,before[n]) for n,p in model.named_parameters() if not p.requires_grad)
        tiny[arm]=dict(loss=float(loss.detach()),adapter_delta_L2=change**.5,trainable=sum(p.numel() for p in params),input_tokens=sum(len(x[0]) for x in fixture))
    result=dict(token_checks=dict(lengths),pairs=len(pairs),gradient_checks=grads,tiny_random_fixture=tiny,pretrained_weights_loaded=False,training_authorized=False)
    pilot.dump(Path(out),result);print("PROCESS_DRYRUN",json.dumps(result),flush=True)
if __name__=="__main__":
    if sys.argv[1]=="freeze":freeze(sys.argv[2])
    elif sys.argv[1]=="dryrun":dryrun(*sys.argv[2:])
    else:raise ValueError("stage")
