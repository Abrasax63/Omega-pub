"""Evaluate an endpoint-only screen before signed quotient construction."""
import json
from itertools import combinations, product
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, priority
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import fixed, prepare, signed


def raw_reject(events):
    endpoints = set()
    for a, b, _ in events:
        pair = (a, b) if a <= b else (b, a)
        if a == b or pair in endpoints:
            return True
        endpoints.add(pair)
    return False


def signed_core(row):
    return signed(prepare(len(row[0]), row[3]), row[4])


def guarded(row):
    return not raw_reject(row[4]) and signed_core(row)


def unsigned(row):
    return not priority(row) and fixed(row)


def reserve(q):
    groups = {key: [] for key in ("raw_reject", "quotient_reject", "survivor_negative", "positive")}
    for anchor, a, b in product(range(q), range(q+3), range(q+3)):
        t = (*range(1, q), 0, anchor, q, q+1, a, b)
        forced = forced_edges(t)
        if not coherent(len(t), forced):
            continue
        for pair in combinations(range(len(t)), 2):
            events = event_edges(t, pair, 4)
            if len(events) != 4:
                continue
            row = t, pair, tuple(range(q)), forced, events
            if raw_reject(events):
                key = "raw_reject"
            elif priority(row):
                key = "quotient_reject"
            else:
                key = "positive" if fixed(row) else "survivor_negative"
            if len(groups[key]) < 12:
                groups[key].append(row)
            if all(len(rows) == 12 for rows in groups.values()):
                return groups
    return groups


def compare_arms(rows):
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
            for _ in range(64):
                for row in rows:
                    arm(row)
            samples[i].append((perf_counter_ns() - start) / (64 * len(rows)))
    return {"n": len(rows), "positive": sum(truth), "errors": errors,
            "median_ns_per_pair": [round(median(sample), 1) for sample in samples]}


def main():
    start = perf_counter_ns()
    t = tuple(range(8))
    parallel = (t, None, tuple(range(4)), (), ((0,1,0),(0,1,1),(2,3,0),(3,0,0)))
    matching = (t, None, tuple(range(4)), ((1,2,0),(3,4,0),(5,6,0),(7,0,0)),
                ((0,1,0),(2,3,0),(4,5,0),(6,7,1)))
    assert raw_reject(parallel[4]) and not certify(parallel) and not guarded(parallel)
    assert not raw_reject(matching[4]) and certify(matching) and guarded(matching)
    witness = ((0,0,3,4,2), (2,3,4), (0,1), 2)
    guards = [compare([witness]), compare(family())]
    assert all(item["new_errors"] == 0 for item in guards)
    results = {q: {key: compare_arms(rows) if rows else {"n": 0}
                   for key, rows in reserve(q).items()} for q in (4, 5)}
    assert all(cell["positive"] == (cell["n"] if key == "positive" else 0)
               for groups in results.values() for key, cell in groups.items() if cell["n"])
    print(json.dumps({"results": results, "guards": guards,
                      "seconds": (perf_counter_ns() - start)/1e9}, indent=2))


if __name__ == "__main__":
    main()
