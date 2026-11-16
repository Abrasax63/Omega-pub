"""OMEGA-ACTION-RANKING-07: exact action-level diagnosis on NEW Mealy machines.

PR132 learners and PR133 exact rational oracles are imported unchanged.
New data are evaluation only, and no model receives optimal actions.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-mean-calibration-06"))
import mean_calibration_lab as m  # unchanged exact uniform and mean oracles
from mealy_lab import digest

b=m.b  # unchanged PR132 learner / policy
EXPERIMENT="OMEGA-ACTION-RANKING-07"
PREREG="e274149fd8e42658f68b8c6320a2c39e41b2f119"
SPLITS=(
    ("eval_random4",24117,24,"random4"),
    ("eval_perm5",24118,30,"perm5"),
    ("eval_reset5",24119,30,"reset5"),
)
RESERVED=("eval_perm5","eval_reset5")
SEEDS=tuple(b.SEEDS)
EPS=1e-10
POLICIES=("MEAN_EXACT","UNIFORM_EXACT_GREEDY","FIXED","MEMORY","TOTAL9","BELIEF_VALUE")


def new_cohorts():
    """The 942 old canonical signatures include #127-#133, no post-hoc filtering."""
    old=b.cohorts()
    former=m.old_signatures(old)
    before=m.new_holdouts(old)
    used=set(former)
    used.update(sig for row in before.values()
                for sig,_ in row["machines"])
    if len(used)!=942:
        raise AssertionError(f"OLD_MACHINE_LEDGER_INVALID:{len(used)}")
    cohorts={}
    for name,seed,size,kind in SPLITS:
        rng=random.Random(seed)
        members=[]
        draws=collisions=0
        while len(members)<size:
            draws+=1
            if draws>100000:
                raise RuntimeError("EXHAUSTED_MACHINE_SIGNATURES")
            machine=b.make_machine(rng,kind)
            if b.category(machine)!=kind:
                raise AssertionError("NEW_STRUCTURE_CLASS_MISMATCH")
            signature=machine.signature()
            if signature in used:
                collisions+=1
                continue
            used.add(signature)
            members.append((signature,machine))
        cohorts[name]={
            "seed":seed,"family":kind,"count":size,
            "attempts":draws,"isomorphism_collisions":collisions,
            "machines":members,
        }
    if len(used)!=942+sum(x[2] for x in SPLITS):
        raise AssertionError("CROSS_SPLIT_MACHINE_LEAKAGE")
    return old,cohorts


def q_tables(group,oracle,value_model):
    """Calculates all candidates; PR133 oracles are EVALUATION ONLY."""
    checks=oracle.checks
    actions=oracle.actions(group)
    if not actions:
        raise ValueError("NO_INFORMATIVE_PROBE")
    n=len(group)
    result={}
    for action in actions:
        blocks=oracle.blocks(group,action)
        qstar=oracle.opt_q(group,action)
        qunif=Fraction(action.cost)+sum(
            Fraction(len(sub),n)*oracle.uniform(sub)
            for sub in blocks
        )
        qmodel=action.cost+sum(
            len(sub)/n*value_model.predict(sub,checks,oracle.n)
            for sub in blocks
        )
        result[action.name]={
            "action":action,"Q_exact_mean":qstar,
            "Q_exact_uniform_continuation":qunif,
            "Q_predicted_continuation":qmodel,
            "successors":blocks,
        }
    return result


def optimal_choice(qs,key):
    return min(qs.values(),key=lambda x:(
        x[key],x["action"].cost,x["action"].name
    ))["action"]


