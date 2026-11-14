"""Compare V19 shadows using only observed transitions in the local calculation."""

import argparse
from itertools import combinations, product
import json
from pathlib import Path

from .verify import shadow


def forced_edges(images):
    return [(u, v, 1) for (u, a), (v, b) in combinations(images.items(), 2)
            if a == b or (a, b) in ((u, v), (v, u))]


def prefix_shadow(cycle, left, right, L):
    """Inputs are the ordered cycle and the two lists of observed state IDs."""
    images = dict(zip(cycle, cycle[1:] + cycle[:1]))
    for orbit in (left, right):
        for u, v in zip(orbit, orbit[1:]):
            if images.setdefault(u, v) != v:
                raise ValueError("Inconsistent observed transitions")
    event = [(u, v, 0) for u, v in zip(left[:L], right[:L])]
    labels = {v: i for i, v in enumerate(sorted(set(cycle) | set(left) | set(right)))}
    edges = [(labels[u], labels[v], p) for u, v, p in forced_edges(images) + event]
    return shadow(len(labels), edges, tuple(labels[v] for v in cycle))


def orbit(T, start, length):
    states = [start]
    for _ in range(length - 1):
        states.append(T[states[-1]])
    return states


def cycles(T):
    for start in range(len(T)):
        trace = orbit(T, start, len(T) + 1)
        if start in trace[1:]:
            cycle = tuple(trace[:trace.index(start, 1)])
            if len(cycle) >= 3 and start == min(cycle):
                yield cycle


def search(extra_steps):
    counts = {}
    for n in range(3, 7):
        counts[n] = 0
        for T in product(range(n), repeat=n):
            forced = forced_edges(dict(enumerate(T)))
            if not shadow(n, forced, ()):
                continue
            for cycle in cycles(T):
                for x, y in combinations(range(n), 2):
                    for L in (2, 3):
                        left = orbit(T, x, L + extra_steps + 1)
                        right = orbit(T, y, L + extra_steps + 1)
                        event = [(u, v, 0) for u, v in zip(left[:L], right[:L])]
                        full = shadow(n, forced + event, cycle)
                        local = prefix_shadow(cycle, left, right, L)
                        counts[n] += 1
                        if local != full:
                            witness = dict(T=T, cycle=cycle, L=L, left=left, right=right,
                                           global_shadow=sorted(full), prefix_shadow=sorted(local))
                            return dict(counts=counts, witness=witness)
    return dict(counts=counts, witness=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output path.")
    report = {
        "scope": "N <= 6, q >= 3, L in {2,3}, coherent forced constraints",
        "through_L_plus_1": search(1),
        "through_L_exploratory": search(0),
    }
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    expected = {3: 12, 4: 456, 5: 12280, 6: 312720}
    return int(report["through_L_plus_1"] != dict(counts=expected, witness=None))


if __name__ == "__main__":
    raise SystemExit(main())
