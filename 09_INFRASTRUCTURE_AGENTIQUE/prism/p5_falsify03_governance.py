"""P5-FALSIFY-03: genuine Qwen inference + certified decision governance.

New N=4,L=4 finite-world technical cohort (distinct from FALSIFY-02).
B is a perfect conventional exact solver. C/E's dual-method certified
arbiter cannot improve exact accuracy over B; this is an INTEGRATION test,
not a demonstration of Omega's superior strategic intelligence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
from time import perf_counter
import json

from planner import plan_mission
import p5_falsify02_real_five_arm as earlier

PROTOCOL="P5-FALSIFY-03"
STATUS="REAL_MODEL_PROOF_GOVERNANCE_INTEGRATION_NOT_INDEPENDENT_BENCHMARK"
WORLD_SIZE=4
WORD_LENGTH=4
CAL=4
TEST=16
ARMS=("direct","classical_exact","omega_no_memory",
      "omega_no_observability","omega_full_governed")
CERT_KIND="OMEGA_FINITE_OBSERVABILITY_CERTIFICATE_V1"
SCOPE="T:4->4;pi:4->2;word_length:4"
VALID="CERTIFICATE_VALID_TWO_METHODS_SINGLE_DATA_PROVIDER"


def _hash(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
                       separators=(",",":")).encode("utf-8")).hexdigest()


def spec(row):
    return {"T":list(row["t"]),"pi":list(row["pi"]),
            "word":list(row["word"]),"scope":SCOPE}


def enumerate_initial(row):
    """Independent brute-force oracle; start states witnessing full word."""
    t,pi,w=row["t"],row["pi"],row["word"]
    ok=[]
    for x0 in range(WORLD_SIZE):
        x=x0
        out=[]
        for _ in range(WORD_LENGTH):
            out.append(pi[x])
            x=t[x]
        if tuple(out)==tuple(w):
            ok.append(x0)
    return ok


def filter_survivors(row):
    """Forward belief filtering, without enumerating starting trajectories."""
    t,pi,w=row["t"],row["pi"],row["word"]
    remaining={x for x in range(WORLD_SIZE) if pi[x]==w[0]}
    sizes=[len(remaining)]
    for symbol in w[1:]:
        remaining={t[x] for x in remaining if pi[t[x]]==symbol}
        sizes.append(len(remaining))
    return {"prefix_counts":sizes,"end_states":sorted(remaining),
            "is_possible":bool(remaining)}


def _last_positions(row,initials):
    t=row["t"]
    result=set()
    for start in initials:
        x=start
        for _ in range(WORD_LENGTH-1):
            x=t[x]
        result.add(x)
    return sorted(result)


def validate_case(row):
    if (len(row["t"])!=WORLD_SIZE or len(row["pi"])!=WORLD_SIZE or
        len(row["word"])!=WORD_LENGTH or
        any(x not in range(WORLD_SIZE) for x in row["t"]) or
        any(x not in (0,1) for x in row["pi"]+row["word"]) or
        len(set(row["pi"]))!=2):
        raise ValueError("invalid 4-state observation task")


def certificate(row):
    """Two genuine computations of the same supplied task: NOT two data sources."""
    validate_case(row)
    start=perf_counter()
    initials=enumerate_initial(row)
    survivor=filter_survivors(row)
    if bool(initials)!=survivor["is_possible"]:
        raise AssertionError("independent algorithms disagree")
    if _last_positions(row,initials)!=survivor["end_states"]:
        raise AssertionError("independent algorithms differ in witness endpoints")
    result={
        "kind":CERT_KIND,"scope":SCOPE,"source":"explicit_task_spec",
        "source_sha256":_hash(spec(row)),
        "algorithms":["initial_state_enumeration","forward_survivor_filter"],
        "independent_data_providers":1,
        "independent_computation_methods":2,
        "is_possible":bool(initials),
        "initial_witness_states":initials,
        "prefix_counts":survivor["prefix_counts"],
        "final_states":survivor["end_states"],
    }
    return result,perf_counter()-start


def validate_certificate(row,received):
    """Reject tampering, stale task hashes, missing scope or impossible witnesses."""
    if not isinstance(received,dict) or set(received)!={
        "kind","scope","source","source_sha256","algorithms",
        "independent_data_providers","independent_computation_methods",
        "is_possible","initial_witness_states","prefix_counts","final_states"}:
        return {"status":"INVALID_SCHEMA"}
    if (received["kind"]!=CERT_KIND or received["scope"]!=SCOPE or
        received["source"]!="explicit_task_spec" or
        received["source_sha256"]!=_hash(spec(row))):
        return {"status":"INVALID_OR_STALE_SOURCE"}
    if (received["algorithms"]!=["initial_state_enumeration",
                                  "forward_survivor_filter"] or
        received["independent_data_providers"]!=1 or
        received["independent_computation_methods"]!=2):
        return {"status":"INVALID_PROVENANCE"}
    # Independent re-execution on the LIVE task is necessary. Claiming
    # an exact result by sending a structured but unaudited string is unsafe.
    try:
        actual_initials=enumerate_initial(row)
        observed_filter=filter_survivors(row)
    except Exception:
        return {"status":"INVALID_TASK"}
    if (type(received["is_possible"]) is not bool or
        received["initial_witness_states"]!=actual_initials or
        received["prefix_counts"]!=observed_filter["prefix_counts"] or
        received["final_states"]!=observed_filter["end_states"] or
        received["is_possible"]!=bool(actual_initials) or
        received["is_possible"]!=observed_filter["is_possible"]):
        return {"status":"CONTRADICTORY_OR_INCOMPATIBLE_WITNESS"}
    return {"status":VALID,"answer":"A" if actual_initials else "B",
            "independent_data_providers":1,"methods":2}


def governed_answer(row,received):
    check=validate_certificate(row,received)
    return (check["answer"],check) if check["status"]==VALID else (
        "ABSTAIN_INVALID_CERTIFICATE",check)


def universe():
    yes=[]
    no=[]
    count=0
    for t in product(range(4),repeat=4):
        for pi in product((0,1),repeat=4):
            if len(set(pi))!=2:
                continue
            for word in product((0,1),repeat=4):
                row={"t":tuple(t),"pi":tuple(pi),"word":tuple(word)}
                initials=enumerate_initial(row)
                filt=filter_survivors(row)
                if bool(initials)!=filt["is_possible"] or (
                   _last_positions(row,initials)!=filt["end_states"]):
                    raise AssertionError("universe oracle disagreement")
                row["id"]="FALSIFY03-"+_hash(spec(row))[:20]
                row["gold_evaluator_only"]="A" if initials else "B"
                (yes if initials else no).append(row)
                count+=1
    if count!=57344:
        raise AssertionError("universe has wrong size")
    for group in (yes,no):
        group.sort(key=lambda r:(_hash(["FALSIFY03",r["id"]]),r["id"]))
    return yes,no,count


def dataset():
    yes,no,total=universe()
    cal=yes[:2]+no[:2]
    test=yes[2:10]+no[2:10]
    assert len(cal)==CAL and len(test)==TEST
    assert len({r["id"] for r in cal+test})==CAL+TEST
    assert Counter(r["gold_evaluator_only"] for r in test)=={"A":8,"B":8}
    for r in cal:r["split"]="calibration"
    for r in test:r["split"]="evaluation"
    return cal,test,total


def _question(row):
    return ("Sur X={0,1,2,3}, T est une fonction totale définie par "
            f"[T(0),T(1),T(2),T(3)]={list(row['t'])} ; "
            "pi est une observation binaire définie par "
            f"[pi(0),pi(1),pi(2),pi(3)]={list(row['pi'])}. "
            "Existe-t-il un état initial dont les quatre observations "
            f"successives soient {list(row['word'])} ?")


def _plan(row):
    return plan_mission({
        "mission_id":row["id"],
        "question":"Auditer un certificat de réalisabilité globale. "+_question(row),
        "mission_type":"mathematical","requires_computation":True,
        "decision_context":{
            "blocking_uncertainty":"La compatibilité globale du mot observé est inconnue",
            "verification":"Exécuter deux calculs exacts et valider les états témoins",
            "verification_effect":"Un état initial valide prouve A ; aucune possibilité prouve B",
        },
    })


def _messages(row,arm,source_snippet=None,cert=None):
    lines=[
        "A=OUI (il existe une trajectoire globale); B=NON (aucune).",
        _question(row),
    ]
    if arm not in ("direct","classical_exact"):
        lines.append("Consigne P1 : distinguer les suites localement possibles des trajets globaux.")
    if source_snippet is not None:
        lines.append("Contexte documentaire RCE non certifié : "+
                     (source_snippet[:380] or "[aucun extrait]"))
    if cert is not None:
        lines.append("Certificat de calcul en attente de vérification externe : "+
                     json.dumps({
                         "source_sha256":cert["source_sha256"],
                         "is_possible":cert["is_possible"],
                         "prefix_counts":cert["prefix_counts"],
                     },sort_keys=True))
        lines.append("is_possible vrai correspond à A, faux à B.")
    return [
        {"role":"system","content":"Réponds uniquement A ou B, sans prose."},
        {"role":"user","content":"\n".join(lines)+"\nRéponse finale A ou B : "},
    ]


def preflight(root):
    cal,test,count=dataset()
    row=cal[0]
    cert,_=certificate(row)
    checked=validate_certificate(row,cert)
    if checked["status"]!=VALID:
        raise AssertionError("valid certificate rejected")
    modified=dict(cert,source_sha256="0"*64)
    if governed_answer(row,modified)[0]!="ABSTAIN_INVALID_CERTIFICATE":
        raise AssertionError("tampered source not rejected")
    if _messages(row,"direct")!=_messages(row,"classical_exact"):
        raise AssertionError("direct/classical raw model input mismatch")
    plan=_plan(row)
    # Do not invoke RCE in the preflight to avoid duplicating costly retrievals.
    return {
        "status":"PREFLIGHT_NO_LLM",
        "universe_checked":count,
        "oracle_agreement_all":True,
        "calibration":CAL,"evaluation":TEST,"arms":list(ARMS),
        "expected_real_model_forwards":len(ARMS)*(CAL+TEST),
        "model_id":earlier.MODEL_ID,"model_revision":earlier.MODEL_REVISION,
        "sample_id_digest":_hash([r["id"] for r in cal+test]),
        "example_certificate":cert,
        "p1_real_planner_version":plan["planner_version"],
        "p2_memory_planned_only":True,
        "p3_model_runner_used":False,
        "tampered_certificate_refused":True,
        "real_model_calls":0,"blind_scientific_holdout":False,
    }


def run(root):
    root=Path(root).resolve()
    cal,test,total=dataset()
    engine=earlier.QwenRealCPU()
    outputs=[]
    memory_work={"physical_p2_calls":0,"physical_rce_searches":0,
                 "physical_memory_seconds":0.,
                 "shared_context_per_task":True}
    for row in cal+test:
        plan=_plan(row)
        # D/E share the SAME RCE snippet, one genuine P2 call per task;
        # cannot report this as 2 independent retrieval operations.
        memory=earlier._memory(root,plan)
        memory_work["physical_p2_calls"]+=1
        memory_work["physical_rce_searches"]+=memory["search_calls"]
        memory_work["physical_memory_seconds"]+=memory["latency_seconds"]
        for arm in sorted(ARMS,key=lambda x:_hash([row["id"],x])):
            cert=None
            cert_seconds=0.
            if arm in ("omega_no_memory","omega_full_governed"):
                cert,cert_seconds=certificate(row)
            visible_mem=(memory["snippet"] if arm in (
                "omega_no_observability","omega_full_governed") else None)
            if arm=="omega_no_memory" and visible_mem is not None:
                raise AssertionError("no-memory intervention failed")
            if arm=="omega_no_observability" and cert is not None:
                raise AssertionError("no-observability intervention failed")
            messages=_messages(row,arm,visible_mem,cert)
            if arm=="classical_exact" and messages!=_messages(row,"direct"):
                raise AssertionError("unequal model input for A/B")
            if any('gold_evaluator_only' in x["content"] for x in messages):
                raise AssertionError("gold annotation leaked")
            raw=engine.infer(messages)
            if raw["model_calls"]!=1:
                raise AssertionError("missing actual Qwen forward")
            raw_answer=raw["model_predicted"]
            check=None
            if arm=="classical_exact":
                now=perf_counter()
                decision="A" if enumerate_initial(row) else "B"
                exact_seconds=perf_counter()-now
                computation_calls=1
            elif cert is not None:
                now=perf_counter()
                decision,check=governed_answer(row,cert)
                exact_seconds=cert_seconds+perf_counter()-now
                computation_calls=4  # certificate (2) + validation replay (2)
            else:
                decision=raw_answer
                exact_seconds=0.
                computation_calls=0
            # Independent evaluator, never called by a policy.
            true_label=row["gold_evaluator_only"]
            outputs.append({
                "arm":arm,"case_id":row["id"],"split":row["split"],
                "model_prediction":raw_answer,"final_answer":decision,
                "reference_evaluator_only":true_label,
                "correct":decision==true_label,
                "input_tokens":raw["input_tokens"],"output_tokens":raw["output_tokens"],
                "inference_seconds":raw["inference_seconds"],
                "logit_margin_A_minus_B":round(raw["logit_a"]-raw["logit_b"],6),
                "model_calls":raw["model_calls"],"exact_computation_calls":computation_calls,
                "exact_seconds":round(exact_seconds,7),
                "memory_enabled":visible_mem is not None,
                "memory_shared_source_manifest":memory["rce_context_hash"] if visible_mem is not None else None,
                "memory_source_hits":memory["returned_documents"] if visible_mem is not None else 0,
                "memory_retrieval_cache_shared":visible_mem is not None,
                "certificate":cert,
                "certificate_validation":check,
                "source_independent_providers":1 if cert else 0,
                "model_id":earlier.MODEL_ID,
                "model_revision":earlier.MODEL_REVISION,
                "prompt_sha256":_hash(messages),
                "p1_version":plan["planner_version"] if arm not in ("direct","classical_exact") else None,
                "p3_model_calls":0,
            })
            print("FALSIFY03_CASE",row["id"],arm,raw_answer,decision,
                  decision==true_label,flush=True)
    score={}
    for arm in ARMS:
        part=[r for r in outputs if r["arm"]==arm]
        score[arm]={
            "model_forwards":len(part),
            "calibration_correct":sum(r["correct"] for r in part if r["split"]=="calibration"),
            "evaluation_correct":sum(r["correct"] for r in part if r["split"]=="evaluation"),
            "evaluation_abstentions":sum(r["final_answer"].startswith("ABSTAIN")
                                        for r in part if r["split"]=="evaluation"),
            "total_model_input_tokens":sum(r["input_tokens"] for r in part),
            "total_model_inference_seconds":round(sum(r["inference_seconds"] for r in part),3),
            "total_exact_computations":sum(r["exact_computation_calls"] for r in part),
            "total_exact_seconds":round(sum(r["exact_seconds"] for r in part),5),
            "used_memory_in_cases":sum(r["memory_enabled"] for r in part),
        }
    by={(r["case_id"],r["arm"]):r for r in outputs}
    delta={}
    for other in ("direct","classical_exact","omega_no_memory","omega_no_observability"):
        delta[other+"_vs_omega_full_governed"]=sum(
            by[(r["id"],other)]["final_answer"]!=
            by[(r["id"],"omega_full_governed")]["final_answer"] for r in test)
    if score["classical_exact"]["evaluation_correct"]!=TEST:
        raise AssertionError("conventional exact solver unexpectedly incorrect")
    if score["omega_no_memory"]["evaluation_correct"]!=TEST or (
        score["omega_full_governed"]["evaluation_correct"]!=TEST):
        raise AssertionError("validated certificates did not govern decisions")
    if delta["omega_no_memory_vs_omega_full_governed"]!=0:
        raise AssertionError("unexpected memory effect on exactly proven finite task")
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "model_id":earlier.MODEL_ID,"model_revision":earlier.MODEL_REVISION,
        "total_world_cases_oracles_checked":total,
        "calibration_cases":CAL,"evaluation_cases":TEST,
        "genuine_model_forwards":len(outputs),
        "p2_shared_actual_retrievals":memory_work,
        "per_arm":score,
        "ablation_decision_differences":delta,
        "omega_specific_gain_over_classical_exact":(
            score["omega_full_governed"]["evaluation_correct"]-
            score["classical_exact"]["evaluation_correct"]),
        "memory_effect_identified":delta["omega_no_memory_vs_omega_full_governed"]>0,
        "observability_effect_identified":delta["omega_no_observability_vs_omega_full_governed"]>0,
        "individual_cases":outputs,
        "restrictions":[
          "Technical finite-world N4,L4, stratified by known truth, NOT independent holdout",
          "All 100 Qwen inferences real, fixed open model and one-step A/B scoring",
          "Two exact methods on one input are NOT two independent data providers",
          "Proof governance is a deterministic post-model decision gate, NOT a learned skill",
          "Classical exact baseline already attains perfect accuracy",
          "Memory is actual P2 lexical retrieval, shared D/E per task, NOT scientific validation",
          "Resource parity of consumed tokens/time is false, only equal model calls and token cap",
          "P3 is a recorder, not the actual experimental model runner",
          "Do not claim any superior adaptive reasoning from this integration demonstration",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",required=True,type=Path)
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--output",type=Path)
    opts=p.parse_args()
    result=preflight(opts.repo_root) if opts.preflight else run(opts.repo_root)
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,
                               sort_keys=True)+"\n",encoding="utf-8")
    if opts.preflight:
        print("FALSIFY03_PREFLIGHT",json.dumps({
            "status":result["status"],"world":result["universe_checked"],
            "forwards":result["expected_real_model_forwards"],
            "sample_id_digest":result["sample_id_digest"],
        },sort_keys=True,ensure_ascii=False),flush=True)
    else:
        print("FALSIFY03_REAL_FIVE_ARM_SUMMARY",json.dumps({
            "forward_passes":result["genuine_model_forwards"],
            "per_arm":result["per_arm"],
            "ablation":result["ablation_decision_differences"],
            "omega_minus_classical":result["omega_specific_gain_over_classical_exact"],
            "memory_effect":result["memory_effect_identified"],
            "observability_effect":result["observability_effect_identified"],
        },sort_keys=True,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
