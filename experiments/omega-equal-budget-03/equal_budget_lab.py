"""OMEGA-EQUAL-BUDGET-03: actual prepaid probe cost matching, blind C/D transfer.

Known 4-state resettable Mealy tables, hidden initial state; not full model learning.
All learned targets are actually observed suffix probe costs. The PR76 exact
minimax solver is invoked only in evaluate(); not in train() / update().
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import argparse
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-policy-feedback-02"))
import feedback_lab as previous  # noqa: E402
from mealy_lab import Check, digest, make_cohorts  # noqa: E402

p=previous.old  # fixed, unmodified PR128 code

EXPERIMENT="OMEGA-EQUAL-BUDGET-03"
PRE_REG="3fac324fb89307d14eb152b31de3011ad4dbf9a0"
GROUPS=(
    ("train_A",11117,64),
    ("train_B",11217,64),
    ("eval_A",11317,24),
    ("eval_B",11417,24),
    ("eval_C",11517,28),
    ("eval_D",11617,28),
)
SEEDS=(881,882,883)
BUDGETS=(120,240,360)
PRIMARY_BUDGET=240
EPSILON=0.2


def machine_groups():
    """No iso overlap with #127, #128, #129, or between new splits."""
    from mealy_lab import random_machine
    prior_127=make_cohorts()
    prior_128=p.group_machines()
    prior_129=previous.cohorts()
    seen={sig for source in (prior_127,prior_128,prior_129)
          for data in source.values() for sig,_ in data["machines"]}
    assert len(seen)==90+148+124
    cohorts={}
    for name,seed,count in GROUPS:
        rng=random.Random(seed)
        items=[]
        collisions=attempts=0
        while len(items)<count:
            attempts+=1
            if attempts>100000:
                raise RuntimeError("SAMPLER_EXHAUSTED")
            machine=random_machine(rng)
            signature=machine.signature()
            if signature in seen:
                collisions+=1
                continue
            seen.add(signature)
            items.append((signature,machine))
        cohorts[name]={
            "seed":seed,"attempts":attempts,
            "isomorphism_collisions":collisions,
            "machines":items,
        }
    if len(seen)!=362+sum(row[2] for row in GROUPS):
        raise AssertionError("SPLIT_ISOMORPHISM_COLLISION")
    return cohorts


def priced_checks(machine,environment):
    base=machine.checks()
    if environment=="A":
        amounts={0:1,1:1}
    elif environment=="B":
        amounts={0:3,1:1}
    elif environment=="C":
        amounts={0:1,1:3}
    elif environment=="D":
        return tuple(Check(c.name,2 if len(c.name)==1 else 1,c.values)
                     for c in base)
    else:
        raise ValueError("UNKNOWN_COST_FAMILY")
    return tuple(Check(c.name,sum(amounts[int(v)] for v in c.name),c.values)
                 for c in base)


def choose_probe(group,checks,arm,model,rng):
    """Read only current belief, costs and learned weights. Never hidden state."""
    candidates=p.choices(group,checks)
    if not candidates:
        return None
    if arm=="OFF":
        return rng.choice(candidates)
    if arm=="ON":
        if rng.random()<EPSILON:
            return rng.choice(candidates)
        return p.choose(group,tuple(candidates),"learned",
                        weights=list(model.weights))
    raise ValueError("UNKNOWN_EXPERIENCE_POLICY")


