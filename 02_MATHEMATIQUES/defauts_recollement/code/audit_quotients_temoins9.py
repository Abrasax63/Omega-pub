from itertools import combinations, product, permutations
from collections import deque

# Audit conditionnel du témoin C4, L=2 à 9 états.
# Contrat : contraintes forcées T(u)=T(v) ou {T(u),T(v)}={u,v};
# égalités de couleur sur les trajectoires aux temps t=0,1.
T = (1, 2, 3, 0, 8, 7, 6, 2, 0)
PAIRS = ((0, 1), (0, 2), (1, 8), (0, 7), (0, 6), (4, 5), (1, 4), (0, 4))
TARGETS = (
    frozenset((0, 7, 8, 15)), frozenset((0, 5, 10, 15)),
    frozenset((2, 7, 8, 13)), frozenset((1, 6, 9, 14)),
    frozenset((0, 3, 4, 7, 8, 11, 12, 15)),
    frozenset((0, 1, 4, 5, 10, 11, 14, 15)),
    frozenset((4, 5, 6, 7, 8, 9, 10, 11)),
    frozenset((2, 3, 6, 7, 8, 9, 12, 13)),
)


def canonical(shadow):
    def rotate(mask, k):
        return sum(((mask >> i) & 1) << ((i + k) % 4) for i in range(4))
    return min(tuple(sorted(rotate(mask, k) for mask in shadow)) for k in range(4))


TARGET_CLASSES = {canonical(s) for s in TARGETS}


def normalize(partition):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in partition)


def congruence_closure(partition):
    p = list(partition)
    changed = True
    while changed:
        changed = False
        for i in range(len(T)):
            for j in range(i):
                if p[i] == p[j] and p[T[i]] != p[T[j]]:
                    lo, hi = sorted((p[T[i]], p[T[j]]))
                    p = [lo if z == hi else z for z in p]
                    changed = True
        p = list(normalize(p))
    return tuple(p)


def congruences_by_closure():
    root = tuple(range(len(T)))
    seen, queue = {root}, deque([root])
    while queue:
        p = queue.popleft()
        for a, b in combinations(sorted(set(p)), 2):
            lo, hi = sorted((a, b))
            q = congruence_closure(tuple(lo if z == hi else z for z in p))
            if q not in seen:
                seen.add(q)
                queue.append(q)
    return seen


def restricted_growth_partitions(n):
    labels = [0] * n
    def visit(i, maximum):
        if i == n:
            yield tuple(labels)
            return
        for z in range(maximum + 2):
            labels[i] = z
            yield from visit(i + 1, max(maximum, z))
    yield from visit(1, 0)


def congruences_by_direct_partition_enumeration():
    out = set()
    for p in restricted_growth_partitions(len(T)):
        if all(p[T[i]] == p[T[j]]
               for i, j in combinations(range(len(T)), 2) if p[i] == p[j]):
            out.add(normalize(p))
    return out


def quotient(partition):
    blocks = sorted(set(partition))
    representative = [partition.index(block) for block in blocks]
    index = {block: i for i, block in enumerate(blocks)}
    F = tuple(index[partition[T[r]]] for r in representative)
    pairs = []
    for x, y in PAIRS:
        a, b = index[partition[x]], index[partition[y]]
        if a == b:
            return None
        pairs.append((a, b))
    cycle = tuple(index[partition[i]] for i in range(4))
    if len(set(cycle)) != 4:
        return None
    return F, tuple(pairs), cycle


def coherent(F):
    n = len(F)
    if any(F.count(v) > 2 for v in range(n)):
        return False
    edges = [(i, j) for i, j in combinations(range(n), 2)
             if F[i] == F[j] or {F[i], F[j]} == {i, j}]
    adjacency = [[] for _ in F]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    colors = [-1] * n
    for start in range(n):
        if colors[start] >= 0:
            continue
        colors[start] = 0
        stack = [start]
        while stack:
            a = stack.pop()
            for b in adjacency[a]:
                if colors[b] < 0:
                    colors[b] = 1 - colors[a]
                    stack.append(b)
                elif colors[b] == colors[a]:
                    return False
    return True


def shadow(F, x, y, cycle):
    n = len(F)
    forced = [(i, j) for i, j in combinations(range(n), 2)
              if F[i] == F[j] or {F[i], F[j]} == {i, j}]
    requirements = []
    a, b = x, y
    for _ in range(2):
        if a != b:
            requirements.append((a, b))
        a, b = F[a], F[b]
    out = set()
    for coloring in product((0, 1), repeat=n):
        if any(coloring[a] == coloring[b] for a, b in forced):
            continue
        if any(coloring[a] != coloring[b] for a, b in requirements):
            continue
        out.add(sum(coloring[cycle[i]] << i for i in range(4)))
    return frozenset(out)


def main():
    closure = congruences_by_closure()
    direct = congruences_by_direct_partition_enumeration()
    assert closure == direct
    print("CONGRUENCES", len(closure))

    eligible_sizes = []
    preserving = []
    for partition in closure:
        q = quotient(partition)
        if q is None:
            continue
        F, pairs, cycle = q
        if not coherent(F):
            continue
        eligible_sizes.append(len(F))
        produced = {canonical(shadow(F, *pair, cycle)) for pair in pairs}
        if TARGET_CLASSES <= produced:
            preserving.append((len(F), F, pairs, cycle, partition))

    sizes = {n: eligible_sizes.count(n) for n in sorted(set(eligible_sizes))}
    print("CYCLE_AND_PAIR_VALID_COHERENT", len(eligible_sizes), "sizes", sizes)
    print("PRESERVE_ALL_TARGETS", len(preserving))
    for item in sorted(preserving, key=lambda z: z[0]):
        print("VALID", item[:4], "partition", item[4])

    base = set(TARGET_CLASSES)
    invariant = True
    for perm in permutations(range(4, 9)):
        relabel = {i: i for i in range(4)}
        relabel.update({4 + i: perm[i] for i in range(5)})
        F = [None] * 9
        for i in range(9):
            F[relabel[i]] = relabel[T[i]]
        moved_pairs = [(relabel[x], relabel[y]) for x, y in PAIRS]
        produced = {canonical(shadow(tuple(F), *pair, (0, 1, 2, 3)))
                    for pair in moved_pairs}
        if produced != base:
            invariant = False
            break
    print("TRANSIENT_RELABELINGS_TESTED", 120,
          "all_eight_target_classes_invariant", invariant)
    assert len(closure) == 49
    assert len(eligible_sizes) == 9
    assert preserving == [(9, T, PAIRS, (0, 1, 2, 3), tuple(range(9)))]
    assert invariant


if __name__ == "__main__":
    main()
