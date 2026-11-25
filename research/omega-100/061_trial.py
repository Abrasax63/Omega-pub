import importlib
import json
from pathlib import Path
from statistics import median
import subprocess
import sys
from time import perf_counter_ns

transport = importlib.import_module("060_trial")
engine = transport.prior.engine


class Registry:
    def __init__(self, mode):
        self.mode = mode
        self.current = {}
        self.decoder = transport.Session(False)

    def bind(self, name, wire, offline=False):
        if self.mode != "naive":
            self.current.pop(name, None)
        if offline:
            return "unavailable", None
        table = self.decoder.table(wire)
        if table is None:
            return "invalid", None
        if self.mode == "naive":
            self.current.setdefault(name, table)
        else:
            self.current[name] = wire if self.mode == "fresh" else table
        return "bound", None

    def solve(self, name, start, steps, offline=False):
        if offline or name not in self.current:
            return "unavailable", None
        current = self.current[name]
        table = self.decoder.table(current) if self.mode == "fresh" else current
        if (type(start) is not int or not 0 <= start < len(table)
                or type(steps) is not int or not 0 <= steps <= 100):
            return "invalid", None
        return "exact", engine.direct(table, start, steps)


FIRST = (
    ("bind", "t", "[1,2,0]"), ("solve", "t", 0, 1),
    ("bind", "peer", "[2,0,1]"), ("bind", "t", "[0,2,1]"),
    ("solve", "t", 0, 1), ("bind", "t", "[true,2,1]"),
    ("solve", "t", 0, 1), ("bind", "t", "[2,1,0]"),
    ("bind", "t", "[1,2,0]", True), ("solve", "t", 0, 1),
    ("solve", "peer", 0, 1), ("bind", "t", "[2,1,0]"),
    ("solve", "t", 0, 1, True), ("solve", "t", 0, 1),
    ("solve", "t", False, 1), ("solve", "t", 0, True),
)
FIRST_EXPECTED = [
    ("bound", None), ("exact", 1), ("bound", None), ("bound", None),
    ("exact", 0), ("invalid", None), ("unavailable", None), ("bound", None),
    ("unavailable", None), ("unavailable", None), ("exact", 2), ("bound", None),
    ("unavailable", None), ("exact", 2), ("invalid", None), ("invalid", None),
]
AFTER_RESTART = (
    ("solve", "t", 0, 1), ("solve", "peer", 0, 1),
    ("bind", "t", "[0,1,2]"), ("solve", "t", 0, 1),
)
AFTER_EXPECTED = [
    ("unavailable", None), ("unavailable", None), ("bound", None), ("exact", 0),
]


def run(mode, rows):
    p = Registry(mode)
    outcomes = [getattr(p, op)(*args) for op, *args in rows]
    return outcomes, p.decoder.scans


def child(mode, phase):
    data = FIRST if phase == "first" else AFTER_RESTART
    return run(mode, data)[0]


def start_child(phase):
    output = subprocess.check_output(
        [sys.executable, str(Path(__file__).resolve()), "--child", phase],
        text=True, timeout=10,
    )
    return [tuple(item) for item in json.loads(output)]


def errors(outcomes, expected):
    return sum(x != y for x, y in zip(outcomes, expected, strict=True))


def measure(n):
    rows, expected = [], []
    for change in range(8):
        table = tuple((i + change + 9) % n for i in range(n))
        rows.append(("bind", "t", json.dumps(table)))
        expected.append(("bound", None))
        for i in range(64):
            start, steps, offline = i % n, (3 * i) % 21, i % 29 == 0
            rows.append(("solve", "t", start, steps, offline))
            expected.append(("unavailable", None) if offline else
                            ("exact", engine.binary(table, start, steps)))
    series = {mode: [] for mode in ("fresh", "candidate")}
    for turn in range(7):
        for mode in (("fresh", "candidate") if turn % 2 == 0 else ("candidate", "fresh")):
            tick = perf_counter_ns()
            observed, scans = run(mode, rows)
            elapsed = perf_counter_ns() - tick
            series[mode].append((elapsed, errors(observed, expected), scans))
    return {mode: dict(median_ns=median(x[0] for x in stats),
                       errors=max(x[1] for x in stats), scans=stats[0][2])
            for mode, stats in series.items()}


def main():
    tick = perf_counter_ns()
    negative = errors(run("naive", FIRST)[0], FIRST_EXPECTED)
    assert negative > 0
    assert run("fresh", FIRST)[0] == FIRST_EXPECTED
    before, after = start_child("first"), start_child("restart")
    assert before == FIRST_EXPECTED and after == AFTER_EXPECTED
    results = {n: measure(n) for n in (67, 127)}
    assert all(row["candidate"]["errors"] == row["fresh"]["errors"] == 0
               for row in results.values())
    print(json.dumps(dict(negative=negative, candidate_controls=len(before)+len(after),
                          results=results, elapsed_ns=perf_counter_ns()-tick), indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        print(json.dumps(child("candidate", sys.argv[2])))
    else:
        main()
