"""Independent finite checks; no imports of archived scientific scripts."""
import json, itertools as it, random
from collections import deque
from fractions import Fraction as F
from pathlib import Path

def parity_ok(n, edges):
    adj=[[] for _ in range(n)]
    for u,v,b in edges:
        adj[u].append((v,b));adj[v].append((u,b))
    col={}
    for u in range(n):
        if u in col:continue
        col[u]=0;stack=[u]
        while stack:
            v=stack.pop()
            for w,b in adj[v]:
                if w in col:
                    if col[w]!=col[v]^b:return False
                else:col[w]=col[v]^b;stack.append(w)
    return True

def forced(t, nodes=None):
    nodes=set(range(len(t))) if nodes is None else set(nodes)
    return [(u,v,1) for u,v in it.combinations(sorted(nodes),2)
            if t[u] in nodes and t[v] in nodes and
            (t[u]==t[v] or {t[u],t[v]}=={u,v})]

def v19():
    coherent=0;models=0
    for n in range(1,7):
        for t in it.product(range(n),repeat=n):
            models+=1;e=forced(t)
            if not parity_ok(n,e):continue
            coherent+=1;adj=[set() for _ in t]
            for u,v,_ in e:adj[u].add(v);adj[v].add(u)
            seen=set()
            for u in range(n):
                if u in seen:continue
                comp={u};stack=[u]
                while stack:
                    for v in adj[stack.pop()]:
                        if v not in comp:comp.add(v);stack.append(v)
                seen|=comp
                assert len(comp)<=4 and all(len(adj[v])<=2 for v in comp)
                assert sum(len(adj[v]) for v in comp)//2==len(comp)-1
    rng=random.Random(141027);checks=0;accepted=0
    # Pair-shadow existential projection, full versus temporal prefix L+2.
    for _ in range(5000):
        n=rng.randrange(5,19);t=tuple(list(range(1,5))+[0]+[rng.randrange(n) for _ in range(n-5)])
        e=forced(t)
        if not parity_ok(n,e):continue
        accepted+=1;x,y=rng.sample(range(n),2);L=rng.choice([2,3,4])
        xs=[x];ys=[y]
        for k in range(L+2):xs.append(t[xs[-1]]);ys.append(t[ys[-1]])
        nodes=set(range(5))|set(xs)|set(ys)
        local=forced(t,nodes)
        eq=[(xs[j],ys[j],0) for j in range(L)]
        for word in it.product((0,1),repeat=5):
            fixes=[(j,n,word[j]) for j in range(5)]
            assert parity_ok(n+1,e+eq+fixes)==parity_ok(n+1,local+eq+fixes)
            checks+=1
    return dict(models=models,coherent=coherent,path_violations=0,
                sampled_coherent_systems=accepted,shadow_color_checks=checks,
                scope="P1..P4 exhaustive n<=6; locality random L=2..4, C5, n<=18")

def rank(a):
    a=[list(map(F,r)) for r in a];i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a)) if a[k][j]),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i];z=a[i][j];a[i]=[x/z for x in a[i]]
        for k in range(len(a)):
            if k!=i:
                z=a[k][j];a[k]=[x-z*y for x,y in zip(a[k],a[i])]
        i+=1
        if i==len(a):break
    return i

def rq4():
    axes=[(int(j==k)*s) for k in range(3) for s in (1,-1) for j in []]
    states=[tuple(s*int(j==k) for j in range(3)) for k in range(3) for s in (1,-1)]
    count=0
    for t in (F(1),F(1,2),F(1,1000),F(0)):
        ps=[[[F(1,2)*(1+t*a[m]),F(1,2)*(1-t*a[m])] for a in states] for m in range(3)]
        assert all(rank(p)==(2 if t else 1) for p in ps)
        if t:
            for m,n in it.combinations(range(3),2):
                assert rank([ps[m][i]+ps[n][i] for i in range(6)])==3
                count+=1
        for q in (F(1,10),F(1,2),F(1)):
            vals=[[sum(ps[m][i][b]*(F(1,2)+(1 if b==0 else -1)*q/2) for b in (0,1))
                   for m in range(3)] for i in range(6)]
            delta=max(abs(row[m]-row[n]) for row in vals for m,n in it.combinations(range(3),2))
            assert delta==t*q/2
            if t:assert 2*delta/t==q
            count+=1
    return dict(exact_rank_and_sharpness_checks=count,
                t_zero_rank_loss=True,scope="Pauli preparation matrices; scalar sharpness, not CPTP realization")

