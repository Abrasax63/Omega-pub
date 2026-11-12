"""P5-VALUE-01: preregistered PUBLIC small-model vs exact verification ablation.

No paid API, private holdout, imported answer key, or autonomous agents.
Source data and grader are public calibration fixtures. Two independent
implementations compute reference and verifier answers for numeric tasks.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import re
from time import perf_counter

from p5_v05_private_runner import build_triplet
from planner import plan_mission

MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
MODEL_REVISION="7ae557604adf67be50417f59c2c2f167def9a775"
SEED=20261112
MAX_NEW_TOKENS=96
ARMS=("A","B","C")
PROTOCOL="P5-VALUE-01-PUBLIC-CALIBRATION"

CRT_PARAMETERS=(
    (7,3,9,5),(5,4,8,3),(6,1,11,8),
    (4,3,7,2),(9,4,10,7),(8,5,11,6),
)
# Each: A successes/total (stratum 1, stratum 2),
#       B successes/total (stratum 1, stratum 2).
DATA_PARAMETERS=(
    (4,9,8,50,12,30,5,10),
    (13,20,2,8,6,12,3,9),
    (2,15,19,20,7,14,4,10),
    (5,11,6,22,16,25,1,8),
    (8,12,3,18,4,10,13,30),
    (1,8,17,20,2,8,12,16),
)
DOC_CLAIMS=(
    ("NX-17", "2023", "protocole N-4"),
    ("ZE-04", "2024", "débit garanti de 90 unités"),
    ("AC-23", "2025", "chiffrement certifié"),
    ("PX-08", "2021", "compatibilité version 12"),
    ("MR-51", "2022", "conformité à une norme"),
    ("BY-09", "2020", "absence totale d'incidents"),
)
SHARED_OUTPUT_POLICY=(
    "Première ligne obligatoire : Réponse: VALEUR. "
    "VALEUR doit être l'entier demandé, A ou B, ou INDETERMINE. "
    "Puis une justification brève. "
    "Ne suppose pas que des documents fictifs sont vérifiés."
)
ANSWER_PATTERN=re.compile(
    r"""(?im)^\s*(?:réponse(?:\s+finale)?|résultat(?:\s+final)?|conclusion(?:\s+finale)?)\s*[:=]\s*["'«]?\s*(INDETERMINE|A|B|[0-9]+)\b"""
)
ALT_PATTERN=re.compile(
    r"""(?im)^\s*la\s+réponse(?:\s+finale)?\s+est\s+["'«]?\s*(INDETERMINE|A|B|[0-9]+)\b"""
)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False).encode("utf-8")

def reference(case):
    """Independent exact reference (brute CRT, Fraction rate)."""
    if case["kind"]=="crt":
        m,r,n,s=case["parameters"]
        return str(next(x for x in range(m*n) if x%m==r and x%n==s))
    if case["kind"]=="data":
        a1,at1,a2,at2,b1,bt1,b2,bt2=case["parameters"]
        x=Fraction(a1+a2,at1+at2)
        y=Fraction(b1+b2,bt1+bt2)
        if x==y:raise AssertionError("tie fixture forbidden")
        return "A" if x>y else "B"
    if case["kind"]=="doc":
        return "INDETERMINE"
    raise AssertionError("unknown reference domain")

def exact_verifier(case):
    """Separate method (inverse CRT, integer cross-products), no reference()."""
    if case["kind"]=="crt":
        m,r,n,s=case["parameters"]
        return str((r+m*(((s-r)*pow(m,-1,n))%n))%(m*n))
    if case["kind"]=="data":
        a1,at1,a2,at2,b1,bt1,b2,bt2=case["parameters"]
        a=(a1+a2)*(bt1+bt2)
        b=(b1+b2)*(at1+at2)
        if a==b:raise AssertionError("tie not permitted")
        return "A" if a>b else "B"
    if case["kind"]=="doc":
        return None
    raise AssertionError("unknown verifier domain")

