"""Certificate-aware objective for Omega STRAT-003 (experimental adapter).

Uses Omega's pre-existing optimize_policy as the legacy comparator.
The new finite DP optimizes verified-certificate coverage - 1/20 per trial,
with failure-typed branches. This is a narrow method-selection adapter, not
another agent/memory/orchestrator. All policies are fit on TRAIN cases only.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations
import json

from action_planning_two_step import optimize_policy
from certification_methods_v01 import METHODS, cases, outcome_key, run_method, truth

COST = Fraction(1, 20)
MAX_TRIES = 2


def _certified(receipt):
    return receipt["observation"] in ("yes","no")


def training_table(training):
    return [{m: outcome_key(run_method(t,m)) for m in METHODS} for t in training]


def _fallback_method(training, excludes):
    possible = [m for m in METHODS if m not in excludes]
    if not possible:
        return None
    scored = []
    for m in possible:
        success = sum(_certified(run_method(t,m)) for t in training)
        scored.append((Fraction(success,len(training)) - COST,m))
    gain, method = sorted(scored, key=lambda item: (-item[0], item[1]))[0]
    return method if gain > 0 else None


def fit_certified(training):
    """Optimize expected certified completion; no training label/oracle used."""
    if not training:
        raise ValueError("nonempty train partition required")
    obs = training_table(training)
    indices = tuple(range(len(training)))

    @lru_cache(maxsize=None)
    def solve(state, methods, trials_left):
        if trials_left <= 0 or not methods or not state:
            return Fraction(0), {"action":"abstain"}
        best_utility = Fraction(0)
        best_policy = {"action":"abstain"}
        for method in methods:  # stable lexical tie break
            groups = defaultdict(list)
            for i in state:
                groups[obs[i][method]].append(i)
            utility = -COST
            children = {}
            remaining = tuple(x for x in methods if x != method)
            for outcome, members in sorted(groups.items()):
                mass = Fraction(len(members),len(state))
                if outcome in ("yes","no"):
                    utility += mass
                else:
                    future, node = solve(tuple(members),remaining,trials_left-1)
                    utility += mass*future
                    children[outcome]=node
            if utility > best_utility:
                best_utility=utility
                best_policy={"action":"method","method":method,
                             "on_unknown":children}
        return best_utility,best_policy

    estimate,policy=solve(indices,tuple(sorted(METHODS)),MAX_TRIES)
    return {"policy":policy, "expected_utility":str(estimate),
            "train_n":len(training), "source":"certificate_coverage_DP"}


def _run_policy(task, fitted, training):
    node = fitted["policy"]
    trace=[]
    while node.get("action") == "method" and len(trace)<MAX_TRIES:
        method=node["method"]
        if method in [r["method"] for r in trace]:
            raise AssertionError("repeated method")
        receipt=run_method(task,method)
        key=outcome_key(receipt)
        trace.append({"method":method, "outcome":key,
                      "certificate":receipt["certificate"]})
        if _certified(receipt):
            return receipt["observation"],trace
        node=node.get("on_unknown",{}).get(key)
        if node is None:
            fallback=_fallback_method(training,{r["method"] for r in trace})
            node={"action":"method","method":fallback,
                  "on_unknown":{}} if fallback else {"action":"abstain"}
    return None,trace


def best_fixed(training):
    """Independent enumeration; strong fixed subtype baseline, same objective."""
    orders=[()] + [(x,) for x in METHODS] + list(permutations(METHODS,2))
    def evaluate(order):
        correct=0
        calls=0
        for task in training:
            for method in order:
                calls+=1
                if _certified(run_method(task,method)):
                    correct+=1
                    break
        return Fraction(correct)-COST*calls
    # Prefer no method when tied, then shorter and lexical.
    return sorted(orders,key=lambda o:(-evaluate(o),len(o),o))[0]


def execute_fixed(task,order):
    trace=[]
    for method in order:
        if len(trace)>=MAX_TRIES:break
        receipt=run_method(task,method)
        trace.append({"method":method,"outcome":outcome_key(receipt),
                      "certificate":receipt["certificate"]})
        if _certified(receipt):
            return receipt["observation"],trace
    return None,trace


def fit_conditioned(training):
    """Independent two-step enumeration, strong failure-aware baseline.

    This is deliberately NOT the DP used by fit_certified().
    """
    if not training: raise ValueError("empty training")
    all_observed=training_table(training)
    best=(Fraction(0),None,{},None)   # total utility, first, branches, fallback
    for first in sorted(METHODS):
        first_results=[row[first] for row in all_observed]
        groups=defaultdict(list)
        successful=0
        for i,key in enumerate(first_results):
            if key in ("yes","no"):successful+=1
            else:groups[key].append(i)
        total=Fraction(successful)-COST*len(training)
        branches={}
        for key,indices in sorted(groups.items()):
            ranked=[]
            for second in METHODS:
                if second == first:continue
                score=Fraction(sum(all_observed[i][second] in ("yes","no")
                                   for i in indices))-COST*len(indices)
                ranked.append((score,second))
            score,second=sorted(ranked,key=lambda p:(-p[0],p[1]))[0]
            if score>0:
                branches[key]=second
                total+=score
        fallback=_fallback_method(training,{first})
        candidate=(total,first,branches,fallback)
        if total>best[0] or (total==best[0] and best[1] is not None and first<best[1]):
            best=candidate
    return {"first":best[1],"on_unknown":best[2],"fallback":best[3],
            "expected_utility":str(best[0]/len(training))}


def execute_conditioned(task,policy):
    first=policy["first"]
    if first is None:return None,[]
    receipt=run_method(task,first)
    key=outcome_key(receipt)
    trace=[{"method":first,"outcome":key,"certificate":receipt["certificate"]}]
    if _certified(receipt):return receipt["observation"],trace
    second=policy["on_unknown"].get(key,policy["fallback"])
    if second is None:return None,trace
    if second==first:raise AssertionError("repeated method")
    r2=run_method(task,second)
    trace.append({"method":second,"outcome":outcome_key(r2),
                  "certificate":r2["certificate"]})
    return (r2["observation"] if _certified(r2) else None),trace


def fit_legacy(training,label):
    """Original Omega's Bayes-risk objective with truthful TRAIN labels."""
    hypotheses=[{"id":t["id"],"weight":1,
                 "decision":"yes" if truth(t) else "no"} for t in training]
    hypotheses += [{"id":"sentinel-no","weight":1,"decision":"no"},
                   {"id":"sentinel-yes","weight":1,"decision":"yes"}]
    model={
        "case_id":label,"question":"Choose method from finite observations",
        "mission_type":"mathematical","uncertainty":"Certificate unknown",
        "hypotheses":hypotheses,
        "checks":[{
            "id":"method-"+m,"action":"verify","step":"Run "+m,
            "method":m,"cost_milli":50,"available":True,
            "observations":[run_method(t,m)["observation"] for t in training]
                           +["unknown","unknown"],
        } for m in METHODS],
    }
    return optimize_policy(model,max_depth=MAX_TRIES,
                           max_cost_milli=MAX_TRIES*50)


