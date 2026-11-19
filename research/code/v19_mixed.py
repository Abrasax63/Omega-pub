"""Exhaustive and timed comparison on a C4/C2 union with a depth-two chain."""
import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_shadow_guard import compare, family as guard_family
from audit_v19_pivot import certify, family, priority
from signed_hybrid import hybrid_core
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def reserve():
    for attachment in range(6):
        transformation = (1, 2, 3, 0, 5, 4, attachment, 6)
        forced = forced_edges(transformation)
        assert coherent(len(transformation), forced)
        for pair in combinations(range(len(transformation)), 2):
            events = event_edges(transformation, pair, 4)
            if len(events) == 4:
                yield transformation, pair, (0, 1, 2, 3), forced, events


def fixed(case):
    return priority(case) == 0 and bool(certify(case))


def run():
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = {"five_states": compare([witness]), "c5_family": compare(guard_family())}
    assert all(row["new_errors"] == 0 for row in guards.values())
    negative = next(family(4, 4))
    assert not certify(negative) and not fixed(negative) and not hybrid_core(negative)
    cases = list(reserve())
    expected = [bool(certify(case)) for case in cases]
    survivors = sum(priority(case) == 0 for case in cases)
    timings = [[], []]
    errors = [0, 0]
    for repetition in range(5):
        for arm in (range(2) if repetition % 2 == 0 else reversed(range(2))):
            verifier = (fixed, hybrid_core)[arm]
            start = perf_counter_ns()
            actual = [verifier(case) for case in cases]
            timings[arm].append(perf_counter_ns() - start)
            errors[arm] = sum(a != e for a, e in zip(actual, expected, strict=True))
            assert actual == expected
    print(json.dumps({
        "guards": guards, "queries": len(cases), "survivors": survivors, "positives": sum(expected),
        "errors": errors, "projection_calls": [5 * survivors, 0, 5 * len(cases)],
        "samples_ns": timings, "median_ns": list(map(median, timings)),
    }, indent=2))


if __name__ == "__main__":
    run()

