import importlib
import json
from statistics import median
from time import perf_counter_ns

base = importlib.import_module("050_trial")
guarded = base.pilots.guarded
direct, orbit, binary = base.direct, base.orbit, base.pilots.pilot.apply_power
ARMS = ("direct", "orbit", "ablated", "verified")
TABLES = (
    tuple(list(range(1, 10)) + [3, 4]),
    tuple([*range(1, 10), 4, *range(11, 21), 16, *range(22, 31), 21]),
)
DENSITIES = (0, 25, 50, 75, 95)


class Run:
    def __init__(self, arm):
        self.arm = arm
        self.cache = {}
        self.calls = self.hits = self.verified = 0

    def solve(self, mapping, start, horizon, fault="ok"):
        def evaluate(values, s, h):
            if fault == "offline":
                raise OSError("simulated outage")
            key = mapping, s, h
            if self.arm == "verified" and key in self.cache:
                self.hits += 1
                return self.cache[key]
            self.calls += 1
            value = (orbit if self.arm == "orbit" else direct)(values, s, h)
            if fault == "wrong":
                value = (value + 1) % len(mapping)
            if self.arm == "verified":
                self.verified += 1
                if value != orbit(values, s, h):
                    return None
                self.cache[key] = value
            return value
        return guarded(evaluate, list(mapping), start, horizon)


def controls():
    runner = Run("verified")
    mapping = TABLES[0]
    assert runner.solve(mapping, 0, 99, "wrong") == ("unavailable", None)
    assert not runner.cache
    assert runner.solve(mapping, 0, 99) == ("exact", binary(mapping, 0, 99))
    assert runner.solve(mapping, 0, 99, "offline") == ("unavailable", None)
    assert runner.solve((11,) + mapping[1:], 0, 99) == ("invalid", None)
    assert runner.hits == 0 and runner.calls == 2 and runner.verified == 2


def batch(mapping, density):
    n = len(mapping)
    count = 480 * (100 - density) // 100
    unique = [(mapping, i % n, 100 - i // n) for i in range(count)]
    return [unique[i % count] for i in range(480)]


def measure(rows):
    truth = [("exact", binary(*row)) for row in rows]
    stats = {arm: [] for arm in ARMS}
    for rep in range(5):
        for arm in (ARMS if rep % 2 == 0 else ARMS[::-1]):
            start = perf_counter_ns()
            runner = Run(arm)
            observed = [runner.solve(*row) for row in rows]
            elapsed = perf_counter_ns() - start
            stats[arm].append((elapsed, sum(a != b for a, b in zip(observed, truth)),
                               runner.calls, runner.hits, runner.verified))
    return {arm: dict(median_ns=median(r[0] for r in data),
                      errors=max(r[1] for r in data), calls=data[0][2],
                      hits=data[0][3], verifications=data[0][4])
            for arm, data in stats.items()}


def main():
    start = perf_counter_ns()
    controls()
    results = {str(len(m)): {d: measure(batch(m, d)) for d in DENSITIES} for m in TABLES}
    print(json.dumps(dict(results=results, adverse_checks=4,
                          elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
