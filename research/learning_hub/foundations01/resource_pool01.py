"""RESOURCE-POOL01: resumable exact residuals with conserved visit ledger."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter,deque
from pathlib import Path
import resource_learn01 as old
import parallel01 as par
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("direct","native","equal","weighted","round_robin","sequential_pool")
CAP=8192
CPU=.8
def cohort():
    rng=random.Random(20270127)
    for n in (20,36,56,72):
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

class Worker:
    def __init__(self,n,e,mask):
        self.mask=mask
        self.stats=Counter()
        self.value=None
        self.finished=False
        self.gen=make_generator(n,e,self.stats)
        next(self.gen)
    def step(self):
        assert not self.finished
        before=self.stats["visits"]
        try:next(self.gen)
        except StopIteration as stop:
            self.finished=True;self.value=stop.value
        assert self.stats["visits"]==before+1
    def close(self):self.gen.close()
def make_generator(n,e,stats):
    adj=core.make_graph(n,e);memo={};policy=(4,8,512);transitions=[]
    def rec(mask,depth):
        yield None
        stats["visits"]+=1
        if mask in memo:
            stats["memo_hits"]+=1;return memo[mask]
        if not mask:return 1
        iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
        if iso:ans=(1<<iso.bit_count())*(yield from rec(mask^iso,depth+1))
        else:
            first=mask&-mask;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&mask&~part
                part|=z;front=z
            if part!=mask:
                stats["splits"]+=1
                ans=(yield from rec(part,depth+1))*(yield from rec(mask^part,depth+1))
            else:
                ans=None;method=None;m=mask.bit_count()
                if isinstance(policy,int) and ((policy==-1 and depth==0) or (policy>=0 and stats["visits"]>=policy)):
                    ans,method=structural(adj,mask,stats)
                    if ans is None and m>=4 and sum((adj[v]&mask).bit_count() for v in bits(mask))<=4*m:
                        ans=eliminate(adj,mask,stats)
                        if ans is not None:method="elimination"
                elif not isinstance(policy,int):
                    sm,em,delay=policy
                    if m>=min(sm,em):
                        ds=sum((adj[v]&mask).bit_count() for v in bits(mask))
                        stats["local_features"]+=1
                        if m>=sm and (ds==2*(m-1) or ds>=.7*m*(m-1)):
                            ans,method=structural(adj,mask,stats)
                        if ans is None and m>=em and stats["visits"]>=delay and ds<=4*m:
                            ans=eliminate(adj,mask,stats)
                            if ans is not None:method="elimination"
                if ans is not None:
                    stats["dispatch_"+method]+=1
                    if depth>0:transitions.append(dict(depth=depth,size=m,method=method))
                else:
                    v=max(bits(mask),key=lambda u:((adj[u]&mask).bit_count(),-u))
                    rem=mask^(1<<v)
                    ans=(yield from rec(rem,depth+1))+(yield from rec(rem&~adj[v],depth+1))
        memo[mask]=ans
        return ans

    return rec((1<<n)-1,0)
def allocations(masks,weighted,cap):
    weights=[m.bit_count()+1 if weighted else 1 for m in masks]
    total=sum(weights);shares=[cap*w//total for w in weights]
    order=sorted(range(len(masks)),key=lambda i:(-(cap*weights[i]%total),i))
    for i in order[:cap-sum(shares)]:shares[i]+=1
    assert sum(shares)==cap
    return shares
def run(n,e,arm,cap=CAP,quantum=64):
    start=time.process_time();wall=time.perf_counter();workers=[];stats=Counter();value=None
    if arm=="native":
        r=old.solve(n,e,(4,8,512),cap,CPU)
        sec=time.process_time()-start;t=time.perf_counter()-wall
        v=r["count"] if sec<=CPU else None
        return dict(count=v,cpu=sec,wall=t,reward=t+.25*sec+(v is None),stats=dict(visits=r["stats"].get("visits",0)))
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        w=Counter({(1<<n)-1:1}) if arm=="direct" else old.frontier(n,e,4)
        masks=sorted(w,key=lambda m:(-m.bit_count(),m))
        for m in masks:
            nn,ee=par.induced(n,e,m)
            workers.append(Worker(nn,ee,m))
        shares=allocations(masks,arm=="weighted",cap) if arm in ("equal","weighted") else None
        stats["tasks"]=len(workers)
        def advance(i,budget):
            x=workers[i];used=0
            if x.stats["visits"]>0:stats["resumptions"]+=1
            while not x.finished and used<budget and stats["visits"]<cap:
                x.step();used+=1;stats["visits"]+=1
            return used
        if shares is not None:
            for i,share in enumerate(shares):
                advance(i,share)
        elif arm=="round_robin":
            q=deque(range(len(workers)))
            while q and stats["visits"]<cap:
                i=q.popleft();advance(i,quantum)
                if not workers[i].finished:q.append(i)
        else:
            for i in range(len(workers)):
                advance(i,cap-stats["visits"])
                if stats["visits"]>=cap:break
        if all(x.finished for x in workers):
            value=sum(w[x.mask]*x.value for x in workers)
        if shares is not None:
            stats["unused_static_visits"]=sum(s-x.stats["visits"] for s,x in zip(shares,workers))
    except Limit:value=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    # Reconcile even if CPU timer interrupted a single generator step.
    stats["visits"]=sum(x.stats["visits"] for x in workers)
    stats["finished"]=sum(x.finished for x in workers)
    stats["unfinished"]=len(workers)-stats["finished"]
    stats["unused_global_visits"]=cap-stats["visits"]
    stats["partial_rejected"]=int(value is None and stats["finished"]>0)
    for x in workers:x.close()
    sec=time.process_time()-start;t=time.perf_counter()-wall
    if sec>CPU:value=None
    assert stats["visits"]<=cap
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
def selftests():
    base=par.selftests();checks=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for m in range(1<<len(pairs)):
            e=[p for i,p in enumerate(pairs) if m>>i&1]
            v=sum(not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
            for a in ("direct","equal","weighted","round_robin","sequential_pool"):
                assert run(n,e,a)["count"]==v
                checks+=1
    n=18;e=[(i,i+1) for i in range(n-1)]+[(0,n-1),(2,9),(5,13)]
    a=run(n,e,"round_robin",quantum=1);b=run(n,e,"round_robin",quantum=64)
    assert a["count"] is not None and a["count"]==b["count"] and a["stats"]["visits"]==b["stats"]["visits"]
    assert run(n,e,"round_robin",cap=1)["count"] is None
    return dict(frontier=base,resumable_checks=checks,suspension_invariance=True,budget_exhaustion=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    stats={a:Counter() for a in (*ARMS,"oracle")};refs=Counter();records=[];paired=Counter();recoveries=0
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=old.stronger_reference(n,f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270128+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{key:statistics.median(r[key] for r in rr) for key in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        if ref is not None and done["round_robin"] and not done["equal"] and not done["weighted"]:recoveries+=1
        choices={a:a for a in ARMS};choices["oracle"]=min(ARMS,key=lambda a:med[a]["reward"])
        for a,b in choices.items():
            s=stats[a];s["verified"]+=int(ref is not None and done[b]);s["unverified"]+=int(ref is None and done[b]);s["unresolved"]+=int(not done[b])
            for key in ("reward","cpu","wall"):s[key]+=med[b][key]
            if ref is not None:s["verified_reward"]+=med[b]["reward"]
            for key in ("visits","tasks","finished","unfinished","resumptions","unused_static_visits","unused_global_visits","partial_rejected"):s[key]+=rs[b][0]["stats"].get(key,0)
            if ref is not None and all(done.values()):
                for key in ("reward","cpu","wall"):paired[a+"_"+key]+=med[b][key]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("POOL_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6)] for a in ARMS},flush=True)
    rr=stats["round_robin"];best=min(("equal","weighted"),key=lambda a:stats[a]["verified_reward"]);b=stats[best];seq=stats["sequential_pool"]
    gain=1-rr["verified_reward"]/b["verified_reward"]
    passed=rr["verified"]>=max(stats[a]["verified"] for a in ("equal","weighted")) and recoveries>0 and gain>=.15 and rr["reward"]<=b["reward"] and (rr["unverified"]<=b["unverified"] or rr["verified"]>b["verified"])
    secondary=rr["verified"]>=seq["verified"] and rr["verified_reward"]<=.85*seq["verified_reward"]
    result=dict(stats=stats,references=refs,paired=paired,best_static=best,gain=gain,verified_recoveries=recoveries,primary_pass=passed,scheduling_pass=secondary,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("POOL_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