def execute_legacy(task,fitted):
    node=fitted["policy"]
    trace=[]
    while "check_id" in node and len(trace)<MAX_TRIES:
        m=node["check_id"].removeprefix("method-")
        if m not in METHODS or m in [r["method"] for r in trace]:
            raise AssertionError("invalid method")
        receipt=run_method(task,m)
        trace.append({"method":m,"outcome":outcome_key(receipt),
                      "certificate":receipt["certificate"]})
        if _certified(receipt):return receipt["observation"],trace
        node=node.get("branches",{}).get("unknown",{})
    return None,trace


def fit(training):
    by_kind=defaultdict(list)
    for t in training:by_kind[t["kind"]].append(t)
    return {
        "A_global":best_fixed(training),
        "B_subtype":{k:best_fixed(v) for k,v in sorted(by_kind.items())},
        "C_certificate":{k:fit_certified(v) for k,v in sorted(by_kind.items())},
        "D_conditioned":{k:fit_conditioned(v) for k,v in sorted(by_kind.items())},
        "E_original":{k:fit_legacy(v,"legacy-"+k) for k,v in sorted(by_kind.items())},
        "training":dict(by_kind),
    }


def evaluate():
    rows=cases()
    train=[t for t in rows if t["partition"]=="train"]
    holdout=[t for t in rows if t["partition"]=="test"]
    if len(train)!=24 or len(holdout)!=24:raise AssertionError("frozen partition")
    fitted=fit(train)
    summary=defaultdict(lambda:{"cases":0,"correct":0,"wrong":0,
                                "abstain":0,"calls":0})
    traces=[]
    for task in holdout:
        kind=task["kind"]
        out={
            "A_global":execute_fixed(task,fitted["A_global"]),
            "B_subtype":execute_fixed(task,fitted["B_subtype"][kind]),
            "C_certificate":_run_policy(task,fitted["C_certificate"][kind],fitted["training"][kind]),
            "D_conditioned":execute_conditioned(task,fitted["D_conditioned"][kind]),
            "E_original":execute_legacy(task,fitted["E_original"][kind]),
        }
        target="yes" if truth(task) else "no"
        for name,(answer,sequence) in out.items():
            if len(sequence)>MAX_TRIES or len({r["method"] for r in sequence})!=len(sequence):
                raise AssertionError("budget or repeat")
            verdict="abstain" if answer is None else ("correct" if answer==target else "wrong")
            s=summary[name]
            s["cases"]+=1
            s[verdict]+=1
            s["calls"]+=len(sequence)
            traces.append({"case":task["id"],"kind":kind,"domain":task["domain"],
                           "arm":name,"answer":answer,"truth":target,
                           "verdict":verdict,"trace":sequence})
    scores={}
    for name,data in sorted(summary.items()):
        score=Fraction(data["correct"])-5*data["wrong"]-COST*data["calls"]
        scores[name]={**data,"objective_score":str(score),
                      "coverage":str(Fraction(data["correct"],data["cases"]))}
    return {
        "status":"PUBLIC_CONSTRUCTED_NEW_PARAMETERS_NOT_BLIND",
        "frozen_corpus_commit":"c395e0e065f345a0d083e383c13e6fac8077ad60",
        "prereg_commit":"bb360711d8790706f55abf28bcb3db3b0eeb43f1",
        "train_cases":len(train),"test_cases":len(holdout),
        "budget":MAX_TRIES,"cost_fraction":str(COST),
        "llm_calls":0,"remote_calls_in_replay":0,
        "independent_checks":__import__("certification_methods_v01").independent_checks(),
        "policy_summary":{
            "A_global":list(fitted["A_global"]),
            "B_subtype":{k:list(v) for k,v in fitted["B_subtype"].items()},
            "C_certificate":{k:{"first":v["policy"].get("method"),
                                "expected_utility":v["expected_utility"]}
                             for k,v in fitted["C_certificate"].items()},
            "D_conditioned":{k:{"first":v["first"],
                                 "expected_utility":v["expected_utility"],
                                 "branches":v["on_unknown"]}
                             for k,v in fitted["D_conditioned"].items()},
            "E_original":{k:{"first":v["policy"].get("check_id"),
                              "expected_loss":v["expected_total_loss"]}
                          for k,v in fitted["E_original"].items()},
        },
        "scores":scores,"traces":traces,
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2,sort_keys=True))
