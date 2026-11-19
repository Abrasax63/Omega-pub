#!/usr/bin/env python3
"""Reader Creative02: evaluate proposals *only after raw inference artifact exists*.

Model cannot access cases from prompt. Python never executes model-authored
source code. No tuning after results, novel math or self-improvement claims.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from dsl import InvalidProposal, parse_proposal, execute_proposal
from propose import MODEL, GGUF_SHA256, MESSAGES, SCHEDULE, MAX_OUTPUT

SEED=20261119
HOLDOUT_COUNT=80
METAMORPH_COUNT=16
MAX_ENUM_LENGTH=12


def stack_baseline(s:str)->tuple[bool,int]:
    # Strong standard classical algorithm, O(n) worst-case.
    stack=0;visits=0
    for c in s:
        visits+=1
        if c=="(":
            stack+=1
        else:
            stack-=1
            if stack<0:
                return False,visits
    return stack==0,visits


def cancellation_oracle(s:str)->bool:
    """Independent reference: rewrite adjacent '()' pairs until no more exist."""
    previous=None
    while s!=previous:
        previous=s
        s=s.replace("()","")
    return s==""


def balanced(rng:random.Random,pairs:int)->str:
    seen_open=0
    open_unclosed=0
    out=[]
    while seen_open<pairs or open_unclosed:
        if seen_open>=pairs:
            out.append(")")
            open_unclosed-=1
        elif open_unclosed==0 or rng.random()<0.55:
            out.append("(")
            open_unclosed+=1
            seen_open+=1
        else:
            out.append(")")
            open_unclosed-=1
    return "".join(out)


def cohorts(seed=SEED):
    rng=random.Random(seed)
    cases=[]
    for i in range(40):
        text=balanced(rng,rng.randint(2,24))
        cases.append({"id":f"V{i+1:02d}","word":text,"generation":"CONSTRUCTED_VALID"})
    for i in range(20):
        text=balanced(rng,rng.randint(2,24))
        cases.append({"id":f"F{i+1:02d}","word":")"+text[1:],
                      "generation":"CORRUPT_FIRST_BRACKET"})
    for i in range(20):
        text=balanced(rng,rng.randint(2,24))
        cases.append({"id":f"S{i+1:02d}","word":")"+text[1:-1]+"(",
                      "generation":"SWAP_BOUNDARY_BRACKETS"})
    metamorph=[]
    for i in range(8):
        a=balanced(rng,rng.randint(2,12))
        b=balanced(rng,rng.randint(2,12))
        word=a+b
        metamorph.append({"id":f"M{i+1:02d}","word":word,
                          "generation":"CONCATENATE_VALID_WORDS"})
        metamorph.append({"id":f"M{i+9:02d}","word":")"+word[1:],
                          "generation":"CORRUPT_CONCATENATION"})
    if len(cases)!=HOLDOUT_COUNT or len(metamorph)!=METAMORPH_COUNT:
        raise AssertionError("FROZEN_COHORT_LENGTH")
    return cases,metamorph


def exhaustive():
    for n in range(MAX_ENUM_LENGTH+1):
        for word in itertools.product("()",repeat=n):
            yield "".join(word)


def sha256_json(value)->str:
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                              separators=(",",":")).encode("utf-8")).hexdigest()


def assess_proposal(row:dict,holdout:list,metamorph:list,words:list[str]) -> dict:
    observed={"attempt":row["attempt"],"seed":row["seed"],
              "temperature":row["temperature"],
              "raw_reply_sha256":row.get("raw_sha256"),
              "status":"ABSTAIN_INVALID_PROPOSAL",
              "parse_error":None,"ast":None,
              "holdout_correct":0,"holdout_count":len(holdout),
              "metamorphic_correct":0,"metamorphic_count":len(metamorph),
              "exhaustive_correct":0,"exhaustive_count":len(words),
              "false_accepts":0,"false_rejects":0,
              "bounded_equivalence_not_general_proof":True,
              "new_math_theorem":False,
              "idea_is_new_to_lab_library_not_global_novelty":None,
              "first_disagreement":None,"chars_inspected":0}
    if row["status"]!="MODEL_RAW_FROZEN":
        observed["parse_error"]="NO_REAL_MODEL_PROPOSAL"
        return observed
    raw=row.get("raw_reply")
    if not isinstance(raw,str) or hashlib.sha256(raw.encode("utf-8")).hexdigest()!=row.get("raw_sha256"):
        observed["parse_error"]="RAW_REPLY_SHA_MISMATCH"
        return observed
    try:
        proposal=parse_proposal(raw)
    except InvalidProposal as error:
        observed["parse_error"]=str(error)
        return observed
    observed["ast"]=proposal
    observed["idea_is_new_to_lab_library_not_global_novelty"]=True
    observed["status"]="VALID_AST_UNDER_EVALUATION"
    for label,batch in (
        ("holdout_correct", [x["word"] for x in holdout]),
        ("metamorphic_correct",[x["word"] for x in metamorph]),
        ("exhaustive_correct",words),
    ):
        for s in batch:
            truth,_=stack_baseline(s)
            guess,visits=execute_proposal(proposal,s)
            observed["chars_inspected"]+=visits
            if guess==truth:
                observed[label]+=1
            else:
                if guess:
                    observed["false_accepts"]+=1
                else:
                    observed["false_rejects"]+=1
                discrepancy={"word":s,"length":len(s),"truth":truth,"guess":guess,
                             "set":label}
                if observed["first_disagreement"] is None or (
                        (len(s),s)<(observed["first_disagreement"]["length"],
                                    observed["first_disagreement"]["word"])):
                    observed["first_disagreement"]=discrepancy
    if (observed["holdout_correct"]==HOLDOUT_COUNT
        and observed["metamorphic_correct"]==METAMORPH_COUNT
        and observed["exhaustive_correct"]==len(words)):
        observed["status"]="EMPIRICAL_BOUNDED_EQUIVALENCE"
    else:
        observed["status"]="FALSIFIED_BY_FINITE_EXACT_TEST"
    return observed


def grade(frozen:dict)->dict:
    if frozen.get("experiment")!="OMEGA_CREATIVE_MODEL02_RAW_UNGRADED_PROPOSALS":
        raise ValueError("WRONG_UNGRADED_ARTIFACT_TYPE")
    if frozen.get("model")!=MODEL or frozen.get("model_gguf_sha256")!=GGUF_SHA256:
        raise ValueError("MODEL_ID_OR_WEIGHTS_CHANGED")
    if frozen.get("prompt_sha256")!=sha256_json(MESSAGES):
        # Match how propose.py serializes its prompt (default separators).
        check=hashlib.sha256(json.dumps(MESSAGES,sort_keys=True).encode()).hexdigest()
        if frozen.get("prompt_sha256")!=check:
            raise ValueError("MODEL_PROMPT_NOT_PREREGISTERED")
    expected=list(SCHEDULE)
    got=frozen.get("proposals")
    if not isinstance(got,list) or len(got)!=3:
        raise ValueError("NOT_THREE_FROZEN_MODEL_ATTEMPTS")
    if [(x.get("seed"),x.get("temperature")) for x in got]!=expected:
        raise ValueError("MODEL_CALL_SCHEDULE_CHANGED")
    holdout,metamorph=cohorts()
    exhaustive_words=list(exhaustive())
    if len(exhaustive_words)!=8191:
        raise AssertionError("ENUMERATION_SIZE_CHANGED")
    ground={}
    all_items=holdout+metamorph
    for item in all_items:
        s=item["word"]
        if not 0<=len(s)<=128:
            raise AssertionError("STRING_SCOPE_OVERFLOW")
        truth,operations=stack_baseline(s)
        independent=cancellation_oracle(s)
        if independent!=truth:
            raise AssertionError("INDEPENDENT_REFERENCE_CONTRADICTION")
        ground[item["id"]]=truth
    if (sum(ground[x["id"]] for x in holdout)!=40 or
        sum(ground[x["id"]] for x in metamorph)!=8):
        raise AssertionError("GENERATED_POSITIVE_NEGATIVE_BALANCE_DRIFT")
    direct_and_strong_agree=sum(
        cancellation_oracle(s)==stack_baseline(s)[0] for s in exhaustive_words
    )
    if direct_and_strong_agree!=8191:
        raise AssertionError("EXHAUSTIVE_REFERENCE_CONTRADICTION")
    results=[assess_proposal(x,holdout,metamorph,exhaustive_words) for x in got]
    return {
        "experiment":"OMEGA_CREATIVE_MODEL02_POST_FROZEN_PROPOSALS",
        "run_status":"EVALUATED_FROZEN_PROPOSALS",
        "inference_artifact_prompt_sha256":frozen["prompt_sha256"],
        "inference_weights_sha256":frozen["model_gguf_sha256"],
        "inference_schedule":[{"seed":x[0],"temperature":x[1]} for x in expected],
        "proposal_digests":[x.get("raw_sha256") for x in got],
        "corpus_seed":SEED,
        "holdout_cases":HOLDOUT_COUNT,
        "metamorphic_cases":METAMORPH_COUNT,
        "exhaustive_cases":len(exhaustive_words),
        "corpus_sha256":sha256_json({"holdout":holdout,"metamorphic":metamorph}),
        "ground_truth_sha256":sha256_json(ground),
        "strong_baseline_correct":len(all_items)+len(exhaustive_words),
        "weak_direct_baseline_correct":len(all_items)+len(exhaustive_words),
        "independent_oracles_agreed":True,
        "model_proposals_accepted":sum(x["status"] in (
            "EMPIRICAL_BOUNDED_EQUIVALENCE","FALSIFIED_BY_FINITE_EXACT_TEST")
            for x in results),
        "model_proposals_bounded_equivalent":sum(x["status"]=="EMPIRICAL_BOUNDED_EQUIVALENCE"
                                                  for x in results),
        "general_equivalence_proved":False,
        "spontaneous_general_creativity_proved":False,
        "model_weight_updates":0,"new_mathematical_theorems":0,
        "scientific_autopromotions":0,"paid_api_calls":0,
        "fair_cpu_cost_comparison":False,
        "raw_proposals_unchanged":True,
        "assessment":results,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    raw=json.loads(args.frozen.read_text(encoding="utf-8"))
    report=grade(raw)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CREATIVE02",report["run_status"],
          "valid ASTs",report["model_proposals_accepted"],
          "bounded-equivalent",report["model_proposals_bounded_equivalent"])
    for result in report["assessment"]:
        print(result["attempt"],result["status"],result["parse_error"],
              result["holdout_correct"],result["metamorphic_correct"],
              result["exhaustive_correct"],result["first_disagreement"],
              flush=True)


if __name__=="__main__":
    main()
