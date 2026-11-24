"""Check four-event minimal contradictions on unequal arms."""
import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family
from audit_v19_shadow_guard import compare, family as guard_family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_shared import candidate


def fixed(case):
    transform, _, _, forced, events = case
    n = len(transform)
    return not coherent(n, forced + events) and all(
        coherent(n, forced + events[:i] + events[i+1:]) for i in range(4)
    )


def reserve():
    for q in (4, 5, 6):
        for short, long in ((1, 2), (1, 3), (2, 3)):
            transform = (*range(1, q), 0, 0,
                         *range(q, q + short),
                         q, *range(q + short + 1, q + short + long))
            forced = forced_edges(transform)
            assert coherent(len(transform), forced)
            for pair in combinations(range(len(transform)), 2):
                events = event_edges(transform, pair, 4)
                if len(events) == 4:
                    yield transform, pair, tuple(range(q)), forced, events


def main():
    start = perf_counter_ns()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(x["new_errors"] == 0 for x in guards)
    adverse = next(family(4, 4))
    assert not certify(adverse) and not fixed(adverse) and not candidate(adverse)
    cases = list(reserve())
    assert 0 < len(cases) <= 500
    oracle = [bool(certify(case)) for case in cases]
    times = [[], []]
    errors = [None, None]
    for replicate in range(9):
        for i in ((0, 1) if replicate % 2 == 0 else (1, 0)):
            fn = (fixed, candidate)[i]
            tick = perf_counter_ns()
            obtained = [fn(case) for case in cases]
            times[i].append(perf_counter_ns() - tick)
            errors[i] = {
                "fp": sum(a and not b for a, b in zip(obtained, oracle)),
                "fn": sum(b and not a for a, b in zip(obtained, oracle)),
            }
    print(json.dumps(dict(queries=len(cases), positives=sum(oracle),
                          errors=errors, timing_ns=times, median_ns=list(map(median, times)),
                          guards=guards, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
