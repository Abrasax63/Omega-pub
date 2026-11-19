"""Read binary relations once, maintaining flat signed components."""
from time import perf_counter

from rule import choose
from solver import Cap, OutOfBudget, solve


def upper_bound(n, edges):
    """Upper bound for the charged reads and small-to-large relabels."""
    return edges + n * (n-1).bit_length() // 2


def incremental(case):
    start = perf_counter()
    n = case['n']
    group = list(range(n))
    members = [[i] for i in range(n)]
    colors = [0] * n
    meter = Cap()
    reads = 0
    answer, witness = None, None
    try:
        for a,b,sign in case['edges']:
            meter.tick()
            reads += 1
            left,right = group[a],group[b]
            delta = colors[a] ^ colors[b] ^ sign
            if left == right:
                if delta:
                    answer = False
                    break
                continue
            if len(members[left]) < len(members[right]):
                left,right = right,left
            # Changing every relative color by delta satisfies the new edge.
            for v in members[right]:
                meter.tick()
                group[v] = left
                colors[v] ^= delta
            members[left].extend(members[right])
            members[right].clear()
        else:
            answer = True
            witness = sum(color << i for i,color in enumerate(colors))
    except OutOfBudget:
        pass
    return dict(answer=answer,witness=witness,steps=meter.used,read_edges=reads,
                source='incremental',seconds=perf_counter()-start)


def route(case, *, guarded=True):
    method = choose(case)
    if (case['kind'] == 'parity' and method == 'B'
            and (not guarded or upper_bound(case['n'],len(case['edges']))<=64)):
        return incremental(case)
    return dict(solve(case,method),source='reference')
