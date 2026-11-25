"""Exact feasibility of name-invariant, balanced splits for a fixed-index equality task."""
from collections import Counter
from itertools import combinations, product
import json
from time import perf_counter


def equality_signature(word):
    return tuple(word[i] == word[j] for i, j in combinations(range(len(word)), 2))


def partition_counts(n):
    # Reference: exhaustive concrete words over an alphabet sufficient for n distinct symbols.
    quotient = {equality_signature(w) for w in product(range(n), repeat=n)}
    return Counter(signature[0] for signature in quotient)


def canonical_words(n, prefix=(0,)):
    if len(prefix) == n:
        yield prefix
        return
    for symbol in range(max(prefix) + 2):
        yield from canonical_words(n, prefix + (symbol,))


def split_by_class(groups):
    if min(map(len, groups.values())) < 3:
        return None
    return tuple((groups[True][i], groups[False][i]) for i in range(3))


def disjoint(splits, signature):
    signatures = [{signature(w) for w in part} for part in splits]
    return all(not a & b for a, b in combinations(signatures, 2))


def main():
    start = perf_counter()
    adverse = tuple(((i, i, i), (i, i+1, i)) for i in (0, 2, 4))
    assert disjoint(adverse, tuple)
    assert not disjoint(adverse, equality_signature)
    results = {}
    for n in range(2, 6):
        expected = partition_counts(n)
        groups = {True: [], False: []}
        for word in canonical_words(n):
            groups[word[0] == word[1]].append(word)
        counts = {label: len(words) for label, words in groups.items()}
        candidate = split_by_class(groups)
        assert counts == expected
        assert bool(candidate) == (min(expected.values()) >= 3)
        if candidate:
            assert disjoint(candidate, equality_signature)
            assert all({word[0] == word[1] for word in part} == {False, True} for part in candidate)
        results[n] = {"equal": counts[True], "different": counts[False], "feasible": bool(candidate)}
    assert [n for n, row in results.items() if row["feasible"]] == [4, 5]
    print(json.dumps({"lengths": results, "literal_adverse_passes": True,
                      "structural_adverse_passes": False, "seconds": round(perf_counter()-start, 6)},
                     indent=2))


if __name__ == "__main__":
    main()
