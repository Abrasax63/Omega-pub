#!/usr/bin/env python3
"""Independent checks for quotient_spectrum_search.py."""

from __future__ import annotations

import itertools
import random

from quotient_spectrum_search import (
    compose_relation,
    exact_spectrum,
    rgs_partitions,
    universal_realisation,
)


def direct_outputs(T, pi, horizon):
    n = len(T)
    m = max(pi) + 1
    q = [0] * m
    for x in range(n):
        q[pi[x]] |= 1 << pi[T[x]]
    q = tuple(q)
    qp = tuple(1 << a for a in range(m))
    th = tuple(range(n))
    out = []
    for _h in range(horizon):
        e = [0] * m
        for x in range(n):
            e[pi[x]] |= 1 << pi[th[x]]
        out.append(any(qp[a] & ~e[a] for a in range(m)))
        qp = compose_relation(qp, q)
        th = tuple(T[th[x]] for x in range(n))
    return tuple(out)


def relabel(T, pi, state_perm, class_perm):
    n = len(T)
    inv = [0] * n
    for old, new in enumerate(state_perm):
        inv[new] = old
    new_T = tuple(state_perm[T[inv[x]]] for x in range(n))
    new_pi = tuple(class_perm[pi[inv[x]]] for x in range(n))
    return new_T, new_pi


def main():
    rng = random.Random(20260917)
    checked = 0
    invariant_checked = 0
    for n in range(1, 7):
        parts = list(rgs_partitions(n))
        cases = []
        if n <= 4:
            cases = itertools.product(itertools.product(range(n), repeat=n), parts)
        else:
            cases = (
                (
                    tuple(rng.randrange(n) for _ in range(n)),
                    rng.choice(parts),
                )
                for _ in range(5000)
            )
        for T, pi in cases:
            T = tuple(T)
            s = exact_spectrum(T, pi)
            direct = direct_outputs(T, pi, 80)
            predicted = tuple(s.accepts(h) for h in range(80))
            assert direct == predicted, (T, pi, s, direct, predicted)
            assert not s.accepts(0)
            assert not s.accepts(1)
            checked += 1

            if invariant_checked < 20000 and n > 1:
                sp = list(range(n))
                rng.shuffle(sp)
                m = max(pi) + 1
                cp = list(range(m))
                rng.shuffle(cp)
                T2, pi2 = relabel(T, pi, sp, cp)
                s2 = exact_spectrum(T2, pi2)
                assert s.key() == s2.key(), (T, pi, T2, pi2, s, s2)
                invariant_checked += 1

    universal_checked = 0
    for mu in range(0, 7):
        for period in range(1, 7):
            for prefix in itertools.product((False, True), repeat=mu):
                for cycle in itertools.product((False, True), repeat=period):
                    def desired(h):
                        if h < mu:
                            return prefix[h]
                        return cycle[(h - mu) % period]

                    if desired(0) or desired(1):
                        continue
                    T, pi = universal_realisation(prefix, cycle)
                    got = direct_outputs(T, pi, 150)
                    want = tuple(desired(h) for h in range(150))
                    assert got == want, (mu, period, prefix, cycle, T, pi)
                    universal_checked += 1

    print(
        f"verified direct={checked} relabelling_invariance={invariant_checked} "
        f"universal_realisations={universal_checked} horizons=80/150"
    )


if __name__ == "__main__":
    main()