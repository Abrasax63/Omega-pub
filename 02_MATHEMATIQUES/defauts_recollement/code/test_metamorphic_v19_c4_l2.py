#!/usr/bin/env python3
"""Tests métamorphiques indépendants du témoin V19 C4, L=2.

Périmètre strict : témoin T à 9 états, cycle distingué C4, huit paires
historiques et contrat opérationnel raccordé à V19(2) dans le dossier source.

Relations testées :
1. équivariance par renommage d'états (36 transpositions de S_9) ;
2. covariance par rotation de l'origine du cycle C4 ;
3. symétrie par complément global des couleurs binaires.

Ce script ne prouve ni le théorème général L+2, ni la minimalité globale,
ni l'originalité bibliographique. Il ne remplace pas les vérificateurs existants.
"""
from itertools import combinations, product

T = (1, 2, 3, 0, 8, 7, 6, 2, 0)
CYCLE = (0, 1, 2, 3)
PAIRS = (
    (0, 1), (0, 2), (1, 8), (0, 7),
    (0, 6), (4, 5), (1, 4), (0, 4),
)
TARGETS = (
    frozenset((0, 7, 8, 15)),
    frozenset((0, 5, 10, 15)),
    frozenset((2, 7, 8, 13)),
    frozenset((1, 6, 9, 14)),
    frozenset((0, 3, 4, 7, 8, 11, 12, 15)),
    frozenset((0, 1, 4, 5, 10, 11, 14, 15)),
    frozenset((4, 5, 6, 7, 8, 9, 10, 11)),
    frozenset((2, 3, 6, 7, 8, 9, 12, 13)),
)


def forced_edges(F):
    return tuple(
        (u, v)
        for u, v in combinations(range(len(F)), 2)
        if F[u] == F[v] or {F[u], F[v]} == {u, v}
    )


def shadow(F, x, y, cycle):
    """Énumération globale directe des colorations binaires."""
    n = len(F)
    forced = forced_edges(F)
    requirements = []
    a, b = x, y
    for _ in range(2):  # L=2 : égalités aux temps 0 et 1
        if a != b:      # diagonale omise
            requirements.append((a, b))
        a, b = F[a], F[b]

    out = set()
    for coloring in product((0, 1), repeat=n):
        if any(coloring[u] == coloring[v] for u, v in forced):
            continue
        if any(coloring[u] != coloring[v] for u, v in requirements):
            continue
        mask = sum(coloring[cycle[i]] << i for i in range(4))
        out.add(mask)
    return frozenset(out)


def rotate_cycle_mask(mask, shift):
    """Coordonnées du masque après remplacement de C par T^shift(C)."""
    return sum(
        ((mask >> ((i + shift) % 4)) & 1) << i
        for i in range(4)
    )


def conjugate(F, permutation):
    """F' = sigma o F o sigma^{-1}, avec transport des étiquettes."""
    inverse = [0] * len(F)
    for old, new in enumerate(permutation):
        inverse[new] = old
    return tuple(permutation[F[inverse[new]]] for new in range(len(F)))


def check_base_witness():
    observed = tuple(shadow(T, x, y, CYCLE) for x, y in PAIRS)
    assert observed == TARGETS, "Les huit ombres brutes ne correspondent plus"
    print("BASE_WITNESS: PASS (8/8 ombres brutes)")


def check_state_relabelings():
    n = len(T)
    tested = 0
    for u, v in combinations(range(n), 2):
        sigma = list(range(n))
        sigma[u], sigma[v] = sigma[v], sigma[u]
        F2 = conjugate(T, sigma)
        cycle2 = tuple(sigma[x] for x in CYCLE)
        pairs2 = tuple((sigma[x], sigma[y]) for x, y in PAIRS)
        for index, (x, y) in enumerate(pairs2):
            got = shadow(F2, x, y, cycle2)
            assert got == TARGETS[index], (
                f"Renommage transposition ({u},{v}), classe {index}: "
                f"{sorted(got)} != {sorted(TARGETS[index])}"
            )
        tested += 1
    assert tested == 36
    print("STATE_RELABELING: PASS (36 transpositions de S_9, 8 classes chacune)")


def check_cycle_origin():
    for shift in range(4):
        cycle2 = tuple(CYCLE[(i + shift) % 4] for i in range(4))
        for index, (x, y) in enumerate(PAIRS):
            got = shadow(T, x, y, cycle2)
            expected = frozenset(
                rotate_cycle_mask(mask, shift) for mask in TARGETS[index]
            )
            assert got == expected, (
                f"Origine du cycle décalée de {shift}, classe {index}"
            )
    print("CYCLE_ORIGIN: PASS (4 origines, relation de rotation exacte)")


def check_global_color_complement():
    for index, target in enumerate(TARGETS):
        complement = frozenset(mask ^ 0b1111 for mask in target)
        assert complement == target, (
            f"Complément global non fermé pour la classe {index}"
        )
    print("COLOR_COMPLEMENT: PASS (8/8 ombres invariantes par c -> 1-c)")


def main():
    assert len(T) == 9 and all(0 <= x < 9 for x in T)
    assert tuple(T[i] for i in CYCLE) == (1, 2, 3, 0)
    check_base_witness()
    check_state_relabelings()
    check_cycle_origin()
    check_global_color_complement()
    print("METAMORPHIC_C4: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
