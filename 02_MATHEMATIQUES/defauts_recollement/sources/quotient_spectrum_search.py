#!/usr/bin/env python3
"""Exact enumeration for defect spectra of finite deterministic quotients.

States are represented by (Q^h, pi o T^h), which is sufficient to recover
Delta_h exactly.  No numerical approximation is used.
"""

from __future__ import annotations

import argparse
import itertools
from collections import Counter, defaultdict
from dataclasses import dataclass
from math import gcd


def rgs_partitions(n: int):
    """Restricted-growth strings: one canonical labelling per set partition."""
    if n == 0:
        yield ()
        return
    a = [0] * n

    def rec(i: int, mx: int):
        if i == n:
            yield tuple(a)
            return
        for v in range(mx + 2):
            a[i] = v
            yield from rec(i + 1, max(mx, v))

    yield from rec(1, 0)


def compose_relation(left: tuple[int, ...], right: tuple[int, ...]):
    """Boolean relation product left * right, with bit-set rows."""
    out = []
    for row in left:
        acc = 0
        bits = row
        while bits:
            low = bits & -bits
            j = low.bit_length() - 1
            acc |= right[j]
            bits ^= low
        out.append(acc)
    return tuple(out)


def divisors(n: int):
    return [d for d in range(1, n + 1) if n % d == 0]


@dataclass(frozen=True)
class Spectrum:
    state_mu: int
    state_period: int
    output_mu: int
    output_period: int
    prefix: tuple[bool, ...]
    cycle: tuple[bool, ...]

    def key(self):
        return (self.output_mu, self.output_period, self.prefix, self.cycle)

    def accepts(self, h: int) -> bool:
        if h < self.output_mu:
            return self.prefix[h]
        return self.cycle[(h - self.output_mu) % self.output_period]

    def label(self) -> str:
        pre = "".join("1" if x else "0" for x in self.prefix)
        cyc = "".join("1" if x else "0" for x in self.cycle)
        return f"{pre}({cyc})"


def exact_spectrum(T: tuple[int, ...], pi: tuple[int, ...]) -> Spectrum:
    n = len(T)
    m = max(pi) + 1
    q = [0] * m
    for x in range(n):
        q[pi[x]] |= 1 << pi[T[x]]
    q = tuple(q)

    relation = tuple(1 << a for a in range(m))  # Q^0
    colour = pi  # pi o T^0
    seen = {}
    outputs = []
    states = []
    h = 0
    while (relation, colour) not in seen:
        seen[(relation, colour)] = h
        states.append((relation, colour))
        exact = [0] * m
        for x, a in enumerate(pi):
            exact[a] |= 1 << colour[x]
        defective = any(relation[a] & ~exact[a] for a in range(m))
        outputs.append(defective)
        relation = compose_relation(relation, q)
        colour = tuple(colour[T[x]] for x in range(n))
        h += 1

    state_mu = seen[(relation, colour)]
    state_period = h - state_mu

    # Two full state cycles suffice to test every suffix equality.
    extended = outputs + outputs[state_mu:h] * 2
    best = None
    for mu in range(h):
        for period in divisors(state_period):
            if all(
                extended[k] == extended[k + period]
                for k in range(mu, len(extended) - period)
            ):
                best = (mu, period)
                break
        if best is not None:
            break
    assert best is not None
    output_mu, output_period = best
    prefix = tuple(outputs[:output_mu])
    cycle = tuple(outputs[output_mu : output_mu + output_period])
    return Spectrum(
        state_mu, state_period, output_mu, output_period, prefix, cycle
    )


def universal_realisation(
    prefix: tuple[bool, ...], cycle: tuple[bool, ...]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Realise any ultimately periodic D with d_0=d_1=False.

    ``prefix`` gives d_0,...,d_{mu-1}; ``cycle`` is the nonempty repeating
    block from mu onward.  The construction uses three macro states:
    S (source), F (always-covered endpoint), and N (endpoint whose absence
    marks a defect).
    """
    if not cycle:
        raise ValueError("cycle must be nonempty")

    mu = len(prefix)
    period = len(cycle)

    def d(h: int) -> bool:
        if h < mu:
            return prefix[h]
        return cycle[(h - mu) % period]

    if d(0) or d(1):
        raise ValueError("a defect spectrum must reject lengths 0 and 1")

    # We may choose any later onset of periodicity.  H >= 2 makes r_1 a
    # genuine transient position and avoids indexing edge cases.
    H = max(mu, 2)

    # State indices and colours: S=0, F=1, N=2.
    s_f, s_w, f_fix, n_fix, f_to_n, n_to_f = range(6)
    T = [0] * (6 + H + period - 1)
    pi = [0, 0, 1, 2, 1, 2] + [0] * (H + period - 1)

    # Complete and endpoint-exact support on {F,N}.
    T[f_fix] = f_fix
    T[n_fix] = n_fix
    T[f_to_n] = n_fix
    T[n_to_f] = f_fix

    first_r = 6
    T[s_f] = f_fix
    T[s_w] = first_r

    # r_h represents the h-th symbol of the prescribed lasso word.
    for h in range(1, H + period):
        idx = first_r + h - 1
        pi[idx] = 1 if d(h) else 2  # F on D, N off D
        if h < H + period - 1:
            T[idx] = idx + 1
        else:
            T[idx] = first_r + H - 1

    return tuple(T), tuple(pi)


def enumerate_n(n: int):
    spectra = Counter()
    witnesses = {}
    by_m = defaultdict(set)
    max_min_states = 0
    max_witness = None
    partitions = list(rgs_partitions(n))
    for T in itertools.product(range(n), repeat=n):
        for pi in partitions:
            s = exact_spectrum(T, pi)
            key = s.key()
            spectra[key] += 1
            witnesses.setdefault(key, (T, pi, s))
            by_m[max(pi) + 1].add(key)
            qstates = s.output_mu + s.output_period
            if qstates > max_min_states:
                max_min_states = qstates
                max_witness = (T, pi, s)
    return spectra, witnesses, by_m, max_min_states, max_witness


def spectrum_is_empty(s: Spectrum) -> bool:
    return not any(s.prefix) and not any(s.cycle)


def spectrum_is_finite(s: Spectrum) -> bool:
    return not any(s.cycle)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--show", type=int, default=100)
    args = ap.parse_args()
    spectra, witnesses, by_m, max_states, max_witness = enumerate_n(args.n)
    print(f"n={args.n} distinct_spectra={len(spectra)} total={sum(spectra.values())}")
    empty = sum(count for key, count in spectra.items() if not any(key[2]) and not any(key[3]))
    finite_nonempty = sum(
        count
        for key, count in spectra.items()
        if any(key[2]) and not any(key[3])
    )
    infinite = sum(count for key, count in spectra.items() if any(key[3]))
    print(
        f"empty={empty} finite_nonempty={finite_nonempty} infinite={infinite}"
    )
    print("by_m=" + ", ".join(f"{m}:{len(v)}" for m, v in sorted(by_m.items())))
    print(f"max_minimal_dfa_states={max_states} witness={max_witness}")
    ordered = sorted(
        witnesses.values(),
        key=lambda z: (z[2].output_mu + z[2].output_period, z[2].label()),
    )
    for T, pi, s in ordered[: args.show]:
        print(
            f"D={s.label():<18} count={spectra[s.key()]:<7} "
            f"state=({s.state_mu},{s.state_period}) T={T} pi={pi}"
        )


if __name__ == "__main__":
    main()