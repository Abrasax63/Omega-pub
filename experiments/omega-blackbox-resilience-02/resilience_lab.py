"""OMEGA-BLACKBOX-RESILIENCE-02: separate fail-closed test campaign.

No new learning policy and no scoring parameter changes. Uses real AALpy L*
through the unmodified PR136 blackbox_lab module (apart from any explicitly
audited bugfix). All three stress systems are fully accessible and pairwise
behaviorally distinguishable from their initial states.
"""
from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
from pathlib import Path
from fractions import Fraction
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-blackbox-01"))
import blackbox_lab as b
from mealy_lab import Mealy,digest

EXPERIMENT="OMEGA-BLACKBOX-RESILIENCE-02"
PREREG="d2f191c1340fae2b8be19a2acdaf02008a013547"
STRESS_SIZES=(4,5,6)
CAPS=(120,400,900)
ARM_SEED_OFFSETS={
    "RANDOM_LSTAR":0,
    "FIXED_LSTAR":100,
    "OMEGA_GUIDED_LSTAR":200,
}


def cycle_marker_machine(n):
    """Input 0 follows n-cycle; exactly one state emits 1 on input 0.

    Access from state 0 via 0**i is guaranteed. Distinguishability: any
    different two cycle phases emit a marker at different offsets over a
    length-n sequence of input 0s. Input 1 is a second n-cycle step.
    """
    if n not in STRESS_SIZES:
        raise ValueError("ONLY_PREREGISTERED_SIZES")
    t=tuple(((i+1)%n,(i+2)%n) for i in range(n))
    o=tuple((1 if i==0 else 0,0) for i in range(n))
    return Mealy(t,o)


def accessible_truth_states(machine):
    seen={0}
    stack=[0]
    while stack:
        state=stack.pop()
        for action in b.ALPHABET:
            target=machine.transitions[state][action]
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


def hidden_trace_from(machine,initial,word):
    """Test-only independent word simulator, NOT passed to a learner."""
    state=initial
    outputs=[]
    for action in word:
        outputs.append(machine.outputs[state][action])
        state=machine.transitions[state][action]
    return tuple(outputs)


def all_states_distinguishable(machine):
    for a in range(machine.size):
        for other in range(a+1,machine.size):
            if hidden_trace_from(machine,a,(0,)*machine.size)==hidden_trace_from(
                machine,other,(0,)*machine.size):
                return False
    return True


def assert_ledger_matches_truth(machine,ledger):
    """Independent audit of ALL complete and incomplete physical queries."""
    records=ledger["query_log"]
    if sum(row["charge"] for row in records)!=ledger["spent_symbols"]:
        raise AssertionError("MISACCOUNTED_ACTUAL_SUL_STEPS")
    for row in records:
        input_word=tuple(row["inputs"])
        actual=hidden_trace_from(machine,0,input_word)
        if tuple(row["outputs"])!=actual:
            raise AssertionError("QUERY_LOG_HAS_FAKE_OR_INCORRECT_OUTPUT")
        if row["charge"]!=len(input_word):
            raise AssertionError("INPUTS_NOT_BILLED")
        if row["phase"] not in ("MQ","EQ"):
            raise AssertionError("MISSING_QUERY_ORIGIN")
    if sum(ledger["by_phase_spent"].values())!=ledger["spent_symbols"]:
        raise AssertionError("QUERY_PHASES_NOT_RECONCILED")
    if ledger["spent_symbols"]>ledger["budget_cap"]:
        raise AssertionError("SYMBOL_BUDGET_OVERSPENT")
    return len(records)


