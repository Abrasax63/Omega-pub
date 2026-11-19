"""Check which forced components can meet a distinguished cycle."""
from itertools import product,combinations
from time import perf_counter
import json
from test_v19_locality_l_plus_1 import forced_edges,event_edges
from audit_v19_shadow_guard import guarded_shadow,exhaustive_shadow
from audit_v19_cached_quotient import ForcedCache

def components(n,edges):
    adj=[[] for _ in range(n)]
    for u,v,_ in edges:adj[u].append(v);adj[v].append(u)
    seen=set();out=[]
    for u in range(n):
        if u in seen:continue
        seen.add(u);stack=[u];part={u}
        while stack:
            for v in adj[stack.pop()]:
                if v not in seen:seen.add(v);part.add(v);stack.append(v)
        out.append(part)
    return out

def audit(q,k):
    n=q+k;C=tuple(range(q));cycle=set(C);cases=[];maximum=0;fiber_errors=0
    for images in product(range(n),repeat=k):
        T=tuple(range(1,q))+(0,)+images;F=forced_edges(T)
        parts=components(n,F)
        maximum=max(maximum,max(len(p&cycle) for p in parts))
        for x in C:
            expected={u for u in range(n) if T[u]==T[x]}
            observed=next(p for p in parts if x in p)
            fiber_errors+=observed!=expected
        assert maximum<=1 and fiber_errors==0
        for pair in combinations(range(n),2):
            for L in (2,3):cases.append((T,F,event_edges(T,pair,L),C))
    cache=ForcedCache();empty=0
    for T,F,E,C in cases:
        exact=exhaustive_shadow(n,F+E,C)
        assert guarded_shadow(n,F+E,C)==cache.query(T,E,C)==exact
        empty+=not exact
    seconds=[]
    start=perf_counter()
    for T,F,E,C in cases:guarded_shadow(n,F+E,C)
    seconds.append(perf_counter()-start)
    cache=ForcedCache();start=perf_counter()
    for T,F,E,C in cases:cache.query(T,E,C)
    seconds.append(perf_counter()-start)
    return dict(q=q,k=k,systems=n**k,maximum_cycle_vertices_in_forced_component=maximum,
                fiber_identity_errors=fiber_errors,projections=len(cases),shadow_errors=0,
                empty=empty,seconds_reference_cache=seconds)
if __name__=='__main__':
    C={0,1,2,3}
    assert max(len(p&C) for p in components(4,((0,1,1),)))==2
    T=(1,2,3,0);F=forced_edges(T);E=event_edges(T,(0,1),2)
    hits=max(len(p&C) for p in components(4,F+E));assert hits==3
    print(json.dumps(dict(negative_control_detected=True,cycle_vertices_joined_by_event=hits)),flush=True)
    print(json.dumps(dict(split='train',**audit(3,2))),flush=True)
    print(json.dumps(dict(split='reserve',**audit(4,3))),flush=True)
