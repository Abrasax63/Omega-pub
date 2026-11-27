"""RAW01: bounded direct-weight pilot; no output repair, tools, vote or routing."""
import argparse, itertools, json, os, random, re, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
SEED = 271126
OPS = ("equal", "not", "and", "xor")
# Balanced truth labels per operation. AND negatives vary; repeats are explicit.
PAIRS = {"equal": [(0,1),(0,0),(1,0),(1,1)],
         "not": [(1,0),(0,0),(1,0),(0,0)],
         "and": [(0,1),(1,1),(1,0),(1,1)],
         "xor": [(0,0),(0,1),(1,1),(1,0)]}
def task(op,a,b,style,tag):
    y = {"equal": int(a==b),"not":1-a,"and":a&b,"xor":a^b}[op]
    if style == "train":
        q = {"equal":f"Are {a} and {b} equal?","not":f"Boolean NOT of {a}?",
             "and":f"Boolean AND of {a} and {b}?","xor":f"Boolean XOR of {a} and {b}?"}[op]
    elif style == "heldout":
        q = {"equal":f"Do {a} and {b} have the same value?","not":f"Negate bit {a}.",
             "and":f"Are both bits {a}, {b} one?","xor":f"Is exactly one of {a}, {b} one?"}[op]
    else:
        x,z = ("blue" if a else "red"),("blue" if b else "red")
        q = {"equal":f"Are {x} and {z} the same color?",
             "not":f"NOT {x}?","and":f"{x} AND {z}?","xor":f"{x} XOR {z}?"}[op]
        q = "Here red means 0 and blue means 1. " + q
    return {"id":tag,"op":op,"style":style,"prompt":q+" Answer only 0 or 1.","target":str(y)}
