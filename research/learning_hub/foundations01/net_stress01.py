"""NET-STRESS01: exact Boolean factor elimination with a hard factor cap."""
import itertools as it
import json,random,time
from collections import Counter
from pathlib import Path
CAP=1<<16
OPS=("xor","and","or","implies")
def op(kind,a,b=0):
    if kind=="pin":return a
    if kind=="xor":return a^b
    if kind=="and":return a&b
    if kind=="or":return a|b
    if kind=="implies":return int(not a or b)
    raise ValueError("RELATION")
def allowed(c,assignment):
    kind,vs,y=c
    return op(kind,*[assignment[v] for v in vs])==y
def factor(c):
    kind,vs,y=c
    return tuple(vs),tuple(int(op(kind,*[(x>>i)&1 for i in range(len(vs))])==y) for x in range(1<<len(vs)))
def eliminate(n,cs,ordering,cap=CAP):
    factors=[factor(c) for c in cs]
    # Every variable contributes two choices, including isolated ones.
    factors.extend(((v,),(1,1)) for v in range(n))
    remaining=set(range(n));peak=max(len(t) for _,t in factors);width=0;trace=[]
    while remaining:
        neighbors={v:set() for v in remaining}
        for vs,_ in factors:
            for v in vs:neighbors[v].update(u for u in vs if u!=v)
        if ordering=="minfill":
            v=min(remaining,key=lambda v:(sum(b not in neighbors[a] for a,b in it.combinations(sorted(neighbors[v]),2)),len(neighbors[v]),v))
        elif ordering=="fixed":v=min(remaining)
        else:raise ValueError("ORDER")
        bucket=[f for f in factors if v in f[0]]
        scope=sorted(set().union(*(set(s) for s,_ in bucket)))
        width=max(width,len(scope)-1)
        required=1<<len(scope)
        if required>cap:
            return dict(status="RESOURCE_LIMIT",count=None,peak=peak,width=width,required_entries=required,trace=trace)
        peak=max(peak,required)
        rest=tuple(x for x in scope if x!=v)
        # Index maps for each local factor, including arbitrary orientation.
        vi=scope.index(v);positions=[scope.index(x) for x in rest]
        maps=[([scope.index(u) for u in s],t) for s,t in bucket]
        table=[]
        for x in range(1<<len(rest)):
            a=sum(((x>>j)&1)<<p for j,p in enumerate(positions))
            total=0
            for bit in (0,1):
                z=a|(bit<<vi);prod=1
                for ps,t in maps:
                    idx=sum(((z>>p)&1)<<i for i,p in enumerate(ps))
                    prod*=t[idx]
                    if prod==0:break
                total+=prod
            table.append(total)
        factors=[f for f in factors if v not in f[0]]
        factors.append((rest,tuple(table)));remaining.remove(v)
        trace.append((v,len(scope),len(table)))
    count=1
    for s,t in factors:
        assert not s and len(t)==1
        count*=t[0]
    return dict(status="EXACT",count=count,peak=peak,width=width,trace=trace)
def infer(n,cs,order):
    start=time.perf_counter()
    a=eliminate(n,cs,order)
    if a["status"]!="EXACT":
        return dict(status="RESOURCE_LIMIT",base=a,seconds=time.perf_counter()-start)
    b=eliminate(n,cs+[("pin",(0,),1)],order)
    if b["status"]!="EXACT":
        return dict(status="RESOURCE_LIMIT",base=a,pinned=b,seconds=time.perf_counter()-start)
    total,ones=a["count"],b["count"]
    assert 0<=ones<=total
    bit=None if total==0 or 0<ones<total else int(ones==total)
    return dict(status="UNSAT" if total==0 else "EXACT",count=total,ones=ones,forced=bit,base=a,pinned=b,seconds=time.perf_counter()-start)
def brute(n,cs):
    total=ones=0
    for x in range(1<<n):
        if all(op(k,*[(x>>v)&1 for v in vs])==y for k,vs,y in cs):
            total+=1;ones+=x&1
    return total,ones

