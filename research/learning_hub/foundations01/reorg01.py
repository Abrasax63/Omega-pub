"""REORG01: reversible shared-state switch, exact completed memo only."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter,deque
from pathlib import Path
import resource_learn01 as old
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("direct","native","partition","fixed_shared","fixed_private","adaptive")
CAP=8192
CPU=.8
def cohort():
    rng=random.Random(20270129)
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


def generator(adj,root,stats,memo,name):
    policy=(4,8,512);transitions=[]
    def rec(mask,depth):
        stats['current_size']=mask.bit_count()
        yield None
        stats["visits"]+=1
        if mask in memo:
            stats["memo_hits"]+=1
            value,owner=memo[mask]
            if owner!=name:stats["cross_hits"]+=1
            return value
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
        if mask in memo:
            assert memo[mask][0]==ans
            stats['duplicate_completed']+=1
        else:memo[mask]=(ans,name)
        return ans

    return rec(root,0)

class Worker:
    def __init__(self,adj,root,memo,name):
        self.root=root;self.stats=Counter();self.finished=False;self.value=None
        self.gen=generator(adj,root,self.stats,memo,name);next(self.gen)
    def step(self):
        try:next(self.gen)
        except StopIteration as stop:self.finished=True;self.value=stop.value
def run(n,e,arm,cap=CAP,probe=256,trial=1024):
    start=time.process_time();wall=time.perf_counter();stats=Counter();workers=[];value=None
    if arm=="native":
        r=old.solve(n,e,(4,8,512),cap,CPU);sec=time.process_time()-start;t=time.perf_counter()-wall
        val=r["count"] if sec<=CPU else None
        return dict(count=val,cpu=sec,wall=t,reward=t+.25*sec+(val is None),stats=dict(visits=r["stats"].get("visits",0)))
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        adj=core.make_graph(n,e);root=(1<<n)-1;memo={}
        def create(mask,cache,name):
            w=Worker(adj,mask,cache,name);workers.append(w);return w
        def advance(w,allow):
            used=0
            while not w.finished and used<allow and stats["visits"]<cap:
                w.step();used+=1;stats["visits"]+=1
        def partition(allow,cache):
            weights=old.frontier(n,e,4)
            leaves=[create(m,cache if cache is not None else {},f"leaf{m}") for m in sorted(weights,key=lambda m:(-m.bit_count(),m))]
            stop=min(cap,stats["visits"]+allow);q=deque(leaves)
            while q and stats["visits"]<stop:
                w=q.popleft();advance(w,min(64,stop-stats["visits"]))
                if not w.finished:q.append(w)
            if not q:
                stats["partition_success"]+=1
                return sum(weights[w.root]*w.value for w in leaves)
            stats["abandoned_leaf_visits"]+=sum(w.stats["visits"] for w in leaves if not w.finished)
            for w in leaves:w.gen.close()
            return None
        if arm=="partition":value=partition(cap,memo)
        else:
            direct=create(root,memo,"direct")
            advance(direct,cap if arm=="direct" else probe)
            if not direct.finished and arm!="direct":
                switch=arm!="adaptive" or (direct.stats["memo_hits"]/max(1,direct.stats["visits"])<.25 and direct.stats["current_size"]>=8)
                if switch and stats["visits"]<cap:
                    stats["switch"]+=1;stats["probe_entries"]+=len(memo)
                    value=partition(trial,None if arm=="fixed_private" else memo)
                    if value is None:
                        stats["fallback"]+=1
                        advance(direct,cap-stats["visits"])
                else:advance(direct,cap-stats["visits"])
            if direct.finished:value=direct.value
    except Limit:value=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    stats["visits"]=sum(w.stats["visits"] for w in workers)
    for w in workers:
        for k in ("cross_hits","duplicate_completed","memo_hits"):stats[k]+=w.stats[k]
        w.gen.close()
    sec=time.process_time()-start;t=time.perf_counter()-wall
    if sec>CPU:value=None
    assert stats["visits"]<=cap
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
def selftests():
    checks=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for m in range(1<<len(pairs)):
            e=[p for i,p in enumerate(pairs) if m>>i&1]
            v=sum(not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
            for a in ARMS:
                if a=="native":continue
                assert run(n,e,a)["count"]==v
                checks+=1
    n=12;e=[(i,i+1) for i in range(n-1)]+[(0,n-1),(2,9)]
    ref=core.reference(n,e)[0]
    for a in ("fixed_shared","fixed_private"):
        r=run(n,e,a,probe=1,trial=1)
        assert r["count"]==ref and r["stats"]["switch"]==1 and r["stats"]["fallback"]==1
        assert run(n,e,a,cap=2,probe=1,trial=1)["count"] is None
    return dict(exhaustive_checks=checks,forced_fallback=2,fail_closed=2)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    stats={a:Counter() for a in (*ARMS,"oracle")};refs=Counter();records=[];paired=Counter();switch_verified=0;cross_verified=0
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=old.stronger_reference(n,f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270130+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        if ref is not None and done["adaptive"]:switch_verified+=int(any(r["stats"].get("switch") for r in rs["adaptive"] if r["count"] is not None))
        if ref is not None and done["fixed_shared"]:cross_verified+=int(any(r["stats"].get("cross_hits") for r in rs["fixed_shared"] if r["count"] is not None))
        choices={a:a for a in ARMS};choices["oracle"]=min(ARMS,key=lambda a:med[a]["reward"])
        for a,b in choices.items():
            s=stats[a];s["verified"]+=int(ref is not None and done[b]);s["unverified"]+=int(ref is None and done[b]);s["unresolved"]+=int(not done[b])
            for key in ("reward","cpu","wall"):s[key]+=med[b][key]
            if ref is not None:s["verified_reward"]+=med[b]["reward"]
            for key in ("visits","switch","fallback","partition_success","probe_entries","cross_hits","duplicate_completed","abandoned_leaf_visits"):s[key]+=rs[b][0]["stats"].get(key,0)
            if ref is not None and all(done.values()):
                for key in ("reward","cpu","wall"):paired[a+"_"+key]+=med[b][key]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("REORG_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6)] for a in ARMS},flush=True)
    s=stats["adaptive"];controls=("direct","partition")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    passed=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls) and switch_verified>0
    sh=stats["fixed_shared"];pr=stats["fixed_private"]
    secondary=sh["verified"]>=pr["verified"] and sh["verified_reward"]<=.85*pr["verified_reward"] and cross_verified>0
    result=dict(stats=stats,references=refs,paired=paired,gains=gains,switch_verified=switch_verified,cross_verified=cross_verified,primary_pass=passed,sharing_pass=secondary,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("REORG_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
