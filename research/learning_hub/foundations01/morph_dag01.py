"""MORPH-DAG01: one persistent exact dependency graph, changing future expansion rules."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import resource_learn01 as old
import reorg01 as reorg
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("binary","multi","morph","direct","partition")
CAP=8192
CPU=.8
def cohort():
    rng=random.Random(20270131)
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
            multi=(arm=="multi" or (arm=="morph" and lo<=stats["requests"]<hi)) and size>=min_size and ds[ordered[0]]>=3
            if multi:
                ch=condition(adj,m,ordered[:2]);reg.plan(m,"sum",ch)
                stats["multi"]+=1;stats["aggregated_children"]+=sum(w for c,w in ch)-len(ch)
            else:
                v=ordered[0];rem=m^(1<<v)
                reg.plan(m,"sum",[(rem,1),(rem&~adj[v],1)]);stats["binary"]+=1
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
    checks=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for m in range(1<<len(pairs)):
            e=[p for i,p in enumerate(pairs) if m>>i&1]
            v=sum(not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
            for a in ARMS[:3]:
                assert run(n,e,a)["count"]==v;checks+=1
    # cycle plus chords gives degree >=3; unchorded cycle is ineligible.
    n=12;e=[(i,(i+1)%n) for i in range(n)]+[(0,6),(2,8),(4,10)]
    ref=core.reference(n,e)[0]
    r=run(n,e,"morph",lo=1,hi=5,min_size=4)
    assert r["count"]==ref and r["stats"]["multi"]>0 and r["stats"]["binary"]>0
    assert run(n,e,"morph",cap=1)["count"] is None
    s=Counter();reg=Registry(s,8);reg.request(3)
    try:reg.plan(3,"sum",[(3,1)])
    except AssertionError:pass
    else:raise AssertionError("bad dependency accepted")
    reg.done(3,2)
    try:reg.done(3,2)
    except AssertionError:pass
    else:raise AssertionError("duplicate accepted")
    return dict(exhaustive=checks,forced_morph=True,fail_closed=True,invalid_dependency=True,duplicate_rejected=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];paired=Counter();mixed=0
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=old.stronger_reference(n,7 if f==6 else f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270132+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        if ref is not None and done["morph"] and any(r["count"] is not None and r["stats"].get("binary",0)>0 and r["stats"].get("multi",0)>0 for r in rs["morph"]):mixed+=1
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
            for k in ("reward","cpu","wall"):s[k]+=med[a][k]
            if ref is not None:s["verified_reward"]+=med[a]["reward"]
            for k in ("requests","reused_requests","expansions","completed","binary","multi","aggregated_children","specialist","nodes","unfinished","reachable_audit_skipped","visits"):s[k]+=rs[a][0]["stats"].get(k,0)
            if ref is not None and all(done.values()):paired[a]+=med[a]["reward"]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("MORPH_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6)] for a in ARMS},flush=True)
    controls=("binary","multi","direct","partition");s=stats["morph"]
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    passed=all(s["verified"]>=stats[a]["verified"] and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) for a in controls) and mixed>0
    result=dict(stats=stats,references=refs,paired=paired,gains=gains,mixed_verified=mixed,primary_pass=passed,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("MORPH_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
