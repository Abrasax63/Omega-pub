import importlib
import json
from statistics import median
from time import perf_counter_ns

engine = importlib.import_module("051_trial")


def table_valid(mapping):
    return type(mapping) is tuple and bool(mapping) and all(
        type(v) is int and 0 <= v < len(mapping) for v in mapping
    )


class Pilot:
    def __init__(self, reuse):
        self.reuse = reuse
        self.last = None
        self.valid = False
        self.scans = 0

    def solve(self, mapping, start, steps, fault):
        if not self.reuse or mapping is not self.last:
            self.scans += 1
            self.last = mapping
            self.valid = table_valid(mapping)
        if not self.valid or type(start) is not int or not 0 <= start < len(mapping):
            return "invalid", None
        if type(steps) is not int or not 0 <= steps <= 100:
            return "invalid", None
        if fault:
            return "unavailable", None
        return "exact", engine.direct(mapping,start,steps)


def tables(n):
    return tuple((i+1)%n for i in range(n)), tuple((i+2)%n for i in range(n))


def control():
    a,b = tables(13)
    invalid=(True,*a[1:])
    assert invalid == a
    rows=[(invalid,0,2,False),(a,0,2,False),(invalid,0,2,False),(b,0,2,False),
          (list(a),0,2,False),((),0,2,False),(b,13,2,False),(b,0,101,False),
          (b,0,0,True),(b,0,0,False)]
    expected=[("invalid",None),("exact",2),("invalid",None),("exact",4),
              *[("invalid",None)]*4,("unavailable",None),("exact",0)]
    for reuse in (False,True):
        p=Pilot(reuse)
        assert [p.solve(*r) for r in rows] == expected


def measure(n,cycle):
    a,b=tables(n)
    rows=[((a,b)[i//cycle%2], i%n, 75+i%20, i%61==0) for i in range(512)]
    truth=[("unavailable",None) if fault else ("exact",engine.binary(m,s,k))
           for m,s,k,fault in rows]
    times=[[],[]]
    errors=[0,0]
    scans=[0,0]
    for rep in range(7):
        for i in ((0,1) if rep%2==0 else (1,0)):
            start=perf_counter_ns()
            runner=Pilot(bool(i))
            results=[runner.solve(*r) for r in rows]
            times[i].append(perf_counter_ns()-start)
            errors[i]+=sum(a!=b for a,b in zip(results,truth,strict=True))
            scans[i]=runner.scans
    return dict(ns=[median(t) for t in times],errors=errors,scans=scans)


def main():
    start=perf_counter_ns()
    control()
    results={n:{b:measure(n,w) for b,w in (("stable",512),("blocks",128),("alternating",1))}
             for n in (47,61)}
    print(json.dumps(dict(results=results,adverse_cases=10,elapsed_ns=perf_counter_ns()-start),indent=2))


if __name__=="__main__":
    main()
