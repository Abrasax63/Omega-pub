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


def shadow(F, x, y, cycle, trajectory_equality=True):
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
        if any((coloring[u] == coloring[v]) != trajectory_equality
               for u, v in requirements):
            continue
        mask = sum(coloring[cycle[i]] << i for i in range(4))
        out.add(mask)
    return frozenset(out)


class ParityDSU:
    """Résolution indépendante des contraintes binaires par union-find à parité."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.parity = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.parity[x] ^= self.parity[self.parent[x]]
            self.parent[x] = root
        return self.parent[x]

    def relation(self, x):
        root = self.find(x)
        return root, self.parity[x]

    def union(self, a, b, required_xor):
        ra, xa = self.relation(a)
        rb, xb = self.relation(b)
        if ra == rb:
            return (xa ^ xb) == required_xor
        self.parent[rb] = ra
        self.parity[rb] = xa ^ xb ^ required_xor
        return True


def shadow_by_parity_dsu(F, x, y, cycle):
    """Même contrat, autre algorithme : propagation des égalités/inégalités."""
    n = len(F)
    dsu = ParityDSU(n)
    for a, b in forced_edges(F):
        if not dsu.union(a, b, 1):
            return frozenset()
    a, b = x, y
    for _ in range(2):
        if a != b and not dsu.union(a, b, 0):
            return frozenset()
        a, b = F[a], F[b]

    roots = [dsu.relation(cycle[i]) for i in range(4)]
    out = set()
    for mask in range(16):
        valid = True
        for i in range(4):
            for j in range(i + 1, 4):
                ri, pi = roots[i]
                rj, pj = roots[j]
                if ri == rj and (((mask >> i) & 1) ^ ((mask >> j) & 1)) != (pi ^ pj):
                    valid = False
                    break
            if not valid:
                break
        if valid:
            out.add(mask)
    return frozenset(out)


def check_independent_solver():
    # Contrôle différentiel sur le témoin et ses 36 images par transposition.
    n = len(T)
    tested = 0
    systems = [(T, list(range(n)))]
    for u, v in combinations(range(n), 2):
        sigma = list(range(n))
        sigma[u], sigma[v] = sigma[v], sigma[u]
        systems.append((conjugate(T, sigma), sigma))
    for F, sigma in systems:
        cycle = tuple(sigma[x] for x in CYCLE)
        pairs = tuple((sigma[x], sigma[y]) for x, y in PAIRS)
        for x, y in pairs:
            brute = shadow(F, x, y, cycle)
            dsu = shadow_by_parity_dsu(F, x, y, cycle)
            assert brute == dsu, ("Désaccord brute-force / DSU", sigma, (x, y))
            tested += 1
    assert tested == 37 * 8
    print("INDEPENDENT_SOLVER: PASS (brute-force = parity-DSU sur 296 ombres)")


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


def check_negative_control():
    # Mutation volontaire du contrat : remplacer les égalités de trajectoire
    # par des inégalités. Le témoin de référence ne doit plus être reproduit.
    mutated = tuple(
        shadow(T, x, y, CYCLE, trajectory_equality=False)
        for x, y in PAIRS
    )
    exact_matches = sum(
        got == expected for got, expected in zip(mutated, TARGETS)
    )
    assert exact_matches == 1, (
        f"Le contrôle négatif aurait dû reproduire exactement 1/8 ombres, "
        f"pas {exact_matches}/8"
    )
    print("NEGATIVE_CONTROL: PASS (contrat muté égalité -> inégalité : 1/8 seulement)")


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
    check_independent_solver()
    check_negative_control()
    check_cycle_origin()
    check_global_color_complement()
    print("METAMORPHIC_C4: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
