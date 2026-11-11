"""Independent finite-binary spectrum audit: graph cycles + Boolean matrices.

Does NOT reuse CL-DYN's joint-state stopping algorithm. This verifies finite
instances and witnesses, NOT the universal proof or bibliographic novelty.
"""
from itertools import product
from math import lcm
from collections import Counter
import json


def dynamics_period(t):
    depth, period = 0, 1
    for x in range(len(t)):
        visited = {}
        y = x
        while y not in visited:
            visited[y] = len(visited)
            y = t[y]
        depth = max(depth, visited[y])
        period = lcm(period, len(visited) - visited[y])
    return depth, period


def bool_multiply(q, r):
    result = 0
    for a in range(2):
        for b in range(2):
            if any((q >> (2*a+c) & 1) and
                   (r >> (2*c+b) & 1) for c in range(2)):
                result |= 1 << (2*a+b)
    return result


def spectrum(t, colors):
    """Returns {h:bitmask} if spectrum finite, or None if infinite."""
    n = len(t)
    q = 0
    for x in range(n):
        q |= 1 << (2*colors[x]+colors[t[x]])
    # Eventually periodic macrorelation powers, computed independently.
    seen, powers, r = {}, [], q
    while r not in seen:
        seen[r] = len(powers) + 1
        powers.append(r)
        r = bool_multiply(r, q)
    macro_start = seen[r]
    macro_period = len(powers) + 1 - macro_start
    depth, cycle_period = dynamics_period(t)
    first_periodic = max(1, macro_start, depth)
    joint_period = lcm(macro_period, cycle_period)
    images = list(range(n))
    defects = {}
    r = q
    for h in range(1, first_periodic + joint_period):
        images = [t[x] for x in images]
        micro_mask = 0
        for x in range(n):
            micro_mask |= 1 << (2*colors[x]+colors[images[x]])
        gap = r & ~micro_mask
        if gap:
            if h >= first_periodic:
                return None
            defects[h] = gap
        r = bool_multiply(r, q)
    return defects


def general_constructor(D):
    if not D:
        return (0, 1), (0, 1)
    H = max(D)
    p = H + 1
    t = [(i+1) % p for i in range(p)]
    colors = [0] + [1]*(p-1)
    for depth in range(1, 2*p-1):
        t.append(0 if depth == 1 else p+depth-2)
        colors.append(1)
    for residue in range(1,p):
        depth = residue + (p if residue in D else 0)
        t.append(0 if depth == 1 else p+depth-2)
        colors.append(0)
    return tuple(t), tuple(colors)


def singleton_constructor(H):
    p = next(p for p in range(2,H+2) if H % p)
    L = H+1
    t = tuple((i+1) % p for i in range(p)) + (0,) + tuple(range(p,p+L-1))
    c = (0,)*(p-1) + (1,) + tuple(
        int(d == L or (2 <= d < L and d % p != L % p))
        for d in range(1,L+1))
    return t, c, p


def main():
    small = {}
    for n in range(2,6):
        count = Counter()
        for t in product(range(n), repeat=n):
            # Color-exchange symmetry, both colors used.
            for bits in range(1,1 << (n-1)):
                c = (0,) + tuple(bits >> i & 1 for i in range(n-1))
                sp = spectrum(t,c)
                count["examined"] += 1
                if sp is None:
                    count["infinite"] += 1
                elif sp:
                    count["finite_nonempty"] += 1
                    union = 0
                    for gap in sp.values(): union |= gap
                    assert union in (1,8), (t,c,sp)
        small[str(n)] = dict(count)
    general = 0
    for bits in range(1 << 9):
        D = {h+2 for h in range(9) if bits >> h & 1}
        t,c = general_constructor(D)
        expected = {h: 1 for h in D}
        if D: assert len(t) == 4*max(D)+1
        assert spectrum(t,c) == expected, (D,spectrum(t,c))
        general += 1
    for H in range(2,121):
        t,c,p = singleton_constructor(H)
        assert len(t)==H+1+p
        assert spectrum(t,c)=={H:8},(H,p)
    t8=(1,2,0,0,3,4,5,6)
    for bits in range(1,128):
        c=(0,)+tuple(bits >> i & 1 for i in range(7))
        assert spectrum(t8,c) != {2:8,4:8},c
    t9=(1,2,3,4,5,3,8,1,0)
    c9=(0,0,0,0,0,1,1,1,0)
    assert spectrum(t9,c9)=={2:8,4:8}
    report = {
        "kind":"finite_independent_audit",
        "small_exhaustive":small,
        "general_subsets_checked":general,
        "singleton_H_2_to_120":119,
        "eight_state_colorings_excluded":127,
        "nine_state_witness_verified":True,
        "universal_theorems_certified":False,
        "generalization_to_real_tasks":False
    }
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
