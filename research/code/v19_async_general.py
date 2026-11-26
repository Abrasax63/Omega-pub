"""Check the asynchronous event forest at first fusion times 6, 7, and 8."""
from collections import Counter
from functools import reduce
from itertools import combinations
import json
from operator import and_
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_async_two import forest
from v19_branch_five import masks
from v19_signed import prepare


def cohort(h, period):
    cycle = tuple(range(1,period)) + (0,)
    prefix = cycle + (0,) + tuple(range(period,period+h-1))
    for length in range(3):
        joins = range(period,period+h) if length else (period,)
        for join in joins:
            branch = (join,) + tuple(range(len(prefix),len(prefix)+length-1)) if length else ()
            for dest in range(len(prefix)+length+1):
                yield prefix + branch + (dest,)


def walk(t, root, h):
    path = [root]
    for _ in range(h):
        path.append(t[path[-1]])
    return path


def main():
    start = perf_counter()
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(row["new_errors"] == 0 for row in guards)
    cases = [(h,p) for h in (6,7,8) for p in (1,2,3,4)]
    all_sizes = {len(t) for h,p in cases for t in cohort(h,p)}
    oracles = {n: masks(n) for n in sorted(all_sizes)}
    results = {}
    total_seconds = Counter()
    for h, p in cases:
        counts = Counter()
        times = Counter()
        for t in cohort(h,p):
            counts["maps"] += 1
            n = len(t)
            f = forced_edges(t)
            if not coherent(n,f):
                continue
            counts["coherent"] += 1
            walks = [walk(t,v,h) for v in range(n)]
            pairs = [(a,b) for a,b in combinations(range(n),2)
                     if walks[a][-2] != walks[b][-2] and walks[a][-1] == walks[b][-1]
                     and walks[a][-1] < p and set(walks[a][:-1]) & set(walks[b][:-1])]
            if not pairs:
                continue
            tick = perf_counter()
            q = prepare(n,f)
            times["forest"] += perf_counter() - tick
            tick = perf_counter()
            mask, bits = oracles[n]
            domain = reduce(and_,(bits[e] for e in f),mask)
            times["oracle"] += perf_counter() - tick
            for pair in pairs:
                e = event_edges(t,pair,h)
                assert len(e) == h
                tick = perf_counter()
                candidate = forest((q[u][0],q[v][0]) for u,v,_ in e[:-1])
                times["forest"] += perf_counter() - tick
                tick = perf_counter()
                reference = coherent(n,f+e[:-1])
                adverse_reference = coherent(n,f+e)
                times["parity"] += perf_counter() - tick
                tick = perf_counter()
                before = reduce(and_,(bits[r] for r in e[:-1]),domain)
                adverse_oracle = bool(before & bits[e[-1]])
                times["oracle"] += perf_counter() - tick
                assert candidate and reference and before and not adverse_oracle and not adverse_reference, (h,p,t,pair)
                counts.update(pairs=1,adv_rejected=1)
        assert counts["pairs"]
        results[f"{h}/{p}"] = dict(counts)
        total_seconds.update(times)
    print(json.dumps(dict(results=results,guards=guards,compare_seconds=total_seconds,
                          seconds=perf_counter()-start),indent=2))


if __name__ == "__main__":
    main()
