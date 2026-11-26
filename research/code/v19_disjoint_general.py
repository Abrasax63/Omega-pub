"""Exhaustive checks for disjoint prefixes before first fusion."""
from collections import Counter
from functools import reduce
from itertools import combinations, product
import json
from operator import and_
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, forced_edges
from v19_branch_five import masks


def periodic(t, v):
    x = t[v]
    for _ in t:
        if x == v:
            return True
        x = t[x]
    return False


def events(t, a, b):
    left, right, seen = set(), set(), set()
    rows = []
    while a != b:
        if (a,b) in seen or a in right or b in left:
            return None
        seen.add((a,b))
        left.add(a)
        right.add(b)
        rows.append((a,b,0))
        a,b = t[a],t[b]
    return rows, a


def main():
    start = perf_counter()
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(not g["new_errors"] for g in guards)
    totals = Counter()
    cost = Counter()
    for n in range(2,7):
        universe, bits = masks(n)
        for t in product(range(n), repeat=n):
            f = forced_edges(t)
            if not coherent(n,f):
                continue
            domain = reduce(and_, (bits[e] for e in f), universe)
            for a,b in combinations(range(n),2):
                item = events(t,a,b)
                if item is None:
                    continue
                rows, out = item
                key = ("periodic" if periodic(t,out) else "transient")
                totals[key] += 1
                if len(rows) > 1:
                    totals[key+"_nonempty"] += 1
                tick = perf_counter()
                before = coherent(n,f+tuple(rows[:-1]))
                after = coherent(n,f+tuple(rows))
                cost["parity"] += perf_counter()-tick
                tick = perf_counter()
                valid = reduce(and_,(bits[r] for r in rows[:-1]),domain)
                adverse = valid & bits[rows[-1]]
                cost["oracle"] += perf_counter()-tick
                assert before and valid and not after and not adverse, (t,a,b,rows)
    assert totals["periodic_nonempty"] and totals["transient_nonempty"]
    print(json.dumps(dict(counts=totals, guards=guards, compare_seconds=cost,
                          seconds=perf_counter()-start),indent=2))


if __name__ == "__main__":
    main()
