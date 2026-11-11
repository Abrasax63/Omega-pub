"""Select between four executable methods using train-only evidence.

B: best precommitted fixed method order per domain; F: best per subtype.
C: the real Omega optimize_policy with certified answers only.
Public deterministic calibration, not a blind multi-agent LLM benchmark.
"""
from collections import defaultdict
from itertools import permutations
import json
from action_planning_two_step import optimize_policy
from strategic_methods_executable import METHODS, oracle, run_method, tasks

BUDGET=2
UNIT_COST_MILLI=10

def _conclusive(value):
    return value in ("yes","no")

def execute_order(task,order):
    trace=[]
    for method in order[:BUDGET]:
        if method in [x["method"] for x in trace]:
            raise AssertionError("duplicate method")
        outcome=run_method(task,method)
        trace.append({"method":method,**outcome})
        if _conclusive(outcome["observation"]):
            return outcome["observation"],trace
    return None,trace

def best_fixed(training):
    results=[]
    for order in permutations(METHODS,2):
        outcomes=[execute_order(task,order) for task in training]
        successes=sum(result==("yes" if oracle(task) else "no")
                      for task,(result,trace) in zip(training,outcomes))
        calls=sum(len(trace) for _,trace in outcomes)
        results.append((-successes,calls,order))
    return min(results)[2]

def fit_omega(training,label):
    hypotheses=[
        {"id":task["id"],"decision":"yes" if oracle(task) else "no","weight":1}
        for task in training
    ]
    # Both hypothetical unseen decisions get unknown outcome for every check.
    hypotheses.extend([{"id":"sentinel-yes","decision":"yes","weight":1},
                       {"id":"sentinel-no","decision":"no","weight":1}])
    checks=[
        {"id":"method-"+m,"step":"Run "+m,"action":"verify","method":m,
         "available":True,"cost_milli":UNIT_COST_MILLI,
         "observations":[run_method(task,m)["observation"] for task in training]
                        +["unknown","unknown"]}
        for m in METHODS
    ]
    model={"case_id":"method-"+label,"question":"Choose verifiable method",
           "mission_type":"mathematical","uncertainty":"Unknown method behavior",
           "hypotheses":hypotheses,"checks":checks}
    return optimize_policy(model,max_depth=BUDGET,max_cost_milli=BUDGET*UNIT_COST_MILLI)

def execute_omega(task,policy):
    node=policy["policy"]
    trace=[]
    while "check_id" in node:
        method=node["check_id"].removeprefix("method-")
        if method not in METHODS or method in [x["method"] for x in trace]:
            raise AssertionError("invalid or repeated method")
        if len(trace)>=BUDGET:raise AssertionError("budget breach")
        result=run_method(task,method)
        trace.append({"method":method,**result})
        if _conclusive(result["observation"]):
            return result["observation"],trace
        node=node.get("branches",{}).get(result["observation"],{})
    # No conclusion without a conclusive executable method (even if the
    # learned finite-state posterior would select a label).
    return None,trace

def fit(training):
    by_domain=defaultdict(list)
    by_kind=defaultdict(list)
    for task in training:
        by_domain[task["domain"]].append(task)
        by_kind[task["kind"]].append(task)
    return {
        "global":best_fixed(training),
        "domain":{k:best_fixed(v) for k,v in sorted(by_domain.items())},
        "kind":{k:best_fixed(v) for k,v in sorted(by_kind.items())},
        "omega":{k:fit_omega(v,k) for k,v in sorted(by_domain.items())},
        "omega_kind":{k:fit_omega(v,"kind-"+k) for k,v in sorted(by_kind.items())}
    }

def evaluate():
    all_tasks=tasks()
    training=[t for t in all_tasks if t["partition"]=="train"]
    testing=[t for t in all_tasks if t["partition"]=="test"]
    assert len(training)==len(testing)==16
    policies=fit(training)
    summary=defaultdict(lambda:{"cases":0,"correct":0,"wrong":0,
                                "abstain":0,"calls":0,"confident_wrong":0})
    by_domain=defaultdict(lambda:defaultdict(lambda:{"cases":0,"correct":0,
                                                    "wrong":0,"abstain":0,"calls":0}))
    records=[]
    for task in testing:
        answers={
            "A_global_fixed":execute_order(task,policies["global"]),
            "B_domain_fixed":execute_order(task,policies["domain"][task["domain"]]),
            "D_simple_fallback":execute_order(task,policies["domain"][task["domain"]]),
            "C_omega":execute_omega(task,policies["omega"][task["domain"]]),
            "C_omega_subtype_exploratory":execute_omega(task,policies["omega_kind"][task["kind"]]),
            "F_subtype_fixed":execute_order(task,policies["kind"][task["kind"]])
        }
        truth="yes" if oracle(task) else "no"
        for arm,(answer,trace) in answers.items():
            if len(trace)>BUDGET:raise AssertionError("budget")
            verdict="abstain" if answer is None else ("correct" if answer==truth else "wrong")
            s=summary[arm]
            s["cases"]+=1;s[verdict]+=1;s["calls"]+=len(trace)
            s["confident_wrong"]+=verdict=="wrong"
            b=by_domain[task["domain"]][arm]
            b["cases"]+=1;b[verdict]+=1;b["calls"]+=len(trace)
            records.append({"id":task["id"],"domain":task["domain"],
                            "kind":task["kind"],"arm":arm,
                            "answer":answer,"verdict":verdict,
                            "calls":len(trace),"trace":trace})
    return {
        "status":"PUBLIC_CONSTRUCTED_CALIBRATION_SYNTHETIC_OUTAGES",
        "preregistered_commit":"9e5d423f2d61d6f88c2bad7296fb58fe9c293813",
        "strong_baseline_addendum":"ea1ed4ebfa2f6e719941b8a915e9ea078f50f472",
        "training_instances":16,"test_instances":16,
        "model_calls":0,"live_source_calls_in_replay":0,"budget":BUDGET,
        "fit":{"global":list(policies["global"]),
               "domain":{k:list(v) for k,v in policies["domain"].items()},
               "kind":{k:list(v) for k,v in policies["kind"].items()},
               "omega_subtype":{k:{"first":v["policy"].get("check_id"),
                                   "loss":v["expected_total_loss"]}
                                for k,v in policies["omega_kind"].items()},
               "omega":{k:{"first":v["policy"].get("check_id"),
                           "loss":v["expected_total_loss"]}
                        for k,v in policies["omega"].items()}},
        "summary":dict(sorted(summary.items())),
        "by_domain":{k:dict(v) for k,v in sorted(by_domain.items())},
        "records":records
    }

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,sort_keys=True,ensure_ascii=False))
