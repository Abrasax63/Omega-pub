"""Two-stage four-event core: unsigned quotient, then signed potentials on survivors."""
from collections import Counter
from itertools import combinations, product
from time import perf_counter
import json

from pivot import family, priority, certify
from test_v19_locality_l_plus_1 import forced_edges, event_edges, coherent

def screen(case):
    transformation, _, _, forced, events = case
    roots=list(range(len(transformation)))
    def root(i):
        while roots[i]!=i: i=roots[i]
        return i
    for a,b,_ in forced: roots[root(b)]=root(a)
    roots=[root(i) for i in range(len(roots))]
    edges=[tuple(sorted((roots[a],roots[b]))) for a,b,_ in events]
    vertices={v for e in edges for v in e}
    if len(vertices)!=4 or len(set(edges))!=4 or any(a==b for a,b in edges): return None
    if any(sum(v in e for e in edges)!=2 for v in vertices): return None
    return roots

def hybrid_core(case):
    transformation,_,_,forced,events=case
    roots=screen(case)
    if roots is None: return False
    adjacency=[[] for _ in transformation]
    for a,b,p in forced:
        adjacency[a].append((b,p)); adjacency[b].append((a,p))
    offset=[None]*len(transformation)
    for start in range(len(transformation)):
        if offset[start] is not None: continue
        offset[start]=0; stack=[start]
        while stack:
            a=stack.pop()
            for b,p in adjacency[a]:
                wanted=offset[a]^p
                if offset[b] is None: offset[b]=wanted; stack.append(b)
                elif offset[b]!=wanted: raise ValueError('forced incoherent')
    total=0
    for a,b,p in events: total ^= offset[a]^offset[b]^p
    return bool(total)

def c4_c3_free():
    n=8; cycle=(0,1,2,3)
    for last in range(n):
        T=(1,2,3,0,5,6,4,last)
        F=forced_edges(T)
        if not coherent(n,F): continue
        for pair in combinations(range(n),2):
            E=event_edges(T,pair,4)
            if len(E)==4: yield T,pair,cycle,F,E

def audit(cases,label):
    rows=list(cases); stats=dict(label=label,total=len(rows),positive=0,
      reference_errors=0,candidate_errors=0,reference_projection_calls=0,
      oracle_projection_calls=5*len(rows),reference_seconds=0.,candidate_seconds=0.,oracle_seconds=0.)
    for case in rows:
        t=perf_counter(); survivor=priority(case)==0; reference=survivor and bool(certify(case));
        stats['reference_seconds']+=perf_counter()-t; stats['reference_projection_calls']+=5*survivor
        t=perf_counter(); candidate=hybrid_core(case); stats['candidate_seconds']+=perf_counter()-t
        t=perf_counter(); exact=bool(certify(case)); stats['oracle_seconds']+=perf_counter()-t
        stats['positive']+=exact; stats['reference_errors']+=reference!=exact; stats['candidate_errors']+=candidate!=exact
    assert stats['reference_errors']==stats['candidate_errors']==0
    return stats

if __name__=='__main__':
    pure=next(family(4,4)); assert not hybrid_core(pure) and not certify(pure)
    witness=next(c for c in family(5,4) if bool(certify(c))); assert hybrid_core(witness)
    print(json.dumps(audit(family(8,6),'c6_plus_two_free'),sort_keys=True))
    print(json.dumps(audit(c4_c3_free(),'c4_disjoint_c3_plus_free'),sort_keys=True))