def rank_belief(group,oracle,value_model):
    """One reachable information state. All exact costs rational."""
    qs=q_tables(group,oracle,value_model)
    learned=b.value_action(group,oracle.checks,value_model)
    oracle_opt=oracle.optimum(group)
    oracle_action=optimal_choice(qs,"Q_exact_mean")
    uniform_action=optimal_choice(qs,"Q_exact_uniform_continuation")
    predicted_action=optimal_choice(qs,"Q_predicted_continuation")
    if learned.name!=predicted_action.name:
        raise AssertionError("LEARNED_POLICY_RANKING_REIMPLEMENTATION_MISMATCH")
    selected=qs[learned.name]
    loss=selected["Q_exact_mean"]-oracle_opt
    if loss<0:
        raise AssertionError("EXACT_LOCAL_ORACLE_UNDERCUT")
    exact_uniform_best=min(v["Q_exact_uniform_continuation"]
                           for v in qs.values())
    # A learned action is genuinely misranked only if not tied for best
    # under the exact uniform-future surrogate.
    approximation_disagreement=(
        selected["Q_exact_uniform_continuation"]>exact_uniform_best
    )
    target_mismatch=(
        qs[uniform_action.name]["Q_exact_mean"]>oracle_opt
    )
    strict_alternatives=sorted({
        v["Q_exact_mean"]-oracle_opt for v in qs.values()
        if v["Q_exact_mean"]>oracle_opt
    })
    margin=strict_alternatives[0] if strict_alternatives else Fraction(0)
    actions=[]
    for value in sorted(qs.values(),key=lambda r:r["action"].name):
        act=value["action"]
        actions.append({
            "name":act.name,
            "cost":act.cost,
            "Q_optimal_rational":m.fr(value["Q_exact_mean"]),
            "Q_uniform_future_rational":m.fr(value["Q_exact_uniform_continuation"]),
            "Q_learned_future_float":value["Q_predicted_continuation"],
            "Q_learned_minus_Q_uniform":(
                value["Q_predicted_continuation"]-
                float(value["Q_exact_uniform_continuation"])
            ),
            "Q_uniform_minus_Q_optimal_rational":m.fr(
                value["Q_exact_uniform_continuation"]-
                value["Q_exact_mean"]
            ),
            "successor_beliefs":[list(s) for s in value["successors"]],
        })
    return {
        "belief":list(group),
        "size":len(group),
        "candidate_count":len(actions),
        "oracle_action":oracle_action.name,
        "uniform_exact_action":uniform_action.name,
        "learned_action":learned.name,
        "oracle_best_Q_rational":m.fr(oracle_opt),
        "strict_best_vs_next_margin_rational":m.fr(margin),
        "oracle_tie_count":sum(
            v["Q_exact_mean"]==oracle_opt for v in qs.values()
        ),
        "learned_suboptimal":loss>0,
        "surrogate_target_mismatch":target_mismatch,
        "approximation_disagreement":approximation_disagreement,
        "learned_local_one_step_regret_rational":m.fr(loss),
        "exact_uniform_local_one_step_regret_rational":m.fr(
            qs[uniform_action.name]["Q_exact_mean"]-oracle_opt
        ),
        "actions":actions,
    }


def replay_uniform_exact(machine,oracle,hidden):
    """Perfect knowledge of V_uniform (diagnostic baseline, not trained)."""
    group=tuple(range(machine.size))
    spent=0
    steps=[]
    while len(group)>1:
        actions=oracle.actions(group)
        n=len(group)
        root=min(actions,key=lambda a:(
            Fraction(a.cost)+sum(
                Fraction(len(sub),n)*oracle.uniform(sub)
                for sub in oracle.blocks(group,a)
            ),
            a.cost,a.name,
        ))
        next_group=tuple(s for s in group
                         if root.values[s]==root.values[hidden])
        if not next_group or len(next_group)>=len(group):
            raise AssertionError("EXACT_UNIFORM_GREEDY_LOOP")
        spent+=root.cost
        steps.append(root.name)
        group=next_group
    if group!=(hidden,):
        raise AssertionError("EXACT_UNIFORM_GREEDY_FALSE_IDENTIFICATION")
    return spent,steps


