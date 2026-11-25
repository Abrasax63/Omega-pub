import importlib
import json
from statistics import median
from time import perf_counter_ns

prior = importlib.import_module("057_trial")


class TwoSlots:
    def __init__(self):
        self.recent = self.other = None
        self.scans = 0

    def solve(self,mapping,start,steps,fault):
        if mapping is not self.recent or self.recent is None:
            if mapping is self.other and self.other is not None:
                self.recent,self.other = self.other,self.recent
            else:
                self.scans += 1
                if not prior.table_valid(mapping):
                    return "invalid",None
                self.other,self.recent = self.recent,mapping
        if type(start) is not int or not 0 <= start < len(mapping):
            return "invalid",None
        if type(steps) is not int or not 0 <= steps <= 100:
            return "invalid",None
        if fault:
            return "unavailable",None
        return "exact",prior.engine.direct(mapping,start,steps)


def controls():
    a,b=prior.tables(11)
    c=tuple(list(a))
    invalid=(True,*a[1:])
    assert c==a and c is not a and invalid==a
    pilot=TwoSlots()
    rows=((a,0,2,False),(b,0,2,False),(a,0,2,True),(invalid,0,2,False),
          (c,0,2,False),(b,0,2,False),(b,False,2,False),(b,0,2,False))
    expected=[("exact",2),("exact",4),("unavailable",None),("invalid",None),
              ("exact",2),("exact",4),("invalid",None),("exact",4)]
    assert [pilot.solve(*r) for r in rows] == expected
    assert pilot.scans==5


def compare(n,arity):
    maps=tuple(tuple((v+k)%n for v in range(n)) for k in (3,4,7))
    rows=[(maps[i%arity],i%n,(i*7)%18,i%67==0) for i in range(600)]
    oracle=[("unavailable",None) if f else ("exact",prior.engine.binary(m,x,k)) for m,x,k,f in rows]
    methods=(lambda:prior.Pilot(False),lambda:prior.Pilot(True),TwoSlots)
    out=[[],[],[]]
    for repeat in range(7):
        for arm in ((0,1,2) if repeat%2==0 else (2,1,0)):
            start=perf_counter_ns()
            pilot=methods[arm]()
            result=[pilot.solve(*r) for r in rows]
            duration=perf_counter_ns()-start
            errors=sum(a!=b for a,b in zip(result,oracle,strict=True))
            out[arm].append((duration,errors,pilot.scans))
    return dict(ns=[median(r[0] for r in a) for a in out],
                errors=[max(r[1] for r in a) for a in out],
                scans=[a[0][2] for a in out])


def main():
    tick=perf_counter_ns()
    controls()
    results={n:{arity:compare(n,arity) for arity in (1,2,3)} for n in (29,109)}
    assert all(rows[2]["scans"][-1]==2 for rows in results.values())
    print(json.dumps(dict(results=results,elapsed_ns=perf_counter_ns()-tick),indent=2))


if __name__=="__main__":
    main()
