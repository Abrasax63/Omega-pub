#!/usr/bin/env python3
"""TRAIN26 exact-safe gate and heldout before/after LoRA measurement.

The LLM never executes Python code. All candidate formulas are untrusted AST
data interpreted in a bounded language, then tested on independently computed
finite examples. The 48-item evaluation set is not imported by train_full.py.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

from data_guard import (MODEL,MODEL_REV,SYSTEM,FORMULAS,
    load_holdout,load_oracles,direct_xor,stack_parens,direct_trace,
    codes,gaussian_xor)
from train_full import sha256_file

MAX_EXPR=320
MAX_AST_NODES=64


class UnsafeView(ValueError):
    pass


def rank_gf2(vectors):
    if type(vectors)!=list or len(vectors)>12 or any(
        type(x)!=int or not 0<=x<=1023 for x in vectors
    ):
        raise UnsafeView("RANK_INVALID_BOUNDED_VECTORS")
    pivots=[0]*10
    for x in vectors:
        val=x
        while val:
            k=val.bit_length()-1
            if pivots[k]:
                val^=pivots[k]
            else:
                pivots[k]=val
                break
    return sum(v!=0 for v in pivots)


def bracket_stats(s):
    if type(s)!=str or len(s)>40 or any(c not in "()" for c in s):
        raise UnsafeView("UNSUPPORTED_BRACKET_ALPHABET")
    running=low=0
    for c in s:
        running+=1 if c=="(" else -1
        low=min(low,running)
    return running,low


def parse_expression(s):
    if type(s)!=str or not s.strip() or len(s)>MAX_EXPR:
        raise UnsafeView("EMPTY_OR_OVERSIZED_EXPRESSION")
    if any(c in s for c in ("#", ";", "\n", "\r", "\x00")):
        raise UnsafeView("COMMENTS_OR_EXTRA_LINES_FORBIDDEN")
    try:
        tree=ast.parse(s,mode="eval")
    except (SyntaxError,TypeError,ValueError):
        raise UnsafeView("NOT_VALID_EXPRESSION") from None
    nodes=list(ast.walk(tree))
    allowed=(ast.Expression,ast.Name,ast.Load,ast.Constant,ast.List,
             ast.BinOp,ast.BitXor,ast.Add,ast.Compare,ast.Eq,ast.NotEq,
             ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.Call,ast.BoolOp,ast.And,
             ast.Or,ast.UnaryOp,ast.Not)
    if len(nodes)>MAX_AST_NODES or any(not isinstance(x,allowed) for x in nodes):
        raise UnsafeView("DISALLOWED_AST")
    vars_and_fns={
        "moves","start","target","s","T","pi","h","x","y",
        "rank","popcount","len","sum_balance","min_prefix_balance",
        "partition_code",
    }
    fn_names={"rank","popcount","len","sum_balance",
              "min_prefix_balance","partition_code"}
    for node in nodes:
        if isinstance(node,ast.Name) and node.id not in vars_and_fns:
            raise UnsafeView("UNKNOWN_VARIABLE_OR_FUNCTION")
        if isinstance(node,ast.Constant) and (
            type(node.value)!=int or not 0<=node.value<=1023
        ):
            raise UnsafeView("INVALID_NUMERIC_CONSTANT")
        if isinstance(node,ast.Call):
            if (not isinstance(node.func,ast.Name) or
                node.func.id not in fn_names or node.keywords or
                len(node.args)!=(5 if node.func.id=="partition_code" else 1)):
                raise UnsafeView("DISALLOWED_FUNCTION_CALL")
        if isinstance(node,ast.List) and len(node.elts)>10:
            raise UnsafeView("OVERLONG_LITERAL_LIST")
        if isinstance(node,ast.Compare) and len(node.ops)!=1:
            raise UnsafeView("CHAINED_COMPARISON_NOT_PERMITTED")
    return tree


def eval_expression(tree,vars):
    operations=[0]
    def visit(node,depth=0):
        operations[0]+=1
        if operations[0]>100 or depth>16:
            raise UnsafeView("EXPRESSION_EXCEEDS_BOUNDED_BUDGET")
        if isinstance(node,ast.Expression):
            return visit(node.body,depth+1)
        if isinstance(node,ast.Name):
            if node.id not in vars:
                raise UnsafeView("UNKNOWN_INPUT")
            return vars[node.id]
        if isinstance(node,ast.Constant):
            return node.value
        if isinstance(node,ast.List):
            return [visit(x,depth+1) for x in node.elts]
        if isinstance(node,ast.BinOp):
            a,b=visit(node.left,depth+1),visit(node.right,depth+1)
            if isinstance(node.op,ast.BitXor) and type(a)==type(b)==int:
                return a^b
            if isinstance(node.op,ast.Add) and type(a)==type(b)==list and len(a)+len(b)<=12:
                return a+b
            raise UnsafeView("INVALID_BINARY_OPERATION")
        if isinstance(node,ast.Call):
            vals=[visit(a,depth+1) for a in node.args]
            name=node.func.id
            if name=="rank":
                return rank_gf2(vals[0])
            if name=="popcount" and type(vals[0])==int and 0<=vals[0]<=1023:
                return vals[0].bit_count()
            if name=="len" and type(vals[0])==list and len(vals[0])<=12:
                return len(vals[0])
            if name=="sum_balance":
                return bracket_stats(vals[0])[0]
            if name=="min_prefix_balance":
                return bracket_stats(vals[0])[1]
            if name=="partition_code":
                T,pi,h,state=vals[0],vals[1],vals[2],vals[3]
                # Syntax was reserved for partition_code(T,pi,h,x), i.e. 4 arguments.
                if type(T)!=list or type(pi)!=list or type(h)!=int or type(state)!=int:
                    raise UnsafeView("INVALID_PARTITION_TYPES")
                c=codes(T,pi,h)
                if state<0 or state>=len(c):
                    raise UnsafeView("PARTITION_STATE_OUT_OF_RANGE")
                return c[state]
            raise UnsafeView("INVALID_CALL_ARGUMENT")
        if isinstance(node,ast.Compare):
            a,b=visit(node.left,depth+1),visit(node.comparators[0],depth+1)
            if type(a)!=int or type(b)!=int:
                raise UnsafeView("COMPARISON_REQUIRES_INTS")
            op=node.ops[0]
            if isinstance(op,ast.Eq):return a==b
            if isinstance(op,ast.NotEq):return a!=b
            if isinstance(op,ast.Gt):return a>b
            if isinstance(op,ast.GtE):return a>=b
            if isinstance(op,ast.Lt):return a<b
            if isinstance(op,ast.LtE):return a<=b
        if isinstance(node,ast.BoolOp):
            vals=[visit(x,depth+1) for x in node.values]
            if any(type(x)!=bool for x in vals):
                raise UnsafeView("BOOLEAN_CONTEXT_REQUIRES_BOOLEANS")
            return all(vals) if isinstance(node.op,ast.And) else any(vals)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Not):
            v=visit(node.operand,depth+1)
            if type(v)!=bool:
                raise UnsafeView("NOT_REQUIRES_BOOLEAN")
            return not v
        raise UnsafeView("UNINTERPRETABLE_AST")
    result=visit(tree)
    if type(result)!=bool:
        raise UnsafeView("VIEW_MUST_RETURN_BOOLEAN")
    return result


def checked_formula(expression,domain,oracles):
    try:
        tree=parse_expression(expression)
        suite=oracles[domain]
        errors=[]
        for case in suite:
            if domain=="xor":
                vars={"moves":case["moves"],"start":case["start"],
                      "target":case["target"]}
                expected=direct_xor(case)
            elif domain=="paren":
                vars={"s":case["s"]}
                expected=stack_parens(case["s"])
            elif domain=="obs":
                vars={k:case[k] for k in ("T","pi","h","x","y")}
                expected=direct_trace(case)
            else:
                raise UnsafeView("UNSUPPORTED_DOMAIN")
            observed=eval_expression(tree,vars)
            if observed!=expected:
                errors.append({"id":case["id"],"wanted":expected,
                               "observed":observed,"full_instance":case})
        return {
            "verifier_status":"EMPIRICALLY_MATCHES_ALL_FINITE_CASES"
                              if not errors else "FALSIFIED_BY_FINITE_COUNTEREXAMPLE",
            "finite_checked":len(suite),
            "mismatches":len(errors),
            "first_counterexample":errors[0] if errors else None,
            "passed":not errors,
            "formal_proof_produced":False,
        }
    except (UnsafeView,ValueError,IndexError,TypeError) as exc:
        return {
            "verifier_status":"REJECTED_UNSUPPORTED_AST",
            "reason":str(exc),"passed":False,
            "mismatches":None,"first_counterexample":None,
            "formal_proof_produced":False,
        }


def check_critic_labels(prompts,gold,oracles):
    checked={}
    for p,g in zip(prompts,gold):
        if p["task"]!="CRITIQUE":
            continue
        if "candidate" not in p:
            raise ValueError("MISSING_HOLDOUT_CRITIQUE_CANDIDATE")
        evidence=checked_formula(p["candidate"],p["domain"],oracles)
        if evidence["verifier_status"]=="REJECTED_UNSUPPORTED_AST":
            raise ValueError("CRITIC_INPUT_OUTSIDE_EXACT_GRAMMAR")
        expected="ACCEPT" if evidence["passed"] else "REJECT"
        if expected!=g["target"]:
            raise AssertionError("PREDEFINED_CRITIQUE_GOLD_CONTRADICTS_EXACT_ORACLE")
        checked[p["id"]]=evidence
    if len(checked)!=12:
        raise AssertionError("CRITIC_ORACLE_NOT_COMPLETE")
    return checked


def strict_model_line(reply):
    if type(reply)!=str or not reply.strip():
        return {"status":"MISSING_OUTPUT"}
    txt=reply.strip()
    if "\n" in txt or "\r" in txt or len(txt)>360:
        return {"status":"NONCANONICAL_MULTILINE_OR_OVERSIZED"}
    if txt in ("ACCEPT","REJECT","ABSTAIN"):
        return {"status":"CONTROL","control":txt}
    if txt.startswith("EXPR: "):
        return {"status":"EXPRESSION","expr":txt[6:]}
    return {"status":"NONCANONICAL_OUTPUT"}


def judge_reply(reply,p,g,oracles,critic_evidence):
    parsed=strict_model_line(reply)
    result={
        "prompt_id":p["id"],"task":p["task"],"domain":p["domain"],
        "gold_target":g["target"],"raw_reply":reply,
        "strict_exact_target":reply.strip()==g["target"],
        "correct_task":False,
        "false_mathematical_assertion":False,
        "gate_accepted_false_claim":False,
        "formalization_verified":False,
        "critic_answer_correct":False,
        "justified_abstention":False,
        "parse_status":parsed["status"],
        "evidence":None,
    }
    if p["task"] in ("FORMALIZE","REPAIR"):
        if parsed["status"]=="EXPRESSION":
            check=checked_formula(parsed["expr"],p["domain"],oracles)
            result["evidence"]=check
            result["formalization_verified"]=check["passed"]
            result["correct_task"]=check["passed"]
            result["false_mathematical_assertion"]=(
                check["verifier_status"]=="FALSIFIED_BY_FINITE_COUNTEREXAMPLE")
    elif p["task"]=="CRITIQUE":
        evidence=critic_evidence[p["id"]]
        result["evidence"]={"candidate_test":evidence}
        if parsed["status"]=="CONTROL":
            ans=parsed["control"]
            result["critic_answer_correct"]=ans==g["target"] and ans in ("ACCEPT","REJECT")
            result["correct_task"]=result["critic_answer_correct"]
            result["false_mathematical_assertion"]=(ans=="ACCEPT" and g["target"]=="REJECT")
    else:
        result["justified_abstention"]=(
            parsed["status"]=="CONTROL" and parsed["control"]=="ABSTAIN")
        result["correct_task"]=result["justified_abstention"]
        result["false_mathematical_assertion"]=not result["justified_abstention"]
    # All evidence is checked and the harness never auto-promotes scientific facts.
    return result


def sha256_outputs(rows):
    b=json.dumps([{"id":x["prompt_id"],"raw":x["raw_reply"]}
                  for x in rows],ensure_ascii=False,sort_keys=True).encode()
    return hashlib.sha256(b).hexdigest()


def summarize(rows):
    by_task={}
    for task in ("FORMALIZE","REPAIR","CRITIQUE","ABSTAIN"):
        subgroup=[x for x in rows if x["task"]==task]
        by_task[task]={
            "n":len(subgroup),
            "correct":sum(x["correct_task"] for x in subgroup),
            "exact_targets":sum(x["strict_exact_target"] for x in subgroup),
        }
    return {
        "total_cases":len(rows),
        "semantic_task_score":sum(x["correct_task"] for x in rows),
        "strict_gold_exact":sum(x["strict_exact_target"] for x in rows),
        "formalization_verified":sum(x["formalization_verified"] for x in rows),
        "correct_critic_verdicts":sum(x["critic_answer_correct"] for x in rows),
        "justified_abstentions":sum(x["justified_abstention"] for x in rows),
        "false_mathematical_assertions":sum(x["false_mathematical_assertion"] for x in rows),
        "false_assertions_auto_accepted":sum(x["gate_accepted_false_claim"] for x in rows),
        "invalid_format":sum(x["parse_status"] in
            ("MISSING_OUTPUT","NONCANONICAL_MULTILINE_OR_OVERSIZED",
             "NONCANONICAL_OUTPUT") for x in rows),
        "task_breakdown":by_task,
        "raw_output_sha256":sha256_outputs(rows),
    }


def evaluate(trained:Path)->dict:
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import PeftModel

    torch.set_num_threads(2)
    trained_manifest=json.loads((trained/"train_manifest.json").read_text(encoding="utf-8"))
    if trained_manifest.get("status")!="TRAINED_ACTUAL_WEIGHTS_CHANGED":
        raise ValueError("TRAIN_MANIFEST_NO_COMPLETED_WEIGHT_CHANGES")
    if trained_manifest.get("steps")!=640 or trained_manifest.get("examples_seen_exactly_twice")!=320:
        raise ValueError("INCOMPLETE_TRAINING_CORPUS")
    for file,digest in trained_manifest["saved_adapter_sha256"].items():
        if sha256_file(trained/"adapter"/file)!=digest:
            raise ValueError("TRAINED_ADAPTER_ARTIFACT_CHANGED")

    prompts,gold=load_holdout()
    oracles=load_oracles()
    critics=check_critic_labels(prompts,gold,oracles)

    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REV,
                                            trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    base=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=MODEL_REV,torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    base.config.use_cache=True
    base.eval()

    def apply(model,arm):
        rows=[]
        total_tokens=0
        elapsed=0.0
        for p,g in zip(prompts,gold):
            prefix=tokenizer.apply_chat_template(
                [{"role":"system","content":SYSTEM},
                 {"role":"user","content":p["prompt"]}],
                tokenize=False,add_generation_prompt=True)
            encoded=tokenizer(prefix,return_tensors="pt")["input_ids"]
            start=time.monotonic()
            with torch.no_grad():
                output=model.generate(
                    encoded,max_new_tokens=96,do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            elapsed_one=time.monotonic()-start
            tokens=int(output.shape[1]-encoded.shape[1])
            raw=tokenizer.decode(output[0,encoded.shape[1]:],
                                 skip_special_tokens=True)
            row=judge_reply(raw,p,g,oracles,critics)
            row["new_tokens"]=tokens
            row["generation_seconds"]=round(elapsed_one,3)
            rows.append(row)
            total_tokens+=tokens
            elapsed+=elapsed_one
            print("TRAIN26_EVAL",arm,p["id"],"correct",row["correct_task"],
                  "false",row["false_mathematical_assertion"],
                  "raw",repr(raw[:130]),flush=True)
        stats=summarize(rows)
        stats["generated_tokens"]=total_tokens
        stats["total_generation_seconds"]=round(elapsed,3)
        return rows,stats

    baseline,base_metrics=apply(base,"BASE")
    adapter=PeftModel.from_pretrained(base,str(trained/"adapter"))
    adapter.eval()
    adapted,new_metrics=apply(adapter,"TRAINED")
    improvement=(
        new_metrics["semantic_task_score"]>base_metrics["semantic_task_score"]
        and new_metrics["false_mathematical_assertions"]<=base_metrics["false_mathematical_assertions"]
    )
    status=("TRAINED_GAIN_ON_RESTRICTED_HOLDOUT" if improvement
            else "TRAINED_NO_EVIDENCE_OF_GAIN")
    return {
        "experiment":"OMEGA_TRAIN26_CORRECTION_AWARE_ADAPTER_COMPARISON",
        "status":status,
        "trained_adapter_loaded":True,
        "model":MODEL,
        "base_revision":MODEL_REV,
        "training_steps":trained_manifest["steps"],
        "unique_training_examples":trained_manifest["unique_examples_seen"],
        "adapter_L2_change":trained_manifest["adapter_delta_L2"],
        "holdout_cases":len(prompts),
        "holdout_prompt_types":["FORMALIZE","REPAIR","CRITIQUE","ABSTAIN"],
        "strong_exact_reference_consistency":True,
        "strong_baseline_cases":48,
        "finite_math_instances":sum(len(oracles[x]) for x in ("xor","paren","obs")),
        "training_holdout_not_external_or_blind_to_public_repo":True,
        "before":base_metrics,
        "after":new_metrics,
        "measured_gain_without_more_false_assertions":improvement,
        "base_rows":baseline,
        "adapted_rows":adapted,
        "new_scientific_discoveries":0,
        "new_representations_not_in_training":0,
        "spontaneous_general_creativity_demonstrated":False,
        "qwen3b_unchanged":True,
        "training_feedback_influenced_model_retries":False,
        "auto_certifications":0,
        "paid_api_calls":0,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--training-artifact",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        result=evaluate(args.training_artifact)
    except Exception:
        result={
            "status":"INDETERMINATE_EVAL_TECHNICAL_FAILURE",
            "error":traceback.format_exc(),
            "auto_certifications":0,
        }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print("TRAIN26_HOLDOUT",result["status"],
          "pre",result.get("before",{}).get("semantic_task_score"),
          "post",result.get("after",{}).get("semantic_task_score"),flush=True)
    if result["status"] not in ("TRAINED_GAIN_ON_RESTRICTED_HOLDOUT",
                                "TRAINED_NO_EVIDENCE_OF_GAIN"):
        raise SystemExit(1)


if __name__=="__main__":
    main()
