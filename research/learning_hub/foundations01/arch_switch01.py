"""ARCH-SWITCH01: exact residual-state switching between counting engines."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import learn_policy01 as core
ARMS=("branch","elimination","root","dynamic")
CPU=.5
class Limit(Exception):pass
def alarm(*_):raise Limit
def bits(mask):return core.bits(mask)
def cohort():
    rng=random.Random(20270105)
    for n in (12,18,24,40,64):
        for f in range(8):
            pairs=list(it.combinations(range(n),2));hubs=[];parts=None
            if f==0:e=[(rng.randrange(v),v) for v in range(1,n)]
            elif f==1:
                e=[(v,v+1) for v in range(n-1)]+[(0,n-1)]
                e+=rng.sample([p for p in pairs if p not in e],n//5)
            elif f in (2,3,7):
                def prob(a,b):
                    return .12 if f==2 else .42 if f==3 else (.4 if (a<n//2)==(b<n//2) else .035)
                e=[(a,b) for a,b in pairs if rng.random()<prob(a,b)]
            elif f==4:
                parts=[len(range(i,n,3)) for i in range(3)]
                e=[(a,b) for a,b in pairs if a%3!=b%3]
            else:
                h=1 if f==5 else 2;hubs=list(range(h))
                e=[(rng.randrange(h,v),v) for v in range(h+1,n) if rng.random()<.82]
                e += [(a,b) for a,b in pairs if a<h and (f==5 or rng.random()<.84)]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[labels[v] for v in hubs],parts
def structural(adj,mask,stats):
    stats["structural_probes"]+=1
    vs=list(bits(mask));m=len(vs)
    degrees=[(adj[v]&mask).bit_count() for v in vs]
    if sum(degrees)==2*(m-1):
        def dp(v,parent):
            a=b=1
            for u in bits(adj[v]&mask):
                if u!=parent:
                    x,y=dp(u,v);a*=x+y;b*=x
            return a,b
        stats["tree_vertices"]+=m
        return sum(dp(vs[0],-1)),"tree"
    if sum(degrees)<m*(m-1)*.7:return None,None
    rest=mask;sizes=[]
    while rest:
        v=(rest&-rest).bit_length()-1
        part=mask&~adj[v]
        if part&~rest or any((mask&~adj[u])!=part for u in bits(part)):return None,None
        sizes.append(part.bit_count());rest^=part
    stats["multipartite_vertices"]+=m
    return 1+sum((1<<s)-1 for s in sizes),"multipartite"
def eliminate(adj,mask,stats):
    stats["elimination_probes"]+=1
    vs=list(bits(mask));work={v:adj[v]&mask for v in vs};order=[]
    remaining=mask
    while remaining:
        v=min(bits(remaining),key=lambda u:((work[u]&remaining).bit_count(),u))
        ns=work[v]&remaining
        if ns.bit_count()>3:return None
        order.append(v);remaining^=1<<v
        for u in bits(ns):work[u]=(work[u]|(ns&~(1<<u)))&~(1<<v)
    # Factors encode independent-set membership bits (1 means selected).
    factors=[((v,),(1,1)) for v in vs]
    for a in vs:
        for b in bits(adj[a]&mask):
            if a<b:factors.append(((a,b),(1,1,1,0)))
    scalar=1
    for v in order:
        bucket=[f for f in factors if v in f[0]]
        factors=[f for f in factors if v not in f[0]]
        scope=tuple(sorted({u for s,t in bucket for u in s if u!=v}))
        assert len(scope)<=3
        table=[]
        for k in range(1<<len(scope)):
            assignment={u:(k>>i)&1 for i,u in enumerate(scope)}
            val=0
            for bit in (0,1):
                assignment[v]=bit;prod=1
                for s,t in bucket:
                    idx=sum(assignment[u]<<i for i,u in enumerate(s))
                    prod*=t[idx]
                    stats["factor_lookups"]+=1
                val+=prod
            table.append(val)
        if scope:factors.append((scope,tuple(table)))
        else:scalar*=table[0]
    assert not factors
    return scalar
def solve(n,e,arm):
    adj=core.make_graph(n,e);memo={};stats=Counter();transitions=[]
    def rec(mask,depth):
        if stats["visits"]>=4096:raise Limit
        stats["visits"]+=1
        if mask in memo:
            stats["memo_hits"]+=1;return memo[mask]
        if not mask:return 1
        iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
        if iso:ans=(1<<iso.bit_count())*rec(mask^iso,depth+1)
        else:
            first=mask&-mask;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&mask&~part
                part|=z;front=z
            if part!=mask:
                stats["splits"]+=1
                ans=rec(part,depth+1)*rec(mask^part,depth+1)
            else:
                ans=None;method=None;m=mask.bit_count()
                if arm=="dynamic" or (arm=="root" and depth==0):
                    ans,method=structural(adj,mask,stats)
                    if ans is None and m>=4 and sum((adj[v]&mask).bit_count() for v in bits(mask))<=4*m:
                        ans=eliminate(adj,mask,stats)
                        if ans is not None:method="elimination"
                if ans is not None:
                    stats["dispatch_"+method]+=1
                    if depth>0:transitions.append(dict(depth=depth,size=m,method=method))
                else:
                    v=max(bits(mask),key=lambda u:((adj[u]&mask).bit_count(),-u))
                    rem=mask^(1<<v)
                    ans=rec(rem,depth+1)+rec(rem&~adj[v],depth+1)
        memo[mask]=ans
        return ans
    start=time.process_time();wall=time.perf_counter()
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        val=eliminate(adj,(1<<n)-1,stats) if arm=="elimination" else rec((1<<n)-1,0)
        status="EXACT" if val is not None else "WIDTH_LIMIT"
    except Limit:
        val=None;status="RESOURCE_LIMIT"
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    if sec>CPU:val=None;status="CPU_LIMIT"
    return dict(count=val,status=status,seconds=sec,wall=time.perf_counter()-wall,
                cost=min(sec,CPU) if val is not None else CPU,stats=dict(stats),transitions=transitions)
def leaf_dp(adj,remaining):
    # Independent leaf removal with multiplicative unary weights.
    active=set(remaining);neighbors={v:set(bits(adj[v]))&active for v in active}
    z={v:1 for v in active};o=z.copy();total=1
    while active:
        v=min(v for v in active if len(neighbors[v])<=1)
        if neighbors[v]:
            u=next(iter(neighbors[v]));z[u]*=z[v]+o[v];o[u]*=z[v];neighbors[u].remove(v)
        else:total*=z[v]+o[v]
        active.remove(v)
    return total
def reference(n,f,e,hubs,parts):
    if n<=18:return core.reference(n,e)
    if f==4:return 1+sum((1<<s)-1 for s in parts),"MULTIPARTITE_FORMULA"
    if f in (0,5,6):
        adj=core.make_graph(n,e);total=0
        for b in it.product((0,1),repeat=len(hubs)):
            selected=[v for v,x in zip(hubs,b) if x]
            if any(adj[u]>>v&1 for u,v in it.combinations(selected,2)):continue
            remaining=set(range(n))-set(hubs)
            for v in selected:remaining-=set(bits(adj[v]))
            total+=leaf_dp(adj,remaining)
        return total,"CONDITIONED_LEAF_DP"
    return core.reference(n,e)
def main(out):
    signal.signal(signal.SIGPROF,alarm)
    data=list(cohort());assert len(data)==40 and len({(n,e) for n,f,e,h,p in data})==40
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];rep={a:[0.]*3 for a in ARMS}
    matched=Counter();oracle=Counter();switch_cases=0;family_stats={}
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=reference(n,f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270106+3*j+k).shuffle(order)
            for a in order:rs[a].append(solve(n,e,a))
        vals={r["count"] for rows in rs.values() for r in rows if r["count"] is not None}
        assert len(vals)<=1,(n,f,vals)
        if ref is not None:assert not vals or vals=={ref},(n,f,ref,vals)
        med={a:statistics.median(r["cost"] for r in rows) for a,rows in rs.items()}
        done={a:sum(r["count"] is not None for r in rows)>=2 for a,rows in rs.items()}
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a]);s["all_cost"]+=med[a]
            for name in ("visits","factor_lookups","structural_probes","elimination_probes"):
                s[name]+=rs[a][0]["stats"].get(name,0)
            s["switches"]+=len(rs[a][0]["transitions"])
            if ref is not None:
                s["verified_cost"]+=med[a]
                if f not in (5,6):s["nonhub_verified_cost"]+=med[a]
                for k,r in enumerate(rs[a]):rep[a][k]+=r["cost"]
                fs=family_stats.setdefault(str(f),Counter());fs[a]+=med[a]
        if ref is not None:
            best=min(("branch","root","elimination"),key=lambda a:med[a])
            oracle["cost"]+=med[best];oracle["verified"]+=int(done[best])
            if done["dynamic"] and any(r["count"] is not None and r["transitions"] for r in rs["dynamic"]):switch_cases+=1
            if done["dynamic"] and done["root"] and done["branch"]:
                matched["cases"]+=1
                for a in ("dynamic","root","branch"):matched[a]+=med[a]
        records.append(dict(n=n,family=f,edges=e,hubs=h,reference=ref,reference_kind=kind,results=rs,median_cost=med,completed=done))
        print("SWITCH_CASE",n,f,kind,{a:[done[a],round(med[a],6),len(rs[a][0]["transitions"])] for a in ARMS},flush=True)
    best=min(("branch","root"),key=lambda a:stats[a]["verified_cost"])
    d=stats["dynamic"];gain=1-d["verified_cost"]/stats[best]["verified_cost"]
    gate=gain>=.15 and d["verified"]>=max(stats[a]["verified"] for a in ("branch","root")) and d["unverified"]<=stats["root"]["unverified"] and switch_cases>0
    result=dict(stats=stats,reference_kinds=refs,matched=matched,static_oracle=oracle,best_static=best,gain=gain,
                switch_verified_cases=switch_cases,rep_cost=rep,family_stats=family_stats,primary_pass=gate,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("SWITCH_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