def training_episode(machine,hidden,checks,remaining,arm,model,rng):
    """A complete diagnosis produces reward labels; a partial episode never does."""
    group=tuple(range(machine.size))
    steps=[]
    while len(group)>1:
        affordable=tuple(c for c in p.choices(group,checks)
                         if c.cost<=remaining)
        if not affordable:
            return {"complete":False,"spent":sum(s["cost"] for s in steps),
                    "steps":steps,"updates":0,"remaining_budget":remaining,
                    "remaining_belief":list(group)}
        choice=choose_probe(group,affordable,arm,model,rng)
        if choice is None or choice.cost>remaining:
            raise AssertionError("UNAFFORDABLE_OR_MISSING_ACTION")
        old_group=group
        # hidden is used ONLY here, by the simulator to produce a real reply.
        reply=choice.values[hidden]
        group=tuple(s for s in group if choice.values[s]==reply)
        if not group or len(group)>=len(old_group):
            raise AssertionError("BAD_BELIEF_TRANSITION")
        remaining-=choice.cost
        steps.append({
            "action":choice.name,"cost":choice.cost,
            "features":p.features(old_group,choice),
            "observed_outputs":list(reply),
            "belief_before":list(old_group),
            "belief_after":list(group),
        })
    if group!=(hidden,):
        raise AssertionError("FALSE_IDENTIFICATION")
    total=sum(s["cost"] for s in steps)
    # This value is observed only AFTER successful episode termination.
    suffix=0
    examples=[]
    for step in reversed(steps):
        suffix+=step["cost"]
        step["observed_return_to_go"]=suffix
    for step in steps:
        examples.append({
            "features":list(step["features"]),
            "observed_return_to_go":step["observed_return_to_go"],
        })
    return {"complete":True,"spent":total,"steps":steps,
            "examples":examples,"remaining_budget":remaining,
            "identified":hidden,"updates":len(examples)}


def train_budgeted(machines,environment,budget,arm,seed):
    """Charges EXACT budget if an informative machine stream is long enough.

    Any residual after a budget-blocked partial diagnosis is used for actual
    cheap calibration probes; those are explicitly non-learning expenditures.
    """
    if environment not in ("A","B") or arm not in ("ON","OFF"):
        raise ValueError("INVALID_TRAIN_PHASE")
    model=p.LinearPolicy.blank()
    memory=[]
    rng=random.Random(seed)
    remain=budget
    completed=partial=skipped=probe_count=0
    utilized=0
    audits=[]
    last_calibration=None
    for signature,machine in machines:
        if remain==0:
            break
        checks=priced_checks(machine,environment)
        if not p.fully_identifiable(checks,machine.size):
            skipped+=1
            continue
        for hidden in range(machine.size):
            if remain==0:
                break
            result=training_episode(machine,hidden,checks,remain,arm,model,rng)
            spent=result["spent"]
            if spent<0 or spent>remain:
                raise AssertionError("BUDGET_OVERSPEND")
            remain-=spent
            utilized+=spent
            probe_count+=len(result["steps"])
            last_calibration=(machine,hidden,checks)
            if result["complete"]:
                examples=result["examples"]
                # No oracle: targets are observed suffix costs, full episodes only.
                model.learn(examples)
                memory.extend(examples)
                completed+=1
            else:
                partial+=1
            audits.append({
                "machine_signature":signature,
                "simulator_hidden_for_audit_only":hidden,
                "complete":result["complete"],
                "episode_probe_cost":spent,
                "steps":result["steps"],
                "parameter_sha256_after":digest(model.weights),
            })
            if not result["complete"]:
                # Cannot complete with affordable informative probes.
                # Spend the remaining credit on actual calibration observations.
                break
        if partial or remain==0:
            break
    # Cohort may exhaust before any budget-limited partial episode.
    exhausted=(remain>0 and partial==0)
    filler=[]
    if remain>0 and not exhausted:
        if last_calibration is None:
            raise AssertionError("NO_CALIBRATION_MACHINE")
        machine,hidden,checks=last_calibration
        calibrator=next((c for c in checks if c.name=="1"),None)
        if calibrator is None or calibrator.cost!=1:
            raise AssertionError("CALIBRATION_UNIT_COST_UNAVAILABLE")
        while remain>0:
            actual=machine.observe(hidden,(1,))
            if tuple(calibrator.values[hidden])!=actual:
                raise AssertionError("CALIBRATION_NOT_REAL")
            filler.append({"probe":"1","observed_outputs":list(actual),
                           "cost":1,"trained_on_this":False})
            remain-=1
    used_total=budget-remain
    if used_total!=utilized+len(filler):
        raise AssertionError("UNACCOUNTED_OBSERVATION_COST")
    if model.updates!=len(memory):
        raise AssertionError("TRAINING_MEMORY_MISMATCH")
    return {
        "environment":environment,"arm":arm,"budget":budget,
        "charged_cost":used_total,
        "episode_cost_used":utilized,
        "filler_cost":len(filler),
        "unspent_due_to_cohort_exhaustion":remain,
        "fully_paid":used_total==budget,
        "completed_episodes":completed,
        "partial_episodes":partial,
        "skipped_nonidentifiable_before_budget_stop":skipped,
        "actual_probe_count":probe_count,
        "updates":model.updates,
        "weights":list(model.weights),
        "weights_sha256":digest(model.weights),
        "memory":memory,
        "memory_sha256":digest(memory),
        "audit":audits,"calibration":filler,
        "audit_sha256":digest(audits),
        "calibration_sha256":digest(filler),
    }


