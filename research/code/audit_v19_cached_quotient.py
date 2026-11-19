"""Experimental signed quotient cached by the complete immutable transition tuple."""
from itertools import combinations,product
from time import perf_counter
import json
from test_v19_locality_l_plus_1 import forced_edges,event_edges,coherent
from audit_v19_shadow_guard import guarded_shadow,exhaustive_shadow

class ForcedCache:
    def __init__(self):self.key=None;self.builds=0
    def prepare(self,T):
        key=tuple(T)
        if key==self.key:return
        self.key=key;self.builds+=1;n=len(key)
        adj=[[] for _ in key]
        for u,v,p in forced_edges(key):adj[u].append((v,p));adj[v].append((u,p))
        self.component=[None]*n;self.offset=[0]*n;self.ok=True;self.count=0
        for root in range(n):
            if self.component[root] is not None:continue
            cid=self.count;self.count+=1;self.component[root]=cid;stack=[root]
            while stack:
                u=stack.pop()
                for v,p in adj[u]:
                    want=self.offset[u]^p
                    if self.component[v] is None:
                        self.component[v]=cid;self.offset[v]=want;stack.append(v)
                    elif self.offset[v]!=want:self.ok=False
    def query(self,T,event,cycle):
        self.prepare(T)
        if not self.ok:return frozenset()
        E=tuple((self.component[u],self.component[v],p^self.offset[u]^self.offset[v]) for u,v,p in event)
        if not coherent(self.count,E):return frozenset()
        adj=[[] for _ in range(self.count)]
        for u,v,p in E:adj[u].append((v,p));adj[v].append((u,p))
        result=set()
        for mask in range(1<<len(cycle)):
            colors={};ok=True
            for i,v in enumerate(cycle):
                root=self.component[v];want=((mask>>i)&1)^self.offset[v]
                if root in colors and colors[root]!=want:ok=False;break
                colors[root]=want
            stack=list(colors)
            while stack and ok:
                u=stack.pop()
                for v,p in adj[u]:
                    want=colors[u]^p
                    if v in colors:
                        if colors[v]!=want:ok=False;break
                    else:colors[v]=want;stack.append(v)
            if ok:result.add(mask)
        return frozenset(result)

def controls():
    cache=ForcedCache();T=[1,2,3,0,4,4,4];C=(0,1,2,3);E=event_edges(T,(0,1),2)
    assert not cache.query(T,E,C)
    T[4:]=[5,6,4]
    exact=exhaustive_shadow(7,forced_edges(T)+event_edges(T,(0,1),2),C)
    assert exact and cache.query(T,event_edges(T,(0,1),2),C)==exact and cache.builds==2
    assert cache.query(T,((0,1,0),(0,1,1)),C)==frozenset()
    return dict(mutation_invalidated=True,event_contradiction_rejected=True)

def audit(q,k):
    cases=[];cache=ForcedCache();empty=0
    for remote in product(range(q,q+k),repeat=k):
        T=tuple(range(1,q))+(0,)+remote;F=forced_edges(T);C=tuple(range(q))
        for pair in combinations(range(q+k),2):
            for L in (2,3):
                E=event_edges(T,pair,L)
                exact=exhaustive_shadow(q+k,F+E,C)
                assert guarded_shadow(q+k,F+E,C)==cache.query(T,E,C)==exact
                empty+=not exact;cases.append((T,F,E,C))
    times=[]
    for _ in range(3):
        start=perf_counter()
        for T,F,E,C in cases:guarded_shadow(len(T),F+E,C)
        baseline=perf_counter()-start
        cached=ForcedCache();start=perf_counter()
        for T,F,E,C in cases:cached.query(T,E,C)
        candidate=perf_counter()-start
        times.append([baseline,candidate])
    return dict(q=q,k=k,systems=(q and k**k),queries=len(cases),empty=empty,errors=0,
                cache_builds=cached.builds,seconds_reference_candidate=times,
                retain=all(c<r for r,c in times))
if __name__=='__main__':
    print(json.dumps(dict(controls=controls())),flush=True)
    print(json.dumps(dict(split='train',**audit(4,3))),flush=True)
    print(json.dumps(dict(split='reserve',**audit(5,4))),flush=True)
