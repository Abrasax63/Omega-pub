"""TRANSFER-REUSE01: immutable boundary vector for distinct conditional queries."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter,defaultdict
from pathlib import Path
import transfer01 as tr
import separator_value01 as sep
import resource_learn01 as old
from arch_switch01 import core,bits,Limit,alarm
ARMS=("direct","fresh","reuse")
CAP=49152
CPU=2.
def prior_cohort():
    rng=random.Random(20270149)
    for n in (24,40,56):
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

def queries(suffix):
    a,b,c,d=list(suffix)[:4]
    return [(0,0),(1<<a,0),(0,1<<b),((1<<a)|(1<<c),0),(1<<b,(1<<c)|(1<<d)),(0,(1<<a)|(1<<b)|(1<<d))]
def conditioned(adj,n,inc,exc):
    if inc&exc or any(adj[v]&inc for v in bits(inc)):return None
    blocked=inc|exc
    for v in bits(inc):blocked|=adj[v]
    return ((1<<n)-1)&~blocked
def reduced(n,e,mask):
    vs=list(bits(mask));ix={v:i for i,v in enumerate(vs)}
    return len(vs),[(ix[a],ix[b]) for a,b in e if a in ix and b in ix],ix
def dp(adj,order,remaining,states,inc,exc,stats,cap):
    for v in order:
        b=1<<v;remaining^=b;nxt=defaultdict(int)
        for s,w in states.items():
            if stats["work"]>=cap:raise Limit
            stats["work"]+=1
            t=s&remaining
            if not inc&b:nxt[t]+=w
            if not (exc|s)&b:nxt[t|(adj[v]&remaining)]+=w
        states=nxt
        stats["peak"]=max(stats["peak"],len(states))
    return states
def run(n,e,prefix,qs,arm,cap=CAP,cpu=CPU):
    start=time.process_time();wall=time.perf_counter();stats=Counter();ans=[None]*len(qs)
    adj=core.make_graph(n,e);m=(1<<n)-1
    if arm=="direct":
        for i,(inc,exc) in enumerate(qs):
            mask=conditioned(adj,n,inc,exc)
            if mask is None:ans[i]=0;continue
            left=cpu-(time.process_time()-start)
            if left<=0 or stats["work"]>=cap:break
            nn,ee,_=reduced(n,e,mask)
            r=old.solve(nn,ee,(4,8,512),cap-stats["work"],left)
            stats["work"]+=r["stats"].get("visits",0)
            if time.process_time()-start<=cpu:ans[i]=r["count"]
    else:
        signal.setitimer(signal.ITIMER_PROF,cpu)
        try:
            order=tr.discover(adj,n,stats);p=[v for v in order if prefix>>v&1];q=[v for v in order if not prefix>>v&1]
            suffix=m^prefix
            if arm=="reuse":
                table=dp(adj,p,m,{0:1},0,0,stats,cap);frozen=tuple(sorted(table.items()))
                stats["prefix_work"]=stats["work"];stats["prefix_states"]=len(table)
            for i,(inc,exc) in enumerate(qs):
                assert not (inc|exc)&prefix
                if conditioned(adj,n,inc,exc) is None:ans[i]=0;continue
                if arm=="reuse":
                    end=dp(adj,q,suffix,table,inc,exc,stats,cap)
                    assert tuple(sorted(table.items()))==frozen
                else:end=dp(adj,p+q,m,{0:1},inc,exc,stats,cap)
                ans[i]=sum(end.values())
        except Limit:pass
        finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start;t=time.perf_counter()-wall
    # Reject outputs if batch overran timer, conservatively last completed value.
    if sec>cpu:
        last=next((i for i in reversed(range(len(ans))) if ans[i] is not None),None)
        if last is not None:ans[last]=None
    assert stats["work"]<=cap
    return dict(counts=ans,cpu=sec,wall=t,reward=t+.25*sec+sum(v is None for v in ans),stats=dict(stats))
def references(n,f,e,g,qs):
    adj=core.make_graph(n,e);out=[]
    for inc,exc in qs:
        mask=conditioned(adj,n,inc,exc)
        if mask is None:out.append(0);continue
        nn,ee,ix=reduced(n,e,mask)
        if g:
            gg=[[ix[v] for v in row if v in ix] for row in g]
            out.append(sep.transfer(nn,ee,gg))
        else:
            v,_=old.stronger_reference(nn,{5:3,6:2,7:7}[f],ee,[],None)
            out.append(v)
    return out
def selftests():
    checks=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2));m=(1<<n)-1
        for k in range(1<<len(pairs)):
            e=[p for j,p in enumerate(pairs) if k>>j&1]
            prefix=(1<<(n//2))-1;suffix=m^prefix
            qs=[(i,x) for i in range(m+1) for x in range(m+1) if not (i|x)&prefix]
            ref=[sum((b&i)==i and not b&x and not any(b>>u&1 and b>>v&1 for u,v in e) for b in range(m+1)) for i,x in qs]
            for a in ARMS:
                assert run(n,e,prefix,qs,a)["counts"]==ref;checks+=len(qs)
    assert run(24,[(i,i+1) for i in range(23)],(1<<12)-1,[(0,0)],"reuse",cap=1)["counts"]==[None]
    return dict(conditioned_checks=checks,cap_failure=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests()
    data=[x for x in prior_cohort() if x[1] in (0,1,4,5,6,7)]
    assert len(data)==18
    stats={a:Counter() for a in ARMS};records=[];allrefs=0;fullbatches=0;strict=0;relabel=0;paired=Counter()
    for j,(n,f,e,g) in enumerate(data):
        adj=core.make_graph(n,e);order=tr.discover(adj,n,Counter());prefix=sum(1<<v for v in order[:n//2])
        qs=queries(order[n//2:]);ref=references(n,f,e,g,qs);full=all(v is not None for v in ref)
        seen=[set() for _ in qs]
        for label in range(2):
            perm=list(range(n))
            if label:random.Random(20270150+j).shuffle(perm)
            def pm(m):return sum(1<<perm[v] for v in bits(m))
            ee=tuple(sorted(tuple(sorted((perm[u],perm[v]))) for u,v in e));pp=pm(prefix);qq=[(pm(i),pm(x)) for i,x in qs]
            rs={a:[] for a in ARMS}
            for k in range(3):
                order_a=list(ARMS);random.Random(20270151+6*j+3*label+k).shuffle(order_a)
                for a in order_a:rs[a].append(run(n,ee,pp,qq,a))
            allrefs+=sum(v is not None for v in ref);fullbatches+=int(full)
            med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
            done={a:[sum(r["counts"][i] is not None for r in rr)>=2 for i in range(len(qs))] for a,rr in rs.items()}
            for a,rr in rs.items():
                for r in rr:
                    for i,v in enumerate(r["counts"]):
                        if v is not None:
                            seen[i].add(v);assert len(seen[i])==1
                            assert ref[i] is None or ref[i]==v
                s=stats[a]
                s["verified"]+=sum(d and v is not None for d,v in zip(done[a],ref))
                s["unverified"]+=sum(d and v is None for d,v in zip(done[a],ref))
                s["unresolved"]+=sum(not d for d in done[a])
                for key in ("reward","cpu","wall"):s[key]+=med[a][key]
                if full:s["verified_reward"]+=med[a]["reward"]
                for key in ("work","prefix_work","prefix_states","peak"):s[key]+=rr[0]["stats"].get(key,0)
                if full and all(all(x) for x in done.values()):paired[a]+=med[a]["reward"]
            if full and all(done["reuse"]) and rs["reuse"][0]["stats"].get("work",0)<rs["fresh"][0]["stats"].get("work",0):strict+=1
            paired["batches"]+=int(full and all(all(x) for x in done.values()))
            records.append(dict(n=n,family=f,label=label,edges=ee,prefix=pp,queries=qq,reference=ref,results=rs,med=med,done=done))
            print("REUSE_CASE",n,f,label,full,{a:[sum(done[a]),round(med[a]["reward"],6)] for a in ARMS},flush=True)
        relabel+=sum(bool(v) for v in seen)
    s=stats["reuse"];controls=("direct","fresh")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    primary=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls)
    reduction=1-s["work"]/stats["fresh"]["work"]
    result=dict(stats=stats,reference_queries=allrefs,full_reference_batches=fullbatches,strict_verified_batches=strict,paired=paired,relabel_consistent_queries=relabel,gains=gains,state_reduction=reduction,primary_pass=primary,secondary_pass=reduction>=.25 and strict>0,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("REUSE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
