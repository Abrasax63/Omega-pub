"""RUNNER11: isolated candidate arm and Qwen architecture smoke.
CLI intentionally only tests a randomly initialized miniature Qwen.
No pretrained weights downloaded, no holdout accessed, no release.
"""
import argparse, hashlib, json, math, time
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import loop09 as l
import devbase08 as d
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def json_write(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False))
def tensor_hash(params):
    h=hashlib.sha256()
    for name,p in params:
        h.update(name.encode());h.update(str(p.shape).encode());h.update(str(p.dtype).encode())
        h.update(p.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()
def evaluate_dev(model,tok,rows):
    import torch
    c.validate(rows,"dev");mode=model.training;model.eval();records=[]
    try:
        for r in rows:
            p=tok.apply_chat_template([{"role":"user","content":r["prompt"]}],tokenize=False,add_generation_prompt=True)
            x=tok(p,return_tensors="pt",add_special_tokens=False);n=x["input_ids"].shape[1]
            need(n+16<=t.MAX_LENGTH,"EVAL_CONTEXT")
            start=time.monotonic()
            with torch.inference_mode():ids=model.generate(**x,max_new_tokens=16,do_sample=False,pad_token_id=tok.eos_token_id)[0,n:].tolist()
            raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
            records.append(dict(id=r["id"],revision=c.REV,prompt_sha=digest(r["prompt"]),raw=raw,raw_sha=digest(raw),input_tokens=n,output_tokens=len(ids),seconds=time.monotonic()-start))
        return d.score(rows,records)["scores"],records
    finally:model.train(mode)
def checked_plan(tok,train,plan,expected):
    c.validate(train,"train")
    need(plan["strategy"] in t.STRATEGIES and len(plan["batches"])==128 and all(len(z)==2 for z in plan["batches"]),"PLAN")
    idx={r["id"]:r for r in train};ids=[i for batch in plan["batches"] for i in batch]
    need(len(ids)==len(set(ids))==256 and set(ids)<=set(idx),"TRAIN_ONLY")
    from collections import Counter
    counts=Counter(idx[i]["kind"] for i in ids)
    need(all(counts[k]==2*plan["skill_pairs"][k] and counts[k]>=32 for k in c.KINDS),"QUOTAS")
    if plan["strategy"]!="supervised":need(all(idx[z[0]]["pair"]==idx[z[1]]["pair"] for z in plan["batches"]),"PAIR_BATCH")
    enc=t.prepare(tok,train);need(t.budget(enc,plan)==expected,"BUDGET_CHANGED")
    return enc
def save_adapter(model,out):
    out=Path(out);out.mkdir(exist_ok=False)
    model.save_pretrained(out,safe_serialization=True)
    files={p.name:sha(p) for p in out.iterdir() if p.is_file()}
    need("adapter_model.safetensors" in files and "adapter_config.json" in files,"ADAPTER_FILES")
    return files
def run_candidate(model,tok,train,dev,plan,expected,out):
    """Full single-block candidate function for future reviewed release.
    Must be called with a fresh isolated pinned base and matching frozen plan.
    No CLI for this function; caller must establish independent evaluation gate.
    """
    import torch
    from peft import get_peft_model
    need(model.config._commit_hash==c.REV,"BASE_REVISION")
    c.validate(dev,"dev");need(not set(r["id"] for r in train)&set(r["id"] for r in dev),"SPLIT")
    need(all(p.device.type=="cpu" for p in model.parameters()),"CPU_ONLY")
    enc=checked_plan(tok,train,plan,expected)
    out=Path(out);out.mkdir(exist_ok=False)
    torch.manual_seed(t.SEED);torch.set_num_threads(2)
    model.config.use_cache=False
    model=get_peft_model(model,t.lora_config())
    named=[(n,p) for n,p in model.named_parameters() if p.requires_grad];params=[p for _,p in named]
    need(named and all("lora_" in n for n,_ in named),"TRAINABLE_SCOPE")
    frozen=[(n,p) for n,p in model.named_parameters() if not p.requires_grad]
    initial=tensor_hash(named);base=tensor_hash(frozen)
    opt=torch.optim.AdamW(params,lr=0.0002,weight_decay=0.0)
    observations=[]
    def ev():
        scores,records=evaluate_dev(model,tok,dev)
        json_write(out/("dev-%d.json"%len(observations)),records)
        observations.append(scores);return scores
    batches=[t.collate(tok,enc,ids) for ids in plan["batches"]]
    tx=l.reversible_block(model,opt,params,batches,lambda b:t.optimizer_step(model,opt,params,b,plan["strategy"]),ev)
    final=tensor_hash(named);need(tensor_hash(frozen)==base,"FROZEN_WEIGHTS_CHANGED")
    if tx["rolled_back"]:need(final==initial and not opt.state,"ROLLBACK_STATE")
    else:need(final!=initial,"NO_WEIGHT_CHANGE")
    adapter=save_adapter(model,out/"adapter") if not tx["rolled_back"] else None
    report=dict(strategy=plan["strategy"],revision=c.REV,budget=expected,initial_adapter_sha=initial,final_adapter_sha=final,frozen_base_sha=base,transaction=tx,adapter_files=adapter,scope="development-only candidate; no independent qualification",promotion_authorized=False)
    json_write(out/"manifest.json",report);return report
def selftest(out):
    import torch
    from transformers import Qwen2Config,Qwen2ForCausalLM
    from peft import get_peft_model,PeftModel
    torch.manual_seed(7);torch.set_num_threads(2)
    cfg=Qwen2Config(vocab_size=32,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=2,max_position_embeddings=64,bos_token_id=1,eos_token_id=2,pad_token_id=0,use_cache=False)
    raw=Qwen2ForCausalLM(cfg);base_state={k:v.detach().clone() for k,v in raw.state_dict().items()}
    model=get_peft_model(raw,t.lora_config());named=[(n,p) for n,p in model.named_parameters() if p.requires_grad];params=[p for _,p in named]
    need(named and all("lora_" in n for n,_ in named),"LORA_SCOPE")
    frozen=[(n,p) for n,p in model.named_parameters() if not p.requires_grad]
    before_hash=tensor_hash(named);base_hash=tensor_hash(frozen)
    opt=torch.optim.AdamW(params,lr=.01)
    X=torch.tensor([[1,5,9,2],[1,5,8,2],[1,6,8,2],[1,6,9,2]])
    Y=X.clone();Y[:,:2]=-100
    batch=dict(input_ids=X,labels=Y,attention_mask=torch.ones_like(X))
    step=lambda b:t.optimizer_step(model,opt,params,b,"contrastive")
    before={k:dict(correct=16,both_pairs=4) for k in c.KINDS}
    bad={k:dict(v) for k,v in before.items()};bad["copy"]["correct"]=15
    good={k:dict(v) for k,v in before.items()};good["select"]=dict(correct=18,both_pairs=5)
    seq=iter((before,bad));reject=l.reversible_block(model,opt,params,[batch],step,lambda:next(seq))
    need(reject["rolled_back"] and tensor_hash(named)==before_hash and not opt.state,"LORA_ROLLBACK")
    seq=iter((before,good));accept=l.reversible_block(model,opt,params,[batch],step,lambda:next(seq))
    need(not accept["rolled_back"] and tensor_hash(named)!=before_hash and tensor_hash(frozen)==base_hash,"LORA_UPDATE")
    out=Path(out);out.mkdir(exist_ok=False)
    files=save_adapter(model,out/"adapter")
    restored=Qwen2ForCausalLM(cfg);restored.load_state_dict(base_state)
    restored=PeftModel.from_pretrained(restored,out/"adapter",is_trainable=False)
    model.eval();restored.eval()
    with torch.inference_mode():a=model(input_ids=X).logits;b=restored(input_ids=X).logits
    need(torch.equal(a,b) or torch.allclose(a,b,atol=1e-7,rtol=1e-6),"RELOAD_LOGITS")
    report=dict(status="RANDOM_MINI_QWEN_LORA_SMOKE_OK",trainable_parameters=sum(p.numel() for p in params),rollback_exact=True,accepted_adapter_changed=True,frozen_base_unchanged=True,reload_max_logit_diff=float((a-b).abs().max()),adapter_sha256=files,decisions_source="synthetic dev scores; not a real learning result",pretrained_qwen_updates=0,training_authorized=False,promotion_authorized=False)
    json_write(out/"report.json",report);print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest"]);p.add_argument("--out",required=True);a=p.parse_args();selftest(a.out)
