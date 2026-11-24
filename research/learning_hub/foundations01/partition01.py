"""PARTITION01: unique exact residual jobs; explicit dependency recomposition."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import arch_gate01 as gate
import arch_local01 as local
import arch_coop01 as coop
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm,CPU,reference
ARMS=("dag_branch","dag_specialist","branch","local","delay","shared_race")
def cohort():
    rng=random.Random(20270117)
    for n in (16,24,40,56,72):
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


class Registry:
    def __init__(self,stats,cap=4096):
        self.jobs={};self.stats=stats;self.cap=cap
    def request(self,mask):
        if self.stats["requests"]>=self.cap:raise Limit
        self.stats["requests"]+=1
        if mask in self.jobs:self.stats["repeated_requests"]+=1
        else:self.jobs[mask]=["NEW",None,None]
    def wait(self,mask,kind,children,scale=1):
        assert self.jobs[mask][0]=="NEW"
        assert kind in ("sum","product","scale")
        assert len(children)==(1 if kind=="scale" else 2)
        assert all(c>=0 and c&mask==c and c.bit_count()<mask.bit_count() for c in children)
        self.jobs[mask]=["WAITING",(kind,tuple(children),scale),None]
        for child in children:self.request(child)
    def done(self,mask,value):
        if self.jobs[mask][0]=="DONE":
            self.stats["duplicate_completed"]+=1
            raise AssertionError("duplicate completion")
        assert isinstance(value,int) and 1<=value<=1<<mask.bit_count()
        self.jobs[mask]=["DONE",None,value]
        self.stats["completed"]+=1
    def recombine(self,mask):
        status,plan,_=self.jobs[mask]
        assert status=="WAITING"
        kind,children,scale=plan
        assert all(self.jobs[c][0]=="DONE" for c in children)
        vals=[self.jobs[c][2] for c in children]
        self.done(mask,sum(vals) if kind=="sum" else vals[0]*vals[1] if kind=="product" else scale*vals[0])
def partition(n,e,specialist,cap=4096):
    adj=core.make_graph(n,e);stats=Counter();reg=Registry(stats,cap);root=(1<<n)-1
    start=time.process_time();wall=time.perf_counter();value=None
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        reg.request(root);stack=[root]
        while stack:
            stats["peak_stack"]=max(stats["peak_stack"],len(stack))
            mask=stack[-1];status,plan,_=reg.jobs[mask]
            if status=="DONE":
                stack.pop();continue
            if status=="WAITING":
                children=plan[1]
                todo=next((c for c in children if reg.jobs[c][0]!="DONE"),None)
                if todo is None:reg.recombine(mask);stack.pop()
                else:
                    assert todo not in stack
                    stack.append(todo)
                continue
            assert status=="NEW"
            stats["unique_expansions"]+=1
            if not mask:reg.done(mask,1);stack.pop();continue
            iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
            if iso:
                reg.wait(mask,"scale",[mask^iso],1<<iso.bit_count());continue
            first=mask&-mask;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&mask&~part
                part|=z;front=z
            if part!=mask:
                reg.wait(mask,"product",[part,mask^part]);continue
            ans=None;m=mask.bit_count()
            if specialist and m>=4:
                ds=sum((adj[v]&mask).bit_count() for v in bits(mask));stats["features"]+=1
                if ds==2*(m-1) or ds>=.7*m*(m-1):
                    ans,method=structural(adj,mask,stats)
                if ans is None and m>=8 and stats["requests"]>=512 and ds<=4*m:
                    ans=eliminate(adj,mask,stats)
                    if ans is not None:method="elimination"
                if ans is not None:stats["dispatch_"+method]+=1
            if ans is not None:reg.done(mask,ans);stack.pop();continue
            v=max(bits(mask),key=lambda u:((adj[u]&mask).bit_count(),-u))
            rem=mask^(1<<v)
            reg.wait(mask,"sum",[rem,rem&~adj[v]])
        value=reg.jobs[root][2]
        assert reg.jobs[root][0]=="DONE"
        assert all(j[0]=="DONE" for j in reg.jobs.values())
    except Limit:value=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    if sec>CPU:value=None
    stats["nodes"]=len(reg.jobs)
    assert stats["requests"]<=cap and stats["nodes"]<=cap
    assert stats["duplicate_completed"]==0 and stats["unique_expansions"]<=stats["nodes"]
    return dict(count=value,cost=min(sec,CPU) if value is not None else CPU,seconds=sec,wall=time.perf_counter()-wall,stats=dict(stats))
def selftests():
    assert partition(0,[],False)["count"]==1
    assert partition(4,[(0,1),(2,3)],False)["count"]==9
    s=Counter();r=Registry(s)
    r.request(7);r.wait(7,"sum",[3,5])
    r.wait(3,"sum",[1,2]);r.wait(5,"sum",[1,4])
    assert s["repeated_requests"]==1
    for k in (1,2,4):r.done(k,1)
    r.recombine(3);r.recombine(5);r.recombine(7);assert r.jobs[7][2]==4
    s=Counter();r=Registry(s);r.request(3)
    try:r.wait(3,"sum",[3,1])
    except AssertionError:pass
    else:raise AssertionError("bad dependency accepted")
    r.done(3,2)
    try:r.done(3,2)
    except AssertionError:pass
    else:raise AssertionError("duplicate accepted")
    assert partition(4,[(0,1),(1,2),(2,3)],False,cap=1)["count"] is None
    return 6
def solve(n,e,a):
    if a.startswith("dag"):return partition(n,e,a=="dag_specialist")
    if a=="shared_race":return coop.cooperative(n,e,"shared")
    if a=="local":return local.solve(n,e,(4,8,512))
    return gate.solve(n,e,4097 if a=="branch" else 512)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests()
    data=list(cohort());assert len(data)==40 and len({(n,e) for n,f,e,h,p in data})==40
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];paired=Counter()
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=reference(n,f,e,h,p);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270118+3*j+k).shuffle(order)
            for a in order:rs[a].append(solve(n,e,a))
        gate.audit(rs,ref)
        med={a:statistics.median(r["cost"] for r in rows) for a,rows in rs.items()}
        done={a:sum(r["count"] is not None for r in rows)>=2 for a,rows in rs.items()}
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a]);s["all_cost"]+=med[a]
            r=rs[a][0]["stats"]
            for name in ("visits","requests","repeated_requests","unique_expansions","duplicate_completed","completed","cross_hits","factor_lookups","structural_probes","elimination_probes","dispatch_tree","dispatch_multipartite","dispatch_elimination"):s[name]+=r.get(name,0)
            for name in ("peak_stack","nodes"):s["max_"+name]=max(s["max_"+name],r.get(name,0))
            if a.startswith("dag"):s["cases_with_repeated_requests"]+=int(r.get("repeated_requests",0)>0)
            if ref is not None:s["verified_cost"]+=med[a]
        if ref is not None and all(done.values()):
            paired["cases"]+=1
            for a in ARMS:paired[a]+=med[a]
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,median_cost=med,completed=done))
        print("PARTITION_CASE",n,f,kind,{a:[done[a],round(med[a],6)] for a in ARMS},flush=True)
    s=stats["dag_specialist"];l=stats["local"];r=stats["shared_race"]
    gains={a:1-s["verified_cost"]/stats[a]["verified_cost"] for a in ("shared_race","local")}
    passed=s["verified"]>=max(l["verified"],r["verified"]) and all(v>=.15 for v in gains.values()) and s["all_cost"]<=l["all_cost"] and (s["unverified"]<=l["unverified"] or s["verified"]>l["verified"])
    result=dict(stats=stats,references=refs,paired=paired,gains=gains,selftests=tests,safety_pass=True,primary_pass=passed,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("PARTITION_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
