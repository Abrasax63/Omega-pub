#!/usr/bin/env python3
"""Independent direct-coloring audit of C4,L=2; no DSU/parity data structure.
The code enumerates canonical two-trajectory functional prefixes and, separately,
all globally coherent endofunctions N=4..8 with local color assignments.
"""
from itertools import product
from collections import Counter
Q=4; L=2; DEPTH=L+2; CYCLE=tuple(range(Q))
TARGETS={
 (0,7,8,15),(0,5,10,15),(2,7,8,13),(1,6,9,14),
 (0,3,4,7,8,11,12,15),(0,1,4,5,10,11,14,15),
 (4,5,6,7,8,9,10,11),(2,3,6,7,8,9,12,13)
}

def rotate(mask,k):
    return sum(((mask>>i)&1)<<((i+k)%Q) for i in range(Q))
def canon(S):
    return min(tuple(sorted(rotate(m,k) for m in S)) for k in range(Q))

def enumerate_local_diagrams():
    out=[]
    for a in range(Q+1):
        hi=max(Q-1,a)
        for b in range(hi+2):
            if a==b: continue
            f={i:(i+1)%Q for i in range(Q)}
            def rec(t,A,B,F,max_label):
                if t==DEPTH:
                    out.append((A,B,F))
                    return
                u,v=A[-1],B[-1]
                ach=(F[u],) if u in F else range(max_label+2)
                for an in ach:
                    FA=F if u in F else {**F,u:an}
                    mA=max(max_label,an)
                    bch=(FA[v],) if v in FA else range(mA+2)
                    for bn in bch:
                        FB=FA if v in FA else {**FA,v:bn}
                        rec(t+1,A+(an,),B+(bn,),FB,max(mA,bn))
            rec(0,(a,),(b,),f,hi if b<=hi else b)
    return out

def local_shadow(diagram):
    A,B,F=diagram
    nodes=sorted(set(A)|set(B)|set(CYCLE)); pos={u:i for i,u in enumerate(nodes)}
    neq=[]
    for i,u in enumerate(nodes):
        for v in nodes[i+1:]:
            if u in F and v in F and (F[u]==F[v] or {F[u],F[v]}=={u,v}):
                neq.append((pos[u],pos[v]))
    eq=[(pos[A[t]],pos[B[t]]) for t in range(L) if A[t]!=B[t]]
    cycle_pos=[pos[i] for i in CYCLE]
    out=set()
    for z in range(1<<len(nodes)):
        if any(((z>>i)^(z>>j))&1 == 0 for i,j in neq): continue
        if any(((z>>i)^(z>>j))&1 == 1 for i,j in eq): continue
        out.add(sum(((z>>p)&1)<<i for i,p in enumerate(cycle_pos)))
    return frozenset(out)

def coherent(F):
    n=len(F)
    if max(F.count(j) for j in range(n))>2: return False
    adj=[[] for _ in range(n)]
    for u in range(n):
        for v in range(u+1,n):
            if F[u]==F[v] or {F[u],F[v]}=={u,v}:
                adj[u].append(v); adj[v].append(u)
    color=[-1]*n
    for s in range(n):
        if color[s]>=0: continue
        color[s]=0; stack=[s]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if color[v]<0: color[v]=1-color[u]; stack.append(v)
                elif color[v]==color[u]: return False
    return True

def local_shadow_for_map(F,x,y):
    A=[x]; B=[y]
    for _ in range(DEPTH): A.append(F[A[-1]]); B.append(F[B[-1]])
    return local_shadow((tuple(A),tuple(B),{u:F[u] for u in set(A[:-1])|set(B[:-1])|set(CYCLE)}))

# Part I: independent complete enumeration of all local trajectory diagrams.
diagrams=enumerate_local_diagrams()
shadows=[local_shadow(d) for d in diagrams]
proper=[s for s in shadows if s and len(s)<(1<<Q)]
classes={canon(s) for s in proper}
class_counts=Counter(canon(s) for s in proper)
assert len(diagrams)==1515, len(diagrams)
assert len(proper)==172, len(proper)
assert len(classes)==8, len(classes)
assert Counter(map(len,classes))==Counter({4:4,8:4})
assert classes=={canon(s) for s in TARGETS}, (classes,{canon(s) for s in TARGETS})
print('LOCAL_CATALOGUE diagrams=1515 proper=172 rotation_classes=8 sizes={4:4,8:4}')
for c,n in sorted(class_counts.items()): print('LOCAL_CLASS',len(c),c,'diagrams=',n)

# Part II: exact global coherence, but shadows computed by local color enumeration.
TARGET_CANON={canon(s) for s in TARGETS}
# Cross-check local-prefix projection against full global colorings on the 9-state witness.
W=(1,2,3,0,8,7,6,2,0)
def global_shadow(F,x,y):
    A=[x]; B=[y]
    for _ in range(L): A.append(F[A[-1]]); B.append(F[B[-1]])
    neq=[(u,v) for u in range(len(F)) for v in range(u+1,len(F)) if F[u]==F[v] or {F[u],F[v]}=={u,v}]
    out=set()
    for z in range(1<<len(F)):
        if any(((z>>u)^(z>>v))&1==0 for u,v in neq): continue
        if any(((z>>A[t])^(z>>B[t]))&1 for t in range(L) if A[t]!=B[t]): continue
        out.add(sum(((z>>i)&1)<<i for i in CYCLE))
    return frozenset(out)
for x in range(len(W)):
    for y in range(x+1,len(W)):
        assert local_shadow_for_map(W,x,y)==global_shadow(W,x,y), (x,y)
print('LOCAL/GLOBAL witness cross-check PASS: all 36 pairs agree.')

rows=[]
for n in range(4,9):
    total=n**(n-4); nc=0; found=False
    for tail in product(range(n),repeat=n-4):
        F=(1,2,3,0)+tail
        if not coherent(list(F)): continue
        nc+=1; seen=set()
        for x in range(n):
            for y in range(x+1,n):
                S=local_shadow_for_map(F,x,y)
                if S: seen.add(canon(S))
                if len(seen)==8: break
            if len(seen)==8: break
        if seen==TARGET_CANON:
            found=True; break
    rows.append((n,total,nc,found))
    print(f'LOCAL_ENUM N={n}: total={total}, coherent={nc}, witness={found}',flush=True)
    assert not found, (n,F)
assert rows==[(4,1,1,False),(5,5,5,False),(6,36,32,False),(7,343,263,False),(8,4096,2695,False)],rows
print('PASS: independent local-coloring audit; all eight target classes absent for N<=8.')
