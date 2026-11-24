"""MORPH-LOCAL01: local candidate expansion with exact cache-aware scoring."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import resource_learn01 as old
import reorg01 as reorg
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("binary","multi","structural","cache","direct","partition")
CAP=8192
CPU=.8
def cohort():
    rng=random.Random(20270133)
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
            elif f==5:
                hubs=[0];e=[(rng.randrange(1,v),v) for v in range(2,n) if rng.random()<.82]
                e += [(0,b) for b in range(1,n)]
            else:
                width=int(n**.5)
                e=[(a,b) for a,b in pairs if b==a+width or (b==a+1 and a//width==b//width)]
                e+=rng.sample([p for p in pairs if p not in e],n//5)
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[labels[v] for v in hubs],parts

class Registry:
    def __init__(self,stats,cap):
        self.jobs={};self.plans={};self.stats=stats;self.cap=cap
    def request(self,m):
        if self.stats["requests"]>=self.cap:raise Limit
        self.stats["requests"]+=1
        if m in self.jobs:self.stats["reused_requests"]+=1
        else:self.jobs[m]=None
    def plan(self,m,kind,children):
        assert self.jobs[m] is None and m not in self.plans
        assert kind in ("sum","product","scale")
        assert children and all(c>=0 and c&m==c and c.bit_count()<m.bit_count() and w>=1 for c,w in children)
        assert kind!="product" or len(children)==2 and all(w==1 for c,w in children)
        assert kind!="scale" or len(children)==1
        assert len({c for c,w in children})==len(children)
        # Atomic reservation avoids a half-published plan on request exhaustion.
        if self.stats["requests"]+len(children)>self.cap:raise Limit
        for c,w in children:self.request(c)
        self.plans[m]=(kind,tuple(children))
    def done(self,m,v):
        assert self.jobs[m] is None,"duplicate completion"
        assert isinstance(v,int) and 1<=v<=1<<m.bit_count()
        self.jobs[m]=v;self.stats["completed"]+=1
    def finish(self,m):
        kind,ch=self.plans[m]
        assert all(self.jobs[c] is not None for c,w in ch)
        vals=[self.jobs[c]*w for c,w in ch]
        self.done(m,vals[0]*vals[1] if kind=="product" else sum(vals))
    def audit(self,root):
        seen=set();todo=[root]
        while todo:
            m=todo.pop()
            if m in seen:continue
            seen.add(m)
            if m in self.plans:todo.extend(c for c,w in self.plans[m][1])
        assert seen==set(self.jobs)
        if self.jobs[root] is not None:assert all(v is not None for v in self.jobs.values())
        return len(seen)
def condition(adj,mask,vs):
    fixed=sum(1<<v for v in vs);out=Counter()
    for b in range(1<<len(vs)):
        chosen=[v for i,v in enumerate(vs) if b>>i&1]
        if any(adj[u]>>v&1 for u,v in it.combinations(chosen,2)):continue
        child=mask&~fixed
        for v in chosen:child&=~adj[v]
        out[child]+=1
    return list(out.items())
def fast_pair(adj,m,v,u):
    rem=m&~((1<<v)|(1<<u));out=Counter((rem,rem&~adj[v],rem&~adj[u]))
    if not (adj[v]>>u)&1:out[rem&~(adj[v]|adj[u])]+=1
    return list(out.items())
def binary_children(adj,m,v):
    rem=m^(1<<v)
    return [(rem,1),(rem&~adj[v],1)]
def select(candidates,jobs,use_cache):
    def rank(i):
        ch=candidates[i][1]
        cost=sum(1 if use_cache and jobs.get(c) is not None else 1+(1<<((c.bit_count()+3)//4)) for c,w in ch)
        return cost,len(ch),i
    return candidates[min(range(len(candidates)),key=rank)]
def run(n,e,arm,cap=CAP,lo=256,hi=1024,min_size=12):
    if arm in ("direct","partition"):return reorg.run(n,e,arm,cap=cap)
    start=time.process_time();wall=time.perf_counter();stats=Counter()
    reg=Registry(stats,cap);root=(1<<n)-1;value=None;expanded=set()
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        adj=core.make_graph(n,e);reg.request(root);stack=[root]
        while stack:
            m=stack[-1]
            if reg.jobs[m] is not None:stack.pop();continue
            if m in reg.plans:
                todo=next((c for c,w in reg.plans[m][1] if reg.jobs[c] is None),None)
                if todo is None:reg.finish(m);stack.pop()
                else:assert todo not in stack;stack.append(todo)
                continue
            assert m not in expanded;expanded.add(m);stats["expansions"]+=1
            if not m:reg.done(m,1);continue
            iso=sum(1<<v for v in bits(m) if not adj[v]&m)
            if iso:reg.plan(m,"scale",[(m^iso,1<<iso.bit_count())]);continue
            first=m&-m;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&m&~part
                part|=z;front=z
            if part!=m:reg.plan(m,"product",[(part,1),(m^part,1)]);continue
            size=m.bit_count();ans=None
            ds={v:(adj[v]&m).bit_count() for v in bits(m)}
            degree_sum=sum(ds.values())
            if size>=4 and (degree_sum==2*(size-1) or degree_sum>=.7*size*(size-1)):
                ans,method=structural(adj,m,stats)
            if ans is None and size>=8 and stats["requests"]>=512 and degree_sum<=4*size:
                ans=eliminate(adj,m,stats)
            if ans is not None:reg.done(m,ans);stats["specialist"]+=1;continue
            ordered=sorted(ds,key=lambda v:(-ds[v],v))
            eligible=size>=min_size and ds[ordered[0]]>=3
            if arm in ("structural","cache") and eligible:
                vs=ordered[:3]
                candidates=[("binary",binary_children(adj,m,v)) for v in vs]
                candidates += [("multi",fast_pair(adj,m,vs[0],u)) for u in vs[1:]]
                stats["candidate_probes"]+=len(candidates)
                kind,ch=select(candidates,reg.jobs,arm=="cache")
                stats["selected_cached_children"]+=sum(reg.jobs.get(c) is not None for c,w in ch)
            elif arm=="multi" and eligible:
                kind,ch="multi",condition(adj,m,ordered[:2])
            else:
                kind,ch="binary",binary_children(adj,m,ordered[0])
            reg.plan(m,"sum",ch)
            stats[kind]+=1
            stats["aggregated_children"]+=sum(w for c,w in ch)-len(ch)
        value=reg.jobs[root]
    except Limit:value=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    # A timeout can interrupt plan registration mid-instruction; report
    # unresolved without claiming an atomic in-memory rollback.
    if value is not None:
        stats["reachable"]=reg.audit(root)
    else:
        stats["reachable_audit_skipped"]=1
    stats["nodes"]=len(reg.jobs);stats["unfinished"]=sum(v is None for v in reg.jobs.values())
    assert stats["requests"]<=cap and len(expanded)<=len(reg.jobs)
    sec=time.process_time()-start;t=time.perf_counter()-wall
    if sec>CPU:value=None
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
def selftests():
    checks=0;identities=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for m in range(1<<len(pairs)):
            e=[p for i,p in enumerate(pairs) if m>>i&1]
            v=sum(not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
            for a in ARMS[:4]:
                assert run(n,e,a,min_size=4)["count"]==v;checks+=1
            adj=core.make_graph(n,e);root=(1<<n)-1
            for x,y in pairs:
                ch=fast_pair(adj,root,x,y)
                assert dict(ch)==dict(condition(adj,root,[x,y]))
                total=0
                for c,w in ch:
                    total+=w*sum(b&~c==0 and not any(b>>a&1 and b>>d&1 for a,d in e) for b in range(1<<n))
                assert total==v;identities+=1
    n=12;e=[(i,(i+1)%n) for i in range(n)]+[(0,6),(2,8),(4,10)]
    ref=core.reference(n,e)[0]
    for a in ("structural","cache"):
        r=run(n,e,a);assert r["count"]==ref and r["stats"]["candidate_probes"]>0
        assert run(n,e,a,cap=1)["count"] is None
    c=[("binary",[(7,1),(1,1)]),("multi",[(255,1),(3,1)])]
    assert select(c,{},False)==c[0] and select(c,{255:1,3:1},True)==c[1]
    return dict(exhaustive=checks,condition_identities=identities,eligible=True,cache_fixture=True,fail_closed=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    fixed=("binary","multi","direct","partition")
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];paired=Counter();cached=0;recoveries=0;oracle=Counter()
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=old.stronger_reference(n,7 if f==6 else f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270134+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        if ref is not None:
            cached+=int(done["cache"] and any(r["count"] is not None and r["stats"].get("selected_cached_children",0)>0 for r in rs["cache"]))
            recoveries+=int(done["cache"] and not any(done[a] for a in fixed))
        for key,arms in (("fixed",fixed),("all",ARMS)):
            b=min(arms,key=lambda a:med[a]["reward"]);oracle[key+"_all_reward"]+=med[b]["reward"]
            if ref is not None:oracle[key+"_verified_reward"]+=med[b]["reward"];oracle[key+"_verified"]+=int(done[b])
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
            for k in ("reward","cpu","wall"):s[k]+=med[a][k]
            if ref is not None:s["verified_reward"]+=med[a]["reward"]
            for k in ("requests","reused_requests","expansions","completed","binary","multi","aggregated_children","specialist","nodes","unfinished","reachable_audit_skipped","visits","candidate_probes","selected_cached_children"):s[k]+=rs[a][0]["stats"].get(k,0)
            if ref is not None and all(done.values()):paired[a]+=med[a]["reward"]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("MLOCAL_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6)] for a in ARMS},flush=True)
    controls=(*fixed,"structural");s=stats["cache"]
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    passed=all(s["verified"]>=stats[a]["verified"] and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) for a in controls) and cached>0
    result=dict(stats=stats,references=refs,paired=paired,gains=gains,cache_verified_cases=cached,novel_verified_recoveries=recoveries,oracle=oracle,primary_pass=passed,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("MLOCAL_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
