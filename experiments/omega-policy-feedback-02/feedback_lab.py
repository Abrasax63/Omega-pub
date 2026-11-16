"""OMEGA-POLICY-FEEDBACK-02: on-policy vs uniform behavior feedback.

Known Mealy, hidden initial state, reset probes. No optimal-action labels.
The old PR76 exact solver is called exclusively by the evaluator (PR128).
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-plasticity-01"))
import plasticity_lab as old  # noqa: E402
from mealy_lab import digest, Check  # noqa: E402

EXPERIMENT="OMEGA-POLICY-FEEDBACK-02"
GROUPS=(
    ("train_A",9117,24),
    ("train_B",9217,24),
    ("train_Aprime",9317,16),
    ("eval_A",9417,18),
    ("eval_B",9517,18),
    ("eval_Aprime",9617,24),
)
SEEDS=(410,411,412)
CHECKPOINTS=(0,8,16)
EPSILON=0.2


def cohorts():
    """Canonical non-overlap against #127, #128 and all new partitions."""
    known=old.group_machines()
    used={sig for entry in known.values() for sig,_ in entry["machines"]}
    from mealy_lab import make_cohorts
    used.update(sig for entry in make_cohorts().values()
                for sig,_ in entry["machines"])
    result={}
    old_count=len(used)
    for name,seed,n in GROUPS:
        rng=random.Random(seed)
        machines=[]
        draws=collisions=0
        while len(machines)<n:
            draws+=1
            if draws>100000:
                raise RuntimeError("SAMPLE_COLLISION_EXHAUSTION")
            m=old.random_machine(rng)
            sig=m.signature()
            if sig in used:
                collisions+=1
                continue
            machines.append((sig,m))
            used.add(sig)
        result[name]={"seed":seed,"attempts":draws,
                      "isomorphism_collisions":collisions,"machines":machines}
    if len(used)!=old_count+sum(n for _,_,n in GROUPS):
        raise AssertionError("CROSS_COHORT_ISOMORPHISM_LEAK")
    return result


def costs(machine,phase):
    if phase in ("A","Aprime"):
        return old.checks_for(machine,old.A_COSTS)
    if phase=="B":
        return tuple(Check(c.name,sum(3 if action=="0" else 1
                                     for action in c.name),c.values)
                     for c in machine.checks())
    raise ValueError("UNKNOWN_PHASE")


def collect_one(machine,hidden,checks,policy,rng):
    """Actual trajectory. hidden is used only by simulator for the observed reply."""
    if policy not in ("OFF","ON"):
        raise ValueError("INVALID_BEHAVIOR")
    belief=tuple(range(machine.size))
    steps=[]
    total=0
    while len(belief)>1:
        available=old.choices(belief,checks)
        if not available:
            return {"success":False,"steps":steps,"total_cost":total}
        # Uniform behavior OFF. ON acts greedily by its own current cost estimate,
        # with fixed epsilon uniform exploration to retain new-action coverage.
        if policy=="OFF" or rng.random()<EPSILON:
            chosen=rng.choice(available)
        else:
            chosen=old.choose(belief,checks,"learned",
                              weights=list(getattr(rng,"_omega_weights")))
        new=tuple(s for s in belief if chosen.values[s]==chosen.values[hidden])
        if not new or len(new)>=len(belief):
            raise AssertionError("INVALID_BELIEF_TRANSITION")
        steps.append({
            "action":chosen.name,
            "cost":chosen.cost,
            "features":old.features(belief,chosen),
            "belief_before":list(belief),
            "observation":list(chosen.values[hidden]),
            "belief_after":list(new),
        })
        total+=chosen.cost
        belief=new
    if belief!=(hidden,):
        raise AssertionError("FALSE_STATE_IDENTIFICATION")
    future=0
    for step in reversed(steps):
        future+=step["cost"]
        step["observed_return_to_go"]=future
    return {"success":True,"steps":steps,"total_cost":total,
            "identified_state":belief[0]}


class BehaviorRNG:
    """Prevent passing hidden state into policy or leaking it through RNG."""
    def __init__(self,seed):
        self.random_source=random.Random(seed)
        self._omega_weights=None
    def random(self):
        return self.random_source.random()
    def choice(self,options):
        return self.random_source.choice(options)


