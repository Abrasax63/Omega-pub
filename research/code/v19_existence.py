"""Evaluate a witness-only query independently of the exhaustive count."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter, perf_counter_ns
from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import prepare, signed


def cases(q):
    base=(*range(1,q),0)
    for a,b in product(range(q),range(q+2)):
        t=(*base,a,q,b)
        f=forced_edges(t)
        if coherent(len(t),f):
            yield t,f


def verify(t,p,quotient):
    e=event_edges(t,p,4)
    return len(e)==4 and signed(quotient,e)


def search(t,f,pairs,early):
    quotient=prepare(len(t),f)
    first=None
    count=0
    questions=0
    for p in pairs:
        questions+=1
        if verify(t,p,quotient):
            if early:
                return p,questions
            first=first or p
            count+=1
    return (first,questions) if early else (first,questions,count)


def batch(rows,early):
    return [search(t,f,pairs,early) for t,f,pairs in rows]


def assess(rows,witnesses):
    if not rows:
        return {"n":0}
    outputs=[batch(rows,early) for early in (False,True)]
    errors=[sum(got[0]!=want for got,want in zip(answer,witnesses,strict=True)) for answer in outputs]
    times=[[],[]]
    for rep in range(7):
        for i in (range(2) if rep%2==0 else (1,0)):
            start=perf_counter_ns()
            for _ in range(16):
                batch(rows,bool(i))
            times[i].append((perf_counter_ns()-start)/16/len(rows))
    return dict(n=len(rows),errors=errors,calls=[sum(r[1] for r in out) for out in outputs],
                median_ns=[round(median(a),1) for a in times])


def main():
    start=perf_counter()
    pure=(1,2,3,0)
    pp=tuple(combinations(range(4),2))
    assert search(pure,forced_edges(pure),pp,True)==(None,6)
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(g["new_errors"]==0 for g in guards)
    results={}
    for q in (4,6):
        values=[]
        for t,f in cases(q):
            pairs=tuple(combinations(range(len(t)),2))
            exact=[]
            for p in pairs:
                e=event_edges(t,p,4)
                if len(e)==4 and certify((t,p,tuple(range(q)),f,e)):
                    exact.append(p)
            values.append((t,f,pairs,exact))
        results[q]={}
        for rev in (False,True):
            results[q][str(rev)]={}
            for positive in (False,True):
                sel=[r for r in values if bool(r[-1])==positive]
                rows=[(t,f,p[::-1] if rev else p) for t,f,p,_ in sel]
                witness=[ex[-1 if rev else 0] if ex else None for _,_,_,ex in sel]
                results[q][str(rev)][str(positive)]=assess(rows,witness)
    print(json.dumps(dict(results=results,guards=guards,seconds=perf_counter()-start),indent=2))


if __name__=="__main__":
    main()
