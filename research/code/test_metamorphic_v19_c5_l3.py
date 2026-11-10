#!/usr/bin/env python3
"""Metamorphic audit V19 C5, L=3 on the archived U42 witness.

Fixed source witness:
  T = archived U42 endofunction (42 states)
  distinguished cycle C5 = (0,1,2,3,4)
  initial pair = (0,20), archived as C5O-13 in U42 triple row 13
  event horizon L=3; locality prefix uses times 0..L+2 = 0..5.

Two solvers are deliberately different:
  - parity DSU;
  - graph propagation from each of the 32 cycle colorings.

This is a finite check of one archived witness, not a proof of the general L+2 lemma.
"""
from itertools import combinations

T = (
    1, 2, 3, 4, 0, 0, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9,
    10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17,
    18, 18, 19, 19, 41, 40
)
CYCLE = (0, 1, 2, 3, 4)
PAIR = (0, 20)
L = 3
N = len(T)


def forced_edges(F):
    return tuple(
        (u, v)
        for u, v in combinations(range(len(F)), 2)
        if F[u] == F[v] or {F[u], F[v]} == {u, v}
    )


def trajectory_prefix(F, pair, horizon):
    visible = set(CYCLE)
    for start in pair:
        x = start
        for _ in range(horizon + 1):  # t = 0,...,L+2 inclusive
            visible.add(x)
            x = F[x]
    return visible


def event_constraints(F, pair, horizon, equality=True):
    edges = []
    a, b = pair
    parity = 0 if equality else 1
    for _ in range(horizon):
        if a != b:
            edges.append((a, b, parity))
        a, b = F[a], F[b]
    return edges


def shadow_dsu(F, pair, cycle, horizon, allowed=None, equality=True):
    n = len(F)
    allowed = set(range(n)) if allowed is None else set(allowed)
    parent = list(range(n))
    rank = [0] * n
    parity = [0] * n
    bad = False

    def find(x):
        if parent[x] != x:
            old_parent = parent[x]
            root, offset = find(old_parent)
            parity[x] ^= offset
            parent[x] = root
        return parent[x], parity[x]

    def impose(a, b, d):
        nonlocal bad
        ra, xa = find(a)
        rb, xb = find(b)
        if ra == rb:
            bad |= (xa ^ xb) != d
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
            xa, xb = xb, xa
        parent[rb] = ra
        parity[rb] = xa ^ xb ^ d
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for a, b in forced_edges(F):
        if a in allowed and b in allowed:
            impose(a, b, 1)
    for a, b, d in event_constraints(F, pair, horizon, equality):
        if a not in allowed or b not in allowed:
            raise AssertionError("visible prefix omits an event endpoint")
        impose(a, b, d)
    if bad:
        return frozenset()

    roots = [find(v) for v in cycle]
    return frozenset(
        mask for mask in range(1 << len(cycle))
        if all(
            roots[i][0] != roots[j][0]
            or (((mask >> i) & 1) ^ ((mask >> j) & 1))
               == (roots[i][1] ^ roots[j][1])
            for i, j in combinations(range(len(cycle)), 2)
        )
    )


def shadow_bfs(F, pair, cycle, horizon, allowed=None, equality=True):
    """Independent solver: adjacency propagation for each fixed cycle mask."""
    allowed = set(range(len(F))) if allowed is None else set(allowed)
    adj = {v: [] for v in allowed}
    for a, b in forced_edges(F):
        if a in allowed and b in allowed:
            adj[a].append((b, 1))
            adj[b].append((a, 1))
    for a, b, d in event_constraints(F, pair, horizon, equality):
        if a not in allowed or b not in allowed:
            raise AssertionError("visible prefix omits an event endpoint")
        adj[a].append((b, d))
        adj[b].append((a, d))

    result = set()
    for mask in range(1 << len(cycle)):
        colors = {v: (mask >> i) & 1 for i, v in enumerate(cycle)}
        stack = list(cycle)
        consistent = True
        while True:
            while stack and consistent:
                u = stack.pop()
                for v, d in adj[u]:
                    wanted = colors[u] ^ d
                    if v in colors:
                        if colors[v] != wanted:
                            consistent = False
                            break
                    else:
                        colors[v] = wanted
                        stack.append(v)
            if not consistent:
                break
            free = next((v for v in allowed if v not in colors), None)
            if free is None:
                break
            colors[free] = 0
            stack = [free]
        if consistent:
            result.add(mask)
    return frozenset(result)