def cases():
    rows=[]
    for i,p in enumerate(CRT_PARAMETERS,1):
        m,r,n,s=p
        rows.append({
            "case_id":f"VALUE-CRT-{i:02d}","kind":"crt",
            "mission_type":"computational","parameters":p,"documents":[],
            "question":(
                f"Trouve le plus petit entier x >= 0 tel que "
                f"x modulo {m} = {r} et x modulo {n} = {s}. "
                "Réponds par cet entier.")
        })
    for i,p in enumerate(DATA_PARAMETERS,1):
        a1,at1,a2,at2,b1,bt1,b2,bt2=p
        rows.append({
            "case_id":f"VALUE-DATA-{i:02d}","kind":"data",
            "mission_type":"computational","parameters":p,"documents":[],
            "question":(
                f"Groupe A : {a1} succès sur {at1} en strate 1, "
                f"{a2} sur {at2} en strate 2. "
                f"Groupe B : {b1} succès sur {bt1} en strate 1, "
                f"{b2} sur {bt2} en strate 2. "
                "Quel groupe a le taux global de succès le plus élevé ? "
                "Réponds A ou B.")
        })
    for i,(name,year,claim) in enumerate(DOC_CLAIMS,1):
        rows.append({
            "case_id":f"VALUE-DOC-{i:02d}","kind":"doc",
            "mission_type":"documentary","parameters":(name,year,claim),
            "question":(
                f"Une note sans auteur ni signature, datée {year}, "
                f"affirme que le dispositif fictif {name} possède {claim}. "
                "Aucune observation indépendante ni source authentifiée "
                "n'est fournie. Cette affirmation est-elle établie ? "
                "Réponds INDETERMINE si ce n'est pas vérifiable."
            ),
            "documents":[{
                "id":"notice-non-authentifiee", "kind":"simulation",
                "text":f"Note fictive non vérifiée : {name} possède {claim}."
            }],
        })
    assert len(rows)==18
    for row in rows:
        if row["kind"]!="doc":
            assert exact_verifier(row)==reference(row)
        else:
            assert exact_verifier(row) is None and reference(row)=="INDETERMINE"
    return rows

def request_for(case,arm):
    if arm not in ARMS:raise ValueError("unsupported treatment arm")
    # NEVER pass the domain, verifier params or reference to the model.
    allowed={
        "case_id":"P5V05-"+case["case_id"],
        "mission_type":case["mission_type"],
        "question":case["question"],
        "documents":case["documents"],
    }
    return build_triplet(allowed)[arm]

def messages(case,arm):
    req=request_for(case,arm)
    payload=json.dumps(req["input"],sort_keys=True,ensure_ascii=False,
                       separators=(",",":"))
    return [
        {"role":"system","content":req["instructions"]},
        {"role":"user","content":payload+"\n"+SHARED_OUTPUT_POLICY},
    ]

def extract_answer(text):
    """Predetermined permissive FORMATTING parser, not semantic evaluator."""
    if not isinstance(text,str) or not text.strip():return None
    hits=(ANSWER_PATTERN.findall(text)+ALT_PATTERN.findall(text))
    choices={x.upper() for x in hits}
    if len(choices)==1:return next(iter(choices))
    if len(choices)>1:return None
    bare=re.fullmatch(r"\s*(INDETERMINE|A|B|[0-9]+)\s*[.]?\s*",
                      text,flags=re.IGNORECASE)
    return bare.group(1).upper() if bare else None

def plan_schedule(rows):
    rng=random.Random(SEED)
    blocks=[[(i,a) for a in rng.sample(list(ARMS),len(ARMS))]
            for i in range(len(rows))]
    rng.shuffle(blocks)
    flat=[item for block in blocks for item in block]
    assert len(flat)==54 and len(set(flat))==54
    return flat

def verification_policies(rows):
    """No model calls: check the incremental value of *routing* vs a trivial rule."""
    by_name={k:{"exact_matches":0,"abstentions":0,
                "verifier_calls":0,"model_calls":0,"predictions":[]}
             for k in ("V-all","Omega-route","Type-route")}
    for case in rows:
        expected=reference(case)
        roles=[t["role"] for t in plan_mission({
            "question":case["question"],
            "mission_type":case["mission_type"]})["tasks"]]
        for policy,out in by_name.items():
            use=(policy=="V-all" or (
                policy=="Omega-route" and "computational" in roles) or (
                policy=="Type-route" and case["mission_type"]=="computational"))
            prediction=exact_verifier(case) if use else None
            if use:out["verifier_calls"]+=1
            prediction=prediction if prediction is not None else "INDETERMINE"
            out["exact_matches"]+=int(prediction==expected)
            out["abstentions"]+=int(prediction=="INDETERMINE")
            out["predictions"].append((case["case_id"],prediction))
    return by_name

def preflight():
    rows=cases()
    request_hashes={}
    for row in rows:
        req=[request_for(row,a) for a in ARMS]
        shared={canonical(r["input"]["shared"]) for r in req}
        assert len(shared)==1
        assert len({canonical(r) for r in req})==3
        request_hashes[row["case_id"]]={
            arm:sha256(canonical(request_for(row,arm))).hexdigest()
            for arm in ARMS
        }
    return {
        "protocol":PROTOCOL,"status":"PREFLIGHT_ONLY",
        "case_count":len(rows),"model_generations":0,
        "planned_model_generations":len(rows)*len(ARMS),
        "private_data_read":False,"paid_api_calls":0,
        "model":MODEL_ID,
        "public_cases_sha256":sha256(canonical(rows)).hexdigest(),
        "request_hashes":request_hashes,
        "verification_policies":verification_policies(rows),
    }

