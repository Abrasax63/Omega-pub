"""Compare real execution cost vs metadata gate on an unchanged script.

This measures the gate, not independent scientific review or disk cache IO.
"""
import json
import statistics
import time
from tools.repro_targeted_gate import eligible_for_reuse, snapshot
from tools.repro_wallclock_benchmark import SCRIPT, execute


def measure(repetitions=7):
    times = {"recompute_ns": [], "gate_ns": []}
    baseline, _ = execute()
    saved = snapshot(SCRIPT)
    for _ in range(repetitions):
        t = time.perf_counter_ns()
        allowed = eligible_for_reuse(saved, snapshot(SCRIPT), True)
        times["gate_ns"].append(time.perf_counter_ns() - t)
        assert allowed
        result, elapsed = execute()
        times["recompute_ns"].append(elapsed)
        assert result == baseline
    return {
        "kind": "same_environment_gate_microbenchmark",
        "repetitions": repetitions,
        "review_status": "test-fixture-only",
        "median_gate_ns": int(statistics.median(times["gate_ns"])),
        "median_recompute_ns": int(statistics.median(times["recompute_ns"])),
        "raw_ns": times,
    }


if __name__ == "__main__":
    print(json.dumps(measure(), sort_keys=True))
