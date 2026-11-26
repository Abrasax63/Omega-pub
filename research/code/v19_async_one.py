"""Check the event quotient for asynchronous overlap on a terminal fixed point."""
from collections import Counter
from functools import reduce
from itertools import combinations
import json
from operator import and_
from time import perf_counter

from v19_async_two import forest
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_async_three import graphs, walk
from v19_branch_five import exact, masks
from v19_signed import prepare, signed
from v19_time_five import check


def cohort():
    for t in graphs(1):
        second_fixed = len(t)
        for dest in (4, len(t) - 1, second_fixed):
            yield t + (second_fixed, dest)


def main():
    start = perf_counter()
    assert check((1,2,3,0,0),(0,4))
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(row["new_errors"] == 0 for row in guards)
    oracles = {n: masks(n) for n in sorted({len(t) for t in cohort()})}
    totals = Counter()
    strata = Counter()
    signed_seconds = exact_seconds = 0.0
    for t in cohort():
        totals["maps"] += 1
        n = len(t)
        f = forced_edges(t)
        if not coherent(n, f):
            continue
        totals["coherent"] += 1
        walks = [walk(t, v) for v in range(n)]
        rows = []
        for a,b in combinations(range(n),2):
            x,y = walks[a], walks[b]
            if x[4] != y[4] and x[5] == y[5] and x[5] == 4:
                lags = {abs(i-j) for i,u in enumerate(x[:5])
                        for j,v in enumerate(y[:5]) if u == v}
                if lags:
                    rows.append((a,b,min(lags),event_edges(t,(a,b),4)))
        if not rows:
            continue
        tick = perf_counter()
        q = prepare(n, f)
        predictions = [signed(q,e) for _,_,_,e in rows]
        signed_seconds += perf_counter() - tick
        tick = perf_counter()
        mask, bits = oracles[n]
        domain = reduce(and_, (bits[e] for e in f), mask)
        answers = [exact(domain,tuple(bits[z] for z in e)) for _,_,_,e in rows]
        exact_seconds += perf_counter() - tick
        for (a,b,lag,e),pred,gold in zip(rows,predictions,answers,strict=True):
            assert len(e) == 4 and lag in (1,2,3,4)
            assert forest((q[u][0],q[v][0]) for u,v,_ in e), (t,a,b,e)
            assert not gold and not pred, (t,a,b,pred,gold)
            strata[lag] += 1
            totals.update(pairs=1, cores=int(gold), errors=int(pred != gold))
    assert all(strata[lag] for lag in (1,2,3,4))
    print(json.dumps(dict(totals=totals, lag=strata, guards=guards,
                          signed_seconds=signed_seconds, exact_seconds=exact_seconds,
                          seconds=perf_counter()-start),indent=2))


if __name__ == "__main__":
    main()
