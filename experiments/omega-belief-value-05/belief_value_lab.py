"""OMEGA-BELIEF-VALUE-05: two representations, *identical* observed episodes.

Known Mealy table, hidden initial state only. Shared uniform-exploration
trajectories supply the SAME raw observations to both learned models:
TOTAL9 predicts observed total return from the first probe; BELIEF_VALUE
predicts continuation cost from the observed successor belief. It evaluates
candidate probes by their known outcome partitions plus learned continuation.
No oracle or counterfactual optimal-action labels during learning.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import random
import sys
from pathlib import Path
from itertools import permutations

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-structural-transfer-04"))
import structural_lab as previous  # noqa: E402
from mealy_lab import Mealy, digest, make_cohorts
from plasticity_lab import (LinearPolicy, features, choices, fully_identifiable,
                            MEMORY_K, choose as choose_old, run_episode,
                            LEARNING_RATE, score, solve)

EXPERIMENT="OMEGA-BELIEF-VALUE-05"
PREREG_SHA="c6c2c40f49662b04fbbd9f1525bfccb186c8db73"
SEEDS=(271,272,273)
COHORTS=(
    ("train_random4",22117,56,"random4"),
    ("eval_control4",22118,20,"random4"),
    ("eval_holdout_perm5",22119,24,"perm5"),
    ("eval_holdout_reset5",22120,24,"reset5"),
)
VALUE_DIMS=7
GROUPS_OF_INTEREST=("eval_holdout_perm5","eval_holdout_reset5")


def make_machine(rng,kind):
    if kind=="random4":
        return previous.generate_machine(rng,"random_restricted")
    n=5
    if kind=="perm5":
        left=rng.sample(range(n),n)
        right=rng.sample(range(n),n)
        transitions=tuple((left[i],right[i]) for i in range(n))
    elif kind=="reset5":
        target=rng.randrange(n)
        cycle=rng.sample(range(n),n)
        step={cycle[i]:cycle[(i+1)%n] for i in range(n)}
        transitions=tuple((target,step[i]) for i in range(n))
    else:
        raise ValueError("INVALID_FAMILY")
    outputs=tuple((rng.randrange(3),rng.randrange(3)) for _ in range(n))
    return Mealy(transitions,outputs)


def category(machine):
    if machine.size==4:
        return "random4" if previous.structure_kind(machine)=="random_restricted" else "other4"
    if machine.size==5:
        left=tuple(machine.transitions[i][0] for i in range(5))
        right=tuple(machine.transitions[i][1] for i in range(5))
        if len(set(left))==5 and len(set(right))==5:
            return "perm5"
        if len(set(left))==1:
            current=0
            visited=set()
            for _ in range(5):
                if current in visited:
                    break
                visited.add(current)
                current=right[current]
            if current==0 and len(visited)==5:
                return "reset5"
    return "other"


def cohorts():
    old=(make_cohorts(),previous.previous.p.group_machines(),
         previous.previous.previous.cohorts(),
         previous.previous.machine_groups(),previous.make_new_cohorts())
    seen={s for group in old for row in group.values()
          for s,_ in row["machines"]}
    if len(seen)!=734:
        raise AssertionError(f"OLD_COHORT_SIGNATURES_MISMATCH:{len(seen)}")
    data={}
    for name,seed,count,kind in COHORTS:
        rng=random.Random(seed)
        items=[]
        duplicates=attempts=0
        while len(items)<count:
            attempts+=1
            if attempts>100000:
                raise RuntimeError("CANONICAL_MACHINE_EXHAUSTION")
            m=make_machine(rng,kind)
            if category(m)!=kind:
                raise AssertionError("UNEXPECTED_STRUCTURAL_FAMILY")
            sig=m.signature()
            if sig in seen:
                duplicates+=1
                continue
            seen.add(sig)
            items.append((sig,m))
        data[name]={
            "seed":seed,"family":kind,"count":count,
            "attempts":attempts,"isomorphism_duplicates":duplicates,
            "machines":items,
        }
    if len(seen)!=734+sum(row[2] for row in COHORTS):
        raise AssertionError("CROSS_SPLIT_CANONICAL_COLLISION")
    return data


def partitions(group,check):
    found={}
    for initial in group:
        found.setdefault(check.values[initial],[]).append(initial)
    return tuple(tuple(x) for x in found.values())


def successor_features(group,checks,all_states):
    """Seven representation features based only on known partitions/costs.

    No labels, oracle or hidden initial state. Singleton downstream cost is 0.
    """
    if len(group)<=1:
        return (0.0,)*VALUE_DIMS
    actions=choices(group,checks)
    if not actions:
        raise ValueError("NONIDENTIFIABLE_POSTERIOR")
    n=len(group)
    a=[(c,partitions(group,c)) for c in actions]
    return (
        n/all_states,                            # relative posterior size
        n*(n-1)/(all_states*(all_states-1)),       # unresolved pair fraction
        min(c.cost for c,_ in a)/2.0,             # cheapest informative probe
        min(max(len(b) for b in blocks)/n
            for _,blocks in a),                 # best worst-case retention
        max((n*n-sum(len(b)**2 for b in blocks))/
            (n*n*c.cost) for c,blocks in a),    # split rate per cost
        len({tuple(sorted(len(b) for b in blocks))
             for _,blocks in a})/len(checks),   # distinct partition profiles
        max(len(blocks)/n for _,blocks in a),   # maximum outcomes per state
    )


def dot(weights,fs):
    return sum(a*b for a,b in zip(weights,fs))


@dataclass
class BeliefValue:
    weights: list[float]
    updates: int=0

    @classmethod
    def blank(cls):
        return cls([0.0]*VALUE_DIMS)

    def learn_one(self,vec,observed_remainder):
        actual=float(observed_remainder)
        if actual<0:
            raise AssertionError("NEGATIVE_OBSERVED_REMAINDER")
        error=max(-10.0,min(10.0,actual-dot(self.weights,vec)))
        self.weights=[w+LEARNING_RATE*error*x
                      for w,x in zip(self.weights,vec)]
        self.updates+=1

    def predict(self,group,checks,n):
        if len(group)<=1:
            return 0.0
        return max(0.0,dot(self.weights,successor_features(group,checks,n)))


def value_action(group,checks,model):
    """One-step *expected* remaining cost under uniform possible hidden states."""
    available=choices(group,checks)
    if not available:
        return None
    n=len(group)
    # all_state_count may be 4 in training and 5 on holdout
    full_n=len(checks[0].values)
    return min(available,key=lambda c:(
        c.cost+sum((len(block)/n)*model.predict(block,checks,full_n)
                   for block in partitions(group,c)),
        c.cost,c.name,
    ))


def collect(machines,seed):
    """One shared observed stream: no policy is consulted while generating it."""
    rng=random.Random(seed)
    records=[]
    impossible=[]
    probe_cost=0
    actual_probe_count=0
    for sig,m in machines:
        if category(m)!="random4":
            raise AssertionError("TRAIN_STRUCTURE_NOT_RANDOM4")
        checks=m.checks()
        if not fully_identifiable(checks,m.size):
            impossible.append(sig)
            continue
        by_name={c.name:c for c in checks}
        for hidden in range(m.size):
            # Existing genuine uniform exploratory simulator, no optimal labels.
            episode=previous.trajectory(m,hidden,"OFF",[0.0]*9,rng)
            first=episode["steps"][0]
            a=by_name[episode["first_probe"]]
            observation=tuple(first["observable_outputs"])
            if observation!=a.values[hidden]:
                raise AssertionError("SIMULATOR_OUTPUT_MISMATCH")
            after=tuple(i for i in range(m.size)
                        if a.values[i]==observation)
            if list(after)!=first["hypotheses_after"]:
                raise AssertionError("POSTERIOR_MISMATCH")
            total=episode["total_cost"]
            if total!=sum(st["probe_cost"] for st in episode["steps"]):
                raise AssertionError("EPISODE_COST_MISMATCH")
            cost_after=total-a.cost
            if cost_after<0:
                raise AssertionError("NEGATIVE_CONTINUATION")
            records.append({
                "machine_signature":sig,
                "true_initial_for_audit_only":hidden,
                "machine":m,
                "first_action":a.name,
                "first_cost":a.cost,
                "first_observation":list(observation),
                "before":tuple(range(m.size)),
                "after":after,
                "total_observed_cost":total,
                "observed_continuation_cost":cost_after,
                "trajectory":episode["steps"],
            })
            probe_cost+=total
            actual_probe_count+=len(episode["steps"])
    return {
        "records":records,
        "impossible":impossible,
        "episodes":len(records),
        "real_probe_count":actual_probe_count,
        "real_probe_cost":probe_cost,
    }


def train_shared(shared):
    """Both receive exactly the SAME raw episode once, in identical order."""
    baseline=LinearPolicy.blank()
    structured=BeliefValue.blank()
    memory=[]
    audit=[]
    for record in shared["records"]:
        m=record["machine"]
        checks=m.checks()
        byname={c.name:c for c in checks}
        a=byname[record["first_action"]]
        total_features=list(features(record["before"],a))
        continuation_features=successor_features(record["after"],checks,m.size)
        total=record["total_observed_cost"]
        residual=record["observed_continuation_cost"]
        # Exactly one parameter update per model per *same* observed episode.
        baseline.learn([{"features":total_features,
                         "observed_return_to_go":total}])
        structured.learn_one(continuation_features,residual)
        memory.append({
            "features":total_features,
            "observed_return_to_go":total,
        })
        audit.append({
            "machine_signature":record["machine_signature"],
            "first_probe":a.name,
            "real_first_response":record["first_observation"],
            "first_observed_cost":a.cost,
            "real_total_cost":total,
            "observed_cost_after_first":residual,
            "successor_belief":list(record["after"]),
            "trained_with_optimal_oracle":False,
            "TOTAL9_weights_hash":digest(baseline.weights),
            "BELIEF_VALUE_weights_hash":digest(structured.weights),
        })
    if not shared["episodes"]:
        raise AssertionError("EMPTY_SHARED_TRAIN")
    if not (baseline.updates==structured.updates==len(memory)==
            shared["episodes"]):
        raise AssertionError("UNMATCHED_EXAMPLES_OR_SGD_UPDATES")
    return {
        "baseline":baseline,"structured":structured,
        "memory":memory,
        "audit":audit,
        "audit_sha256":digest(audit),
    }


def run_value_episode(machine,hidden,model):
    checks=machine.checks()
    group=tuple(range(machine.size))
    total=0
    traces=[]
    while len(group)>1:
        action=value_action(group,checks,model)
        if action is None:
            return {"success":False,"cost":total,"trace":traces}
        observed=action.values[hidden]
        new=tuple(s for s in group if action.values[s]==observed)
        if not new or len(new)>=len(group):
            raise AssertionError("VALUE_POLICY_BELIEF_ERROR")
        total+=action.cost
        traces.append({
            "probe":action.name,
            "observation":list(observed),
            "cost":action.cost,
            "belief_before":list(group),
            "belief_after":list(new),
        })
        group=new
    if group!=(hidden,):
        raise AssertionError("FALSE_IDENTIFICATION")
    return {"success":True,"cost":total,"trace":traces}


def evaluate(cohort,trained):
    """Only evaluation may use exact PR76. Four or five hidden starts."""
    baseline=trained["baseline"]
    value=trained["structured"]
    memory=trained["memory"]
    names=("FIXED","MEMORY","TOTAL9","BELIEF_VALUE")
    rows=[]
    eligible=0
    for sig,m in cohort:
        checks=m.checks()
        oracle=solve(tuple(range(m.size)),checks)
        admissible=fully_identifiable(checks,m.size)
        if admissible!=(oracle["adaptive"] is not None):
            raise AssertionError("ORACLE_IDENTIFIABILITY_MISMATCH")
        row={
            "signature":sig,"size":m.size,
            "identifiable":admissible,
            "oracle_minimax_worst_cost":oracle["adaptive"],"arms":{},
        }
        if admissible:
            eligible+=1
            for arm in names:
                outcomes=[]
                for hidden in range(m.size):
                    if arm=="BELIEF_VALUE":
                        ep=run_value_episode(m,hidden,value)
                    elif arm=="TOTAL9":
                        ep=run_episode(m,checks,hidden,"learned",weights=baseline.weights,log=False)
                    elif arm=="MEMORY":
                        ep=run_episode(m,checks,hidden,"memory",memory=memory,log=False)
                    else:
                        ep=run_episode(m,checks,hidden,"fixed",log=False)
                    if not ep["success"]:
                        raise AssertionError("INADMISSIBLE_ABSTENTION")
                    outcomes.append(ep.get("cost",ep.get("total_cost")))
                if any(not isinstance(x,int) for x in outcomes):
                    raise AssertionError("MISSING_COST")
                worst=max(outcomes)
                if worst<oracle["adaptive"]:
                    raise AssertionError("BEATS_EXACT_ORACLE")
                row["arms"][arm]={
                    "mean_cost":sum(outcomes)/m.size,
                    "worst_cost":worst,
                    "worst_regret_to_oracle":worst-oracle["adaptive"],
                    "state_costs":outcomes,
                }
        else:
            row["status"]="JUSTIFIED_ABSTENTION_UNIDENTIFIABLE"
        rows.append(row)
    means={}
    if eligible:
        for arm in names:
            filtered=[r["arms"][arm] for r in rows if r["identifiable"]]
            means[arm]={
                "mean_cost":sum(item["mean_cost"] for item in filtered)/eligible,
                "mean_worst":sum(item["worst_cost"] for item in filtered)/eligible,
                "mean_worst_regret":sum(
                    item["worst_regret_to_oracle"] for item in filtered)/eligible,
            }
    return {
        "total":len(cohort),"eligible":eligible,
        "impossible":len(cohort)-eligible,
        "means":means,"rows":rows,
    }


def summarize(repetitions,cohort_name):
    evaluations=[rep["evaluations"][cohort_name] for rep in repetitions]
    eligible=evaluations[0]["eligible"]
    total=evaluations[0]["total"]
    if any(x["eligible"]!=eligible or x["total"]!=total for x in evaluations):
        raise AssertionError("UNEQUAL_EVALUATION_CASES")
    if not eligible:
        return {"total":total,"eligible":0,"impossible":total,
                "status":"INSUFFICIENT_IDENTIFIABLE_CASES"}
    keys=("FIXED","MEMORY","TOTAL9","BELIEF_VALUE")
    mean={
        arm:sum(ev["means"][arm]["mean_cost"] for ev in evaluations)/len(evaluations)
        for arm in keys
    }
    differences={
        f"BELIEF_VALUE_minus_{arm}":mean["BELIEF_VALUE"]-mean[arm]
        for arm in ("TOTAL9","FIXED","MEMORY")
    }
    per_seed=[{
        "seed":rep["seed"],
        "BELIEF_VALUE_minus_TOTAL9":ev["means"]["BELIEF_VALUE"]["mean_cost"]-
                                    ev["means"]["TOTAL9"]["mean_cost"],
        "BELIEF_VALUE_minus_FIXED":ev["means"]["BELIEF_VALUE"]["mean_cost"]-
                                   ev["means"]["FIXED"]["mean_cost"],
        "BELIEF_VALUE_minus_MEMORY":ev["means"]["BELIEF_VALUE"]["mean_cost"]-
                                    ev["means"]["MEMORY"]["mean_cost"],
    } for rep,ev in zip(repetitions,evaluations)]
    counters={
        "improved_vs_TOTAL9":sum(
            r["arms"]["BELIEF_VALUE"]["mean_cost"] <
            r["arms"]["TOTAL9"]["mean_cost"]
            for ev in evaluations for r in ev["rows"] if r["identifiable"]),
        "worse_vs_TOTAL9":sum(
            r["arms"]["BELIEF_VALUE"]["mean_cost"] >
            r["arms"]["TOTAL9"]["mean_cost"]
            for ev in evaluations for r in ev["rows"] if r["identifiable"]),
    }
    return {
        "total":total,"eligible":eligible,"impossible":total-eligible,
        "mean_cost":mean,"differences":differences,
        "per_seed_differences":per_seed,"machine_counters":counters,
    }


def conduct():
    all_machines=cohorts()
    repetitions=[]
    for seed in SEEDS:
        shared=collect(all_machines["train_random4"]["machines"],seed)
        trained=train_shared(shared)
        raw_stream=[{
            k:v for k,v in record.items() if k!="machine"
        } for record in shared["records"]]
        repetitions.append({
            "seed":seed,
            "shared_training":{
                "episodes":shared["episodes"],
                "impossible_signatures":shared["impossible"],
                "probe_count":shared["real_probe_count"],
                "charged_probe_cost":shared["real_probe_cost"],
                "raw_trajectories":raw_stream,
                "raw_stream_sha256":digest(raw_stream),
            },
            "models":{
                "TOTAL9":{
                    "initial_weights_sha256":digest([0.0]*9),
                    "final_weights":trained["baseline"].weights,
                    "final_weights_sha256":digest(trained["baseline"].weights),
                    "updates":trained["baseline"].updates,
                },
                "BELIEF_VALUE":{
                    "initial_weights_sha256":digest([0.0]*VALUE_DIMS),
                    "final_weights":trained["structured"].weights,
                    "final_weights_sha256":digest(trained["structured"].weights),
                    "updates":trained["structured"].updates,
                },
            },
            "memory":{
                "count":len(trained["memory"]),
                "sha256":digest(trained["memory"]),
            },
            "learning_audit":{
                "sha256":trained["audit_sha256"],
                "rows":trained["audit"],
            },
            "evaluations":{
                name:evaluate(all_machines[name]["machines"],trained)
                for name in ("eval_control4",*GROUPS_OF_INTEREST)
            },
        })
    aggregates={
        name:summarize(repetitions,name)
        for name in ("eval_control4",*GROUPS_OF_INTEREST)
    }
    holdouts=[aggregates[name] for name in GROUPS_OF_INTEREST]
    if any(h["eligible"]==0 for h in holdouts):
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
        passed=0
    else:
        passed=sum(
            all(h["differences"][f"BELIEF_VALUE_minus_{arm}"]<0
                for arm in ("TOTAL9","FIXED","MEMORY"))
            for h in holdouts
        )
        status=("DESCRIPTIVE_BELIEF_VALUE_TRANSFER" if passed==2
                else "NO_BELIEF_VALUE_STRONG_TRANSFER")

    manifests={
        name:{
            "seed":row["seed"],"family":row["family"],
            "count":row["count"],"attempts":row["attempts"],
            "isomorphism_duplicates":row["isomorphism_duplicates"],
            "signatures":[s for s,_ in row["machines"]],
            "signatures_sha256":digest([s for s,_ in row["machines"]]),
        } for name,row in all_machines.items()
    }
    result={
        "experiment":EXPERIMENT,"prereg_commit":PREREG_SHA,
        "status":status,"strong_family_gates_passed":passed,
        "seeds":list(SEEDS),
        "shared_experience_between_learners":True,
        "same_observed_episode_labels_and_costs":True,
        "same_one_update_per_episode":True,
        "oracle_used_during_training":False,
        "oracle_used_during_evaluation":True,
        "same_training_trajectories_for_learners":True,
        "memory_training_data_same_stream":True,
        "information_content_per_training_episode_equal":True,
        "paid_api_calls":0,"language_model_trained":False,
        "main_modified":False,"scientific_generalization_proven":False,
        "splits":manifests,"repetitions":repetitions,"family_results":aggregates,
        "limitations":[
            "Known Mealy model, only its initial state is hidden.",
            "A fixed menu of six reset probes; no test outside this finite menu.",
            "Both models see the identical logged trajectories, not their own policies' rollouts.",
            "Comparison changes representation, prediction target and inductive bias together.",
            "Value prediction uses exact partitions known to all, no optimal-action oracle.",
            "Single OOD holdout of five-state structures; 3 seeds share the same test machines.",
            "Equal data and observation costs, but not necessarily equal inference CPU.",
            "One favorable holdout cannot establish autonomous self-improvement or generalization.",
        ],
    }
    if any(
        rep["shared_training"]["episodes"]!=rep["models"]["TOTAL9"]["updates"]
        or rep["shared_training"]["episodes"]!=rep["models"]["BELIEF_VALUE"]["updates"]
        or rep["shared_training"]["episodes"]!=rep["memory"]["count"]
        for rep in repetitions
    ):
        raise AssertionError("LABELS_OR_UPDATES_NOT_MATCHED")
    all_sigs=[s for item in manifests.values() for s in item["signatures"]]
    if len(all_sigs)!=len(set(all_sigs)):
        raise AssertionError("CANONICAL_MACHINE_REUSE")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    result=conduct()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    a.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,
        "status":result["status"],
        "passed_structural_family_checks":result["strong_family_gates_passed"],
        "eligible":{
            n:result["family_results"][n]["eligible"]
            for n in result["family_results"]
        },
        "deltas":{
            n:result["family_results"][n].get("differences")
            for n in GROUPS_OF_INTEREST
        },
        "same_training_updates":[
            {
                "seed":r["seed"],
                "episodes":r["shared_training"]["episodes"],
                "TOTAL9":r["models"]["TOTAL9"]["updates"],
                "BELIEF_VALUE":r["models"]["BELIEF_VALUE"]["updates"],
                "actual_spent":r["shared_training"]["charged_probe_cost"],
            } for r in result["repetitions"]
        ],
        "sha256":hashlib.sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
