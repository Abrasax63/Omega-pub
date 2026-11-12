
"""Verify verdicts under a global budget of one incorrect binary observation."""
from functools import cache
from itertools import combinations, product
from math import inf
from pathlib import Path
import json

from benchmark import CHECKS, CUBE, SELECTOR, Check, solve
from bounded_search import interruptible, verify_plan


def scenarios(verdicts, checks, copies):
    calls=tuple((c,k) for c in checks for k in range(copies))
    worlds=tuple(product(range(len(verdicts)),range(-1,len(calls))))
    noisy_checks=tuple(
        Check(f"{c.name}_{k+1}",c.cost,tuple(c.values[w]^(err==i) for w,err in worlds))
        for i,(c,k) in enumerate(calls)
    )
    return tuple(verdicts[w] for w,_ in worlds),noisy_checks


def fixed_oracle(verdicts,checks,copies):
    # Two binary result vectors have intersecting radius-one balls iff d <= 2.
    pairs=[(i,j) for i,j in combinations(range(len(verdicts)),2) if verdicts[i]!=verdicts[j]]
    return min(
        (sum(c.cost*k for c,k in zip(checks,counts,strict=True))
         for counts in product(range(copies+1),repeat=len(checks))
         if all(sum(k for c,k in zip(checks,counts,strict=True) if c.values[i]!=c.values[j])>=3 for i,j in pairs)),
        default=inf,
    )


def game_oracle(verdicts,checks,copies):
    """Independent game on worlds that have used zero or one error."""
    full=(1<<len(verdicts))-1
    masks=tuple(tuple(sum(1<<i for i,x in enumerate(c.values) if x==y) for y in (0,1)) for c in checks)
    by_verdict=tuple(sum(1<<i for i,x in enumerate(verdicts) if x==y) for y in (0,1))

    @cache
    def value(zero,one,remaining):
        possible=zero|one
        if not all(possible&v for v in by_verdict):
            return 0
        best=inf
        for i,left in enumerate(remaining):
            if not left:
                continue
            rest=remaining[:i]+(left-1,)+remaining[i+1:]
            costs=[]
            for mask in masks[i]:
                new_zero=zero&mask
                new_one=(one&mask)|(zero&(full^mask))
                if new_zero or new_one:
                    costs.append(value(new_zero,new_one,rest))
            best=min(best,checks[i].cost+max(costs))
        return best
    return value(full,0,(copies,)*len(checks)),value.cache_info().currsize


def evaluate(verdicts,checks,copies):
    noisy,probes=scenarios(verdicts,checks,copies)
    exact=solve(noisy,probes)
    adaptive,states=game_oracle(verdicts,checks,copies)
    fixed=fixed_oracle(verdicts,checks,copies)
    assert exact["fixed"]==(fixed if fixed<inf else None)
    assert exact["adaptive"]==(adaptive if adaptive<inf else None)
    if exact["tree"]:
        assert verify_plan(exact["tree"],noisy,probes)==adaptive
    return {"fixed":exact["fixed"],"adaptive":exact["adaptive"],"tree":exact["tree"],
            "fixed_checks":exact["fixed_checks"],"game_states":states,
            "expanded_worlds":len(noisy)}


def main():
    weighted=tuple(Check(c.name,k,c.values) for c,k in zip(CHECKS,(1,2,3),strict=True))
    parity=tuple(sum(w)%2 for w in CUBE)
    results={
        "annual_tables":evaluate(SELECTOR,CHECKS,3),
        "weighted_annual_tables":evaluate(SELECTOR,weighted,3),
        "parity":evaluate(parity,CHECKS,3),
        "annual_tables_at_most_two_calls":evaluate(SELECTOR,CHECKS,2),
    }
    assert results["annual_tables"]["fixed"]==9
    assert results["weighted_annual_tables"]["fixed"]==18
    assert results["parity"]["fixed"]==9
    assert results["annual_tables_at_most_two_calls"]["adaptive"] is None

    noisy,probes=scenarios(SELECTOR,CHECKS,3)
    exact=results["annual_tables"]["adaptive"]
    advance,impossible=interruptible(noisy,probes)
    assert impossible is None
    intervals={}
    last=(0,inf)
    for budget in (0,8,32,64,128):
        snap=advance(budget)
        lo,hi=snap["lower"],snap["upper"]
        assert last[0]<=lo<=exact<=hi<=last[1]
        assert verify_plan(snap.pop("plan"),noisy,probes)==hi
        assert snap["expanded"]<=budget
        intervals[budget]=snap
        last=(lo,hi)
    report={"error_budget":1,"results":results,"intervals_annual_tables":intervals}
    Path("finite_one_error_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"results":{k:{a:b for a,b in v.items() if a!="tree"} for k,v in results.items()},
                      "intervals_annual_tables":intervals},indent=2))


if __name__=="__main__":
    main()