def train_two_phases(machines_A,machines_B,budget,arm,seed):
    """Carry model/memory A to B. Equal prepaid budget per phase and arm."""
    # First phase model; B must continue from A without duplicating learning.
    phase_A=train_budgeted(machines_A,"A",budget,arm,seed)
    model=p.LinearPolicy(list(phase_A["weights"]),phase_A["updates"])
    memory=list(phase_A["memory"])
    rng=random.Random(seed+31337)
    remaining=budget
    completed=partial=skipped=probes=utilized=0
    audits=[]
    calibration_info=None
    for signature,machine in machines_B:
        if remaining==0:break
        checks=priced_checks(machine,"B")
        if not p.fully_identifiable(checks,machine.size):
            skipped+=1
            continue
        for hidden in range(machine.size):
            if remaining==0:break
            outcome=training_episode(machine,hidden,checks,remaining,arm,model,rng)
            spent=outcome["spent"]
            if not 0<=spent<=remaining:raise AssertionError("B_COST_OVERSPEND")
            remaining-=spent
            utilized+=spent
            probes+=len(outcome["steps"])
            calibration_info=(machine,hidden,checks)
            if outcome["complete"]:
                model.learn(outcome["examples"])
                memory.extend(outcome["examples"])
                completed+=1
            else:
                partial+=1
            audits.append({
                "machine_signature":signature,
                "simulator_hidden_for_audit_only":hidden,
                "complete":outcome["complete"],
                "episode_probe_cost":spent,
                "steps":outcome["steps"],
                "parameter_sha256_after":digest(model.weights),
            })
            if not outcome["complete"]:break
        if partial or remaining==0:break
    exhausted=(remaining>0 and partial==0)
    filler=[]
    if remaining>0 and not exhausted:
        if calibration_info is None:raise AssertionError("NO_B_CALIBRATION_MACHINE")
        m,h,checks=calibration_info
        cheap=next(c for c in checks if c.name=="1")
        if cheap.cost!=1:raise AssertionError("B_CHEAP_PROBE_NOT_UNIT_COST")
        while remaining:
            actual=m.observe(h,(1,))
            if actual!=cheap.values[h]:raise AssertionError("B_CALIBRATION_INVALID")
            filler.append({"probe":"1","observed_outputs":list(actual),
                           "cost":1,"trained_on_this":False})
            remaining-=1
    charged=budget-remaining
    if charged!=utilized+len(filler):
        raise AssertionError("B_UNACCOUNTED_COST")
    if model.updates!=len(memory):
        raise AssertionError("TWO_PHASE_UPDATE_COUNT_MISMATCH")
    phase_B={
        "environment":"B","arm":arm,"budget":budget,
        "charged_cost":charged,"episode_cost_used":utilized,
        "filler_cost":len(filler),
        "unspent_due_to_cohort_exhaustion":remaining,
        "fully_paid":charged==budget,
        "completed_episodes":completed,"partial_episodes":partial,
        "skipped_nonidentifiable_before_budget_stop":skipped,
        "actual_probe_count":probes,
        "updates_after_B":model.updates,
        "weights_sha256_after_B":digest(model.weights),
        "memory_records_after_B":len(memory),
        "memory_sha256_after_B":digest(memory),
        "audit":audits,"calibration":filler,
        "audit_sha256":digest(audits),
        "calibration_sha256":digest(filler),
    }
    return model,memory,{"A":phase_A,"B":phase_B}


