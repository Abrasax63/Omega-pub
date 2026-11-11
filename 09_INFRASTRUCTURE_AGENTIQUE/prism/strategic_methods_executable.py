"""Executable four-method, four-domain STRAT-002 lab.

No LLM or live retrieval in replay. RFC and Python documentation are manually
audited normative snapshots; outages are explicitly simulated.
"""
from collections import Counter
from fractions import Fraction

METHODS=("formal","compute","refute","source")
RFC={301:True,302:True,307:False,308:False}
RFC_URL={301:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2",
         302:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.3",
         307:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.8",
         308:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.9"}

def tasks():
    configs={
      "math":[("mod",{"a":6,"b":3,"m":3}),
              ("euler",{"edges":[[0,1],[1,2],[2,3],[3,0]]}),
              ("mod",{"a":4,"b":1,"m":2}),
              ("euler",{"edges":[[0,1],[1,2]]}),
              ("mod",{"a":8,"b":2,"m":2}),
              ("euler",{"edges":[[0,1],[1,2],[2,0]]}),
              ("mod",{"a":7,"b":2,"m":3}),
              ("euler",{"edges":[[0,1],[1,2],[2,3]]})],
      "programming":[("map",{"mapping":[1,2,3,0]}),
                     ("zip",{"left":[1],"right":[2,3]}),
                     ("map",{"mapping":[1,1,2,3]}),
                     ("zip",{"left":[1,2],"right":[3,4]}),
                     ("map",{"mapping":[0,2,1,3]}),
                     ("zip",{"left":[1,2,3],"right":[4]}),
                     ("map",{"mapping":[0,1,1,3]}),
                     ("zip",{"left":[1,2],"right":[0,9]})],
      "data":[("ratio",{"a":[3,4],"b":[2,4]}),
              ("simpson",{"a":[[9,10],[10,100]],"b":[[80,100],[0,10]]}),
              ("ratio",{"a":[1,4],"b":[3,4]}),
              ("simpson",{"a":[[9,10],[9,10]],"b":[[8,10],[8,10]]}),
              ("ratio",{"a":[7,9],"b":[4,9]}),
              ("simpson",{"a":[[8,10],[1,80]],"b":[[60,100],[0,10]]}),
              ("ratio",{"a":[2,9],"b":[6,9]}),
              ("simpson",{"a":[[6,10],[8,10]],"b":[[3,10],[5,10]]})],
      "documentation":[("rfc",{"status":301}),("rfc",{"status":308}),
                       ("rfc",{"status":302}),("rfc",{"status":307}),
                       ("rfc",{"status":302}),("rfc",{"status":307}),
                       ("rfc",{"status":301}),("rfc",{"status":308})],
    }
    failures={"math":{1:"formal",5:"formal"},
              "programming":{1:"compute",5:"compute"},
              "data":{0:"compute",5:"formal"},
              "documentation":{1:"source",4:"source"}}
    out=[]
    for domain,values in configs.items():
        for i,(kind,params) in enumerate(values):
            out.append({"id":("S" if domain=="documentation" else domain[0].upper())+str(i),
                        "domain":domain,"kind":kind,"params":params,
                        "partition":"train" if i<4 else "test",
                        "simulated_outage":failures[domain].get(i)})
    assert len(out)==len({x["id"] for x in out})==32
    return out

def _euler_theorem(edges):
    deg=Counter(v for edge in edges for v in edge)
    if not deg or any(x%2 for x in deg.values()): return False
    adj={v:set() for v in deg}
    for a,b in edges: adj[a].add(b);adj[b].add(a)
    seen={next(iter(deg))};todo=list(seen)
    while todo:
        for z in adj[todo.pop()]-seen:seen.add(z);todo.append(z)
    return len(seen)==len(deg)

def _euler_dfs(edges):
    if not edges:return False
    for start in set(v for edge in edges for v in edge):
        stack=[(start,frozenset())]
        while stack:
            v,used=stack.pop()
            if len(used)==len(edges) and v==start:return True
            for i,(a,b) in enumerate(edges):
                if i in used:continue
                if v==a:stack.append((b,used|{i}))
                if v==b:stack.append((a,used|{i}))
    return False

def _rates(t):
    p=t["params"]
    if t["kind"]=="ratio":return Fraction(*p["a"])>Fraction(*p["b"])
    a,b=p["a"],p["b"]
    within=all(Fraction(*a[i])>Fraction(*b[i]) for i in range(2))
    pooled=Fraction(sum(x[0] for x in a),sum(x[1] for x in a)) < Fraction(sum(x[0] for x in b),sum(x[1] for x in b))
    return within and pooled

def oracle(t):
    k,p=t["kind"],t["params"]
    if k=="mod":return p["a"]%p["m"]==0 and p["b"]%p["m"]==0
    if k=="euler":return _euler_dfs(p["edges"])
    if k=="map":
        v=p["mapping"]
        return all(v[i]!=v[j] for i in range(len(v)) for j in range(i+1,len(v)))
    if k=="zip":return len(p["left"])!=len(p["right"])
    if k in ("ratio","simpson"):return _rates(t)
    if k=="rfc":return RFC[p["status"]]
    raise ValueError(k)

def formal(t):
    k,p=t["kind"],t["params"]
    if k=="mod":return (p["a"]%p["m"]==0 and p["b"]%p["m"]==0),"divisibility of coefficient and constant"
    if k=="euler":return _euler_theorem(p["edges"]),"Euler criterion of degree and connectivity"
    if k=="map":
        v=p["mapping"]
        return all(v[i]!=v[j] for i in range(len(v)) for j in range(i+1,len(v))),"all distinct image pairs"
    if k=="ratio":
        a,b=p["a"],p["b"];return a[0]*b[1]>b[0]*a[1],"integer cross product"
    if k=="simpson":
        a,b=p["a"],p["b"]
        within=all(a[i][0]*b[i][1]>b[i][0]*a[i][1] for i in range(2))
        pooled=sum(x[0] for x in a)*sum(x[1] for x in b)<sum(x[0] for x in b)*sum(x[1] for x in a)
        return within and pooled,"exact integer rate inequalities"
    return None,"formal method not applicable"

def compute(t):
    k,p=t["kind"],t["params"]
    if k=="mod":
        for i in range(-8,9):
            if (p["a"]*i+p["b"])%p["m"]:return False,"counterexample k=%d"%i
        return None,"finite search cannot prove universal positive"
    if k=="euler":
        return (True,"constructive circuit witness") if _euler_dfs(p["edges"]) else (None,"no constructive witness")
    if k=="map":return len(set(p["mapping"]))==len(p["mapping"]),"exact image cardinality"
    if k=="zip":
        try:list(zip(p["left"],p["right"],strict=True))
        except ValueError:return True,"Python runtime raised ValueError"
        return False,"Python runtime did not raise"
    if k in ("ratio","simpson"):return _rates(t),"Fraction exact arithmetic"
    return None,"runtime cannot certify normative source"

def refute(t):
    k,p=t["kind"],t["params"]
    if k=="mod":
        for i in range(-8,9):
            if (p["a"]*i+p["b"])%p["m"]:return False,"modular witness k=%d"%i
        return None,"no bounded witness; truth not certified"
    if k=="euler":
        deg=Counter(v for edge in p["edges"] for v in edge)
        for v,n in deg.items():
            if n%2:return False,"odd-degree vertex %d"%v
        return None,"no obstruction found"
    if k=="map":
        seen={}
        for i,v in enumerate(p["mapping"]):
            if v in seen:return False,"collision %d and %d"%(seen[v],i)
            seen[v]=i
        return None,"no collision is not a refutation"
    if k in ("ratio","simpson"):
        return (None,"no contradiction found") if _rates(t) else (False,"exact violated inequality")
    return None,"no refutation method for this claim"

def source(t):
    k,p=t["kind"],t["params"]
    if k=="rfc":return RFC[p["status"]],RFC_URL[p["status"]]
    if k=="zip":return len(p["left"])!=len(p["right"]),"https://docs.python.org/3/library/functions.html#zip"
    return None,"no eligible primary source for claim"

EXECUTORS={"formal":formal,"compute":compute,"refute":refute,"source":source}

def run_method(task,method):
    if method not in METHODS:raise ValueError(method)
    if task["simulated_outage"]==method:
        return {"observation":"unknown","certificate":"synthetic method outage"}
    result,cert=EXECUTORS[method](task)
    return {"observation":"unknown" if result is None else ("yes" if result else "no"),
            "certificate":cert}
