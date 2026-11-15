#!/usr/bin/env python3
"""Exact finite pilot: collective constraints hidden from lower-order observers.

The detector receives *only observable trajectories*, not generators, parity
labels or latent states. It is a mathematical reference, NOT an Omega agent.
"""
from collections import Counter
from itertools import combinations, product
from fractions import Fraction
import json


def parity_world(dimension, parity):
    """GENERATOR ONLY: a cyclic deterministic system, uniform initial states."""
    if dimension < 3 or parity not in (0, 1):
        raise ValueError("dimension >=3 and parity 0 or 1 required")
    return tuple(x for x in product((0, 1), repeat=dimension)
                 if sum(x) % 2 == parity)


def trajectories(world, horizon):
    """Cyclic shift T(x0,...,x(n-1))=(x1,...,x(n-1),x0), pi(x)=x0."""
    if horizon < 1 or not world:
        raise ValueError("nonempty world, horizon >= 1 required")
    n = len(world[0])
    if any(len(x) != n or any(b not in (0, 1) for b in x) for x in world):
        raise ValueError("all states must be equal-length binary tuples")
    return tuple(tuple(x[t % n] for t in range(horizon)) for x in world)


def projected_distribution(rows, coordinates):
    """Exact empirical probabilities of selected columns (raw rows only)."""
    if not rows:
        raise ValueError("need observed rows")
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("duplicate coordinate")
    if not coordinates or min(coordinates) < 0 or max(coordinates) >= len(rows[0]):
        raise ValueError("coordinate outside observations")
    counts = Counter(tuple(r[i] for i in coordinates) for r in rows)
    return {k: Fraction(v, len(rows)) for k, v in counts.items()}


def walsh(rows, coordinates):
    """Exact parity Fourier/Walsh coefficient, computed on observed rows."""
    if not rows or not coordinates:
        raise ValueError("need rows and nonempty coordinates")
    return sum((1 if sum(r[i] for i in coordinates) % 2 == 0 else -1)
               for r in rows) * Fraction(1, len(rows))


def inspect_observations(rows_a, rows_b):
    """Try successively longer temporal representations; no latent-state access.

    The experimental finder enumerates full observable words. It returns the
    first separating horizon, all differences in the corresponding projection,
    and the first Walsh order that distinguishes the trace distributions.
    """
    if not rows_a or not rows_b:
        raise ValueError("both observable datasets required")
    horizon = min(len(rows_a[0]), len(rows_b[0]))
    if any(len(r) < horizon for r in rows_a + rows_b):
        raise ValueError("inconsistent trace lengths")
    differences = []
    for length in range(1, horizon + 1):
        a = projected_distribution(rows_a, tuple(range(length)))
        b = projected_distribution(rows_b, tuple(range(length)))
        if a != b:
            differences.append(length)
    first = differences[0] if differences else None
    walsh_witness = None
    if first is not None:
        for size in range(1, first + 1):
            for coords in combinations(range(first), size):
                a = walsh(rows_a, coords)
                b = walsh(rows_b, coords)
                if a != b:
                    walsh_witness = {"coordinates": list(coords),
                                     "coefficient_a": str(a),
                                     "coefficient_b": str(b)}
                    break
            if walsh_witness:
                break
    return {"first_separating_horizon": first,
            "compared_horizons": horizon,
            "separating_horizons": differences,
            "walsh_witness": walsh_witness}


def endpoint_relation(rows, h):
    if h < 1 or not rows or len(rows[0]) <= h:
        raise ValueError("invalid endpoint horizon")
    return frozenset((r[0], r[h]) for r in rows)


def pair_only_baseline(rows_a, rows_b):
    """Uses the unordered one- and two-time marginals of available traces."""
    horizon = min(len(rows_a[0]), len(rows_b[0]))
    for size in (1, 2):
        for coords in combinations(range(horizon), size):
            if projected_distribution(rows_a, coords) != projected_distribution(rows_b, coords):
                return "different"
    return "indistinguishable"


def independent_support_audit(rows_a, rows_b, horizon):
    """Independent set-based comparison; no Fraction, Counter or Walsh."""
    support_a = {tuple(row[:horizon]) for row in rows_a}
    support_b = {tuple(row[:horizon]) for row in rows_b}
    return {"equal": support_a == support_b,
            "only_a": [list(x) for x in sorted(support_a - support_b)],
            "only_b": [list(x) for x in sorted(support_b - support_a)]}


def run(dimension=3):
    even = trajectories(parity_world(dimension, 0), 2 * dimension + 1)
    odd = trajectories(parity_world(dimension, 1), 2 * dimension + 1)
    found = inspect_observations(even, odd)
    if found["first_separating_horizon"] != dimension:
        raise AssertionError("unexpected first horizon")
    return {
        "experiment": "collective_observability_v01",
        "status": "CALCUL EXACT (finite synthetic models)",
        "dimension": dimension,
        "states_per_world": len(even),
        "first_separating_horizon": found["first_separating_horizon"],
        "pair_only_baseline": pair_only_baseline(even, odd),
        "walsh_witness": found["walsh_witness"],
        "endpoint_relations_identical_h1_to_h2n": all(
            endpoint_relation(even, h) == endpoint_relation(odd, h)
            for h in range(1, 2 * dimension + 1)),
        "independent_support_check_before": independent_support_audit(
            even, odd, dimension - 1),
        "independent_support_check_at": independent_support_audit(
            even, odd, dimension),
        "omega_planner_executed": False,
        "model_calls": 0,
        "limitation": "Synthetic known parity examples; reference detector, not the Omega planner or autonomous research.",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimension", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(run(args.dimension), ensure_ascii=False, indent=2))
