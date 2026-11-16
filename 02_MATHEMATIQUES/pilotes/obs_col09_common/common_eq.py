#!/usr/bin/env python3
"""OBS-COL-09B: real AALpy L*, KV, L#, L#+P1, one shared EQ word suite.

The candidate equivalence *words* are fixed, independent of the learner and
target, and identical to the Java TTT words. Actual observations differ
when hypotheses diverge. NO full equivalence certificate is issued.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "obs_col09"
for p in (PARENT, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from aalpy.base import Oracle
from aalpy.learning_algs import run_Lstar, run_KV, run_Lsharp
from benchmark import FIXTURES, PhysicalCounter, external_fixture, evaluation_words
from generate_manifests import INPUTS, equivalence_words, read_words, encode, manifest_hash

ALGORITHMS = ("Lstar", "KV", "Lsharp", "Lsharp_P1")
MAX_RESETS, MAX_SYMBOLS = 10000, 50000


class SharedWordEquivalenceOracle(Oracle):
    """Bounded EQ: each round restarts the EXACT same published 512-word list.

    The first differing output prefix is returned as a counterexample.
    No hidden state count, perfect equivalence, or target graph access.
    """
    def __init__(self, alphabet, sul, words):
        super().__init__(alphabet, sul)
        self.words = tuple(words)
        self.rounds = 0
        self.found_counterexamples = 0
        self.completed_suites = 0
        self.proposed_words = 0

    def find_cex(self, hypothesis):
        self.rounds += 1
        for word in self.words:
            self.reset_hyp_and_sul(hypothesis)
            self.proposed_words += 1
            for k, symbol in enumerate(word):
                actual = self.sul.step(symbol)
                predicted = hypothesis.step(symbol)
                self.num_steps += 1
                if actual != predicted:
                    self.sul.post()
                    self.found_counterexamples += 1
                    return tuple(word[:k + 1])
            self.sul.post()
        self.completed_suites += 1
        return None


def run_method(index, name, blob, algorithm, manifest_dir, *, oracle_factory=SharedWordEquivalenceOracle):
    target, provenance = external_fixture(name, blob)
    alphabet = sorted(target.get_input_alphabet(), key=str)
    alphabet_as_text = tuple(map(str, alphabet))
    if INPUTS[index] != (name, alphabet_as_text):
        raise AssertionError("unexpected third-party alphabet")
    words, eq_sha = read_words(
        Path(manifest_dir) / (name + ".eq.words"),
        equivalence_words(alphabet_as_text, index),
    )
    mapping = {str(sym): sym for sym in alphabet}
    if len(mapping) != len(alphabet):
        raise AssertionError("non-injective alphabet normalization")
    oracle_words = [tuple(mapping[x] for x in word) for word in words]

    physical = PhysicalCounter(target, use_p1=(algorithm == "Lsharp_P1"))
    eq = oracle_factory(alphabet, physical, oracle_words)
    learner = {"Lstar": run_Lstar, "KV": run_KV,
               "Lsharp": run_Lsharp, "Lsharp_P1": run_Lsharp}[algorithm]

    cpu_start = time.process_time()
    wall_start = time.perf_counter()
    learned, info = learner(
        alphabet, physical, eq, automaton_type="moore",
        max_learning_rounds=40, cache_and_non_det_check=False,
        return_data=True, print_level=0,
    )
    cpu = time.process_time() - cpu_start
    wall = time.perf_counter() - wall_start
    if physical.physical_symbols > MAX_SYMBOLS or physical.physical_resets > MAX_RESETS:
        raise AssertionError("physical budget exceeded")

    # Read common test words only AFTER the model has been frozen.
    expected = [tuple(map(str, w)) for w in evaluation_words(alphabet, index)]
    eval_words, eval_sha = read_words(
        Path(manifest_dir) / (name + ".words"), expected)
    errors = 0
    unseen = 0
    unseen_errors = 0
    for word in eval_words:
        physical_word = tuple(mapping[x] for x in word)
        ground_truth = target.execute_sequence(target.initial_state, physical_word)[-1]
        prediction = learned.execute_sequence(learned.initial_state, physical_word)[-1]
        error = ground_truth != prediction
        errors += bool(error)
        if physical_word not in physical.observed_prefixes:
            unseen += 1
            unseen_errors += bool(error)

    return {
        "fixture": name,
        "origin": provenance["source_url"],
        "algorithm": algorithm,
        "eq_manifest_sha256": eq_sha,
        "evaluation_manifest_sha256": eval_sha,
        "proposed_eq_words_per_round": len(oracle_words),
        "completed_eq_suites": eq.completed_suites,
        "eq_rounds": eq.rounds,
        "eq_candidates_executed": eq.proposed_words,
        "eq_counterexamples": eq.found_counterexamples,
        "eq_order_sha256": getattr(eq, "order_digest", lambda: None)(),
        "eq_first_proposals": getattr(eq, "first_proposals", []),
        "eq_policy": getattr(eq, "policy", "fixed"),
        "source_states_posthoc_only": len(target.states),
        "learned_states": len(learned.states),
        "physical_resets": physical.physical_resets,
        "physical_symbols": physical.physical_symbols,
        "physical_trace_sha256": physical.fingerprint(),
        "p1_calls": physical.p1_calls,
        "cpu_seconds": round(cpu, 6),
        "wall_seconds": round(wall, 6),
        "library_counters": info,
        "evaluation_count": len(eval_words),
        "evaluation_errors_all": errors,
        "evaluation_unseen_count": unseen,
        "evaluation_unseen_errors": unseen_errors,
        "status": "NO_CEX_IN_BOUNDED_SUITE" if eq.completed_suites else "NOT_CONVERGED_IN_BOUNDED_SUITE",
        "equivalence_certified": False,
        "omega_gains_demonstrated": False,
    }


def run(manifest_dir):
    if importlib.metadata.version("aalpy") != "2.0.0":
        raise AssertionError("AALpy==2.0.0 is required")
    results = [
        run_method(i, name, sha, algorithm, manifest_dir)
        for i, (name, sha) in enumerate(FIXTURES)
        for algorithm in ALGORITHMS
    ]
    for name, _ in FIXTURES:
        a = next(x for x in results if x["fixture"] == name and x["algorithm"] == "Lsharp")
        b = next(x for x in results if x["fixture"] == name and x["algorithm"] == "Lsharp_P1")
        for key in ("learned_states", "physical_resets", "physical_symbols",
                    "physical_trace_sha256", "eq_rounds",
                    "eq_candidates_executed", "eq_counterexamples",
                    "evaluation_unseen_count", "evaluation_unseen_errors"):
            if a[key] != b[key]:
                raise AssertionError(f"L# / Omega P1 mismatch: {name}:{key}")
        if a["p1_calls"] != 0 or b["p1_calls"] != b["physical_resets"]:
            raise AssertionError("P1 calls not accounted")
    return {
        "protocol": "OBS-COL-09B",
        "mode": "COMMON_DETERMINISTIC_EQ_WORD_MANIFEST",
        "preregistration": "94d2233166d3a6013a94287fce2975bab41132e4",
        "models_external_public_not_blind": True,
        "p1_selects_probes": False,
        "not_a_true_equivalence_oracle": True,
        "algorithms": list(ALGORITHMS),
        "results": results,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: common_eq.py <manifest-dir>")
    print(json.dumps(run(sys.argv[1]), indent=2, ensure_ascii=False, default=str))