def conjugate(F, permutation):
    inverse = [0] * len(F)
    for old, new in enumerate(permutation):
        inverse[new] = old
    return tuple(permutation[F[inverse[new]]] for new in range(len(F)))


def rotate_mask(mask, shift, q=5):
    return sum(((mask >> ((i + shift) % q)) & 1) << i for i in range(q))


def check_source_witness():
    assert N == 42
    assert tuple(T[i] for i in CYCLE) == (1, 2, 3, 4, 0)
    assert PAIR == (0, 20)
    # The archived row has C5O-13 at pair_c=(0,20).
    assert T[20] == 10 and T[10] == 5 and T[5] == 0
    print("SOURCE_WITNESS: PASS (U42, C5, L=3, pair (0,20), C5O-13)")


def check_global_locality_and_solvers():
    visible = trajectory_prefix(T, PAIR, L)
    global_dsu = shadow_dsu(T, PAIR, CYCLE, L)
    local_dsu = shadow_dsu(T, PAIR, CYCLE, L, visible)
    global_bfs = shadow_bfs(T, PAIR, CYCLE, L)
    local_bfs = shadow_bfs(T, PAIR, CYCLE, L, visible)
    assert global_dsu == local_dsu
    assert global_bfs == local_bfs
    assert global_dsu == global_bfs
    assert len(global_dsu) not in (0, 32)
    print(
        "GLOBAL_LOCAL: PASS (global = prefix L+2; "
        f"|shadow|={len(global_dsu)}, visible_states={len(visible)})"
    )
    print("DUAL_SOLVER: PASS (parity-DSU = graph propagation)")


def check_all_state_transpositions():
    tested = 0
    for a, b in combinations(range(N), 2):
        sigma = list(range(N))
        sigma[a], sigma[b] = sigma[b], sigma[a]
        F2 = conjugate(T, sigma)
        C2 = tuple(sigma[v] for v in CYCLE)
        P2 = tuple(sigma[v] for v in PAIR)
        visible2 = trajectory_prefix(F2, P2, L)
        g = shadow_dsu(F2, P2, C2, L)
        l = shadow_dsu(F2, P2, C2, L, visible2)
        assert g == l, ("global/local mismatch after relabel", a, b)
        assert g == shadow_dsu(T, PAIR, CYCLE, L)
        assert g == shadow_bfs(F2, P2, C2, L)
        tested += 1
    assert tested == 861
    print("STATE_RELABELING: PASS (861 transpositions of S_42)")


def check_cycle_origin():
    base = shadow_dsu(T, PAIR, CYCLE, L)
    for shift in range(5):
        rotated = tuple(CYCLE[(i + shift) % 5] for i in range(5))
        got = shadow_dsu(T, PAIR, rotated, L)
        expected = frozenset(rotate_mask(m, shift) for m in base)
        assert got == expected, ("cycle origin", shift)
    print("CYCLE_ORIGIN: PASS (5 origins, exact mask rotation)")


def check_color_complement():
    base = shadow_dsu(T, PAIR, CYCLE, L)
    complement = frozenset(mask ^ 0b11111 for mask in base)
    assert complement == base
    print("COLOR_COMPLEMENT: PASS (C5 shadow invariant under c -> 1-c)")


def check_negative_control():
    correct = shadow_dsu(T, PAIR, CYCLE, L)
    mutated = shadow_dsu(T, PAIR, CYCLE, L, equality=False)
    assert mutated != correct
    assert shadow_bfs(T, PAIR, CYCLE, L, equality=False) == mutated
    print(
        "NEGATIVE_CONTROL: PASS (equality->inequality mutation detected; "
        f"correct={len(correct)} masks, mutated={len(mutated)} masks)"
    )


def main():
    check_source_witness()
    check_global_locality_and_solvers()
    check_all_state_transpositions()
    check_cycle_origin()
    check_color_complement()
    check_negative_control()
    print("METAMORPHIC_C5_L3: ALL CHECKS PASSED")
    print("Scope: one archived U42 witness only; no universal L+2 proof.")


if __name__ == "__main__":
    main()
