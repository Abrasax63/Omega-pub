"""P5 FALSIFY-01 — evidence-based READINESS GATE for a five-arm falsification.

Does NOT run an LLM benchmark, does NOT treat role perspectives as agents and
does NOT claim P1 executes actions, P2 validates memory, or P3 invokes a model.

The goal is to prohibit a false 5-arm comparison from being reported when the
real code only supplies a static plan, read-only context and a recording shell.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from planner import plan_mission
from context import prepare_contexts
from execution import start_execution, close_execution
from p5_obs01_active_sensing import survivors,STATES as OBS_STATES
from p5_obs01_active_sensing import phantom_counterexample

PROTOCOL="P5-FALSIFY-01"
STATUS="PRE_REGISTERED_5_ARM_EXECUTION_NOT_READY"
ARMS=("direct","classical_strong","omega_no_memory",
      "omega_no_observability","omega_full")
MAIN_PREREG="EXPERIMENT_P5_FALSIFY01_FIVE_ARM_PREREG_2026-11-12.md"
REVIEW_OPEN="REVIEW_P5_EVID06_SQL_SEMANTICS_OPEN_2026-11-12.md"

def _digest(value):
    return sha256(json.dumps(value,sort_keys=True,
            ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def _recorded_decision(trace):
    """Extract a strictly verifiable action/answer, not presentation metadata."""
    if not isinstance(trace,dict):
        raise ValueError("invalid trace")
    mandatory={
        "arm","task_id","model_calls","model_sha","actual_action",
        "final_answer","memory_reads","observability_filter_calls",
        "provenance_evidence","execution_kind","tokens_total","tool_calls",
    }
    if set(trace)!=mandatory:
        raise ValueError("missing execution audit fields or injected gold")
    if trace["arm"] not in ARMS or not trace["task_id"]:
        raise ValueError("unknown arm or task")
    if trace["execution_kind"]!="REAL_TOOL_AND_MODEL_CALLS":
        raise ValueError("synthetic/planning-only trace cannot establish an ablation")
    if type(trace["model_calls"]) is not int or trace["model_calls"]<1:
        raise ValueError("must record an actual model call")
    if not isinstance(trace["model_sha"],str) or len(trace["model_sha"])<16:
        raise ValueError("model not versioned")
    for key in ("memory_reads","observability_filter_calls","tokens_total",
                "tool_calls"):
        if type(trace[key]) is not int or trace[key]<0:
            raise ValueError("invalid measured resource count")
    if not isinstance(trace["provenance_evidence"],list):
        raise ValueError("invalid evidence ledger")
    if not isinstance(trace["actual_action"],str) or not trace["actual_action"]:
        raise ValueError("missing selected action")
    if trace["final_answer"] not in (
          "ENTAILED","CONTRADICTED","NOT ENOUGH INFO","ABSTAIN"):
        raise ValueError("invalid decision")
    if trace["arm"]=="omega_no_memory" and trace["memory_reads"]!=0:
        raise ValueError("no-memory arm actually read memory")
    if trace["arm"]=="omega_no_observability" and trace["observability_filter_calls"]!=0:
        raise ValueError("no-observability arm actually filtered evidence")
    if trace["arm"]=="omega_full" and (trace["memory_reads"]==0 or
        trace["observability_filter_calls"]==0):
        raise ValueError("full arm did not use both mechanisms")
    return {
        "task_id":trace["task_id"],"actual_action":trace["actual_action"],
        "final_answer":trace["final_answer"],
    }

def ablation_pair_certification(left,right,mechanism):
    """Cannot pass from cosmetic flags, logging or labels alone."""
    if mechanism not in ("memory","observability"):
        raise ValueError("unsupported ablation")
    l=_recorded_decision(left)
    r=_recorded_decision(right)
    if l["task_id"]!=r["task_id"] or left["model_sha"]!=right["model_sha"]:
        raise ValueError("different task or model")
    expected=("omega_no_memory" if mechanism=="memory"
              else "omega_no_observability")
    if (left["arm"],right["arm"])!=(expected,"omega_full"):
        raise ValueError("incorrect causal ablation pairing")
    if mechanism=="memory":
        changed=left["memory_reads"]==0 and right["memory_reads"]>0
    else:
        changed=(left["observability_filter_calls"]==0
                 and right["observability_filter_calls"]>0)
    if not changed:
        return {"status":"FAIL_MECHANISM_NOT_INTERVENED"}
    if (l["actual_action"],l["final_answer"])==(
         r["actual_action"],r["final_answer"]):
        return {"status":"NON_IDENTIFIABLE_SAME_ACTION_AND_DECISION"}
    return {"status":"PASS_CAUSAL_MECHANISM_ACTIVATION_AND_ACTION_DIVERGENCE",
            "note":"This is necessary, not evidence that the full arm is more correct."}

def _evidence_path(root,name):
    return root/"09_INFRASTRUCTURE_AGENTIQUE"/name

def audit(root):
    root=Path(root).resolve()
    if not _evidence_path(root,MAIN_PREREG).is_file():
        raise ValueError("preregistered protocol missing from checkout")
    source=_evidence_path(root,MAIN_PREREG).read_bytes()
    # Use the ACTUAL existing P1, P2 and P3, not stubs.
    plan=plan_mission({
        "mission_id":"P5-FALSIFY01-AUDIT",
        "question":"Sélectionner une vérification et tester si mémoire et "
                   "observabilité modifient une décision sur un nouveau problème.",
        "mission_type":"exploratory",
        "requires_computation":True,
        "decision_context":{
            "blocking_uncertainty":"La validité globale des preuves et des hypothèses est inconnue",
            "verification":"Consulter une source versionnée et tester sa cohérence",
            "verification_effect":"Une preuve peut réfuter l'hypothèse courante",
        },
    })
    if plan["planner"]!="omega-adaptive-prism":
        raise AssertionError("not the actual P1 planner")
    try:
        ctx=prepare_contexts(root,plan,max_documents=2)
        ctx_error=None
    except Exception as ex:
        ctx=None
        ctx_error=f"{type(ex).__name__}: {str(ex)[:250]}"
    recording=None
    if ctx is not None:
        record=start_execution(plan,ctx)
        recording=close_execution(record)
    phantom=phantom_counterexample()
    if (not phantom["locally_possible"] or phantom["realizable"] or
        phantom["prefix_survivor_counts"]!=[2,1,0]):
        raise AssertionError("known observability adversary no longer holds")
    conditional=survivors(frozenset(OBS_STATES),"U",1)
    if len(conditional)!=8:
        raise AssertionError("survivor state filter not functioning")
    # Structural checks: positive evidence a mechanism exists is distinct
    # from proof it was used for a decision or is causally responsible for it.
    plan_kind=plan["execution_model"]
    context_kind=ctx["execution_model"] if ctx else None
    execution_kind=recording["execution_policy"] if recording else None
    gates={
        "GATE_A_ACTUAL_EQUAL_MODEL_RUNS":{
            "pass":False,
            "evidence":"P1 planning_only; P3 recorder, no shared five-arm model run",
        },
        "GATE_B_STRONG_CLASSICAL_COMPARATOR":{
            "pass":False,
            "evidence":"Existing VOI/DP controls exist, but no matched new-cohort five-arm execution",
        },
        "GATE_MEMORY_CAUSAL_ABLATION":{
            "pass":False,
            "evidence":"P2 retrieves RCE contexts read-only; neither P1 nor P3 uses a memory retrieval to change a tested answer",
        },
        "GATE_OBSERVABILITY_CAUSAL_ABLATION":{
            "pass":False,
            "evidence":"An exact survivor filter exists on finite synthetic problems; not wired to actual P1/P2/P3 model decisions",
        },
        "GATE_RESOURCE_PARITY":{
            "pass":False,
            "evidence":"No actual five-arm tokens, time, tool calls and model versions measured on identical tasks",
        },
        "GATE_NEW_BLINDED_TASKS":{
            "pass":False,
            "evidence":"Existing ClaimDB, BIRD, and PR29 examples previously analyzed; fresh audited 160-case holdout not created",
        },
        "GATE_INDEPENDENT_SEMANTIC_REVIEW":{
            "pass":False,
            "evidence":"An OPEN independent SQL-to-English reviewer checklist exists, no completed third-party verdict",
        },
    }
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "pre_registration_sha256":sha256(source).hexdigest(),
        "actual_paths_tested":[
            "prism/planner.py plan_mission",
            "prism/context.py prepare_contexts",
            "prism/execution.py start_execution/close_execution"
                  if recording else "prism/execution.py blocked: upstream context unavailable",
            "prism/p5_obs01_active_sensing.py survivors + phantom",
        ],
        "actual_P1_version":plan["planner_version"],
        "actual_P1_execution_model":plan_kind,
        "actual_P1_next_action":plan["next_action"],
        "actual_P2_context_preparer":ctx and ctx["context_preparer"],
        "actual_P2_error":ctx_error,
        "actual_P2_manifest":ctx and ctx["manifest"],
        "actual_P2_execution_model":context_kind,
        "actual_P3_execution_policy":execution_kind,
        "actual_P3_coverage":recording and recording["coverage"],
        "actual_P3_scientific_verdict":recording and recording["scientific_verdict"],
        "observability_phantom_test":phantom,
        "observability_survivor_filter_positive_test":{
            "possible_states_before":16,"possible_states_after_U_equals_1":8,
        },
        "required_arms":list(ARMS),
        "arms_have_genuine_5_way_results":False,
        "gates":gates,
        "readiness":("READY" if all(x["pass"] for x in gates.values())
                     else "NOT_READY"),
        "model_inference_now":0,
        "new_genuine_evaluation_tasks_scored":0,
        "honest_next_steps":[
            "Implement one real model/tool execution interface reused by all arms",
            "Wire P2 memory retrievals into decisions and enforce no-memory via denied gateway access",
            "Wire survivor/provenance filter into decisions and enforce no-observability via actual bypass",
            "Demonstrate ablation action differences on calibration examples without optimizing scores",
            "Commit new held-out statements and external semantic audits before seeing outputs",
            "Meter actual per-arm tokens/time/action counts; select classical competitor on calibration",
            "Execute 160 paired new tasks only after all preflight gates are GREEN",
        ],
        "restrictions":[
            "No invented sub-agent execution or scientific validation",
            "No claims of five-arm statistical results from existing historical outputs",
            "P1 is a deterministic planner; P2 lexical RCE reader; P3 a supervised recorder",
            "Existing Omega label and conventional VOI can be functionally identical",
            "This is a readiness audit, NOT a performed falsification of broad Omega intelligence",
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    r=audit(args.repo_root)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2,
                        sort_keys=True)+"\n",encoding="utf-8")
    print("P5_FALSIFY01_READINESS",json.dumps({
        "status":r["status"],"readiness":r["readiness"],
        "gates":{k:v["pass"] for k,v in r["gates"].items()},
        "p1":r["actual_P1_version"],
        "p2_retrievals":(r["actual_P2_manifest"] or {}).get("exact_retrieval_calls"),
        "p3_model_execution":(r["actual_P3_execution_policy"] or {}).get("model_calls_performed_by_module"),
        "real_new_inferences":r["model_inference_now"],
    },sort_keys=True,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
