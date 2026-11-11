"""STRAT-004: finite strategic value of non-decisional evidence.

The certificate DP and an independently enumerated conditional baseline use
identical TRAIN receipts. The legacy arm calls the existing optimize_policy.
No selector receives target payloads, target truth, or future check outcomes.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations
import json

from action_planning_two_step import optimize_policy
from intermediate_evidence_gateway import (
    ACTIONS,SPECIALISTS,cases,run_check,independent_verify,_actual_truth,
    frozen_audit,
)

COST=Fraction(1,50)
BUDGET=2


def _terminal(obs):
    return obs in ("yes","no")


def training_table(train):
    return [{a:run_check(t,a)["outcome"] for a in ACTIONS} for t in train]


def fit_certificate_dp(train):
    table=training_table(train)
    @lru_cache(maxsize=None)
    def solve(state,remaining,depth):
        best=Fraction(0)
        policy={"action":"abstain"}
        if depth==0 or not remaining:return best,policy
        for a in remaining:
            groups=defaultdict(list)
            for i in state: groups[table[i][a]].append(i)
            gain=-COST
            branches={}
            follow=tuple(m for m in remaining if m!=a)
            for obs,indices in sorted(groups.items()):
                prob=Fraction(len(indices),len(state))
                if _terminal(obs):
                    gain+=prob
                else:
                    future,child=solve(tuple(indices),follow,depth-1)
                    gain+=prob*future
                    branches[obs]=child
            if gain>best:
                best=gain
                policy={"action":"try","check_id":a,"branches":branches}
        return best,policy
    utility,policy=solve(tuple(range(len(train))),ACTIONS,BUDGET)
    return {"policy":policy,"train_value":str(utility),
            "states":solve.cache_info().currsize}


def fit_conditional_enumeration(train):
    """A separate, non-recursive exhaustive first/second action comparator.

    Unlike DP, evaluates each candidate first action, all its observed
    outcome groups, and all possible final methods explicitly.
    """
    table=training_table(train)
    n=len(train)
    best_value=Fraction(0)
    best={"action":"abstain"}
    for first in ACTIONS:
        groups=defaultdict(list)
        for i in range(n):
            groups[table[i][first]].append(i)
        total=Fraction(-n)*COST
        branches={}
        for outcome,indices in sorted(groups.items()):
            if _terminal(outcome):
                total+=len(indices)
                continue
            highest=Fraction(0)
            chosen=None
            for second in ACTIONS:
                if second==first:continue
                successes=sum(_terminal(table[i][second]) for i in indices)
                value=Fraction(successes)-COST*len(indices)
                if value>highest:
                    highest=value
                    chosen=second
            total+=highest
            branches[outcome]=(
                {"action":"try","check_id":chosen,"branches":{}}
                if chosen else {"action":"abstain"}
            )
        utility=total/n
        if utility>best_value:
            best_value=utility
            best={"action":"try","check_id":first,"branches":branches}
    return {"policy":best,"train_value":str(best_value)}


def fit_fixed(train,allowed=ACTIONS):
    table=training_table(train)
    choices=[()] + [(a,) for a in allowed] + list(permutations(allowed,2))
    def score(order):
        success=0
        calls=0
        for row in table:
            for a in order:
                calls+=1
                if _terminal(row[a]):
                    success+=1
                    break
        return Fraction(success)-COST*calls
    return sorted(choices,key=lambda order:(-score(order),len(order),order))[0]


def fit_myopic(train):
    table=training_table(train)
    ordered=sorted(ACTIONS,key=lambda a:(-
        (Fraction(sum(_terminal(row[a]) for row in table),len(table))-COST),a))
    # The second choice remains fixed independently of the first observation.
    return ordered[:2]


def fit_legacy(train):
    model={
        "case_id":"STRAT004-legacy",
        "question":"Determine the truth of an opaque evidence claim",
        "mission_type":"documentary",
        "uncertainty":"unknown sealed evidence type",
        "hypotheses":[
            {"id":t["id"],"decision":"yes" if _actual_truth(t) else "no","weight":1}
            for t in train
        ],
        "checks":[{
            "id":a,"step":"Consult "+a,"method":"evidence_method",
            "action":"verify","available":True,"cost_milli":20,
            "observations":[run_check(t,a)["outcome"] for t in train],
        } for a in ACTIONS],
    }
    return optimize_policy(model,max_depth=BUDGET,max_cost_milli=40)


def fit(train):
    if len(train)!=32:raise ValueError("32 training cases required")
    return {
        "A_fixed":fit_fixed(train),
        "B_specialists":fit_fixed(train,SPECIALISTS),
        "C_omega":fit_legacy(train),
        "D_certificate":fit_certificate_dp(train),
        "E_strong_conditional":fit_conditional_enumeration(train),
        "F_myopic":fit_myopic(train),
    }


def execute(task,policy,*,is_fixed=False,is_legacy=False):
    """Policy is compiled before test. Only action receipts control navigation."""
    node={"action":"try","check_id":policy[0],"branches":{}} if is_fixed and policy else (
        {"action":"abstain"} if is_fixed else policy)
    trace=[]
    while len(trace)<BUDGET:
        if is_fixed:
            if len(trace)>=len(policy):break
            action=policy[len(trace)]
        else:
            if is_legacy:
                action=node.get("check_id")
            else:
                action=node.get("check_id") if node.get("action")=="try" else None
            if action is None:break
        if action not in ACTIONS or action in [x["action"] for x in trace]:
            raise AssertionError("invalid or repeated action")
        receipt=run_check(task,action)
        entry={"action":action,"outcome":receipt["outcome"],
               "certificate":receipt["certificate"]}
        if not independent_verify(task,receipt):
            raise AssertionError("invalid certificate")
        trace.append(entry)
        if _terminal(receipt["outcome"]):
            return receipt["outcome"],trace
        if not is_fixed:
            node=node.get("branches",{}).get(receipt["outcome"],{})
    # A posterior 'answer' from the legacy optimizer is NOT proof.
    return None,trace


def evaluate():
    rows=cases()
    train=[x for x in rows if x["partition"]=="train"]
    test=[x for x in rows if x["partition"]=="test"]
    frozen=frozen_audit()
    if len(test)!=32:raise AssertionError("wrong frozen test")
    fitdata=fit(train)
    scores=defaultdict(lambda:{"cases":0,"correct":0,"wrong":0,"abstain":0,
                              "calls":0,"probe_calls":0})
    by_mode=defaultdict(lambda:defaultdict(lambda:{"correct":0,"abstain":0,
                                                  "wrong":0,"calls":0}))
    traces=[]
    for task in test:
        truth="yes" if _actual_truth(task) else "no"
        # Six arms receive exactly the same opaque ID and call provider.
        policies=[
            ("A_fixed",fitdata["A_fixed"],True,False),
            ("B_specialists",fitdata["B_specialists"],True,False),
            ("C_omega",fitdata["C_omega"]["policy"],False,True),
            ("D_certificate",fitdata["D_certificate"]["policy"],False,False),
            ("E_strong_conditional",fitdata["E_strong_conditional"]["policy"],False,False),
            ("F_myopic",fitdata["F_myopic"],True,False),
        ]
        for arm,policy,is_fixed,is_legacy in policies:
            decision,events=execute(task,policy,is_fixed=is_fixed,
                                    is_legacy=is_legacy)
            verdict=("abstain" if decision is None
                     else "correct" if decision==truth else "wrong")
            s=scores[arm]
            s["cases"]+=1;s[verdict]+=1;s["calls"]+=len(events)
            s["probe_calls"]+=sum(x["action"]=="probe" for x in events)
            route=run_check(task,"probe")["outcome"]
            b=by_mode[route][arm]
            b[verdict]+=1;b["calls"]+=len(events)
            traces.append({"id":task["id"],"arm":arm,"truth":truth,
                           "decision":decision,"verdict":verdict,
                           "trace":events})
    out={}
    for arm,s in sorted(scores.items()):
        objective=Fraction(s["correct"])-5*s["wrong"]-COST*s["calls"]
        out[arm]={**s,"objective":str(objective)}
    return {
        "status":"PUBLIC_CONSTRUCTED_NONBLIND_INTERMEDIATE_EVIDENCE",
        "data_commit":"dff3ceeb90d2523dba0c3146f1bbf32ec5e1de01",
        "prereg_commit":"232bc81443cbb902fabe989acfd981ceb64bb48f",
        "training":len(train),"testing":len(test),"budget":BUDGET,
        "model_calls":0,"network_calls_in_replay":0,
        "frozen_audit":frozen,
        "fit_summary":{
            "A_fixed":list(fitdata["A_fixed"]),
            "B_specialists":list(fitdata["B_specialists"]),
            "F_myopic":list(fitdata["F_myopic"]),
            "C_omega":{"first":fitdata["C_omega"]["policy"].get("check_id"),
                       "expected_loss":fitdata["C_omega"]["expected_total_loss"]},
            "D_certificate":{"first":fitdata["D_certificate"]["policy"].get("check_id"),
                             "train_value":fitdata["D_certificate"]["train_value"]},
            "E_strong_conditional":{"first":fitdata["E_strong_conditional"]["policy"].get("check_id"),
                                    "train_value":fitdata["E_strong_conditional"]["train_value"]},
        },
        "scores":out,
        "by_mode":{k:dict(v) for k,v in sorted(by_mode.items())},
        "traces":traces,
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
