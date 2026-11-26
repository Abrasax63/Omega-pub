"""Check the first-meeting frontier for four-event minimal V19 cores."""
from collections import Counter
from itertools import combinations, product
import json
from statistics import median
from time import perf_counter, perf_counter_ns

from audit_v19_pivot import certify
from audit_v19_shadow_guard import compare, exhaustive_shadow, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_signed import prepare, signed

CYCLE = (0, 1, 2, 3)


def iterate(t):
    square = tuple(t[x] for x in t)
    return tuple(square[x] for x in square)


def first_meeting(t, pair):
    a, b = pair
    for k in range(5):
        if a == b:
            return k
        a, b = t[a], t[b]
    return None


def verdicts(t, force, pairs, guarded):
    quotient = prepare(len(t), force)
    image = iterate(t) if guarded else None
    out = []
    for a, b in pairs:
        if image is not None and image[a] == image[b]:
            out.append(False)
            continue
        events = event_edges(t, (a, b), 4)
        out.append(len(events) == 4 and signed(quotient, events))
    return out


def main():
    start = perf_counter()
    late = (1, 2, 3, 0, 0, 4, 5, 6)
    adverse = (1, 2, 3, 0, 0)
    assert first_meeting(late, (0, 7)) == 4
    assert first_meeting(adverse, (0, 4)) is None
    f = forced_edges(late)
    e = event_edges(late, (0, 7), 4)
    assert exhaustive_shadow(8, f, CYCLE)
    assert len(e) == 4 and not exhaustive_shadow(8, f + e[-1:], CYCLE)
    assert not certify((late, (0, 7), CYCLE, f, e))
    guards = [compare([((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)]), compare(family())]
    assert all(row["new_errors"] == 0 for row in guards)
    pairs = tuple(combinations(range(8), 2))
    sample, strata = [], {}
    for a, b in product(range(4), range(8)):
        t = (1, 2, 3, 0, a, 4, 5, b)
        f = forced_edges(t)
        if not coherent(8, f):
            continue
        truths = []
        for p in pairs:
            meeting = first_meeting(t, p)
            key = "time4" if meeting == 4 else "early" if meeting is not None else "unmerged"
            stats = strata.setdefault(key, Counter())
            events = event_edges(t, p, 4)
            truth = len(events) == 4 and bool(certify((t, p, CYCLE, f, events)))
            if meeting == 4:
                assert len(events) == 4
                stats["singleton_empty"] += not exhaustive_shadow(8, f + events[-1:], CYCLE)
            stats.update(pairs=1, cores=int(truth))
            truths.append(truth)
        sample.append((t, f, truths))
    assert strata["time4"]["pairs"] > 0
    assert strata["time4"]["singleton_empty"] == strata["time4"]["pairs"]
    assert strata["time4"]["cores"] == 0

    def batch(arm):
        return [verdicts(t, f, pairs, arm) for t, f, _ in sample]

    errors = [sum(x != y for arm, (_, _, gold) in zip(batch(guard), sample, strict=True)
                  for x, y in zip(arm, gold, strict=True)) for guard in (False, True)]
    assert errors == [0, 0]
    times = [[], []]
    for rep in range(7):
        for arm in ((0, 1) if rep % 2 == 0 else (1, 0)):
            t = perf_counter_ns()
            for _ in range(20):
                batch(bool(arm))
            times[arm].append((perf_counter_ns()-t)/(20*len(sample)*len(pairs)))
    print(json.dumps(dict(strata=strata, cards=len(sample), errors=errors, guards=guards,
                          median_ns_per_pair=[median(t) for t in times],
                          seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
