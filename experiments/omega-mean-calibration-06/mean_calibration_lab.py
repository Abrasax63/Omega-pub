"""OMEGA-CALIBRATION-06 — rational exact mean and uniform-value calibration.

Trained models/collection are UNCHANGED from PR #132; only evaluators and new
sealed machine cohorts are added. Machines are KNOWN, hidden initial state
unknown. Every probe resets to that same hidden state. No black-box model
learning, neural-network training, or API calls.
"""
from __future__ import annotations
from collections import deque
from fractions import Fraction
from functools import cache
from hashlib import sha256
from pathlib import Path
import argparse
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-belief-value-05"))
import belief_value_lab as b  # unchanged PR132 learner
from mealy_lab import digest

EXPERIMENT="OMEGA-CALIBRATION-06"
PREREG="188336dfb8629c50e09ed8f0eb3a133e1c7e8c99"
SPLITS=(
    ("eval_random4",23117,24,"random4"),
    ("eval_perm5",23118,30,"perm5"),
    ("eval_reset5",23119,30,"reset5"),
)
RESERVED=("eval_perm5","eval_reset5")
TEST_OBSERVATION_SEED=44321
EPS=1e-10


def new_holdouts(old_cohorts=None):
    """No old pilot machine, no new cross-family state-renaming duplicates."""
    if old_cohorts is None:
        old_cohorts=b.cohorts()
    seen={sig for part in old_cohorts.values()
          for sig,_ in part["machines"]}
    if len(seen)!=858:
        raise AssertionError("OLD_HOLDOUT_COUNT_CHANGED")
    data={}
    for name,seed,count,kind in SPLITS:
        rng=random.Random(seed)
        machines=[]
        collisions=attempts=0
        while len(machines)<count:
            attempts+=1
            if attempts>100000:
                raise AssertionError("UNIQUE_MACHINE_EXHAUSTION")
            machine=b.make_machine(rng,kind)
            if b.category(machine)!=kind:
                raise AssertionError("STRUCTURAL_FAMILY_MISMATCH")
            sig=machine.signature()
            if sig in seen:
                collisions+=1
                continue
            seen.add(sig)
            machines.append((sig,machine))
        data[name]={
            "seed":seed,"kind":kind,"count":count,
            "attempts":attempts,"isomorphism_collisions":collisions,
            "machines":machines,
        }
    assert len(seen)==858+sum(s[2] for s in SPLITS)
    return data


def fr(value):
    """Exact rational evidence with decimal used only for presentation."""
    value=Fraction(value)
    return {"numerator":value.numerator,"denominator":value.denominator,
            "decimal":float(value)}


class ExactMeanAndUniform:
    """Two separate exact rational DPs with the identical six-probe menu.

    - optimum: the best adaptive *expected mean* probe cost, uniform hidden state
    - uniform: expected cost of choosing a random informative probe at each node
    Both use exact Fraction arithmetic; neither is available in train_shared().
    """
    def __init__(self,checks,n_states):
        self.checks=tuple(checks)
        self.n=n_states
        if n_states<=1 or len(self.checks)!=6:
            raise ValueError("INVALID_EVALUATION_DOMAIN")
        if any(len(c.values)!=n_states or c.cost<1 for c in self.checks):
            raise ValueError("INVALID_ORACLE_CHECKS")

    def actions(self,group):
        return b.choices(group,self.checks)

    def blocks(self,group,action):
        parts=b.partitions(group,action)
        if sum(map(len,parts))!=len(group):
            raise AssertionError("NOT_A_PARTITION")
        return parts

    @cache
    def optimum(self,group):
        if len(group)<=1:
            return Fraction(0)
        options=self.actions(group)
        if not options:
            raise ValueError("NONIDENTIFIABLE_EXACT_MEAN_STATE")
        return min(self.opt_q(group,c) for c in options)

    def opt_q(self,group,action):
        subgroups=self.blocks(group,action)
        if len(subgroups)<=1:
            raise ValueError("NONINFORMATIVE_ACTION")
        return Fraction(action.cost)+sum(
            Fraction(len(sub),len(group))*self.optimum(sub)
            for sub in subgroups
        )

    def optimal_action(self,group):
        actions=self.actions(group)
        if not actions:
            return None
        return min(actions,key=lambda a:(
            self.opt_q(group,a),a.cost,a.name
        ))

    @cache
    def uniform(self,group):
        if len(group)<=1:
            return Fraction(0)
        actions=self.actions(group)
        if not actions:
            raise ValueError("NONIDENTIFIABLE_UNIFORM_STATE")
        return sum(
            Fraction(a.cost)+sum(
                Fraction(len(sub),len(group))*self.uniform(sub)
                for sub in self.blocks(group,a)
            ) for a in actions
        )/len(actions)

    def reachable_beliefs(self):
        """Every reachable, non-singleton posterior, counted once per machine."""
        full=tuple(range(self.n))
        seen=set()
        queue=[full]
        while queue:
            group=queue.pop()
            if group in seen:
                continue
            seen.add(group)
            for action in self.actions(group):
                queue.extend(self.blocks(group,action))
        return tuple(sorted((s for s in seen if len(s)>1),
                            key=lambda s:(-len(s),s)))

    def actual_optimal_costs(self):
        """Exhaustively replay the chosen optimal mean decision tree."""
        costs=[]
        for hidden in range(self.n):
            group=tuple(range(self.n))
            cost=0
            while len(group)>1:
                action=self.optimal_action(group)
                if action is None:
                    raise AssertionError("MISSING_EXACT_MEAN_ACTION")
                result=action.values[hidden]
                nxt=tuple(s for s in group if action.values[s]==result)
                if not nxt or len(nxt)>=len(group):
                    raise AssertionError("EXACT_MEAN_ORACLE_LOOP")
                group=nxt
                cost+=action.cost
            if group!=(hidden,):
                raise AssertionError("EXACT_ORACLE_FALSE_IDENTIFICATION")
            costs.append(cost)
        if Fraction(sum(costs),self.n)!=self.optimum(tuple(range(self.n))):
            raise AssertionError("MEAN_DP_REPLAY_MISMATCH")
        return costs


