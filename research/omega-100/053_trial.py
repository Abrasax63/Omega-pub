import importlib
import json
from statistics import median
from time import perf_counter_ns

previous = importlib.import_module("052_trial")
trial = previous.trial
ARMS = ("previous", "sampled", "orbit")


class Window:
    def __init__(self):
        self.total = self.valid = 0
        self.keys = set()

    def track(self, key, status):
        if self.total % 4 == 0 and status == "exact":
            self.valid += 1
            self.keys.add(key)
        self.total += 1
        if self.total != 128:
            return None
        enable = self.valid >= 24 and 10 * (self.valid - len(self.keys)) >= 9 * self.valid
        self.total = self.valid = 0
        self.keys.clear()
        return enable


class Policy:
    def __init__(self):
        self.engine = trial.Run("orbit")
        self.window = Window()
        self.activations = self.reversions = self.hits = self.calls = 0

    def solve(self, mapping, start, horizon, fault):
        engine = self.engine
        if len(engine.cache) >= 128:
            engine.cache.clear()
        calls, hits = engine.calls, engine.hits
        result = engine.solve(mapping, start, horizon, fault)
        self.calls += engine.calls - calls
        self.hits += engine.hits - hits
        enable = self.window.track((mapping, start, horizon), result[0])
        if enable is not None and enable != (engine.arm == "verified"):
            self.activations += enable
            self.reversions += not enable
            self.engine = trial.Run("verified" if enable else "orbit")
        return result


def rows(profile):
    n = 23 if profile == "sparse" else 19
    mapping = tuple((i * 3 + 2) % n for i in range(n))
    if profile == "invalid":
        mapping = (n,) + mapping[1:]
    for i in range(512):
        k = i % 2 if profile == "dense" else i
        fault = "offline" if profile == "offline" or profile in ("dense", "sparse") and i % 16 == 0 else "ok"
        yield mapping, k % n, 100 - k // n, fault


def independent(row):
    mapping, start, horizon, fault = row
    if mapping[0] >= len(mapping):
        return "invalid", None
    if fault == "offline":
        return "unavailable", None
    return "exact", trial.binary(mapping, start, horizon)


def measure(profile):
    inputs = list(rows(profile))
    expected = [independent(row) for row in inputs]
    results = {arm: [] for arm in ARMS}
    for rep in range(5):
        for arm in (ARMS if rep % 2 == 0 else ARMS[::-1]):
            start = perf_counter_ns()
            runner = previous.Policy() if arm == "previous" else Policy() if arm == "sampled" else trial.Run("orbit")
            out = [runner.solve(*row) for row in inputs]
            ns = perf_counter_ns()-start
            results[arm].append(dict(ns=ns, errors=sum(a != b for a,b in zip(out, expected, strict=True)),
                                     activations=getattr(runner, "activations", 0),
                                     unavailable=sum(x[0] == "unavailable" for x in out),
                                     invalid=sum(x[0] == "invalid" for x in out),
                                     calls=runner.calls, hits=runner.hits))
    return {arm: dict(data[0], ns=median(r["ns"] for r in data), errors=max(r["errors"] for r in data))
            for arm, data in results.items()}


def main():
    start = perf_counter_ns()
    results = {p: measure(p) for p in ("offline", "invalid", "dense", "sparse")}
    for profile in ("offline", "invalid"):
        assert results[profile]["previous"]["activations"] == 1
        assert results[profile]["sampled"]["activations"] == 0
    assert results["dense"]["sampled"]["activations"] == 1
    assert results["sparse"]["sampled"]["activations"] == 0
    print(json.dumps(dict(results=results, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
