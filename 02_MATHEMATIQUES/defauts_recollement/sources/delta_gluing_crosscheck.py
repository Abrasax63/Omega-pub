#!/usr/bin/env python3
"""Independent Boolean-matrix and subset-state cross-check of the gluing audit."""
from itertools import product
from collections import deque
from delta_gluing_audit import family, invariants

def matrix_accepts(t, p, word):
    n = len(t)
    row = [True] * n
    for a in word:
        nxt = [False] * n
        for x in range(n):
            if row[x] and p[x] == a:
                nxt[t[x]] = True
        row = nxt
    return any(row)

def subsets(t, p, q):
    start = frozenset(range(len(t)))
    found = {start}
    todo = deque([start])
    while todo:
        b = todo.popleft()
        for a in range(q):
            nxt = frozenset(t[x] for x in b if p[x] == a)
            if nxt not in found:
                found.add(nxt)
                todo.append(nxt)
    return found

def audit(n, q):
    count = 0
    for t in product(range(n), repeat=n):
        for p in product(range(q), repeat=n):
            if len(set(p)) != q:
                continue
            count += 1
            inv = invariants(t, p, q)
            basis = inv['basis']
            for length in range(1, n + 3):
                for w in product(range(q), repeat=length):
                    mat = matrix_accepts(t, p, w)
                    avoid = not any(w[i:i+len(f)] == f for f in basis
                                    for i in range(length - len(f) + 1))
                    assert mat == avoid, (t, p, w, basis)
            length = inv['Lstar'] + 2
            for w in product(range(q), repeat=length):
                if matrix_accepts(t, p, w):
                    continue
                if matrix_accepts(t, p, w[:-1]) and matrix_accepts(t, p, w[1:]):
                    raise AssertionError(('long forbidden', t, p, w))
    return count

if __name__ == '__main__':
    for n, q in [(2, 2), (3, 2), (4, 2), (3, 3), (4, 3)]:
        print('independent matrix/basis:', n, q, audit(n, q), flush=True)
    for m in range(1, 7):
        t, p = family(m)
        found = subsets(t, p, 2)
        assert len(found) == len(t) + 2, (m, found)
        print('family subset DFA:', m, len(found), flush=True)
