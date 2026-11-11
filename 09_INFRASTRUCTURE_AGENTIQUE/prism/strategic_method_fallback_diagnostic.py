"""Exploratory POST-RESULT fix, NOT part of STRAT-002 preregistered ranking.

If the Omega finite-model policy terminates without an actual method certificate,
one more method may be selected from TRAIN-ONLY historical success frequency.
Do not reinterpret this external safeguard as a capability learned by the
original optimizer or as a prospective benchmark victory.
"""
import json
from collections import defaultdict
from strategic_methods_executable import METHODS, tasks, run_method, oracle
from strategic_method_selection import BUDGET, fit, execute_omega

def run_omega_plus_train_fallback(task,policy,train_of_kind):
    first,trace=execute_omega(task,policy)
    if first is not None or len(trace)>=BUDGET:
        return first,trace
    used={item["method"] for item in trace}
    choices=[]
    for method in METHODS:
        if method in used:
            continue
        # No oracle, test labels, or future outage conditions are used here.
        successes=sum(run_method(x,method)["observation"] in ("yes","no")
                      for x in train_of_kind)
        if successes:
            choices.append((-successes,method))
    if not choices:
        return None,trace
    method=min(choices)[1]
    response=run_method(task,method)
    trace.append({"method":method,**response})
    return (response["observation"] if response["observation"] in ("yes","no")
            else None),trace

def run():
    all_tasks=tasks()
    train=[x for x in all_tasks if x["partition"]=="train"]
    test=[x for x in all_tasks if x["partition"]=="test"]
    training_by_kind=defaultdict(list)
    for t in train:training_by_kind[t["kind"]].append(t)
    p=fit(train)
    rows=[]
    for t in test:
        old,old_trace=execute_omega(t,p["omega"][t["domain"]])
        new,new_trace=run_omega_plus_train_fallback(t,p["omega"][t["domain"]],
                                                    training_by_kind[t["kind"]])
        truth="yes" if oracle(t) else "no"
        rows.append({"id":t["id"],"domain":t["domain"],"old":old,"old_calls":len(old_trace),
                     "new":new,"new_calls":len(new_trace),"truth":truth,
                     "fallback_methods":[x["method"] for x in new_trace[len(old_trace):]]})
    return {"status":"POST_RESULT_EXPLORATION_ONLY","case_count":len(rows),
            "model_calls":0,"live_source_calls":0,"max_calls":BUDGET,
            "Omega_original_correct":sum(r["old"]==r["truth"] for r in rows),
            "Omega_original_calls":sum(r["old_calls"] for r in rows),
            "Omega_guarded_correct":sum(r["new"]==r["truth"] for r in rows),
            "Omega_guarded_calls":sum(r["new_calls"] for r in rows),
            "rows":rows}

if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2,sort_keys=True))
