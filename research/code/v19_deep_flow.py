"""Non-stratified comparison on two families with a deep attached tree."""
import json
from itertools import combinations, product
from time import perf_counter

from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_prevalence import compare_arms
from v19_raw_screen import guarded, raw_reject


def evaluate(base):
    q = len(base)
    rows = []
    maps = 0
    for anchor, leaf in product(range(4), range(q+3)):
        t = (*base, anchor, q, q+1, leaf)
        forced = forced_edges(t)
        if not coherent(len(t), forced):
            continue
        maps += 1
        for pair in combinations(range(len(t)), 2):
            events = event_edges(t, pair, 4)
            if len(events) == 4:
                rows.append((t, pair, tuple(range(4)), forced, events))
    return dict(maps=maps, raw_rejections=sum(raw_reject(r[4]) for r in rows),
                **compare_arms(rows, passes=16))


def main():
    start = perf_counter()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    adverse = (tuple(range(4)), None, tuple(range(4)), (),
               ((0,1,0),(0,1,1),(2,3,0),(3,0,0)))
    assert raw_reject(adverse[4]) and not certify(adverse) and not guarded(adverse)
    guard = [compare([witness]), compare(family())]
    assert all(g["new_errors"] == 0 for g in guard)
    results = {"transposition": evaluate((1,2,3,0,5,4)),
               "fixed_point": evaluate((1,2,3,0,4))}
    print(json.dumps(dict(results=results, guard=guard, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
