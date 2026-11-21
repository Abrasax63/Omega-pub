#!/usr/bin/env python3
"""Classify the information in V19 observations by exhaustive completions.

No paid API; uses stdlib only. Proof certificates are finite/exhaustive on a
fixed, labelled carrier, not universal theorems.  Does not import V19 solvers.
"""
from collections import Counter, defaultdict
from itertools import combinations, product
import json
import sys


CASES = {
    'C3_n10_unseen': {
        'n': 10, 'cycle': (0, 1, 2),
        'paths': ((7, 5, 3), (8, 6, 4)),
    },
    'C3_n9': {
        'n': 9, 'cycle': (0, 1, 2),
        'paths': ((7, 5, 3), (8, 6, 4)),
    },
    'C4_n10': {
        'n': 10, 'cycle': (0, 1, 2, 3),
        'paths': ((8, 6, 4), (9, 7, 5)),
    },
}


def edges(n, t):
    forced = tuple((u, v, 1) for u, v in combinations(range(n), 2)
                   if t[u] == t[v] or {t[u], t[v]} == {u, v})
    return forced


def parity_consistent(n, edges_, cycle=(), mask=0):
    """DSU/parity solver; anchor n is the color zero."""
    parent = list(range(n + 1))
    parity = [0] * (n + 1)
    rank = [0] * (n + 1)

    def root(u):
        if parent[u] == u:
            return u, 0
        r, p = root(parent[u])
        parity[u] ^= p
        parent[u] = r
        return r, parity[u]

    def put(u, v, p):
        a, x = root(u)
        b, y = root(v)
        if a == b:
            return (x ^ y) == p
        if rank[a] < rank[b]:
            a, b, x, y = b, a, y, x
        parent[b] = a
        parity[b] = x ^ y ^ p
        if rank[a] == rank[b]:
            rank[a] += 1
        return True

    if not all(put(u, v, p) for u, v, p in edges_):
        return False
    return all(put(v, n, (mask >> i) & 1) for i, v in enumerate(cycle))


def oracle(n, cycle, constraints):
    """Separate 2^n brute force solver, not using parity_consistent."""
    shadows = set()
    for bits in range(1 << n):
        if all((((bits >> u) ^ (bits >> v)) & 1) == p
               for u, v, p in constraints):
            shadows.add(sum(((bits >> v) & 1) << i for i, v in enumerate(cycle)))
    return frozenset(shadows)


def classify(spec):
    n, cycle, paths = spec['n'], spec['cycle'], spec['paths']
    horizon = len(paths[0]) - 1
    assert len(paths) == 2 and all(len(path) == horizon + 1 for path in paths)
    known = dict(zip(cycle, cycle[1:] + cycle[:1]))
    for path in paths:
        for u, v in zip(path, path[1:]):
            assert known.setdefault(u, v) == v
    unknown = tuple(sorted(set(range(n)) - set(known)))
    assert len(unknown) <= 3
    event = tuple((paths[0][i], paths[1][i], 0) for i in range(horizon))
    compatible = {}
    for values in product(range(n), repeat=len(unknown)):
        mapping = known | dict(zip(unknown, values))
        t = tuple(mapping[v] for v in range(n))
        f = edges(n, t)
        if not parity_consistent(n, f):
            continue
        constraints = f + event
        shadow = frozenset(mask for mask in range(1 << len(cycle))
                           if parity_consistent(n, constraints, cycle, mask))
        assert shadow == oracle(n, cycle, constraints), (t, shadow)
        compatible[values] = shadow

    reports = []
    for size in range(len(unknown) + 1):
        for observed in combinations(unknown, size):
            lookup = [unknown.index(v) for v in observed]
            groups = defaultdict(list)
            for values, shadow in compatible.items():
                key = tuple(values[i] for i in lookup)
                groups[key].append((values, shadow))
            ambiguous, decided, witnesses = 0, 0, []
            decisive_values = []
            for key, entries in sorted(groups.items()):
                first_values, first_shadow = entries[0]
                contrast = next(((v, s) for v, s in entries if s != first_shadow), None)
                if contrast is None:
                    decided += len(entries)
                    decisive_values.append(list(key))
                else:
                    ambiguous += len(entries)
                    witnesses.append({
                        'observation': list(key),
                        'completion_a': list(first_values),
                        'shadow_a': sorted(first_shadow),
                        'completion_b': list(contrast[0]),
                        'shadow_b': sorted(contrast[1]),
                        'class_size': len(entries),
                    })
            assert decided + ambiguous == len(compatible)
            reports.append({
                'observed_transitions': list(observed),
                'nonempty_observation_classes': len(groups),
                'decisive_classes': len(decisive_values),
                'ambiguous_classes': len(witnesses),
                'decisive_completions': decided,
                'ambiguous_completions': ambiguous,
                'decisive_values': decisive_values,
                'ambiguity_witnesses': witnesses,
            })
    histogram = Counter(tuple(sorted(v)) for v in compatible.values())
    return {
        'scope': 'fixed labelled state space and fixed observed paths; only globally coherent forced graphs',
        'n': n, 'cycle': list(cycle), 'paths': [list(p) for p in paths],
        'known': [[k, v] for k, v in sorted(known.items())],
        'unknown': list(unknown),
        'raw_completions': n ** len(unknown),
        'admissible_completions': len(compatible),
        'excluded_incoherent': n ** len(unknown) - len(compatible),
        'double_checked_completions': len(compatible),
        'shadow_histogram': [{'shadow': list(shadow), 'count': count}
                             for shadow, count in sorted(histogram.items())],
        'observation_classes': reports,
    }


def main():
    result = {name: classify(spec) for name, spec in CASES.items()}
    p = result['C3_n10_unseen']
    assert (p['raw_completions'], p['admissible_completions'], p['excluded_incoherent']) == (1000, 800, 200)
    assert {tuple(s['shadow']): s['count'] for s in p['shadow_histogram']} == {
        (): 15, tuple(range(8)): 785}
    for s in (3, 4):
        row = next(r for r in p['observation_classes'] if r['observed_transitions'] == [s])
        assert (row['decisive_classes'], row['ambiguous_classes'], row['decisive_completions']) == (8, 2, 651)
    both = next(r for r in p['observation_classes'] if r['observed_transitions'] == [3, 4])
    assert (both['ambiguous_classes'], both['decisive_completions']) == (0, 800)
    assert (result['C3_n9']['admissible_completions'],
            result['C4_n10']['admissible_completions']) == (74, 92)
    for name, item in result.items():
        print(f"{name}: raw={item['raw_completions']} admissible={item['admissible_completions']} "+
              f"excluded={item['excluded_incoherent']} two_oracles_match={item['double_checked_completions']}")
        for cls in item['observation_classes']:
            if len(cls['observed_transitions']) <= 1 or cls['observed_transitions'] == item['unknown'][:2]:
                print(f"  observed={cls['observed_transitions']} decisive_classes={cls['decisive_classes']} "+
                      f"ambiguous_classes={cls['ambiguous_classes']} decisive_completions={cls['decisive_completions']}")
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')


if __name__ == '__main__':
    main()