def collect(machines,phase,seed,off_model,on_model,off_memory):
    """Both arms see same machine/state order; trajectories can differ."""
    off_rng,on_rng=seed
    checks_seen=0
    result={"phase":phase,"machines":len(machines),
            "eligible":0,"impossible":0,
            "arms":{k:{"episodes":0,"decisions":0,"probe_cost":0,
                       "records":[]} for k in ("OFF","ON")}}
    for signature,machine in machines:
        cs=costs(machine,phase)
        if not old.fully_identifiable(cs,machine.size):
            result["impossible"]+=1
            continue
        result["eligible"]+=1
        for hidden in range(machine.size):
            for arm,policy,rng in (("OFF",off_model,off_rng),
                                   ("ON",on_model,on_rng)):
                rng._omega_weights=tuple(policy.weights)
                episode=collect_one(machine,hidden,cs,arm,rng)
                if not episode["success"]:
                    raise AssertionError("FAILED_COMPLETE_DIAGNOSIS")
                examples=[{
                    "features":step["features"],
                    "observed_return_to_go":step["observed_return_to_go"],
                } for step in episode["steps"]]
                # One update after the true episode has ended. No teacher labels.
                policy.learn(examples)
                if arm=="OFF":
                    off_memory.extend(examples)
                entry=result["arms"][arm]
                entry["episodes"]+=1
                entry["decisions"]+=len(episode["steps"])
                entry["probe_cost"]+=episode["total_cost"]
                entry["records"].append({
                    "signature":signature,
                    "hidden_initial_for_audit_only":hidden,
                    "episode_cost":episode["total_cost"],
                    "steps":episode["steps"],
                    "weight_sha256_after_episode":digest(policy.weights),
                })
    for arm in ("OFF","ON"):
        entry=result["arms"][arm]
        entry["records_sha256"]=digest(entry["records"])
        if entry["episodes"]!=result["eligible"]*4:
            raise AssertionError("EPISODE_COUNT_MISMATCH")
    if result["eligible"]+result["impossible"]!=len(machines):
        raise AssertionError("COHORT_DROPPED")
    return result


def policies(off,on,memory):
    return {
        "FIXED":("fixed",None,None),
        "MEMORY":("memory",None,memory),
        "OFF":("learned",list(off.weights),None),
        "ON":("learned",list(on.weights),None),
    }


def evaluate(machines,phase,off,on,memory):
    # ONLY this function may call PR76's exact oracle through old.evaluate.
    return old.evaluate(machines,costs_dummy(phase),
                        policies(off,on,memory)) if False else _evaluate_per_machine(
                            machines,phase,policies(off,on,memory))


def _evaluate_per_machine(machines,phase,arms):
    # PR128 evaluate accepts one cost tuple for every machine. Phase B costs
    # depend on probe letters, so call its unchanged oracle/replay per machine.
    rows=[]
    eligible=0
    for signature,machine in machines:
        cs=costs(machine,phase)
        exact=old.solve(tuple(range(machine.size)),cs)
        identifiable=old.fully_identifiable(cs,machine.size)
        if identifiable!=(exact["adaptive"] is not None):
            raise AssertionError("ORACLE_IDENTIFIABILITY_CONFLICT")
        row={"signature":signature,"identifiable":identifiable,
             "oracle_worst":exact["adaptive"],"arms":{}}
        if identifiable:
            eligible+=1
            for name,(arm,weights,memory) in arms.items():
                results=[old.run_episode(machine,cs,s,arm,weights=weights,
                                         memory=memory,log=False)
                         for s in range(machine.size)]
                if not all(x["success"] for x in results):
                    raise AssertionError("INVALID_EVAL_ABSTENTION")
                costs_seen=[x["total_cost"] for x in results]
                worst=max(costs_seen)
                if worst<exact["adaptive"]:
                    raise AssertionError("IMPOSSIBLE_BEATS_ORACLE")
                row["arms"][name]={
                    "mean_cost":sum(costs_seen)/machine.size,
                    "worst_cost":worst,
                    "worst_regret":worst-exact["adaptive"],
                    "cost_per_state":costs_seen,
                }
        else:
            row["status"]="PROVEN_NOT_IDENTIFIABLE_WITH_SIX_PROBES"
        rows.append(row)
    averages={}
    if eligible:
        for name in arms:
            applicable=[r["arms"][name] for r in rows if r["identifiable"]]
            averages[name]={
                "mean_cost":sum(x["mean_cost"] for x in applicable)/eligible,
                "mean_worst_cost":sum(x["worst_cost"] for x in applicable)/eligible,
                "mean_worst_regret":sum(x["worst_regret"] for x in applicable)/eligible,
            }
    return {"total":len(machines),"eligible":eligible,
            "impossible":len(machines)-eligible,
            "mean_by_policy":averages,"rows":rows}


