"""OMEGA-STRUCTURAL-TRANSFER-04: exact same episodes, labels and billed probes.

The current Mealy TABLE is known, only the resettable initial state is hidden.
One observed first-probe return label is learned per completed episode; the
simulator, not the policy, knows the initial state. No oracle during training.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import random
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-equal-budget-03"))
import equal_budget_lab as previous  # noqa: E402
from mealy_lab import (Mealy, random_machine, make_cohorts, digest)
from plasticity_lab import LinearPolicy, features, choices, fully_identifiable, A_COSTS
from plasticity_lab import choose as choose_reference
from plasticity_lab import MEMORY_K

EXPERIMENT="OMEGA-STRUCTURAL-TRANSFER-04"
PREREG_SHA="1da94d3afb76c27c9300ab7098695b02cc0c71aa"
N_STATES=4
COST_PER_EPISODE=6
EPSILON=0.2
SEEDS=(171,172,173)
GROUPS=(
    ("train_random",21117,64,"random_restricted"),
    ("control_random",21118,20,"random_restricted"),
    ("holdout_perm",21119,28,"permutation"),
    ("holdout_reset_cycle",21120,28,"reset_cycle"),
)


def column(machine,action):
    return tuple(machine.transitions[state][action]
                 for state in range(machine.size))


def is_permutation(values):
    return len(set(values))==len(values)


def is_reset(values):
    return len(set(values))==1


def is_cycle4(values):
    if len(values)!=4:
        return False
    visited=set()
    current=0
    for _ in range(4):
        if current in visited:
            return False
        visited.add(current)
        current=values[current]
    return current==0 and len(visited)==4


def structure_kind(machine):
    a,b=column(machine,0),column(machine,1)
    if is_permutation(a) and is_permutation(b):
        return "permutation"
    if is_reset(a) and is_cycle4(b):
        return "reset_cycle"
    if not is_reset(a) and not is_reset(b) and not (
        is_permutation(a) and is_permutation(b)
    ):
        return "random_restricted"
    return "other"


def generate_machine(rng,kind):
    """Only structure is selected; never a success/identifiability metric."""
    if kind=="random_restricted":
        while True:
            machine=random_machine(rng)
            if structure_kind(machine)=="random_restricted":
                return machine
    if kind=="permutation":
        a=rng.sample(range(N_STATES),N_STATES)
        b=rng.sample(range(N_STATES),N_STATES)
        transitions=tuple((a[s],b[s]) for s in range(N_STATES))
    elif kind=="reset_cycle":
        reset_target=rng.randrange(N_STATES)
        cycle_order=rng.sample(range(N_STATES),N_STATES)
        permutation={
            cycle_order[i]:cycle_order[(i+1)%N_STATES]
            for i in range(N_STATES)
        }
        transitions=tuple((reset_target,permutation[s])
                          for s in range(N_STATES))
    else:
        raise ValueError("INVALID_STRUCTURE_FAMILY")
    outputs=tuple(tuple(rng.randrange(3) for _ in range(2))
                  for _ in range(N_STATES))
    machine=Mealy(transitions,outputs)
    if structure_kind(machine)!=kind:
        raise AssertionError("STRUCTURAL_FAMILY_GENERATOR_BUG")
    return machine


def make_new_cohorts():
    """No re-used canonical machine from any of the four previous pilots."""
    from plasticity_lab import group_machines
    from feedback_lab import cohorts as feedback_cohorts
    old_collections=(
        make_cohorts(),group_machines(),feedback_cohorts(),
        previous.machine_groups()
    )
    used={sig for source in old_collections
          for group in source.values()
          for sig,_ in group["machines"]}
    if len(used)!=594:
        raise AssertionError(f"OLD_SPLIT_INTEGRITY: {len(used)}")
    collection={}
    for name,seed,count,kind in GROUPS:
        rng=random.Random(seed)
        items=[]
        duplicates=attempts=0
        while len(items)<count:
            attempts+=1
            if attempts>100000:
                raise RuntimeError("EXHAUSTED_UNIQUE_MACHINE_POOL")
            machine=generate_machine(rng,kind)
            signature=machine.signature()
            if structure_kind(machine)!=kind:
                raise AssertionError("STRUCTURAL_FAMILY_CONTAMINATION")
            if signature in used:
                duplicates+=1
                continue
            used.add(signature)
            items.append((signature,machine))
        collection[name]={
            "seed":seed, "family":kind,
            "requested":count, "attempts":attempts,
            "isomorphism_duplicates":duplicates,
            "machines":items,
        }
    if len(used)!=594+sum(row[2] for row in GROUPS):
        raise AssertionError("OVERLAPPING_EVALUATION_STRUCTURES")
    return collection


def action_for_training(group,checks,arm,weights,rng):
    """Does not accept, inspect or infer the hidden initial state."""
    actions=choices(group,checks)
    if not actions:
        return None
    if arm=="OFF" or rng.random()<EPSILON:
        return rng.choice(actions)
    if arm=="ON":
        return choose_reference(group,checks,"learned",
                                weights=weights)
    raise ValueError("INVALID_TRAINING_ARM")


def trajectory(machine,secret_state,arm,weights,rng):
    """Only here can the simulator read the hidden initial state."""
    checks=machine.checks()
    if not fully_identifiable(checks,machine.size):
        raise ValueError("NONIDENTIFIABLE_MACHINE_MUST_BE_FILTERED")
    group=tuple(range(machine.size))
    steps=[]
    total_cost=0
    while len(group)>1:
        action=action_for_training(group,checks,arm,weights,rng)
        if action is None:
            raise AssertionError("IDENTIFIABLE_WITHOUT_INFORMATIVE_ACTION")
        before=group
        observation=action.values[secret_state]
        group=tuple(state for state in group
                    if action.values[state]==observation)
        if not group or len(group)>=len(before):
            raise AssertionError("INVALID_BELIEF")
        steps.append({
            "action":action.name,
            "probe_cost":action.cost,
            "features":list(features(before,action)),
            "observable_outputs":list(observation),
            "hypotheses_before":list(before),
            "hypotheses_after":list(group),
        })
        total_cost+=action.cost
    if group!=(secret_state,):
        raise AssertionError("FALSE_IDENTIFICATION")
    if len(steps)>N_STATES-1 or total_cost>COST_PER_EPISODE:
        raise AssertionError("UNEXPECTED_EPISODE_COST_OVERFLOW")
    if not steps:
        raise AssertionError("EXPECTED_POSITIVE_TRAINING_EXPERIENCE")
    return {
        "correct":True,
        "total_cost":total_cost,
        "first_probe":steps[0]["action"],
        "first_features":steps[0]["features"],
        "steps":steps,
    }


def train_seed(machines,seed):
    """Paired state/machine stream, single outcome label each, prepaid cost 6.

    It is legitimate for the trajectories/observational content to differ.
    Models are updated only from their own actual FULL episode cost.
    """
    learners={"OFF":LinearPolicy.blank(),"ON":LinearPolicy.blank()}
    memories={"OFF":[],"ON":[]}
    rng={"OFF":random.Random(seed),"ON":random.Random(seed+10000)}
    ledgers={
        arm:{
            "productive_cost":0,"filler_cost":0,"charged_cost":0,
            "completed_episodes":0,"real_probe_count":0,
            "calibration_probe_count":0,"training_labels":0,
        } for arm in learners
    }
    records=[]
    impossible=[]
    for signature,machine in machines:
        if structure_kind(machine)!="random_restricted":
            raise AssertionError("NONTRAIN_STRUCTURAL_CLASS")
        checks=machine.checks()
        if not fully_identifiable(checks,machine.size):
            impossible.append(signature)
            continue
        for secret in range(machine.size):
            pair={}
            for arm in ("OFF","ON"):
                episode=trajectory(machine,secret,arm,
                                   list(learners[arm].weights),rng[arm])
                spent=episode["total_cost"]
                filler=[]
                # An actually observed one-symbol resettable probe; its output
                # is not an SGD example and never reaches the policy.
                for _ in range(COST_PER_EPISODE-spent):
                    response=machine.observe(secret,(0,))
                    filler.append({
                        "probe":"0","outputs":list(response),
                        "cost":1,"used_for_learning":False,
                    })
                if spent+len(filler)!=COST_PER_EPISODE:
                    raise AssertionError("UNPAID_BUDGET")
                # ONE observed target per completed episode, for both arms.
                sample={
                    "features":list(episode["first_features"]),
                    "observed_return_to_go":spent,
                }
                learners[arm].learn([sample])
                memories[arm].append(sample)
                ledger=ledgers[arm]
                ledger["productive_cost"]+=spent
                ledger["filler_cost"]+=len(filler)
                ledger["charged_cost"]+=spent+len(filler)
                ledger["completed_episodes"]+=1
                ledger["training_labels"]+=1
                ledger["real_probe_count"]+=len(episode["steps"])
                ledger["calibration_probe_count"]+=len(filler)
                pair[arm]={
                    "observed_total_cost":spent,
                    "first_probe":episode["first_probe"],
                    "observed_first_probe_features":episode["first_features"],
                    "actual_trajectory":episode["steps"],
                    "calibration":filler,
                    "weight_sha256_after_episode":digest(learners[arm].weights),
                }
            records.append({
                "signature":signature,
                "true_initial_state_for_audit_only":secret,
                "arms":pair,
            })
    expected=len(records)
    if expected==0:
        raise AssertionError("NO_ADMISSIBLE_TRAINING_EPISODES")
    for arm in learners:
        ledger=ledgers[arm]
        if (ledger["completed_episodes"]!=expected or
            ledger["training_labels"]!=expected or
            learners[arm].updates!=expected or
            len(memories[arm])!=expected or
            ledger["charged_cost"]!=COST_PER_EPISODE*expected):
            raise AssertionError("UNMATCHED_INFORMATION_OR_BUDGET")
    if ledgers["OFF"]["charged_cost"]!=ledgers["ON"]["charged_cost"]:
        raise AssertionError("UNMATCHED_TRAINING_SPENDING")

    return {
        "seed":seed,
        "train_machine_count":len(machines),
        "train_identifiable":len(machines)-len(impossible),
        "train_impossible_signatures":impossible,
        "same_completed_episode_count":expected,
        "same_per_arm_charge":COST_PER_EPISODE*expected,
        "ledgers":ledgers,
        "parameters":{
            arm:{
                "initial_weights_sha256":digest([0.0]*9),
                "final_weights":list(learners[arm].weights),
                "final_weights_sha256":digest(learners[arm].weights),
                "updates":learners[arm].updates,
            } for arm in learners
        },
        "memories":{
            arm:{"examples":memories[arm],"sha256":digest(memories[arm])}
            for arm in learners
        },
        "records":records,"records_sha256":digest(records),
    }


def evaluate_seed(cohorts,training):
    """Oracle #76 is invoked solely by the existing PR130 evaluator."""
    models={
        arm:LinearPolicy(
            list(training["parameters"][arm]["final_weights"]),
            training["parameters"][arm]["updates"],
        ) for arm in ("OFF","ON")
    }
    mem={
        arm:training["memories"][arm]["examples"]
        for arm in ("OFF","ON")
    }
    arms={
        "FIXED":("fixed",None,None),
        "MEMORY_OFF":("memory",None,mem["OFF"]),
        "MEMORY_ON":("memory",None,mem["ON"]),
        "OFF":("learned",list(models["OFF"].weights),None),
        "ON":("learned",list(models["ON"].weights),None),
    }
    return {
        label:previous.evaluate(cohorts[label]["machines"],"A",arms)
        for label in ("control_random","holdout_perm","holdout_reset_cycle")
    }