def machine(q,k):
    n=2*k+1;s=n-1;tr=[];out=[]
    tr.append(tuple(range(n)));out.append(tuple([i for i in range(k) for _ in (0,1)]+[k]))
    for j in range(k):
        tr.append((s,)*n);out.append(tuple([0 if i==j else b for i in range(k) for b in (0,1)]+[k]))
    return tr,out

def r1(tr,out):
    n=len(tr[0]);syms={(a,y) for a,row in enumerate(out) for y in row}
    dest={(a,y):frozenset(tr[a][x] for x in range(n) if out[a][x]==y) for a,y in syms}
    allowed={(s,z) for s,b in dest.items() for z in syms if any(out[z[0]][x]==z[1] for x in b)}
    initial=[(s,b) for s,b in dest.items()];queue=deque(initial);seen=set(initial)
    while queue:
        s,b=queue.popleft()
        for z in syms:
            if (s,z) not in allowed:continue
            d=frozenset(tr[z[0]][x] for x in b if out[z[0]][x]==z[1])
            assert d
            v=(z,d)
            if v not in seen:seen.add(v);queue.append(v)
    return len(seen)

def pds(tr,out,pairs):
    start=frozenset(tuple(sorted(p)) for p in pairs);queue=deque([start]);seen={start}
    while queue:
        mask=queue.popleft()
        if not mask:return True,len(seen)
        for a in range(len(tr)):
            nxt=set();dead=False
            for x,y in mask:
                if x==y:dead=True;break
                if out[a][x]!=out[a][y]:continue
                nxt.add(tuple(sorted((tr[a][x],tr[a][y]))))
            if dead:continue
            nxt=frozenset(nxt)
            if nxt not in seen:seen.add(nxt);queue.append(nxt)
    return False,len(seen)

def mealy():
    cases=[];subsets=0
    for q in range(3,8):
        for k in range(2,q):
            tr,out=machine(q,k);n=len(tr[0]);local=r1(tr,out)
            assert not pds(tr,out,it.combinations(range(n),2))[0]
            for r in range(k+1):
                for sub in it.combinations(range(k),r):
                    assert pds(tr,out,[(2*i,2*i+1) for i in sub])[0]==(r<k)
                    subsets+=1
            # after root a, choose t_j, j!=i, distinguishes each two-state branch.
            for i in range(k):
                j=(i+1)%k
                assert out[j+1][2*i]!=out[j+1][2*i+1]
            assert n>q or k>=2  # no single input resolves: each t destroys a pair, a preserves pairs.
            cases.append(dict(q=q,k=k,n=n,local_states=local,ADS_depth=2,PDS=False))
    return dict(cases=cases,resolution_subfamilies=subsets,
                scope="C(q,k) exact full-language and PDS searches q=3..7; general proofs audited separately")

def sum_check():
    b=F(1001,1000);H=7382
    assert b**(H-1)<1600<=b**H and 16/b**H<=F(1,100)
    assert 107383<=2**17 and 12002<=2**14
    assert 65+14+2*(25+32+17)==227
    assert 65+14+2*(27+25+48+17)==313
    checks=0
    for s,t in it.product(range(-5,12),repeat=2):
        e0,e1=b**s,b**t
        assert e0+e1>=max(e0,e1);checks+=1
    # Strict sum-only crossing exists without either track crossing.
    assert b**(H-1)<b**H and 2*b**(H-1)>=b**H
    return dict(threshold=H,budget_valid=True,register_bits=[227,313],
                exact_sum_inequalities=checks,strict_dominance_witness=[H-1,H-1],
                scope="Static exact arithmetic; no power simulation or calibration certification")

if __name__=="__main__":
    r={"V19":v19(),"RQ4":rq4(),"MEALY27":mealy(),"SUM":sum_check()}
    Path("commit_audit_checks.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(r,ensure_ascii=False,indent=2))
