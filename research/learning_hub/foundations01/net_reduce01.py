"""NET-REDUCE01: exact unary/parity substitutions, independent references."""
import itertools as it
import json,random,time
from collections import Counter
from pathlib import Path
from net_stress01 import eliminate,op,world,brute,transfer,CAP

class DSU:
    def __init__(self,n):
        self.p=list(range(n+1));self.d=[0]*(n+1);self.n=n
    def find(self,x):
        if self.p[x]!=x:
            r,d=self.find(self.p[x]);self.d[x]^=d;self.p[x]=r
        return self.p[x],self.d[x]
    def join(self,a,b,v):
        ra,da=self.find(a);rb,db=self.find(b)
        if ra==rb:return 0 if da^db==v else -1
        # Keep constant n as root if involved; otherwise lower index.
        if ra==self.n or (rb!=self.n and ra<rb):ra,rb=rb,ra
        self.p[ra]=rb;self.d[ra]=da^db^v
        return 1

def relation(d,c):
    k,vs,y=c
    locations=[d.find(v) for v in vs]
    roots=tuple(sorted({r for r,_ in locations if r!=d.n}))
    good=[]
    for bits in it.product((0,1),repeat=len(roots)):
        a=dict(zip(roots,bits));a[d.n]=0
        if op(k,*[a[r]^p for r,p in locations])==y:good.append(bits)
    return roots,good

def reduce(n,cs,parity):
    d=DSU(n);rounds=0;merges=0
    while True:
        rounds+=1;changed=0
        for c in cs:
            roots,good=relation(d,c)
            if not good:return None,None,dict(rounds=rounds,merges=merges,contradiction=True)
            proposals=[]
            for i,r in enumerate(roots):
                s={g[i] for g in good}
                if len(s)==1:proposals.append((r,n,next(iter(s))))
            if parity and len(roots)==2:
                s={a^b for a,b in good}
                if len(s)==1:proposals.append((*roots,next(iter(s))))
            for a,b,v in proposals:
                z=d.join(a,b,v)
                if z<0:return None,None,dict(rounds=rounds,merges=merges,contradiction=True)
                changed+=z;merges+=z
        if not changed:break
    roots=sorted({d.find(v)[0] for v in range(n)}-{n})
    ids={r:i for i,r in enumerate(roots)};new=set()
    for c in cs:
        vs,good=relation(d,c)
        assert good
        if len(vs)<2:
            assert len(good)==1<<len(vs)
            continue
        a,b=map(ids.get,vs)
        for t in set(it.product((0,1),repeat=2))-set(good):
            if t==(0,0):new.add(("or",(a,b),1))
            elif t==(1,1):new.add(("and",(a,b),0))
            elif t==(1,0):new.add(("implies",(a,b),1))
            else:new.add(("implies",(b,a),1))
    return len(roots),sorted(new),dict(rounds=rounds,merges=merges,contradiction=False)

def count(n,cs,arm):
    if arm=="plain":m,rs,info=n,cs,{}
    else:m,rs,info=reduce(n,cs,arm=="full")
    if m is None:return dict(status="EXACT",count=0,peak=0,reduced_n=None,**info)
    if m==0:return dict(status="EXACT",count=1,peak=1,reduced_n=0,**info)
    r=eliminate(m,rs,"minfill")
    return dict(status=r["status"],count=r["count"],peak=r["peak"],reduced_n=m,**info)
def infer(n,cs,arm):
    start=time.perf_counter()
    a=count(n,cs,arm)
    b=count(n,cs+[("pin",(0,),1)],arm) if a["status"]=="EXACT" else None
    result=dict(base=a,pinned=b,seconds=time.perf_counter()-start)
    if b is None or b["status"]!="EXACT":return dict(status="RESOURCE_LIMIT",**result)
    total,ones=a["count"],b["count"]
    assert 0<=ones<=total
    return dict(status="UNSAT" if not total else "EXACT",count=total,ones=ones,
                forced=None if not total or 0<ones<total else int(total==ones),**result)

