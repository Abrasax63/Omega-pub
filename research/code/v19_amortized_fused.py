"""Measure the integrated raw screen when the signed quotient is shared per map."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter, perf_counter_ns
from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_raw_screen import raw_reject
from v19_signed import prepare, signed


def generated(t, pair):
    a,b=pair
    edges=[]
    for _ in range(4):
        if a==b:
            return ()
        edge=(a,b,0) if a<b else (b,a,0)
        if edge in edges:
            return ()
        edges.append(edge)
        a,b=t[a],t[b]
    return edges


def solve(cards, mode):
    answers=[]
    for t,f,pairs in cards:
        quotient=prepare(len(t),f)
        for pair in pairs:
            if mode==2:
                e=generated(t,pair)
            else:
                e=event_edges(t,pair,4)
            answers.append(len(e)==4 and (mode!=1 or not raw_reject(e)) and signed(quotient,e))
    return answers


def make_cards(base):
    q=len(base)
    for a,b in product(range(4),range(q+2)):
        t=(*base,a,q,b,(b+2)%(q+2))
        f=forced_edges(t)
        if coherent(len(t),f):
            yield t,f,tuple(combinations(range(len(t)),2))


def evaluate(cards):
    truth=[]
    for t,f,pairs in cards:
        for pair in pairs:
            e=event_edges(t,pair,4)
            truth.append(len(e)==4 and bool(certify((t,pair,(0,1,2,3),f,e))))
    errors=[sum(a!=b for a,b in zip(solve(cards,m),truth,strict=True)) for m in range(3)]
    samples=[[],[],[]]
    for rep in range(7):
        for mode in (range(3) if rep%2==0 else (2,1,0)):
            t=perf_counter_ns()
            for _ in range(16):
                solve(cards,mode)
            samples[mode].append((perf_counter_ns()-t)/(16*len(truth)))
    return dict(n=len(truth),positive=sum(truth),errors=errors,ns=[round(median(x),1) for x in samples])


def main():
    start=perf_counter()
    assert not generated((0,0),(0,1))
    assert not generated((1,0),(0,1))
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(g["new_errors"]==0 for g in guards)
    results={}
    for label,base in (("fixed_point",(1,2,3,0,4)),("transposition",(1,2,3,0,5,4))):
        cards=list(make_cards(base))
        sparse=[(t,f,tuple(p[i] for i in (0,1,len(p)//2-1,len(p)//2,-2,-1))) for t,f,p in cards]
        results[label]=dict(cards=len(cards),full=evaluate(cards),sparse=evaluate(sparse))
    print(json.dumps(dict(results=results,guards=guards,seconds=perf_counter()-start),indent=2))


if __name__=="__main__":
    main()