def evaluate(machines,environment,policies):
    """Only evaluator imports and uses the exact P5 oracle."""
    rows=[]
    eligible=0
    for signature,machine in machines:
        checks=priced_checks(machine,environment)
        oracle=p.solve(tuple(range(machine.size)),checks)
        identifiable=p.fully_identifiable(checks,machine.size)
        if identifiable!=(oracle["adaptive"] is not None):
            raise AssertionError("ORACLE_IDENTIFIABILITY_CONFLICT")
        row={
            "signature":signature,
            "identifiable":identifiable,
            "oracle_exact_adaptive_worst_cost":oracle["adaptive"],
            "oracle_exact_fixed_worst_cost":oracle["fixed"],
            "arms":{},
        }
        if identifiable:
            eligible+=1
            for name,armdata in policies.items():
                policy,weights,memory=armdata
                trials=[p.run_episode(machine,checks,s,policy,
                                      weights=weights,memory=memory,log=False)
                        for s in range(machine.size)]
                if not all(t["success"] for t in trials):
                    raise AssertionError("FALSELY_ABSTAINED")
                per_state=[t["total_cost"] for t in trials]
                worst=max(per_state)
                if worst<oracle["adaptive"]:
                    raise AssertionError("BEATS_EXACT_MINIMAX_ORACLE")
                row["arms"][name]={
                    "mean_cost":sum(per_state)/machine.size,
                    "worst_cost":worst,
                    "worst_regret":worst-oracle["adaptive"],
                    "per_state_costs":per_state,
                }
        else:
            row["status"]="IMPOSSIBLE_WITH_FROZEN_SIX_PROBES"
        rows.append(row)
    means={}
    if eligible:
        for name in policies:
            values=[r["arms"][name] for r in rows if r["identifiable"]]
            means[name]={
                "mean_cost":sum(r["mean_cost"] for r in values)/eligible,
                "mean_worst_cost":sum(r["worst_cost"] for r in values)/eligible,
                "mean_worst_regret":sum(r["worst_regret"] for r in values)/eligible,
            }
    return {"environment":environment,"total":len(machines),
            "eligible":eligible,"impossible":len(machines)-eligible,
            "means":means,"rows":rows}


def evaluated_arms(model_off,model_on,memory_off,memory_on):
    if not memory_off or not memory_on:
        raise AssertionError("TRAIN_MEMORY_MISSING")
    return {
        "FIXED":("fixed",None,None),
        "MEMORY_OFF":("memory",None,memory_off),
        "MEMORY_ON":("memory",None,memory_on),
        "OFF":("learned",list(model_off.weights),None),
        "ON":("learned",list(model_on.weights),None),
    }


def contrast(report,a,b):
    if not report["eligible"]:
        return None
    return report["means"][a]["mean_cost"]-report["means"][b]["mean_cost"]


def one_repetition(groups,seed,budget):
    off,mem_off,train_off=train_two_phases(
        groups["train_A"]["machines"],groups["train_B"]["machines"],
        budget,"OFF",seed)
    on,mem_on,train_on=train_two_phases(
        groups["train_A"]["machines"],groups["train_B"]["machines"],
        budget,"ON",seed)
    arms=evaluated_arms(off,on,mem_off,mem_on)
    outcomes={
        label:evaluate(groups[f"eval_{label}"]["machines"],label,arms)
        for label in ("A","B","C","D")
    }
    totals={
        "OFF":sum(x["charged_cost"] for x in train_off.values()),
        "ON":sum(x["charged_cost"] for x in train_on.values()),
    }
    budget_valid=all(phase["fully_paid"]
                     for training in (train_off,train_on)
                     for phase in training.values())
    primary_parts={
        name:contrast(outcomes[name],"ON","OFF")
        for name in ("C","D")
    }
    return {
        "seed":seed,"per_phase_budget":budget,
        "comparison_valid_at_charged_budget":budget_valid and (
            totals["ON"]==totals["OFF"]==2*budget),
        "charged_total_cost":totals,
        "train":{"OFF":train_off,"ON":train_on},
        "trained_parameter_hash":{"OFF":digest(off.weights),"ON":digest(on.weights)},
        "evaluation":outcomes,
        "on_minus_off_per_unseen_cost_family":primary_parts,
        "strong_baseline_deltas":{
            name:{
                "ON_minus_FIXED":contrast(outcomes[name],"ON","FIXED"),
                "ON_minus_MEMORY_OFF":contrast(outcomes[name],"ON","MEMORY_OFF"),
                "ON_minus_MEMORY_ON":contrast(outcomes[name],"ON","MEMORY_ON"),
            } for name in ("C","D")
        },
    }


