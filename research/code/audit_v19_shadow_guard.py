"""Audit the V19 shadow projector against exhaustive binary assignments."""
from itertools import combinations, product
from time import perf_counter

from test_v19_locality_l_plus_1 import (
    coherent, event_edges, forced_edges, projected_shadow, visible_l_plus_1,
)


def guarded_shadow(n, constraints, cycle):
    if not coherent(n, constraints):
        return frozenset()
    return projected_shadow(n, constraints, cycle)


def exhaustive_shadow(n, constraints, cycle):
    return frozenset(
        sum(colors[v] << i for i, v in enumerate(cycle))
        for colors in product((0, 1), repeat=n)
        if all(colors[u] ^ colors[v] == p for u, v, p in constraints)
    )


def family():
    # Distinguished C5, a disjoint C2, and two leaves each pointing
    # to a different periodic state. Includes the two leaves of a P4.
    cycle = (0, 1, 2, 3, 4)
    for destinations in combinations(range(7), 2):
        T = (1, 2, 3, 4, 0, 6, 5) + destinations
        for pair in combinations(range(len(T)), 2):
            for horizon in (2, 3, 4):
                yield T, cycle, pair, horizon


def compare(cases):
    times = [0.0] * 3
    old_errors = new_errors = locality_errors = empty = projections = 0
    for T, cycle, pair, horizon in cases:
        forced = forced_edges(T)
        assert coherent(len(T), forced)
        full = forced + event_edges(T, pair, horizon)
        visible = visible_l_plus_1(T, pair, horizon, cycle)
        local = tuple(e for e in full if e[0] in visible and e[1] in visible)
        references = []
        for constraints in (full, local):
            results = []
            for i, projector in enumerate(
                (projected_shadow, guarded_shadow, exhaustive_shadow)
            ):
                start = perf_counter()
                results.append(projector(len(T), constraints, cycle))
                times[i] += perf_counter() - start
            old, new, exact = results
            old_errors += old != exact
            new_errors += new != exact
            empty += not exact
            projections += 1
            references.append(exact)
        locality_errors += references[0] != references[1]
    return dict(projections=projections, empty=empty, old_errors=old_errors,
                new_errors=new_errors, locality_errors=locality_errors,
                seconds=[round(t, 6) for t in times])


if __name__ == "__main__":
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    for name, cases in (("witness", [witness]), ("reserved", family())):
        report = compare(cases)
        print(name, report, flush=True)
        assert report["new_errors"] == 0
