"""PARALLEL01: matched unique frontier tasks, actual worker processes."""
import itertools as it,json,random,signal,statistics,time,os,resource,multiprocessing as mp
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import arch_local01 as local
from arch_switch01 import core,bits,alarm,reference
ARMS=("serial","p1","p2","p4","direct")
def cohort():
    rng=random.Random(20270119)
    for n in (32,48,64,72):
        for f in range(8):
            if f not in (1,2,3,7) and n!=48:continue
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



def frontier(n,e):
    adj=core.make_graph(n,e)
    selected=sorted(range(n),key=lambda v:(-adj[v].bit_count(),v))[:4]
    root=(1<<n)-1;fixed=sum(1<<v for v in selected);weights=Counter()
    for b in range(1<<len(selected)):
        chosen=[v for i,v in enumerate(selected) if b>>i&1]
        if any(adj[u]>>v&1 for u,v in it.combinations(chosen,2)):continue
        residual=root&~fixed
        for v in chosen:residual&=~adj[v]
        weights[residual]+=1
    return weights
def induced(n,e,mask):
    vs=list(bits(mask));idx={v:i for i,v in enumerate(vs)}
    return len(vs),[(idx[a],idx[b]) for a,b in e if a in idx and b in idx]
def init():signal.signal(signal.SIGPROF,alarm)
def task(arg):
    n,e,mask=arg
    start=time.monotonic_ns();cpu=time.process_time()
    m,edges=induced(n,e,mask);r=local.solve(m,edges,(4,8,512))
    return dict(mask=mask,pid=os.getpid(),start=start,end=time.monotonic_ns(),
                cpu=time.process_time()-cpu,count=r["count"],visits=r["stats"].get("visits",0))
def combine(weights,rows):
    assert len(rows)==len(weights) and {r["mask"] for r in rows}==set(weights)
    if any(r["count"] is None for r in rows):return None
    return sum(weights[r["mask"]]*r["count"] for r in rows)
def overlap(rows):
    events=[(r[k],d,r["pid"]) for r in rows for k,d in (("start",1),("end",-1))]
    active=Counter();peak=0
    for _,d,p in sorted(events):
        active[p]+=d
        assert active[p]>=0
        peak=max(peak,sum(v>0 for v in active.values()))
    return peak
def run_case(case,arm,pool):
    n,f,e,h,p=case;start=time.perf_counter();parent=time.process_time()
    if arm=="direct":
        r=local.solve(n,e,(4,8,512))
        return dict(count=r["count"],wall=time.perf_counter()-start,cpu=time.process_time()-parent,
                    tasks=0,rows=[],peak_overlap=0,assignments=0)
    w=frontier(n,e);args=[(n,e,m) for m in sorted(w,key=lambda m:(-m.bit_count(),m))]
    if pool is None:rows=[task(a) for a in args]
    else:
        futures=[pool.submit(task,a) for a in args]
        rows=[f.result() for f in as_completed(futures)]
    val=combine(w,rows)
    return dict(count=val,wall=time.perf_counter()-start,
                cpu=time.process_time()-parent+(sum(r["cpu"] for r in rows) if pool else 0),
                tasks=len(w),assignments=sum(w.values()),rows=rows,peak_overlap=overlap(rows),
                duplicate_frontier_tasks=0)
def child_cpu():
    r=resource.getrusage(resource.RUSAGE_CHILDREN);return r.ru_utime+r.ru_stime
def machine():
    d=dict(logical_cpus=os.cpu_count(),affinity=sorted(os.sched_getaffinity(0)))
    for path in ("/sys/fs/cgroup/cpu.max","/sys/fs/cgroup/cpu.stat","/sys/fs/cgroup/cpu/cpu.cfs_quota_us","/sys/fs/cgroup/cpu/cpu.cfs_period_us","/sys/fs/cgroup/cpuset.cpus.effective"):
        try:d[path]=Path(path).read_text().strip()
        except OSError:pass
    try:
        pairs=set()
        for cpu in d["affinity"]:
            root=Path("/sys/devices/system/cpu")/("cpu"+str(cpu))/"topology"
            pairs.add((root.joinpath("physical_package_id").read_text().strip(),root.joinpath("core_id").read_text().strip()))
        d["visible_core_ids"]=len(pairs)
    except OSError:pass
    return d