def transfer(rows,cs,force=None,wrap=False):
    """Independent row transfer, using predicates not factor products.
    For ring with one bit per row, retain first row state to enforce closure.
    """
    loc={v:(i,j) for i,r in enumerate(rows) for j,v in enumerate(r)}
    internal=[[] for _ in rows];cross=[[] for _ in rows];closing=[]
    for c in cs+([] if force is None else [("pin",(0,),force)]):
        ids=sorted(set(loc[v][0] for v in c[1]))
        if len(ids)==1:internal[ids[0]].append(c)
        elif wrap and ids==[0,len(rows)-1]:closing.append(c)
        else:
            assert ids[1]==ids[0]+1
            cross[ids[1]].append(c)
    def val(c,i,x,j=None,y=None):
        k,vs,b=c;bits=[]
        for v in vs:
            row,col=loc[v]
            assert row==i or row==j
            bits.append(((x if row==i else y)>>col)&1)
        return op(k,*bits)==b
    legal=[[x for x in range(1<<len(r)) if all(val(c,i,x) for c in internal[i])] for i,r in enumerate(rows)]
    if not all(legal):return 0
    starts=legal[0] if wrap else [None];total=0
    for first in starts:
        dp={x:1 for x in legal[0] if first is None or x==first}
        for i in range(1,len(rows)):
            nxt={}
            for y in legal[i]:
                count=sum(a for x,a in dp.items() if all(val(c,i-1,x,i,y) for c in cross[i]))
                if count:nxt[y]=count
            dp=nxt
            if not dp:break
        total+=sum(a for x,a in dp.items() if all(val(c,0,first,len(rows)-1,x) for c in closing))
    return total
def world(rng,n,kind,idx,side=None):
    labels=list(range(n));rng.shuffle(labels)
    if kind=="grid":
        rows=[labels[i:i+side] for i in range(0,n,side)]
        edges=[(rows[i][j],rows[i][j+1]) for i in range(side) for j in range(side-1)]
        edges += [(rows[i][j],rows[i+1][j]) for i in range(side-1) for j in range(side)]
    else:
        rows=[[x] for x in labels]
        if kind in ("path","ring"):edges=list(zip(labels,labels[1:]))+([(labels[-1],labels[0])] if kind=="ring" else [])
        elif kind=="random":edges=rng.sample(list(it.combinations(labels,2)),min(n*2,n*(n-1)//2))
        elif kind=="dense":edges=list(it.combinations(labels,2))
        else:raise ValueError("KIND")
    hidden=[rng.randrange(2) for _ in range(n)]
    cs=[]
    for a,b in edges:
        k=rng.choice(OPS if kind!="dense" else ("and","xor"))
        cs.append((k,(a,b),op(k,hidden[a],hidden[b])))
    if kind!="dense" and idx%2:
        v=rng.randrange(n);cs.extend([("pin",(v,),0),("pin",(v,),1)])
    assert all(allowed(c,hidden) for c in cs) if not (kind!="dense" and idx%2) else True
    return rows,cs
def main(out):
    rng=random.Random(20261207);cases=[]
    for n in (8,12,16):
        for k in ("path","ring","random"):
            for i in range(4):cases.append((n,k,i,*world(rng,n,k,i),"brute"))
    for n in (32,64,128):
        for k in ("path","ring"):
            for i in range(4):cases.append((n,k,i,*world(rng,n,k,i),"transfer"))
    for side in (4,6,8):
        for i in range(4):cases.append((side**2,"grid",i,*world(rng,side**2,"grid",i,side),"transfer"))
    for n in (8,32,128):
        rows=[[i] for i in range(n)]
        cs=[("xor",(i,i+1),0) for i in range(n-1)]+[("xor",(n-1,0),1)]
        cases.append((n,"odd_cycle",0,rows,cs,"transfer"))
    for n in (18,24):cases.append((n,"dense",0,*world(rng,n,"dense",0),"none"))
    records=[];stats={o:Counter() for o in ("minfill","fixed")}
    for n,k,i,rows,cs,ref_kind in cases:
        start=time.perf_counter()
        if ref_kind=="brute":ref=brute(n,cs)
        elif ref_kind=="transfer":
            wrap=k in ("ring","odd_cycle")
            ref=(transfer(rows,cs,wrap=wrap),transfer(rows,cs,force=1,wrap=wrap))
        else:ref=None
        ref_seconds=time.perf_counter()-start
        if k=="odd_cycle":assert ref==(0,0)
        for order in stats:
            r=infer(n,cs,order);s=stats[order];s["cases"]+=1
            s["resource_limit"]+=int(r["status"]=="RESOURCE_LIMIT")
            assert r["base"]["peak"]<=CAP and r.get("pinned",{}).get("peak",0)<=CAP
            if r["status"]!="RESOURCE_LIMIT":
                assert ref is not None and (r["count"],r["ones"])==ref
                s["exact"]+=1;s["unsat"]+=int(r["status"]=="UNSAT")
                s["forced"]+=int(r["forced"] is not None)
            if order=="minfill" and ref is not None:assert r["status"]!="RESOURCE_LIMIT"
            s["max_peak"]=max(s["max_peak"],r["base"]["peak"],r.get("pinned",{}).get("peak",0))
            records.append(dict(n=n,kind=k,index=i,order=order,reference=ref,reference_seconds=ref_seconds,**r))
            print("NET_CASE",n,k,i,order,r["status"],"peak",r["base"]["peak"],"width",r["base"]["width"],"seconds",r["seconds"],flush=True)
    result=dict(stats=stats,cases=len(cases),cap=CAP,passed=True,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("NET_STRESS_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