def difference(ev,one,two):
    if ev["eligible"]==0:
        return None
    return ev["mean_by_policy"][one]["mean_cost"]-ev["mean_by_policy"][two]["mean_cost"]


def machine_changes(first,last,policy):
    x={r["signature"]:r for r in first["rows"] if r["identifiable"]}
    y={r["signature"]:r for r in last["rows"] if r["identifiable"]}
    if x.keys()!=y.keys():
        raise AssertionError("CHECKPOINT_MACHINE_DRIFT")
    diffs=[
        y[s]["arms"][policy]["mean_cost"]-
        x[s]["arms"][policy]["mean_cost"] for s in x
    ]
    return {"changed":sum(v!=0 for v in diffs),
            "improved":sum(v<0 for v in diffs),
            "worsened":sum(v>0 for v in diffs)}


def one_seed(cohorts_data,seed):
    off=old.LinearPolicy.blank()
    on=old.LinearPolicy.blank()
    memory=[]
    off_rng=BehaviorRNG(seed)
    on_rng=BehaviorRNG(seed+10000)
    pair=(off_rng,on_rng)

    phases={}
    phases["train_A"]=collect(cohorts_data["train_A"]["machines"],
                              "A",pair,off,on,memory)
    eval_A_after_A=evaluate(cohorts_data["eval_A"]["machines"],
                            "A",off,on,memory)
    snapshot_A={"OFF":off.snapshot(),"ON":on.snapshot()}

    phases["train_B"]=collect(cohorts_data["train_B"]["machines"],
                              "B",pair,off,on,memory)
    eval_A_after_B=evaluate(cohorts_data["eval_A"]["machines"],
                            "A",off,on,memory)
    eval_B_after_B=evaluate(cohorts_data["eval_B"]["machines"],
                            "B",off,on,memory)
    snapshot_B={"OFF":off.snapshot(),"ON":on.snapshot()}

    aprime=cohorts_data["train_Aprime"]["machines"]
    checkpoints=[]
    for count in CHECKPOINTS:
        if count:
            prev=CHECKPOINTS[CHECKPOINTS.index(count)-1]
            stage=collect(aprime[prev:count],"Aprime",pair,off,on,memory)
            phases[f"train_Aprime_{prev}_{count}"]=stage
        ev=evaluate(cohorts_data["eval_Aprime"]["machines"],
                    "Aprime",off,on,memory)
        checkpoints.append({
            "after_training_machines":count,
            "evaluation":ev,
            "weight_snapshots":{"OFF":off.snapshot(),"ON":on.snapshot()},
            "memory_records":len(memory),
            "primary_ON_minus_OFF":difference(ev,"ON","OFF"),
        })

    first,last=checkpoints[0]["evaluation"],checkpoints[-1]["evaluation"]
    return {
        "seed":seed,
        "phase_logs":phases,
        "snapshots_after_A":snapshot_A,
        "snapshots_after_B":snapshot_B,
        "evaluation_A_after_A":eval_A_after_A,
        "evaluation_A_after_B":eval_A_after_B,
        "evaluation_B_after_B":eval_B_after_B,
        "checkpoints_Aprime":checkpoints,
        "retention_A_after_B_minus_A":{
            arm:difference(eval_A_after_B,arm,arm) if False
                else (eval_A_after_B["mean_by_policy"][arm]["mean_cost"]-
                      eval_A_after_A["mean_by_policy"][arm]["mean_cost"])
            for arm in ("OFF","ON")
        },
        "Aprime_change_0_to_16":{
            arm:machine_changes(first,last,arm)
            for arm in ("OFF","ON","MEMORY","FIXED")
        },
        "actual_updates":{
            "OFF":off.updates,"ON":on.updates,
        },
        "actual_training_probe_cost":{
            arm:sum(stage["arms"][arm]["probe_cost"] for stage in phases.values())
            for arm in ("OFF","ON")
        },
        "actual_training_episode_count":{
            arm:sum(stage["arms"][arm]["episodes"] for stage in phases.values())
            for arm in ("OFF","ON")
        },
    }


