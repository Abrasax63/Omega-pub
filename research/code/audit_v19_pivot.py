"""Compare orbit order with an unsigned parity-quotient priority."""
from itertools import combinations, product
from random import Random
from time import perf_counter
import json

from test_v19_locality_l_plus_1 import forced_edges, event_edges, coherent
from audit_v19_shadow_guard import exhaustive_shadow

LIMIT = 32


def family(n, q):
    cycle = tuple(range(q))
    prefix = (*range(1, q), 0)
    for tail in product(range(n), repeat=n-q):
        transformation = prefix + tail
        forced = forced_edges(transformation)
        if not coherent(n, forced):
            continue
        for pair in combinations(range(n),2):
            events = event_edges(transformation, pair, 4)
            if len(events) == 4:
                yield transformation, pair, cycle, forced, events


def priority(case):
    transformation, _, _, forced, events = case
    roots = list(range(len(transformation)))

    def root(i):
        while roots[i] != i:
            i = roots[i]
        return i

    for a,b,_ in forced:
        roots[root(b)] = root(a)
    edges = [tuple(sorted((root(a),root(b)))) for a,b,_ in events]
    vertices = {i for e in edges for i in e}
    if len(vertices)!=4 or len(set(edges))!=4 or any(a==b for a,b in edges):
        return 1
    return int(any(sum(v in e for e in edges)!=2 for v in vertices))


def certify(case):
    transformation, pair, cycle, forced, events = case
    n = len(transformation)
    sizes = [len(exhaustive_shadow(n,forced+subset,cycle)) for subset in
             [events, *(events[:i]+events[i+1:] for i in range(4))]]
    if sizes[0] == 0 and all(sizes[1:]):
        return dict(T=transformation,pair=pair,C=cycle,F=forced,E=events,sizes=sizes)
    return None


def search(cases):
    start=perf_counter()
    for rank,case in enumerate(cases[:LIMIT],1):
        certificate=certify(case)
        if certificate:
            return dict(query_checks=rank,projection_calls=5*rank,seconds=perf_counter()-start,
                        witness=certificate)
    count=min(LIMIT,len(cases))
    return dict(query_checks=count,projection_calls=5*count,seconds=perf_counter()-start,witness=None)


def main():
    pure = next(family(4,4))
    assert priority(pure)==0 and certify(pure) is None
    for n in (4,5,6):
        for q in range(3,n+1):
            start=perf_counter()
            cases=list(family(n,q))
            shared=perf_counter()-start
            fixed=search(cases)
            start=perf_counter()
            ranked=sorted(cases,key=priority)
            ranking_seconds=perf_counter()-start
            pivot=search(ranked)
            random=[]
            for seed in range(8):
                shuffled=list(cases)
                Random(seed).shuffle(shuffled)
                x=search(shuffled)
                random.append(dict(checks=x['query_checks'],hit=x['witness'] is not None))
            print(json.dumps(dict(kind='budget',n=n,q=q,cases=len(cases),shared_seconds=shared,
                fixed=fixed,ranking_seconds=ranking_seconds,pivot=pivot,random=random)))
    for n in (3,4,5):
        for q in range(3,n+1):
            cases=list(family(n,q))
            hits=[w for case in cases if (w:=certify(case))]
            print(json.dumps(dict(kind='full',n=n,q=q,cases=len(cases),cores=len(hits),
                                  first=hits[0] if hits else None)))


if __name__=='__main__':
    main()
