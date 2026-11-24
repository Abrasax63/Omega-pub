"""Move semantic bounds from grammar routing to the guarded solver."""
import importlib
import json
import sys
import time
from pathlib import Path

previous = importlib.import_module("047_trial")
solver = previous.solver
router = previous.router


def parse(text):
    for pattern, groups in (*router.prior.PATTERNS, *router.PATTERNS):
        match = pattern.fullmatch(text)
        if match:
            try:
                return tuple(router.prior.integer(match[group]) for group in groups)
            except ValueError:
                return None
    return None


def candidate(case, arm):
    route = parse(case["question"])
    if route is None:
        return "abstain", None, 0
    return solver.one(arm, dict(mapping=case["mapping"], start=route[0], horizon=route[1],
                                fault=case["fault"]))


if __name__ == "__main__":
    cases, labels = (json.loads(Path(f).read_text()) for f in sys.argv[1:])
    t = time.perf_counter_ns()
    reference = previous.measure(cases, labels, solver.guarded)
    previous.pair = candidate
    report = previous.measure(cases, labels, solver.guarded)
    assert candidate(cases[7], solver.guarded) == ("invalid", None, 0)
    assert candidate(cases[11], solver.guarded) == ("unavailable", None, 1)
    print(json.dumps(dict(reference=reference, candidate=report, elapsed_ns=time.perf_counter_ns()-t), indent=2))

