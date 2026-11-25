import json
from itertools import combinations, zip_longest
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, priority
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import candidate, fixed, prepare, prepared, signed


def groups():
    for q in (4,5):
        for a in range(3):
            for tail in ((a,q,q+1,q+2,q+3),(a,(a+1)%q,q,q+1,q+1)):
                t = (*range(1,q),0,*tail)
                f = forced_edges(t)
                if not coherent(len(t),f):
                    continue
                strata = [[],[]]
                for pair in combinations(range(len(t)),2):
                    e = event_edges(t,pair,4)
                    if len(e)==4:
                        row = t,pair,tuple(range(q)),f,e
                        strata[priority(row)].append(row)
                ordered = [r for pair in zip_longest(*strata) for r in pair if r is not None]
                assert len(ordered)>=4
                yield ordered[:4]


def check(gs):
    rows = [r for g in gs for r in g]
    truth = [bool(certify(r)) for r in rows]
    arms = (lambda:[fixed(r) for r in rows],lambda:[candidate(r) for r in rows],lambda:prepared(gs))
    errors = [sum(a!=b for a,b in zip(f(),truth,strict=True)) for f in arms]
    times = [[] for _ in arms]
    for rep in range(9):
        for i in ((0,1,2) if rep%2==0 else (2,1,0)):
            t=perf_counter_ns()
            for _ in range(96):
                arms[i]()
            times[i].append((perf_counter_ns()-t)/96)
    return dict(n=len(rows),positives=sum(truth),errors=errors,ns=[median(t) for t in times])


def main():
    t=perf_counter_ns()
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(g["new_errors"]==0 for g in guards)
    e=((0,1,0),(0,1,1),(1,2,0),(2,3,0))
    assert not coherent(4,e) and not signed(prepare(4,()),e)
    gs=list(groups())
    results={n:check([g[:n] for g in gs]) for n in (1,2,4)}
    print(json.dumps(dict(results=results,guards=guards,elapsed_ns=perf_counter_ns()-t),indent=2))


if __name__=="__main__":
    main()
