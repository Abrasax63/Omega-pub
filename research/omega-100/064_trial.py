"""Control the number-of-symbols shortcut at the first feasible equality length."""
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from time import perf_counter
from importlib import import_module

prior = import_module("063_trial")


def groups(words):
    result = {True: [], False: []}
    for word in words:
        result[word[0] == word[1]].append(word)
    return result


def ceiling(pairs):
    classes = defaultdict(Counter)
    for word in pairs:
        classes[len(set(word))][word[0] == word[1]] += 1
    return sum(max(counts.values()) for counts in classes.values())


def evaluate(splits):
    assert prior.disjoint(splits, prior.equality_signature)
    assert all({w[0] == w[1] for w in part} == {True, False} for part in splits)
    flat = tuple(word for part in splits for word in part)
    def oracle(word):
        return prior.equality_signature(word)[0]
    for word in flat:
        for glyphs in (("a", "b", "c", "d"), ("D", "C", "B", "A")):
            renamed = tuple(glyphs[i] for i in word)
            assert oracle(renamed) == (word[0] == word[1])
    return dict(n=len(flat), oracle_correct=len(flat), size_only_ceiling=ceiling(flat),
                size_and_split_ceiling=sum(ceiling(part) for part in splits),
                per_split=[ceiling(part) for part in splits])


def main():
    start = perf_counter()
    words = tuple(prior.canonical_words(4))
    fixed = prior.split_by_class(groups(words))
    binary = [word for word in words if len(set(word)) == 2]
    oracle = {prior.equality_signature(w) for w in product(range(2), repeat=4) if len(set(w)) == 2}
    assert {prior.equality_signature(w) for w in binary} == oracle
    counts = Counter(signature[0] for signature in oracle)
    candidate = prior.split_by_class(groups(binary))
    before, after = evaluate(fixed), evaluate(candidate)
    assert before["size_only_ceiling"] > 3
    assert after["size_only_ceiling"] == after["size_and_split_ceiling"] == 3
    assert after["per_split"] == [1, 1, 1]
    print(json.dumps(dict(fixed=before, candidate=after, eligible_equal=counts[True],
                          eligible_different=counts[False], seconds=round(perf_counter()-start, 6)), indent=2))


if __name__ == "__main__":
    main()
