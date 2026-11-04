"""
Audit computationnel indépendant V8/V9.

- Vérifie la formule de comptage V8 contre un brute-force des colorations.
- Vérifie que, pour toute orbite de paire, le rang ne peut plus croître
  après sa première stagnation.

Les routines sont volontairement distinctes des scripts V8/V9 historiques.
"""
from itertools import product
from collections import deque, Counter
import random

def mobius(n):
    x=n; p=0; d=2
    while d*d<=x:
        if x%d==0:
            x//=d; p+=1
            if x%d==0:
                return 0
            while x%d==0:
                x//=d
        d+=1
    if x>1:
        p+=1
    return -1 if p%2 else 1

def primitive_count(m,r):
    return sum(mobius(d)*m**(r//d)
               for d in range(1,r+1) if r%d==0)

def falling(a,k):
    out=1
    for j in range(k):
        out*=a-j
    return out

def structure(T):
    n=len(T)
    indeg=[0]*n
    for y in T:
        indeg[y]+=1
    tmp=indeg[:]
    q=deque(i for i,d in enumerate(tmp) if d==0)
    periodic=[True]*n
    while q:
        x=q.popleft()
        periodic[x]=False
        y=T[x]
        tmp[y]-=1
        if tmp[y]==0:
            q.append(y)
    cycles=Counter()
    seen=set()
    for s in range(n):
        if periodic[s] and s not in seen:
            x=s; r=0
            while x not in seen:
                seen.add(x)
                r+=1
                x=T[x]
            cycles[r]+=1
    return indeg,periodic,cycles

def v8_formula(T,m):
    indeg,periodic,cycles=structure(T)
    ans=1
    for y,d in enumerate(indeg):
        if periodic[y]:
            ans*=falling(m-1,d-1)
        else:
            ans*=falling(m,d)
    for r,c in cycles.items():
        q=primitive_count(m,r)
        for j in range(c):
            ans*=q-j*r
    return ans

def brute_count(T,m):
    n=len(T)
    L=1 if n==1 else n-1
    ans=0
    for c in product(range(m),repeat=n):
        signatures=[]
        for x in range(n):
            y=x
            sig=[]
            for _ in range(L):
                sig.append(c[y])
                y=T[y]
            signatures.append(tuple(sig))
        if len(set(signatures))==n:
            ans+=1
    return ans

def audit_v8_exhaustive():
    checks=0
    for n in range(1,6):
        for T in product(range(n),repeat=n):
            for m in (1,2,3):
                checks+=1
                assert v8_formula(T,m)==brute_count(T,m)
    n=6; m=2
    for T in product(range(n),repeat=n):
        checks+=1
        assert v8_formula(T,m)==brute_count(T,m)
    return checks

def audit_pair_rank(T):
    n=len(T)
    for x in range(n):
        for y in range(x+1,n):
            parent=list(range(n))
            rank=0
            stalled=False
            def find(a):
                while parent[a]!=a:
                    parent[a]=parent[parent[a]]
                    a=parent[a]
                return a
            a,b=x,y
            for _ in range(2*n+2):
                before=rank
                if a!=b:
                    ra,rb=find(a),find(b)
                    if ra!=rb:
                        parent[rb]=ra
                        rank+=1
                inc=rank-before
                if inc==0:
                    stalled=True
                elif stalled:
                    return False
                a,b=T[a],T[b]
    return True

def audit_rank_exhaustive():
    total=0
    for n in range(1,7):
        for T in product(range(n),repeat=n):
            total+=1
            assert audit_pair_rank(T)
    return total

if __name__=="__main__":
    print("V8 comparisons:", audit_v8_exhaustive())
    print("Rank systems:", audit_rank_exhaustive())
