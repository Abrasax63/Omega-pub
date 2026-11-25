import importlib
import json
from statistics import median
from time import perf_counter_ns

two = importlib.import_module("058_trial")
prior = two.prior
ARMS = (lambda: prior.Pilot(False), lambda: prior.Pilot(True), two.TwoSlots)


def transport(pilot, wire):
    try:
        data = json.loads(wire)
    except json.JSONDecodeError:
        return [("invalid", None)]
    tables = tuple(tuple(source) for source in data["tables"])
    return [pilot.solve(tables[i], start, steps, fault)
            for i, start, steps, fault in data["queries"]]


def encode(tables, queries):
    return json.dumps(dict(tables=tables, queries=queries), separators=(",", ":"))


def controls():
    a, b = prior.tables(7)
    invalid = (True, *a[1:])
    one = encode([a, a, invalid, b], [(0,0,2,False),(1,0,2,False),(2,0,2,False),
                                     (1,0,2,True),(3,0,2,False)])
    assert transport(two.TwoSlots(), "{") == [("invalid", None)]
    p = two.TwoSlots()
    assert transport(p, one) == [("exact",2),("exact",2),("invalid",None),("unavailable",None),("exact",4)]
    assert p.scans == 4


def fixture(n, batch):
    maps = tuple(tuple((i+k)%n for i in range(n)) for k in (5,11))
    rows = [(i%2, i%n, (i*3)%19, i%83==0) for i in range(512)]
    if batch:
        wire = [encode(maps, rows[k:k+128]) for k in range(0,512,128)]
    else:
        wire = [encode([maps[i]], [(0,s,h,f)]) for i,s,h,f in rows]
    truth = [("unavailable",None) if f else ("exact",prior.engine.binary(maps[i],s,h)) for i,s,h,f in rows]
    return wire,truth


def measure(n, batch):
    wire, truth = fixture(n,batch)
    samples = [[],[],[]]
    for rep in range(7):
        for i in ((0,1,2) if rep%2==0 else (2,1,0)):
            start=perf_counter_ns()
            pilot=ARMS[i]()
            out=[v for text in wire for v in transport(pilot,text)]
            ns=perf_counter_ns()-start
            errors=sum(a!=b for a,b in zip(out,truth,strict=True))
            samples[i].append((ns,errors,pilot.scans))
    return dict(ns=[median(r[0] for r in arm) for arm in samples],
                errors=[max(r[1] for r in arm) for arm in samples],
                scans=[arm[0][2] for arm in samples])


def main():
    start=perf_counter_ns()
    controls()
    results={n:{k:measure(n,k=="batch") for k in ("messages","batch")} for n in (73,173)}
    print(json.dumps(dict(results=results,elapsed_ns=perf_counter_ns()-start),indent=2))


if __name__=="__main__":
    main()
