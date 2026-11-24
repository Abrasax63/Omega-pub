"""Exercise the exact solver behind a strict, isolated data contract."""
import importlib
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

pilot = importlib.import_module("040_selector_trial")


def guarded(solve, mapping, start, horizon):
    if (
        not isinstance(mapping, list) or not mapping
        or type(start) is not int or not 0 <= start < len(mapping)
        or type(horizon) is not int or not 0 <= horizon <= 100
        or any(type(value) is not int or not 0 <= value < len(mapping) for value in mapping)
    ):
        return "invalid", None
    try:
        state = solve(mapping, start, horizon)
    except OSError:
        return "unavailable", None
    if type(state) is not int or not 0 <= state < len(mapping):
        return "unavailable", None
    return "exact", state


def reference(solve, mapping, start, horizon):
    return "exact", solve(mapping, start, horizon)


def direct(case):
    state = case["start"]
    for _ in range(case["horizon"]):
        state = case["mapping"][state]
    return state


def one(arm, case):
    calls = 0

    def solve(mapping, start, horizon):
        nonlocal calls
        calls += 1
        if case["fault"] == "offline":
            raise OSError("supplier unavailable")
        if case["fault"] == "bad_reply":
            return True
        return pilot.apply_power(mapping, start, horizon)

    try:
        status, state = arm(solve, case["mapping"], case["start"], case["horizon"])
    except (OSError, TypeError, IndexError):
        status, state = "exception", None
    return status, state, calls


def measure(arm, cases, labels):
    times = []
    for _ in range(500):
        t = time.perf_counter_ns()
        rows = [one(arm, case) for case in cases]
        times.append(time.perf_counter_ns() - t)
    counts = Counter()
    for case, label, (status, state, calls) in zip(cases, labels, rows, strict=True):
        match = status == label and (label != "exact" or (type(state) is int and state == direct(case)))
        counts["correct"] += match
        counts["false_verdict"] += status == "exact" and not match
        counts["exception"] += status == "exception"
        counts["invalid_stopped_before_call"] += label == "invalid" and status == "invalid" and not calls
        counts["unavailable"] += status == "unavailable"
        counts["solver_calls"] += calls
    return dict(counts, median_ns=statistics.median(times))


if __name__ == "__main__":
    cases, labels = (json.loads(Path(f).read_text()) for f in sys.argv[1:])
    assert len(cases) == 14 and labels.count("exact") == 6
    result = {"reference": measure(reference, cases, labels),
              "candidate": measure(guarded, cases, labels)}
    assert one(guarded, cases[6]) == ("invalid", None, 0)
    assert one(guarded, cases[-1]) == ("unavailable", None, 1)
    print(json.dumps(result, indent=2))