def evaluate_machine(signature,machine,trained):
    checks=machine.checks()
    eligible=b.fully_identifiable(checks,machine.size)
    row={
        "signature":signature,"num_states":machine.size,
        "identifiable":eligible,
        "reachable_beliefs":[],"policy_scores":{},
    }
    if not eligible:
        row["status"]="JUSTIFIED_ABSTENTION_INIDENTIFIABLE"
        return row
    oracle=m.ExactMeanAndUniform(checks,machine.size)
    initial=tuple(range(machine.size))
    exact_optimum=oracle.optimum(initial)
    old_minimax=b.solve(initial,checks)["adaptive"]
    if old_minimax is None:
        raise AssertionError("NO_MINIMAX_FOR_IDENTIFIABLE")
    beliefs=oracle.reachable_beliefs()
    row["reachable_beliefs"]=[
        rank_belief(group,oracle,trained["structured"])
        for group in beliefs
    ]
    replay={}
    replay["MEAN_EXACT"]=oracle.actual_optimal_costs()
    replay["UNIFORM_EXACT_GREEDY"]=[
        replay_uniform_exact(machine,oracle,i)[0]
        for i in range(machine.size)
    ]
    replay["BELIEF_VALUE"]=[
        b.run_value_episode(machine,i,trained["structured"])["cost"]
        for i in range(machine.size)
    ]
    for key,kind in (("FIXED","fixed"),("MEMORY","memory"),
                     ("TOTAL9","learned")):
        replay[key]=[
            b.run_episode(machine,checks,i,kind,
                          weights=trained["baseline"].weights,
                          memory=trained["memory"],log=False)["total_cost"]
            for i in range(machine.size)
        ]
    for name,costs in replay.items():
        if len(costs)!=machine.size:
            raise AssertionError("MISSING_HIDDEN_STATE_REPLAY")
        mean=Fraction(sum(costs),machine.size)
        regret=mean-exact_optimum
        if regret<0:
            raise AssertionError("POLICY_BEATS_RATIONAL_MEAN_ORACLE")
        worst=max(costs)
        if worst<old_minimax:
            raise AssertionError("POLICY_BEATS_OLD_MINIMAX")
        row["policy_scores"][name]={
            "cost_by_initial":costs,
            "mean_cost_rational":m.fr(mean),
            "regret_to_exact_mean_rational":m.fr(regret),
            "worst_cost":worst,
            "worst_regret_minimax":worst-old_minimax,
        }
    row["exact_mean_optimum_rational"]=m.fr(exact_optimum)
    row["old_minimax_worst"]=old_minimax
    if row["policy_scores"]["MEAN_EXACT"]["mean_cost_rational"]["numerator"]!=(
        row["exact_mean_optimum_rational"]["numerator"]
    ) or row["policy_scores"]["MEAN_EXACT"]["mean_cost_rational"]["denominator"]!=(
        row["exact_mean_optimum_rational"]["denominator"]
    ):
        raise AssertionError("EXACT_MEAN_DP_REPLAY_DISAGREES")
    return row


