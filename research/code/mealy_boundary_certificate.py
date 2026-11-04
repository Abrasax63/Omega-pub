#!/usr/bin/env python3
"""Independent finite certificate for the (5,2,3) Mealy counterexample.

It verifies, without using the paper proof:
  * r_IO = 1 (exact 1-step trace language),
  * optimal ADS depth L_A = 3,
  * no preset distinguishing sequence exists (L_P = infinity).

Python 3 standard library only.
"""
from collections import deque
from itertools import combinations

STATES = ("P0", "P1", "Q0", "Q1", "S")
INPUTS = ("a", "b")
OUTPUTS = (0, 1, 2)

# (state,input) -> (output,next_state)
T = {
    ("P0", "a"): (0, "Q0"), ("P0", "b"): (0, "S"),
    ("P1", "a"): (0, "Q1"), ("P1", "b"): (1, "S"),
    ("Q0", "a"): (1, "P0"), ("Q0", "b"): (2, "S"),
    ("Q1", "a"): (1, "P1"), ("Q1", "b"): (2, "S"),
    ("S",  "a"): (2, "S"),  ("S",  "b"): (2, "S"),
}


def verify_rio_one():
    """Exact BFS of local 1-step graph x compatible hidden-state sets."""
    symbols = [(a, y) for a in INPUTS for y in OUTPUTS]

    # Hidden current states compatible after reading one observable symbol.
    after = {}
    occurring = []
    for z in symbols:
        a, y = z
        sset = frozenset(
            nxt for s in STATES for out, nxt in [T[(s, a)]] if out == y
        )
        after[z] = sset
        if sset:
            occurring.append(z)

    # Real length-2 blocks.
    adjacency = set()
    for z in occurring:
        for z2 in occurring:
            a2, y2 = z2
            if any(T[(s, a2)][0] == y2 for s in after[z]):
                adjacency.add((z, z2))

    def advance(S, z):
        a, y = z
        return frozenset(
            T[(s, a)][1] for s in S if T[(s, a)][0] == y
        )

    # If a locally legal continuation ever empties the compatible hidden set,
    # then a locally admissible word is globally unrealizable.
    seen = set()
    q = deque()
    for z in occurring:
        item = (z, after[z])
        seen.add(item)
        q.append(item)

    while q:
        last, S = q.popleft()
        for z2 in occurring:
            if (last, z2) not in adjacency:
                continue
            S2 = advance(S, z2)
            if not S2:
                raise AssertionError(
                    f"Local 1-step path is not globally realizable: {last} -> {z2}"
                )
            item = (z2, S2)
            if item not in seen:
                seen.add(item)
                q.append(item)

    # r_IO is not 0: find two individually occurring symbols whose pair is forbidden.
    forbidden_pair = None
    for z in occurring:
        for z2 in occurring:
            if (z, z2) not in adjacency:
                forbidden_pair = (z, z2)
                break
        if forbidden_pair:
            break
    assert forbidden_pair is not None
    return {
        "product_states": len(seen),
        "occurring_symbols": len(occurring),
        "allowed_2_blocks": len(adjacency),
        "forbidden_pair_witness": forbidden_pair,
    }


def verify_ads_depth():
    """Exact minimax reachability on beliefs preserving initial identity."""
    K0 = frozenset((s, s) for s in STATES)  # (initial,current)

    def initials(K):
        return frozenset(i for i, _ in K)

    def update(K, a, y):
        return frozenset(
            (i, T[(cur, a)][1])
            for i, cur in K
            if T[(cur, a)][0] == y
        )

    # Reachable belief states.
    reachable = {K0}
    q = deque([K0])
    while q:
        K = q.popleft()
        for a in INPUTS:
            for y in OUTPUTS:
                K2 = update(K, a, y)
                if K2 and K2 not in reachable:
                    reachable.add(K2)
                    q.append(K2)

    # Synchronous Bellman layers: W_d = states solvable in <= d further inputs.
    winning = {K for K in reachable if len(initials(K)) <= 1}
    depth = {K: 0 for K in winning}
    for d in range(1, 100):
        prev = set(winning)
        additions = []
        for K in reachable - prev:
            for a in INPUTS:
                branches = [update(K, a, y) for y in OUTPUTS]
                branches = [B for B in branches if B]
                if branches and all(B in prev for B in branches):
                    additions.append(K)
                    break
        for K in additions:
            winning.add(K)
            depth[K] = d
        if K0 in winning:
            break
        if not additions:
            break

    assert depth.get(K0) == 3, depth.get(K0)
    return {"belief_states": len(reachable), "optimal_ADS_depth": depth[K0]}


def verify_no_pds():
    """Exact BFS on all still-undistinguished initial pairs under preset words."""
    initial_pairs = list(combinations(STATES, 2))

    def cp(x, y):
        return tuple(sorted((x, y)))

    # Each entry tracks (initial_pair, current_pair) while output histories remain equal.
    start = tuple((p, p) for p in initial_pairs)

    def step(cfg, a):
        nxt = []
        for initial_pair, current_pair in cfg:
            s, t = current_pair
            y1, s1 = T[(s, a)]
            y2, t1 = T[(t, a)]
            if y1 == y2:  # pair is still not distinguished
                nxt.append((initial_pair, cp(s1, t1)))
        return tuple(nxt)

    seen = {start}
    q = deque([start])
    while q:
        cfg = q.popleft()
        if not cfg:
            raise AssertionError("A PDS exists, contrary to the claimed counterexample")
        for a in INPUTS:
            cfg2 = step(cfg, a)
            if cfg2 not in seen:
                seen.add(cfg2)
                q.append(cfg2)

    assert all(cfg for cfg in seen)
    return {"preset_configurations": len(seen), "PDS_exists": False}


def main():
    rio = verify_rio_one()
    ads = verify_ads_depth()
    pds = verify_no_pds()

    print("CERTIFIED COUNTEREXAMPLE")
    print("states=5, inputs=2, outputs=3")
    print("r_IO = 1")
    print(f"  exact product configurations explored: {rio['product_states']}")
    print(f"  occurring observable symbols: {rio['occurring_symbols']}")
    print(f"  allowed 2-blocks: {rio['allowed_2_blocks']}")
    print(f"  witness r_IO != 0: forbidden pair {rio['forbidden_pair_witness']}")
    print(f"L_A = {ads['optimal_ADS_depth']}")
    print(f"  reachable belief states explored: {ads['belief_states']}")
    print("L_P = infinity")
    print(f"  closed preset-configuration graph size: {pds['preset_configurations']}")
    print("All assertions passed.")


if __name__ == "__main__":
    main()