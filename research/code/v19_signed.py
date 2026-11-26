import json
from itertools import combinations
from statistics import median
from time import perf_counter_ns

from audit_v19_pivot import certify, family
from audit_v19_shadow_guard import compare, family as guard_family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_shared import candidate
from v19_unequal import fixed


def prepare(n, edges):
    link = [[] for _ in range(n)]
    for a,b,p in edges:
        link[a].append((b,p))
        link[b].append((a,p))
    comp = [None] * n
    for root in range(n):
        if comp[root] is not None:
            continue
        comp[root] = root, 0
        stack = [root]
        while stack:
            a = stack.pop()
            for b,p in link[a]:
                value = root, comp[a][1] ^ p
                if comp[b] is None:
                    comp[b] = value
                    stack.append(b)
                elif comp[b] != value:
                    raise ValueError("incoherent base")
    return comp


def signed(comp, events):
    parity = 0
    degrees = {}
    seen = set()
    for a,b,p in events:
        a,x = comp[a]
        b,y = comp[b]
        if a == b:
            return False
        edge = (a,b) if a < b else (b,a)
        if edge in seen:
            return False
        seen.add(edge)
        parity ^= x ^ y ^ p
        degrees[a] = degrees.get(a, 0) + 1
        degrees[b] = degrees.get(b, 0) + 1
    return bool(parity and len(degrees) == 4 and all(d == 2 for d in degrees.values()))


def cohorts():
    for q in (4, 6):
        prefix = (*range(1,q), 0)
        for anchor in (0, 1):
            for tail in ((anchor, (anchor+1)%q, q, q+1), (anchor,q,q+1,q+2)):
                t = prefix + tail
                n = len(t)
                forced = forced_edges(t)
                assert coherent(n, forced)
                yield [(t, pair, tuple(range(q)), forced, events)
                       for pair in reversed(tuple(combinations(range(n),2)))
                       if len(events := event_edges(t,pair,4)) == 4]


def prepared(groups):
    answers = []
    for group in groups:
        if group:
            t, _, _, edges, _ = group[0]
            comp = prepare(len(t), edges)
            answers.extend(signed(comp, row[4]) for row in group)
    return answers


def main():
    start = perf_counter_ns()
    witness = ((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)
    guards = [compare([witness]), compare(guard_family())]
    assert all(row["new_errors"] == 0 for row in guards)
    pure = next(family(4,4))
    assert not certify(pure) and prepared([[pure]]) == [False]
    assert not signed(prepare(4, ()), ((0,0,1),(0,1,0),(1,2,0),(2,3,0)))
    groups = list(cohorts())
    rows = [r for group in groups for r in group]
    assert len(rows) <= 400
    truths = [bool(certify(row)) for row in rows]
    fns = (lambda: [fixed(r) for r in rows], lambda: [candidate(r) for r in rows],
           lambda: prepared(groups))
    times = [[] for _ in fns]
    errors = []
    for fn in fns:
        values = fn()
        errors.append(sum(a != b for a,b in zip(values,truths,strict=True)))
    for rep in range(7):
        for i in (range(3) if rep%2 == 0 else (2,1,0)):
            t = perf_counter_ns()
            for _ in range(40):
                fns[i]()
            times[i].append((perf_counter_ns()-t)/40)
    print(json.dumps(dict(cases=len(rows), positives=sum(truths), groups=len(groups),
                          errors=errors, ns=[median(t) for t in times], guards=guards,
                          elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
