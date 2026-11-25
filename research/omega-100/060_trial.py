import importlib
import json
from statistics import median
from time import perf_counter_ns

prior = importlib.import_module("057_trial")


class Session:
    def __init__(self, enabled):
        self.enabled = enabled
        self.slots = []
        self.scans = 0

    def table(self, wire):
        if self.enabled:
            for i, (key, value) in enumerate(self.slots):
                if wire == key:
                    if i:
                        self.slots.reverse()
                    return value
        self.scans += 1
        try:
            parsed = json.loads(wire)
        except (json.JSONDecodeError, TypeError):
            return None
        table = tuple(parsed) if type(parsed) is list else None
        if not prior.table_valid(table):
            return None
        if self.enabled and len(wire) <= 4096:
            self.slots.insert(0,(wire,table))
            del self.slots[2:]
        return table

    def run(self, table_wire, query_wire):
        table = self.table(table_wire)
        try:
            start, steps, offline = json.loads(query_wire)
        except (ValueError, TypeError):
            return "invalid", None
        if (table is None or type(start) is not int or not 0 <= start < len(table)
                or type(steps) is not int or not 0 <= steps <= 100 or type(offline) is not bool):
            return "invalid", None
        if offline:
            return "unavailable", None
        return "exact", prior.engine.direct(table,start,steps)


def adverse():
    s=Session(True)
    cases=(("[1,0]","[0,1,false]",("exact",1)),("[true,0]","[0,1,false]",("invalid",None)),
           ("[1,]","[0,1,false]",("invalid",None)),("[1,0]","{",("invalid",None)),
           ("[1,0]","[0,1,true]",("unavailable",None)),("[1, 0]","[0,1,false]",("exact",1)),
           (" "*4096+"[1,0]","[0,1,false]",("exact",1)),("[1,0]","[0,1,false]",("exact",1)))
    for table, query, expected in cases:
        assert s.run(table,query)==expected
    assert {key for key,_ in s.slots} == {"[1,0]","[1, 0]"}
    assert Session(True).run("[1,0]","[0,1,false]")==("exact",1)


def measure(n, varied):
    tables=tuple(tuple((i+offset)%n for i in range(n)) for offset in (9,13))
    raw=[json.dumps(t,separators=(",",":")) for t in tables]
    requests=[]; expected=[]
    for i in range(384):
        k=i%2
        start,steps,offline=i%n,i%17,i%73==0
        wire=(" "*(i+1) if varied else " ")+raw[k]
        if not varied:
            wire=wire[1:]
        requests.append((wire,json.dumps((start,steps,offline))))
        expected.append(("unavailable",None) if offline else ("exact",prior.engine.binary(tables[k],start,steps)))
    times=[[],[]]
    errors=[0,0]
    scans=[0,0]
    for rep in range(7):
        for arm in ((0,1) if rep%2==0 else (1,0)):
            start=perf_counter_ns()
            pilot=Session(bool(arm))
            out=[pilot.run(*request) for request in requests]
            times[arm].append(perf_counter_ns()-start)
            errors[arm]+=sum(a!=b for a,b in zip(out,expected,strict=True))
            scans[arm]=pilot.scans
    return dict(ns=[median(t) for t in times],errors=errors,scans=scans)


def main():
    tick=perf_counter_ns()
    adverse()
    results={n:{p:measure(n,p=="varied") for p in ("canonical","varied")} for n in (89,191)}
    print(json.dumps(dict(results=results,elapsed_ns=perf_counter_ns()-tick),indent=2))


if __name__=="__main__":
    main()