def summarise_family_across_seeds(seeds,name):
    evaluations=[x["evaluations"][name] for x in seeds]
    active=evaluations[0]["eligible"]
    total=evaluations[0]["total"]
    if any(r["eligible"]!=active or r["total"]!=total
           for r in evaluations):
        raise AssertionError("UNMATCHED_EVAL_COHORT_PER_SEED")
    if not active:
        return {"total":total,"eligible":0,
                "impossible":total,"status":"INSUFFICIENT_IDENTIFIABLE_CASES"}
    policies=("FIXED","MEMORY_OFF","MEMORY_ON","OFF","ON")
    means={
        arm:sum(row["means"][arm]["mean_cost"] for row in evaluations)/
             len(evaluations) for arm in policies
    }
    worst_regret={
        arm:sum(row["means"][arm]["mean_worst_regret"] for row in evaluations)/
             len(evaluations) for arm in policies
    }
    per_seed=[
        {
            "seed":seeds[idx]["seed"],
            "ON_minus_FIXED":row["means"]["ON"]["mean_cost"]-
                             row["means"]["FIXED"]["mean_cost"],
            "ON_minus_MEMORY_OFF":row["means"]["ON"]["mean_cost"]-
                                  row["means"]["MEMORY_OFF"]["mean_cost"],
            "ON_minus_OFF":row["means"]["ON"]["mean_cost"]-
                            row["means"]["OFF"]["mean_cost"],
        }
        for idx,row in enumerate(evaluations)
    ]
    improved_vs_fixed=sum(
        result["arms"]["ON"]["mean_cost"] <
        result["arms"]["FIXED"]["mean_cost"]
        for row in evaluations for result in row["rows"] if result["identifiable"]
    )
    degraded_vs_fixed=sum(
        result["arms"]["ON"]["mean_cost"] >
        result["arms"]["FIXED"]["mean_cost"]
        for row in evaluations for result in row["rows"] if result["identifiable"]
    )
    return {
        "total":total,"eligible":active,"impossible":total-active,
        "mean_cost_per_policy":means,
        "mean_worst_regret_per_policy":worst_regret,
        "differences":{
            "ON_minus_FIXED":means["ON"]-means["FIXED"],
            "ON_minus_MEMORY_OFF":means["ON"]-means["MEMORY_OFF"],
            "ON_minus_MEMORY_ON":means["ON"]-means["MEMORY_ON"],
            "ON_minus_OFF":means["ON"]-means["OFF"],
        },
        "ON_better_machines_than_FIXED_over_seeds":improved_vs_fixed,
        "ON_worse_machines_than_FIXED_over_seeds":degraded_vs_fixed,
        "per_seed_differences":per_seed,
    }


