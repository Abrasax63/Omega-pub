import importlib
import json
from statistics import median
from time import perf_counter_ns

trial = importlib.import_module("051_trial")
ARMS = ("direct", "orbit", "verified", "adaptive")
TABLES = (
    tuple([(i + 3) % 17 for i in range(16)] + [8]),
    tuple([(i + 1) % 29 if i % 4 else i for i in range(29)]),
)
PROFILES = ("HH", "LL", "HL", "LH")
BLOCK_SIZE = 128


class Policy:
    def __init__(self):
        self.engine = trial.Run("orbit")
        self.keys = set()
        self.count = 0
        self.activations = self.reversions = self.hits = self.calls = self.clears = 0

    def solve(self, mapping, start, horizon, fault="ok"):
        engine = self.engine
        if len(engine.cache) >= BLOCK_SIZE:
            engine.cache.clear()
            self.clears += 1
        before_calls, before_hits = engine.calls, engine.hits
        output = engine.solve(mapping, start, horizon, fault)
        self.hits += engine.hits - before_hits
        self.calls += engine.calls - before_calls
        # Faults are tracked separately. Only validated requests enter the estimate.
        if output[0] == "exact":
            self.keys.add((mapping, start, horizon))
        self.count += 1
        if self.count == BLOCK_SIZE:
            mode = "verified" if BLOCK_SIZE - len(self.keys) >= 116 else "orbit"
            if mode != engine.arm:
                self.activations += mode == "verified"
                self.reversions += mode == "orbit"
                self.engine = trial.Run(mode)
            self.keys.clear()
            self.count = 0
        return output


def cohort(mapping, profile):
    n = len(mapping)
    for phase, kind in enumerate(profile):
        for i in range(512):
            k = (i % 8) + 512 * phase if kind == "H" else i + 512 * phase
            yield mapping, k % n, 100 - k // n


def checks():
    runner = Policy()
    mapping = TABLES[0]
    for _ in range(BLOCK_SIZE):
        runner.solve(mapping, 0, 80)
    assert runner.activations == 1
    answer = ("exact", trial.binary(mapping, 0, 80))
    assert runner.solve(mapping, 0, 80) == answer
    assert runner.solve(mapping, 0, 80, "offline") == ("unavailable", None)
    assert runner.solve(mapping, 0, 80) == answer


def compare(mapping, profile):
    rows = list(cohort(mapping, profile))
    true = [("exact", trial.binary(*row)) for row in rows]
    stats = {arm: [] for arm in ARMS}
    for rep in range(5):
        for arm in (ARMS if rep % 2 == 0 else ARMS[::-1]):
            tick = perf_counter_ns()
            runner = Policy() if arm == "adaptive" else trial.Run(arm)
            out = [runner.solve(*row) for row in rows]
            elapsed = perf_counter_ns() - tick
            stats[arm].append(dict(ns=elapsed, errors=sum(x != y for x, y in zip(out, true)),
                                   calls=runner.calls, hits=runner.hits,
                                   activations=getattr(runner, "activations", 0),
                                   reversions=getattr(runner, "reversions", 0),
                                   clears=getattr(runner, "clears", 0)))
    return {arm: dict(data[0], ns=median(r["ns"] for r in data),
                      errors=max(r["errors"] for r in data)) for arm, data in stats.items()}


def main():
    start = perf_counter_ns()
    checks()
    results = {str(len(mapping)): {profile: compare(mapping, profile) for profile in PROFILES}
               for mapping in TABLES}
    for data in results.values():
        assert data["LL"]["adaptive"]["activations"] == 0
        assert data["HL"]["adaptive"]["reversions"] == 1
        assert data["LH"]["adaptive"]["activations"] == 1
    print(json.dumps(dict(results=results, total_ns=perf_counter_ns() - start), indent=2))


if __name__ == "__main__":
    main()
