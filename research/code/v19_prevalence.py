"""Measure the raw event screen without selecting cases by their labels."""
import json
from itertools import combinations
from statistics import median
from time import perf_counter, perf_counter_ns

from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_raw_screen import fixed, guarded, raw_reject, signed_core, unsigned

def compare_arms(rows, passes=64):
    truth = [bool(certify(row)) for row in rows]
    arms = (fixed, unsigned, signed_core, guarded)
    errors = [sum(arm(row) != value for row, value in zip(rows, truth, strict=True))
              for arm in arms]
    samples = [[] for _ in arms]
    for run in range(7):
        order = range(4) if run % 2 == 0 else reversed(range(4))
        for i in order:
            arm = arms[i]
            start = perf_counter_ns()
            for _ in range(passes):
                for row in rows:
                    arm(row)
            samples[i].append((perf_counter_ns() - start) / (passes * len(rows)))
    return {"n": len(rows), "positive": sum(truth), "errors": errors,
            "median_ns_per_pair": [round(median(sample), 1) for sample in samples]}



def cohort(q):
    tail = sorted({(a, b) for a in range(q+2)
                   for b in ((3*a+1) % (q+2), (5*a+2) % (q+2))})
    rows, maps = [], 0
    for a, b in tail:
        t = (*range(1, q), 0, q+1, q, a, b)
        forced = forced_edges(t)
        if not coherent(len(t), forced):
            continue
        maps += 1
        for pair in combinations(range(len(t)), 2):
            events = event_edges(t, pair, 4)
            if len(events) == 4:
                rows.append((t, pair, tuple(range(q)), forced, events))
    return maps, rows


def main():
    start = perf_counter()
    adverse = (tuple(range(4)), None, tuple(range(4)), (),
               ((0,1,0),(0,1,1),(2,3,0),(3,0,0)))
    assert raw_reject(adverse[4]) and not certify(adverse) and not guarded(adverse)
    witness = ((0,0,3,4,2), (2,3,4), (0,1), 2)
    guards = [compare([witness]), compare(family())]
    assert all(g["new_errors"] == 0 for g in guards)
    results = {}
    for q in (6, 7):
        maps, rows = cohort(q)
        results[q] = dict(maps=maps, raw_rejections=sum(raw_reject(r[4]) for r in rows),
                          **compare_arms(rows, passes=16))
    print(json.dumps(dict(results=results, guards=guards, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