def datasets():
    train=[]
    for agent in range(3):
        rows=[]
        for op in OPS:
            pairs=PAIRS[op][:]
            random.Random(SEED+agent+sum(map(ord,op))).shuffle(pairs)
            for i,(a,b) in enumerate(pairs):
                # Same truth-table curriculum, independently ordered, no artificial roles.
                rows.append(task(op,a,b,"train",f"train-{agent}-{op}-{i}"))
        random.Random(SEED+agent).shuffle(rows)
        train.append(rows)
    exams=[task(op,a,b,style,f"{style}-{op}-{i}") for style in ("heldout","transfer")
           for op in OPS for i,(a,b) in enumerate(PAIRS[op])]
    assert not ({x["prompt"] for s in train for x in s}&{x["prompt"] for x in exams})
    for s in train+[exams]:
        for op in OPS:
            assert sum(x["target"]=="1" for x in s if x["op"]==op)*2==sum(x["op"]==op for x in s)
    return train,exams

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="raw01-results")
    p.add_argument("--fixture",action="store_true")
    args=p.parse_args()
    train,exams=datasets()
    if args.fixture:
        print("fixture OK: 48 train presentations, 32 exam presentations; repeated truth inputs disclosed")
        return
    torch.manual_seed(SEED)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    revision=HfApi().model_info(MODEL).sha
    tok=AutoTokenizer.from_pretrained(MODEL,revision=revision,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=revision,trust_remote_code=False,torch_dtype=torch.float32)
    model.config.use_cache=False
    for p0 in model.parameters(): p0.requires_grad_(False)
    block=model.model.layers[-1]
    for p0 in block.parameters(): p0.requires_grad_(True)
    params=list(block.parameters())
    def snap(): return {k:v.detach().clone() for k,v in block.state_dict().items()}
    def load(s): block.load_state_dict(s)
    base=snap()
    manifest={"model":MODEL,"revision":revision,"seed":SEED,"torch":torch.__version__,
              "trainable":sum(x.numel() for x in params),"total":sum(x.numel() for x in model.parameters()),
              "train":train,"exams":exams,"scope":"last transformer block only; 3 seeds of curriculum ordering, not independent initial weights",
              "limitations":"Repeated small truth-table inputs, one model revision, one initialization; no peer weight learning; no causal claim."}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    def emit(file,row):
        with (out/file).open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    def prompt_ids(q):
        return tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,return_tensors="pt")
    def train_arm(name,rows):
        load(base); model.train()
        optim=torch.optim.AdamW(params,lr=1e-5,weight_decay=0)
        for i,row in enumerate(rows):
            prefix=prompt_ids(row["prompt"])
            target=tok(row["target"],add_special_tokens=False,return_tensors="pt").input_ids
            ids=torch.cat([prefix,target,torch.tensor([[tok.eos_token_id]])],dim=1)
            labels=ids.clone(); labels[:,:prefix.shape[1]]=-100
            optim.zero_grad(set_to_none=True)
            loss=model(input_ids=ids,labels=labels,use_cache=False).loss
            if not torch.isfinite(loss): raise RuntimeError("nonfinite loss")
            loss.backward()
            grad=torch.nn.utils.clip_grad_norm_(params,1.0)
            if not torch.isfinite(grad): raise RuntimeError("nonfinite gradient")
            optim.step()
            emit("train.jsonl",{"arm":name,"step":i+1,"id":row["id"],"loss":loss.item(),"grad_norm":float(grad)})
        state=snap()
        delta=sum(float((state[k]-base[k]).square().sum()) for k in state)**0.5
        emit("train.jsonl",{"arm":name,"steps":len(rows),"delta_l2":delta})
        assert delta>0
        return state
    def answer(state,q):
        load(state);model.eval()
        ids=prompt_ids(q)
        with torch.no_grad():
            gen=model.generate(ids,attention_mask=torch.ones_like(ids),do_sample=False,max_new_tokens=5,
                               use_cache=True,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
        suffix=gen.sequences[0,ids.shape[1]:]
        raw=tok.decode(suffix,skip_special_tokens=True)
        scores=gen.scores[0][0].float().log_softmax(-1)
        vals={}
        for label in ("0","1"):
            t=tok(label,add_special_tokens=False).input_ids
            if len(t)==1: vals[label]=float(scores[t[0]])
        return {"raw":raw,"token_ids":suffix.tolist(),"first_logp":vals}
    def record(arm,row,agent,round_,q,ans):
        emit("answers.jsonl",{"arm":arm,"id":row["id"],"op":row["op"],"style":row["style"],
             "agent":agent,"round":round_,"prompt":q,"target":row["target"],
             **ans,"correct":ans["raw"].strip()==row["target"]})
    for row in exams:
        q=row["prompt"];record("base",row,0,0,q,answer(base,q))
    solo=train_arm("solo",sum(train,[]))
    states=[train_arm(f"agent-{i}",s) for i,s in enumerate(train)]
    # Connected and independent use the exact same 3 trained states and initial outputs.
    # Solo control uses the same total optimization steps and six logical calls per exam.
    for row in exams:
        q=row["prompt"]
        for arm,ss in (("solo",[solo]*3),("independent",states)):
            initial=[answer(s,q) for s in ss]
            for i,ans in enumerate(initial):
                record(arm,row,i,0,q,ans)
                if arm=="independent": record("connected",row,i,0,q,ans)
            for i,s in enumerate(ss):
                # Equal number of response slots; no correctness information.
                own=json.dumps(initial[i]["raw"],ensure_ascii=False)
                q2=q+"\nPrevious answer: "+own+"\nOther answers: "+own+" ; "+own+"\nAnswer again."
                record(arm,row,i,1,q2,answer(s,q2))
                if arm=="independent":
                    peers=[json.dumps(initial[j]["raw"],ensure_ascii=False) for j in range(3) if j!=i]
                    q3=q+"\nPrevious answer: "+own+"\nOther answers: "+" ; ".join(peers)+"\nAnswer again."
                    record("connected",row,i,1,q3,answer(s,q3))
    rows=[json.loads(line) for line in (out/"answers.jsonl").read_text().splitlines()]
    summary={}
    for arm in ("base","solo","independent","connected"):
        summary[arm]={}
        for style in ("heldout","transfer"):
            subset=[r for r in rows if r["arm"]==arm and r["style"]==style and r["round"]==(0 if arm=="base" else 1)]
            summary[arm][style]={"correct":sum(r["correct"] for r in subset),"n":len(subset),
                "invalid":sum(r["raw"].strip() not in ("0","1") for r in subset)}
    (out/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__": main()