def uniform_episode(machine,hidden,rng):
    """Observed evaluation-only test episodes, never fed into train_shared()."""
    checks=machine.checks()
    group=tuple(range(machine.size))
    steps=[]
    total=0
    while len(group)>1:
        action=rng.choice(b.choices(group,checks))
        before=group
        response=action.values[hidden]
        group=tuple(s for s in group if action.values[s]==response)
        if len(group)>=len(before) or not group:
            raise AssertionError("BAD_HELDOUT_OBSERVATION")
        total+=action.cost
        steps.append({
            "probe":action.name,"cost":action.cost,
            "observed_outputs":list(response),
            "belief_before":list(before),
            "belief_after":list(group),
        })
    suffix=0
    for item in reversed(steps):
        suffix+=item["cost"]
        item["observed_return_to_go"]=suffix
    return steps,total


def evaluate_one_cohort(machines,trained,test_seed=TEST_OBSERVATION_SEED):
    """Every exact oracle is used here, not in training or learned decisions."""
    rng=random.Random(test_seed)
    policies=("FIXED","MEMORY","TOTAL9","BELIEF_VALUE")
    rows=[]
    eligible=0
    for signature,machine in machines:
        checks=machine.checks()
        identifiable=b.fully_identifiable(checks,machine.size)
        row={
            "signature":signature,"num_states":machine.size,
            "identifiable":identifiable,
            "calibration":None,"decisions":{},
        }
        if not identifiable:
            row["status"]="JUSTIFIED_ABSTENTION_INIDENTIFIABLE"
            rows.append(row)
            continue
        eligible+=1
        oracle=ExactMeanAndUniform(checks,machine.size)
        full=tuple(range(machine.size))
        vstar=oracle.optimum(full)
        optimum_costs=oracle.actual_optimal_costs()
        old_minimax=b.solve(full,checks)["adaptive"]
        if old_minimax is None:
            raise AssertionError("MINIMAX_UNAVAILABLE_FOR_IDENTIFIABLE")
        if vstar>old_minimax:
            raise AssertionError("MEAN_GREATER_THAN_MINIMAX")
        if max(optimum_costs)<old_minimax:
            raise AssertionError("MEAN_POLICY_BEATS_MINIMAX")
        row["oracle_exact_mean"] = fr(vstar)
        row["oracle_exact_mean_per_state"] = optimum_costs
        row["oracle_old_minimax_worst"]=old_minimax
        row["oracle_uniform_expected_cost"]=fr(oracle.uniform(full))

        # Predictions for every reachable *non-singleton* belief. Observed
        # calibration reports a separate, noisy held-out trajectory measure.
        cal=[]
        for group in oracle.reachable_beliefs():
            actual=oracle.uniform(group)
            predicted=trained["structured"].predict(
                group,checks,machine.size)
            size_reference=len(group)-1
            cal.append({
                "group":list(group),"size":len(group),
                "V_uniform_rational":fr(actual),
                "V_belief_pred":predicted,
                "signed_error":predicted-float(actual),
                "abs_error":abs(predicted-float(actual)),
                "size_baseline_error":abs(size_reference-float(actual)),
                "zero_baseline_error":float(actual),
            })
        if not cal:
            raise AssertionError("NO_NONTRIVIAL_REACHABLE_BELIEFS")
        sampled=[]
        for hidden in range(machine.size):
            trace,total=uniform_episode(machine,hidden,rng)
            if not trace:
                raise AssertionError("EMPTY_HELDOUT_EPISODE")
            first=trace[0]
            after=tuple(first["belief_after"])
            realized=total-first["cost"]
            predicted=trained["structured"].predict(after,checks,machine.size)
            sampled.append({
                "hidden_for_audit_only":hidden,
                "first_probe":first["probe"],
                "first_observation":first["observed_outputs"],
                "successor_belief":list(after),
                "actually_observed_remaining_cost":realized,
                "prediction":predicted,
                "abs_prediction_error":abs(predicted-realized),
                "full_observed_probe_cost":total,
                "full_trajectory":trace,
            })

        def avg(key):
            return sum(c[key] for c in cal)/len(cal)
        row["calibration"]={
            "reachable_nontrivial_beliefs":len(cal),
            "mae_belief":avg("abs_error"),
            "bias_belief":avg("signed_error"),
            "mae_size":avg("size_baseline_error"),
            "mae_zero":avg("zero_baseline_error"),
            "realized_holdout_mae":sum(
                x["abs_prediction_error"] for x in sampled)/len(sampled),
            "per_belief":cal,
            "heldout_real_observations":sampled,
        }

        for arm in policies:
            costs=[]
            for hidden in range(machine.size):
                if arm=="BELIEF_VALUE":
                    output=b.run_value_episode(machine,hidden,trained["structured"])
                    spent=output["cost"]
                else:
                    method={"FIXED":"fixed","MEMORY":"memory","TOTAL9":"learned"}[arm]
                    ep=b.run_episode(machine,checks,hidden,method,
                                     weights=trained["baseline"].weights,
                                     memory=trained["memory"],log=False)
                    if not ep["success"]:
                        raise AssertionError("FALSE_HELDOUT_ABSTENTION")
                    spent=ep["total_cost"]
                costs.append(spent)
            empirical_mean=Fraction(sum(costs),machine.size)
            regret=empirical_mean-vstar
            if regret<0:
                raise AssertionError("LEARNED_POLICY_BEATS_EXACT_MEAN_ORACLE")
            if max(costs)<old_minimax:
                raise AssertionError("LEARNED_POLICY_BEATS_MINIMAX_ORACLE")
            row["decisions"][arm]={
                "cost_per_hidden_initial":costs,
                "mean_cost":fr(empirical_mean),
                "mean_regret_to_exact":fr(regret),
                "worst_cost":max(costs),
                "worst_regret_to_old_minimax":max(costs)-old_minimax,
            }
        rows.append(row)

    group_cal=group_decision=None
    if eligible:
        valid=[r for r in rows if r["identifiable"]]
        group_cal={
            name:sum(r["calibration"][name] for r in valid)/eligible
            for name in ("mae_belief","bias_belief","mae_size",
                         "mae_zero","realized_holdout_mae")
        }
        group_cal["mean_reachable_beliefs"]=sum(
            r["calibration"]["reachable_nontrivial_beliefs"]
            for r in valid)/eligible
        group_decision={
            arm:{
                "mean_cost":sum(
                    r["decisions"][arm]["mean_cost"]["decimal"]
                    for r in valid)/eligible,
                "mean_regret_to_exact":sum(
                    r["decisions"][arm]["mean_regret_to_exact"]["decimal"]
                    for r in valid)/eligible,
                "mean_worst_regret_to_minimax":sum(
                    r["decisions"][arm]["worst_regret_to_old_minimax"]
                    for r in valid)/eligible,
            } for arm in policies
        }
        group_decision["EXACT_MEAN_ORACLE"]={
            "mean_cost":sum(
                r["oracle_exact_mean"]["decimal"] for r in valid)/eligible,
            "mean_regret_to_exact":0.0,
        }
    return {
        "total":len(machines),"eligible":eligible,
        "impossible":len(machines)-eligible,
        "calibration":group_cal,"decisions":group_decision,
        "rows":rows,
    }


