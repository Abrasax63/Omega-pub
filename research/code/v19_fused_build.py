"""Measure a raw duplicate screen folded into the event generator."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter, perf_counter_ns
from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_raw_screen import raw_reject
from v19_signed import prepare, signed


def core(t, forced, events):
    return signed(prepare(len(t), forced), events)


def plain(row):
    t, pair, _, forced = row
    events = event_edges(t, pair, 4)
    return len(events) == 4 and core(t, forced, events)


def separated(row):
    t, pair, _, forced = row
    events = event_edges(t, pair, 4)
    return len(events) == 4 and not raw_reject(events) and core(t, forced, events)


def fused(row):
    t, (a, b), _, forced = row
    events = []
    for _ in range(4):
        if a == b:
            return False
        edge = (a,b,0) if a < b else (b,a,0)
        if edge in events:
            return False
        events.append(edge)
        a, b = t[a], t[b]
    return core(t, forced, events)


def evaluate(base):
    q = len(base)
    rows = []
    maps = 0
    for anchor, leaf in product(range(4), range(q+3)):
        t = (*base, anchor, q, q, leaf)
        f = forced_edges(t)
        if not coherent(len(t), f):
            continue
        maps += 1
        rows.extend((t,pair,tuple(range(4)),f) for pair in combinations(range(len(t)),2))
    traces = [event_edges(row[0],row[1],4) for row in rows]
    truth = [len(e)==4 and bool(certify((*r,e))) for r,e in zip(rows,traces,strict=True)]
    arms = (plain, separated, fused)
    errors = [sum(arm(x)!=y for x,y in zip(rows,truth,strict=True)) for arm in arms]
    times = [[] for _ in arms]
    for tick in range(7):
        for i in (range(3) if tick%2==0 else (2,1,0)):
            arm = arms[i]
            start = perf_counter_ns()
            for _ in range(16):
                for row in rows:
                    arm(row)
            times[i].append((perf_counter_ns()-start)/(16*len(rows)))
    return dict(maps=maps,n=len(rows),positive=sum(truth),
                merged=sum(len(e)!=4 for e in traces),errors=errors,
                median_ns=[round(median(x),1) for x in times])


def main():
    start=perf_counter()
    t=(1,2,3,0,5,4)
    f=forced_edges(t)
    case=(t,(4,5),tuple(range(4)),f)
    assert raw_reject(event_edges(t,(4,5),4))
    assert not any(arm(case) for arm in (plain,separated,fused))
    guards=[compare([((0,0,3,4,2),(2,3,4),(0,1),2)]),compare(family())]
    assert all(item["new_errors"]==0 for item in guards)
    results=dict(transposition=evaluate(t),fixed_point=evaluate((1,2,3,0,4)))
    print(json.dumps(dict(results=results,guards=guards,seconds=perf_counter()-start),indent=2))


if __name__=="__main__":
    main()
