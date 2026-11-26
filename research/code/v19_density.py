import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family, priority
from audit_v19_shadow_guard import compare, family as guard_family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_shared import candidate
from v19_unequal import fixed


def reserve():
    strata = [[], []]
    for q in (4, 5, 6):
        prefix = (*range(1, q), 0, q + 1, q + 2, q)
        for a in range(len(prefix)):
            for b in range(len(prefix) + 1):
                transform = (*prefix, a, b)
                n = len(transform)
                forced = forced_edges(transform)
                if not coherent(n, forced):
                    continue
                for pair in combinations(range(n), 2):
                    events = event_edges(transform, pair, 4)
                    if len(events) != 4:
                        continue
                    case = (transform, pair, tuple(range(q)), forced, events)
                    group = strata[priority(case)]
                    if len(group) < 48:
                        group.append(case)
                    if all(len(group) == 48 for group in strata):
                        return strata
    raise AssertionError("Insufficient coverage")


def timing(cases):
    timings = [[], []]
    for rep in range(7):
        for i in ((0, 1) if rep % 2 == 0 else (1, 0)):
            check = (fixed, candidate)[i]
            tick = perf_counter_ns()
            for _ in range(96):
                for case in cases:
                    check(case)
            timings[i].append((perf_counter_ns() - tick) / 96)
    return [median(t) for t in timings]


def main():
    start = perf_counter_ns()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(g["new_errors"] == 0 for g in guards)
    adverse = next(family(4, 4))
    assert priority(adverse) == 0 and not certify(adverse)
    assert not fixed(adverse) and not candidate(adverse)
    survivors, rejected = reserve()
    oracle = [bool(certify(case)) for case in survivors + rejected]
    errors = []
    for method in (fixed, candidate):
        values = [method(case) for case in survivors + rejected]
        errors.append(dict(fp=sum(a and not b for a,b in zip(values, oracle)),
                           fn=sum(b and not a for a,b in zip(values, oracle))))
    times = {count: timing(survivors[:count] + rejected[:48-count])
             for count in (0, 12, 24, 36, 48)}
    print(json.dumps(dict(cases=len(oracle), positives=sum(oracle), errors=errors,
                          median_ns_by_survivors=times,
                          guards=guards, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
