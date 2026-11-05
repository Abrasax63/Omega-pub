#!/usr/bin/env python3
"""Targeted adversarial audit of V19 L+2 visibility edge cases.

Enumerates all endofunction extensions in the stated finite domain and
classifies:
  (A) P4 components whose two leaves are both bad-event trajectory anchors;
  (B) fixed-point I-pairs with exactly one endpoint in the visible prefix;
  (C) bad-event equalities joining distinct forced components.
For every pair/horizon, checks global-vs-local shadow using parity DSU.
This is finite falsification, not a general proof.
"""
from itertools import combinations, product


def forced(T):
    return [(u,v) for u,v in combinations(range(len(T)),2)
            if T[u]==T[v] or {T[u],T[v]}=={u,v}]


def components(n, edges):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v); adj[v].append(u)
    comp=[-1]*n; groups=[]
    for root in range(n):
        if comp[root]>=0: continue
        k=len(groups); stack=[root]; comp[root]=k; group=[]
        while stack:
            u=stack.pop(); group.append(u)
            for v in adj[u]:
                if comp[v]<0: comp[v]=k; stack.append(v)
        groups.append(group)
    return comp,groups,adj


def bipartite(n,edges):
    _,_,adj=components(n,edges)
    col={}
    for s in range(n):
        if s in col: continue
        col[s]=0; stack=[s]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v in col:
                    if col[v]==col[u]: return False
                else: col[v]=1-col[u]; stack.append(v)
    return True


def shadow(T,pair,L,q,allowed=None):
    n=len(T); allowed=set(range(n)) if allowed is None else set(allowed)
    par=list(range(n)); rank=[0]*n; xr=[0]*n; bad=False
    def find(x):
        if par[x]!=x:
            root,d=find(par[x]); xr[x]^=d; par[x]=root
        return par[x],xr[x]
    def join(a,b,d):
        nonlocal bad
        ra,xa=find(a); rb,xb=find(b)
        if ra==rb:
            if xa^xb!=d: bad=True
            return
        if rank[ra]<rank[rb]: ra,rb=rb,ra; xa,xb=xb,xa
        par[rb]=ra; xr[rb]=xa^xb^d
        if rank[ra]==rank[rb]: rank[ra]+=1
    for a,b in forced(T):
        if a in allowed and b in allowed: join(a,b,1)
    a,b=pair
    for _ in range(L):
        if a!=b: join(a,b,0)
        a,b=T[a],T[b]
    if bad: return frozenset()
    roots=[find(i) for i in range(q)]
    return frozenset(m for m in range(1<<q) if all(
        roots[i][0]!=roots[j][0] or
        (((m>>i)&1)^((m>>j)&1))==(roots[i][1]^roots[j][1])
        for i,j in combinations(range(q),2)))


def prefix(T,pair,L,q):
    p=set(range(q)); a,b=pair
    for _ in range(L+3):
        p.update((a,b)); a,b=T[a],T[b]
    return p


def run():
    totals={"extensions":0,"coherent":0,"comparisons":0,
            "P4_both_leaves_anchors":0,"fixed_I_exactly_one_visible":0,
            "equalities_cross_forced_components":0}
    witnesses={}
    for q in range(3,7):
        base=tuple((i+1)%q for i in range(q))
        for n in range(q,q+5):
            for tail in product(range(n),repeat=n-q):
                T=base+tail; totals["extensions"]+=1
                E=forced(T)
                if not bipartite(n,E): continue
                totals["coherent"]+=1
                cid,groups,adj=components(n,E)
                for L in (2,3,4,5):
                    for pair in combinations(range(n),2):
                        P=prefix(T,pair,L,q)
                        R=set(range(q)); a,b=pair
                        for _ in range(L):
                            R.update((a,b)); a,b=T[a],T[b]
                        totals["comparisons"]+=1
                        full=shadow(T,pair,L,q)
                        local=shadow(T,pair,L,q,P)
                        if full!=local:
                            raise AssertionError(("LOCALITY COUNTEREXAMPLE",q,n,T,L,pair,sorted(P),sorted(full),sorted(local)))
                        # A: a P4 whose two degree-one leaves are both E-anchors.
                        for g in groups:
                            if len(g)!=4: continue
                            deg={v:sum(1 for w in adj[v] if w in g) for v in g}
                            leaves=[v for v in g if deg[v]==1]
                            if len(leaves)==2 and all(v in R for v in leaves):
                                key="P4_both_leaves_anchors"; totals[key]+=1
                                witnesses.setdefault(key,(q,n,T,L,pair,sorted(g),sorted(R),sorted(P)))
                        # B: fixed-point I edge, exactly one endpoint in visible P.
                        for u,v in E:
                            if T[u]==u and T[v]==v and ((u in P) != (v in P)):
                                key="fixed_I_exactly_one_visible"; totals[key]+=1
                                witnesses.setdefault(key,(q,n,T,L,pair,(u,v),sorted(P)))
                        # C: at least one E equality joins different forced components.
                        a,b=pair
                        for _ in range(L):
                            if a!=b and cid[a]!=cid[b]:
                                key="equalities_cross_forced_components"; totals[key]+=1
                                witnesses.setdefault(key,(q,n,T,L,pair,(a,b),cid[a],cid[b]))
                            a,b=T[a],T[b]
    assert totals["extensions"]==4258, totals
    assert totals["coherent"]==1582, totals
    assert totals["comparisons"]==173680, totals
    for k in ("P4_both_leaves_anchors","fixed_I_exactly_one_visible","equalities_cross_forced_components"):
        assert totals[k]>0, (k,totals,witnesses)
    print("COUNTS",totals)
    for k,v in witnesses.items(): print("WITNESS",k,v)
    print("PASS: no global/local shadow mismatch in targeted finite domain.")
    print("PASS: all three adversarial edge cases occurred and were checked.")

if __name__=="__main__": run()
