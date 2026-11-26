"""Benchmark an amortized T^3 coalescence test for V19 witnesses."""
from itertools import combinations, product
import json
from statistics import median
from time import perf_counter, perf_counter_ns

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_quotient_screen import exact
from v19_signed import prepare, signed


def third_images(t):
    return tuple(t[t[nxt]] for nxt in t)


def search(t, forced, pairs, filtered):
    quotient = prepare(len(t), forced)
    images = third_images(t) if filtered else None
    generated = 0
    for a, b in pairs:
        if images is not None and images[a] == images[b]:
            continue
        generated += 1
        events = event_edges(t, (a, b), 4)
        if len(events) == 4 and signed(quotient, events):
            return (a, b), generated
    return None, generated


def assess(rows):
    if not rows:
        return {"n": 0}

    def batch(arm):
        return [search(t, f, pairs, arm) for t, f, pairs, _ in rows]

    results = [batch(arm) for arm in (False, True)]
    times = [[], []]
    for rep in range(9):
        for arm in ((0, 1) if rep % 2 == 0 else (1, 0)):
            start = perf_counter_ns()
            for _ in range(20):
                batch(bool(arm))
            times[arm].append((perf_counter_ns() - start) / (20 * len(rows)))
    return dict(n=len(rows), positives=sum(row[3] is not None for row in rows),
                generated=[sum(n for _, n in arm) for arm in results],
                errors=[sum(w != row[3] for (w, _), row in zip(arm, rows)) for arm in results],
                median_ns=[round(median(arm), 1) for arm in times])


def main():
    start = perf_counter()
    pure = (1, 2, 3, 0)
    assert exact(pure, forced_edges(pure), tuple(combinations(range(4), 2))) is None
    assert len(set(third_images(pure))) == 4
    late = (1, 2, 3, 0, 0, 4, 5)
    a, b = 6, 1
    assert len(event_edges(late, (a, b), 4)) == 3
    assert third_images(late)[a] == third_images(late)[b]
    assert search(late, forced_edges(late), ((a, b),), True) == (None, 0)
    guards = [compare([((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)]), compare(family())]
    assert all(guard["new_errors"] == 0 for guard in guards)

    pairs = tuple(combinations(range(7), 2))
    rows = []
    for t in dict.fromkeys([*( (1, 2, 3, 0, a, b, c)
                               for a, b, c in product(range(4), range(4, 7), range(7))),
                             (1, 2, 3, 0, 5, 6, 4)]):
        forced = forced_edges(t)
        if coherent(7, forced):
            rows.append((t, forced, pairs, exact(t, forced, pairs)))
    permuted = [row for row in rows if len(set(row[0])) == 7]
    mixed = [row for row in rows if len(set(row[0])) < 7]
    print(json.dumps(dict(mixed=assess(mixed), no_coalescence=assess(permuted),
                          all=assess(rows), guards=guards, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
