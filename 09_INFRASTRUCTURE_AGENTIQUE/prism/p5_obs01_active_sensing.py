"""P5-OBS-01 — exact finite controlled observability under costly probes.

Reuses the set-of-survivors insight of Delta_h/gluing research; DOES NOT claim
that the autonomous Delta_h theorem proves active verification policies.
No LLM is queried. This is a 16-state *synthetic* counterexample to myopic VOI.
The two-ply exact Bayesian dynamic program is a standard strong control.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import log2
import argparse
import json

from planner import plan_mission

PROTOCOL="P5-OBS-01"
STATUS="EXACT_FINITE_SYNTHETIC_OBSERVABILITY_NOT_REAL_OMEGA_ADVANTAGE"
STATES=tuple((u,v,z) for u,v,z in product(range(2),range(2),range(4)))
PROBES=("U","V","Z")
COST={"U":Fraction(12,100),"V":Fraction(12,100),"Z":Fraction(5,100)}
ABSTAIN=Fraction(5,100)
CORRECT=Fraction(1)
WRONG=Fraction(-2)
DEFAULT_BUDGET=2
POLICIES=("no_probe","myopic_decision_voi","entropy_greedy",
          "fixed_u_then_v","exact_bayesian_dp","omega_observable_candidate")

def hidden_label(state):
    return state[0]^state[1]

def observation(state,probe):
    if probe not in PROBES:
        raise ValueError("unknown probe")
    return state[PROBES.index(probe)]

def survivors(belief,probe,outcome):
    """Exact filter B' = T_a(B) intersect pi_a^-1(o), with T_a=identity."""
    if not belief:
        raise ValueError("empty belief")
    if probe not in PROBES:
        raise ValueError("unknown probe")
    if type(outcome) is not int:
        raise ValueError("non-integer observed output")
    candidate=frozenset(s for s in belief if observation(s,probe)==outcome)
    if not candidate:
        raise ValueError("observation incompatible with surviving hypotheses")
    return candidate

def branches(belief,probe):
    """Possible output -> surviving states; no reference to true hidden state."""
    values=sorted({observation(s,probe) for s in belief})
    return {o:survivors(belief,probe,o) for o in values}

def terminal(belief):
    """Best decision and expected utility from a uniform finite belief."""
    if not belief:
        raise ValueError("cannot decide with an empty belief")
    n=len(belief)
    counts={bit:sum(hidden_label(x)==bit for x in belief)
            for bit in (0,1)}
    options={
        "ABSTAIN":ABSTAIN,
        "ANSWER_0":(CORRECT*counts[0]+WRONG*counts[1])/n,
        "ANSWER_1":(CORRECT*counts[1]+WRONG*counts[0])/n,
    }
    # Stable preference ABSTAIN > 0 > 1 for ties.
    action=max(("ABSTAIN","ANSWER_0","ANSWER_1"),
               key=lambda a:(options[a],-("ABSTAIN","ANSWER_0","ANSWER_1").index(a)))
    return action,options[action]

def expected_terminal_after_one(belief,probe):
    groups=branches(belief,probe)
    return -COST[probe]+sum(
        Fraction(len(b),len(belief))*terminal(b)[1] for b in groups.values())

@lru_cache(maxsize=None)
def set_dp(belief,remaining,budget):
    """Candidate Omega: exact survivor-set lookahead, standard finite DP."""
    action,value=terminal(belief)
    best=("STOP",None)
    if budget>0:
        for probe in PROBES:
            if probe not in remaining:
                continue
            groups=branches(belief,probe)
            nxt=tuple(p for p in remaining if p!=probe)
            forecast=-COST[probe]+sum(
                Fraction(len(subset),len(belief))*
                set_dp(subset,nxt,budget-1)[1]
                for subset in groups.values())
            if forecast>value:
                best=("PROBE",probe)
                value=forecast
    return best,value

def independent_tree_enumeration(belief,budget):
    """Independent two-ply exhaustive policy-tree enumeration.

    For each first probe, enumerate STOP/probe assignments on EACH observed
    first outcome; do not call the set_dp function or use its memoization.
    """
    if budget not in (0,1,2):
        raise ValueError("enumerator limited to 0..2")
    best=terminal(belief)[1]
    if budget==0:
        return best
    for first in PROBES:
        first_groups=branches(belief,first)
        outcomes=tuple(first_groups)
        remaining=[p for p in PROBES if p!=first]
        action_options=("STOP",*remaining) if budget==2 else ("STOP",)
        for policy in product(action_options,repeat=len(outcomes)):
            total=-COST[first]
            for output,next_action in zip(outcomes,policy):
                subset=first_groups[output]
                value=terminal(subset)[1]
                if next_action!="STOP":
                    second_groups=branches(subset,next_action)
                    value=-COST[next_action]+sum(
                        Fraction(len(leaf),len(subset))*terminal(leaf)[1]
                        for leaf in second_groups.values())
                total+=Fraction(len(subset),len(belief))*value
            if total>best:
                best=total
    return best