def run_stress():
    rows=[]
    for n in STRESS_SIZES:
        world=cycle_marker_machine(n)
        if len(accessible_truth_states(world))!=n:
            raise AssertionError("STRESS_WORLD_NOT_FULLY_ACCESSIBLE")
        if not all_states_distinguishable(world):
            raise AssertionError("STRESS_WORLD_NOT_BEHAVIORALLY_MINIMAL")
        groups={}
        for arm in b.ARMS:
            seed=775000+n+ARM_SEED_OFFSETS[arm]
            entries={}
            for cap in CAPS:
                model,queried,training=b.train_one(world,arm,cap,seed)
                exact=b.exact_equivalence(world,model)
                ledger=training["ledger"]
                observed_queries=assert_ledger_matches_truth(world,ledger)
                if exact["status"]=="EXACT_EQUIVALENT":
                    # One deterministic held-out score as additional check.
                    words=b.reserved_words(n,0)
                    check=b.heldout_score(world,model,words,queried)
                    if check["whole_word_accuracy"]!=1.0:
                        raise AssertionError("BFS_SAYS_EQ_BUT_HELDOUT_SAYS_NOT")
                if exact["status"]=="NOT_EQUIVALENT":
                    word=tuple(exact["counterexample"])
                    if not word or hidden_trace_from(world,0,word)==b.predict_mealy(model,word):
                        raise AssertionError("INVALID_INDEPENDENT_COUNTEREXAMPLE")
                if exact["status"]=="NO_HYPOTHESIS" and model is not None:
                    raise AssertionError("HIDDEN_HYPOTHESIS_ON_NO_HYPOTHESIS")
                entries[str(cap)]={
                    "status":training["status"],
                    "hypothesis_state_count":training["model_states"],
                    "exact_bfs":exact,
                    "spent_symbols":ledger["spent_symbols"],
                    "membership_symbols":ledger["by_phase_spent"]["MQ"],
                    "equivalence_symbols":ledger["by_phase_spent"]["EQ"],
                    "approx_eq_words":training["equivalence_words_tested"],
                    "counterexamples_seen":training["counterexamples_seen"],
                    "queries_logged":observed_queries,
                    "queries_completed":ledger["completed_queries"],
                    "incomplete_queries":ledger["incomplete_queries"],
                    "query_log_sha256":ledger["queries_sha256"],
                    "sample_log":ledger["query_log"][:5],
                }
            groups[arm]=entries
        rows.append({
            "machine_size":n,
            "canonical_signature":world.signature(),
            "reachable_states":len(accessible_truth_states(world)),
            "distinguishable_physical_states":all_states_distinguishable(world),
            "arms":groups,
        })
    totals={}
    for cap in CAPS:
        totals[str(cap)]={
            arm:{
                "exact_equivalent":sum(
                    x["arms"][arm][str(cap)]["exact_bfs"]["status"]==
                    "EXACT_EQUIVALENT" for x in rows),
                "budget_interrupted":sum(
                    x["arms"][arm][str(cap)]["status"].startswith("BUDGET_INTERRUPTED")
                    for x in rows),
                "without_model":sum(
                    x["arms"][arm][str(cap)]["hypothesis_state_count"] is None
                    for x in rows),
                "spent_symbols":sum(
                    x["arms"][arm][str(cap)]["spent_symbols"]
                    for x in rows),
            } for arm in b.ARMS
        }
    result={
        "experiment":EXPERIMENT,
        "preregistered_commit":PREREG,
        "technical_status":"RESILIENCE_TEST_EXECUTED",
        "scientific_gain_certified":False,
        "modes":list(b.ARMS),
        "external_aalpy_version":b.version("aalpy"),
        "caps":list(CAPS),
        "same_random_seed_per_arm_across_caps":True,
        "test_worlds_all_accessible_and_distinguishable":True,
        "oracle_evaluation_only":True,
        "any_budget_interruption_accepted_as_normal_verification":False,
        "no_paid_api":True,
        "main_modified":False,
        "report":rows,
        "totals":totals,
        "limitations":[
            "Three deterministic fully reachable and distinguishable stress cases, not a representative population.",
            "An approximate EQ acceptance is not an exact certificate.",
            "No speed or query-information superiority is established by this technical stress test.",
            "Low budget may yield no hypothesis; that is legitimate if reported.",
            "The true model is available to the test evaluator, never supplied to AALpy learners.",
        ],
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=run_stress()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,
        "technical_status":report["technical_status"],
        "totals":report["totals"],
        "report_sha256":sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
