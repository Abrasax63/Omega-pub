
"""Exact worst-case cost of deciding a verdict in a finite set of worlds."""
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from math import inf
from pathlib import Path
import json
import sys


@dataclass(frozen=True)
class Check:
    name: str
    cost: int
    values: tuple


def partition(worlds, checks):
    groups = {}
    for i in worlds:
        key = tuple(check.values[i] for check in checks)
        groups.setdefault(key, []).append(i)
    return {key: tuple(group) for key, group in groups.items()}


def solve(verdicts, checks):
    worlds = tuple(range(len(verdicts)))
    assert worlds and len({c.name for c in checks}) == len(checks)
    assert all(c.cost > 0 and len(c.values) == len(worlds) for c in checks)

    def decided(group):
        return len({verdicts[i] for i in group}) == 1

    @cache
    def adaptive(group):
        if decided(group):
            return 0, {"verdict": verdicts[group[0]]}
        cost, tree = inf, None
        for check in checks:
            blocks = partition(group, [check])
            if len(blocks) <= 1:
                continue
            children = {key[0]: adaptive(block) for key, block in blocks.items()}
            candidate = check.cost + max(child[0] for child in children.values())
            if candidate < cost:
                cost = candidate
                tree = {"check": check.name, "branches": {out: child[1] for out, child in children.items()}}
        return cost, tree

    fixed = min(
        (sum(c.cost for c in subset), tuple(c.name for c in subset))
        for size in range(len(checks) + 1)
        for subset in combinations(checks, size)
        if all(decided(group) for group in partition(worlds, subset).values())
    ) if all(decided(group) for group in partition(worlds, checks).values()) else (inf, None)
    adaptive_cost, tree = adaptive(worlds)
    if tree is not None:
        by_name = {c.name: c for c in checks}
        observed = []
        for i, expected in enumerate(verdicts):
            node, spent = tree, 0
            while "check" in node:
                check = by_name[node["check"]]
                spent += check.cost
                node = node["branches"][check.values[i]]
            assert node["verdict"] == expected
            observed.append(spent)
        assert max(observed) == adaptive_cost
    else:
        assert fixed[0] == inf
    assert adaptive_cost <= fixed[0]
    return {"fixed": None if fixed[0] == inf else fixed[0], "adaptive": None if adaptive_cost == inf else adaptive_cost,
            "fixed_checks": fixed[1], "tree": tree}


CUBE = tuple(product(range(2), repeat=3))
CHECKS = tuple(Check(name, 1, tuple(w[i] for w in CUBE)) for i, name in enumerate(("note", "table_A", "table_B")))
SELECTOR = tuple(b if year else a for year, a, b in CUBE)


def brute_cube(verdicts):
    """Independent depth-0/1/2 enumeration on the full Boolean cube."""
    def separates(indices, coordinates):
        labels = {}
        for i in indices:
            key = tuple(CUBE[i][j] for j in coordinates)
            if key in labels and labels[key] != verdicts[i]:
                return False
            labels[key] = verdicts[i]
        return True

    indices = range(8)
    coordinates = range(3)
    fixed = next(d for d in range(4) if any(separates(indices, xs) for xs in combinations(coordinates, d)))
    if fixed <= 1:
        return fixed, fixed
    for root in coordinates:
        if all(
            any(separates([i for i in indices if CUBE[i][root] == outcome], (other,))
                for other in coordinates if other != root)
            for outcome in range(2)
        ):
            return fixed, 2
    return fixed, 3


def planner_probe():
    from planner import MissionValidationError, plan_mission
    base = {"question": "Le chiffre correspond-il à l’année de référence ?", "mission_type": "documentary"}
    blocker = {"blocking_uncertainty": "L’année et le verdict de son tableau sont inconnus."}
    unspecified = plan_mission({**base, "decision_context": blocker})["next_action"]
    menu = {**blocker, "available_checks": ["note", "table_A", "table_B"]}
    try:
        plan_mission({**base, "decision_context": menu})
    except MissionValidationError:
        menu_rejected = True
    else:
        menu_rejected = False
    supplied = []
    for check in CHECKS:
        context = {**blocker, "verification": check.name, "verification_effect": "Consigner la valeur observée."}
        recommendation = plan_mission({**base, "decision_context": context})["next_action"]
        assert recommendation["action"] == "verify" and recommendation["next_step"] == check.name
        supplied.append(recommendation["next_step"])
    assert unspecified["action"] == "insufficient_evidence" and menu_rejected
    return {"commit": "6a7db42bb8587657edda700c245c9b7a0fd7a13b", "blocker_only": unspecified["action"],
            "menu_rejected": menu_rejected, "caller_selected_checks_returned": supplied}


def main():
    weighted = tuple(Check(c.name, cost, c.values) for c, cost in zip(CHECKS, (1, 2, 3), strict=True))
    cases = {
        "year_selection": solve(SELECTOR, CHECKS),
        "weighted_year_selection": solve(SELECTOR, weighted),
        "parity": solve(tuple(sum(w) % 2 for w in CUBE), CHECKS),
        "hidden_bit": solve(tuple(w[2] for w in CUBE), CHECKS[:2]),
        "already_decided": solve((1,) * 8, CHECKS),
    }
    assert [(v["fixed"], v["adaptive"]) for v in cases.values()] == [(3, 2), (6, 4), (3, 3), (None, None), (0, 0)]
    counts = {}
    for verdicts in product(range(2), repeat=8):
        exact = solve(verdicts, CHECKS)
        pair = (exact["fixed"], exact["adaptive"])
        assert pair == brute_cube(verdicts)
        key = "/".join(map(str, pair))
        counts[key] = counts.get(key, 0) + 1
    summary = {"cases": cases, "cube_counts_fixed_adaptive": counts, "p1": planner_probe()}
    Path("finite_verification_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
