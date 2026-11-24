"""Property-scoped exact reduction selector. No learned invariance claims."""
import hashlib
import itertools as it
import json
import time
from collections import Counter
from pathlib import Path
from libstruct01.symmetry_audit import signature
from libstruct01.rule90_audit import direct, reduced

SOURCE="38f614d6358042c3168f8b60853d9bf712e922de"
REGISTRY={
 "delta_census":("state_color_conjugacy","DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md"),
 "global_triple_census":("vertex_conjugacy","LIBSTRUCT01_RESULTS.md"),
 "ordered_triple_census":("direct","LIBSTRUCT01_RESULTS.md"),
 "rule90_histogram":("causal_cone","BR-R90-02_MAJORITY_WALSH.md"),
}
def choose(task,params,force=None):
    if task not in REGISTRY: raise ValueError("UNKNOWN_TASK")
    if not isinstance(params,dict):raise ValueError("PARAMS")
    if task=="delta_census":
        if set(params)!={"n"} or type(params["n"]) is not int or not 2<=params["n"]<=5:raise ValueError("DOMAIN")
        method="state_color_conjugacy"
    elif task in ("global_triple_census","ordered_triple_census"):
        if set(params)!={"n"} or type(params["n"]) is not int or not 3<=params["n"]<=4:raise ValueError("DOMAIN")
        method=REGISTRY[task][0]
    else:
        if set(params)!={"n","h"} or any(type(params[k]) is not int for k in params) or not 3<=params["n"]<=15 or not 0<=params["h"]<=6:raise ValueError("DOMAIN")
        method="causal_cone" if params["n"]>=2*params["h"]+3 else "direct"
    if force is not None and force!=method and force!="direct":raise ValueError("UNSAFE_REDUCTION")
    return force or method

def delta_domain(n):
    colors=[p for p in it.product((0,1),repeat=n) if 0 in p and 1 in p]
    for t in it.product(range(n),repeat=n):
        for p in colors:yield t,p

def state_orbit(t,p,perms):
    orbit=set();n=len(t)
    for s,inv in perms:
        u=tuple(s[t[inv[j]]] for j in range(n));v=tuple(p[inv[j]] for j in range(n))
        orbit.add((u,v));orbit.add((u,tuple(1-x for x in v)))
    return orbit

def delta_value(t,p):
    ds,exact,ghost=signature(t,p)
    return json.dumps([list(ds),exact,ghost],separators=(",",":"))

def delta(n,method):
    hist=Counter();sizes=Counter();visited=set();evaluations=0;start=time.perf_counter()
    perms=[(s,tuple(s.index(i) for i in range(n))) for s in it.permutations(range(n))]
    for t,p in delta_domain(n):
        if method!="direct":
            if (t,p) in visited:continue
            orb=state_orbit(t,p,perms)
            if visited.intersection(orb):raise AssertionError("OVERLAP")
            visited.update(orb);m=len(orb)
        else:m=1
        hist[delta_value(t,p)]+=m;sizes[m]+=1;evaluations+=1
    total=n**n*(2**n-2)
    assert sum(hist.values())==total and sum(k*v for k,v in sizes.items())==total
    return hist,dict(raw=total,evaluations=evaluations,orbit_sizes=dict(sizes),seconds=time.perf_counter()-start)

def graph(n,method,ordered):
    es=list(it.permutations(range(n),2));index={e:i for i,e in enumerate(es)}
    maps=[tuple(index[s[a],s[b]] for a,b in es) for s in it.permutations(range(n))]
    triples=[(0,1,2)] if ordered else list(it.permutations(range(n),3))
    queries=[(index[a,b],index[b,c],index[a,c]) for a,b,c in triples]
    visited=set();hist=Counter();sizes=Counter();count=0;start=time.perf_counter()
    for mask in range(1<<len(es)):
        if method!="direct":
            if mask in visited:continue
            orbit={sum(1<<v for i,v in enumerate(mapping) if mask>>i&1) for mapping in maps}
            assert not visited.intersection(orbit);visited.update(orbit);m=len(orbit)
        else:m=1
        truth=any((mask>>a&1) and (mask>>b&1) and not(mask>>c&1) for a,b,c in queries)
        hist[str(int(truth))]+=m;sizes[m]+=1;count+=1
    total=1<<len(es)
    assert sum(hist.values())==total
    return hist,dict(raw=total,evaluations=count,orbit_sizes=dict(sizes),seconds=time.perf_counter()-start)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def solve(task,params,force=None):
    method=choose(task,params,force);n=params["n"]
    if task=="delta_census":hist,work=delta(n,method)
    elif task in ("global_triple_census","ordered_triple_census"):
        hist,work=graph(n,method,task=="ordered_triple_census")
    else:
        h=params["h"];start=time.perf_counter();hist=(reduced if method=="causal_cone" else direct)(n,h)
        work=dict(raw=1<<n,evaluations=1<<(2*h+3) if method=="causal_cone" else 1<<n,seconds=time.perf_counter()-start)
    hypotheses={"state_color_conjugacy":"total endofunction, binary surjective observation; invariant counts only",
      "vertex_conjugacy":"loopless directed graph, existential distinct triple, no marked vertices",
      "causal_cone":"uniform initial states, cyclic rule90, local Majority, N>=2h+3",
      "direct":"exact enumeration of declared finite domain"}[method]
    result=dict(task=task,params=params.copy(),method=method,source_commit=SOURCE,source=REGISTRY[task][1],
      hypotheses=hypotheses,histogram={str(k):v for k,v in hist.items()},work=work)
    result["outcome_sha256"]=digest({k:v for k,v in result.items() if k!="work"})
    return result

