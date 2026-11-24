"""Compare coherence shortcut against guarded projections on fused tails."""
import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family, priority
from audit_v19_shadow_guard import compare, guarded_shadow, family as guard_family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_shared import candidate


def reserve(q):
    for attach in range(q):
        mapping = (*range(1, q), 0, attach, q, q + 1, q)
        n = len(mapping)
        forced = forced_edges(mapping)
        assert coherent(n, forced)
        for pair in combinations(range(n), 2):
            events = event_edges(mapping, pair, 4)
            if len(events) == 4:
                yield mapping, pair, tuple(range(q)), forced, events


def fixed(case):
    if priority(case) != 0:
        return False
    mapping, _, cycle, forced, events = case
    n = len(mapping)
    return not guarded_shadow(n, forced + events, cycle) and all(
        guarded_shadow(n, forced + events[:i] + events[i+1:], cycle)
        for i in range(4)
    )


def audit(cases):
    oracle = [bool(certify(c)) for c in cases]
    survivors = sum(priority(c) == 0 for c in cases)
    times = [[], []]
    mistakes = [0, 0]
    for lap in range(9):
        for arm in ((0, 1) if lap % 2 == 0 else (1, 0)):
            t = perf_counter_ns()
            decisions = [(fixed, candidate)[arm](c) for c in cases]
            times[arm].append(perf_counter_ns() - t)
            mistakes[arm] += sum(a != b for a, b in zip(decisions, oracle, strict=True))
    return dict(n=len(cases), survivors=survivors, positives=sum(oracle),
                errors=mistakes, median_ns=[median(t) for t in times], timing_ns=times)


if __name__ == "__main__":
    start = perf_counter_ns()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(row["new_errors"] == 0 for row in guards)
    negative = next(family(4, 4))
    assert not certify(negative) and not fixed(negative) and not candidate(negative)
    cases = {q: list(reserve(q)) for q in (4, 6)}
    assert sum(map(len, cases.values())) <= 1000
    results = {q: audit(lot) for q, lot in cases.items()}
    print(json.dumps(dict(guards=guards, families=results, duration_ns=perf_counter_ns()-start), indent=2))

