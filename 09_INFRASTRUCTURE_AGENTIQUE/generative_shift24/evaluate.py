#!/usr/bin/env python3
"""GEN24 independent post-proposal scoring, provenance and negative evidence.

Stage predict cannot load gold or import a reachability oracle. Stage audit
runs BFS and an independent Gaussian-elimination baseline only AFTER the
candidate decisions have been persisted and content-hashed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from expression_interpreter import UnsupportedExpression,extract_expression,interpret
CASES=HERE/"CASES_FROZEN.json"
GOLD=HERE/"GOLD_NOT_FED_TO_LLM.json"
CASES_BLOB="28b25b17bb6bb73eb7b625c245d1cbc361b32ec0"
GOLD_BLOB="4932f03c5e10d6b7394c2b96971a4578e48198af"
MAX_ROWS=64


def git_blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def load_pinned(path:Path,pin:str)->dict:
    raw=path.read_bytes()
    if len(raw)>50000 or git_blob(raw)!=pin:
        raise ValueError("FROZEN_FIXTURE_BLOB_MISMATCH")
    return json.loads(raw)


def validate_cases(data:dict)->list[dict]:
    cases=data["cases"]
    if len(cases)!=MAX_ROWS or len({x["id"] for x in cases})!=MAX_ROWS:
        raise ValueError("BAD_FROZEN_COHORT")
    for i,c in enumerate(cases):
        n=c["n"]; moves=c["moves"]; lo=1<<n
        if not 5<=n<=8 or not 2<=len(moves)<=5 or len(set(moves))!=len(moves):
            raise ValueError("CASE_LIMITS_CHANGED")
        if any(type(x)!=int or not 0<x<lo for x in moves):
            raise ValueError("OUT_OF_DOMAIN_ACTION")
        if any(type(x)!=int or not 0<=x<lo for x in (c["start"],c["target"])):
            raise ValueError("OUT_OF_DOMAIN_STATES")
        if c["id"]!=f"R{i+1:03d}":
            raise ValueError("CASE_ID_ORDER_DRIFT")
    return cases


def mutations(c:dict,index:int)->list[dict]:
    """Three transformations that preserve reachability, without changing n."""
    moves=c["moves"]
    mask=(7+13*index)&((1<<c["n"])-1)
    return [
        {**c,"moves":list(reversed(moves)),"mutation":"reverse_moves"},
        {**c,"moves":moves[1:]+moves[:1],"mutation":"rotate_moves"},
        {**c,"start":c["start"]^mask,"target":c["target"]^mask,
         "mutation":"translate_both_states_xor"},
    ]


def is_linear_idea(text:str)->bool:
    if not isinstance(text,str) or len(text)>10000:
        return False
    return bool(re.search(
        r"linear|vector|basis|span|rank|gaussian|gf\s*\(?2\)?|"
        r"algèbre|algebra|espace vectoriel|base linéaire|rang|"
        r"xor.*(space|vector)",
        text,re.I,
    ))


def predict(proposal:dict)->dict:
    if proposal.get("status")!="COMPLETED_REAL_MODEL_INFERENCE" or proposal.get("model_calls")!=4:
        raise ValueError("NO_REAL_FOUR_CALLS_PROPOSAL")
    if len(proposal.get("results",[]))!=2:
        raise ValueError("MISSING_PROMPT_VARIANTS")
    cases=validate_cases(load_pinned(CASES,CASES_BLOB))
    results=[]
    for p in proposal["results"]:
        reply=p["formalization_after_DSL"]["reply"]
        idea=p["idea_before_DSL"]["reply"]
        if hashlib.sha256(idea.encode()).hexdigest()!=p["first_idea_sealed_sha256"]:
            raise ValueError("IDEA_NOT_SEALED")
        if p["feedback_from_oracle_seen"] or p["any_case_or_gold_sent_to_model"]:
            raise ValueError("INFERENCE_INFORMATION_LEAK_FLAG")
        expr=None; parse_error=None
        try:
            expr=extract_expression(reply)
        except UnsupportedExpression as exc:
            parse_error=str(exc)
        predictions=[]
        for i,c in enumerate(cases):
            # Predict original and all metamorphic cases BEFORE reading gold.
            for v,row in [("original",c)]+[(m["mutation"],m) for m in mutations(c,i)]:
                result={"case_id":c["id"],"variant":v,"prediction":None,
                        "status":"ABSTAIN_PARSE_OR_SCOPE","reason":parse_error}
                if expr is not None:
                    try:
                        decision=interpret(expr,moves=row["moves"],
                                           start=row["start"],target=row["target"])
                        result.update({"status":"PREDICTED","prediction":decision,
                                       "reason":None})
                    except UnsupportedExpression as exc:
                        result["reason"]=str(exc)
                predictions.append(result)
        results.append({
            "prompt_id":p["prompt_id"],
            "idea_before_DSL_hash":p["first_idea_sealed_sha256"],
            "idea_has_linear_family_keyword_proxy":is_linear_idea(idea),
            "raw_idea":idea,"raw_formal_reply":reply,
            "expression":expr,"parse_error":parse_error,
            "tokens_idea":p["idea_before_DSL"].get("tokens"),
            "tokens_formal":p["formalization_after_DSL"].get("tokens"),
            "idea_duration_s":p["idea_before_DSL"].get("duration_s"),
            "formal_duration_s":p["formalization_after_DSL"].get("duration_s"),
            "predictions":predictions,
        })
    stable=[
        {"prompt_id":r["prompt_id"],"idea_hash":r["idea_before_DSL_hash"],
         "expression":r["expression"],"predictions":r["predictions"]}
        for r in results
    ]
    hash_before_gold=hashlib.sha256(json.dumps(stable,sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()
    return {
        "experiment":"OMEGA_GEN24_PREDICTIONS_BEFORE_ORACLE",
        "status":"FROZEN_CANDIDATE_DECISIONS",
        "fixture_blob":CASES_BLOB,
        "gold_loaded":False,"labels_revealed_to_model":False,
        "proposals":len(results),"total_predictions":sum(len(x["predictions"]) for x in results),
        "stable_decisions_sha256_before_gold":hash_before_gold,
        "automatic_certifications":0,
        "models_used":1,
        "results":results,
    }


def bfs_reference(c:dict)->tuple[bool,int]:
    moves=c["moves"]
    seen={c["start"]}
    queue=[c["start"]]
    for current in queue:
        if current==c["target"]:
            return True,len(seen)
        for m in moves:
            nxt=current^m
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False,len(seen)


def strong_gaussian(c:dict)->tuple[bool,int]:
    """Independent GF(2) basis pivot reduction, distinct from AST rank2 method."""
    pivots=[0]*c["n"]
    ops=0
    def reduce(v,store):
        nonlocal ops
        for k in range(c["n"]-1,-1,-1):
            ops+=1
            if (v>>k)&1:
                if pivots[k]:
                    v^=pivots[k]
                elif store:
                    pivots[k]=v
                    return 0
                else:
                    return v
        return v
    for m in c["moves"]:
        reduce(m,True)
    diff=c["start"]^c["target"]
    return reduce(diff,False)==0,ops


def audit(predictions:dict)->dict:
    if predictions.get("status")!="FROZEN_CANDIDATE_DECISIONS" or predictions.get("gold_loaded"):
        raise ValueError("PREDICTIONS_NOT_SEALED")
    cases=validate_cases(load_pinned(CASES,CASES_BLOB))
    key=load_pinned(GOLD,GOLD_BLOB)["labels"]
    if len(key)!=64 or [x["id"] for x in key]!=[x["id"] for x in cases]:
        raise ValueError("GOLD_ID_MISMATCH")
    gold={x["id"]:x["reachable"] for x in key}
    direct_count=strong_count=0
    bfs_visited=gauss_ops=0
    expected={}
    for i,c in enumerate(cases):
        bfs,nvisited=bfs_reference(c)
        gaussian,nops=strong_gaussian(c)
        if bfs is not gaussian or bfs is not gold[c["id"]]:
            raise AssertionError("INDEPENDENT_REFERENCE_DISAGREEMENT")
        direct_count+=int(bfs==gold[c["id"]])
        strong_count+=int(gaussian==gold[c["id"]])
        bfs_visited+=nvisited
        gauss_ops+=nops
        expected[(c["id"],"original")]=bfs
        for variant in mutations(c,i):
            lhs,_=bfs_reference(variant)
            rhs,_=strong_gaussian(variant)
            if lhs is not bfs or rhs is not gaussian:
                raise AssertionError("METAMORPHIC_ORACLE_DISAGREEMENT")
            expected[(c["id"],variant["mutation"])]=bfs
    arms=[]
    for run in predictions["results"]:
        pos=wrong=abstentions=0
        first_wrong=None
        if len(run["predictions"])!=256:
            raise ValueError("PREDICTION_COUNT_CHANGED")
        for p in run["predictions"]:
            wanted=expected[(p["case_id"],p["variant"])]
            actual=p["prediction"]
            if p["status"]=="PREDICTED" and type(actual) is bool:
                if actual is wanted:
                    pos+=1
                else:
                    wrong+=1
                    if first_wrong is None:
                        first_wrong={
                            "case_id":p["case_id"],"variant":p["variant"],
                            "expected":wanted,"observed":actual,
                            "original_case":next(x for x in cases if x["id"]==p["case_id"])
                        }
            else:
                abstentions+=1
        originals=[p for p in run["predictions"] if p["variant"]=="original"]
        accurate_original=sum(p["status"]=="PREDICTED" and p["prediction"] is gold[p["case_id"]] for p in originals)
        wrong_original=sum(p["status"]=="PREDICTED" and p["prediction"] is not gold[p["case_id"]] for p in originals)
        if accurate_original==64 and wrong==0 and abstentions==0:
            classification=("MODEL_PROPOSED_FORMULA_VALIDATED" if run["idea_has_linear_family_keyword_proxy"]
                            else "FORMULA_VALID_BUT_ORIGIN_UNVERIFIED")
        elif wrong>0:
            classification="FORMULA_REFUTED"
        else:
            classification="ABSTAIN_PARSE_OR_SCOPE"
        arms.append({
            "prompt_id":run["prompt_id"],
            "first_idea_linear_family_keyword_proxy":run["idea_has_linear_family_keyword_proxy"],
            "expression":run["expression"],
            "classification":classification,
            "correct_original":accurate_original,
            "wrong_original":wrong_original,
            "correct_metamorphic":pos-accurate_original,
            "wrong_metamorphic":wrong-wrong_original,
            "abstentions_all_256":abstentions,
            "first_counterexample":first_wrong,
            "parse_error":run["parse_error"],
            "tokens_idea":run["tokens_idea"],
            "tokens_formal":run["tokens_formal"],
            "idea_duration_s":run["idea_duration_s"],
            "formal_duration_s":run["formal_duration_s"],
            "independent_semantic_labeler":False,
        })
    return {
        "experiment":"OMEGA_GEN24_POSTHOC_ORACLE_AND_STRONG_BASELINE",
        "status":"SCORED_REAL_MODEL_PROPOSALS",
        "predictions_sha256_before_gold":predictions["stable_decisions_sha256_before_gold"],
        "fixture_blob":CASES_BLOB,
        "gold_blob":GOLD_BLOB,
        "source_scope":"FINITE_GF2_BITMASK_TOGGLE_REACHABILITY_ONLY",
        "first_idea_prompts_hide_solution_recipe":True,
        "second_prompt_contains_rank_primitive":True,
        "benchmark_is_new_to_pilot_not_new_to_pretraining":True,
        "case_count":64,"positive_cases":32,"negative_cases":32,
        "metamorphic_cases":192,
        "A_direct_bfs_exact":direct_count,
        "D_strong_gaussian_exact":strong_count,
        "bfs_visited_states_total":bfs_visited,
        "D_gauss_pivot_steps_total":gauss_ops,
        "model_arm_results":arms,
        "no_better_than_strong_baseline_if_D_perfect":strong_count==64,
        "runtime_budget_equalized":False,
        "new_scientific_theorem":False,
        "independent_semantic_attribution_review":False,
        "open_ended_creativity_demonstrated":False,
        "automatic_certifications":0,
        "model_weight_updates":0,
        "paid_api_calls":0,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",required=True,choices=("predict","audit"))
    ap.add_argument("--proposal",type=Path)
    ap.add_argument("--predictions",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    opt=ap.parse_args()
    try:
        if opt.mode=="predict":
            if opt.proposal is None:
                raise ValueError("MISSING_UNSCORED_MODEL_RESPONSE")
            result=predict(json.loads(opt.proposal.read_text(encoding="utf-8")))
        else:
            if opt.predictions is None:
                raise ValueError("MISSING_FROZEN_PREDICTION_REPORT")
            result=audit(json.loads(opt.predictions.read_text(encoding="utf-8")))
    except Exception:
        result={"status":"FAILED_INTEGRITY_OR_ENGINE",
                "error":traceback.format_exc(),
                "automatic_certifications":0}
    opt.output.parent.mkdir(parents=True,exist_ok=True)
    opt.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GEN24",opt.mode,result["status"],flush=True)
    if opt.mode=="audit" and result["status"]=="SCORED_REAL_MODEL_PROPOSALS":
        print("BASELINES",result["A_direct_bfs_exact"],result["D_strong_gaussian_exact"],
              "64 cases",flush=True)
        for a in result["model_arm_results"]:
            print("MODEL",a["prompt_id"],a["classification"],
                  "correct",a["correct_original"],"wrong",a["wrong_original"],
                  "abstain",a["abstentions_all_256"],flush=True)
    if result["status"] not in ("FROZEN_CANDIDATE_DECISIONS","SCORED_REAL_MODEL_PROPOSALS"):
        raise SystemExit(1)

if __name__=="__main__":
    main()