def summarize(actual,rows):
    expected={r["case_id"]:reference(r) for r in rows}
    per_arm={}
    for arm in ARMS:
        subset=[r for r in actual if r["arm"]==arm]
        per_arm[arm]={
            "generations":len(subset),
            "strict_exact_matches":sum(r["parsed"]==expected[r["case_id"]]
                                      for r in subset),
            "unparsed_or_ambiguous":sum(r["parsed"] is None for r in subset),
            "input_tokens":sum(r["input_tokens"] for r in subset),
            "output_tokens":sum(r["output_tokens"] for r in subset),
            "latency_seconds":round(sum(r["latency_seconds"] for r in subset),3),
        }
    checked={}
    for arm in ("A","C"):
        subset=[r for r in actual if r["arm"]==arm]
        checked[arm+"+V"]={
            "model_calls":len(subset),"verifier_calls":sum(
                c["kind"]!="doc" for c in rows),
            "exact_matches":sum(
                (exact_verifier(case) or "INDETERMINE")==expected[case["case_id"]]
                for case in rows),
            "warning":"Mechanical verifier overwrites model predictions; not an Omega-only gain",
        }
    return per_arm,checked

def run(output):
    # Preflight MUST validate the two oracle paths before importing model.
    pre=preflight()
    rows=cases()
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=MODEL_REVISION)
    model=AutoModelForCausalLM.from_pretrained(
        MODEL_ID,revision=MODEL_REVISION,torch_dtype=torch.float32).eval()
    output_rows=[]
    for index,arm in plan_schedule(rows):
        case=rows[index]
        msg=messages(case,arm)
        formatted=tokenizer.apply_chat_template(
            msg,tokenize=False,add_generation_prompt=True)
        tokens=tokenizer([formatted],return_tensors="pt")
        t=perf_counter()
        with torch.inference_mode():
            generated=model.generate(
                **tokens,do_sample=False,max_new_tokens=MAX_NEW_TOKENS,
                pad_token_id=tokenizer.eos_token_id)
        elapsed=perf_counter()-t
        prefix=tokens["input_ids"].shape[1]
        continuation=generated[0][prefix:]
        text=tokenizer.decode(continuation,skip_special_tokens=True)
        parsed=extract_answer(text)
        match=parsed==reference(case)
        output_rows.append({
            "case_id":case["case_id"],"arm":arm,"model_output":text,
            "parsed":parsed,"reference":reference(case),
            "exact_match":match,
            "input_tokens":int(prefix),
            "output_tokens":int(continuation.shape[0]),
            "latency_seconds":round(elapsed,3),
            "request_sha256":sha256(canonical(request_for(case,arm))).hexdigest(),
        })
        print("VALUE_REAL_GENERATION",case["case_id"],arm,
              "parsed="+str(parsed),"exact="+str(match),flush=True)
    if len(output_rows)!=54:
        raise RuntimeError("Incomplete real generation campaign")
    per_arm,checked=summarize(output_rows,rows)
    report={
        "protocol":PROTOCOL,"status":"PUBLIC_EXPLORATORY_NOT_INDEPENDENT",
        "model":MODEL_ID,
        "model_revision":getattr(model.config,"_commit_hash",None),
        "preflight_public_cases_sha256":pre["public_cases_sha256"],
        "only_public_data":True,"openai_api_calls":0,
        "model_generation_count":len(output_rows),
        "max_new_tokens":MAX_NEW_TOKENS,
        "per_arm":per_arm,
        "checker_ablations":checked,
        "routing_baselines":verification_policies(rows),
        "rows":output_rows,
        "limitations":[
            "Public author-designed calibration, not independent holdout",
            "Verifier deliberately knows exact computational task semantics",
            "Simple task-type router is a negative control for Omega",
            "Small open-weight model is not GPT-6",
            "First pilot same-day exploratory only",
            "No verified provider billing or general intelligence gain",
        ],
    }
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2,
                                sort_keys=True)+"\n",encoding="utf-8")
    print("P5_VALUE_RESULT",json.dumps({
        "status":report["status"],"generations":len(output_rows),
        "per_arm":per_arm,"checker_ablations":checked,
        "routing_counts":{k:(v["exact_matches"],v["verifier_calls"])
                          for k,v in report["routing_baselines"].items()},
    },ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--output",default="p5_value_public_results.json")
    args=ap.parse_args()
    if args.preflight:
        p=preflight()
        print(json.dumps({
            "protocol":p["protocol"],"status":p["status"],
            "case_count":p["case_count"],
            "planned_model_generations":p["planned_model_generations"],
            "public_cases_sha256":p["public_cases_sha256"],
            "paid_api_calls":p["paid_api_calls"],
        },sort_keys=True))
    else:run(args.output)

if __name__=="__main__":
    main()