def entropy_micro(belief,probe):
    # Uniform prior; higher means more bits about full hidden microstate.
    groups=branches(belief,probe)
    n=len(belief)
    return log2(n)-sum(len(b)/n*log2(len(b)) for b in groups.values())

def policy_step(policy,belief,used,remaining):
    if not remaining or policy=="no_probe":
        return None
    if policy=="fixed_u_then_v":
        for probe in ("U","V"):
            if probe in remaining:
                return probe
        return None
    if policy=="entropy_greedy":
        return max(remaining,key=lambda p:(entropy_micro(belief,p),
                                           -PROBES.index(p)))
    if policy=="myopic_decision_voi":
        current=terminal(belief)[1]
        chosen=max(remaining,key=lambda p:(expected_terminal_after_one(belief,p),
                                           -PROBES.index(p)))
        return chosen if expected_terminal_after_one(belief,chosen)>current else None
    if policy in ("exact_bayesian_dp","omega_observable_candidate"):
        best,value=set_dp(belief,remaining,DEFAULT_BUDGET-len(used))
        return best[1] if best[0]=="PROBE" else None
    raise ValueError("unsupported policy")

def run_one(policy,secret,budget=DEFAULT_BUDGET,initial=None):
    """The controller sees ONLY belief+previous probes. Oracle used on probe."""
    if policy not in POLICIES:raise ValueError("unknown policy")
    if secret not in STATES:raise ValueError("hidden state outside model")
    belief=frozenset(STATES) if initial is None else frozenset(initial)
    if secret not in belief:raise ValueError("secret incompatible with initial evidence")
    if type(budget) is not int or not 0<=budget<=DEFAULT_BUDGET:
        raise ValueError("invalid verification budget")
    transcript=[]
    spent=Fraction(0)
    used=()
    planner_version=None
    if policy=="omega_observable_candidate":
        plan=plan_mission({
            "question":"Choisir une séquence de vérifications qui distingue "
                       "des hypothèses microscopiques pour une décision cible.",
            "mission_type":"exploratory",
            "decision_context":{
                "blocking_uncertainty":"États encore observationnellement indiscernables",
                "verification":"Sonder la fibre U ou V pour tester une hypothèse",
                "verification_effect":"Éliminer les états incompatibles avec la réponse",
            },
        })
        if plan["next_action"]["action"]!="verify":
            raise AssertionError("P1 did not plan a verification")
        planner_version=plan["planner_version"]
    while len(used)<budget:
        remaining=tuple(p for p in PROBES if p not in used)
        if policy in ("exact_bayesian_dp","omega_observable_candidate"):
            act,_=set_dp(belief,remaining,budget-len(used))
            probe=act[1] if act[0]=="PROBE" else None
        else:
            probe=policy_step(policy,belief,used,remaining)
        if probe is None:break
        if probe in used:
            raise AssertionError("duplicate paid probe")
        before=len(belief)
        # ONLY the selected action's output is disclosed after payment.
        returned=observation(secret,probe)
        belief=survivors(belief,probe,returned)
        spent+=COST[probe]
        used+= (probe,)
        transcript.append({
            "probe":probe,"observed_output":returned,
            "survivors_before":before,"survivors_after":len(belief),
            "consistent_labels_after":sorted({hidden_label(s) for s in belief}),
        })
    conclusion,expected_gain=terminal(belief)
    if conclusion=="ABSTAIN":
        realized=ABSTAIN
    else:
        guess=int(conclusion[-1])
        realized=CORRECT if guess==hidden_label(secret) else WRONG
    return {
        "policy":policy,
        "secret_evaluator_only":list(secret),
        "initial_survivors":len(STATES if initial is None else initial),
        "final_survivors":len(belief),
        "observations":transcript,
        "probes":list(used),
        "terminal_decision":conclusion,
        "true_target_evaluator_only":hidden_label(secret),
        "net_reward":realized-spent,
        "paid_cost":spent,
        "final_conditional_expected_gain":expected_gain,
        "planner_version":planner_version,
    }

def q_graph(t,pi):
    return {(pi[x],pi[t[x]]) for x in range(len(t))}

