"""SEPARATOR-VALUE01: exact BFS side cuts and value-sensitive activation."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import resource_learn01 as old
import reorg01 as reorg
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm
ARMS=("direct","partition","open128","cheap","value")
CAP=8192
CPU=.8
def prior_cohort():
    rng=random.Random(20270141)
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
def find_bounded(adj,m,stats,probe_cap=128,filter_balance=True):
    size=m.bit_count()
    root=min(bits(m),key=lambda v:((adj[v]&m).bit_count(),v))
    first=layers(adj,m,root)
    other=min(bits(first[-1]))
    candidates={}
    for ls in (first,layers(adj,m,other)):
        stats["bfs_vertices"]+=size
        prefix=0
        for s in ls:
            w=s.bit_count();suffix=size-prefix-w
            if 1<=w<=3 and (not filter_balance or 5*min(prefix,suffix)>=size):
                key=(max(prefix,suffix),w,s)
                if s not in candidates or key<candidates[s]:candidates[s]=key
            prefix+=w
    best=None
    for s in sorted(candidates,key=candidates.get):
        if stats["separator_probes"]>=probe_cap:break
        stats["separator_probes"]+=1
        cs=components(adj,m^s);largest=max((c.bit_count() for c in cs),default=0)
        if len(cs)<2 or 5*largest>4*size:
            stats["failed_probes"]+=1;continue
        key=(largest,s.bit_count(),s)
        if best is None or key<best[0]:best=(key,s,cs)
    return best
def cohort():
    yield from prior_cohort()
    rng=random.Random(20270142)
    for n in (24,40,56,72):
        for f in (8,9):
            m=n if f==8 else n-1
            w=8 if f==8 else 4
            groups=[list(range(i,min(m,i+w))) for i in range(0,m,w)]
            e=[]
            for g in groups:
                e+=list(it.combinations(g,2)) if f==9 else [(a,b) for a,b in it.combinations(g,2) if rng.random()<.65]
            for a,b in zip(groups,groups[1:]):
                e.append((rng.choice(a),rng.choice(b)))
                if f==8:e += [(u,v) for u in a for v in b if rng.random()<.16]
            if f==9:e += [(v,m) for v in range(m)]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[[labels[v] for v in g] for g in groups]
def cheap_cut(adj,m,stats):
    size=m.bit_count();root=min(bits(m),key=lambda v:((adj[v]&m).bit_count(),v))
    first=layers(adj,m,root);other=min(bits(first[-1]));best=None
    for ls in (first,layers(adj,m,other)):
        stats["bfs_vertices"]+=size
        prefix=0
        for s in ls:
            suffix=m&~(prefix|s)
            if 1<=s.bit_count()<=3 and 5*min(prefix.bit_count(),suffix.bit_count())>=size:
                stats["cheap_candidates"]+=1
                key=(max(prefix.bit_count(),suffix.bit_count()),s.bit_count(),s)
                if best is None or key<best[0]:best=(key,s,[prefix,suffix])
            prefix|=s
    return best
def proxy(masks,requests,memo):
    return requests+sum(1+(1<<((m.bit_count()+3)//4)) for m in masks if m and m not in memo)
def valuable(adj,m,s,cs,memo,stats):
    residuals=[]
    for blocked in assignments(adj,s):
        residuals.extend(c&~blocked for c in cs)
    v=max(bits(m),key=lambda u:((adj[u]&m).bit_count(),-u))
    rem=m^(1<<v);children=[rem,rem&~adj[v]]
    cut=proxy(set(residuals),len(residuals),memo)
    branch=proxy(set(children),len(children),memo)
    stats["value_evaluations"]+=1
    stats["value_factor_masks"]+=len(set(residuals))
    return 4*cut<=3*branch
def run(n,e,arm,cap=CAP):
    if arm=="partition":return reorg.run(n,e,"partition",cap=cap)
    start=time.process_time();wall=time.perf_counter();stats=Counter();memo={};value=None
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        adj=core.make_graph(n,e);root=(1<<n)-1;root_positive=False
        search_cap,probe_cap=128,1024
        def rec(m):
            nonlocal root_positive
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
                    if ans is None and size>=16 and arm in ("open128","cheap","value") and stats["separator_searches"]<search_cap and stats["separator_probes"]<probe_cap and (arm!="value" or ds<=8*size):
                        stats["separator_searches"]+=1
                        found=find_bounded(adj,m,stats,probe_cap,True) if arm=="open128" else cheap_cut(adj,m,stats)
                        if m==root:
                            stats["root_tested"]=1
                            root_positive=found is not None
                            stats["root_positive"]=int(root_positive)
                        if found is not None and arm=="value" and not valuable(adj,m,found[1],found[2],memo,stats):
                            stats["value_rejected"]+=1;found=None
                        if found is not None:
                            key,s,cs=found;stats["separators"]+=1
                            if m!=root and stats["root_tested"] and not root_positive:stats["late_after_negative"]+=1
                            stats["separator_vertices"]+=s.bit_count()
                            stats["largest_component_sum"]+=key[0]
                            ans=factor_sum(adj,m,s,cs,rec,stats)
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
    if arm in ("open128","cheap","value"):assert stats["separator_searches"]<=search_cap and stats["separator_probes"]<=probe_cap
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
from separator01 import transfer,brute
def reference(n,f,e,g):
    if f==9:
        apex=next(v for v in range(n) if all(v not in row for row in g))
        # Relabel for transfer reference, independent from solver.
        vs=[v for v in range(n) if v!=apex];ix={v:i for i,v in enumerate(vs)}
        return transfer(n-1,[(ix[a],ix[b]) for a,b in e if apex not in (a,b)],[[ix[v] for v in row] for row in g])+1,"APEX_TRANSFER"
    if g:return transfer(n,e,g),"GROUP_TRANSFER"
    return old.stronger_reference(n,{5:3,6:2,7:7}[f],e,[],None)
def selftests():
    checks=0;cuts=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for k in range(1<<len(pairs)):
            e=[p for j,p in enumerate(pairs) if k>>j&1];m=(1<<n)-1;adj=core.make_graph(n,e)
            ref=brute(n,e,m)
            for a in ARMS:
                assert run(n,e,a)["count"]==ref;checks+=1
            if n and len(components(adj,m))==1:
                for v in range(n):
                    prefix=0
                    for s in layers(adj,m,v):
                        suffix=m&~(prefix|s)
                        if prefix and suffix:
                            assert not any(adj[u]&suffix for u in bits(prefix))
                            fn=lambda x:brute(n,e,x)
                            assert factor_sum(adj,m,s,[prefix,suffix],fn,Counter())==ref
                            cuts+=1
                        prefix|=s
    e=[]
    for start in range(0,24,4):
        e+=list(it.combinations(range(start,start+4),2))
        if start:e.append((start-1,start))
    ref=transfer(24,e,[list(range(i,i+4)) for i in range(0,24,4)])
    for a in ("cheap","value"):
        r=run(24,e,a)
        assert r["count"]==ref and r["stats"]["separators"]>0
        assert run(24,e,a,cap=1)["count"] is None
    adj=core.make_graph(24,list(it.product(range(12),range(12,24))))
    assert cheap_cut(adj,(1<<24)-1,Counter()) is None
    # Proxy rejects a cut with no predicted saving: both branch children cached.
    adj=core.make_graph(24,e);m=(1<<24)-1;s=cheap_cut(adj,m,Counter())
    v=max(bits(m),key=lambda u:((adj[u]&m).bit_count(),-u));rem=m^(1<<v)
    assert not valuable(adj,m,s[1],s[2],{rem:1,rem&~adj[v]:1},Counter())
    return dict(exhaustive=checks,bfs_cut_identities=cuts,positive=True,negative=True,fail_closed=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==40 and len({(n,e) for n,f,e,g in data})==40
    stats={a:Counter() for a in ARMS};split={k:{a:Counter() for a in ARMS} for k in ("structured","random","new")};families={str(f):{a:Counter() for a in ARMS} for f in range(10)}
    refs=Counter();records=[];paired=Counter();oracle=Counter();recoveries=0
    for j,(n,f,e,g) in enumerate(data):
        ref,kind=reference(n,f,e,g);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270143+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        recoveries+=int(ref is not None and done["value"] and not any(done[a] for a in ("direct","partition","open128")))
        for key,arms in (("fixed",("direct","partition","open128")),("all",ARMS)):
            b=min(arms,key=lambda a:med[a]["reward"]);oracle[key+"_all"]+=med[b]["reward"]
            if ref is not None:oracle[key+"_verified"]+=med[b]["reward"]
        for a in ARMS:
            for s in (stats[a],split["structured" if f<5 else "random" if f<8 else "new"][a],families[str(f)][a]):
                s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
                for k in ("reward","cpu","wall"):s[k]+=med[a][k]
                if ref is not None:s["verified_reward"]+=med[a]["reward"]
                for k in ("visits","separator_searches","separator_probes","bfs_vertices","cheap_candidates","separators","factor_requests","factor_hits","value_evaluations","value_rejected","late_after_negative"):s[k]+=rs[a][0]["stats"].get(k,0)
            if ref is not None and all(done.values()):paired[a]+=med[a]["reward"]
        paired["cases"]+=int(ref is not None and all(done.values()))
        records.append(dict(n=n,family=f,edges=e,groups=g,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("SVAL_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6),rs[a][0]["stats"].get("separators",0)] for a in ARMS},flush=True)
    s=stats["value"];controls=("direct","partition","open128")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in ARMS if a!="value"}
    passed=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls)
    cheap_gain=1-stats["cheap"]["verified_reward"]/stats["open128"]["verified_reward"]
    secondary=cheap_gain>=.15 and stats["cheap"]["verified"]>=stats["open128"]["verified"]
    result=dict(stats=stats,split=split,families=families,references=refs,paired=paired,gains=gains,cheap_gain=cheap_gain,oracle=oracle,novel_verified_recoveries=recoveries,primary_pass=passed,secondary_pass=secondary,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("SVAL_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("records","families")}),flush=True)
    print("SVAL_FAMILIES",json.dumps({f:{a:{k:s[k] for k in ("verified","unverified","unresolved","verified_reward","reward")} for a,s in x.items()} for f,x in families.items()}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
