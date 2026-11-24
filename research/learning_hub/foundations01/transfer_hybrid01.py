"""TRANSFER-HYBRID01: reusable exact prefix and conserved fallback."""
import itertools as it,json,random,signal,statistics,time,hashlib
from collections import Counter,defaultdict
from pathlib import Path
import transfer01 as tr
import separator_value01 as sep
import resource_learn01 as old
from arch_switch01 import core,bits,Limit,alarm
ARMS=("direct","fresh","reuse","serialized")
CAP=49152
CPU=2.
def prior_cohort():
    rng=random.Random(20270153)
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
def digest(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def context(n,e,p,q):
    return digest(canonical([1,n,sorted(tuple(sorted(edge)) for edge in e),p,q]))
def encode(table,ctx):
    payload=canonical({"version":1,"context":ctx,"rows":sorted(table.items())})
    return canonical({"digest":digest(payload),"payload":payload.decode()})
def decode(raw,ctx,suffix,prefix):
    x=json.loads(raw);payload=x["payload"].encode()
    if digest(payload)!=x["digest"]:raise ValueError("digest")
    p=json.loads(payload)
    if p["version"]!=1 or p["context"]!=ctx:raise ValueError("context")
    out={}
    for mask,w in p["rows"]:
        if type(mask)!=int or type(w)!=int or mask<0 or mask&~suffix or not 0<w<=1<<prefix.bit_count() or mask in out:raise ValueError("row")
        out[mask]=w
    if not out or sum(out.values())>1<<prefix.bit_count():raise ValueError("mass")
    return out
def run(n,e,prefix,qs,arm,cap=CAP,cpu=CPU,trial=4096):
    start=time.process_time();wall=time.perf_counter();stats=Counter();ans=[None]*len(qs)
    adj=core.make_graph(n,e);m=(1<<n)-1;suffix=m^prefix
    def left():return cpu-(time.process_time()-start)
    def attempt(fn):
        before=stats["work"];budget=min(.12,left())
        if budget<=0 or before>=cap:return None
        begin=time.process_time()
        signal.setitimer(signal.ITIMER_PROF,budget)
        try:r=fn(min(cap,before+trial))
        except Limit:r=None
        finally:signal.setitimer(signal.ITIMER_PROF,0)
        if time.process_time()-begin>budget or left()<0:r=None
        if r is None:
            stats["abandoned_work"]+=stats["work"]-before
            stats["failed_trials"]+=1
        return r
    def direct(mask):
        if left()<=0 or stats["work"]>=cap:return None
        nn,ee,_=reduced(n,e,mask)
        remaining=left()
        if remaining<=0:return None
        r=old.solve(nn,ee,(4,8,512),cap-stats["work"],remaining)
        stats["work"]+=r["stats"].get("visits",0)
        stats["direct_work"]+=r["stats"].get("visits",0)
        return r["count"] if left()>=0 else None
    use=arm!="direct";table=None
    if use:
        order=tr.discover(adj,n,stats);p=[v for v in order if prefix>>v&1];q=[v for v in order if suffix>>v&1]
        stats["actual_width"]=tr.order_width(adj,p+q)
        if stats["actual_width"]>12:
            use=False;stats["width_fallback"]=1
        elif arm!="fresh":
            before=stats["work"]
            table=attempt(lambda lim:dp(adj,p,m,{0:1},0,0,stats,lim))
            stats["prefix_work"]=stats["work"]-before
            if table is None:use=False;stats["prefix_fallback"]=1
            else:
                stats["prefix_states"]=len(table)
                if arm=="serialized":
                    begin=time.process_time()
                    ctx=context(n,e,p,q);raw=encode(table,ctx);stats["serialized_bytes"]=len(raw)
                    table=decode(raw,ctx,suffix,prefix);stats["serialization_cpu"]=time.process_time()-begin
                frozen=tuple(sorted(table.items()))
    for i,(inc,exc) in enumerate(qs):
        assert not (inc|exc)&prefix
        if left()<=0:break
        mask=conditioned(adj,n,inc,exc)
        if mask is None:ans[i]=0;continue
        end=None
        if use:
            before=stats["work"]
            if arm=="fresh":end=attempt(lambda lim:dp(adj,p+q,m,{0:1},inc,exc,stats,lim))
            else:
                end=attempt(lambda lim:dp(adj,q,suffix,table,inc,exc,stats,lim))
                assert tuple(sorted(table.items()))==frozen
                if end is not None:stats["reused_queries"]+=1
            stats["dp_query_work"]+=stats["work"]-before
        if end is not None:
            v=sum(end.values())
            if left()>=0:ans[i]=v;stats["dp_answers"]+=1
        else:
            if arm!="direct":stats["fallback_queries"]+=1
            ans[i]=direct(mask)
    sec=time.process_time()-start;t=time.perf_counter()-wall
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
            prefix=(1<<(n//2))-1
            qs=[(i,x) for i in range(m+1) for x in range(m+1) if not (i|x)&prefix]
            ref=[sum((b&i)==i and not b&x and not any(b>>u&1 and b>>v&1 for u,v in e) for b in range(m+1)) for i,x in qs]
            for a in ARMS:
                assert run(n,e,prefix,qs,a)["counts"]==ref;checks+=len(qs)
    n=16;e=list(it.combinations(range(n),2));p=(1<<8)-1
    for a in ARMS[1:]:
        r=run(n,e,p,[(0,0)],a);assert r["counts"]==[17] and r["stats"]["width_fallback"]==1
    e=[(i,i+1) for i in range(23)];p=(1<<12)-1
    ref=run(24,e,p,[(0,0)],"direct")["counts"]
    for a in ARMS[1:]:
        r=run(24,e,p,[(0,0)],a,trial=1)
        assert r["counts"]==ref and r["stats"]["fallback_queries"]==1 and r["stats"]["abandoned_work"]==1
        assert run(24,e,p,[(0,0)],a,cap=1,trial=1)["counts"]==[None]
    good=encode({0:2,4:1},"ctx");assert decode(good,"ctx",12,3)=={0:2,4:1}
    bad=json.loads(good);bad["digest"]="0"
    tests=[(canonical(bad),"ctx"),(good,"wrong"),(encode({1:1},"ctx"),"ctx"),(encode({0:0},"ctx"),"ctx"),(encode({0:4,4:4},"ctx"),"ctx")]
    for raw,ctx in tests:
        try:decode(raw,ctx,12,3)
        except ValueError:pass
        else:raise AssertionError("invalid artifact accepted")
    return dict(conditioned_checks=checks,width_fallback=True,trial_fallback=True,cap_failure=True,rejected_artifacts=len(tests))
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=[x for x in prior_cohort() if x[1] in (0,1,4,5,6,7)]
    assert len(data)==24
    stats={a:Counter() for a in ARMS};records=[];allrefs=0;fullbatches=0;paired=Counter();both=Counter();both_verified=Counter();mismatched_serial=0
    for j,(n,f,e,g) in enumerate(data):
        adj=core.make_graph(n,e);order=tr.discover(adj,n,Counter());prefix=sum(1<<v for v in order[:n//2])
        qs=queries(order[n//2:]);ref=references(n,f,e,g,qs);full=all(v is not None for v in ref)
        seen=[set() for _ in qs];labels_done={a:[] for a in ARMS}
        for label in range(2):
            perm=list(range(n))
            if label:random.Random(20270154+j).shuffle(perm)
            def pm(m):return sum(1<<perm[v] for v in bits(m))
            ee=tuple(sorted(tuple(sorted((perm[u],perm[v]))) for u,v in e));pp=pm(prefix);qq=[(pm(i),pm(x)) for i,x in qs]
            rs={a:[] for a in ARMS}
            for k in range(3):
                order_a=list(ARMS);random.Random(20270155+6*j+3*label+k).shuffle(order_a)
                for a in order_a:rs[a].append(run(n,ee,pp,qq,a))
            allrefs+=sum(v is not None for v in ref);fullbatches+=int(full)
            med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
            done={a:[sum(r["counts"][i] is not None for r in rr)>=2 for i in range(len(qs))] for a,rr in rs.items()}
            mismatched_serial+=sum(x!=y for x,y in zip(done["reuse"],done["serialized"]))
            for a,rr in rs.items():
                labels_done[a].append(done[a])
                for r in rr:
                    for i,v in enumerate(r["counts"]):
                        if v is not None:
                            seen[i].add(v);assert len(seen[i])==1
                            assert ref[i] is None or ref[i]==v
                s=stats[a];s["verified"]+=sum(d and v is not None for d,v in zip(done[a],ref))
                s["unverified"]+=sum(d and v is None for d,v in zip(done[a],ref));s["unresolved"]+=sum(not d for d in done[a])
                for key in ("reward","cpu","wall"):s[key]+=med[a][key]
                if full:s["verified_reward"]+=med[a]["reward"]
                for key in ("work","prefix_work","prefix_states","peak","width_fallback","prefix_fallback","fallback_queries","dp_answers","reused_queries","failed_trials","abandoned_work","direct_work","dp_query_work","serialized_bytes","serialization_cpu"):s[key]+=rr[0]["stats"].get(key,0)
                if full and all(all(x) for x in done.values()):paired[a]+=med[a]["reward"]
            paired["batches"]+=int(full and all(all(x) for x in done.values()))
            records.append(dict(n=n,family=f,label=label,edges=ee,prefix=pp,queries=qq,reference=ref,results=rs,med=med,done=done))
            print("THYB_CASE",n,f,label,full,{a:[sum(done[a]),round(med[a]["reward"],6),rs[a][0]["stats"].get("fallback_queries",0)] for a in ARMS},flush=True)
        for a,ds in labels_done.items():
            both[a]+=sum(x and y for x,y in zip(*ds))
            both_verified[a]+=sum(x and y and v is not None for x,y,v in zip(*ds,ref))
    s=stats["reuse"];controls=("direct","fresh")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    primary=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls)
    se=stats["serialized"]
    secondary=mismatched_serial==0 and se["verified"]==s["verified"] and se["unverified"]==s["unverified"] and se["verified_reward"]<=1.1*s["verified_reward"] and se["reused_queries"]>0
    result=dict(stats=stats,reference_queries=allrefs,full_reference_batches=fullbatches,paired=paired,both_labels=both,both_labels_verified=both_verified,serialization_coverage_differences=mismatched_serial,gains=gains,primary_pass=primary,secondary_pass=secondary,selftests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print("THYB_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
