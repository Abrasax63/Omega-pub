"""Exact minimum for a fixed transposition in three disjoint equality splits."""
from collections import Counter
from importlib import import_module
from itertools import product
import json
from time import perf_counter

prior = import_module("063_trial")


def swap(word):
    return (word[0], word[2], word[1], *word[3:])


def literal_oracle(n):
    edges = set()
    for word in product(range(2), repeat=n):
        a, b = prior.equality_signature(word), prior.equality_signature(swap(word))
        if a[0] and not b[0]:
            edges.add((a, b))
    assert len({x for edge in edges for x in edge}) == 2 * len(edges)
    return edges


def verify_pairs(rows):
    assert prior.disjoint(rows, prior.equality_signature)
    return sum(prior.equality_signature(w)[0] == (i == 0)
               for pair in rows for i, w in enumerate(pair))


def main():
    start = perf_counter()
    adverse = ((0,0,1,1), (0,1,1,0))
    assert Counter(adverse[0]) == Counter(adverse[1])
    assert verify_pairs((adverse,)) == 2
    assert prior.equality_signature(swap(adverse[0])) != prior.equality_signature(adverse[1])
    results = {}
    for n in range(3, 7):
        rows = [(w, swap(w)) for w in prior.canonical_words(n)
                if len(set(w)) == 2 and w[0] == w[1] and w[0] != w[2]]
        edges = {(prior.equality_signature(a), prior.equality_signature(b)) for a,b in rows}
        assert edges == literal_oracle(n)
        assert all(Counter(a) == Counter(b) for a,b in rows)
        assert verify_pairs(rows) == 2*len(rows)
        results[n] = dict(pairs=len(rows), feasible=len(rows)>=3,
                          oracle_correct_on_three=verify_pairs(rows[:3]) if len(rows)>=3 else None)
    assert min(n for n,row in results.items() if row["feasible"]) == 5
    print(json.dumps(dict(lengths=results, adverse_profile_passed=True, adverse_swap_passed=False,
                          seconds=round(perf_counter()-start, 6)),indent=2))


if __name__ == "__main__":
    main()