def summarize_rows(rows):
    eligible=[row for row in rows if row["identifiable"]]
    summary={"total":len(rows),"eligible":len(eligible),
             "impossible":len(rows)-len(eligible)}
    if not eligible:
        return summary
    beliefs=[r for machine in eligible for r in machine["reachable_beliefs"]]
    size={}
    for n in (2,3,4,5):
        subset=[v for v in beliefs if v["size"]==n]
        if subset:
            size[str(n)]={
                "count":len(subset),
                "learned_suboptimal_count":sum(x["learned_suboptimal"] for x in subset),
                "surrogate_mismatch_count":sum(x["surrogate_target_mismatch"] for x in subset),
                "approximation_disagreement_count":sum(x["approximation_disagreement"] for x in subset),
                "local_regret_mean":sum(
                    x["learned_local_one_step_regret_rational"]["decimal"]
                    for x in subset)/len(subset),
            }
    matrix={}
    for surrogate in (False,True):
        for approximation in (False,True):
            group=[v for v in beliefs
                   if v["surrogate_target_mismatch"]==surrogate
                   and v["approximation_disagreement"]==approximation]
            key=f"surrogate={int(surrogate)},approximation={int(approximation)}"
            local=sum((
                Fraction(x["learned_local_one_step_regret_rational"]["numerator"],
                         x["learned_local_one_step_regret_rational"]["denominator"])
                for x in group
            ),Fraction(0))
            matrix[key]={
                "beliefs":len(group),
                "learned_suboptimal_count":sum(v["learned_suboptimal"] for v in group),
                "total_local_regret_rational":m.fr(local),
            }
    mean_costs={
        arm:sum(r["policy_scores"][arm]["mean_cost_rational"]["decimal"]
                for r in eligible)/len(eligible)
        for arm in POLICIES
    }
    mean_regrets={
        arm:sum(r["policy_scores"][arm]["regret_to_exact_mean_rational"]["decimal"]
                for r in eligible)/len(eligible)
        for arm in POLICIES
    }
    denom=len(beliefs)
    summary.update({
        "reachable_nontrivial_beliefs":denom,
        "learned_suboptimal_beliefs":sum(v["learned_suboptimal"] for v in beliefs),
        "learned_suboptimal_rate":sum(v["learned_suboptimal"] for v in beliefs)/denom,
        "surrogate_mismatch_beliefs":sum(v["surrogate_target_mismatch"] for v in beliefs),
        "surrogate_mismatch_rate":sum(v["surrogate_target_mismatch"] for v in beliefs)/denom,
        "approximation_disagreement_beliefs":sum(v["approximation_disagreement"] for v in beliefs),
        "approximation_disagreement_rate":sum(v["approximation_disagreement"] for v in beliefs)/denom,
        "mean_local_regret":sum(
            v["learned_local_one_step_regret_rational"]["decimal"]
            for v in beliefs)/denom,
        "by_belief_size":size,
        "surrogate_x_approximation_matrix":matrix,
        "policy_mean_cost":mean_costs,
        "policy_mean_regret_to_oracle":mean_regrets,
    })
    return summary


def summarize_repetitions(repetitions,name):
    sample=[rep["evaluations"][name]["summary"] for rep in repetitions]
    if any(r["total"]!=sample[0]["total"] or
           r["eligible"]!=sample[0]["eligible"] for r in sample):
        raise AssertionError("EVALUATION_COHORT_CHANGED_BETWEEN_SEEDS")
    n=sum(s.get("reachable_nontrivial_beliefs",0) for s in sample)
    if not n:
        return {"total":sample[0]["total"],"eligible":sample[0]["eligible"],
                "impossible":sample[0]["impossible"]}
    keys=("learned_suboptimal_beliefs","surrogate_mismatch_beliefs",
          "approximation_disagreement_beliefs")
    totals={key:sum(s[key] for s in sample) for key in keys}
    result={
        "total":sample[0]["total"],
        "eligible":sample[0]["eligible"],
        "impossible":sample[0]["impossible"],
        "beliefs_with_seed_repeats":n,
        **{key:totals[key] for key in keys},
        "learned_suboptimal_rate":totals[keys[0]]/n,
        "surrogate_mismatch_rate":totals[keys[1]]/n,
        "approximation_disagreement_rate":totals[keys[2]]/n,
        "surrogate_unique_beliefs":sample[0]["surrogate_mismatch_beliefs"],
        "unique_beliefs":sample[0]["reachable_nontrivial_beliefs"],
        "mean_local_regret":sum(s["mean_local_regret"] for s in sample)/len(sample),
        "policy_mean_cost":{
            arm:sum(s["policy_mean_cost"][arm] for s in sample)/len(sample)
            for arm in POLICIES
        },
        "policy_mean_regret":{
            arm:sum(s["policy_mean_regret_to_oracle"][arm] for s in sample)/len(sample)
            for arm in POLICIES
        },
    }
    return result


