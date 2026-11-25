"""Bounded V19 search for a minimal core with first meeting at time five."""
from itertools import combinations, product
import json
from time import perf_counter

from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import prepare, signed

CYCLE = (0, 1, 2, 3)


def image(t, depth):
    result = tuple(range(len(t)))
    for _ in range(depth):
        result = tuple(t[x] for x in result)
    return result


def check(t, pair):
    f = forced_edges(t)
    assert coherent(len(t), f)
    e = event_edges(t, pair, 4)
    return certify((t, pair, CYCLE, f, e))


def evaluate(maps, size):
    start = perf_counter()
    pairs = tuple(combinations(range(size), 2))
    totals = dict(maps=0, eligible_maps=0, pairs=0, cores=0, errors=0)
    witness = None
    signed_seconds = exact_seconds = 0.0
    for t in maps:
        totals["maps"] += 1
        fourth = image(t, 4)
        fifth = tuple(t[i] for i in fourth)
        matching = [(a, b) for a, b in pairs if fourth[a] != fourth[b] and fifth[a] == fifth[b]]
        if not matching:
            continue
        forced = forced_edges(t)
        if not coherent(size, forced):
            continue
        totals["eligible_maps"] += 1
        rows = [(p, event_edges(t, p, 4)) for p in matching]
        assert all(len(e) == 4 for _, e in rows)
        started = perf_counter()
        quotient = prepare(size, forced)
        guesses = [signed(quotient, e) for _, e in rows]
        signed_seconds += perf_counter() - started
        started = perf_counter()
        truths = [certify((t, p, CYCLE, forced, e)) for p, e in rows]
        exact_seconds += perf_counter() - started
        totals["pairs"] += len(rows)
        totals["cores"] += sum(x is not None for x in truths)
        totals["errors"] += sum(g != bool(x) for g, x in zip(guesses, truths, strict=True))
        if witness is None:
            witness = next((x for x in truths if x), None)
    return dict(**totals, first_witness=witness, signed_seconds=signed_seconds,
                exact_seconds=exact_seconds, total_seconds=perf_counter()-start)


def main():
    start = perf_counter()
    positive = (1, 2, 3, 0, 0)
    assert check(positive, (0, 4)) is not None
    late = (1, 2, 3, 0, 0, 4, 5, 6)
    assert image(late, 3)[0] != image(late, 3)[7] and image(late, 4)[0] == image(late, 4)[7]
    assert check(late, (0, 7)) is None
    guards = [compare([((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)]), compare(family())]
    assert all(r["new_errors"] == 0 for r in guards)
    base = (1, 2, 3, 0)
    a = evaluate((base + tail for tail in product(range(9), repeat=5)), 9)
    b = evaluate((base + (0, 4, 5, 6, 7) + tail for tail in product(range(11), repeat=2)), 11)
    assert a["pairs"] and b["pairs"] and a["errors"] == b["errors"] == 0
    print(json.dumps(dict(family_a=a, family_b=b, guards=guards, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
