import importlib
import json
from statistics import median
from time import perf_counter_ns

pilot = importlib.import_module("048_trial")
TABLES = (
    ([1, 2, 3, 4, 4], 0, 17),
    ([1, 2, 0, 4, 3, 4], 5, 22),
    ([2, 2, 3, 4, 3, 0, 1], 6, 39),
    ([7, 5, 1, 6, 2, 0, 4, 3], 7, 93),
)


def relabel(mapping, permutation):
    if sorted(permutation) != list(range(len(mapping))):
        raise ValueError("Not a bijection")
    relabeled = list(mapping)
    for index, value in enumerate(mapping):
        relabeled[permutation[index]] = permutation[value]
    return relabeled


def case(mapping, start, horizon, fault="ok"):
    return dict(mapping=mapping, fault=fault,
                question=f"Effectue {horizon} transitions à partir de l’état {start}.")


def oracle(mapping, start, horizon):
    state = start
    for _ in range(horizon):
        state = mapping[state]
    return state


def call(row):
    return pilot.candidate(row, pilot.solver.guarded)


def main():
    started = perf_counter_ns()
    m, s, h = TABLES[0]
    assert call(case(m, s, h, "offline")) == ("unavailable", None, 1)
    assert call(case(m, len(m), h, "offline")) == ("invalid", None, 0)
    try:
        relabel(m, [0] * len(m))
    except ValueError:
        pass
    else:
        raise AssertionError("Non-bijection accepted")
    rows = []
    for mapping, start, horizon in TABLES:
        ids = list(range(len(mapping)))
        for permutation in (ids, ids[::-1], ids[1:] + ids[:1], ids[::2] + ids[1::2]):
            transformed = relabel(mapping, permutation)
            rows.append((transformed, permutation[start], horizon,
                         permutation[oracle(mapping, start, horizon)]))
    requests = [case(*row[:3]) for row in rows]
    expected = [row[3] for row in rows]
    times = [[], []]
    for repeat in range(200):
        for side in ((0, 1) if repeat % 2 == 0 else (1, 0)):
            tick = perf_counter_ns()
            if side == 0:
                reference = [oracle(*row[:3]) for row in rows]
            else:
                observed = [call(row) for row in requests]
            times[side].append(perf_counter_ns() - tick)
    assert reference == expected
    assert observed == [("exact", y, 1) for y in expected]
    print(json.dumps(dict(rows=len(rows), correct=len(rows), errors=0,
                          disabled=1, invalid=1, nonbijection=1,
                          median_ns=list(map(median, times)),
                          elapsed_ns=perf_counter_ns()-started), indent=2))


if __name__ == "__main__":
    main()
