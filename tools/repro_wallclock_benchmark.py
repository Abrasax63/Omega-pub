"""Measure real wall-clock cost of strict, fast, adaptive on one Omega script.

Experimental microbenchmark. Cached values are checked against a precomputed
reference; adaptive 'review' is a full recomputation here, not free validation.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "02_MATHEMATIQUES/observabilite_temporelle/sources/verification_specialisation_unaire.py"


def execute():
    t = time.perf_counter_ns()
    p = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True,
                       text=True, check=False, timeout=30)
    elapsed = time.perf_counter_ns() - t
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout, elapsed


def benchmark(repetitions=3):
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    results = []
    for trial in range(repetitions):
        # Fixed reference: all strategies see the same unchanged/changed flags.
        baseline, setup_ns = execute()
        cases = [("unchanged", False), ("dependency-change", True),
                 ("unchanged-again", False)]
        for policy in ("strict", "fast", "adaptive"):
            cached = baseline
            spent = 0
            runs = 0
            wrong = 0
            for _, changed in cases:
                if policy == "strict" and changed:
                    cached, elapsed = execute()
                    spent += elapsed
                    runs += 1
                elif policy == "adaptive" and changed:
                    # Conservative verification by re-executing; no claimed saving.
                    candidate, elapsed = execute()
                    spent += elapsed
                    runs += 1
                    cached = candidate
                # The fast policy reuses without checking.
                wrong += cached != baseline
            results.append({"trial": trial, "policy": policy,
                            "execution_ns": spent, "executions": runs,
                            "observed_output_mismatches": wrong,
                            "baseline_setup_ns": setup_ns})
    return results


if __name__ == "__main__":
    print(json.dumps({"schema_version": 1, "kind": "real_wallclock_microbenchmark",
                      "records": benchmark()}, sort_keys=True))