def summarize(repetitions,name):
    data=[r["evaluations"][name] for r in repetitions]
    n=data[0]["eligible"]
    if any(x["eligible"]!=n for x in data):
        raise AssertionError("EVAL_CASES_DRIFTED_ACROSS_SEEDS")
    if n==0:
        return {"total":data[0]["total"],"eligible":0,"impossible":data[0]["total"]}
    cal={key:sum(r["calibration"][key] for r in data)/len(data)
         for key in data[0]["calibration"]}
    arms=data[0]["decisions"].keys()
    policy={
        arm:{
            k:sum(r["decisions"][arm][k] for r in data)/len(data)
            for k in data[0]["decisions"][arm]
        } for arm in arms
    }
    def diff(arm):
        return (policy["BELIEF_VALUE"]["mean_regret_to_exact"]-
                policy[arm]["mean_regret_to_exact"])
    return {
        "total":data[0]["total"],"eligible":n,
        "impossible":data[0]["total"]-n,
        "calibration":cal,"policy":policy,
        "decision_regret_differences":{
            "BELIEF_VALUE_minus_TOTAL9":diff("TOTAL9"),
            "BELIEF_VALUE_minus_FIXED":diff("FIXED"),
            "BELIEF_VALUE_minus_MEMORY":diff("MEMORY"),
        },
    }


