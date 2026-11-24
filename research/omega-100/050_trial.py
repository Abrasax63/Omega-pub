import importlib
import json
from pathlib import Path
from statistics import median
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter_ns

pilots = importlib.import_module("046_trial")
ARMS = ("direct", "binary", "ablated", "retained")


def direct(mapping, state, horizon):
    for _ in range(horizon):
        state = mapping[state]
    return state


def orbit(mapping, state, horizon):
    history = []
    first = {}
    while state not in first:
        first[state] = len(history)
        history.append(state)
        state = mapping[state]
    if horizon < len(history):
        return history[horizon]
    head = first[state]
    return history[head + (horizon - head) % (len(history) - head)]


def propose(path):
    start = perf_counter_ns()
    mapping = (1, 2, 3, 4, 0)
    requests = [(mapping, i % 4, 98) for i in range(100)]
    duplicates = len(requests) - len(set(requests))
    policy = {"version": 1, "enable": 2 * duplicates >= len(requests)}
    path.write_text(json.dumps(policy))
    return duplicates, perf_counter_ns() - start


def reserve():
    mapping = (1, 1, 4, 2, 5, 7, 0, 9, 0, 10, 12, 8, 6)
    swapped = (0,) + mapping[1:]
    # Adversaries first. Warm the key, then change the table and disable the solver.
    rows = [(mapping, 0, 100, "ok"), (swapped, 0, 100, "ok"),
            (mapping, 0, 100, "offline"), ((13,) + mapping[1:], 0, 100, "ok")]
    rows += [(mapping, i % 5, 95 + i % 6, "ok") for i in range(900)]
    rows += [(mapping, i % 13, 100 - i // 13, "ok") for i in range(300)]
    return rows


def worker(arm, path):
    start = perf_counter_ns()
    enabled = arm == "retained" and json.loads(path.read_text()) == {"version": 1, "enable": True}
    solver = pilots.pilot.apply_power if arm == "binary" else direct
    cache = {}
    calls = hits = 0

    def solve(values, state, horizon):
        nonlocal calls, hits
        if fault == "offline":
            raise OSError("disabled solver")
        if enabled:
            key = original, state, horizon
            if key in cache:
                hits += 1
                return cache[key]
        calls += 1
        value = solver(values, state, horizon)
        if enabled:
            cache[key] = value
        return value

    rows = []
    for original, state, horizon, fault in reserve():
        result = pilots.guarded(solve, list(original), state, horizon)
        label = (("unavailable", None) if fault == "offline" else ("invalid", None)
                 if any(v >= len(original) for v in original)
                 else ("exact", orbit(original, state, horizon)))
        rows.append((result, label))
    return dict(rows=len(rows), errors=sum(x != y for x, y in rows), solver_calls=calls,
                cache_hits=hits, unavailable=sum(x[0] == "unavailable" for x, _ in rows),
                invalid=sum(x[0] == "invalid" for x, _ in rows),
                local_ns=perf_counter_ns()-start)


def main():
    if len(sys.argv) == 3:
        print(json.dumps(worker(sys.argv[1], Path(sys.argv[2]))))
        return
    t = perf_counter_ns()
    with TemporaryDirectory() as temp:
        path = Path(temp) / "policy.json"
        duplicates, training_ns = propose(path)
        measurements = {arm: [] for arm in ARMS}
        for rep in range(5):
            ordered = ARMS if rep % 2 == 0 else ARMS[::-1]
            for arm in ordered:
                start = perf_counter_ns()
                completed = subprocess.run([sys.executable, __file__, arm, str(path)],
                                           check=True, capture_output=True, text=True, timeout=4)
                wall = perf_counter_ns() - start
                measurements[arm].append(dict(json.loads(completed.stdout), wall_ns=wall))
    summary = {arm: dict(rows=records[0]["rows"], errors=max(r["errors"] for r in records),
                         solver_calls=records[0]["solver_calls"], cache_hits=records[0]["cache_hits"],
                         unavailable=records[0]["unavailable"], invalid=records[0]["invalid"],
                         median_local_ns=median(r["local_ns"] for r in records),
                         median_wall_ns=median(r["wall_ns"] for r in records))
               for arm, records in measurements.items()}
    print(json.dumps(dict(training_duplicates=duplicates, training_ns=training_ns, arms=summary,
                          elapsed_ns=perf_counter_ns()-t), indent=2))


if __name__ == "__main__":
    main()
