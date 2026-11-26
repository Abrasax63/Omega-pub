"""Time the signed hybrid on two larger disjoint-cycle families."""
import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family, priority
from audit_v19_shadow_guard import compare, family as guard_family
from signed_hybrid import hybrid_core
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def reserve(q):
    prefix = (*range(1, q), 0, *range(q + 1, q + 5), q)
    for attach in range(len(prefix)):
        transform = (*prefix, attach)
        forced = forced_edges(transform)
        if not coherent(len(transform), forced):
            continue
        for pair in combinations(range(len(transform)), 2):
            events = event_edges(transform, pair, 4)
            if len(events) == 4:
                yield transform, pair, tuple(range(q)), forced, events


def fixed(case):
    return priority(case) == 0 and bool(certify(case))


def audit(cases):
    start = perf_counter_ns()
    oracle = [bool(certify(case)) for case in cases]
    oracle_ns = perf_counter_ns() - start
    survivors = sum(priority(case) == 0 for case in cases)
    timings = [[], []]
    errors = [0, 0]
    for replicate in range(5):
        for i in ((0, 1) if replicate % 2 == 0 else (1, 0)):
            verifier = (fixed, hybrid_core)[i]
            start = perf_counter_ns()
            output = [verifier(case) for case in cases]
            timings[i].append(perf_counter_ns() - start)
            errors[i] += sum(a != b for a, b in zip(output, oracle, strict=True))
    return dict(queries=len(cases), survivors=survivors, positives=sum(oracle), errors=errors,
                projections=[5 * survivors, 0, 5 * len(cases)], oracle_ns=oracle_ns,
                timing_ns=timings, median_ns=[median(samples) for samples in timings])


if __name__ == "__main__":
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(row["new_errors"] == 0 for row in guards)
    pure = next(family(4, 4))
    assert not certify(pure) and not fixed(pure) and not hybrid_core(pure)
    families = {str(q): list(reserve(q)) for q in (4, 6)}
    assert sum(map(len, families.values())) <= 1300
    print(json.dumps({"guards": guards, "families": {q: audit(cases) for q, cases in families.items()}}, indent=2))

