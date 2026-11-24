"""PROPOSAL-03: neutral vs targeted graph construction, frozen weights."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time
from math import comb
from proposal02 import decode,digits_for,digest,MODEL,REV,TEMP
from corpus_gate import identities,motif
from teacher import admit

N=32
SEED=20261126
NEUTRAL=("Invent a directed binary relation on A,B,C. Return exactly nine bits "
         "of its adjacency matrix in row-major A,B,C order, 1=edge present, "
         "0=absent. Choose every bit yourself. No spaces or explanation.")

def desired(seed):
    if not SEED<=seed<SEED+N:
        raise ValueError("BAD_SEED")
    return format((seed-SEED)%8,"03b")

def prompt(arm,seed):
    if arm=="N":
        return NEUTRAL
    if arm!="T":
        raise ValueError("BAD_ARM")
    requirements=[f"The edge {a} to {b} must be {'present' if v=='1' else 'absent'}."
                  for (a,b),v in zip(("AB","BC","AC"),desired(seed))]
    return NEUTRAL+" "+" ".join(requirements)

def constrained9(model,inputs,tok,digits,torch):
    sequence=inputs["input_ids"]
    generated=[]
    masses=[]
    choices=[]
    for pos in range(9):
        alphabet='01'
        ids=[digits[d] for d in alphabet]
        logits=model(input_ids=sequence, use_cache=False).logits[0,-1].float()/TEMP
        selected=logits[ids]
        probs=torch.softmax(selected,dim=0)
        mass=torch.exp(torch.logsumexp(selected,dim=0)-torch.logsumexp(logits,dim=0)).item()
        if not bool(torch.isfinite(probs).all()) or not 0<mass<=1.000001:
            raise ValueError("NONFINITE_CONSTRAINED_DISTRIBUTION")
        k=int(torch.multinomial(probs,1).item())
        generated.append(ids[k])
        choices.append(alphabet[k])
        masses.append(mass)
        sequence=torch.cat((sequence,torch.tensor([[ids[k]]],dtype=sequence.dtype)),dim=1)
    raw=tok.decode(generated,skip_special_tokens=False,clean_up_tokenization_spaces=False)
    if raw!="".join(choices):
        raise ValueError("GRAMMAR_ROUNDTRIP_FAILURE")
    return generated,raw,masses

def summarize(rows,sensor):
    expected={(a,SEED+i) for a in ("N","T") for i in range(N)}
    if len(rows)!=2*N or {(r["arm"],r["seed"]) for r in rows}!=expected:
        raise ValueError("INCOMPLETE_OR_DUPLICATE_ATTEMPTS")
    arms={}
    paired={}
    for arm in ("N","T"):
        counts=Counter({format(i,"03b"):0 for i in range(8)})
        matches=counts.copy()
        graphs=set()
        tasks=set()
        bits=0
        exact=0
        positives=0
        samples=[r for r in rows if r["arm"]==arm]
        results=[]
        for r in samples:
            seed=r["seed"]
            if r["raw_sha256"]!=digest(r["raw"]) or r["prompt_sha256"]!=digest(prompt(arm,seed)):
                raise ValueError("DIGEST_MISMATCH")
            if len(r["raw"])!=9 or any(c not in "01" for c in r["raw"]):
                raise ValueError("BAD_RAW")
            if len(r["token_ids"])!=9 or len(r["allowed_mass"])!=9 or any(not 0<m<=1.000001 for m in r["allowed_mass"]):
                raise ValueError("BAD_TRACE")
            p=decode(r["raw"]+"012")
            label=json.loads(admit(p,sensor)["target"])
            actual=motif(p)
            if actual!="".join(str(int(label[k])) for k in ("xy","yz","xz")):
                raise ValueError("ORACLE_DISAGREEMENT")
            target=desired(seed)
            correct=actual==target
            exact+=int(correct)
            bits+=sum(a==b for a,b in zip(actual,target))
            counts[actual]+=1
            matches[target]+=int(correct)
            positives+=int(label["violates"])
            g,k=identities(p)
            graphs.add(g)
            tasks.add(k)
            paired.setdefault(seed,{})[arm]=correct
            results.append({"seed":seed,"target":target,"actual":actual,"match":correct,"packet":p})
        arms[arm]={"exact":exact,"bits_correct":bits,"motifs":dict(counts),
                   "matches_by_target":dict(matches),"unique_graphs":len(graphs),"unique_tasks":len(tasks),
                   "violations":positives,"input_tokens":sum(r["input_tokens"] for r in samples),
                   "output_tokens":sum(len(r["token_ids"]) for r in samples),
                   "seconds":sum(r["seconds"] for r in samples),"results":results}
    n,t=arms["N"]["exact"],arms["T"]["exact"]
    contingency=Counter({k:0 for k in ("both","N_only","T_only","neither")})
    for p in paired.values():
        contingency["both" if p["N"] and p["T"] else "N_only" if p["N"] else "T_only" if p["T"] else "neither"]+=1
    return {"arms":arms,"paired":dict(contingency),"targeted_minus_neutral":t-n,
            "uniform_expected":N/8,"uniform_tail_at_T":sum(comb(N,k)*(1/8)**k*(7/8)**(N-k) for k in range(t,N+1)),
            "exploratory_feasibility":t>=16 and t-n>=8 and all(v>=1 for v in arms["T"]["matches_by_target"].values()),
            "weight_updates":0,"training_authorized":False,"holdout_accessed":False}

def run(output):
    import torch
    import transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    import omega_hybrid_exact_sensor as sensor
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    path=output/"raw.jsonl"
    rows=[]
    with path.open("x",encoding="utf-8") as log:
        torch.set_num_threads(2)
        tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
        model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,
                  torch_dtype=torch.float32).to("cpu").eval()
        if model.config._commit_hash!=REV:
            raise ValueError("MODEL_REVISION_NOT_CONFIRMED")
        digits=digits_for(tok)
        for i in range(N):
            seed=SEED+i
            for arm in ("N","T"):
                query=prompt(arm,seed)
                rendered=tok.apply_chat_template([{"role":"user","content":query}],tokenize=False,add_generation_prompt=True)
                inputs=tok(rendered,return_tensors="pt",add_special_tokens=False)
                torch.manual_seed(seed)
                start=time.monotonic()
                with torch.inference_mode():
                    ids,raw,masses=constrained9(model,inputs,tok,digits,torch)
                row={"arm":arm,"seed":seed,"raw":raw,"raw_sha256":digest(raw),
                     "prompt_sha256":digest(query),"rendered_prompt_sha256":digest(rendered),
                     "token_ids":ids,"allowed_mass":masses,"input_tokens":int(inputs["input_ids"].shape[1]),
                     "seconds":time.monotonic()-start}
                rows.append(row)
                log.write(json.dumps(row)+"\n")
                log.flush()
                print("PROPOSAL03",arm,i+1,"of",N,flush=True)
    result=summarize(rows,sensor)
    result.update(model=MODEL,revision=REV,digit_token_ids=digits,temperature=TEMP,
                  torch=torch.__version__,transformers=transformers.__version__,
                  raw_file_sha256=sha256(path.read_bytes()).hexdigest())
    (output/"report.json").write_text(json.dumps(result,indent=2)+"\n")
    for a,r in result["arms"].items():
        print("RESULT",a,"exact",r["exact"],"bits",r["bits_correct"],"motifs",r["motifs"],flush=True)
    print("PAIRED",result["paired"],"signal",result["exploratory_feasibility"],flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
