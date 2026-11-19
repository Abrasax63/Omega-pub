#!/usr/bin/env python3
"""CONTRAST27: external audited NL vs two original Lean theorem candidates.

No new Lean proof or autoformalization is generated. The task is original
pair retrieval, with A/B permutations to reject position heuristics. Same
underlying Qwen replies feed direct and stability/marker-gated decisions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"proofnet26"))
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
from runner import fetch_pinned, extract_original_pair
from read import blob as git_blob

FROZEN=HERE/"FROZEN_PAIRS.json"
SERVER="http://127.0.0.1:8091/v1/chat/completions"
MODEL_SHA={
    "0p5b":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b":"626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
LLAMA_SHA="5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
EXPECTED_PAIRS=((4,5),(7,8),(9,11),(12,13),(14,15),(16,17),
                (18,19),(20,21),(23,24),(25,26),(27,28),(29,30))
MAX_NEW_TOKENS=64


def manifest()->dict:
    data=json.loads(FROZEN.read_text(encoding="utf8"))
    if (data.get("status")!="FROZEN_BEFORE_ANY_REAL_INFERENCE_OR_CODE"
        or tuple(map(tuple,data["pairs"]))!=EXPECTED_PAIRS
        or len(data["source_docs"])!=24
        or [x["index"] for x in data["source_docs"]] != [i for pair in EXPECTED_PAIRS for i in pair]
        or len({x["git_blob"] for x in data["source_docs"]})!=24
        or data["source_commit"]!="b7ca411a2abaa6caf3580192b30d865e5bd10bc4"):
        raise ValueError("BROKEN_FROZEN_EXTERNAL_COHORT")
    return data


def anonymize_reference(lean:str)->str:
    """Remove identifiers and sorry only; preserve every logical binder/token.

    Theorem name may encode the original exercise title and trivially leak
    identity. Never include it, source ID or URL in a model prompt.
    """
    found=re.match(r"\s*theorem\s+([A-Za-z0-9_']+)",lean)
    if not found:
        raise ValueError("INVALID_LEAN_THEOREM_DECLARATION")
    neutral="theorem candidate"+lean[found.end():]
    neutral=re.sub(r":= by\s*\n\s*sorry\s*\Z","",neutral)
    if (neutral==lean or ":= by" in neutral or "sorry" in neutral
        or len(neutral.strip())<30):
        raise ValueError("THEOREM_NORMALIZATION_FAILED")
    return neutral.strip()


def prepare(*,cache_dir:Path|None=None)->list[dict]:
    source=manifest()
    all_docs={}
    for item in source["source_docs"]:
        raw=fetch_pinned(item,cache_dir=cache_dir)
        ref=extract_original_pair(raw,item)
        informal=ref["informal_statement_exact"]
        lean=ref["reference_lean_theorem_exact"]
        code=anonymize_reference(lean)
        if not informal.strip():
            raise ValueError("EMPTY_REFERENCE_STATEMENT")
        all_docs[item["index"]]={
            "index":item["index"],"nl":informal,
            "lean_code":code,
            "original_theorem_sha256":ref["reference_lean_sha256"],
            "informal_sha256":ref["informal_sha256"],
            "source_blob":item["git_blob"],
            "source_url":item["source_url"],
        }
    tasks=[]
    for first,second in EXPECTED_PAIRS:
        d1,d2=all_docs[first],all_docs[second]
        if d1["lean_code"]==d2["lean_code"]:
            raise ValueError("IDENTICAL_NEGATIVE_LEAN_CANDIDATES")
        for idx,opp in ((first,second),(second,first)):
            original,other=all_docs[idx],all_docs[opp]
            if original["source_blob"]==other["source_blob"]:
                raise ValueError("NEGATIVE_IS_SAME_ORIGINAL_SOURCE")
            tasks.append({
                "index":idx,"decoy_index":opp,"source_blob":original["source_blob"],
                "source_url":original["source_url"],
                "informal_statement_exact":original["nl"],
                "reference_lean_sha256":original["original_theorem_sha256"],
                "own_lean":original["lean_code"],
                "decoy_lean":other["lean_code"],
                "decoy_source_blob":other["source_blob"],
                "negative_equivalence_human_checked":False,
            })
    if len(tasks)!=24 or len({t["index"] for t in tasks})!=24:
        raise ValueError("SOURCE_COHORT_MISMATCH")
    return tasks


def assigned(task:dict,orientation:int)->dict:
    if orientation not in (0,1):
        raise ValueError("INVALID_ORIENTATION")
    # Both positions occur once per case; fixed A-only has exactly 50%.
    own_is_A=(task["index"]%2 == 0) ^ (orientation==1)
    options={
        "A":task["own_lean"] if own_is_A else task["decoy_lean"],
        "B":task["decoy_lean"] if own_is_A else task["own_lean"],
    }
    if options["A"]==options["B"]:
        raise ValueError("DUPLICATE_OPTION_CODE")
    return {
        "orientation":orientation,"correct_option":"A" if own_is_A else "B",
        "options":options,
    }


def prompt(task:dict,orientation:int)->tuple[list[dict],dict]:
    config=assigned(task,orientation)
    messages=[
        {"role":"system","content":(
            "You are evaluating the correspondence between an original "
            "natural-language mathematical theorem and a formal Lean theorem "
            "statement. Choose the candidate which best matches the ORIGINAL "
            "mathematical meaning, quantifiers, assumptions and conclusion. "
            "Return only A, B, or NONE. If neither is defensible, NONE. "
            "Do not prove either theorem."
        )},
        {"role":"user","content":(
            "NATURAL LANGUAGE THEOREM:\n"+
            task["informal_statement_exact"]+
            "\n\nLEAN CANDIDATE A:\n"+config["options"]["A"]+
            "\n\nLEAN CANDIDATE B:\n"+config["options"]["B"]+
            "\n\nAnswer (A, B, or NONE):"
        )},
    ]
    joined=json.dumps(messages,ensure_ascii=False)
    forbidden=(str(task["source_url"]),str(task["source_blob"]),
               f"proofnet-{task['index']}",f"proofnet-{task['decoy_index']}")
    if any(x in joined for x in forbidden):
        raise ValueError("LABEL_LEAKED_TO_MODEL_PROMPT")
    return messages,config


def parse_model_choice(raw:str)->str:
    if not isinstance(raw,str):
        raise ValueError("NON_STRING_REPLY")
    canonical=raw.strip()
    return canonical if canonical in ("A","B","NONE") else "INVALID"


def semantic_marker_check(natural:str,chosen_lean:str)->dict:
    """Only a *warning* (not a theorem or full semantic equivalence test).
    This never chooses a candidate or uses gold labels.
    """
    x=natural.lower()
    y=chosen_lean
    missing=[]
    supported=[]
    numbers=set(re.findall(r"(?<![A-Za-z0-9])\d{1,4}(?![A-Za-z0-9])",natural))
    lean_numbers=set(re.findall(r"(?<![A-Za-z0-9])\d{1,4}(?![A-Za-z0-9])",chosen_lean))
    for n in sorted(numbers):
        if n not in lean_numbers:
            missing.append("MISSING_LITERAL_NUMBER_"+n)
        else:
            supported.append("SHARED_LITERAL_NUMBER_"+n)
    if re.search(r"\bif and only if\b|\\iff\b|\\Leftrightarrow",x,re.I):
        if "↔" not in y and "Iff" not in y:
            missing.append("MISSING_EXPLICIT_IFF")
        else:
            supported.append("SHARED_IFF_MARKER")
    if re.search(r"\bthere (?:is|exists?|are)\b|\\exists",x,re.I):
        if "∃" not in y and "Nonempty" not in y and "Exists" not in y:
            missing.append("MISSING_EXPLICIT_EXISTENTIAL_MARKER")
        else:
            supported.append("SHARED_EXISTENTIAL_MARKER")
    return {
        "status":"SUSPECT_MISSING_EXPLICIT_MARKER" if missing else
                 "NO_EXPLICIT_CONTRADICTION_DETECTED",
        "missing":missing,"supported":supported,
        "is_semantic_proof":False,
    }


def call_local(messages:list[dict])->dict:
    body={"messages":messages,"temperature":0,"max_tokens":MAX_NEW_TOKENS,
          "stream":False}
    req=urllib.request.Request(
        SERVER, data=json.dumps(body,ensure_ascii=False).encode("utf8"),
        headers={"Content-Type":"application/json"},method="POST",
    )
    t0=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as response:
        obj=json.loads(response.read(160000))
    info=obj["choices"][0]
    if not isinstance(info["message"]["content"],str):
        raise ValueError("NON_TEXT_MODEL_RESPONSE")
    return {
        "raw_reply":info["message"]["content"],
        "elapsed_seconds":round(time.perf_counter()-t0,3),
        "usage":obj.get("usage"),
        "finish_reason":info.get("finish_reason"),
        "server_model":obj.get("model"),
    }


def generation(task:dict,orientation:int,model:str,call=call_local)->dict:
    messages,setup=prompt(task,orientation)
    data=call(messages)
    if data["finish_reason"]=="length":
        raise ValueError("TRUNCATED_MODEL_RESPONSE")
    choice=parse_model_choice(data["raw_reply"])
    selected_original_id=None
    if choice in ("A","B"):
        selected_original_id=task["index"] if choice==setup["correct_option"] else task["decoy_index"]
    # The semantic marker gate consumes only the chosen Lean code and NL, not gold.
    marker=semantic_marker_check(task["informal_statement_exact"],setup["options"][choice]) if choice in ("A","B") else None
    return {
        "index":task["index"],"decoy_index":task["decoy_index"],
        "model":model,"orientation":orientation,
        "original_source_blob":task["source_blob"],
        "decoy_source_blob":task["decoy_source_blob"],
        "source_url":task["source_url"],
        "original_nl":task["informal_statement_exact"],
        "correct_option_for_posthoc_scoring_only":setup["correct_option"],
        "options_sha256":{k:hashlib.sha256(v.encode("utf8")).hexdigest()
                          for k,v in setup["options"].items()},
        "prompts":messages,
        "raw_reply":data["raw_reply"],
        "parsed_choice":choice,
        "chosen_original_index":selected_original_id,
        "correct_original_pair":selected_original_id==task["index"],
        "marker_check":marker,
        "inference":data,
        "external_negative_semantic_equivalence_independently_adjudicated":False,
        "formal_certifications":0,
    }


def directly_score(rows:list[dict])->dict:
    return {
        "n":len(rows),
        "correct":sum(x["correct_original_pair"] for x in rows),
        "wrong":sum(x["chosen_original_index"] is not None and not x["correct_original_pair"] for x in rows),
        "abstained":sum(x["parsed_choice"]=="NONE" for x in rows),
        "invalid":sum(x["parsed_choice"]=="INVALID" for x in rows),
        "accuracy_over_all":round(sum(x["correct_original_pair"] for x in rows)/len(rows),5) if rows else None,
        "answer_rate":round(sum(x["chosen_original_index"] is not None for x in rows)/len(rows),5) if rows else None,
    }


def gated_score(rows:list[dict])->dict:
    bycase={}
    for x in rows:
        bycase.setdefault(x["index"],[]).append(x)
    if len(bycase)!=24 or any(len(x)!=2 or {z["orientation"] for z in x}!={0,1} for x in bycase.values()):
        raise ValueError("PAIR_ORIENTATION_COVERAGE_INCOMPLETE")
    results=[]
    for index,pair in sorted(bycase.items()):
        a,b=sorted(pair,key=lambda x:x["orientation"])
        selections=[x["chosen_original_index"] for x in (a,b)]
        stable=(selections[0] is not None and selections[0]==selections[1])
        marker_clear=(stable and a["marker_check"]["status"]=="NO_EXPLICIT_CONTRADICTION_DETECTED"
                      and b["marker_check"]["status"]=="NO_EXPLICIT_CONTRADICTION_DETECTED")
        results.append({
            "index":index,"orientation_0_correct":a["correct_original_pair"],
            "orientation_1_correct":b["correct_original_pair"],
            "same_original_lean_selected":stable,
            "stable_chosen_index":selections[0] if stable else None,
            "stable_correct":stable and selections[0]==index,
            "structural_marker_pass":marker_clear,
            "combined_accepted_correct":marker_clear and selections[0]==index,
            "declined_due_to_swap":not stable,
            "declined_due_to_marker":bool(stable and not marker_clear),
            "potential_equivalent_negative_unreviewed":True,
        })
    def summarize(prefix,accept_field,correct_field)->dict:
        count=sum(x[accept_field] for x in results)
        tp=sum(x[correct_field] for x in results)
        return {
            "accepted":count,"correct":tp,"wrong":count-tp,
            "coverage":round(count/24,5),
            "accepted_pair_precision":round(tp/count,5) if count else None,
        }
    return {
        "n_cases":24,
        "order_swap_stability":summarize("stable","same_original_lean_selected","stable_correct"),
        "stability_plus_semantic_markers":summarize("joint","structural_marker_pass","combined_accepted_correct"),
        "rows":results,
    }


def load_reference(*,offline_dir:Path|None=None)->dict:
    tasks=prepare(cache_dir=offline_dir)
    totals={"n_cases":len(tasks),"n_pairs":len(EXPECTED_PAIRS),
            "source_status":"FROZEN_EXTERNAL_GIT_BLOBS_VERIFIED",
            "chosen_original_pair_reference":"INDEPENDENTLY_CURATED_UPSTREAM",
            "decoy_non_equivalence_human_annotated":False,
            "n_ordered_prompts":48,
            "source_items":[{
                "index":t["index"],"source_blob":t["source_blob"],
                "source_url":t["source_url"],"nl_sha256":hashlib.sha256(t["informal_statement_exact"].encode()).hexdigest(),
                "lean_sha256":hashlib.sha256(t["own_lean"].encode()).hexdigest(),
                "decoy_index":t["decoy_index"],
                "reference_math_semantics_guarantee":"ONLY_SOURCE_PAIRING_NOT_DECOY_NON_EQUIVALENCE",
            } for t in tasks],
            "all_model_prompts_without_gold":True,
            "baseline_always_A_accuracy":0.5,"baseline_always_B_accuracy":0.5,
            "baseline_abstain_coverage":0,
    }
    for t in tasks:
        configs=[prompt(t,k)[1] for k in (0,1)]
        if {x["correct_option"] for x in configs}!={"A","B"}:
            raise ValueError("UNBALANCED_LABELS_PER_CASE")
    return totals


def run_model(model:str,*,offline_dir:Path|None=None)->dict:
    if model not in MODEL_SHA:
        raise ValueError("UNKNOWN_MODEL")
    tasks=prepare(cache_dir=offline_dir)
    rows=[]
    for task in tasks:
        for order in (0,1):
            row=generation(task,order,model)
            rows.append(row)
            print("CONTRAST27",model,task["index"],order,
                  repr(row["raw_reply"]),row["chosen_original_index"],flush=True)
    return {
        "status":"COMPLETED_REAL_MODEL_INFERENCE",
        "model":model,"model_sha256":MODEL_SHA[model],
        "llama_cpp_sha":LLAMA_SHA,
        "n_cases":len(tasks),"n_generations":len(rows),
        "rows":rows,
        "direct_first":directly_score([x for x in rows if x["orientation"]==0]),
        "direct_swapped":directly_score([x for x in rows if x["orientation"]==1]),
        "direct_both":directly_score(rows),
        "gated":gated_score(rows),
        "inference_seconds":round(sum(x["inference"]["elapsed_seconds"] for x in rows),3),
        "certified_lean_proofs":0,
        "interpretation_generation":"NONE_ONLY_REFERENCE_SELECTION",
    }


def compare(control:dict,a:dict,b:dict)->dict:
    if (control["n_cases"]!=24 or control["n_ordered_prompts"]!=48
        or {a.get("model"),b.get("model")}!={"0p5b","3b"}
        or any(x["status"]!="COMPLETED_REAL_MODEL_INFERENCE" or x["n_generations"]!=48 for x in (a,b))):
        raise ValueError("INCOMPLETE_EQUAL_BUDGET_PAIRING")
    if ([x["index"] for x in a["rows"]]!=[x["index"] for x in b["rows"]]
        or [x["orientation"] for x in a["rows"]]!=[x["orientation"] for x in b["rows"]]
        or [x["original_source_blob"] for x in a["rows"]]!=[x["original_source_blob"] for x in b["rows"]]
        or [x["options_sha256"] for x in a["rows"]]!=[x["options_sha256"] for x in b["rows"]]):
        raise ValueError("MODELS_NOT_COMPARABLE_SAME_PROMPTS")
    out={}
    for v in (a,b):
        out[v["model"]]={
            "first":v["direct_first"],"swapped":v["direct_swapped"],
            "both":v["direct_both"],
            "stability":v["gated"]["order_swap_stability"],
            "stable_plus_markers":v["gated"]["stability_plus_semantic_markers"],
            "runtime_seconds":v["inference_seconds"],
            "by_case":v["gated"]["rows"],
        }
    return {
        "status":"COMPLETED_EXTERNAL_CONTRASTIVE_SELECTION_PROXY",
        "original_reference_items":24,
        "experimental_calls":96,
        "always_A_or_B_chance_baseline":0.5,
        "original_pair_gold_origin":"EXTERNALLY_CURATED_PROOFNET_VERIFIED",
        "decoy_non_equivalence_human_verified":False,
        "cannot_claim_full_semantic_fidelity":True,
        "not_a_lean_autoformalizer":True,
        "not_a_general_math_model":True,
        "formal_certifications":0,
        "scores":out,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("control","model","compare"),required=True)
    p.add_argument("--model",choices=("0p5b","3b"))
    p.add_argument("--offline-dir",type=Path)
    p.add_argument("--control",type=Path)
    p.add_argument("--small",type=Path)
    p.add_argument("--large",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    failed=False
    try:
        if args.mode=="control":
            data={"status":"FROZEN_CONTROLS_VALIDATED",**load_reference(offline_dir=args.offline_dir)}
        elif args.mode=="model":
            data=run_model(args.model,offline_dir=args.offline_dir)
        else:
            c=json.loads(args.control.read_text(encoding="utf8"))
            a=json.loads(args.small.read_text(encoding="utf8"))
            b=json.loads(args.large.read_text(encoding="utf8"))
            data=compare(c,a,b)
    except Exception:
        data={"status":"FAILED_NO_VALID_SCIENTIFIC_COMPARISON",
              "error":traceback.format_exc()}
        failed=True
    args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("CONTRAST27",args.mode,data["status"],flush=True)
    if failed:
        sys.exit(1)

if __name__=="__main__":
    main()
