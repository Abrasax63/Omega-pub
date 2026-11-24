"""SEPARATOR01: exact separator conditioning and cached component factors."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import resource_learn01 as old
import reorg01 as reorg
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("direct","condition","factor","partition")
CAP=8192
CPU=.8
def cohort():
    rng=random.Random(20270135)
    for n in (24,40,56,72):
        for f in range(8):
            pairs=list(it.combinations(range(n),2));groups=[];e=[]
            if f<5:
                start=0
                while start<n:
                    w=(4,3,5,2 if len(groups)%2==0 else 6,6)[f]
                    groups.append(list(range(start,min(n,start+w))));start+=w
                for g in groups:
                    if f==0:e+=list(it.combinations(g,2))
                    elif f==1:e+=list(zip(g,g[1:]))
                    else:
                        e+=list(zip(g,g[1:]))
                        e+=[(a,b) for a,b in it.combinations(g,2) if b!=a+1 and rng.random()<(.35 if f==2 else .8)]
                for a,b in zip(groups,groups[1:]):
                    if f in (0,2):e.append((rng.choice(a),rng.choice(b)))
                    elif f==1:e+=list(zip(a,b))
                    else:
                        e += [(u,v) for u in a for v in b if rng.random()<(.85 if f==3 else .22)]
                        if not any(u in a and v in b for u,v in e):e.append((rng.choice(a),rng.choice(b)))
            else:
                def p(a,b):return .42 if f==5 else .12 if f==6 else (.4 if (a<n//2)==(b<n//2) else .035)
                e=[(a,b) for a,b in pairs if rng.random()<p(a,b)]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[[labels[v] for v in g] for g in groups]
def components(adj,mask):
    out=[]
    while mask:
        part=front=mask&-mask
        while front:
            z=0
            for v in bits(front):z|=adj[v]&mask&~part
            part|=z;front=z
        out.append(part);mask^=part
    return out
def layers(adj,m,root):
    visited=front=1<<root;out=[front]
    while front:
        z=0
        for v in bits(front):z|=adj[v]&m&~visited
        if not z:break
        out.append(z);visited|=z;front=z
    assert visited==m
    return out
def find_separator(adj,m,stats):
    size=m.bit_count();root=min(bits(m),key=lambda v:((adj[v]&m).bit_count(),v))
    first=layers(adj,m,root)
    other=min(bits(first[-1]))
    candidates=set(s for s in first+layers(adj,m,other) if 1<=s.bit_count()<=3)
    best=None
    for s in sorted(candidates):
        stats["separator_probes"]+=1
        cs=components(adj,m^s);largest=max((c.bit_count() for c in cs),default=0)
        if len(cs)<2 or 5*largest>4*size:continue
        key=(largest,s.bit_count(),s)
        if best is None or key<best[0]:best=(key,s,cs)
    return best
def assignments(adj,s):
    vs=list(bits(s))
    for b in range(1<<len(vs)):
        chosen=[v for i,v in enumerate(vs) if b>>i&1]
        if any(adj[u]>>v&1 for u,v in it.combinations(chosen,2)):continue
        blocked=0
        for v in chosen:blocked|=adj[v]
        yield blocked
def factor_sum(adj,m,s,cs,rec,stats):
    factors={};total=0
    for blocked in assignments(adj,s):
        prod=1;stats["assignments"]+=1
        for c in cs:
            residual=c&~blocked
            stats["factor_requests"]+=1
            if residual in factors:stats["factor_hits"]+=1
            else:factors[residual]=rec(residual)
            prod*=factors[residual]
        total+=prod
    return total
def condition_sum(adj,m,s,rec,stats):
    total=0
    for blocked in assignments(adj,s):
        stats["assignments"]+=1
        total+=rec((m^s)&~blocked)
    return total
def run(n,e,arm,cap=CAP):
    if arm=="partition":return reorg.run(n,e,"partition",cap=cap)
    start=time.process_time();wall=time.perf_counter();stats=Counter();memo={};value=None
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        adj=core.make_graph(n,e)
        def rec(m):
            if stats["visits"]>=cap:raise Limit
            stats["visits"]+=1
            if m in memo:stats["memo_hits"]+=1;return memo[m]
            if not m:return 1
            iso=sum(1<<v for v in bits(m) if not adj[v]&m)
            if iso:ans=(1<<iso.bit_count())*rec(m^iso)
            else:
                cs=components(adj,m)
                if len(cs)>1:
                    # Match previous engine's binary component recurrence.
                    ans=rec(cs[0])*rec(m^cs[0])
                else:
                    size=m.bit_count();ans=None
                    if size>=4:
                        ds=sum((adj[v]&m).bit_count() for v in bits(m))
                        if ds==2*(size-1) or ds>=.7*size*(size-1):
                            ans,_=structural(adj,m,stats)
                    if ans is None and arm!="direct" and size>=16:
                        stats["separator_searches"]+=1
                        found=find_separator(adj,m,stats)
                        if found is not None:
                            key,s,cs=found;stats["separators"]+=1
                            stats["separator_vertices"]+=s.bit_count()
                            stats["largest_component_sum"]+=key[0]
                            if arm=="condition":ans=condition_sum(adj,m,s,rec,stats)
                            else:ans=factor_sum(adj,m,s,cs,rec,stats)
                    if ans is None and size>=8 and stats["visits"]>=512 and ds<=4*size:
                        ans=eliminate(adj,m,stats)
                    if ans is None:
                        v=max(bits(m),key=lambda u:((adj[u]&m).bit_count(),-u))
                        rem=m^(1<<v);ans=rec(rem)+rec(rem&~adj[v])
            memo[m]=ans
            return ans
        value=rec((1<<n)-1)
    except Limit:value=None
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start;t=time.perf_counter()-wall
    if sec>CPU:value=None
    assert stats["visits"]<=cap
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
def transfer(n,e,groups):
    # Independent ordered-group DP, using explicit edge lists and subsets.
    idx={v:i for i,g in enumerate(groups) for v in g}
    assert sorted(idx)==list(range(n)) and sum(map(len,groups))==n
    assert all(abs(idx[a]-idx[b])<=1 for a,b in e)
    prev={frozenset():1};prev_group=set()
    for g in groups:
        group=set(g)
        inside=[(a,b) for a,b in e if a in group and b in group]
        cross=[(a,b) if a in prev_group else (b,a) for a,b in e if (a in prev_group and b in group) or (b in prev_group and a in group)]
        nxt={}
        for k in range(1<<len(g)):
            s=frozenset(v for j,v in enumerate(g) if k>>j&1)
            if any(a in s and b in s for a,b in inside):continue
            nxt[s]=sum(w for q,w in prev.items() if not any(a in q and b in s for a,b in cross))
        prev=nxt;prev_group=group
    return sum(prev.values())
def brute(n,e,m):
    return sum(b&~m==0 and not any(b>>a&1 and b>>c&1 for a,c in e) for b in range(1<<n))
def selftests():
    forced=0;transfers=0;checks=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for i in range(1<<len(pairs)):
            e=[p for j,p in enumerate(pairs) if i>>j&1];m=(1<<n)-1;ref=brute(n,e,m);adj=core.make_graph(n,e)
            assert transfer(n,e,[list(range(n//2)),list(range(n//2,n))])==ref;transfers+=1
            for a in ARMS[:3]:
                assert run(n,e,a)["count"]==ref;checks+=1
            for s in range(1,m+1):
                cs=components(adj,m^s)
                if len(cs)<2:continue
                fun=lambda x:brute(n,e,x)
                assert factor_sum(adj,m,s,cs,fun,Counter())==condition_sum(adj,m,s,fun,Counter())==ref
                forced+=1
    e=[]
    for start in range(0,24,4):
        e+=list(it.combinations(range(start,start+4),2))
        if start:e.append((start-1,start))
    ref=transfer(24,e,[list(range(i,i+4)) for i in range(0,24,4)])
    for a in ("condition","factor"):
        r=run(24,e,a);assert r["count"]==ref and r["stats"]["separators"]>0
        assert run(24,e,a,cap=1)["count"] is None
    return dict(solver_checks=checks,transfer_checks=transfers,forced_separator_checks=forced,eligible=True,fail_closed=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==32 and len({(n,e) for n,f,e,g in data})==32
    stats={a:Counter() for a in ARMS};split={k:{a:Counter() for a in ARMS} for k in ("structured","control")};refs=Counter();records=[];paired=Counter();used=0;recoveries=0
    for j,(n,f,e,g) in enumerate(data):
        ref,kind=(transfer(n,e,g),"GROUP_TRANSFER") if g else old.stronger_reference(n,{5:3,6:2,7:7}[f],e,[],None)
        refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270136+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        if ref is not None:
            used+=int(done["factor"] and any(r["count"] is not None and r["stats"].get("separators",0)>0 for r in rs["factor"]))
            recoveries+=int(done["factor"] and not done["direct"] and not done["partition"])
        for a in ARMS:
            for s in (stats[a],split["structured" if g else "control"][a]):
                s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
                for k in ("reward","cpu","wall"):s[k]+=med[a][k]
                if ref is not None:s["verified_reward"]+=med[a]["reward"]
                for k in ("visits","memo_hits","separator_searches","separator_probes","separators","separator_vertices","largest_component_sum","assignments","factor_requests","factor_hits","factor_lookups"):s[k]+=rs[a][0]["stats"].get(k,0)
            if ref is not None and all(done.values()):paired[a]+=med[a]["reward"]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,groups=g,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("SEP_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6),rs[a][0]["stats"].get("separators",0)] for a in ARMS},flush=True)
    s=stats["factor"];controls=("direct","partition")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in ("direct","partition","condition")}
    passed=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) for a in ("direct","partition","condition")) and all(gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls) and used>0
    secondary=s["verified"]>=stats["condition"]["verified"] and gains["condition"]>=.15
    result=dict(stats=stats,split=split,references=refs,paired=paired,gains=gains,verified_separator_cases=used,novel_verified_recoveries=recoveries,primary_pass=passed,factorization_pass=secondary,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("SEP_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
