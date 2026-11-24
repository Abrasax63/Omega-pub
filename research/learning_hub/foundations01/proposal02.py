"""PROPOSAL-02: paired compact-output experiment, no gradients or holdout."""
import argparse
from collections import Counter
from hashlib import sha256
import itertools
import json
from pathlib import Path
import re
import time

from corpus_gate import identities, motif, MOTIFS
from teacher import admit
from proposal_pilot import MODEL, REV

N=16
SEED=20261125
TEMP=0.8
PROMPT=("Invent a directed binary relation on A,B,C and an ordered triple of nodes to inspect. "
        "Return exactly 12 digits, no spaces or explanation: first 9 bits of the adjacency matrix "
        "in row-major A,B,C order (1=edge present, 0=absent), then 3 node indices "
        "(0=A,1=B,2=C). Choose every bit and index yourself. Repetition of nodes is allowed. "
        "Do not give any answer to the mathematical query.")

def digest(s):
    return sha256(s.encode("utf-8")).hexdigest()

def allowed(position):
    if type(position) is not int or not 0<=position<12:
        raise ValueError("BAD_POSITION")
    return "01" if position<9 else "012"

def decode(raw):
    if not isinstance(raw,str) or re.fullmatch(r"[01]{9}[012]{3}",raw) is None:
        raise ValueError("COMPACT_SYNTAX")
    nodes=list("ABC")
    edges=[[a,b] for k,(a,b) in enumerate(itertools.product(nodes,repeat=2)) if raw[k]=="1"]
    return {"nodes":nodes,"edges":edges,"triple":[nodes[int(x)] for x in raw[9:]]}

def summarize(rows,sensor):
    expected={(a,SEED+i) for a in ("F","G") for i in range(N)}
    if len(rows)!=2*N or {(r["arm"],r["seed"]) for r in rows}!=expected:
        raise ValueError("INCOMPLETE_OR_DUPLICATE_ATTEMPTS")
    result={}
    for arm in ("F","G"):
        samples=[r for r in rows if r["arm"]==arm]
        seen,graphs=set(),set()
        motifs=Counter({m:0 for m in MOTIFS})
        rejected=Counter()
        accepted=[]
        valid=0
        for r in samples:
            if r["raw_sha256"]!=digest(r["raw"]) or r["prompt_sha256"]!=digest(PROMPT):
                raise ValueError("DIGEST_MISMATCH")
            if len(r["token_ids"])!=r["output_tokens"] or not 0<=r["output_tokens"]<=(32 if arm=="F" else 12):
                raise ValueError("TOKEN_LIMIT")
            if arm=="G":
                if r["output_tokens"]!=12 or len(r["allowed_mass"])!=12:
                    raise ValueError("CONSTRAINT_TRACE")
                if any(not 0<m<=1.000001 for m in r["allowed_mass"]):
                    raise ValueError("INVALID_MASS")
            try:
                packet=decode(r["raw"])
            except ValueError:
                if arm=="G":
                    raise ValueError("GRAMMAR_ROUNDTRIP_FAILURE")
                rejected["COMPACT_SYNTAX"]+=1
                continue
            valid+=1
            graph,key=identities(packet)
            if key in seen:
                rejected["DUPLICATE_ISOMORPHIC_TASK"]+=1
                continue
            row=admit(packet,sensor)  # independent label; never used in generation
            seen.add(key)
            graphs.add(graph)
            motifs[motif(packet)]+=1
            accepted.append({"seed":r["seed"],"raw":r["raw"],"packet":packet,
                             "label":json.loads(row["target"]),"input_sha256":row["input_sha256"]})
        signal=len(seen)>=8 and sum(v>0 for v in motifs.values())>=4 and motifs["110"]>=2
        result[arm]={"valid":valid,"unique_tasks":len(seen),"unique_graphs":len(graphs),
                     "motifs":dict(motifs),"rejections":dict(rejected),"accepted":accepted,
                     "positive":motifs["110"],"negative":len(seen)-motifs["110"],
                     "input_tokens":sum(r["input_tokens"] for r in samples),
                     "output_tokens":sum(r["output_tokens"] for r in samples),
                     "seconds":sum(r["seconds"] for r in samples),
                     "exploratory_feasibility":signal}
    return {"arms":result,"G_minus_F_unique":result["G"]["unique_tasks"]-result["F"]["unique_tasks"],
            "training_authorized":False,"weight_updates":0,"holdout_accessed":False}

def digits_for(tok):
    result={}
    for d in "012":
        ids=tok.encode(d,add_special_tokens=False)
        if len(ids)!=1 or tok.decode(ids,skip_special_tokens=False,clean_up_tokenization_spaces=False)!=d:
            raise ValueError("DIGIT_TOKENIZER_ROUNDTRIP")
        result[d]=ids[0]
    if len(set(result.values()))!=3:
        raise ValueError("AMBIGUOUS_DIGIT_IDS")
    # Verify all two-digit continuations; final full string checked as well.
    for a,b in itertools.product(result,repeat=2):
        if tok.decode([result[a],result[b]],skip_special_tokens=False,clean_up_tokenization_spaces=False)!=a+b:
            raise ValueError("DIGIT_PAIR_ROUNDTRIP")
    return result

def constrained(model,inputs,tok,digits,torch):
    sequence=inputs["input_ids"]
    generated=[]
    masses=[]
    choices=[]
    for pos in range(12):
        alphabet=allowed(pos)
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
        rendered=tok.apply_chat_template([{"role":"user","content":PROMPT}],tokenize=False,add_generation_prompt=True)
        inputs=tok(rendered,return_tensors="pt",add_special_tokens=False)
        for i in range(N):
            for arm in ("F","G"):
                seed=SEED+i
                torch.manual_seed(seed)
                start=time.monotonic()
                with torch.inference_mode():
                    if arm=="F":
                        out=model.generate(**inputs,max_new_tokens=32,do_sample=True,
                            temperature=TEMP,top_k=0,top_p=1.0,pad_token_id=tok.eos_token_id)
                        ids=out[0,inputs["input_ids"].shape[1]:].tolist()
                        raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
                        mass=[]
                    else:
                        ids,raw,mass=constrained(model,inputs,tok,digits,torch)
                row={"arm":arm,"seed":seed,"raw":raw,"raw_sha256":digest(raw),
                     "prompt_sha256":digest(PROMPT),"rendered_prompt_sha256":digest(rendered),
                     "token_ids":ids,"output_tokens":len(ids),"allowed_mass":mass,
                     "input_tokens":int(inputs["input_ids"].shape[1]),"seconds":time.monotonic()-start}
                rows.append(row)
                log.write(json.dumps(row,ensure_ascii=False)+"\n")
                log.flush()
                print("PROPOSAL02",arm,i+1,"of",N,"tokens",len(ids),flush=True)
    result=summarize(rows,sensor)
    result.update(model=MODEL,revision=REV,digit_token_ids=digits,temperature=TEMP,
                  torch=torch.__version__,transformers=transformers.__version__,
                  raw_file_sha256=sha256(path.read_bytes()).hexdigest())
    (output/"report.json").write_text(json.dumps(result,indent=2)+"\n")
    for arm,a in result["arms"].items():
        print("RESULT",arm,"valid",a["valid"],"unique",a["unique_tasks"],
              "motifs",a["motifs"],"signal",a["exploratory_feasibility"],flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
