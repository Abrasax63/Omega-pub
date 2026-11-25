"""Bounded two-branch V19 experiment against exhaustive truth tables."""
from functools import reduce
from itertools import combinations, product
import json
from operator import and_
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import prepare, signed
from v19_time_five import check, image

BASE = (1, 2, 3, 0, 5, 6, 7, 8, 0)


def masks(n):
    size = 1 << n
    mask = (1 << size) - 1
    bits = [int(("0" * (1 << v) + "1" * (1 << v)) * (size >> (v + 1)), 2)
            for v in range(n)]
    return mask, {(a, b, p): (bits[a] ^ bits[b]) ^ (mask if p == 0 else 0)
                  for a in range(n) for b in range(n) for p in (0, 1)}


def exact(base, events):
    if reduce(and_, events, base):
        return False
    return all(reduce(and_, events[:i] + events[i+1:], base) for i in range(len(events)))


def assess(prefix, mask, values):
    start = perf_counter()
    cases = tuple(combinations(range(16), 2))
    results = dict(maps=0, pairs=0, cores=0, errors=0, exterior_pairs=0, first_witness=None)
    costs = [0., 0.]
    for ends in product(range(16), repeat=2):
        t = prefix + ends
        force = forced_edges(t)
        if not coherent(16, force):
            continue
        results["maps"] += 1
        fourth = image(t, 4)
        rows = [(a, b, event_edges(t, (a, b), 4)) for a, b in cases
                if fourth[a] != fourth[b] and t[fourth[a]] == t[fourth[b]]]
        results["pairs"] += len(rows)
        results["exterior_pairs"] += len(rows) if any(max(a,b) >= 14 for a,b,_ in force) else 0
        tick = perf_counter()
        quotient = prepare(16, force)
        fixed = [signed(quotient, e) for _, _, e in rows]
        costs[0] += perf_counter()-tick
        tick = perf_counter()
        common = reduce(and_, (values[e] for e in force), mask)
        assert common
        truth = [exact(common, tuple(values[edge] for edge in e)) for _, _, e in rows]
        costs[1] += perf_counter()-tick
        results["cores"] += sum(truth)
        results["errors"] += sum(x != y for x,y in zip(fixed,truth,strict=True))
        if any(truth) and results["first_witness"] is None:
            a,b,_ = rows[truth.index(True)]
            assert check(t, (a,b))
            results["first_witness"] = (t,(a,b))
    return dict(**results, seconds=perf_counter()-start, signed_seconds=costs[0], oracle_seconds=costs[1])


def main():
    start = perf_counter()
    assert check((1,2,3,0,0), (0,4))
    adverse = (1,2,3,0,0,4,5,6)
    assert not check(adverse, (0,7))
    mask, values = masks(16)
    for t,p in [((1,2,3,0,0),(0,4)),(adverse,(0,7))]:
        forced = reduce(and_, (values[e] for e in forced_edges(t)), mask)
        assert exact(forced, tuple(values[e] for e in event_edges(t,p,4))) == bool(check(t,p))
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(g["new_errors"] == 0 for g in guards)
    a = assess(BASE[:-1]+(14,10,11,12,13,14), mask, values)
    b = assess(BASE+(10,1,12,11,13), mask, values)
    assert a["pairs"] and b["pairs"] and a["errors"] == b["errors"] == 0
    print(json.dumps(dict(a=a,b=b,guards=guards,seconds=perf_counter()-start), indent=2))

if __name__ == "__main__":
    main()
