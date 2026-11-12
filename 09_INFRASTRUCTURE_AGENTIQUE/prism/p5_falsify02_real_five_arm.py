"""P5-FALSIFY-02: 5-arm real-model INTEGRATION smoke, not a valid proof of advantage.

A: bare model; B: same model + COMPLETE exact finite-state classical verifier;
C: P1 + exact survivor tool, NO P2; D: P1 + actual P2 RCE retrieval,
NO survivor tool; E: P1 + P2 + survivor tool.

The new runtime is EXPERIMENTAL. P3 remains a supervised recorder and is not
misrepresented as the executor. Synthesized 3-state tasks are NOT a fresh
independent 160-task multi-domain holdout. B is a perfect classical solver.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from itertools import product
import json
import os

from planner import plan_mission
from context import prepare_contexts

PROTOCOL="P5-FALSIFY-02"
STATUS="REAL_FIVE_ARM_LLM_INTEGRATION_SMOKE_SYNTHETIC_EXACT_TASKS"
MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
MODEL_REVISION="7ae557604adf67be50417f59c2c2f167def9a775"
ARMS=("direct","classical_exact","omega_no_memory",
      "omega_no_observability","omega_full_candidate")
WORLD_SIZE=3
LEN_WORD=3
CAL=8
TEST=32
TOKEN_CAP=512
GHOST={"t":(0,2,2),"pi":(0,0,1),"word":(0,0,1)}

def _hash(obj):
    return sha256(json.dumps(obj,sort_keys=True,
            separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def is_realizable(row):
    """Independent enumerative oracle, no RCE and no DP call."""
    t,pi,w=row["t"],row["pi"],row["word"]
    for state in range(3):
        x=state
        seq=[]
        for k in range(len(w)):
            seq.append(pi[x])
            x=t[x]
        if tuple(seq)==tuple(w):
            return True
    return False

def survivor_certificate(row):
    """An autonomous filtering tool; outputs explicitly reveal exact answer."""
    t,pi,w=row["t"],row["pi"],row["word"]
    belief={x for x in range(3) if pi[x]==w[0]}
    sizes=[len(belief)]
    for a in w[1:]:
        belief={t[x] for x in belief if pi[t[x]]==a}
        sizes.append(len(belief))
    return {"prefix_survivor_counts":sizes,
            "final_survivors":sorted(belief),
            "is_possible":bool(belief),
            "description":"Exact calculation of all jointly compatible microstates",
            "source":"deterministic_p5_falsify02_survivor_filter",
            "semantic_scope":"only the 3-state autonomous finite map in this task"}

def _full_universe():
    rows=[]
    for t in product(range(3),repeat=3):
        for pi in product(range(2),repeat=3):
            if len(set(pi))<2:continue
            for word in product(range(2),repeat=3):
                row={"t":t,"pi":pi,"word":word}
                row["answer"]="A" if is_realizable(row) else "B"
                row["id"]="FALSIFY02-"+_hash({
                    k:list(row[k]) for k in ("t","pi","word")})[:18]
                assert survivor_certificate(row)["is_possible"]==(
                        row["answer"]=="A")
                rows.append(row)
    return rows

def dataset():
    """Stratified technical smoke, NOT a blind scientific holdout."""
    rows=_full_universe()
    ghost=next(r for r in rows if all(tuple(r[k])==v for k,v in GHOST.items()))
    assert ghost["answer"]=="B"
    groupA=sorted((r for r in rows if r["answer"]=="A"),
            key=lambda r:(_hash(["FALSIFY02-ORDER",r["id"]]),r["id"]))
    groupB=sorted((r for r in rows if r["answer"]=="B" and r["id"]!=ghost["id"]),
            key=lambda r:(_hash(["FALSIFY02-ORDER",r["id"]]),r["id"]))
    calibration=groupA[:4]+[ghost]+groupB[:3]
    evaluation=groupA[4:20]+groupB[3:19]
    assert len(calibration)==CAL and len(evaluation)==TEST
    assert len(set(r["id"] for r in calibration+evaluation))==CAL+TEST
    assert Counter(r["answer"] for r in calibration)=={"A":4,"B":4}
    assert Counter(r["answer"] for r in evaluation)=={"A":16,"B":16}
    for r in calibration:r["split"]="calibration"
    for r in evaluation:r["split"]="evaluation"
    return calibration,evaluation

def _question(row):
    return (
        "Sur X={0,1,2}, T est la fonction totale définie par "
        f"[T(0),T(1),T(2)]={list(row['t'])}; "
        f"pi est l'observation binaire [pi(0),pi(1),pi(2)]={list(row['pi'])}. "
        f"Existe-t-il un état initial x tel que la trajectoire observée "
        f"(pi(x),pi(T(x)),pi(T(T(x)))) soit {list(row['word'])} ?"
    )

def _plan(row):
    return plan_mission({
        "mission_id":row["id"],
        "question":"Distinguer observation locale et trajectoire globale. "+_question(row),
        "mission_type":"mathematical",
        "requires_computation":True,
        "decision_context":{
            "blocking_uncertainty":"Existence d'une trajectoire microscopique complète et cohérente",
            "verification":"Calculer la suite de survivants des microétats compatibles",
            "verification_effect":"Un ensemble final vide réfute la réalisabilité du mot",
        },
    })

def _memory(root,plan):
    """Actually use P2 RCE, return a capped generic source-backed excerpt."""
    started=perf_counter()
    bundle=prepare_contexts(root,plan,max_documents=1)
    elapsed=perf_counter()-started
    entries=[]
    for pkg in bundle["packages"]:
        for record in pkg["search_context"].get("candidate_documents",[])[:1]:
            excerpts=record.get("excerpts") or []
            # No artificially invented doc, never include an 'expected answer'.
            excerpt=" ".join(str(x) for x in excerpts)[:240]
            if excerpt:
                entries.append({"path":record["path"],
                                "excerpt":excerpt,"role":pkg["role"]})
    # Bounded to 380 source characters; this is a *real* RCE retrieval, not
    # a compiled domain-specific memory, and no truth of the current task.
    snippet="; ".join((x["path"]+": "+x["excerpt"]) for x in entries)[:380]
    return {
        "snippet":snippet,"returned_documents":len(entries),
        "search_calls":bundle["manifest"]["search_calls"],
        "exact_get_calls":bundle["manifest"]["exact_retrieval_calls"],
        "source_path_count":len({e["path"] for e in entries}),
        "rce_mode":bundle["mode"],
        "latency_seconds":elapsed,
        "rce_context_hash":bundle["manifest"]["content_hash"],
    }

def public_request(row,arm,repo_root):
    """No gold labels are read. For C/E, exact tool output is PAID evidence."""
    if arm not in ARMS:
        raise ValueError("invalid arm")
    question=_question(row)
    plan=None
    memory=None
    evidence=None
    plan_seconds=0.
    if arm not in ("direct","classical_exact"):
        start=perf_counter()
        plan=_plan(row)
        plan_seconds=perf_counter()-start
    if arm in ("omega_no_observability","omega_full_candidate"):
        memory=_memory(repo_root,plan)
    if arm in ("omega_no_memory","omega_full_candidate"):
        start=perf_counter()
        evidence=survivor_certificate(row)
        evidence["calculation_seconds"]=perf_counter()-start
    lines=[
        "A=OUI (au moins une trajectoire complète existe); B=NON (aucune trajectoire complète).",
        question,
    ]
    if plan is not None:
        lines.append("Instruction P1 de méthode : vérifier la compatibilité des témoins sur toute la trajectoire.")
    if memory is not None:
        lines.append("Mémoire RCE documentaire non certifiée : "+(
            memory["snippet"] or "[recherche réalisée, aucun extrait retrouvé]"
        ))
    if evidence is not None:
        lines.append("Sortie d'un VERIFICATEUR EXACT (calcul d'ensemble de survivants) : "
                     +json.dumps({"prefix_survivor_counts":evidence["prefix_survivor_counts"],
                                  "is_possible":evidence["is_possible"]},
                                 ensure_ascii=False,sort_keys=True))
        lines.append("Un résultat is_possible vrai correspond à A; faux correspond à B.")
    messages=[
        {"role":"system","content":"Tu dois répondre à la question mathématique par une seule lettre A ou B, sans prose."},
        {"role":"user","content":"\n".join(lines)+"\nRéponse finale A ou B : "},
    ]
    # B's exact classical computation is performed AFTER its real model call
    # using a separate algorithm; its raw model prompt is identical to A.
    if arm=="classical_exact":
        assert messages==public_request_without_tools(row)
    prompt=json.dumps(messages,ensure_ascii=False,sort_keys=True)
    if "\"answer\"" in prompt or "\"gold\"" in prompt:
        raise AssertionError("hidden answer field leaked into model request")
    return {
        "messages":messages,"prompt_sha256":sha256(prompt.encode()).hexdigest(),
        "planner_version":plan and plan["planner_version"],
        "planner_task_count":len(plan["tasks"]) if plan else 0,
        "plan_seconds":plan_seconds,
        "memory":memory,
        "observation_tool":evidence,
        "actual_rce_searches":memory["search_calls"] if memory else 0,
        "actual_observability_calls":1 if evidence else 0,
    }

def public_request_without_tools(row):
    return [
        {"role":"system","content":"Tu dois répondre à la question mathématique par une seule lettre A ou B, sans prose."},
        {"role":"user","content":"\n".join([
            "A=OUI (au moins une trajectoire complète existe); B=NON (aucune trajectoire complète).",
            _question(row),
        ])+"\nRéponse finale A ou B : "},
    ]

def validate_requests_for_case(row,requests):
    if set(requests)!=set(ARMS):
        raise ValueError("must have all five arms")
    for arm,req in requests.items():
        if len(req["prompt_sha256"])!=64:
            raise ValueError("invalid request commitment")
        if arm=="omega_no_memory" and req["memory"] is not None:
            raise ValueError("no-memory arm read memory")
        if arm=="omega_no_observability" and req["observation_tool"] is not None:
            raise ValueError("no-observability arm used survivor tool")
        if arm=="omega_full_candidate" and (
            req["memory"] is None or req["observation_tool"] is None):
            raise ValueError("full arm did not activate both mechanisms")
    if requests["direct"]["messages"]!=requests["classical_exact"]["messages"]:
        raise ValueError("A/B differ before classical exact verification")
    if (requests["direct"]["prompt_sha256"]==
        requests["omega_full_candidate"]["prompt_sha256"]):
        raise ValueError("cosmetic ablation: full prompt did not change")
    return True

def _label_token_ids(tokenizer):
    groups={}
    for lab in ("A","B"):
        ids=[]
        for variant in (lab," "+lab):
            tokens=tokenizer.encode(variant,add_special_tokens=False)
            if len(tokens)==1 and tokens[0] not in ids:
                ids.append(tokens[0])
        if not ids:
            raise ValueError("no single token available for "+lab)
        groups[lab]=ids
    if set(groups["A"]) & set(groups["B"]):
        raise ValueError("overlapping token sets")
    return groups

class QwenRealCPU:
    def __init__(self):
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        self.torch=torch
        torch.set_num_threads(2)
        self.tokenizer=AutoTokenizer.from_pretrained(
            MODEL_ID,revision=MODEL_REVISION)
        self.model=AutoModelForCausalLM.from_pretrained(
            MODEL_ID,revision=MODEL_REVISION,torch_dtype=torch.float32).eval()
        self.token_ids=_label_token_ids(self.tokenizer)
    def infer(self,messages):
        rendered=self.tokenizer.apply_chat_template(
            messages,tokenize=False,add_generation_prompt=True)
        batch=self.tokenizer([rendered],return_tensors="pt")
        tokens=batch["input_ids"].shape[1]
        if tokens>TOKEN_CAP:
            raise ValueError(f"model input tokens {tokens} exceed {TOKEN_CAP}")
        started=perf_counter()
        with self.torch.inference_mode():
            logits=self.model(**batch).logits[0,-1,:]
        elapsed=perf_counter()-started
        scores={
          k:float(self.torch.logsumexp(logits[v],dim=0).item())
          for k,v in self.token_ids.items()
        }
        return {
            "model_predicted":"A" if scores["A"]>=scores["B"] else "B",
            "input_tokens":int(tokens),"output_tokens":1,
            "inference_seconds":round(elapsed,5),
            "logit_a":round(scores["A"],6),
            "logit_b":round(scores["B"],6),
            "model_calls":1,
        }

def invoke_case(arm,row,repo_root,engine):
    visible=public_request(row,arm,repo_root)
    result=engine.infer(visible["messages"])
    if result["model_calls"]!=1:
        raise AssertionError("actual inference count must equal one")
    chosen=result["model_predicted"]
    tool_time=0.
    if arm=="classical_exact":
        started=perf_counter()
        chosen="A" if is_realizable(row) else "B"
        tool_time=perf_counter()-started
    else:
        tool_time=(visible["observation_tool"] or {}).get("calculation_seconds",0)
    # Truth looked up ONLY after a decision; the classical B oracle is
    # a paid tool which may equal truth by construction on this simple domain.
    grade=is_realizable(row)
    return {
        "arm":arm,"task_id":row["id"],"split":row["split"],
        "model_answer":result["model_predicted"],
        "final_answer":chosen,
        "evaluator_only_reference":"A" if grade else "B",
        "correct":chosen==("A" if grade else "B"),
        "model_id":MODEL_ID,"model_revision":MODEL_REVISION,
        "model_calls":result["model_calls"],
        "input_tokens":result["input_tokens"],
        "output_tokens":result["output_tokens"],
        "inference_seconds":result["inference_seconds"],
        "model_logits":{"A":result["logit_a"],"B":result["logit_b"]},
        "planning_seconds":round(visible["plan_seconds"],6),
        "retrieval_seconds":round((visible["memory"] or {}).get("latency_seconds",0),6),
        "exact_tool_seconds":round(tool_time,6),
        "rce_search_calls":visible["actual_rce_searches"],
        "rce_document_hits":(visible["memory"] or {}).get("returned_documents",0),
        "rce_manifest_sha":(visible["memory"] or {}).get("rce_context_hash"),
        "filter_calls":visible["actual_observability_calls"]+int(arm=="classical_exact"),
        "survivor_counts":(visible["observation_tool"] or {}).get("prefix_survivor_counts"),
        "supplied_exact_tool_output":visible["observation_tool"] is not None,
        "prompt_sha256":visible["prompt_sha256"],
        "prompt_contains_RCE_context":visible["memory"] is not None,
        "old_omega_P3_model_calls":0,
        "actual_new_experimental_runner":True,
    }

def preflight(root):
    cal,test=dataset()
    # Only a small no-model subset is expanded in preflight: full P2 scan
    # of 40 cases is deferred to the real execution.
    ghost=next(r for r in cal if all(tuple(r[k])==v for k,v in GHOST.items()))
    r={
        arm:public_request(ghost,arm,root) for arm in ARMS
    }
    validate_requests_for_case(ghost,r)
    return {
        "status":"P5_FALSIFY02_PREFLIGHT_NO_MODEL_CALLS",
        "calibration":len(cal),"evaluation":len(test),
        "five_arms":list(ARMS),
        "expected_real_cpu_forwards":(len(cal)+len(test))*len(ARMS),
        "model":MODEL_ID,"revision":MODEL_REVISION,
        "token_cap":TOKEN_CAP,
        "gold_oracle_agreement_40":True,
        "ghost_certified":survivor_certificate(ghost),
        "sample_ids_digest":_hash([x["id"] for x in cal+test]),
        "same_A_B_prompt":r["direct"]["messages"]==r["classical_exact"]["messages"],
        "actual_P2_RCE_hits_for_ghost":r["omega_full_candidate"]["memory"]["returned_documents"],
        "actual_P2_search_calls_for_ghost":r["omega_full_candidate"]["actual_rce_searches"],
        "P1_plan_used":r["omega_full_candidate"]["planner_version"] is not None,
        "P3_is_not_model_runner":True,
        "is_blinded_independent_benchmark":False,
    }

def run(root):
    cal,test=dataset()
    engine=QwenRealCPU()
    outputs=[]
    for row in cal+test:
        # One inference per arm, randomized arm order by case hash to reduce
        # systematic per-arm warming effects. Deterministic schedule.
        order=sorted(ARMS,key=lambda k:_hash([row["id"],k]))
        for arm in order:
            result=invoke_case(arm,row,root,engine)
            outputs.append(result)
            print("FALSIFY02_FORWARDED",row["id"],arm,result["final_answer"],
                  result["correct"],flush=True)
    scores={}
    for arm in ARMS:
        rows=[r for r in outputs if r["arm"]==arm]
        scores[arm]={
            "actual_forward_passes":len(rows),
            "evaluation_cases":TEST,
            "evaluation_correct":sum(r["correct"] for r in rows
                                     if r["split"]=="evaluation"),
            "calibration_correct":sum(r["correct"] for r in rows
                                      if r["split"]=="calibration"),
            "total_input_tokens":sum(r["input_tokens"] for r in rows),
            "total_output_tokens":sum(r["output_tokens"] for r in rows),
            "total_inference_seconds":round(sum(r["inference_seconds"] for r in rows),3),
            "total_memory_searches":sum(r["rce_search_calls"] for r in rows),
            "total_memory_document_hits":sum(r["rce_document_hits"] for r in rows),
            "total_exact_tool_calls":sum(r["filter_calls"] for r in rows),
        }
    by={(r["task_id"],r["arm"]):r for r in outputs}
    diffs={}
    for arm in ("omega_no_memory","omega_no_observability"):
        diffs[arm+"_vs_full"]=sum(
            by[(row["id"],arm)]["final_answer"]!=
            by[(row["id"],"omega_full_candidate")]["final_answer"]
            for row in test)
    # Restrict causal attribution: memory retrieval itself may not have
    # changed the answer, and B already has an exact classical tool.
    assert all(v["actual_forward_passes"]==40 for v in scores.values())
    assert scores["classical_exact"]["evaluation_correct"]==32
    assert scores["omega_no_memory"]["total_memory_searches"]==0
    assert scores["omega_no_observability"]["total_exact_tool_calls"]==0
    assert scores["omega_full_candidate"]["total_memory_searches"]>0
    assert scores["omega_full_candidate"]["total_exact_tool_calls"]==40
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "sample_digest":_hash([x["id"] for x in cal+test]),
        "calibration_cases":CAL,"evaluation_cases":TEST,
        "actual_model_forwards":sum(v["actual_forward_passes"] for v in scores.values()),
        "max_input_tokens_per_call":TOKEN_CAP,
        "same_model_version_for_all":True,
        "real_model_execution_performed_by_new_experimental_runner":True,
        "P3_real_model_execution":False,
        "classical_exact_tool_available_and_perfect_in_this_finite_world":True,
        "memory_context_is_actual_P2_RCE_but_not_validated_scientific_proof":True,
        "realized_resource_parity":False,
        "ablation_decision_differences":diffs,
        "ablation_did_not_change_decision":{
            k:v==0 for k,v in diffs.items()},
        "per_arm":scores,"raw":outputs,
        "limitations":[
            "Synthetic 3-state task generator; NOT independent diverse scientific test",
            "Actual one-forward open-weight Qwen model per case/arm",
            "Classical B has the complete exact solution oracle and thus 100% possible correctness",
            "C and E receive oracle-like survivor tool output, not independently learned reasoning",
            "P2 memory is local lexical retrieval; neither P1 nor P3 learns from outcomes",
            "P3 is only a supervised recorder and is not the experimental model runner",
            "Equal number of model forwards, max 512 tokens, actual token/latency totals differ",
            "Prompts change between arms; a decision difference is not uniquely memory's causal effect",
            "No statistical or multi-domain claim about Omega advantage",
            "Pre-registered final 160-case five-arm experiment remains NOT READY",
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",required=True,type=Path)
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=preflight(args.repo_root) if args.preflight else run(args.repo_root)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,sort_keys=True,
                     indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if not args.preflight:
        print("FALSIFY02_REAL_SMOKE_SUMMARY",json.dumps({
            "status":result["status"],
            "forward_passes":result["actual_model_forwards"],
            "per_arm":result["per_arm"],
            "ablation_decision_differences":result["ablation_decision_differences"],
            "realized_resource_parity":result["realized_resource_parity"],
        },ensure_ascii=False,sort_keys=True))
    else:
        print("FALSIFY02_PREFLIGHT",json.dumps(result,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