def conduct():
    groups=cohorts()
    outcomes=[one_seed(groups,seed) for seed in SEEDS]
    primaries=[
        checkpoint["primary_ON_minus_OFF"]
        for result in outcomes for checkpoint in result["checkpoints_Aprime"]
    ]
    if any(v is None for v in primaries):
        primary=None
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
    else:
        primary=sum(primaries)/len(primaries)
        status=("DESCRIPTIVE_ON_POLICY_ADVANTAGE" if primary<0 else
                "ON_POLICY_REGRESSION" if primary>0 else
                "NO_ON_POLICY_ADVANTAGE")
    splits={}
    for key,group in groups.items():
        sigs=[sig for sig,_ in group["machines"]]
        splits[key]={
            "seed":group["seed"],"size":len(sigs),
            "attempts":group["attempts"],
            "isomorphism_collisions":group["isomorphism_collisions"],
            "signatures":sigs,"signatures_sha256":digest(sigs),
        }
    result={
        "experiment":EXPERIMENT,
        "prereg_commit":"3a88640aa947ec7f1de829d8d601578d8eb3263d",
        "status":status,
        "primary_mean_ON_minus_OFF":primary,
        "primary_sample_points":len(primaries),
        "primary_repetitions_share_same_holdout":True,
        "environment_costs":{"A":{"0":1,"1":1},
                             "B":{"0":3,"1":1},
                             "Aprime":{"0":1,"1":1}},
        "epsilon":EPSILON,
        "learning_rate":old.LEARNING_RATE,
        "training_feedback":"observed_return_to_go_only",
        "model_type":"nine_parameter_linear_cost_regressor",
        "three_seeds":list(SEEDS),
        "splits":splits,
        "repetitions":outcomes,
        "learner_trained_on_oracle":False,
        "language_model_trained":False,
        "paid_API_calls":0,
        "main_modified":False,
        "scientific_generalization_proven":False,
        "limitations":[
            "Known Mealy transition/output table, unknown initial state only.",
            "Same machine/state training sequence, but different data trajectories.",
            "Same episode counts, different symbol costs and CPU, not equal training budgets.",
            "Three seeds share test machines; NOT independent holdouts.",
            "Oracle used in evaluation only, never to teach policy.",
            "ON on-policy epsilon-greedy with approximation, no guarantees of improvement.",
            "One fixed holdout with descriptive primary is not generalization evidence.",
        ],
    }
    if len(primaries)!=len(SEEDS)*len(CHECKPOINTS):
        raise AssertionError("PRIMARY_POINTS_MISSING")
    if not all(row["actual_updates"]["OFF"]>0
               and row["actual_updates"]["ON"]>0 for row in outcomes):
        raise AssertionError("NO_LEARNING_UPDATES")
    if not all(row["actual_training_episode_count"]["OFF"]==
               row["actual_training_episode_count"]["ON"] for row in outcomes):
        raise AssertionError("TRAIN_EPISODES_NOT_EQUAL")
    all_sig=[sig for group in splits.values() for sig in group["signatures"]]
    if len(all_sig)!=len(set(all_sig)):
        raise AssertionError("LEAKED_ISOMORPHIC_MACHINE")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,"status":result["status"],
        "primary_ON_minus_OFF":result["primary_mean_ON_minus_OFF"],
        "test_eligible":[r["checkpoints_Aprime"][0]["evaluation"]["eligible"]
                         for r in result["repetitions"]],
        "training_probe_costs":[r["actual_training_probe_cost"]
                                for r in result["repetitions"]],
        "training_updates":[r["actual_updates"] for r in result["repetitions"]],
        "report_sha256":sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
