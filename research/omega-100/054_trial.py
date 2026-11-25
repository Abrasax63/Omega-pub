from collections import Counter
import importlib
import json
from statistics import median
from time import perf_counter_ns

previous = importlib.import_module("053_trial")


def full(rows):
    valid = 0
    keys = set()
    for key, status in rows:
        if status == "exact":
            valid += 1
            keys.add(key)
    return valid >= 96 and 10 * len(keys) <= valid


def bounded(rows):
    valid = 0
    keys = set()
    for key, status in rows:
        if status == "exact":
            valid += 1
            keys.add(key)
            if len(keys) == 13:
                return False
    return valid >= 96 and 10 * len(keys) <= valid


def sampled(rows):
    window = previous.Window()
    for row in rows:
        decision = window.track(*row)
    return decision


def oracle(rows):
    frequencies = Counter(key for key, status in rows if status == "exact")
    valid = sum(frequencies.values())
    duplicates = sum(count - 1 for count in frequencies.values())
    return valid >= 96 and 10 * duplicates >= 9 * valid


def reserve():
    def profile(valid, distinct):
        return [(i % distinct, "exact" if i < valid else "unavailable") for i in range(128)]

    return {
        "dense": profile(128, 1),
        "alias": [(0 if i % 4 == 0 else i, "exact") for i in range(128)],
        "offline": profile(0, 1),
        "valid95": profile(95, 3),
        "valid96": profile(96, 3),
        "keys12_valid119": profile(119, 12),
        "keys12_valid120": profile(120, 12),
        "sample_offline": [(0, "unavailable" if i % 4 == 0 else "exact") for i in range(128)],
        "sparse": profile(127, 127),
    }


def benchmark(rows):
    expected = oracle(rows)
    arms = (full, bounded, sampled)
    times = [[] for _ in arms]
    for rep in range(7):
        for i in (range(3) if rep % 2 == 0 else (2, 1, 0)):
            arm = arms[i]
            start = perf_counter_ns()
            for _ in range(512):
                verdict = arm(rows)
            times[i].append((perf_counter_ns()-start)/512)
    return dict(expected=expected, results=[f(rows) for f in arms],
                median_ns=[median(x) for x in times])


def main():
    start = perf_counter_ns()
    sets = reserve()
    assert sets["dense"][::4] == sets["alias"][::4]
    assert oracle(sets["dense"]) and not oracle(sets["alias"])
    assert sampled(sets["dense"]) and sampled(sets["alias"])
    results = {key: benchmark(rows) for key, rows in sets.items()}
    assert all(r["results"][:2] == [r["expected"]] * 2 for r in results.values())
    print(json.dumps(dict(results=results, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
