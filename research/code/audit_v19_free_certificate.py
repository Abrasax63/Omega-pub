"""Check a graph certificate for a full shadow against all binary assignments."""
from collections import Counter
from itertools import product
from time import perf_counter
from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import coherent, forced_edges, event_edges

def full_shadow_certificate(n, constraints, cycle):
    adjacent=[[] for _ in range(n)]
    for u,v,parity in constraints:
        adjacent[u].append((v,parity))
        adjacent[v].append((u,parity))
    colors={}
    cycle=set(cycle)
    for root in range(n):
        if root in colors:
            continue
        colors[root]=0
        stack=[root]
        cycle_count=0
        while stack:
            u=stack.pop()
            cycle_count+=u in cycle
            for v,parity in adjacent[u]:
                wanted=colors[u]^parity
                if v in colors:
                    if colors[v]!=wanted:
                        return False
                else:
                    colors[v]=wanted
                    stack.append(v)
        if cycle_count>1:
            return False
    return True

def check_controls():
    for constraints,expected in [
        (((0,1,0),(0,1,1)),False),
        (((0,1,0),),False),
        (((0,2,1),(1,3,0)),True),
    ]:
        assert full_shadow_certificate(4,constraints,(0,1))==expected
        assert (len(exhaustive_shadow(4,constraints,(0,1)))==4)==expected
    print("controls",3)

def audit(q,L):
    n=q+2*(L+1)+1
    cycle=tuple(range(q))
    paths=(tuple(range(q,q+L+1)),tuple(range(q+L+1,q+2*(L+1))))
    ends=tuple(p[-1] for p in paths)
    free=n-1
    fixed={v:(v+1)%q for v in cycle}
    for path in paths:
        fixed.update(zip(path,path[1:]))
    counts=Counter()
    seconds=[0.,0.]
    for read,unread in (ends,ends[::-1]):
        for a,b in product(range(n),repeat=2):
            T=tuple((fixed|{read:free,unread:a,free:b})[v] for v in range(n))
            F=forced_edges(T)
            if not coherent(n,F):
                continue
            constraints=F+event_edges(T,tuple(p[0] for p in paths),L)
            start=perf_counter()
            certificate=full_shadow_certificate(n,constraints,cycle)
            seconds[0]+=perf_counter()-start
            start=perf_counter()
            shadow=exhaustive_shadow(n,constraints,cycle)
            seconds[1]+=perf_counter()-start
            exact=len(shadow)==2**q
            counts["cases"]+=1
            counts["accepted"]+=certificate
            counts["false_accepts"]+=certificate and not exact
            counts["false_rejects"]+=not certificate and exact
    print("family",q,L,n,dict(counts),"seconds",*[round(x,6) for x in seconds])
    assert counts["false_accepts"]==counts["false_rejects"]==0

if __name__=="__main__":
    check_controls()
    audit(4,3)
    audit(5,2)
