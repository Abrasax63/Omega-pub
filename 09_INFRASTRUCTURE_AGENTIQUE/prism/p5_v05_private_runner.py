"""P5V05: private-candidate A/B/C live runner.

This file is PUBLIC code, not a public dataset. No answer keys, prompt data,
credentials, provider result, or hidden random seed may be checked into GitHub.

Default invocation only validates SHA-256 and builds plans in memory (0 calls).
Actual generation REQUIRES --execute --allow-billable-api, an injected
OpenAI Responses SDK client, exact model, explicit token and call caps,
an off-Git output directory, and the private file bound to the PUBLIC hash.

This is NOT independent grading, a blind external holdout, or a claim of an
Omega gain. The old DispatchLedger provides durable per-attempt commitments.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import secrets
from time import perf_counter

from planner import ROLE_ORDER, ROLE_QUESTIONS, plan_mission
from p5_dispatch import DispatchLedger

ARMS=("A","B","C")
MISSION_TYPES=("mathematical","documentary","computational","exploratory","general")
REPS=2
REQUIRED_COUNT=16
EXPECTED_COUNTS={"FORMAL":4,"CRT":4,"DOC":4,"DATA":4}
EXP="P5V05_PRIVATE_CANDIDATE"
SYSTEM_INSTRUCTIONS=(
    "Réponds en français. Sois exact et vérifiable. "
    "N'invente ni document ni vérification effectuée. "
    "Distingue les faits des hypothèses et justifie les conclusions. "
    "Si l'information nécessaire manque, indique-le sans inventer."
)
DELIVERABLES=[
    "Répondre à la question, si cela est justifié.",
    "Indiquer l'argument décisif ou les étapes de calcul.",
    "Signaler les contradictions, incertitudes et données manquantes.",
]

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False).encode("utf-8")

def hash_data(x):
    return sha256(canonical(x)).hexdigest()

def _secure_outside_git(path):
    path=Path(path).expanduser().resolve()
    for p in (path,*path.parents):
        if (p/".git").exists():
            raise ValueError("private input/output must not live within a Git checkout")
    return path

def _check_text(x,name):
    if not isinstance(x,str) or not x.strip():
        raise ValueError(f"missing or invalid {name}")
    if len(x)>12000:
        raise ValueError(f"overlong {name}")
    return x

def validate_inputs(path,manifest_path):
    src=_secure_outside_git(path)
    manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("protocol")!="P5V05_CANDIDATE" or manifest.get("case_count")!=REQUIRED_COUNT:
        raise ValueError("wrong public manifest")
    if manifest.get("expected_arms")!=list(ARMS) or manifest.get("expected_repetitions")!=REPS:
        raise ValueError("changed arm/repetition protocol")
    if manifest.get("expected_generations")!=REQUIRED_COUNT*len(ARMS)*REPS:
        raise ValueError("changed call count")
    if manifest.get("status")!="PRIVATE_CANDIDATE_NOT_BLIND_NOT_INDEPENDENTLY_VETTED":
        raise ValueError("candidate status misrepresented")
    bytestream=src.read_bytes()
    if sha256(bytestream).hexdigest()!=manifest.get("prompt_only_sha256"):
        raise ValueError("private inputs differ from public precommitment")
    data=json.loads(bytestream)
    if set(data)!={"protocol","status","created","cases"} or (
        data["protocol"]!="P5V05_CANDIDATE_PRIVATE" or
        data["status"]!="candidate_not_independently_vetted"):
        raise ValueError("invalid private input container")
    cases=data["cases"]
    if len(cases)!=REQUIRED_COUNT or len({x["case_id"] for x in cases})!=len(cases):
        raise ValueError("wrong private case population")
    totals=Counter()
    for case in cases:
        if set(case)!={"case_id","mission_type","question","documents"}:
            raise ValueError("possible private key/answer contamination")
        cid=_check_text(case["case_id"],"case_id")
        prefix=cid.split("-")
        if len(prefix)!=3 or prefix[0]!="P5V05" or prefix[1] not in EXPECTED_COUNTS:
            raise ValueError("invalid candidate case ID")
        totals[prefix[1]]+=1
        if case["mission_type"] not in MISSION_TYPES:
            raise ValueError("invalid mission type")
        _check_text(case["question"],"question")
        if not isinstance(case["documents"],list) or len(case["documents"])>12:
            raise ValueError("invalid document list")
        ids=set()
        for doc in case["documents"]:
            if set(doc)!={"id","kind","text"}:
                raise ValueError("document contains hidden metadata")
            did=_check_text(doc["id"],"document id")
            if did in ids:raise ValueError("duplicate document id")
            ids.add(did)
            for field in ("kind","text"):
                _check_text(doc[field],field)
    if dict(totals)!=EXPECTED_COUNTS:
        raise ValueError("frozen candidate strata drift")
    return cases,manifest

def build_triplet(case):
    shared={
        "question":case["question"],
        "mission_type":case["mission_type"],
        "documents":[dict(x) for x in sorted(case["documents"],key=lambda d:d["id"])],
        "livrables":list(DELIVERABLES),
    }
    plan=plan_mission({"question":shared["question"],
                       "mission_type":shared["mission_type"]})
    roles=[t["role"] for t in plan["tasks"]]
    if not roles or any(r not in ROLE_ORDER for r in roles):
        raise AssertionError("invalid real Omega planner role")
    fixed=" ; ".join(f"{r}: {ROLE_QUESTIONS[r]}" for r in ROLE_ORDER)
    adapted=" ; ".join(f"{r}: {ROLE_QUESTIONS[r]}" for r in roles)
    strategies={
        "A":"Réponse directe, sans liste de perspectives.",
        "B":"Appliquer les cinq perspectives fixes : "+fixed,
        "C":"Appliquer les perspectives choisies par le planificateur : "+adapted,
    }
    requests={
        arm:{"instructions":SYSTEM_INSTRUCTIONS,
             "input":{"shared":shared,"strategy":strategies[arm]}}
        for arm in ARMS
    }
    if any(canonical(requests[x]["input"]["shared"])!=canonical(shared) for x in ARMS):
        raise AssertionError("different information across experimental arms")
    return requests

def private_schedule(cases,seed):
    if type(seed) is not int or seed<0:
        raise ValueError("private integer scheduling seed required")
    rng=random.Random(seed)
    schedule=[]
    for case in cases:
        for rep in range(1,REPS+1):
            a=list(ARMS)
            rng.shuffle(a)
            for arm in a:
                schedule.append({"case_id":case["case_id"],
                                 "repetition":rep,"arm":arm})
    # Shuffle case/repetition block order while preserving a randomized
    # arm order WITHIN each 3-call block.
    blocks=[schedule[i:i+3] for i in range(0,len(schedule),3)]
    rng.shuffle(blocks)
    schedule=[record for block in blocks for record in block]
    if len(schedule)!=REQUIRED_COUNT*REPS*len(ARMS):
        raise AssertionError("lost schedule entries")
    if len(set((x["case_id"],x["repetition"],x["arm"]) for x in schedule))!=len(schedule):
        raise AssertionError("duplicated arm or repetition")
    return schedule

def preflight(cases,manifest):
    packets={x["case_id"]:build_triplet(x) for x in cases}
    n=sum(len(x) for x in packets.values())*REPS
    if n!=manifest["expected_generations"]:
        raise AssertionError("missing public-commitment calls")
    return {
        "status":"PREFLIGHT_ONLY",
        "frozen_input_sha256":manifest["prompt_only_sha256"],
        "case_count":len(cases),
        "required_generations":n,
        "arms":list(ARMS),
        "repetitions":REPS,
        "provider_token_counts":None,
        "provider_generations":0,
        "grader_count":0,
        "independently_vetted":False,
        "frozen_request_hashes":{
            cid:{arm:hash_data(req) for arm,req in by_arm.items()}
            for cid,by_arm in packets.items()},
    }

def _response_value(response,key):
    if isinstance(response,dict):return response.get(key)
    return getattr(response,key,None)

def _count_input(client,model,req,timeout):
    options=client.with_options(max_retries=0,timeout=timeout)
    payload=json.dumps(req["input"],sort_keys=True,ensure_ascii=False,
                       separators=(",",":"))
    c=options.responses.input_tokens.count(
        model=model,instructions=req["instructions"],input=payload,tools=[])
    count=_response_value(c,"input_tokens")
    if type(count) is not int or count<0:
        raise RuntimeError("actual provider input token count absent")
    return count,payload

def _generate(client,model,req,payload,output_cap,timeout):
    options=client.with_options(max_retries=0,timeout=timeout)
    start=perf_counter()
    response=options.responses.create(
        model=model,instructions=req["instructions"],
        input=payload,tools=[],max_output_tokens=output_cap,
        truncation="disabled",store=False)
    elapsed=perf_counter()-start
    status=_response_value(response,"status")
    usage=_response_value(response,"usage")
    actual_model=_response_value(response,"model")
    txt=_response_value(response,"output_text")
    in_tokens=_response_value(usage,"input_tokens")
    out_tokens=_response_value(usage,"output_tokens")
    if status!="completed" or type(in_tokens) is not int or (
            type(out_tokens) is not int or not isinstance(txt,str) or
            not txt.strip()):
        raise RuntimeError("provider incomplete response or missing real usage")
    if actual_model!=model:
        raise RuntimeError("provider returned a model different from frozen snapshot")
    return {"response_id":_response_value(response,"id"),
            "model":actual_model,"status":status,"text":txt,
            "input_tokens":in_tokens,"output_tokens":out_tokens,
            "latency_seconds":round(elapsed,6)}

def execute(cases,manifest,*,client,model,total_token_cap,
            output_token_cap,max_generation_calls,allow_billable_api,
            output_dir,seed=None,timeout_seconds=90):
    if not allow_billable_api:
        raise ValueError("paid API generation requires explicit opt-in")
    if not isinstance(model,str) or not model.strip():
        raise ValueError("exact API model required")
    if type(max_generation_calls) is not int or (
            max_generation_calls!=manifest["expected_generations"]):
        raise ValueError("exact approved maximum generation count required")
    if (type(total_token_cap) is not int or type(output_token_cap) is not int
            or not 0<output_token_cap<total_token_cap):
        raise ValueError("exact identical token budgets required")
    if not hasattr(client,"with_options"):
        raise ValueError("explicit authenticated Responses client required")
    if not isinstance(timeout_seconds,(float,int)) or timeout_seconds<=0:
        raise ValueError("invalid timeout")
    target=_secure_outside_git(output_dir)
    if target.exists():
        raise FileExistsError("a run directory cannot be reused or overwritten")
    packets={x["case_id"]:build_triplet(x) for x in cases}
    seed=secrets.randbits(128) if seed is None else seed
    schedule=private_schedule(cases,seed)
    requests=[]
    # PRECOUNT every prompt BEFORE the first billable model generation. If
    # even one case cannot fit in the per-call cap, abort with no generations.
    for item in schedule:
        req=packets[item["case_id"]][item["arm"]]
        count,payload=_count_input(client,model,req,timeout_seconds)
        if count+output_token_cap>total_token_cap:
            raise RuntimeError("one model prompt exceeds shared per-call token cap")
        requests.append((item,req,count,payload))
    target.mkdir(mode=0o700,parents=True)
    os.chmod(target,0o700)
    private_start={"status":"STARTED_NOT_COMPLETE",
                   "frozen_input_sha256":manifest["prompt_only_sha256"],
                   "model":model,"total_token_cap":total_token_cap,
                   "output_token_cap":output_token_cap,
                   "planned_generations":len(requests),
                   "seed_private":seed,"schedule":schedule,
                   "counted_inputs":[{"case_id":i["case_id"],"arm":i["arm"],
                                      "rep":i["repetition"],"count":cnt,
                                      "prompt_sha256":hash_data(req)}
                                     for i,req,cnt,_ in requests],
                   "gold_file_not_loaded":True,
                   "actual_usd_spend":None}
    def save(name,record):
        p=target/name
        with os.fdopen(os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),
                       "w",encoding="utf-8") as f:
            json.dump(record,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write("\n")
        return p
    save("run_private_start.json",private_start)
    ledger=DispatchLedger(target/"dispatch_events.jsonl",EXP)
    completed=[]
    for j,(item,req,cnt,payload) in enumerate(requests):
        call_id=sha256(canonical({"nonce":seed,"position":j,
                                  "case_id":item["case_id"],
                                  "arm":item["arm"],"rep":item["repetition"]})
                       ).hexdigest()[:24]
        identity=(EXP,item["case_id"],item["arm"],
                  item["repetition"],"generate",1,call_id)
        ledger.reserve(identity)
        response=_generate(client,model,req,payload,
                           output_token_cap,timeout_seconds)
        if (response["input_tokens"]+response["output_tokens"]>
                total_token_cap or response["output_tokens"]>output_token_cap):
            raise RuntimeError("provider actual usage exceeds approved token cap")
        row={"call_id":call_id,
             "case_id":item["case_id"],"arm":item["arm"],
             "repetition":item["repetition"],"index":j,
             "prompt_sha256":hash_data(req),
             "preflight_input_tokens":cnt,
             "actual_input_tokens":response["input_tokens"],
             "actual_output_tokens":response["output_tokens"],
             "elapsed_seconds":response["latency_seconds"],
             "model":response["model"],
             "provider_response_id":response["response_id"],
             "output_text_sha256":sha256(response["text"].encode()).hexdigest()}
        # Preserve the exact provider answer outside Git; existing ledger
        # hashes the telemetry and stores the raw output durably, without a
        # silent automatic retry after an uncertain outcome.
        ledger.finish_payload(identity,row,response)
        completed.append(row)
    ledger.verify_results(completed)
    summary={"status":"RUN_UNGRADED","provider_generations":len(completed),
             "frozen_input_sha256":manifest["prompt_only_sha256"],
             "model":model,"measured_input_tokens":sum(
                 x["actual_input_tokens"] for x in completed),
             "measured_output_tokens":sum(
                 x["actual_output_tokens"] for x in completed),
             "measured_latency_seconds":round(sum(
                 x["elapsed_seconds"] for x in completed),6),
             "actual_usd_spend":None,
             "case_count":len(cases),"repetitions":REPS,
             "independent_grader_count":0,"answer_key_used":False,
             "primary_quality_comparison_complete":False}
    save("private_ungaded_summary.json",summary)
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--allow-billable-api",action="store_true")
    ap.add_argument("--output-dir")
    ap.add_argument("--model")
    ap.add_argument("--total-token-cap",type=int)
    ap.add_argument("--output-token-cap",type=int)
    ap.add_argument("--max-generation-calls",type=int)
    a=ap.parse_args()
    cases,manifest=validate_inputs(a.inputs,a.manifest)
    if not a.execute:
        print("OMEGA_P5V05_PRIVATE_PREFLIGHT "+json.dumps({
            k:v for k,v in preflight(cases,manifest).items()
            if k!="frozen_request_hashes"},sort_keys=True))
        return
    if not a.output_dir or not a.allow_billable_api:
        ap.error("real model calls require output dir and explicit billable API opt-in")
    from openai import OpenAI
    client=OpenAI()
    result=execute(
        cases,manifest,client=client,model=a.model,
        total_token_cap=a.total_token_cap,
        output_token_cap=a.output_token_cap,
        max_generation_calls=a.max_generation_calls,
        allow_billable_api=a.allow_billable_api,
        output_dir=a.output_dir,
    )
    print("OMEGA_P5V05_RUN_UNGRADED "+json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