def independent_delta(n):
    # Different evaluation: explicitly trace all initial states at each horizon;
    # stop on repeated full mapping power and Boolean adjacency bitmask.
    hist=Counter()
    for t,p in delta_domain(n):
        q=sum(1<<k for k in {2*p[i]+p[t[i]] for i in range(n)})
        step=q;v=list(t);seen=set();seq=[]
        while (step,tuple(v)) not in seen:
            seen.add((step,tuple(v)))
            actual=sum(1<<k for k in {2*p[i]+p[v[i]] for i in range(n)})
            seq.append((step&~actual).bit_count())
            step=sum(1<<(2*a+c) for a,c in it.product((0,1),repeat=2)
                 if any(step>>(2*a+b)&1 and q>>(2*b+c)&1 for b in (0,1)))
            v=[t[j] for j in v]
        ghosts=0
        for a,b,c in it.product((0,1),repeat=3):
            if q>>(2*a+b)&1 and q>>(2*b+c)&1 and not any((p[i],p[t[i]],p[t[t[i]]])==(a,b,c) for i in range(n)):ghosts+=1
        hist[json.dumps([seq,not any(seq),ghosts],separators=(",",":"))]+=1
    return hist

def independent_graph(n,ordered):
    es=list(it.permutations(range(n),2));hist=Counter()
    triples=[(0,1,2)] if ordered else list(it.permutations(range(n),3))
    for mask in range(1<<len(es)):
        e={x for i,x in enumerate(es) if mask>>i&1}
        truth=any((a,b) in e and (b,c) in e and (a,c) not in e for a,b,c in triples)
        hist[str(int(truth))]+=1
    return hist

def mutations():
    cases=[("unknown",{},None),("delta_census",{"n":True},None),
           ("delta_census",{"n":6},None),("delta_census",{"n":5,"x":1},None),
           ("ordered_triple_census",{"n":4},"vertex_conjugacy"),
           ("rule90_histogram",{"n":7,"h":3},"causal_cone"),
           ("rule90_histogram",{"n":0,"h":0},None),
           ("global_triple_census",{"n":4},"causal_cone")]
    out=[]
    for t,p,f in cases:
        try:choose(t,p,f);out.append(False)
        except ValueError:out.append(True)
    return out

def main(out):
    tasks=[("delta_census",{"n":5}),("global_triple_census",{"n":4}),("ordered_triple_census",{"n":4})]
    tasks += [("rule90_histogram",{"n":15,"h":h}) for h in range(7)]
    tasks += [("rule90_histogram",{"n":n,"h":3}) for n in range(3,8)]
    records=[]
    for task,params in tasks:
        r=solve(task,params);start=time.perf_counter()
        if task=="delta_census":ref=independent_delta(params["n"])
        elif task.endswith("triple_census"):ref=independent_graph(params["n"],task=="ordered_triple_census")
        else:ref=direct(params["n"],params["h"])
        r["reference_seconds"]=time.perf_counter()-start
        r["match"]=r["histogram"]=={str(k):v for k,v in ref.items()}
        records.append(r)
        print("SELECT",task,params,r["method"],r["work"],"reference",r["reference_seconds"],"match",r["match"],flush=True)
    checks=mutations();passed=all(r["match"] for r in records) and all(checks)
    result=dict(passed=passed,records=records,mutation_checks=checks)
    Path(out).write_text(json.dumps(result,indent=2));assert passed
if __name__=="__main__":
    import sys
    main(sys.argv[1])
