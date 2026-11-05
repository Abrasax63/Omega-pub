#!/usr/bin/env python3
"""Independent exact V19-style verification of the 9-state C4,L=2 witness.
Uses direct parity constraints and enumerates all binary colorings of C4.
"""
from collections import deque

T = [1, 2, 3, 0, 8, 7, 6, 2, 0]
CYCLE = (0, 1, 2, 3)
EXPECTED = {
    "C4O-00": (0, 1, 14, 15),
    "C4O-01": (0, 5, 10, 15),
    "C4O-02": (1, 4, 11, 14),
    "C4O-03": (1, 6, 9, 14),
    "C4O-04": (0, 1, 2, 3, 12, 13, 14, 15),
    "C4O-05": (0, 1, 4, 5, 10, 11, 14, 15),
    "C4O-06": (1, 2, 5, 6, 9, 10, 13, 14),
    "C4O-07": (1, 3, 4, 6, 9, 11, 12, 14),
}

def rotmask(mask, k):
    return sum(((mask >> i) & 1) << ((i + k) % 4) for i in range(4))

def canon(shadow):
    return min(tuple(sorted(rotmask(m, k) for m in shadow)) for k in range(4))

class ParityDSU:
    def __init__(self, nodes):
        self.p = {x: x for x in nodes}
        self.xr = {x: 0 for x in nodes}

    def find(self, x):
        if self.p[x] != x:
            root, parity = self.find(self.p[x])
            self.xr[x] ^= parity
            self.p[x] = root
        return self.p[x], self.xr[x]

    def union(self, a, b, parity):
        ra, xa = self.find(a)
        rb, xb = self.find(b)
        if ra == rb:
            return (xa ^ xb) == parity
        self.p[rb] = ra
        self.xr[rb] = xa ^ xb ^ parity
        return True

def exact_shadow(x, y):
    # V19(2), L=2: local model uses trajectory prefixes through L+2=4.
    A, B = [x], [y]
    for _ in range(4):
        A.append(T[A[-1]])
        B.append(T[B[-1]])
    nodes = sorted(set(A) | set(B) | set(CYCLE))
    dsu = ParityDSU(nodes)

    # Singleton forced pairs: equal images OR invariant unordered pair.
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            if T[u] == T[v] or {T[u], T[v]} == {u, v}:
                if not dsu.union(u, v, 1):
                    return frozenset()

    # Bad event at L=2: equality at t=0,1, omitting diagonal pairs.
    for t in range(2):
        if A[t] != B[t] and not dsu.union(A[t], B[t], 0):
            return frozenset()

    roots = [dsu.find(i) for i in range(4)]
    out = set()
    for mask in range(16):
        if all(
            roots[i][0] != roots[j][0]
            or (((mask >> i) & 1) ^ ((mask >> j) & 1))
               == (roots[i][1] ^ roots[j][1])
            for i in range(4) for j in range(i + 1, 4)
        ):
            out.add(mask)
    return frozenset(out)

def globally_forced_coherent():
    n = len(T)
    indegree = [0] * n
    for v in T:
        indegree[v] += 1
    if max(indegree) > 2:
        return False

    adj = [[] for _ in T]
    for u in range(n):
        for v in range(u + 1, n):
            if T[u] == T[v] or {T[u], T[v]} == {u, v}:
                adj[u].append(v)
                adj[v].append(u)

    color = [None] * n
    for s in range(n):
        if color[s] is not None:
            continue
        color[s] = 0
        todo = deque([s])
        while todo:
            u = todo.popleft()
            for v in adj[u]:
                if color[v] is None:
                    color[v] = color[u] ^ 1
                    todo.append(v)
                elif color[v] == color[u]:
                    return False
    return True

assert len(T) == 9 and all(0 <= v < len(T) for v in T)
assert tuple(T[i] for i in CYCLE) == (1, 2, 3, 0)
assert globally_forced_coherent()

found = {}
for x in range(len(T)):
    for y in range(x + 1, len(T)):
        S = exact_shadow(x, y)
        if not S:
            continue
        c = canon(S)
        for name, target in EXPECTED.items():
            if c == tuple(sorted(target)):
                found.setdefault(name, (x, y, tuple(sorted(S))))

assert set(found) == set(EXPECTED), (set(EXPECTED) - set(found))
print("PASS: total endofunction on 9 states; distinguished C4; globally forced-coherent.")
print("PASS: all 8 expected rotation classes realized under V19(2) local model.")
for name in sorted(found):
    print(f"{name}: pair={found[name][0:2]}, shadow={found[name][2]}")
print("T =", T)
