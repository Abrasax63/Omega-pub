from itertools import combinations, product
from time import perf_counter_ns
import json

from v19_amortize import check
from v19_signed import fixed, prepare, signed
from audit_v19_pivot import priority
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def reserve():
    prefix = (1, 2, 3, 0, 5, 4)
    groups = []
    for tail in product(range(6), repeat=3):
        t = prefix + tail
        forced = forced_edges(t)
        if not coherent(len(t), forced):
            continue
        strata = [[], []]
        for pair in combinations(range(len(t)), 2):
            events = event_edges(t, pair, 4)
            if len(events) != 4:
                continue
            row = t, pair, tuple(range(4)), forced, events
            if priority(row) == 0:
                strata[bool(fixed(row))].append(row)
        if min(map(len, strata)) < 2:
            continue
        a, b = strata
        order = [a[0], b[0], a[1], b[1]]
        if len(groups) % 2:
            order.reverse()
        groups.append(order)
        if len(groups) == 8:
            return groups
    raise AssertionError("insufficient reserve")


def main():
    start = perf_counter_ns()
    gs = reserve()
    e = ((0, 1, 0), (0, 1, 1), (1, 2, 0), (2, 3, 0))
    assert not signed(prepare(4, ()), e)
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(g["new_errors"] == 0 for g in guards)
    results = {n:check([g[:n] for g in gs]) for n in (1,2,4)}
    assert all(r["positives"] * 2 == r["n"] for r in results.values())
    print(json.dumps(dict(results=results,guards=guards,elapsed_ns=perf_counter_ns()-start),indent=2))


if __name__ == "__main__":
    main()