def phantom_counterexample():
    """Direct known DELTA_H minimal internal-gluing counterexample."""
    t=(0,2,2)
    pi=(0,0,1)
    q=q_graph(t,pi)
    word=(0,0,1)
    locally_possible=all((word[j],word[j+1]) in q
                         for j in range(len(word)-1))
    surviving=frozenset(x for x in range(3) if pi[x]==word[0])
    sizes=[len(surviving)]
    for observed in word[1:]:
        surviving=frozenset(t[x] for x in surviving if pi[t[x]]==observed)
        sizes.append(len(surviving))
    delta_empty=[]
    q_power=set(q)
    for h in range(1,21):
        actual={(pi[x],pi[iterate(t,x,h)]) for x in range(3)}
        delta_empty.append(q_power<=actual)
        q_power={(a,c) for a,b in q_power for b2,c in q if b==b2}
    return {"T":list(t),"pi":list(pi),"Q":sorted([list(e) for e in q]),
            "ghost_word":list(word),"locally_possible":locally_possible,
            "prefix_survivor_counts":sizes,
            "realizable":bool(surviving),
            "endpoint_delta_h_empty_h_1_through_20":all(delta_empty)}

def iterate(t,x,h):
    for _ in range(h):
        x=t[x]
    return x

def summarize():
    belief=frozenset(STATES)
    expected=set_dp(belief,PROBES,DEFAULT_BUDGET)[1]
    independent=independent_tree_enumeration(belief,DEFAULT_BUDGET)
    if expected!=independent:
        raise AssertionError("two-ply Bayesian tree enumeration disagrees with survivor DP")
    results={}
    for name in POLICIES:
        paths=[run_one(name,secret) for secret in STATES]
        mean=sum((row["net_reward"] for row in paths),Fraction(0))/len(paths)
        results[name]={
            "mean_net_exact":str(mean),
            "mean_net_float":float(mean),
            "query_counts":{
                p:sum(p in row["probes"] for row in paths) for p in PROBES},
            "mean_paid_cost":float(sum((r["paid_cost"] for r in paths),
                                       Fraction(0))/len(paths)),
            "terminal_counts":dict(sorted({
                a:sum(r["terminal_decision"]==a for r in paths)
                for a in ("ABSTAIN","ANSWER_0","ANSWER_1")}.items())),
            "all_state_runs":[{
                **{k:v for k,v in r.items()
                   if k not in ("net_reward","paid_cost","final_conditional_expected_gain")},
                "net_reward":str(r["net_reward"]),
                "paid_cost":str(r["paid_cost"]),
                "final_conditional_expected_gain":str(r["final_conditional_expected_gain"]),
            } for r in paths],
        }
    assert results["exact_bayesian_dp"]["mean_net_exact"]==str(expected)
    assert results["omega_observable_candidate"]["mean_net_exact"]==str(expected)
    assert results["fixed_u_then_v"]["mean_net_exact"]==str(expected)
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "world_size":len(STATES),
        "full_state_prior":"uniform_exact",
        "max_probes":DEFAULT_BUDGET,
        "only_chosen_probe_observed":True,
        "paid_api_calls":0,"model_generations":0,
        "bayesian_dp_value_exact":str(expected),
        "independent_policy_tree_value_exact":str(independent),
        "phantom_guardrail":phantom_counterexample(),
        "policy_results":results,
        "limitations":[
            "Exact 16-state synthetic controlled sensing, not actual model errors",
            "Classical exact POMDP/Bayesian DP ties Omega candidate by construction",
            "Fixed U then V also optimal: not a unique Omega advantage",
            "Delta_h counterexample is autonomous, XOR probes are controlled maps",
            "Uniform finite prior, perfect deterministic and known probes",
            "No nonstationarity, no imperfect evidence, no learned model of probes",
            "No scientific memory or actual multi-agent inference measured",
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=str)
    args=ap.parse_args()
    data=summarize()
    if args.output:
        with open(args.output,"w",encoding="utf-8") as file:
            json.dump(data,file,indent=2,ensure_ascii=False,sort_keys=True)
            file.write("\n")
    print("OBS01_EXACT_FINITE_RESULT "+json.dumps({
        "protocol":data["protocol"],"status":data["status"],
        "bayesian_dp_value_exact":data["bayesian_dp_value_exact"],
        "independent_policy_tree_value_exact":data["independent_policy_tree_value_exact"],
        "policy_means":{k:v["mean_net_exact"]
                        for k,v in data["policy_results"].items()},
        "phantom_guardrail":data["phantom_guardrail"],
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
