import json
from itertools import combinations, product
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family, priority
from audit_v19_shadow_guard import compare, family as guard_family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_shared import candidate
from v19_unequal import fixed


def cases(extra):
    q = 4
    prefix = (*range(1, q), 0, q+1, q)
    if extra:
        prefix += (q+2,)
    groups = [[], []]
    for a, b in product(range(len(prefix)), repeat=2):
        t = (*prefix, a, b)
        n = len(t)
        forced = forced_edges(t)
        if not coherent(n, forced):
            continue
        for pair in combinations(range(n), 2):
            events = event_edges(t, pair, 4)
            if len(events) != 4:
                continue
            row = t, pair, tuple(range(q)), forced, events
            group = groups[priority(row)]
            if len(group) < 48:
                group.append(row)
            if min(map(len, groups)) == 48:
                return groups
    raise AssertionError("insufficient strata")


def select(rows):
    return candidate if sum(priority(row) == 0 for row in rows[:8]) <= 4 else fixed


def check(rows, expected):
    times = [[], [], []]
    errors = [0] * 3
    for rep in range(7):
        for arm in (range(3) if rep % 2 == 0 else (2, 1, 0)):
            start = perf_counter_ns()
            for _ in range(48):
                method = (fixed, candidate)[arm] if arm < 2 else select(rows)
                values = [method(row) for row in rows]
            times[arm].append((perf_counter_ns()-start)/48)
            errors[arm] = sum(a != b for a,b in zip(values, expected, strict=True))
    return dict(ns=[median(x) for x in times], errors=errors, positives=sum(expected),
                selected=select(rows).__name__)


def main():
    tick = perf_counter_ns()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(row["new_errors"] == 0 for row in guards)
    adverse = next(family(4, 4))
    assert priority(adverse) == 0 and not any((certify(adverse), fixed(adverse), candidate(adverse)))
    results = {}
    for q, extra in ((8, False), (9, True)):
        pass_filter, rejected = cases(extra)
        truth = {row: bool(certify(row)) for row in pass_filter + rejected}
        lots = dict(high=pass_filter, low=rejected, misleading=rejected[:8]+pass_filter[:40])
        results[q] = {key: check(rows, [truth[row] for row in rows]) for key, rows in lots.items()}
    print(json.dumps(dict(results=results, guards=guards, elapsed_ns=perf_counter_ns()-tick), indent=2))


if __name__ == "__main__":
    main()