def conduct():
    cohorts=make_new_cohorts()
    repetitions=[]
    for seed in SEEDS:
        training=train_seed(cohorts["train_random"]["machines"],seed)
        evaluations=evaluate_seed(cohorts,training)
        repetitions.append({
            "seed":seed,"training":training,"evaluations":evaluations
        })
    family_results={
        family:summarise_family_across_seeds(repetitions,family)
        for family in ("control_random","holdout_perm","holdout_reset_cycle")
    }
    holdouts=[family_results[name] for name in (
        "holdout_perm","holdout_reset_cycle"
    )]
    if any(x["eligible"]==0 for x in holdouts):
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
        passes=0
    else:
        passes=sum(
            x["differences"]["ON_minus_FIXED"]<0 and
            x["differences"]["ON_minus_MEMORY_OFF"]<0
            for x in holdouts
        )
        status=("DESCRIPTIVE_STRONG_BASELINE_TRANSFER"
                if passes==2 else "NO_STRONG_BASELINE_TRANSFER")

    manifests={}
    for name,row in cohorts.items():
        signatures=[sig for sig,_ in row["machines"]]
        manifests[name]={
            "seed":row["seed"],
            "structural_family":row["family"],
            "count":len(signatures),
            "generation_attempts":row["attempts"],
            "isomorphism_duplicates":row["isomorphism_duplicates"],
            "signatures":signatures,
            "signatures_sha256":digest(signatures),
        }
    result={
        "experiment":EXPERIMENT,
        "prereg_commit":PREREG_SHA,
        "status":status,
        "passed_both_strong_baseline_checks":passes==2,
        "structural_family_gates_passed":passes,
        "prepaid_budget_per_identifiable_training_episode":COST_PER_EPISODE,
        "seeds":list(SEEDS),
        "same_training_machines_and_hidden_starts":True,
        "same_training_label_count_per_arm":True,
        "same_charged_observation_cost_per_arm":True,
        "information_content_not_equalized":True,
        "training_feedback":"one_observed_first_action_full_episode_cost",
        "no_optimal_action_labels_in_training":True,
        "oracle_evaluation_only":True,
        "frozen_linear_SGD_lr":0.025,
        "epsilon_greedy":EPSILON,
        "language_model_trained":False,
        "paid_api_calls":0,
        "main_modified":False,
        "scientific_generalization_proven":False,
        "splits":manifests,
        "repetitions":repetitions,
        "family_results":family_results,
        "limitations":[
            "Known Mealy transitions and outputs; only initial state hidden.",
            "Every test probe resets machine; six length-one/two probes only.",
            "Equal label count and charged observation cost do not mean equal information content.",
            "Calibration probes are real but excluded from learning; report productive fraction.",
            "Only the first selected action's observed episode return is used for each update.",
            "ON and OFF action data differ; sample content/quality not controlled.",
            "The three seeds reuse the same training/evaluation machines.",
            "Primary is conjunctive versus FIXED and MEMORY_OFF in both OOD families.",
            "A single finite distribution sample does not certify generalized intelligence.",
        ],
    }
    if not all(
        row["training"]["ledgers"]["ON"]["charged_cost"]==
        row["training"]["ledgers"]["OFF"]["charged_cost"]==
        row["training"]["same_per_arm_charge"]
        for row in repetitions
    ):
        raise AssertionError("BUDGET_MATCH_VIOLATED")
    for r in repetitions:
        for arm in ("ON","OFF"):
            if r["training"]["ledgers"][arm]["training_labels"]!=(
                r["training"]["same_completed_episode_count"]
            ):
                raise AssertionError("LABEL_COUNT_MISMATCH")
            if r["training"]["parameters"][arm]["updates"]!=(
                r["training"]["same_completed_episode_count"]
            ):
                raise AssertionError("LEARNING_UPDATE_COUNT_MISMATCH")
    if len({
        sig for row in manifests.values() for sig in row["signatures"]
    })!=sum(row["count"] for row in manifests.values()):
        raise AssertionError("DUPLICATED_NEW_SPLIT")
    return result


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    report=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "status":report["status"],
        "strong_baseline_families_passed":report["structural_family_gates_passed"],
        "primary_differences":{
            x:report["family_results"][x]["differences"]
            for x in ("holdout_perm","holdout_reset_cycle")
        },
        "admissible":{
            x:report["family_results"][x]["eligible"]
            for x in report["family_results"]
        },
        "training_labels_per_arm":[
            x["training"]["same_completed_episode_count"]
            for x in report["repetitions"]
        ],
        "training_paid_budget_per_arm":[
            x["training"]["same_per_arm_charge"]
            for x in report["repetitions"]
        ],
        "report_sha256":hashlib.sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
