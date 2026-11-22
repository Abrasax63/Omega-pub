"""One-shot real CPU pilot: self-directed math library -> abstraction -> blind finite tests.

No synthetic concept seed, no gold in prompts, no model weight updates.
The exact model file hash and the PDF SHA are recorded by the calling workflow.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import time
from urllib.request import Request, urlopen

from incremental_math_library import run as build_library, read_ledger, canonical
from concept_abstraction_lab import from_library, check_axioms, AXIOMS

MODEL = "Qwen2.5-3B-Instruct-Q4_K_M"
TARGET_PAGES = 3
HOLDOUT_TASKS = 4
SEED_TAG = "OMEGA-ABSTRACTION-REAL-01-2026-11-22"
AXIOM_DEFINITIONS = (
    "reflexive: all (x,x) present; irreflexive: no (x,x) present; "
    "symmetric: xRy implies yRx; antisymmetric: xRy and yRx imply x=y; "
    "transitive: xRy and yRz imply xRz; total: for any different "
    "x,y at least one xRy or yRx; serial: every x has an outgoing "
    "edge; functional: each x has at most one outgoing edge."
)
TASK_PROMPT = (
    "For the binary relation described below, return ONE JSON object "
    "with a single key 'axioms', a list of ALL properties which hold, "
    "drawn only from the labels listed. Do not guess; use exactly the "
    "stated definitions. You may use {\\\"abstain\\\":true} if unsure. "
    + AXIOM_DEFINITIONS
)


def extract_document_pages(pdf, output, count=TARGET_PAGES):
    import subprocess
    from subprocess import check_output
    pdf = Path(pdf)
    data = pdf.read_bytes()
    if data[:4] != b"%PDF":
        raise ValueError("NOT_A_PDF")
    pdf_sha = sha256(data).hexdigest()
    raw_info = check_output(["pdfinfo", str(pdf)], text=True)
    pages = None
    for line in raw_info.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":",1)[1].strip())
    if pages is None or pages < 100:
        raise ValueError("SOURCE_PDF_PAGE_COUNT_TOO_SMALL")
    max_page = min(pages-10, 240)
    if max_page < 32:
        raise ValueError("INSUFFICIENT_SOURCE_PAGES")
    rng = random.Random(int(sha256((pdf_sha+SEED_TAG).encode()).hexdigest(),16))
    page_numbers = sorted(rng.sample(range(30,max_page+1),count))
    source = []
    for number in page_numbers:
        extracted = check_output([
            "pdftotext","-f",str(number),"-l",str(number),
            "-layout",str(pdf),"-"], text=True)
        if not 200 <= len(extracted) <= 8000:
            # No silent cherry-picking or page replacement after inspecting.
            raise ValueError("SOURCE_PAGE_INVALID_"+str(number))
        source.append({
            "page": number, "text": extracted,
            "text_sha256": sha256(extracted.encode()).hexdigest(),
            "character_count": len(extracted),
        })
    meta = {"source_pdf_sha256":pdf_sha,"pdf_page_count":pages,
            "page_selection_method":"SHA256(pdf+frozen_seed), sample 3 pages in [30,min(n-10,240)]",
            "pages":[{k:v for k,v in x.items() if k!="text"} for x in source]}
    Path(output).write_text(json.dumps(meta,indent=2)+"\n")
    return source,meta


class RealClient:
    def __init__(self, endpoint):
        self.endpoint=endpoint.rstrip("/")+"/v1/chat/completions"
        self.calls=[]
    def __call__(self, messages, max_tokens):
        req_data={
            "model":MODEL,"messages":messages, "temperature":0,
            "seed":9123, "max_tokens":max_tokens,"stream":False,
        }
        start=time.monotonic()
        request=Request(self.endpoint,
            headers={"Content-Type":"application/json"},
            data=json.dumps(req_data).encode(),method="POST")
        with urlopen(request, timeout=210) as resp:
            data=json.load(resp)
        raw=data["choices"][0]["message"]["content"]
        if not isinstance(raw,str):
            raise ValueError("MODEL_RETURNED_NONTEXT")
        metric={
            "output_sha256":sha256(raw.encode()).hexdigest(),
            "max_output_tokens":max_tokens,
            "input_message_chars":sum(len(m["content"]) for m in messages),
            "time_s":round(time.monotonic()-start,3),
            "usage":data.get("usage",{}),
            "finish_reason":data["choices"][0].get("finish_reason"),
        }
        self.calls.append(metric)
        return {"text":raw,**metric}


def finite_holdout(seed_text):
    seed=sha256((seed_text+":blind-finite-holdout-v1").encode()).hexdigest()
    rng=random.Random(int(seed,16))
    nodes=("a","b","c")
    pairs=[(a,b) for a in nodes for b in nodes]
    sample=rng.sample(range(1<<len(pairs)),HOLDOUT_TASKS)
    tasks=[]
    for i,mask in enumerate(sample):
        edges=[list(p) for j,p in enumerate(pairs) if mask & (1<<j)]
        tasks.append({"id":"finite-"+str(i),"universe":list(nodes),
                      "edges":edges})
    return tasks


def predict_axioms(raw):
    try:
        obj=json.loads(raw.strip())
        if not isinstance(obj,dict) or obj.get("abstain") is True:
            return None
        found=obj.get("axioms")
        if (not isinstance(found,list) or
                not all(isinstance(x,str) and x in AXIOMS for x in found)
                or len(set(found))!=len(found)):
            return None
        return sorted(found)
    except (ValueError,TypeError):
        return None


def eval_blind(client, concept_report, pdf_sha):
    if concept_report.get("status")!="STRUCTURAL_CHECKS_PASSED_SEMANTICS_UNVERIFIED":
        return {"status":"NO_VERIFIED_MODEL_FORMATTED_ABSTRACTION_FOR_COMPARISON",
                "model_calls":0}
    shared=concept_report["analysis"]["common_axioms_on_inputs"]
    guessed=concept_report["analysis"]["model_proposed_axioms"]
    summary=("A tentative abstraction, inferred from model-drawn examples, "
             "shares these properties: "+(", ".join(shared) or "(none)")+
             ". The model also hypothesized: "+(", ".join(guessed) or "(none)")+
             ". This is NOT verified as a faithful description of any source. "
             "Always check the relation in the task itself.")
    tasks=finite_holdout(pdf_sha)
    output=[]
    for task in tasks:
        edges={tuple(edge) for edge in task["edges"]}
        # The exact oracle is run only after the two models have answered.
        prompt=(TASK_PROMPT+"\nNodes: "+canonical(task["universe"])+
                "\nEdges: "+canonical(task["edges"]))
        direct=client([{"role":"system","content":"You are a finite-math reader."},
                       {"role":"user","content":prompt}],260)
        augmented=client([
            {"role":"system","content":"You are a finite-math reader."},
            {"role":"user","content":"[UNTRUSTED EDUCATIONAL CONTEXT]\n"+summary+
             "\n[END CONTEXT]\n"+prompt}],260)
        gold=sorted([k for k,v in check_axioms(task["universe"],edges).items()
                     if v["holds"]])
        p_a,p_b=predict_axioms(direct["text"]),predict_axioms(augmented["text"])
        output.append({
            "id":task["id"],"universe":task["universe"],"edges":task["edges"],
            "oracle_axioms":gold,
            "A_direct":{"raw":direct["text"],"parsed":p_a,
                        "correct":p_a==gold if p_a is not None else None,
                        "usage":direct["usage"],"seconds":direct["time_s"]},
            "B_abstract_context":{"raw":augmented["text"],"parsed":p_b,
                        "correct":p_b==gold if p_b is not None else None,
                        "usage":augmented["usage"],"seconds":augmented["time_s"]},
            "C_B_plus_independent_exact_guard":{
                "accepted":p_b==gold if p_b is not None else False,
                "correct_if_accepted":True if p_b==gold else None,
                "note":"The guard uses gold; certification by construction, NOT model learning."},
        })
    def summarize(key):
        vals=[row[key]["correct"] for row in output]
        return {
            "correct":sum(v is True for v in vals),
            "incorrect":sum(v is False for v in vals),
            "abstentions_or_invalid":sum(v is None for v in vals),
            "n":len(vals),
            "prompt_tokens":sum(row[key]["usage"].get("prompt_tokens",0)
                                for row in output),
            "completion_tokens":sum(row[key]["usage"].get("completion_tokens",0)
                                    for row in output)
        }
    return {
        "status":"REAL_BLIND_FINITE_TASKS_EVALUATED",
        "same_model_same_max_output_tokens":True,
        "prompt_tokens_equal":False,
        "A":summarize("A_direct"),"B":summarize("B_abstract_context"),
        "C":{"accepted":sum(r["C_B_plus_independent_exact_guard"]["accepted"]
                          for r in output),
             "note":"Gold-based exact guard with guaranteed no false accept; not fair model-vs-model score"},
        "tasks":output,
        "caution":"Finite edge-list classification does not validate source semantic fidelity or generalization across mathematics.",
    }


def run_experiment(pdf,output,endpoint):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    sources,source_meta=extract_document_pages(pdf,output/"sources.json")
    ledger=output/"math_library_candidates.jsonl"
    client=RealClient(endpoint)
    report={
        "protocol":SEED_TAG, "source":source_meta,
        "research":[ ],"abstraction":None,"blind_finite":None,
        "no_premade_concept_pairs":True,"source_pages_without_answer_keys":True,
        "scientific_semantic_fidelity":"NOT_VERIFIED",
        "theorems_certified":0,"model_weights_updated":False,
    }
    def store():
        report["model_calls"]=len(client.calls)
        report["model_call_metrics"]=client.calls
        report["ledger_records"]=len(read_ledger(ledger))
        (output/"report.json").write_text(json.dumps(report,indent=2,
                                      ensure_ascii=False)+"\n")
    try:
        for source in sources:
            try:
                reading=build_library(
                    source["text"],ledger,endpoint=endpoint,max_hops=1,
                    model_call=client)
                report["research"].append({
                    "page":source["page"],"text_sha256":source["text_sha256"],
                    "result":reading})
            except Exception as exc:
                report["research"].append({
                    "page":source["page"],"error_type":type(exc).__name__})
                store()
                raise
            store()
        report["abstraction"]=from_library(ledger,endpoint=endpoint,
                                          model_call=client)
        store()
        report["blind_finite"]=eval_blind(
            client,report["abstraction"],source_meta["source_pdf_sha256"])
        store()
    finally:
        store()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-pdf",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    result=run_experiment(args.source_pdf,args.output,args.server)
    print(json.dumps({
        "protocol":result["protocol"],
        "model_calls":result["model_calls"],
        "library_records":result["ledger_records"],
        "abstraction_status":result["abstraction"]["status"],
        "blind_status":result["blind_finite"]["status"],
        "theorems_certified":0},ensure_ascii=False))


if __name__=="__main__":
    main()
