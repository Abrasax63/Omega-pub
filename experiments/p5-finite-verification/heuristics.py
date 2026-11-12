
"""Compare local check selection with the exact finite verification benchmark."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import product
from math import inf
from pathlib import Path
import json

from benchmark import CHECKS, CUBE, SELECTOR, Check, partition, solve


def policy(verdicts, checks, method):
    worlds = tuple(range(len(verdicts)))

    @cache
    def branches(group, check):
        return tuple(partition(group, [check]).values())

    def mixed_pairs(group):
        counts = Counter(verdicts[i] for i in group)
        return (len(group)**2 - sum(n*n for n in counts.values())) // 2

    @cache
    def horizon(group, remaining):
        if not mixed_pairs(group):
            return 0
        if not remaining:
            return inf
        return min(
            (check.cost + max(horizon(block, remaining-1) for block in branches(group, check))
             for check in checks if len(branches(group, check)) > 1),
            default=inf,
        )

    @cache
    def options(group):
        available = [check for check in checks if len(branches(group, check)) > 1]
        if method == "two_step" and horizon(group, 2) < inf:
            best = horizon(group, 2)
            return tuple(check for check in available
                         if check.cost + max(horizon(b, 1) for b in branches(group, check)) == best)

        def score(check):
            reduction = mixed_pairs(group) - sum(mixed_pairs(b) for b in branches(group, check))
            return Fraction(reduction, check.cost)

        best = max(map(score, available), default=None)
        return tuple(check for check in available if score(check) == best)

    @cache
    def costs(group):
        if not mixed_pairs(group):
            return 0, 0, 0
        choices = options(group)
        if not choices:
            return inf, inf, inf
        child = [
            tuple(check.cost + max(costs(b)[i] for b in branches(group, check)) for i in range(3))
            for check in choices
        ]
        # First choice fixes deterministic ties; min/max bound all tie policies.
        return child[0][0], min(c[1] for c in child), max(c[2] for c in child)

    def exact_after(check):
        return check.cost + max(
            solve(tuple(verdicts[i] for i in block),
                  tuple(Check(c.name, c.cost, tuple(c.values[i] for i in block))
                        for c in checks if c != check))["adaptive"]
            for block in branches(worlds, check)
        )

    determined = not mixed_pairs(worlds)
    normal, best_ties, worst_ties = costs(worlds)
    roots = () if determined else options(worlds)
    return dict(cost=normal, best_ties=best_ties, worst_ties=worst_ties,
                roots=[c.name for c in roots],
                root_costs={c.name:exact_after(c) for c in roots} if normal < inf else {})


def compare(verdicts, checks):
    exact = solve(verdicts, checks)
    out = {"fixed":exact["fixed"], "optimal":exact["adaptive"],
           "optimal_root":exact["tree"].get("check") if exact["tree"] else None}
    for name in ("greedy", "two_step"):
        result = policy(verdicts, checks, name)
        if exact["adaptive"] is None:
            assert result["cost"] == inf
            out[name] = None
        else:
            assert exact["adaptive"] <= result["best_ties"] <= result["cost"] <= result["worst_ties"]
            out[name] = result
    return out


def main():
    profiles = tuple(product(range(1, 4), repeat=3))
    hist = {label:{m:Counter() for m in ("greedy","two_step")} for label in ("unit","weighted_grid")}
    witnesses = {}
    for weights in profiles:
        checks = tuple(Check(c.name, cost, c.values) for c,cost in zip(CHECKS, weights, strict=True))
        for verdicts in product(range(2), repeat=8):
            row = compare(verdicts, checks)
            for method in ("greedy", "two_step"):
                data = row[method]
                for key in ("cost","best_ties","worst_ties"):
                    excess = data[key]-row["optimal"]
                    hist["weighted_grid"][method][f"{key}_gap_{excess}"] += 1
                    if weights==(1,1,1):
                        hist["unit"][method][f"{key}_gap_{excess}"] += 1
                if data["roots"] and min(data["root_costs"].values())>row["optimal"]:
                    hist["weighted_grid"][method]["all_allowed_roots_suboptimal"] += 1
                    if weights==(1,1,1):
                        hist["unit"][method]["all_allowed_roots_suboptimal"] += 1
                    if len(data["roots"])==1 and method not in witnesses:
                        witnesses[method]=dict(weights=weights,verdicts=verdicts,result=row)
    selector = compare(SELECTOR,CHECKS)
    assert selector["greedy"]["cost"]==3 and selector["two_step"]["cost"]==2
    assert all(cost==3 for cost in selector["greedy"]["root_costs"].values())
    cube5 = tuple(product(range(2),repeat=5))
    weights=(2,1,2,2,2)
    checks=tuple(Check(n,c,tuple(w[i] for w in cube5))
                 for i,(n,c) in enumerate(zip(("note","a","b","c","d"),weights,strict=True)))
    verdicts=tuple((c^d) if note else (a^b) for note,a,b,c,d in cube5)
    deeper = compare(verdicts,checks)
    assert deeper["optimal"]==6
    assert deeper["two_step"]["roots"]==["a"] and deeper["two_step"]["root_costs"]["a"]>6
    impossible = compare(tuple(w[2] for w in CUBE),CHECKS[:2])
    assert impossible["greedy"] is None and impossible["two_step"] is None
    assert hist["weighted_grid"]["two_step"]["worst_ties_gap_0"]==len(profiles)*256
    report=dict(unit_cases=256,weighted_cases=len(profiles)*256,hist=hist,
                witnesses=witnesses,selector=selector,deeper=deeper,impossible=impossible)
    Path("finite_heuristics_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
