#!/usr/bin/env python3
"""Post-result exact product-automaton BFS audit, NOT a new fit policy.

This finite-state proof/evaluator is only called AFTER the experiment
reported by run #43822021430. It cannot affect selection, training, the
original test answers, or modify code/policies. It also guards against
a supposedly identical rerun changing any previously archived costs.
"""
from __future__ import annotations

from collections import deque
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from external_transfer import load_pinned_moore, fit_one

ARMS = ("fixed", "coverage_only", "omega_candidate", "Lstar", "KV")


def exact_equivalence_or_counterexample(source, learned):
    """BFS in the product of two deterministic complete Moore machines.

    A mismatch at product pair reached by w certifies different outputs.
    If BFS visits every reachable pair without mismatch, induction on
    word length proves equality for ALL finite input histories.
    """
    alphabet = tuple(sorted(source.get_input_alphabet(), key=str))
    if alphabet != tuple(sorted(learned.get_input_alphabet(), key=str)):
        raise ValueError("different input alphabet")
    start = (source.initial_state, learned.initial_state)
    queue = deque([(start[0], start[1], ())])
    seen = {(start[0], start[1])}
    while queue:
        x, y, word = queue.popleft()
        if x.output != y.output:
            return {
                "status": "EXACT_COUNTEREXAMPLE",
                "shortest_word": list(word),
                "shortest_length": len(word),
                "target_output": x.output,
                "learned_output": y.output,
                "visited_product_states": len(seen),
                "product_upper_bound": len(source.states) * len(learned.states),
            }
        for symbol in alphabet:
            next_pair = (x.transitions[symbol], y.transitions[symbol])
            if next_pair not in seen:
                seen.add(next_pair)
                queue.append((next_pair[0], next_pair[1], word + (symbol,)))
    return {
        "status": "EXACT_EQUIVALENT_FINITE_MOORE",
        "shortest_word": None,
        "shortest_length": None,
        "visited_product_states": len(seen),
        "product_upper_bound": len(source.states) * len(learned.states),
    }


def run(directory):
    folder = Path(directory)
    expected = json.loads((HERE / "FROZEN_FIRST_RUN.json").read_text())["models"]
    hashes = json.loads((HERE / "SOURCE_SHA_LOCK.json").read_text())["sha256"]
    results = []
    for name, previous in expected.items():
        result = {"model": name, "cases": {}}
        for arm in ARMS:
            original_target, _ = load_pinned_moore(folder / name, hashes[name])
            learned, metrics = fit_one(original_target, arm, name, list(hashes).index(name))
            locked_resets, locked_symbols, locked_states, locked_error_count = previous[arm]
            # Original error count was measured in the reserved set; we
            # deliberately do not open that set again for this exact audit.
            if (metrics["physical_resets"], metrics["physical_symbols"],
                    metrics["learned_states"]) != (
                    locked_resets, locked_symbols, locked_states):
                raise AssertionError("posthoc replay drifted from frozen first run: " + name + " " + arm)
            if metrics["status"] != "FIT_FINISHED":
                result["cases"][arm] = {"status": "INDETERMINATE_FIT",
                                        "reproduced_training_costs": True}
                continue
            # Exact evaluator may see the original target graph ONLY here.
            exact = exact_equivalence_or_counterexample(original_target, learned)
            exact.update({
                "reproduced_training_costs": True,
                "source_sha256": hashes[name],
                "original_heldout_errors": locked_error_count,
                "physical_resets": locked_resets,
                "physical_symbols": locked_symbols,
                "learned_states": locked_states,
                "not_seen_by_policy": True,
            })
            result["cases"][arm] = exact
        results.append(result)
    return {
        "protocol": "OBS-COL-11-POSTHOC-EXACT",
        "amendment_commit": "e60964303b7de24b0721296f8e061cf0c79a8e9e",
        "original_run": 43822021430,
        "posthoc_not_preregistered_in_initial_trial": True,
        "no_policy_or_training_changes": True,
        "comparison_type": "complete finite Moore product graph BFS",
        "not_novel_scientific_theorem": True,
        "models": results,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_exact_equivalence.py source_dir")
    print(json.dumps(run(sys.argv[1]), indent=2, ensure_ascii=False))
