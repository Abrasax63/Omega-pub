"""Compare isolated pairs with and without the solver's data contract."""
import importlib
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

router = importlib.import_module("045_trial")
solver = importlib.import_module("046_trial")


def pair(case, arm):
    route = router.route(case["question"])
    if route is None:
        return "abstain", None, 0
    fault = case["fault"]
    return solver.one(arm, dict(mapping=case["mapping"], start=route[0], horizon=route[1],
                                fault="bad_reply" if fault == "wrong-response" else fault))


def expected(case, label):
    if label[0] != "exact":
        return label[0], None
    state = label[1]
    for _ in range(label[2]):
        state = case["mapping"][state]
    return "exact", state


def measure(cases, labels, arm):
    timings = []
    for _ in range(500):
        start = time.perf_counter_ns()
        rows = [pair(c, arm) for c in cases]
        timings.append(time.perf_counter_ns()-start)
    result = Counter()
    for case, label, (status, value, calls) in zip(cases, labels, rows, strict=True):
        target = expected(case, label)
        correct = (status, value) == target and (status != "exact" or type(value) is int)
        result["correct"] += correct
        result["false_results"] += status == "exact" and not correct
        result["exceptions"] += status == "exception"
        result["invalid_calls"] += calls if label[0] == "invalid" else 0
        result["ambiguous_calls"] += calls if label[0] == "abstain" else 0
        result["unavailable"] += status == "unavailable"
    return dict(result, median_ns=statistics.median(timings))


if __name__ == "__main__":
    cases, labels = (json.loads(Path(f).read_text()) for f in sys.argv[1:])
    t = time.perf_counter_ns()
    report = {"reference": measure(cases, labels, solver.reference),
              "candidate": measure(cases, labels, solver.guarded)}
    report["elapsed_ns"] = time.perf_counter_ns()-t
    print(json.dumps(report, indent=2))

