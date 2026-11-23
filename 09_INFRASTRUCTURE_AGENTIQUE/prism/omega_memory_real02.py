"""OMEGA REAL-02: constrained formal acquisition and memory test, no paid API.
The language-model prose remains unverified and quarantined.
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import random
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

import incremental_math_library as library
from incremental_math_library import canonical, read_ledger
from concept_abstraction_lab import check_axioms
from real_abstraction_trial import RealClient

UPSTREAM_COMMIT = "1a2005c6797bec10289f09e706f81c6c4b809a52"
UPSTREAM_BLOB = "75bebda318694bb4712d60380b0e183e77f1e757"
UPSTREAM_URL = ("https://raw.githubusercontent.com/oscarlevin/discrete-book/"
                +UPSTREAM_COMMIT+"/source/sec_gt-relations.ptx")
SECTION = "subsec_equivalence-relations"
SALT = "OMEGA-LIBRARY-MEMORY-REAL-02-HOLDOUT"
NODES = ("a","b","c")
PAIRS = tuple((a,b) for a in NODES for b in NODES)
TARGETS = {
 "equivalence relation": ("reflexive","symmetric","transitive"),
 "partial order": ("reflexive","antisymmetric","transitive"),
 "preorder": ("reflexive","transitive"),
 **{n:(n,) for n in ("reflexive","irreflexive","symmetric",
                      "antisymmetric","transitive","total","serial","functional")}
}
CARD_SUFFIX = (
 " IMPORTANT: exact_quote MUST be copied literally from the WIKIPEDIA "
 "source declared by the integer source_page_id, never from the original book. "
 "Add 'formal_axioms', a list of required defining property names chosen ONLY "
 "from reflexive, irreflexive, symmetric, antisymmetric, transitive, total, "
 "serial, functional. Do not list merely incidental properties. "
 "Add 'positive_edges' and 'negative_edges' as arrays of distinct [from,to] "
 "pairs over nodes a,b,c, invented by YOU, illustrating a relation satisfying "
 "the definition and one failing it. No examples are preloaded. "
 "If the concept is outside this grammar, leave formal_axioms empty."
)

def source_seed(data):
    git_blob = b"blob "+str(len(data)).encode()+b"\x00"+data
    if sha1(git_blob).hexdigest()!=UPSTREAM_BLOB:
        raise ValueError("UPSTREAM_SOURCE_BLOB_CHANGED")
    root=ET.fromstring(data)
    key="{http://www.w3.org/XML/1998/namespace}id"
    section=next((x for x in root.iter() if x.get(key)==SECTION),None)
    if section is None: raise ValueError("SOURCE_SECTION_MISSING")
    seed="\n".join(" ".join("".join(x.itertext()).split()) for x in list(section)[:7])
    if not 200<=len(seed)<=8000: raise ValueError("SOURCE_LENGTH_OUT_OF_BOUNDS")
    return seed

def concept_name(value):
    if not isinstance(value,str): return None
    s=re.sub(r"\s+"," ",value.casefold().replace("-"," ").strip())
    if s=="equivalence relations" or s=="equivalence": s="equivalence relation"
    if s in ("partial ordering","partial order relation"): s="partial order"
    return s if s in TARGETS else None

def relation(mask):
    return frozenset(p for i,p in enumerate(PAIRS) if (mask>>i)&1)

def is_example(edges, sig, expected):
    if not isinstance(edges,list) or len(edges)>9: return False
    try:
        pairs=[tuple(x) for x in edges]
        if len(set(pairs))!=len(pairs) or any(
           len(x)!=2 or x[0] not in NODES or x[1] not in NODES for x in pairs):
            return False
        facts=check_axioms(NODES,frozenset(pairs))
        return all(facts[a]["holds"] for a in sig) is expected
    except (TypeError,ValueError,KeyError): return False

def inspect_bounded(card,quote_ok,seed):
    name=concept_name(card.get("concept")) if isinstance(card,dict) else None
    sig=TARGETS.get(name,())
    proposed=card.get("formal_axioms") if isinstance(card,dict) else None
    signature=(bool(name) and isinstance(proposed,list)
          and len(proposed)==len(sig) and len(set(proposed))==len(sig)
          and set(proposed)==set(sig))
    pos=bool(signature and is_example(card.get("positive_edges"),sig,True))
    neg=bool(signature and is_example(card.get("negative_edges"),sig,False))
    source=bool(name and name in seed.casefold())
    return {"target":name,"citation":bool(quote_ok),
            "source_mentions_target":source,"formal_signature":signature,
            "positive_example":pos,"negative_example":neg,
            "bounded_pass":all((quote_ok,source,signature,pos,neg)),
            "free_text_semantics":"NOT_VERIFIED"}

def holdout(sig):
    # Generator is frozen before inference. Exact truths are computed locally.
    order=sorted(range(512),key=lambda i:sha256((SALT+":"+str(i)).encode()).hexdigest())
    def truth(mask):
        facts=check_axioms(NODES,relation(mask))
        return all(facts[a]["holds"] for a in sig)
    pos=[m for m in order if truth(m)][:2]
    neg=[m for m in order if not truth(m)][:2]
    if len(pos)!=2 or len(neg)!=2: raise ValueError("NO_BALANCED_HOLDOUT")
    masks=pos+neg
    random.Random(9204).shuffle(masks)
    return [{"id":i,"mask":m,"edges":[list(x) for x in PAIRS if x in relation(m)],
             "truth":truth(m)} for i,m in enumerate(masks)]

def parse_answer(raw,sig):
    try:
        obj=json.loads(raw.strip())
        if not isinstance(obj,dict) or obj.get("abstain") is True:return None
        holds,failed=obj.get("holds"),obj.get("failed_axioms")
        if type(holds) is not bool or not isinstance(failed,list): return None
        if len(failed)!=len(set(failed)) or any(x not in sig for x in failed):
            return None
        return holds if holds==(len(failed)==0) else None
    except (ValueError,TypeError):return None

def save_report(directory,report):
    (directory/"report.json").write_text(json.dumps(report,indent=2,
                          ensure_ascii=False)+"\n")

def acquire_phase(root,source_file,endpoint):
    root.mkdir(parents=True,exist_ok=True)
    raw=Path(source_file).read_bytes()
    seed=source_seed(raw)
    (root/"seed.txt").write_text(seed)
    source={"git_commit":UPSTREAM_COMMIT,"git_blob":UPSTREAM_BLOB,
            "source_url":UPSTREAM_URL,
            "source_sha256":sha256(raw).hexdigest(),
            "seed_sha256":sha256(seed.encode()).hexdigest(),
            "seed_length":len(seed),
            "extraction":"first seven direct children, XML itertext, normalized spaces",
            "license":"CC BY-NC-SA 4.0"}
    report={"protocol":"OMEGA-MEMORY-REAL-02",
            "stage":"ACQUISITION","source":source,
            "model_calls":0,"theorems_certified":0,"paid_api_calls":0,
            "model_weights_updated":False}
    save_report(root,report)
    model=RealClient(endpoint)
    original=library.CARD_TASK
    try:
        library.CARD_TASK=original+CARD_SUFFIX
        # Keep base library unchanged. The added bounded formal fields are
        # verified separately; they are not promoted to scientific memory.
        def model_call(messages,tokens):
            return model(messages,900 if tokens==550 else tokens)
        report["research"]=library.run(seed,root/"candidate.jsonl",
                     endpoint=endpoint,max_hops=1,model_call=model_call)
    finally:
        library.CARD_TASK=original
        report["model_calls"]=len(model.calls)
        report["model_metrics"]=model.calls
        report["stage"]="ACQUISITION_ATTEMPTED"
        save_report(root,report)
    return report

def prompt_budget(endpoint,text):
    # Only a relative, local llama.cpp token count for prompt-size matching.
    body=json.dumps({"content":text}).encode()
    req=Request(endpoint.rstrip("/")+"/tokenize",data=body,
                headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=20) as resp:
        payload=json.load(resp)
    return len(payload["tokens"])

def equalize_contexts(endpoint,contexts):
    size=max(prompt_budget(endpoint,s) for s in contexts.values())
    padded={}
    for arm,body in contexts.items():
        # deterministic neutral filler; never contains relation vocabulary
        for i in range(300):
            if prompt_budget(endpoint,body)>=size:break
            body+="\nUnrelated administrative placeholder."
        padded[arm]=body
    actual={k:prompt_budget(endpoint,v) for k,v in padded.items()}
    if max(actual.values())-min(actual.values())>3:
        raise ValueError("PROMPT_TOKEN_MATCH_FAILED")
    return padded,actual

def memory_phase(root,endpoint):
    report=json.loads((root/"report.json").read_text())
    records=read_ledger(root/"candidate.jsonl") if (root/"candidate.jsonl").exists() else []
    if len(records)!=1:
        report["stage"]="BLOCKED_NO_SINGLE_CARD";save_report(root,report);return report
    entry=records[0]
    guard=entry["verification"]
    if not guard.get("schema_valid") or not guard.get("verbatim_source_quote_valid"):
        report["stage"]="BLOCKED_INVALID_JSON_OR_QUOTE";save_report(root,report);return report
    seed=(root/"seed.txt").read_text()
    fidelity=inspect_bounded(entry["interpretation_candidate"],
                       guard["verbatim_source_quote_valid"],seed)
    report["bounded_fidelity"]=fidelity
    save_report(root,report)
    if not fidelity["bounded_pass"]:
        report["stage"]="BLOCKED_BOUNDED_FIDELITY";save_report(root,report);return report

    # This is a new interpreter process. Re-read verified ledger and inject
    # ONLY model-proposed + independently checked formal facts, not prose.
    target=fidelity["target"]
    sig=TARGETS[target]
    core={"concept":target,"defining_axioms":list(sig),
          "candidate_id":entry["candidate_id"]}
    tasks=holdout(sig)
    report["holdout_sha256"]=sha256(canonical(tasks).encode()).hexdigest()
    report["candidate_id_reloaded"]=entry["candidate_id"]
    model=RealClient(endpoint)
    rows=[]
    for task in tasks:
        question=("Classify this finite relation as '"+target+"'. Return exactly "
            "a JSON object with boolean 'holds' and array 'failed_axioms' "
            "containing all required defining axioms that fail. Abstain if "
            "uncertain? You may instead return JSON with abstain set true. Nodes: "
            +canonical(NODES)+"; edges: "+canonical(task["edges"]))
        contexts={"D":"No educational note is available.",
                  "M":"Verified formal memory note: "+canonical(core),
                  "N":"Note from the archive, content withheld: "+canonical(
                      {"concept":"[WITHHELD]","defining_axioms":"[WITHHELD]",
                       "candidate_id":entry["candidate_id"]})}
        contexts,budgets=equalize_contexts(endpoint,contexts)
        order=["D","M","N"]
        random.Random(318+task["mask"]).shuffle(order)
        row={"id":task["id"],"edges":task["edges"],
             "oracle_holds":task["truth"],"order":order,
             "padded_context_tokens":budgets,"arms":{}}
        for arm in order:
            messages=[{"role":"system","content":"You are a finite relation reader."},
                 {"role":"user","content":"[UNTRUSTED MEMORY]\n"+contexts[arm]
                 +"\n[END MEMORY]\n"+question}]
            result=model(messages,260)
            prediction=parse_answer(result["text"],sig)
            row["arms"][arm]={"raw":result["text"],"parsed":prediction,
                   "correct":prediction==task["truth"] if prediction is not None else None,
                   "usage":result["usage"],"seconds":result["time_s"]}
        rows.append(row)
        report["memory"]={"status":"PARTIAL","tasks":rows}
        save_report(root,report)

    counts={}
    for arm in ("D","M","N"):
        vals=[x["arms"][arm] for x in rows]
        counts[arm]={"correct":sum(v["correct"] is True for v in vals),
                     "errors":sum(v["correct"] is False for v in vals),
                     "abstentions_or_invalid":sum(v["correct"] is None for v in vals),
                     "prompt_tokens":sum(v["usage"].get("prompt_tokens",0) for v in vals),
                     "completion_tokens":sum(v["usage"].get("completion_tokens",0) for v in vals)}
    prompt_counts=[counts[a]["prompt_tokens"] for a in ("D","M","N")]
    comparable=min(prompt_counts)>0 and (max(prompt_counts)-min(prompt_counts))/min(prompt_counts)<=.05
    gain=bool(comparable and counts["M"]["correct"]>=3
        and counts["M"]["correct"]>=counts["D"]["correct"]+2
        and counts["M"]["correct"]>=counts["N"]["correct"]+2
        and counts["M"]["errors"]==0)
    report["memory"]={"status":"COMPLETE","tasks":rows,"metrics":counts,
                      "prompt_budget_equal_within_five_percent":comparable,
                      "registered_bounded_memory_gain":gain,
                      "full_textual_semantics_proved":False}
    report["stage"]="EVALUATED"
    report["model_calls"]+=len(model.calls)
    report["memory_model_metrics"]=model.calls
    save_report(root,report)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",required=True,choices=("acquire","memory"))
    ap.add_argument("--source-file",default="")
    ap.add_argument("--output",required=True)
    ap.add_argument("--server",default="http://127.0.0.1:8080")
    args=ap.parse_args()
    root=Path(args.output)
    if args.phase=="acquire":report=acquire_phase(root,args.source_file,args.server)
    else:report=memory_phase(root,args.server)
    print(json.dumps({"stage":report["stage"],
                      "calls":report["model_calls"],
                      "fidelity":report.get("bounded_fidelity"),
                      "memory":(report.get("memory") or {}).get("metrics")},
                     ensure_ascii=False))

if __name__=="__main__":main()
