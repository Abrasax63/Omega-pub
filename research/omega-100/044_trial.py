"""Validate literal numeric spans against their role in the lexical contract."""
import importlib
import json
import statistics
import sys
import time
from pathlib import Path

lexical = importlib.import_module("043_trial")


def literal(case):
    question, route, spans = (case[key] for key in ("question", "route", "spans"))
    if not lexical.previous.valid(route, 6) or len(spans) != 2:
        return False
    for (start, end), value in zip(spans, route, strict=True):
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(question):
            return False
        try:
            if lexical.integer(question[start:end]) != value:
                return False
        except (ValueError, KeyError):
            return False
    return True


def role_bound(case):
    if not literal(case):
        return False
    for pattern, groups in lexical.PATTERNS:
        match = pattern.fullmatch(case["question"])
        if match:
            return tuple(map(tuple, case["spans"])) == tuple(match.span(group) for group in groups)
    return False


def measure(check, cases, expected):
    times = []
    for _ in range(500):
        start = time.perf_counter_ns()
        accepted = [check(case) for case in cases]
        times.append(time.perf_counter_ns() - start)
    tp = sum(a and b for a, b in zip(accepted, expected, strict=True))
    fp = sum(a and not b for a, b in zip(accepted, expected, strict=True))
    return dict(tp=tp, fp=fp, fn=sum(expected) - tp, tn=len(expected) - sum(expected) - fp,
                median_ns=statistics.median(times))


if __name__ == "__main__":
    cases, expected = (json.loads(Path(p).read_text()) for p in sys.argv[1:])
    results = {"reference": measure(literal, cases, expected),
               "candidate": measure(role_bound, cases, expected)}
    assert role_bound(cases[2])
    assert not role_bound(cases[5])
    assert not role_bound(cases[6])
    print(json.dumps(results, indent=2))

