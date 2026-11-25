import importlib
import json
from statistics import median
from time import perf_counter_ns

prior = importlib.import_module("054_trial")


def chunked(rows):
    valid = 0
    keys = set()
    for offset in (0,32,64,96):
        for key, status in rows[offset:offset+32]:
            if status == "exact":
                valid += 1
                keys.add(key)
        if len(keys) >= 13:
            return False
    return valid >= 96 and 10 * len(keys) <= valid


def reserve():
    def boundary(at):
        return [((i % 12 if i < at else 12), "exact") for i in range(128)]

    return {
        **{f"boundary_{at+1}": boundary(at) for at in (30,31,32,62,63,64)},
        "dense_tail_outage": [(i % 3, "exact" if i < 112 else "unavailable") for i in range(128)],
        "dense_interleaved": [(i % 5, "exact" if i % 5 else "invalid") for i in range(128)],
        "invalid_burst": [(i, "invalid" if i < 100 else "exact") for i in range(128)],
        "sparse": [(i, "exact") for i in range(128)],
        "sparse_then_offline": [(i, "exact" if i < 48 else "unavailable") for i in range(128)],
    }


def check(rows):
    expected = prior.oracle(rows)
    arms = (prior.full, prior.bounded, chunked)
    result = [arm(rows) for arm in arms]
    assert result == [expected] * 3
    times = [[] for _ in arms]
    for rep in range(7):
        for i in ((0,1,2) if rep % 2 == 0 else (2,1,0)):
            arm = arms[i]
            tick = perf_counter_ns()
            for _ in range(512):
                arm(rows)
            times[i].append((perf_counter_ns()-tick)/512)
    return dict(expected=expected, result=result, ns=[median(t) for t in times])


def main():
    start = perf_counter_ns()
    print(json.dumps(dict(results={k: check(rows) for k, rows in reserve().items()},
                          elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
