"""P5 ROUTE-02: no-model, public synthetic verification allocation stress test.

This is an ablation of an *experimental candidate* decision layer, not
proof of general intelligence or of the existing planner P1. Every episode
has six general missions and heterogeneous verification costs. All policies
see identical public features. Only the evaluation oracle sees real faults.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from planner import plan_mission

VERSION="P5-ROUTE-02"
N_EPISODES=128
N_CASES=6
BUDGET=8
COST_PENALTY_HUNDREDTHS=20
REGIMES=("calibrated","shifted")
KINDS=("arithmetic","provenance","consistency","simulation")
PUBLIC_FIELDS={"id","mission_type","question","kind","risk_percent",
               "loss_impact","verification_cost"}
POLICIES=("none","fixed","risk_first","impact_first","ratio",
          "exact_knapsack","omega_candidate","hindsight_oracle")
STATUS="SYNTHETIC_CALIBRATION_NOT_EMPIRICAL_VALIDATION"

def _number(*parts):
    return int.from_bytes(
        sha256(("P5ROUTE02|"+"|".join(map(str,parts))).encode("utf-8")).digest()[:8],
        "big")

def episode(regime,index):
    """Returns two separate lists. Fault labels NEVER enter the public list."""
    if regime not in REGIMES or type(index) is not int or index<0:
        raise ValueError("unknown regime or episode")
    public=[]
    hidden={}
    for j in range(N_CASES):
        risk=10+_number(regime,index,j,"risk")%81
        impact=2+_number(regime,index,j,"impact")%19
        cost=1+_number(regime,index,j,"cost")%5
        kind=KINDS[_number(regime,index,j,"kind")%len(KINDS)]
        cid=f"{regime}-{index:03d}-{j:02d}"
        public.append({
            "id":cid,"mission_type":"general",
            "kind":kind,
            "question":(
                f"Un dossier {kind} comporte une conclusion contestée. "
                "Déterminer s'il faut vérifier avant de confirmer."),
            "risk_percent":risk,
            "loss_impact":impact,
            "verification_cost":cost,
        })
        threshold=risk if regime=="calibrated" else 100-risk
        hidden[cid]=_number(regime,index,j,"fault")%100 < threshold
    return public, hidden

def _validate(public):
    if not isinstance(public,list) or len(public)!=N_CASES:
        raise ValueError("invalid public candidate population")
    seen=set()
    for p in public:
        if not isinstance(p,dict) or set(p)!=PUBLIC_FIELDS:
            raise ValueError("unrecognized or private field")
        if p["mission_type"]!="general" or p["kind"] not in KINDS:
            raise ValueError("unexpected type")
        if type(p["risk_percent"]) is not int or not 0<=p["risk_percent"]<=100:
            raise ValueError("invalid public risk")
        if type(p["loss_impact"]) is not int or not 1<=p["loss_impact"]<=100:
            raise ValueError("invalid loss")
        if type(p["verification_cost"]) is not int or not 1<=p["verification_cost"]<=BUDGET:
            raise ValueError("invalid cost")
        if not isinstance(p["id"],str) or p["id"] in seen:
            raise ValueError("duplicate or invalid id")
        if not isinstance(p["question"],str) or not p["question"]:
            raise ValueError("question required")
        seen.add(p["id"])

def expected_score_hundredths(p):
    return p["risk_percent"]*p["loss_impact"] - (
        COST_PENALTY_HUNDREDTHS * p["verification_cost"])

def _best_by_enumeration(public,benefit):
    """Exhaustively enumerate every feasible subset, no learned model."""
    answer=()
    max_score=0
    ordered=sorted(public,key=lambda p:p["id"])
    for mask in range(1<<len(ordered)):
        subset=[ordered[k] for k in range(len(ordered)) if mask>>k&1]
        if sum(p["verification_cost"] for p in subset)>BUDGET:
            continue
        score=sum(benefit(p) for p in subset)
        ids=tuple(p["id"] for p in subset)
        if score>max_score or (score==max_score and ids<answer):
            max_score=score
            answer=ids
    return answer

def _best_by_dp(public):
    """Independent exact optimizer for candidate Omega wrapper (not P1)."""
    ordered=tuple(sorted(public,key=lambda p:p["id"]))
    @lru_cache(None)
    def visit(i,available):
        if i==len(ordered):
            return (0,())
        skip=visit(i+1,available)
        row=ordered[i]
        if row["verification_cost"]>available:
            return skip
        rest=visit(i+1,available-row["verification_cost"])
        choose=(expected_score_hundredths(row)+rest[0],(row["id"],)+rest[1])
        if choose[0]>skip[0] or (choose[0]==skip[0] and choose[1]<skip[1]):
            return choose
        return skip
    return visit(0,BUDGET)[1]

def _greedy(public,ranking):
    if ranking=="fixed":
        sorted_rows=sorted(public,key=lambda p:p["id"])
    elif ranking=="risk_first":
        sorted_rows=sorted(public,key=lambda p:(-p["risk_percent"],p["id"]))
    elif ranking=="impact_first":
        sorted_rows=sorted(public,key=lambda p:(-p["loss_impact"],p["id"]))
    elif ranking=="ratio":
        sorted_rows=sorted(public,key=lambda p:(
            -(expected_score_hundredths(p)/p["verification_cost"]),p["id"]))
    else:raise ValueError("unknown greedy policy")
    remaining=BUDGET
    result=[]
    for row in sorted_rows:
        if expected_score_hundredths(row)>0 and row["verification_cost"]<=remaining:
            result.append(row["id"])
            remaining-=row["verification_cost"]
    return tuple(sorted(result))

def choose(policy,public):
    """Public data ONLY. No hidden outcome is accepted by deployable policies."""
    _validate(public)
    if policy=="none":return ()
    if policy in ("fixed","risk_first","impact_first","ratio"):
        return _greedy(public,policy)
    if policy=="exact_knapsack":
        return _best_by_enumeration(public,expected_score_hundredths)
    if policy=="omega_candidate":
        # Exercise the real P1 planner (with explicit decision_context) while
        # recognizing that P1 has no tool allocation policy on its own.
        # The separate DP layer is a candidate, NOT an existing Omega feature.
        for p in public:
            plan=plan_mission({
                "question":p["question"],
                "mission_type":p["mission_type"],
                "decision_context":{
                    "blocking_uncertainty":"Conclusion contestée",
                    "verification":"Contrôle correspondant à l'hypothèse",
                    "verification_effect":"Permet de confirmer ou réfuter la conclusion",
                },
            })
            if plan["next_action"]["action"]!="verify":
                raise AssertionError("P1 did not recognize need for verification")
        return _best_by_dp(public)
    raise ValueError("oracle policy must not be called through public interface")

def _measures(public,hidden,selected):
    if set(hidden)!={p["id"] for p in public}:
        raise ValueError("different private labels and visible candidates")
    if set(selected)-set(hidden) or len(set(selected))!=len(selected):
        raise ValueError("invalid verifier allocation")
    lookup={p["id"]:p for p in public}
    cost=sum(lookup[cid]["verification_cost"] for cid in selected)
    if cost>BUDGET:raise AssertionError("budget violation")
    realized=sum((lookup[cid]["loss_impact"]*100 if hidden[cid] else 0)
                 -COST_PENALTY_HUNDREDTHS*lookup[cid]["verification_cost"]
                 for cid in selected)
    expected=sum(expected_score_hundredths(lookup[cid]) for cid in selected)
    missed=sum(p["loss_impact"] for p in public
               if hidden[p["id"]] and p["id"] not in selected)
    return {"selected":list(selected),"checks":len(selected),"cost_units":cost,
            "faults_found":sum(hidden[x] for x in selected),
            "missed_fault_impact":missed,
            "expected_net_hundredths":expected,
            "realized_net_hundredths":realized}

def run():
    results={}
    all_row_hashes=[]
    for regime in REGIMES:
        totals={name:{"episodes":0,"checks":0,"cost_units":0,"faults_found":0,
                      "missed_fault_impact":0,"expected_net_hundredths":0,
                      "realized_net_hundredths":0} for name in POLICIES}
        comparisons={name:{"wins":0,"ties":0,"losses":0} for name in POLICIES
                     if name not in ("none","omega_candidate")}
        episodes=[]
        for i in range(N_EPISODES):
            visible,hidden=episode(regime,i)
            # Callers observe only the separate, validated public values.
            selections={name:choose(name,visible) for name in POLICIES
                        if name!="hindsight_oracle"}
            selections["hindsight_oracle"]=_best_by_enumeration(
                visible,lambda p:(p["loss_impact"]*100 if hidden[p["id"]] else 0)
                -COST_PENALTY_HUNDREDTHS*p["verification_cost"])
            if selections["omega_candidate"]!=selections["exact_knapsack"]:
                raise AssertionError("candidate differs from exact standard baseline")
            scores={name:_measures(visible,hidden,ids)
                    for name,ids in selections.items()}
            episode_row={
                "index":i,
                "public_sha256":sha256(json.dumps(visible,sort_keys=True,
                    ensure_ascii=False).encode("utf-8")).hexdigest(),
                "policy_scores":scores,
                # Hidden truth is used only for evaluative outcomes, not a policy.
                "fault_count":sum(hidden.values()),
            }
            all_row_hashes.append(episode_row["public_sha256"])
            episodes.append(episode_row)
            for name,values in scores.items():
                target=totals[name]
                target["episodes"]+=1
                for key in ("checks","cost_units","faults_found",
                            "missed_fault_impact","expected_net_hundredths",
                            "realized_net_hundredths"):
                    target[key]+=values[key]
            ours=scores["omega_candidate"]["realized_net_hundredths"]
            for name in comparisons:
                theirs=scores[name]["realized_net_hundredths"]
                comparisons[name][
                    "wins" if ours>theirs else "losses" if ours<theirs else "ties"
                ]+=1
        results[regime]={"policy_totals":totals,
                          "paired_comparisons_vs_omega":comparisons,
                          "episodes":episodes}
    return {"protocol":VERSION,"status":STATUS,
            "dataset":"public_author_designed_deterministic_simulation",
            "paid_api_calls":0,"model_generations":0,
            "private_data_used":False,
            "same_mission_type":"general",
            "episodes_per_regime":N_EPISODES,
            "hypotheses_per_episode":N_CASES,
            "budget_per_episode":BUDGET,
            "loss_penalty_per_cost_unit":"0.20",
            "public_input_digest":sha256("".join(
                all_row_hashes).encode()).hexdigest(),
            "results":results,
            "limitations":[
                "Synthetic faults, perfect verification tools, exogenous risk scores",
                "Existing P1 only describes a verification, not which one to run",
                "Omega candidate is a standard exact knapsack DP wrapper",
                "Public author-designed data, not independent blinded evaluation",
                "No inference model or real scientific tasks tested",
            ]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output")
    args=parser.parse_args()
    result=run()
    if args.output:
        output=Path(args.output)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2,ensure_ascii=False,
                          sort_keys=True)+"\n",encoding="utf-8")
    summary={}
    for name,group in result["results"].items():
        summary[name]={
            p:{"realized_net":round(v["realized_net_hundredths"]/100,2),
               "checks":v["checks"],"faults_found":v["faults_found"],
               "missed_fault_impact":v["missed_fault_impact"]}
            for p,v in group["policy_totals"].items()
        }
    print("P5_ROUTE02",json.dumps({
        "status":result["status"],"episodes":N_EPISODES,
        "budget":BUDGET,"input_digest":result["public_input_digest"],
        "summary":summary},ensure_ascii=False,sort_keys=True))

if __name__=="__main__":main()
