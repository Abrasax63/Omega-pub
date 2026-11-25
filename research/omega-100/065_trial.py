"""Test whether equality splits can hold the strongest symbol multiplicity fixed."""
from collections import Counter
from importlib import import_module
from itertools import combinations, product
import json
from time import perf_counter

prior = import_module("063_trial")
fixed_design = import_module("064_trial")


def maximum(word):
    return max(Counter(word).values())


def ceiling(words):
    counts = {}
    for word in words:
        bucket = counts.setdefault(maximum(word), Counter())
        bucket[word[0] == word[1]] += 1
    return sum(max(bucket.values()) for bucket in counts.values())


def evaluate(splits):
    assert prior.disjoint(splits, prior.equality_signature)
    for part in splits:
        assert all(len(w) == 4 and len(set(w)) == 2 for w in part)
        assert {prior.equality_signature(w)[0] for w in part} == {True, False}
    return dict(global_ceiling=ceiling(w for part in splits for w in part),
                by_split_ceiling=sum(ceiling(part) for part in splits),
                oracle_correct=sum(map(len, splits)))


def main():
    start = perf_counter()
    adverse = ((0,0,0,1), (0,1,0,1))
    assert ceiling(adverse) == 2 and prior.disjoint(((adverse[0],), (adverse[1],)), prior.equality_signature)
    words = tuple(w for w in prior.canonical_words(4) if len(set(w)) == 2)
    groups = fixed_design.groups(words)
    ref = prior.split_by_class(groups)
    pairs = [(a,b) for a,b in product(groups[True],groups[False]) if maximum(a) == maximum(b)]
    chosen = []
    for pair in pairs:
        if all(set(pair).isdisjoint(prior_pair) for prior_pair in chosen):
            chosen.append(pair)
    # Independent oracle: actual bit patterns and index pair comparisons.
    signed = {prior.equality_signature(w): maximum(w)
              for w in product(range(2), repeat=4) if len(set(w)) == 2}
    edges = [(a,b) for a,b in product(signed,repeat=2)
             if a[0] and not b[0] and signed[a] == signed[b]]
    max_matching = max(n for n in range(1,len(signed)//2+1)
                       if any(len({v for edge in es for v in edge}) == 2*n
                              for es in combinations(edges,n)))
    before, after = evaluate(ref), evaluate(chosen)
    assert max_matching == len(chosen) == 3
    assert before["global_ceiling"] > after["global_ceiling"] == after["by_split_ceiling"] == 3
    print(json.dumps(dict(fixed=before, candidate=after, oracle_pairs=max_matching,
                          seconds=round(perf_counter()-start, 6)), indent=2))


if __name__ == "__main__":
    main()