def conduct():
    old=b.cohorts()
    cohorts=new_holdouts(old)
    repeat=[]
    for seed in b.SEEDS:
        # THE EXACT SAME TRAINING CODE AND TRAINING SET AS PR #132.
        shared=b.collect(old["train_random4"]["machines"],seed)
        trained=b.train_shared(shared)
        before={
            "TOTAL9":digest(trained["baseline"].weights),
            "BELIEF_VALUE":digest(trained["structured"].weights),
            "MEMORY":digest(trained["memory"]),
        }
        evaluations={
            name:evaluate_one_cohort(
                cohorts[name]["machines"],trained,TEST_OBSERVATION_SEED)
            for name,*_ in SPLITS
        }
        after={
            "TOTAL9":digest(trained["baseline"].weights),
            "BELIEF_VALUE":digest(trained["structured"].weights),
            "MEMORY":digest(trained["memory"]),
        }
        if before!=after:
            raise AssertionError("HOLDOUT_CHANGED_TRAINED_PARAMETERS")
        if not (trained["baseline"].updates==trained["structured"].updates==shared["episodes"]):
            raise AssertionError("TRAINED_LABEL_COUNT_CHANGED")
        repeat.append({
            "seed":seed,
            "training_episodes":shared["episodes"],
            "training_probe_cost":shared["real_probe_cost"],
            "train_initials":shared["episodes"],
            "training_weights_sha":before,
            "evaluation_weights_sha":after,
            "evaluations":evaluations,
        })
    aggregate={name:summarize(repeat,name) for name,*_ in SPLITS}
    if any(aggregate[name]["eligible"]==0 for name in RESERVED):
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
        passed=0
    else:
        passed=0
        for name in RESERVED:
            group=aggregate[name]
            c=group["calibration"]
            deltas=group["decision_regret_differences"]
            calibration_pass=(
                c["mae_belief"] < c["mae_size"]-EPS and
                c["mae_belief"] < c["mae_zero"]-EPS
            )
            decision_pass=all(v < -EPS for v in deltas.values())
            passed+=int(calibration_pass and decision_pass)
        status=("DESCRIPTIVE_CALIBRATED_MEAN_GAIN" if passed==len(RESERVED)
                else "NO_CALIBRATED_MEAN_GAIN")
    manifests={
        name:{
            "seed":entry["seed"],"family":entry["kind"],
            "count":entry["count"],"attempts":entry["attempts"],
            "isomorphism_collisions":entry["isomorphism_collisions"],
            "signatures":[s for s,_ in entry["machines"]],
            "signatures_sha256":digest([s for s,_ in entry["machines"]]),
        } for name,entry in cohorts.items()
    }
    result={
        "experiment":EXPERIMENT,"prereg_commit":PREREG,
        "status":status,"strong_families_passed":passed,
        "test_observation_rng_seed":TEST_OBSERVATION_SEED,
        "evaluation_families":[x[0] for x in SPLITS],
        "structural_holdouts":list(RESERVED),
        "training_seeds":list(b.SEEDS),
        "training_original_PR132_code_unchanged":True,
        "model_updated_during_evaluation":False,
        "oracle_used_for_training":False,
        "oracle_used_for_evaluation_only":True,
        "exact_mean_oracle_rational":True,
        "uniform_policy_calibration_oracle_rational":True,
        "same_raw_training_data_for_learners":True,
        "paid_api_calls":0,"language_model_trained":False,
        "main_modified":False,"scientific_generalization_proven":False,
        "splits":manifests,"repetitions":repeat,"summary":aggregate,
        "limitations":[
            "Known Mealy transitions and outputs, hidden starting state only.",
            "Optimality is exact only for this six-probe resettable experiment.",
            "Prior over hidden starting state is uniform.",
            "Calibration target is uniform-probe future, NOT the policy's own future.",
            "Four- and five-state test machines, repeated seeds share test cases.",
            "No model updates or thresholds adjusted on the reserved evaluation.",
            "Better calibration does not imply better decisions in general.",
        ],
    }
    return result


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",required=True,type=Path)
    args=cli.parse_args()
    result=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,
        "status":result["status"],
        "strong_families_passed":result["strong_families_passed"],
        "eligible":{
            name:result["summary"][name]["eligible"]
            for name in result["summary"]
        },
        "summary":{
            name:{
                "calibration":result["summary"][name].get("calibration"),
                "regret":result["summary"][name].get("decision_regret_differences"),
            } for name in result["summary"]
        },
        "report_sha256":sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
