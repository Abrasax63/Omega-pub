"""TRANSFER01: discovered boundary relations, exact blocked-state quotient."""
import itertools as it,json,random,signal,statistics,time
from collections import Counter,defaultdict
from pathlib import Path
import resource_learn01 as old
import reorg01 as reorg
import arch_gate01 as gate
import separator_value01 as sep
from arch_switch01 import core,bits,Limit,alarm
ARMS=("explicit","compact","hybrid","elimination","partition","direct")
CAP=8192
CPU=.8
def prior_cohort():
    rng=random.Random(20270145)
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
def old_cohort():
    yield from prior_cohort()
    rng=random.Random(20270146)
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

def cohort():
    yield from old_cohort()
    rng=random.Random(20270147)
    for n in (40,72):
        for f in range(10,14):
            w={10:5,11:9,12:4,13:3}[f]
            groups=[list(range(i,min(n,i+w))) for i in range(0,n,w)]
            e=[]
            for g in groups:
                e+=list(it.combinations(g,2)) if f==12 else list(zip(g,g[1:]))
            links=[((i-1)//2,i) for i in range(1,len(groups))] if f==12 else [(i,i+1) for i in range(len(groups)-1)]
            if f==13:links.append((len(groups)-1,0))
            for i,j in links:
                a,b=groups[i],groups[j]
                if f in (10,11):e+=list(zip(a,b))
                else:e.append((rng.choice(a),rng.choice(b)))
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[[labels[v] for v in g] for g in groups]
def order_width(adj,order):
    rem=sum(1<<v for v in order);live=0;width=0
    for v in order:
        rem^=1<<v;live|=1<<v
        live=sum(1<<u for u in bits(live) if adj[u]&rem)
        width=max(width,live.bit_count())
    return width
def discover(adj,n,stats):
    result=[]
    for m in sep.components(adj,(1<<n)-1):
        v=min(bits(m),key=lambda u:((adj[u]&m).bit_count(),u))
        ls=sep.layers(adj,m,v);u=min(bits(ls[-1]))
        candidates=[tuple(x for row in ls for x in bits(row)),tuple(x for row in sep.layers(adj,m,u) for x in bits(row))]
        stats["order_candidates"]+=2
        result.extend(min(candidates,key=lambda x:(order_width(adj,x),x)))
    assert sorted(result)==list(range(n))
    stats["width"]=order_width(adj,result)
    return result
def boundary(adj,order,compact,stats,cap=CAP,stop=None):
    states={0:1};rem=sum(1<<v for v in order);live=0
    for v in order[:stop]:
        b=1<<v;rem^=b
        if not compact:
            live|=b;live=sum(1<<u for u in bits(live) if adj[u]&rem)
        nxt=defaultdict(int)
        for s,w in states.items():
            if stats["work"]>=cap:raise Limit
            stats["work"]+=1
            if compact:
                t=s&rem;allowed=not s&b
                selected=t|(adj[v]&rem)
            else:
                t=s&live;allowed=not adj[v]&s
                selected=t|(b&live)
            if t in nxt:stats["merges"]+=1
            nxt[t]+=w;stats["transitions"]+=1
            if allowed:
                if selected in nxt:stats["merges"]+=1
                nxt[selected]+=w;stats["transitions"]+=1
        states=nxt;stats["peak_states"]=max(stats["peak_states"],len(states))
    return states
def minfill(adj,n,stats,cap):
    rem=(1<<n)-1;work=list(adj);order=[];rows=0
    while rem:
        def key(v):
            ns=work[v]&rem
            missing=sum((ns&~work[u]&~(1<<u)).bit_count() for u in bits(ns))//2
            return missing,ns.bit_count(),v
        v=min(bits(rem),key=key);ns=work[v]&rem;w=ns.bit_count()
        stats["width"]=max(stats["width"],w)
        rows+=1<<w
        if w>12 or rows>cap:return None
        order.append(v);rem^=1<<v
        for u in bits(ns):work[u]=(work[u]|(ns&~(1<<u)))&~(1<<v)
    stats["planned_rows"]=rows
    return order
def eliminate(n,e,order,stats,cap):
    factors=[((v,),(1,1)) for v in range(n)]+[((a,b),(1,1,1,0)) for a,b in e]
    scalar=1
    for v in order:
        bucket=[(s,t) for s,t in factors if v in s]
        factors=[(s,t) for s,t in factors if v not in s]
        scope=tuple(sorted({u for s,t in bucket for u in s if u!=v}));pos={u:i for i,u in enumerate(scope)}
        # For each factor precompute the bit projection of the new scope.
        maps=[(tuple((pos[u],j) for j,u in enumerate(s) if u!=v),1<<s.index(v),t) for s,t in bucket]
        table=[]
        for k in range(1<<len(scope)):
            if stats["work"]>=cap:raise Limit
            stats["work"]+=1;p0=p1=1
            for proj,bit,t in maps:
                idx=sum(((k>>i)&1)<<j for i,j in proj)
                p0*=t[idx];p1*=t[idx|bit];stats["factor_lookups"]+=2
            table.append(p0+p1)
        if scope:factors.append((scope,tuple(table)))
        else:scalar*=table[0]
    assert not factors
    return scalar
def run(n,e,arm,cap=CAP):
    if arm in ("partition","direct"):return reorg.run(n,e,arm,cap=cap)
    start=time.process_time();wall=time.perf_counter();stats=Counter();value=None;fallback=False
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        adj=core.make_graph(n,e)
        if arm=="elimination":
            order=minfill(adj,n,stats,cap)
            if order is None:fallback=True
            else:value=eliminate(n,e,order,stats,cap)
        else:
            order=discover(adj,n,stats)
            if arm=="hybrid" and stats["width"]>12:fallback=True
            else:value=sum(boundary(adj,order,arm!="explicit",stats,cap).values())
    except Limit:value=None;fallback=False
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    if fallback:
        stats["fallback"]=1
        left=CPU-(time.process_time()-start)
        if left>0:
            r=old.solve(n,e,(4,8,512),cap,left);value=r["count"]
            stats["fallback_visits"]=r["stats"].get("visits",0)
    sec=time.process_time()-start;t=time.perf_counter()-wall
    if sec>CPU:value=None
    assert stats["work"]+stats["fallback_visits"]<=cap
    return dict(count=value,cpu=sec,wall=t,reward=t+.25*sec+(value is None),stats=dict(stats))
def block_reference(n,e,g,cycle):
    idx={v:i for i,row in enumerate(g) for v in row}
    assert sorted(idx)==list(range(n))
    states=[]
    for row in g:
        es=[(a,b) for a,b in e if a in row and b in row]
        states.append([frozenset(v for j,v in enumerate(row) if k>>j&1) for k in range(1<<len(row)) if not any(k>>row.index(a)&1 and k>>row.index(b)&1 for a,b in es)])
    links=defaultdict(list)
    for a,b in e:
        i,j=idx[a],idx[b]
        if i!=j:links[i,j].append((a,b));links[j,i].append((b,a))
    def ok(i,j,a,b):return not any(u in a and v in b for u,v in links[i,j])
    if cycle:
        assert all((i-j)%len(g) in (1,len(g)-1) for i,j in links)
        total=0
        for first in states[0]:
            prev={first:1}
            for i in range(1,len(g)):
                prev={s:sum(v for p,v in prev.items() if ok(i-1,i,p,s)) for s in states[i]}
            total+=sum(v for s,v in prev.items() if ok(len(g)-1,0,s,first))
        return total
    neighbors={i:[j for j in range(len(g)) if (i,j) in links] for i in range(len(g))}
    assert sum(map(len,neighbors.values()))==2*(len(g)-1)
    seen=set()
    def rec(i,p):
        assert i not in seen;seen.add(i);rows=[(j,rec(j,i)) for j in neighbors[i] if j!=p]
        out={}
        for s in states[i]:
            val=1
            for j,table in rows:val*=sum(v for t,v in table.items() if ok(i,j,s,t))
            out[s]=val
        return out
    ans=sum(rec(0,-1).values());assert len(seen)==len(g)
    return ans
def reference(n,f,e,g):
    if f<10:return sep.reference(n,f,e,g)
    if f in (10,11):return sep.transfer(n,e,g),"WIDE_TRANSFER"
    return block_reference(n,e,g,f==13),("CYCLE_TRANSFER" if f==13 else "TREE_BLOCK_DP")
def selftests():
    checks=0;queries=0;quotient=0
    for n in range(5):
        pairs=list(it.combinations(range(n),2))
        for k in range(1<<len(pairs)):
            e=[p for j,p in enumerate(pairs) if k>>j&1];adj=core.make_graph(n,e);m=(1<<n)-1
            ref=sep.brute(n,e,m)
            for a in ARMS:
                assert run(n,e,a)["count"]==ref;checks+=1
            order=discover(adj,n,Counter());p=n//2
            explicit=boundary(adj,order,False,Counter(),stop=p)
            compact=boundary(adj,order,True,Counter(),stop=p)
            rem=sum(1<<v for v in order[p:]);prefix=m^rem;projection=Counter()
            for s,w in explicit.items():
                blocked=0
                for v in bits(s):blocked|=adj[v]&rem
                projection[blocked]+=w
            assert dict(projection)==compact
            quotient+=int(len(explicit)>len(compact))
            for q in range(1<<n):
                if q&~rem:continue
                expected=sum(1 for b in range(1<<n) if not b&~prefix and not any((b|q)>>u&1 and (b|q)>>v&1 for u,v in e) ) if not any(q>>u&1 and q>>v&1 for u,v in e) else None
                if expected is not None:
                    assert sum(w for s,w in compact.items() if not s&q)==expected;queries+=1
    assert quotient>0
    e=[(i,i+1) for i in range(19)]
    assert run(20,e,"compact",cap=1)["count"] is None
    e=list(it.combinations(range(16),2))
    for a in ("hybrid","elimination"):
        r=run(16,e,a);assert r["count"]==17 and r["stats"]["fallback"]==1
    return dict(exhaustive=checks,conditional_queries=queries,quotient_fixtures=quotient,cap_failure=True,width_fallback=True)
def main(out):
    signal.signal(signal.SIGPROF,alarm);tests=selftests();data=list(cohort())
    assert len(data)==48 and len({(n,e) for n,f,e,g in data})==48
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];paired=Counter();oracle=Counter();families={str(f):{a:Counter() for a in ARMS} for f in range(14)}
    for j,(n,f,e,g) in enumerate(data):
        ref,kind=reference(n,f,e,g);refs[kind]+=1;rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20270148+3*j+k).shuffle(order)
            for a in order:rs[a].append(run(n,e,a))
        gate.audit(rs,ref)
        med={a:{k:statistics.median(r[k] for r in rr) for k in ("reward","cpu","wall")} for a,rr in rs.items()}
        done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
        for a in ARMS:
            r=rs[a][0]["stats"]
            for s in (stats[a],families[str(f)][a]):
                s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a])
                for k in ("reward","cpu","wall"):s[k]+=med[a][k]
                if ref is not None:s["verified_reward"]+=med[a]["reward"]
                for k in ("work","visits","merges","transitions","fallback","fallback_visits","factor_lookups","order_candidates"):s[k]+=r.get(k,0)
                for k in ("width","peak_states"):s["max_"+k]=max(s["max_"+k],r.get(k,0))
                if ref is not None and done[a] and not r.get("fallback"):s["verified_no_fallback"]+=1
            if ref is not None and all(done.values()):paired[a]+=med[a]["reward"]
        paired["cases"]+=int(ref is not None and all(done.values()))
        for key,arms in (("fixed",("direct","partition","elimination")),("all",ARMS)):
            b=min(arms,key=lambda a:med[a]["reward"]);oracle[key+"_all"]+=med[b]["reward"]
            if ref is not None:oracle[key+"_verified"]+=med[b]["reward"]
        records.append(dict(n=n,family=f,edges=e,groups=g,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
        print("TRANSFER_CASE",n,f,kind,{a:[done[a],round(med[a]["reward"],6),rs[a][0]["stats"].get("fallback",0)] for a in ARMS},flush=True)
    s=stats["hybrid"];controls=("direct","partition","elimination")
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in controls}
    passed=all(s["verified"]>=stats[a]["verified"] and (s["unverified"]<=stats[a]["unverified"] or s["verified"]>stats[a]["verified"]) and gains[a]>=.15 and s["reward"]<=stats[a]["reward"] for a in controls)
    compact_gain=1-stats["compact"]["verified_reward"]/stats["explicit"]["verified_reward"]
    secondary=compact_gain>=.15 and stats["compact"]["verified"]>=stats["explicit"]["verified"] and tests["quotient_fixtures"]>0
    novel=sum(r["reference"] is not None and r["done"]["hybrid"] and not any(r["done"][a] for a in controls) for r in records)
    result=dict(stats=stats,references=refs,paired=paired,gains=gains,compact_gain=compact_gain,oracle=oracle,novel_verified_recoveries=novel,primary_pass=passed,secondary_pass=secondary,selftests=tests,families=families,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("TRANSFER_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("records","families")}),flush=True)
    print("TRANSFER_FAMILIES",json.dumps({f:{a:{k:s[k] for k in ("verified","unverified","unresolved","verified_reward","reward","fallback")} for a,s in x.items()} for f,x in families.items()}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
