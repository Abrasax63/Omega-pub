"""NET-DECOMP01: exact #2SAT fallback with components and bounded cache."""
import itertools as it
import json,random,time
from collections import Counter
from pathlib import Path
from net_reduce01 import cases, count as base_count, reduce, independent_count
from net_stress01 import op, brute, transfer
LIMIT=4096
CACHE_SLOTS=250000
class Budget(Exception):pass

def forbidden(a,b,t):
    if t==(0,0):return ("or",(a,b),1)
    if t==(1,1):return ("and",(a,b),0)
    if t==(1,0):return ("implies",(a,b),1)
    return ("implies",(b,a),1)
def clauses_from(cs):
    clauses=set()
    for k,vs,y in cs:
        for bits in it.product((0,1),repeat=len(vs)):
            if op(k,*bits)!=y:
                cl=tuple(sorted((v+1 if b==0 else -(v+1)) for v,b in zip(vs,bits)))
                assert len(set(map(abs,cl)))==len(cl)
                clauses.add(cl)
    return tuple(sorted(clauses))

def branch_count(n,cs,clique):
    memo={};slots=0;stats=Counter()
    def restrict(cl,l):
        return tuple(tuple(x for x in c if x!=-l) for c in cl if l not in c)
    def rec(active,cl):
        nonlocal slots
        stats["visits"]+=1
        if stats["visits"]>LIMIT:raise Budget()
        while True:
            if any(not c for c in cl):return 0
            unit=next((c[0] for c in cl if len(c)==1),None)
            if unit is None:break
            active=active-{abs(unit)};cl=restrict(cl,unit)
            stats["units"]+=1
        cl=tuple(sorted(set(cl)))
        used={abs(x) for c in cl for x in c}
        assert used<=active
        multiplier=1<<(len(active)-len(used))
        if not cl:return multiplier
        if cl in memo:
            stats["hits"]+=1
            return multiplier*memo[cl]
        adj={v:set() for v in used}
        signs={v:set() for v in used}
        for a,b in cl:
            adj[abs(a)].add(abs(b));adj[abs(b)].add(abs(a))
            signs[abs(a)].add(a>0);signs[abs(b)].add(b>0)
        left=set(used);components=[]
        while left:
            stack=[min(left)];part=set(stack);left-=part
            while stack:
                v=stack.pop();new=adj[v]&left
                part|=new;left-=new;stack.extend(new)
            components.append(part)
        if len(components)>1:
            stats["splits"]+=1
            value=1
            for part in components:
                value*=rec(part,tuple(c for c in cl if abs(c[0]) in part))
                if not value:break
        elif clique and len(cl)==len(used)*(len(used)-1)//2 and all(len(s)==1 for s in signs.values()) and all(len(a)==len(used)-1 for a in adj.values()):
            stats["cliques"]+=1
            value=len(used)+1
        else:
            v=min(used,key=lambda x:(-len(adj[x]),x))
            value=rec(used-{v},restrict(cl,v))+rec(used-{v},restrict(cl,-v))
        if len(memo)<LIMIT and slots+len(cl)<=CACHE_SLOTS:
            memo[cl]=value;slots+=len(cl)
        return multiplier*value
    try:
        v=rec(set(range(1,n+1)),clauses_from(cs))
        return dict(status="EXACT",count=v,stats=dict(stats),cache_slots=slots,cache_entries=len(memo))
    except Budget:
        return dict(status="RESOURCE_LIMIT",count=None,stats=dict(stats),cache_slots=slots,cache_entries=len(memo))

def count(n,cs,arm):
    r=base_count(n,cs,"full")
    if r["status"]=="EXACT" or arm=="base":return dict(**r,fallback=False)
    m,rs,info=reduce(n,cs,True)
    assert m is not None and m>0
    f=branch_count(m,rs,arm=="clique")
    return dict(**f,reduced_n=m,fallback=True,base=r)
def infer(n,cs,arm):
    start=time.perf_counter()
    a=count(n,cs,arm)
    b=count(n,cs+[("pin",(0,),1)],arm) if a["status"]=="EXACT" else None
    r=dict(base=a,pinned=b,seconds=time.perf_counter()-start)
    if b is None or b["status"]!="EXACT":return dict(status="RESOURCE_LIMIT",**r)
    v,w=a["count"],b["count"]
    assert 0<=w<=v
    return dict(status="EXACT" if v else "UNSAT",count=v,ones=w,forced=None if not v or 0<w<v else int(w==v),**r)

def fresh():
    rng=random.Random(20261209)
    for n in (10,12,16):
        for i in range(4):
            h=[rng.randrange(2) for _ in range(n)]
            cs=[]
            for a,b in rng.sample(list(it.combinations(range(n),2)),2*n):
                k=rng.choice(("xor","and","or","implies"))
                cs.append((k,(a,b),op(k,h[a],h[b])))
            if i%2:cs.extend([("pin",(0,),0),("pin",(0,),1)])
            yield n,"fresh_mixed",i,None,cs,"brute"
    for n in (24,64,128):
        a=n//2;b=n-a
        for kind in ("disjoint","overlap","bipartite"):
            if kind=="disjoint":
                edges=list(it.combinations(range(a),2))+list(it.combinations(range(a,n),2))
                total=(a+1)*(b+1);normone=a*(b+1)
            elif kind=="overlap":
                edges=list(it.combinations(range(a),2))+list(it.combinations([0]+list(range(a,n)),2))
                total=a*(b+1)+1;normone=total-1
            else:
                edges=list(it.product(range(a),range(a,n)))
                total=(1<<a)+(1<<b)-1;normone=(1<<(a-1))+(1<<b)-1
            flips=[rng.randrange(2) for _ in range(n)]
            cs=[forbidden(u,v,(flips[u],flips[v])) for u,v in edges]
            ones=normone if not flips[0] else total-normone
            yield n,kind,0,None,cs,(total,ones)

def main(out):
    records=[];stats={a:Counter() for a in ("base","dpll","clique")};clique_visits={a:0 for a in ("dpll","clique")}
    for n,k,i,rows,cs,refkind in it.chain(cases(),fresh()):
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
                if detail and detail["fallback"]:
                    s["fallbacks"]+=1
                    assert detail["cache_slots"]<=CACHE_SLOTS and detail["cache_entries"]<=LIMIT
                    assert detail["stats"].get("visits",0)<=LIMIT+1
                    s.update(detail["stats"])
                    if k=="dense_or":clique_visits[arm]+=detail["stats"].get("visits",0)
            if r["status"]!="RESOURCE_LIMIT":
                assert (r["count"],r["ones"])==ref,(n,k,i,arm,r,ref)
                s["exact"]+=1;s["unsat"]+=int(r["status"]=="UNSAT")
            records.append(dict(n=n,kind=k,index=i,arm=arm,reference=ref,**r))
            print("DECOMP_CASE",n,k,i,arm,r["status"],"count",r.get("count"),"visits",sum(d.get("stats",{}).get("visits",0) for d in (r["base"],r["pinned"]) if d),"seconds",r["seconds"],flush=True)
        if current["base"]["status"]!="RESOURCE_LIMIT":assert current["clique"]["status"]!="RESOURCE_LIMIT"
        if k in ("dense_or","disjoint","overlap","bipartite"):assert current["clique"]["status"]!="RESOURCE_LIMIT"
    assert stats["clique"]["cases"]==110
    result=dict(stats=stats,clique_visits=clique_visits,passed=True,clique_gain=clique_visits["clique"]<clique_visits["dpll"],records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("NET_DECOMP_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