def conduct():
    old,cohorts=new_cohorts()
    repetitions=[]
    for seed in SEEDS:
        shared=b.collect(old["train_random4"]["machines"],seed)
        trained=b.train_shared(shared)
        initial_fingerprints={
            "TOTAL9":digest(trained["baseline"].weights),
            "BELIEF_VALUE":digest(trained["structured"].weights),
            "MEMORY":digest(trained["memory"]),
        }
        evaluations={}
        for name,*_ in SPLITS:
            rows=[
                evaluate_machine(sig,machine,trained)
                for sig,machine in cohorts[name]["machines"]
            ]
            evaluations[name]={
                "summary":summarize_rows(rows),"rows":rows
            }
        after={
            "TOTAL9":digest(trained["baseline"].weights),
            "BELIEF_VALUE":digest(trained["structured"].weights),
            "MEMORY":digest(trained["memory"]),
        }
        if initial_fingerprints!=after:
            raise AssertionError("EVALUATION_LEAK_INTO_TRAINED_MODEL")
        if not (trained["baseline"].updates==
                trained["structured"].updates==shared["episodes"]):
            raise AssertionError("ORIGINAL_TRAINING_LABEL_COUNT_DRIFT")
        repetitions.append({
            "seed":seed,
            "training_observed_episodes":shared["episodes"],
            "training_probe_cost":shared["real_probe_cost"],
            "training_fingerprints_before":initial_fingerprints,
            "training_fingerprints_after":after,
            "evaluations":evaluations,
        })
    aggregates={
        name:summarize_repetitions(repetitions,name)
        for name,*_ in SPLITS
    }
    if any(aggregates[name]["eligible"]==0 for name in RESERVED):
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
        families_mismatch=0
    else:
        families_mismatch=sum(
            aggregates[name]["surrogate_unique_beliefs"]>0 for name in RESERVED
        )
        status=("TARGET_MISMATCH_OBSERVED_BOTH" if families_mismatch==2
                else "TARGET_MISMATCH_OBSERVED_ONE" if families_mismatch==1
                else "TARGET_MISMATCH_NOT_OBSERVED")
    manifests={
        name:{
            "seed":data["seed"],"kind":data["family"],
            "count":data["count"],"attempts":data["attempts"],
            "isomorphism_collisions":data["isomorphism_collisions"],
            "signatures":[s for s,_ in data["machines"]],
            "signatures_sha256":digest([s for s,_ in data["machines"]]),
        } for name,data in cohorts.items()
    }
    report={
        "experiment":EXPERIMENT,
        "prereg_commit":PREREG,
        "status":status,
        "structural_families_with_exact_surrogate_mismatch":families_mismatch,
        "training_seeds":list(SEEDS),
        "test_shares_machines_across_seeds":True,
        "evaluation_weights_unchanged":True,
        "all_oracles_evaluation_only":True,
        "original_PR132_training_unchanged":True,
        "known_Mealy_machine_hidden_initial_only":True,
        "exact_average_cost_oracle_rational":True,
        "no_claim_of_generalization":True,
        "paid_api_calls":0,
        "main_modified":False,
        "language_model_trained":False,
        "new_split_manifests":manifests,
        "repetitions":repetitions,
        "aggregate":aggregates,
        "limitations":[
            "Uniform future is a different prediction target from optimal future.",
            "Exact local Q*(S,a)-V*(S) assumes optimal decisions after this action.",
            "Local cost regret is not the total cost of an executing approximate policy.",
            "Subsets are equally weighted per machine, not by visitation probability.",
            "Three behavior seeds share the same machine holdout.",
            "An approximate predictor can disagree with a uniform-target policy yet choose an optimal action.",
            "Two diagnostic flags can overlap; neither establishes a unique causal mechanism.",
            "The finite known-Mealy six-probe setting is not model learning or LLM self-improvement.",
        ],
    }
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,
        "status":result["status"],
        "surrogate_mismatch_families":result["structural_families_with_exact_surrogate_mismatch"],
        "metrics":{
            name:{
                "eligible":result["aggregate"][name]["eligible"],
                "beliefs":result["aggregate"][name].get("beliefs_with_seed_repeats"),
                "unique_beliefs":result["aggregate"][name].get("unique_beliefs"),
                "learned_suboptimal_rate":result["aggregate"][name].get("learned_suboptimal_rate"),
                "surrogate_mismatch_rate":result["aggregate"][name].get("surrogate_mismatch_rate"),
                "approximation_disagreement_rate":result["aggregate"][name].get("approximation_disagreement_rate"),
                "policy_mean_cost":result["aggregate"][name].get("policy_mean_cost"),
            } for name in result["aggregate"]
        },
        "report_sha256":sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