def selftests():
    count=0;dedup=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for m in range(1<<len(pairs)):
            e=[p for i,p in enumerate(pairs) if m>>i&1]
            w=frontier(n,e);rows=[]
            for residual in w:
                z,ee=induced(n,e,residual)
                value=sum(not any(b>>a&1 and b>>c&1 for a,c in ee) for b in range(1<<z))
                rows.append(dict(mask=residual,count=value))
            ref=sum(not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
            assert combine(w,rows)==ref
            bad=[dict(r) for r in rows];bad[0]["count"]=None;assert combine(w,bad) is None
            count+=1;dedup+=int(sum(w.values())>len(w))
    assert dedup>0
    return dict(exhaustive_graphs=count,multiplicity_cases=dedup,fail_closed_cases=count)
def main(out):
    init();hw=machine();tests=selftests();data=list(cohort())
    assert len(data)==20 and len({(n,e) for n,f,e,h,p in data})==20
    refs=[reference(n,f,e,h,p) for n,f,e,h,p in data]
    results=[{a:[] for a in ARMS} for _ in data];aggregate={a:[] for a in ARMS}
    print("PARALLEL_MACHINE",json.dumps(hw),flush=True)
    for rep in range(3):
        order=list(ARMS);random.Random(20270120+rep).shuffle(order)
        cases=list(range(len(data)));random.Random(20270123+rep).shuffle(cases)
        for arm in order:
            start=time.perf_counter();cpu=time.process_time();child=child_cpu()
            if arm.startswith("p"):
                with ProcessPoolExecutor(max_workers=int(arm[1:]),mp_context=mp.get_context("fork"),initializer=init) as pool:
                    for j in cases:results[j][arm].append(run_case(data[j],arm,pool))
            else:
                for j in cases:results[j][arm].append(run_case(data[j],arm,None))
            aggregate[arm].append(dict(wall=time.perf_counter()-start,cpu=time.process_time()-cpu+child_cpu()-child))
            print("PARALLEL_ARM",rep,arm,aggregate[arm][-1],flush=True)
    stats={a:Counter() for a in ARMS};paired=Counter();records=[];parts=ARMS[:4];refs_count=Counter()
    for j,case in enumerate(data):
        n,f,e,h,p=case;ref,kind=refs[j];refs_count[kind]+=1;rs=results[j]
        vals={r["count"] for rr in rs.values() for r in rr if r["count"] is not None}
        assert len(vals)<=1 and (ref is None or not vals or vals=={ref})
        masks={r["mask"] for r in rs["serial"][0]["rows"]}
        assert all({t["mask"] for t in r["rows"]}==masks for a in parts for r in rs[a])
        for m in masks:
            lv={t["count"] for a in parts for r in rs[a] for t in r["rows"] if t["mask"]==m and t["count"] is not None}
            assert len(lv)<=1
        med={a:{k:statistics.median(r[k] for r in rs[a]) for k in ("wall","cpu")} for a in ARMS}
        done={a:sum(r["count"] is not None for r in rs[a])>=2 for a in ARMS}
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
            s["wall"]+=med[a]["wall"];s["cpu"]+=med[a]["cpu"]
            s["tasks"]+=rs[a][0]["tasks"];s["assignments"]+=rs[a][0]["assignments"]
            s["peak_overlap"]=max(s["peak_overlap"],max(r["peak_overlap"] for r in rs[a]))
            s["overlap_cases"]+=int(any(r["peak_overlap"]>1 for r in rs[a]))
            s["visits"]+=sum(t["visits"] for t in rs[a][0]["rows"])
        if ref is not None and all(done[a] for a in parts):
            paired["cases"]+=1
            for a in parts:
                for k in ("wall","cpu"):paired[a+"_"+k]+=med[a][k]
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,medians=med,completed=done))
    pids={a:sorted({t["pid"] for r in results for x in r[a] for t in x["rows"]}) for a in parts}
    assert pids["p1"] and all(p!=os.getpid() for p in pids["p1"])
    speed={a:paired["serial_wall"]/paired[a+"_wall"] for a in ("p1","p2","p4")}
    gate=paired["cases"]>0 and speed["p4"]>=1.25 and paired["p1_wall"]/paired["p4_wall"]>=1.25 and paired["p4_cpu"]<=1.25*paired["serial_cpu"] and stats["p4"]["verified"]>=stats["serial"]["verified"] and stats["p4"]["peak_overlap"]>1
    result=dict(machine=hw,selftests=tests,stats=stats,paired=paired,aggregate=aggregate,reference_kinds=refs_count,speed=speed,pids=pids,primary_pass=gate,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("PARALLEL_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