def conduct():
    groups=machine_groups()
    observations=[]
    for budget in BUDGETS:
        for seed in SEEDS:
            observations.append(one_repetition(groups,seed,budget))
    primary_trials=[o for o in observations
                    if o["per_phase_budget"]==PRIMARY_BUDGET]
    if any(not r["comparison_valid_at_charged_budget"] for r in primary_trials):
        primary=None
        status="INVALID_EQUAL_COST_COMPARISON"
    elif any(v is None
             for r in primary_trials
             for v in r["on_minus_off_per_unseen_cost_family"].values()):
        primary=None
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
    else:
        diffs=[v for r in primary_trials
                 for v in r["on_minus_off_per_unseen_cost_family"].values()]
        primary=sum(diffs)/len(diffs)
        status=("DESCRIPTIVE_EQUAL_BUDGET_ON_ADVANTAGE" if primary<0
                else "EQUAL_BUDGET_ON_REGRESSION" if primary>0
                else "NO_EQUAL_BUDGET_ON_ADVANTAGE")
    manifests={}
    for name,group in groups.items():
        signatures=[s for s,_ in group["machines"]]
        manifests[name]={
            "seed":group["seed"],"size":len(signatures),
            "attempts":group["attempts"],
            "isomorphism_collisions":group["isomorphism_collisions"],
            "signatures":signatures,
            "signatures_sha256":digest(signatures),
        }
    result={
        "experiment":EXPERIMENT,"prereg_commit":PRE_REG,
        "status":status,
        "primary_ON_minus_OFF":primary,
        "primary_budget_total_charged_per_arm":2*PRIMARY_BUDGET,
        "seeds":list(SEEDS),"per_phase_budgets":list(BUDGETS),
        "known_model_unknown_start":True,
        "no_optimal_labels_in_train":True,
        "oracle_evaluation_only":True,
        "language_model_trained":False,
        "paid_api_calls":0,
        "main_modified":False,
        "scientific_generalization_proven":False,
        "primary_unseen_cost_families":["C","D"],
        "primary_repeated_seeds_same_holdout":True,
        "split_manifests":manifests,
        "observations":observations,
        "limits":[
            "Same prepaid cost, but informative completed-episode cost and data differ.",
            "Calibration filler costs are real probes, deliberately not used to train.",
            "One precommitted holdout; three seeds do not make three independent datasets.",
            "Equal observed probe-cost does not equalize Python CPU cost.",
            "Model of the Mealy system is known; only hidden initial state diagnosed.",
            "Exact oracle proves worst-case bound, not mean-cost optimality.",
            "Neither language model nor self-modifying algorithm was trained.",
        ],
    }
    signatures=[s for g in manifests.values() for s in g["signatures"]]
    if len(signatures)!=len(set(signatures)):
        raise AssertionError("NEW_SPLIT_COLLISION")
    for row in observations:
        for e in ("A","B","C","D"):
            ev=row["evaluation"][e]
            if ev["eligible"]+ev["impossible"]!=ev["total"]:
                raise AssertionError("EVAL_COHORT_DROP")
            for r in ev["rows"]:
                if r["identifiable"]:
                    for details in r["arms"].values():
                        if details["worst_regret"]<0:
                            raise AssertionError("BEATS_ORACLE")
        for arm in ("ON","OFF"):
            for phase in ("A","B"):
                x=row["train"][arm][phase]
                if x["charged_cost"] != x["episode_cost_used"]+x["filler_cost"]:
                    raise AssertionError("BAD_LEDGER")
                if x["charged_cost"]>x["budget"]:
                    raise AssertionError("OVER_BUDGET")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    report=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(raw)
    summary={
        "experiment":EXPERIMENT,
        "status":report["status"],
        "primary_ON_minus_OFF":report["primary_ON_minus_OFF"],
        "primary_equal_charged_budget":all(
            r["comparison_valid_at_charged_budget"] for r in report["observations"]
            if r["per_phase_budget"]==PRIMARY_BUDGET
        ),
        "primary_families_eligible":{
            e:report["observations"][3]["evaluation"][e]["eligible"]
            for e in ("C","D")
        },
        "primary_seed_diffs":[
            {"seed":r["seed"],"differences":r["on_minus_off_per_unseen_cost_family"],
             "charged":r["charged_total_cost"]}
            for r in report["observations"]
            if r["per_phase_budget"]==PRIMARY_BUDGET
        ],
        "report_sha256":sha256(raw).hexdigest(),
    }
    print(json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    main()
