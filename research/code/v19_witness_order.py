"""Compare an order derived from transient depths with lexicographic witness search."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter, perf_counter_ns
from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_existence import search


def depth(t, vertex):
    seen={}
    while vertex not in seen:
        seen[vertex]=len(seen)
        vertex=t[vertex]
    return seen[vertex]


def run(rows,ranked):
    answers=[]
    for t,f,pairs in rows:
        if ranked:
            d=[depth(t,v) for v in range(len(t))]
            pairs=sorted(pairs,key=lambda p:-(d[p[0]]+d[p[1]]))
        answers.append(search(t,f,pairs,True))
    return answers


def measure(rows,truth,idx):
    if not idx:
        return dict(n=0)
    sample=[rows[i] for i in idx]
    answers=[run(sample,arm) for arm in (False,True)]
    errors=[sum((p is None and bool(truth[i])) or (p is not None and p not in truth[i])
                for i,(p,_) in zip(idx,r,strict=True)) for r in answers]
    durations=[[],[]]
    for rep in range(7):
        for arm in (range(2) if rep%2==0 else (1,0)):
            start=perf_counter_ns()
            for _ in range(24):
                run(sample,arm)
            durations[arm].append((perf_counter_ns()-start)/(24*len(sample)))
    return dict(n=len(idx),errors=errors,calls=[sum(c for _,c in a) for a in answers],
                ns_per_card=[round(median(d),1) for d in durations])


def main():
    start=perf_counter()
    pure=(1,2,3,0)
    rows=[(pure,forced_edges(pure),tuple(combinations(range(4),2)))]
    assert run(rows,False)==run(rows,True)==[(None,6)]
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(g["new_errors"]==0 for g in guards)
    rows=[]
    truth=[]
    for a,b in product(range(7),repeat=2):
        t=(1,2,3,0,a,b,(a+b)%7)
        f=forced_edges(t)
        if not coherent(7,f):
            continue
        pairs=tuple(combinations(range(7),2))
        truth.append({p for p in pairs if len(e:=event_edges(t,p,4))==4 and certify((t,p,(0,1,2,3),f,e))})
        rows.append((t,f,pairs))
    samples=dict(all=list(range(len(rows))),positive=[i for i,w in enumerate(truth) if w],
                 negative=[i for i,w in enumerate(truth) if not w])
    print(json.dumps(dict(results={k:measure(rows,truth,i) for k,i in samples.items()},
                          guards=guards,seconds=perf_counter()-start),indent=2))


if __name__=="__main__":
    main()
