"""Evaluate full coloring certificates; preserve the existing global reference."""
from itertools import product
from time import perf_counter
import json
from test_v19_locality_l_plus_1 import forced_edges,event_edges,projected_shadow
from audit_v19_shadow_guard import exhaustive_shadow,guarded_shadow

def construct(n,edges):
    adj=[[] for _ in range(n)]
    for u,v,p in edges:adj[u].append((v,p));adj[v].append((u,p))
    colors=[None]*n
    for root in range(n):
        if colors[root] is not None:continue
        colors[root]=0;stack=[root]
        while stack:
            u=stack.pop()
            for v,p in adj[u]:
                wanted=colors[u]^p
                if colors[v] is None:colors[v]=wanted;stack.append(v)
                elif colors[v]!=wanted:return None
    return tuple(colors)

def verify(n,edges,colors):
    return (isinstance(colors,(tuple,list)) and len(colors)==n
            and all(type(c) is int and c in (0,1) for c in colors)
            and all(colors[u]^colors[v]==p for u,v,p in edges))

def candidate(n,edges,cycle):
    colors=construct(n,edges)
    if colors is None:return frozenset()
    assert verify(n,edges,colors)
    return projected_shadow(n,edges,cycle)

def audit(q,k):
    cases=[];positive=empty=mutations=0
    for remote in product(range(q,q+k),repeat=k):
        T=tuple(range(1,q))+(0,)+remote
        edges=forced_edges(T)+event_edges(T,(0,1),2)
        cyc=tuple(range(q));n=q+k
        # The first assignment is the remote triangle negative control.
        exact=exhaustive_shadow(n,edges,cyc)
        colors=construct(n,edges)
        assert (colors is not None)==bool(exact)
        assert candidate(n,edges,cyc)==guarded_shadow(n,edges,cyc)==exact
        if colors is None:
            empty+=1
            assert not verify(n,edges,(0,)*n)
        else:
            positive+=1;assert verify(n,edges,colors)
            assert not verify(n,edges,colors[:-1])
            if any(p==1 for _,_,p in edges):
                u,_,_=next(e for e in edges if e[2]==1)
                bad=list(colors);bad[u]^=1
                assert not verify(n,edges,bad);mutations+=1
        cases.append((n,edges,cyc))
    times=[]
    for _ in range(3):
        trial=[]
        for fn in (guarded_shadow,candidate):
            start=perf_counter()
            for args in cases:fn(*args)
            trial.append(perf_counter()-start)
        times.append(trial)
    start=perf_counter()
    certificates=[construct(n,edges) for n,edges,_ in cases]
    construction=perf_counter()-start
    start=perf_counter()
    for (n,edges,_),certificate in zip(cases,certificates):verify(n,edges,certificate)
    validation=perf_counter()-start
    return dict(q=q,k=k,cases=len(cases),positive_certificates=positive,empty=empty,
                truncated_rejected=positive,edge_mutations_rejected=mutations,errors=0,
                seconds_reference_candidate=times,
                seconds_construction_validation=[construction,validation],
                retain_cost=all(c<r for r,c in times))
if __name__=='__main__':
    print(json.dumps(audit(4,3),sort_keys=True),flush=True)
    print(json.dumps(audit(6,4),sort_keys=True),flush=True)
