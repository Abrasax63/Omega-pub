"""Benchmark the first two contracted arcs as a filter for a minimal V19 core."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter, perf_counter_ns

from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import prepare, signed


def possible(t, a, b, quotient):
    x, y = quotient[a][0], quotient[b][0]
    u, v = quotient[t[a]][0], quotient[t[b]][0]
    return x != y and u != v and not ((x, y) == (u, v) or (x, y) == (v, u))


def search(t, forced, pairs, screened):
    quotient = prepare(len(t), forced)
    calls = 0
    for a, b in pairs:
        if screened and not possible(t, a, b, quotient):
            continue
        events = event_edges(t, (a, b), 4)
        if len(events) == 4:
            calls += 1
            if signed(quotient, events):
                return (a, b), calls
    return None, calls


def exact(t, forced, pairs):
    for pair in pairs:
        events = event_edges(t, pair, 4)
        if len(events) == 4 and certify((t, pair, (0, 1, 2, 3), forced, events)):
            return pair
    return None


def assess(rows):
    if not rows:
        return {"n": 0}
    times = [[], []]

    def batch(arm):
        return [search(t, f, p, arm) for t, f, p, _ in rows]

    results = [batch(arm) for arm in (False, True)]
    for rep in range(7):
        for arm in ((0, 1) if rep % 2 == 0 else (1, 0)):
            start = perf_counter_ns()
            for _ in range(25):
                batch(bool(arm))
            times[arm].append((perf_counter_ns() - start) / (25 * len(rows)))
    return {
        "n": len(rows),
        "fp": [sum(got is not None and row[3] is None for (got, _), row in zip(r, rows)) for r in results],
        "fn": [sum(got is None and row[3] is not None for (got, _), row in zip(r, rows)) for r in results],
        "wrong_first": [sum(got != row[3] for (got, _), row in zip(r, rows)) for r in results],
        "signed_calls": [sum(c for _, c in r) for r in results],
        "median_ns_per_card": [round(median(arm), 1) for arm in times],
    }


def main():
    start = perf_counter()
    pure = (1, 2, 3, 0)
    forced = forced_edges(pure)
    control = ((0, 1),)
    assert possible(pure, *control[0], prepare(4, forced))
    assert exact(pure, forced, control) is None
    assert search(pure, forced, control, False) == search(pure, forced, control, True) == (None, 1)
    guards = [compare([((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)]), compare(family())]
    assert all(guard["new_errors"] == 0 for guard in guards)
    pairs = tuple(combinations(range(8), 2))
    rows = []
    for a, b in product(range(8), repeat=2):
        t = (1, 2, 3, 0, 5, 4, a, b)
        forced = forced_edges(t)
        if coherent(8, forced):
            rows.append((t, forced, pairs, exact(t, forced, pairs)))
    print(json.dumps({
        "all": assess(rows), "negative": assess([r for r in rows if r[3] is None]),
        "positive": assess([r for r in rows if r[3] is not None]),
        "guards": guards, "seconds": perf_counter() - start,
    }, indent=2))


if __name__ == "__main__":
    main()
