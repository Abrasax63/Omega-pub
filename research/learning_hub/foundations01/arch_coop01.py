"""ARCH-COOP01: cooperative resumable exact workers with optional shared memo."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm,CPU,reference
ARMS=("A_only","B_only","isolated","shared","delay")
def cohort():
    rng=random.Random(20270115)
    for n in (18,32,48,72):
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

def cooperative(n,e,arm):
    adj=core.make_graph(n,e);stats=Counter();local={w:Counter() for w in ("A","B")}
    common={0:(1,"seed")};memos={"A":common,"B":common} if arm=="shared" else {"A":{0:(1,"seed")},"B":{0:(1,"seed")}}
    # All stored values are completed exact counts, never tentative work.
    def rec(mask,w,depth):
        if stats["visits"]>=4096:raise Limit
        stats["visits"]+=1;local[w]["visits"]+=1
        yield None
        memo=memos[w]
        if mask in memo:
            val,producer=memo[mask]
            stats["hits"]+=1
            if producer not in (w,"seed"):stats["cross_hits"]+=1
            return val
        iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
        if iso:
            val=(1<<iso.bit_count())*(yield from rec(mask^iso,w,depth+1))
        else:
            first=mask&-mask;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&mask&~part
                part|=z;front=z
            if part!=mask:
                a=yield from rec(part,w,depth+1)
                b=yield from rec(mask^part,w,depth+1)
                val=a*b
            else:
                val=None;m=mask.bit_count()
                if w=="B" and m>=4:
                    ds=sum((adj[v]&mask).bit_count() for v in bits(mask))
                    stats["features"]+=1
                    if ds==2*(m-1) or ds>=.7*m*(m-1):
                        val,method=structural(adj,mask,stats)
                    if val is None and m>=8 and local[w]["visits"]>=512 and ds<=4*m:
                        val=eliminate(adj,mask,stats)
                    if val is not None:stats["dispatch"]+=1
                if val is None:
                    v=max(bits(mask),key=lambda u:((adj[u]&mask).bit_count(),-u))
                    rem=mask^(1<<v)
                    a=yield from rec(rem,w,depth+1)
                    b=yield from rec(rem&~adj[v],w,depth+1)
                    val=a+b
        if mask in memo:
            assert memo[mask][0]==val
            stats["duplicate_completed"]+=1
        elif sum(len(d) for d in {id(x):x for x in memos.values()}.values())<4096:
            memo[mask]=(val,w)
        return val
    workers=["A"] if arm=="A_only" else ["B"] if arm=="B_only" else ["A","B"]
    root=(1<<n)-1;gens={w:rec(root,w,0) for w in workers}
    start=time.process_time();wall=time.perf_counter();val=None;winner=None
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        while winner is None:
            for w in workers:
                stats["turns"]+=1
                for _ in range(32):
                    try:next(gens[w])
                    except StopIteration as stop:
                        val=stop.value;winner=w;break
                if winner is not None:break
    except Limit:val=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    for g in gens.values():g.close()
    if sec>CPU:val=None;winner=None
    stats["memo_entries"]=sum(len(d) for d in {id(x):x for x in memos.values()}.values())
    stats["cancelled"]=len(workers)-1 if winner else len(workers)
    stats["A_visits"]=local["A"]["visits"];stats["B_visits"]=local["B"]["visits"]
    assert stats["visits"]<=4096 and stats["memo_entries"]<=4096
    return dict(count=val,winner=winner,seconds=sec,wall=time.perf_counter()-wall,cost=sec if val is not None else CPU,stats=dict(stats))
def solve(n,e,a):
    if a=="delay":
        r=gate.solve(n,e,512);return dict(r,winner="delay" if r["count"] is not None else None)
    return cooperative(n,e,a)
def main(out):
    signal.signal(signal.SIGPROF,alarm)
    data=list(cohort());assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];paired=Counter();cross_cases=0
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=reference(n,f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270116+3*j+k).shuffle(order)
            for a in order:rs[a].append(solve(n,e,a))
        gate.audit(rs,ref)
        med={a:statistics.median(r["cost"] for r in rows) for a,rows in rs.items()}
        done={a:sum(r["count"] is not None for r in rows)>=2 for a,rows in rs.items()}
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a]);s["all_cost"]+=med[a]
            r=rs[a][0]
            for name in ("visits","cross_hits","hits","duplicate_completed","cancelled","turns","factor_lookups","structural_probes","elimination_probes"):s[name]+=r["stats"].get(name,0)
            s["peak_memo_entries"]=max(s["peak_memo_entries"],r["stats"].get("memo_entries",0))
            if r["winner"]:s["wins_"+r["winner"]]+=1
            if ref is not None:
                s["verified_cost"]+=med[a]
                if done[a]:s["verified_cross_hits"]+=r["stats"].get("cross_hits",0)
            if not done[a]:s["unresolved_cross_hits"]+=r["stats"].get("cross_hits",0)
        if ref is not None:
            if done["shared"] and any(r["count"] is not None and r["stats"].get("cross_hits",0)>0 for r in rs["shared"]):cross_cases+=1
            if all(done[a] for a in ARMS):
                paired["cases"]+=1
                for a in ARMS:paired[a]+=med[a]
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,median_cost=med,completed=done))
        print("COOP_CASE",n,f,kind,{a:[done[a],round(med[a],6),rs[a][0]["stats"].get("cross_hits",0)] for a in ARMS},flush=True)
    s=stats["shared"];i=stats["isolated"];best=min(("A_only","B_only","delay"),key=lambda a:stats[a]["verified_cost"])
    gains={a:1-s["verified_cost"]/stats[a]["verified_cost"] for a in ("isolated",best)}
    passed=s["verified"]>=max(i["verified"],stats["B_only"]["verified"]) and s["unverified"]<=i["unverified"] and all(v>=.15 for v in gains.values()) and cross_cases>0
    result=dict(stats=stats,references=refs,paired=paired,best_single=best,gains=gains,cross_verified_cases=cross_cases,primary_pass=passed,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("COOP_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
