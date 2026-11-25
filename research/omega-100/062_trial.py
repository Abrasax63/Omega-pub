"""Compare bounded registries under controlled concurrent replacement."""

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import importlib
import json
from statistics import median
from threading import Event, Lock
from time import perf_counter_ns, sleep

prior = importlib.import_module("061_trial")
CAPACITY = 2


class Registry:
    def __init__(self, mode, solver):
        self.mode = mode
        self.solver = solver
        self.current = OrderedDict()
        self.lock = Lock()

    def bind(self, name, wire):
        with self.lock:
            self.current.pop(name, None)
            table = prior.transport.Session(False).table(wire)
            if table is None:
                return "invalid", None
            if len(self.current) == CAPACITY:
                self.current.popitem(last=False)
            # A separate object identifies every incarnation of a table.
            self.current[name] = (table,)
            return "bound", None

    def compute(self, entry, state, horizon):
        if entry is None:
            return "unavailable", None
        table, = entry
        if (type(state) is not int or not 0 <= state < len(table)
                or type(horizon) is not int or not 0 <= horizon <= 100):
            return "invalid", None
        try:
            result = self.solver(table, state, horizon)
        except OSError:
            return "unavailable", None
        if type(result) is not int or not 0 <= result < len(table):
            return "unavailable", None
        return "exact", result

    def solve(self, name, state, horizon):
        with self.lock:
            entry = self.current.get(name)
            if self.mode == "global":
                return self.compute(entry, state, horizon)
        result = self.compute(entry, state, horizon)
        if self.mode == "snapshot" and entry is not None:
            with self.lock:
                if self.current.get(name) is not entry:
                    return "stale", None
        return result


def forced(mode, changes):
    started, proceed = Event(), Event()

    def paused(table, state, horizon):
        started.set()
        if not proceed.wait(5):
            raise TimeoutError("solver did not resume")
        return prior.engine.direct(table, state, horizon)

    registry = Registry(mode, paused)
    assert registry.bind("target", "[1,2,0]") == ("bound", None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = pool.submit(registry.solve, "target", 0, 1)
        try:
            assert started.wait(5)
            for name, wire, expected in changes:
                assert pool.submit(registry.bind, name, wire).result(timeout=5) == (expected, None)
        finally:
            proceed.set()
        observed = result.result(timeout=5)
    return observed, registry.solve("target", 0, 1), len(registry.current)


def controls():
    replace = (("target", "[2,0,1]", "bound"),)
    assert forced("naive", replace)[:2] == (("exact", 1), ("exact", 2))
    cases = {
        "replacement": (replace, ("stale", None), ("exact", 2), 1),
        "same_content_after_eviction": (
            (("other", "[0]", "bound"), ("third", "[0]", "bound"),
             ("target", "[1,2,0]", "bound")),
            ("stale", None), ("exact", 1), 2,
        ),
        "failed_replacement": (
            (("target", "[true,2,0]", "invalid"),),
            ("stale", None), ("unavailable", None), 0,
        ),
        "independent_replacement": (
            (("other", "[0]", "bound"), ("other", "[1,0]", "bound")),
            ("exact", 1), ("exact", 1), 2,
        ),
    }
    for changes, observed, following, size in cases.values():
        assert forced("snapshot", changes) == (observed, following, size)

    def outage(*_):
        raise OSError("simulated solver failure")

    pilot = Registry("snapshot", outage)
    assert pilot.bind("target", "[1,0]") == ("bound", None)
    assert pilot.solve("target", 0, 1) == ("unavailable", None)
    assert pilot.solve("target", False, 1) == ("invalid", None)
    return {"naive_stale_values": 1, "candidate_stale_abstentions": 3,
            "candidate_forced_cases": len(cases), "capacity": CAPACITY}


def one(mode, delay):
    table = tuple((i + 7) % 79 for i in range(79))

    def solver(mapping, state, horizon):
        if delay:
            sleep(delay)
        return prior.engine.direct(mapping, state, horizon)

    pilot = Registry(mode, solver)
    assert pilot.bind("target", json.dumps(table)) == ("bound", None)
    binds = []
    jobs, observed = [], []

    def timed_bind(i):
        tick = perf_counter_ns()
        status = pilot.bind("other", "[0]" if i % 2 else "[1,0]")
        return status, perf_counter_ns() - tick

    with ThreadPoolExecutor(max_workers=4) as pool:
        tick = perf_counter_ns()
        for i in range(128):
            if i % 16 == 8:
                jobs.append(("bind", pool.submit(timed_bind, i // 16)))
            state, horizon = i % len(table), i % 23
            jobs.append(("solve", pool.submit(pilot.solve, "target", state, horizon)))
        for op, job in jobs:
            if op == "bind":
                status, duration = job.result(timeout=5)
                assert status == ("bound", None)
                binds.append(duration)
            else:
                observed.append(job.result(timeout=5))
        elapsed = perf_counter_ns() - tick
    expected = [("exact", prior.engine.binary(table, i % len(table), i % 23))
                for i in range(128)]
    return elapsed, binds, prior.errors(observed, expected)


def benchmark(delay):
    samples = {"global": [], "snapshot": []}
    for repeat in range(7):
        order = ("global", "snapshot") if repeat % 2 == 0 else ("snapshot", "global")
        for mode in order:
            samples[mode].append(one(mode, delay))
    results = {}
    for mode, arms in samples.items():
        durations = sorted(value for _, binds, _ in arms for value in binds)
        p95 = durations[(95 * len(durations) + 99) // 100 - 1]
        results[mode] = dict(median_ns=median(a[0] for a in arms), bind_p95_ns=p95,
                             errors=sum(a[2] for a in arms))
    return results


if __name__ == "__main__":
    start = perf_counter_ns()
    proof = controls()
    results = {name: benchmark(delay) for name, delay in (("direct", 0), ("wait_1ms", 0.001))}
    print(json.dumps(dict(controls=proof, results=results, elapsed_ns=perf_counter_ns()-start),
                     indent=2))
