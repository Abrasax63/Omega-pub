
"""Interruptible minimax search for exact deterministic verification."""
from collections import Counter
from functools import cache
from fractions import Fraction
from itertools import combinations, product
from math import inf
from pathlib import Path
import json

from benchmark import CHECKS, CUBE, SELECTOR, Check, partition, solve


def interruptible(verdicts, checks):
    worlds = tuple(range(len(verdicts)))
    assert worlds and all(c.cost > 0 and len(c.values)==len(worlds) for c in checks)
    assert len({c.name for c in checks}) == len(checks)
    separating = {}
    for a,b in combinations(worlds,2):
        if verdicts[a] == verdicts[b]:
            continue
        prices = [c.cost for c in checks if c.values[a]!=c.values[b]]
        if not prices:
            return None, (a,b)
        separating[a,b] = min(prices)

    expanded = set()

    @cache
    def outcomes(group, check):
        return tuple((key[0], block) for key,block in partition(group,[check]).items())

    @cache
    def actions(group):
        return tuple((c,outcomes(group,c)) for c in checks if len(outcomes(group,c))>1)

    @cache
    def mixed(group):
        counts = Counter(verdicts[i] for i in group)
        return (len(group)**2-sum(n*n for n in counts.values()))//2

    @cache
    def lower(group):
        return max((separating.get(pair,0) for pair in combinations(group,2)), default=0)

    @cache
    def greedy(group):
        if not mixed(group):
            return 0, {"verdict":verdicts[group[0]]}
        c, blocks = max(actions(group), key=lambda action: Fraction(
            mixed(group)-sum(mixed(b) for _,b in action[1]), action[0].cost))
        children = {y:greedy(b) for y,b in blocks}
        return c.cost+max(v[0] for v in children.values()), {"check":c.name,"branches":{y:v[1] for y,v in children.items()}}

    def action_interval(action):
        check, blocks = action
        intervals = [bounds(b) for _,b in blocks]
        return tuple(check.cost + max(x[k] for x in intervals) for k in range(2))

    @cache
    def bounds(group):
        lo, hi = lower(group), greedy(group)[0]
        if group in expanded:
            vals = [action_interval(action) for action in actions(group)]
            lo = max(lo,min(x[0] for x in vals))
            hi = min(hi,min(x[1] for x in vals))
        assert lo <= hi
        return lo,hi

    def frontier(group):
        lo, hi = bounds(group)
        assert lo < hi
        if group not in expanded:
            return group
        action = min(actions(group),key=lambda a:action_interval(a)[0])
        branch_lower = max(bounds(b)[0] for _,b in action[1])
        possible = [b for _,b in action[1] if bounds(b)[1]>branch_lower]
        # A potentially improving action must have an unresolved worst branch.
        assert possible
        chosen = max(possible,key=lambda b:(bounds(b)[1], bounds(b)[1]-bounds(b)[0]))
        return frontier(chosen)

    def upper_plan(group):
        hi, plan = greedy(group)
        if group not in expanded:
            return plan
        action = min(actions(group),key=lambda a:action_interval(a)[1])
        if action_interval(action)[1]>=hi:
            return plan
        check, blocks = action
        return {"check":check.name,"branches":{y:upper_plan(b) for y,b in blocks}}

    def snapshot():
        lo,hi = bounds(worlds)
        return {"lower":lo,"upper":hi,"expanded":len(expanded),"certified":lo==hi,"plan":upper_plan(worlds)}

    def advance(limit):
        while limit is None or len(expanded)<limit:
            lo,hi = bounds(worlds)
            if lo==hi:
                break
            group=frontier(worlds)
            assert group not in expanded
            expanded.add(group)
            bounds.cache_clear()
        return snapshot()

    return advance,None


def verify_plan(plan, verdicts, checks):
    by_name={c.name:c for c in checks}
    maximum=0
    for i,expected in enumerate(verdicts):
        node,cost=plan,0
        seen=set()
        while "check" in node:
            c=by_name[node["check"]]
            assert c.name not in seen
            seen.add(c.name)
            cost+=c.cost
            node=node["branches"][c.values[i]]
        assert node["verdict"]==expected
        maximum=max(maximum,cost)
    return maximum


BUDGETS=(0,1,2,4,8,16,32,64,128)
def run(verdicts,checks):
    exact=solve(verdicts,checks)["adaptive"]
    advance, impossible=interruptible(verdicts,checks)
    if advance is None:
        a,b=impossible
        assert exact is None and verdicts[a]!=verdicts[b] and all(c.values[a]==c.values[b] for c in checks)
        return {"indistinguishable_worlds":impossible}
    previous=(0,inf)
    records={}
    for budget in (*BUDGETS,None):
        record=advance(budget)
        lo,hi=record["lower"],record["upper"]
        assert previous[0]<=lo<=exact<=hi<=previous[1]
        assert verify_plan(record.pop("plan"),verdicts,checks)==hi
        assert budget is None or record["expanded"]<=budget
        if budget is None:
            assert record["certified"]
        previous=lo,hi
        records[str(budget) if budget is not None else "complete"]=record
    return {"exact":exact,"records":records}


def selector_with_parities(width):
    cube=tuple(product(range(2),repeat=1+2*width))
    names=("note",)+tuple(f"x{i}" for i in range(2*width))
    costs=(2,1)+(2,)*(2*width-1)
    checks=tuple(Check(n,c,tuple(w[i] for w in cube)) for i,(n,c) in enumerate(zip(names,costs,strict=True)))
    verdicts=tuple(sum(w[1+width*w[0]:1+width*(w[0]+1)])%2 for w in cube)
    return verdicts,checks


def main():
    counts={str(b):0 for b in BUDGETS}
    counts["complete"]=0
    worst_gap={b:0 for b in counts}
    for weights in [(1,1,1),(1,1,2),(3,2,1)]:
        checks=tuple(Check(c.name,w,c.values) for c,w in zip(CHECKS,weights,strict=True))
        for labels in product(range(2),repeat=8):
            records=run(labels,checks)["records"]
            for budget,row in records.items():
                counts[budget]+=int(row["certified"])
                worst_gap[budget]=max(worst_gap[budget],row["upper"]-row["lower"])
    cases={
        "year_selection":run(SELECTOR,CHECKS),
        "five_checks":run(*selector_with_parities(2)),
        "seven_checks":run(*selector_with_parities(3)),
        "impossible":run(tuple(w[2] for w in CUBE),CHECKS[:2]),
    }
    assert cases["five_checks"]["exact"]==6 and cases["seven_checks"]["exact"]==8
    assert cases["five_checks"]["records"]["0"]["upper"]==9
    summary={"cube_cases":768,"certified_at_budget":counts,"worst_interval_width":worst_gap,"cases":cases}
    Path("finite_bounds_results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