def independent_count(n,cs):
    # Separate branching reference: direct local allowed rows, no DSU or elimination.
    tables=[(vs,[b for b in it.product((0,1),repeat=len(vs)) if op(k,*b)==y]) for k,vs,y in cs]
    def visit(dom):
        while True:
            changed=False
            for vs,rows in tables:
                valid=[b for b in rows if all(dom[v]&(1<<x) for v,x in zip(vs,b))]
                if not valid:return 0
                for j,v in enumerate(vs):
                    mask=sum(1<<x for x in {b[j] for b in valid})
                    new=dom[v]&mask
                    if new!=dom[v]:dom[v]=new;changed=True
            if not changed:break
        if 3 not in dom:return 1
        v=dom.index(3);total=0
        for bit in (1,2):
            nxt=dom.copy();nxt[v]=bit;total+=visit(nxt)
        return total
    return visit([3]*n)

def cases():
    rng=random.Random(20261207)
    for n in (8,12,16):
        for k in ("path","ring","random"):
            for i in range(4):yield n,k,i,*world(rng,n,k,i),"brute"
    for n in (32,64,128):
        for k in ("path","ring"):
            for i in range(4):yield n,k,i,*world(rng,n,k,i),"transfer"
    for side in (4,6,8):
        for i in range(4):yield side**2,"grid",i,*world(rng,side**2,"grid",i,side),"transfer"
    for n in (8,32,128):
        cs=[("xor",(i,i+1),0) for i in range(n-1)]+[("xor",(n-1,0),1)]
        yield n,"odd_cycle",0,[[i] for i in range(n)],cs,"transfer"
    for n in (18,24):yield n,"dense",0,*world(rng,n,"dense",0),"branch"
    rng=random.Random(20261208)
    for n in (24,64,128):
        h=[rng.randrange(2) for _ in range(n)]
        cs=[("xor",(a,b),h[a]^h[b]) for a,b in it.combinations(range(n),2)]
        yield n,"dense_xor",0,None,cs,(2,1)
        yield n,"dense_xor_pin",0,None,cs+[("pin",(0,),h[0])],(1,h[0])
        yield n,"dense_xor_bad",0,None,cs+[("xor",(0,1),1^h[0]^h[1])],(0,0)
        yield n,"dense_or",0,None,[("or",(a,b),1) for a,b in it.combinations(range(n),2)],(n+1,n)
def main(out):
    stats={a:Counter() for a in ("plain","unary","full")};records=[]
    for n,k,i,rows,cs,refkind in cases():
        if refkind=="brute":ref=brute(n,cs)
        elif refkind=="transfer":ref=(transfer(rows,cs,wrap=k in ("ring","odd_cycle")),transfer(rows,cs,force=1,wrap=k in ("ring","odd_cycle")))
        elif refkind=="branch":ref=(independent_count(n,cs),independent_count(n,cs+[("pin",(0,),1)]))
        else:ref=refkind
        current={}
        for arm,s in stats.items():
            r=infer(n,cs,arm);current[arm]=r
            s["cases"]+=1;s["seconds"]+=r["seconds"]
            s["resource_limit"]+=int(r["status"]=="RESOURCE_LIMIT")
            for detail in (r["base"],r["pinned"]):
                if detail is not None:
                    assert detail["peak"]<=CAP;s["max_peak"]=max(s["max_peak"],detail["peak"])
            if r["status"]!="RESOURCE_LIMIT":
                assert (r["count"],r["ones"])==ref,(n,k,i,arm,r,ref)
                s["exact"]+=1;s["unsat"]+=int(r["status"]=="UNSAT")
            records.append(dict(n=n,kind=k,index=i,arm=arm,reference=ref,**r))
            print("REDUCE_CASE",n,k,i,arm,r["status"],"count",r.get("count"),"reduced",r["base"]["reduced_n"],"peak",r["base"]["peak"],"seconds",r["seconds"],flush=True)
        if current["plain"]["status"]!="RESOURCE_LIMIT":assert current["full"]["status"]!="RESOURCE_LIMIT"
        if k=="dense" or k.startswith("dense_xor"):assert current["full"]["status"]!="RESOURCE_LIMIT"
    result=dict(stats=stats,passed=True,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("NET_REDUCE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
