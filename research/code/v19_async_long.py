"""Search asynchronous V19 overlap in terminal-cycle families."""
from collections import Counter
from functools import reduce
from itertools import combinations
import json
from operator import and_
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_branch_five import exact, masks
from v19_signed import prepare, signed
from v19_time_five import check

PERIODS = (4, 5)


def graphs(period):
    cycle = tuple(range(5,4+period)) + (4,)
    first = 4 + period
    chain = (4,) + tuple(range(first,first+4))
    prefix = (1,2,3,0) + cycle + chain
    for k in range(4):
        for join in range(first,first+5) if k else (first,):
            branch = (join,) + tuple(range(len(prefix),len(prefix)+k-1)) if k else ()
            for tail in range(len(prefix)+k+1):
                yield prefix + branch + (tail,)


def walk(t, v):
    path = [v]
    for _ in range(5):
        path.append(t[path[-1]])
    return path


def assess(period, oracles):
    start = perf_counter()
    totals = Counter()
    fixed_time = oracle_time = 0.
    witness = None
    by_lag = Counter()
    for t in graphs(period):
        totals["maps"] += 1
        n = len(t)
        f = forced_edges(t)
        if not coherent(n,f):
            continue
        totals["coherent"] += 1
        walks = [walk(t,i) for i in range(n)]
        rows = []
        for a,b in combinations(range(n),2):
            x,y = walks[a],walks[b]
            if x[4] != y[4] and x[5] == y[5] and set(x[:5]) & set(y[:5]):
                rows.append((a,b,event_edges(t,(a,b),4)))
        if not rows:
            continue
        mask,bits = oracles[n]
        tick = perf_counter()
        q = prepare(n,f)
        ref = [signed(q, e) for _,_,e in rows]
        fixed_time += perf_counter()-tick
        tick = perf_counter()
        domain = reduce(and_,(bits[e] for e in f),mask)
        answers = [exact(domain,tuple(bits[z] for z in e)) for _,_,e in rows]
        oracle_time += perf_counter()-tick
        for (a,b,e),fixed,gold in zip(rows,ref,answers,strict=True):
            assert len(e)==4
            lag = min(abs(i-j) for i,x in enumerate(walks[a][:5])
                      for j,y in enumerate(walks[b][:5]) if x == y)
            by_lag[lag] += 1
            left = [q[x][0] for x,y,_ in e]
            right = [q[y][0] for x,y,_ in e]
            private = any(len(set(x))==4 and not set(x)&set(y) for x,y in ((left,right),(right,left)))
            totals.update(pairs=1,errors=int(fixed!=gold),cores=int(gold),without_private=int(not private))
            if gold and witness is None:
                assert check(t,(a,b))
                witness=(t,(a,b))
    for key in ("pairs", "errors", "cores", "without_private"):
        totals.setdefault(key, 0)
    return dict(**totals,witness=witness,by_lag=dict(sorted(by_lag.items())),seconds=perf_counter()-start,
                signed_seconds=fixed_time,oracle_seconds=oracle_time)


def main():
    start=perf_counter()
    assert check((1,2,3,0,0),(0,4))
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(x["new_errors"]==0 for x in guards)
    oracles={n:masks(n) for n in sorted({len(t) for p in PERIODS for t in graphs(p)})}
    result=[assess(p,oracles) for p in PERIODS]
    print(json.dumps(dict(results=result,guards=guards,seconds=perf_counter()-start),indent=2))

if __name__=="__main__":
    main()
