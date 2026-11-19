#!/usr/bin/env python3
"""Independent strict validation of base vs genuinely trained LoRA model.

Read-only: never updates weights, never uses holdout to tune prompts or
hyperparameters. Strong references evaluate the same fixed finite cases.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
import sys
import time
import traceback

from data_guard import (
    MODEL,MODEL_REV,SYSTEM,XOR,PAREN,ABSTAIN,
    validate_holdout,validate_finite_oracles,validate_train,strong_gf2,direct_paren,
)
class UnsafeFormula(ValueError):
    pass


def rank_gf2(vectors):
    if type(vectors)!=list or len(vectors)>10 or any(
        type(x)!=int or not 0<=x<1024 for x in vectors
    ):
        raise UnsafeFormula("BAD_RANK_ARGUMENT")
    basis=[0]*10
    for val in vectors:
        v=val
        for k in range(9,-1,-1):
            if (v>>k)&1:
                if basis[k]:
                    v^=basis[k]
                else:
                    basis[k]=v
                    break
    return sum(int(x!=0) for x in basis)


def balance(s):
    if type(s)!=str or len(s)>40 or any(c not in "()" for c in s):
        raise UnsafeFormula("BAD_PAREN_WORD")
    cur=0; lower=0
    for c in s:
        cur+=1 if c=="(" else -1
        lower=min(lower,cur)
    return cur,lower


def parse_formula(raw):
    if not isinstance(raw,str) or len(raw)>240 or "\n" in raw.strip() or "#" in raw:
        raise UnsafeFormula("INVALID_LINE")
    line=raw.strip()
    if line=="ABSTAIN":
        return None
    if not line.startswith("EXPR: "):
        raise UnsafeFormula("INVALID_PREFIX")
    expression=line[6:]
    try: tree=ast.parse(expression,mode="eval")
    except (ValueError,SyntaxError):raise UnsafeFormula("PARSE_ERROR") from None
    allowed=(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.UnaryOp,
             ast.Not,ast.Compare,ast.Eq,ast.NotEq,ast.Gt,ast.GtE,ast.Lt,
             ast.LtE,ast.Call,ast.Name,ast.Load,ast.List,ast.BinOp,
             ast.BitXor,ast.Add,ast.Constant)
    nodes=list(ast.walk(tree))
    if len(nodes)>48 or any(not isinstance(x,allowed) for x in nodes):
        raise UnsafeFormula("FORBIDDEN_AST")
    for n in nodes:
        if isinstance(n,ast.Name) and n.id not in (
            "moves","start","target","s","rank","sum_balance","min_prefix_balance"
        ): raise UnsafeFormula("FORBIDDEN_NAME")
        if isinstance(n,ast.Constant) and (type(n.value)!=int or not 0<=n.value<=1023):
            raise UnsafeFormula("FORBIDDEN_LITERAL")
        if isinstance(n,ast.Call) and (
            not isinstance(n.func,ast.Name) or
            n.func.id not in ("rank","sum_balance","min_prefix_balance") or
            len(n.args)!=1 or n.keywords
        ):raise UnsafeFormula("FORBIDDEN_CALL")
        if isinstance(n,ast.Compare) and len(n.ops)!=1:
            raise UnsafeFormula("CHAINED_COMPARE")
    return tree


def evaluate_formula(tree,c):
    env=c.copy()
    steps=[0]
    def visit(n):
        steps[0]+=1
        if steps[0]>100:raise UnsafeFormula("COMPLEXITY_LIMIT")
        if isinstance(n,ast.Expression):return visit(n.body)
        if isinstance(n,ast.Constant):return n.value
        if isinstance(n,ast.Name):
            if n.id not in env:raise UnsafeFormula("NAME_UNDEFINED")
            return env[n.id]
        if isinstance(n,ast.List):
            if len(n.elts)>8:raise UnsafeFormula("LONG_LIST")
            return [visit(x) for x in n.elts]
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.BitXor) and type(a)==type(b)==int:return a^b
            if isinstance(n.op,ast.Add) and type(a)==type(b)==list and len(a)+len(b)<=10:return a+b
            raise UnsafeFormula("BAD_BINOP")
        if isinstance(n,ast.Call):
            arg=visit(n.args[0]); fn=n.func.id
            if fn=="rank":return rank_gf2(arg)
            if type(arg)!=str:raise UnsafeFormula("BAD_STRING_ARG")
            if fn=="sum_balance":return balance(arg)[0]
            if fn=="min_prefix_balance":return balance(arg)[1]
        if isinstance(n,ast.Compare):
            a,b=visit(n.left),visit(n.comparators[0])
            if type(a)!=type(b) or type(a)!=int:raise UnsafeFormula("BAD_COMPARISON")
            op=n.ops[0]
            if isinstance(op,ast.Eq):return a==b
            if isinstance(op,ast.NotEq):return a!=b
            if isinstance(op,ast.Gt):return a>b
            if isinstance(op,ast.GtE):return a>=b
            if isinstance(op,ast.Lt):return a<b
            if isinstance(op,ast.LtE):return a<=b
        if isinstance(n,ast.BoolOp):
            vals=[visit(x) for x in n.values]
            if any(type(x)!=bool for x in vals):raise UnsafeFormula("BAD_BOOLEAN_OPERAND")
            return all(vals) if isinstance(n.op,ast.And) else any(vals)
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.Not):
            v=visit(n.operand)
            if type(v)!=bool:raise UnsafeFormula("BAD_NOT_OPERAND")
            return not v
        raise UnsafeFormula("NODE_NOT_IMPLEMENTED")
    result=visit(tree)
    if type(result)!=bool:raise UnsafeFormula("EXPRESSION_NOT_BOOL")
    return result


def score_reply(reply,domain,finite):
    try: tree=parse_formula(reply)
    except UnsafeFormula as e:
        return {"status":"INVALID_FORMAL_OUTPUT","reason":str(e),"semantic_verified":False,
                "silent_false_claim":False}
    if tree is None:
        return {"status":"ABSTAIN","reason":None,"semantic_verified":False,
                "silent_false_claim":False}
    if domain not in ("xor_reachability","parenthesis_balance"):
        return {"status":"UNSUPPORTED_DOMAIN_FORMULA","reason":"OOD_FORMULA",
                "semantic_verified":False,"silent_false_claim":True}
    try:
        if domain=="xor_reachability":
            cases=finite["xor"]
            verdicts=[evaluate_formula(tree,{"moves":c["moves"],"start":c["start"],
                                             "target":c["target"]}) for c in cases]
            truth=[strong_gf2(c) for c in cases]
        else:
            cases=finite["parentheses"]
            verdicts=[evaluate_formula(tree,{"s":c["s"]}) for c in cases]
            truth=[direct_paren(c["s"]) for c in cases]
    except UnsafeFormula as e:
        return {"status":"FORMULA_EVALUATION_REJECTED","reason":str(e),
                "semantic_verified":False,"silent_false_claim":False}
    correct=sum(a==b for a,b in zip(verdicts,truth))
    return {
        "status":"VERIFIED_ON_FINITE_CASES" if correct==len(cases) else "FALSE_ON_FINITE_CASES",
        "finite_cases":len(cases),"finite_correct":correct,
        "first_counterexample":next(({"case_id":c["id"],"claimed":v,"actual":gold}
                                     for c,v,gold in zip(cases,verdicts,truth) if v!=gold),None),
        "reason":None,"semantic_verified":correct==len(cases),
        "silent_false_claim":correct!=len(cases),
    }


def sha_file(path:Path)->str:
    h=hashlib.sha256();h.update(path.read_bytes());return h.hexdigest()


def evaluate(adapter_dir:Path,train_manifest:dict):
    import torch
    import transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2)
    prompts,labels=validate_holdout()
    finite=validate_finite_oracles()
    if train_manifest["status"]!="TRAINED_ACTUAL_LORA_PARAMETERS_CHANGED":
        raise ValueError("NO_UPDATED_WEIGHTS")
    if not train_manifest["weight_delta_L2"]>0 or train_manifest["steps"]!=24:
        raise ValueError("TRAINING_PARAMETER_OR_DELTA_CHANGED")
    for filename,digest in train_manifest["adapter_file_sha256"].items():
        if sha_file(adapter_dir/filename)!=digest:
            raise ValueError("ADAPTER_ARTIFACT_MODIFIED")
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REV,
                                            trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    model.config.use_cache=True
    model.eval()

    def predict_all(which,model):
        result=[]
        for prompt,gold in zip(prompts,labels):
            conversation=[{"role":"system","content":SYSTEM},
                          {"role":"user","content":prompt["prompt"]}]
            text=tokenizer.apply_chat_template(conversation,tokenize=False,
                                                add_generation_prompt=True)
            ids=tokenizer(text,return_tensors="pt")["input_ids"]
            tic=time.monotonic()
            with torch.no_grad():
                output=model.generate(ids,max_new_tokens=45,do_sample=False,
                                      pad_token_id=tokenizer.eos_token_id,
                                      eos_token_id=tokenizer.eos_token_id)
            took=round(time.monotonic()-tic,3)
            raw=tokenizer.decode(output[0,ids.shape[1]:],skip_special_tokens=True)
            check=score_reply(raw,gold["domain"],finite)
            item={
                "prompt_id":prompt["id"],"domain":gold["domain"],
                "raw_output":raw,"target_is_public_classical_formula":True,
                "strict_gold":gold["target"],
                "exact_target_hit":raw.strip()==gold["target"],
                "semantic_check":check,
                "tokens_generated":int(output.shape[1]-ids.shape[1]),
                "generation_wall_seconds":took
            }
            result.append(item)
            print(which,prompt["id"],repr(raw[:150]),
                  check["status"],"exact",item["exact_target_hit"],flush=True)
        return result

    base=predict_all("BASE",model)
    adapted=PeftModel.from_pretrained(model,str(adapter_dir))
    adapted.eval()
    post=predict_all("ADAPTED",adapted)
    def summary(rows):
        return {
            "exact_target_hits":sum(x["exact_target_hit"] for x in rows),
            "semantic_verified":sum(x["semantic_check"]["semantic_verified"] for x in rows),
            "false_claims":sum(x["semantic_check"]["silent_false_claim"] for x in rows),
            "abstentions":sum(x["semantic_check"]["status"]=="ABSTAIN" for x in rows),
            "invalid_outputs":sum(x["semantic_check"]["status"]=="INVALID_FORMAL_OUTPUT" for x in rows),
            "domain_summary":{domain:{
                "cases":sum(x["domain"]==domain for x in rows),
                "exact":sum(x["domain"]==domain and x["exact_target_hit"] for x in rows),
                "semantic_verified":sum(x["domain"]==domain and x["semantic_check"]["semantic_verified"] for x in rows)
            } for domain in ("xor_reachability","parenthesis_balance",
                             "unsupported","transfer_unseen")},
            "generated_tokens_total":sum(x["tokens_generated"] for x in rows),
            "generation_seconds_total":round(sum(x["generation_wall_seconds"] for x in rows),3),
        }
    before=summary(base);after=summary(post)
    # Semantic credit for unsupported-domain correct abstention.
    def verified_score(rows):
        return sum(x["semantic_check"]["semantic_verified"] or (
            x["domain"] in ("unsupported","transfer_unseen")
            and x["semantic_check"]["status"]=="ABSTAIN") for x in rows)
    pre_score=verified_score(base);post_score=verified_score(post)
    improved=(post_score>pre_score and after["false_claims"]<=before["false_claims"])
    return {
        "experiment":"OMEGA_TRAIN25_CPU_LORA_BEFORE_AFTER",
        "status":"TRAINED_AND_EVALUATED" if improved else "TRAINED_NO_EVIDENCE_OF_GAIN",
        "model":MODEL,"revision":MODEL_REV,
        "real_weight_updates":True,
        "adapter_delta_L2":train_manifest["weight_delta_L2"],
        "training_examples":96,"training_steps":24,
        "holdout_new_prompts":24,
        "before":before,"after":after,
        "reference_verified_score_before":pre_score,
        "reference_verified_score_after":post_score,
        "model_improved_on_holdout":improved,
        "strong_baseline_exact_cases":24,
        "finite_oracle_cases":24,
        "source_formula_templates_previously_given":True,
        "creative_novel_ideas_discovered":False,
        "general_math_transfer_demonstrated":False,
        "qwen3b_weights_modified":False,
        "evaluation_selection_or_prompt_tuning_posthoc":False,
        "auto_certifications":0,
        "paid_api_calls":0,
        "details":{"base":base,"adapted":post},
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--training-output",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    arg=ap.parse_args()
    try:
        manifest=json.loads((arg.training_output/"train_manifest.json").read_text())
        result=evaluate(arg.training_output/"adapter",manifest)
    except Exception:
        result={"status":"INDETERMINATE_EVAL_INFRA",
                "error":traceback.format_exc(),
                "auto_certifications":0}
    arg.output.parent.mkdir(parents=True,exist_ok=True)
    arg.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("TRAIN25_EVALUATION",result["status"],
          "pre",result.get("reference_verified_score_before"),
          "post",result.get("reference_verified_score_after"),flush=True)
    if result["status"] not in ("TRAINED_AND_EVALUATED","TRAINED_NO_EVIDENCE_OF_GAIN"):
        raise SystemExit(1)


if __name__=="__main__":
    main()
