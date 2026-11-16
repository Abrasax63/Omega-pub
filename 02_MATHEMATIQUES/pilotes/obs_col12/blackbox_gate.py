#!/usr/bin/env python3
"""OBS-COL-12: measured black-box conformity gate AFTER frozen learning.

Real AALpy W and Wp as baselines; Wp memory-ranked arm reuses AALpy Wp's
EXACT first/second-phase test generator with a different order, selected by
the unchanged OBS-COL-10 coverage_ranking heuristic. Target internals are
only available to the separate replay and POST-HOC evaluator, not selectors.

This is CALIBRATION on previously disclosed Radboud registers, not a
prospective private holdout or a theorem about Omega intelligence.
"""
from __future__ import annotations

from collections import OrderedDict
from itertools import chain
from pathlib import Path
import hashlib
import json
import sys
import time

from aalpy.oracles import WMethodEqOracle, WpMethodEqOracle
from aalpy.oracles.WpMethodEqOracle import first_phase_it, second_phase_it

HERE = Path(__file__).resolve().parent
for p in (HERE.parent / "obs_col11", HERE.parent / "obs_col10",
          HERE.parent / "obs_col09"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from external_transfer import load_pinned_moore, fit_one
from policy_divergence import coverage_ranking
from benchmark import PhysicalCounter

SOURCE_NAMES = ("register3.dot", "register5.dot")
FROZEN_ARMS = {
    "register3.dot": ("fixed", "omega_candidate"),
    "register5.dot": ("fixed", "coverage_only", "omega_candidate", "KV"),
}
VERIFIERS = ("W", "Wp", "Wp_coverage_ranked", "Wp_memory_ranked")
RESET_BUDGET = 600
SYMBOL_BUDGET = 8000


class VerificationBudgetExceeded(Exception):
    pass


class MeteredBlackBox:
    """Physical oracle wrapper. The gate cannot read delegate target graph."""
    def __init__(self, target, *, with_p1=False, max_resets=RESET_BUDGET,
                 max_symbols=SYMBOL_BUDGET):
        self._counter = PhysicalCounter(target, use_p1=with_p1)
        self.max_resets, self.max_symbols = max_resets, max_symbols

    def pre(self):
        if self._counter.physical_resets >= self.max_resets:
            raise VerificationBudgetExceeded("verifier reset limit reached")
        self._counter.pre()

    def step(self, action):
        if self._counter.physical_symbols >= self.max_symbols:
            raise VerificationBudgetExceeded("verifier symbol limit reached")
        return self._counter.step(action)

    def post(self):
        self._counter.post()

    @property
    def physical_resets(self):
        return self._counter.physical_resets

    @property
    def physical_symbols(self):
        return self._counter.physical_symbols

    @property
    def p1_calls(self):
        return self._counter.p1_calls


def wp_candidate_suite(hypothesis, alphabet, extra_states=1):
    """Use authentic AALpy Wp generators. Dedup exactly as native Wp cache."""
    if not hypothesis.characterization_set:
        hypothesis.characterization_set = hypothesis.compute_characterization_set()
    state_cover = list(dict.fromkeys(s.prefix for s in hypothesis.states))
    state_cover_set = set(state_cover)
    transition_cover = list(dict.fromkeys(
        s.prefix + (a,) for s in hypothesis.states for a in alphabet
    ))
    difference = [w for w in transition_cover if w not in state_cover_set]
    # n+1 bound was frozen BEFORE this diagnostic; NOT the true size.
    depth = extra_states + 1
    sequences = chain(
        first_phase_it(alphabet, state_cover, depth, hypothesis.characterization_set),
        second_phase_it(hypothesis, alphabet, difference, depth),
    )
    return tuple(dict.fromkeys(sequences))


def ranked_wp_gate(hypothesis, sul, alphabet, previously_measured_prefixes, *, use_memory):
    """Execute fixed Wp candidate set in precommitted classical memory ranking."""
    words = wp_candidate_suite(hypothesis, alphabet)
    source_digest = hashlib.sha256(
        json.dumps([list(w) for w in words], separators=(",", ":")).encode()
    ).hexdigest()
    ranked = coverage_ranking(
        hypothesis, words,
        known_prefixes=previously_measured_prefixes,
        memory=use_memory,
    )
    if len(words) != len(ranked) or set(ranked) != set(words):
        raise AssertionError("ranking dropped/added Wp candidate words")
    order_digest = hashlib.sha256(
        json.dumps([list(w) for w in ranked], separators=(",", ":")).encode()
    ).hexdigest()
    actual_tests = 0
    for word in ranked:
        hypothesis.reset_to_initial()
        sul.pre()
        actual_tests += 1
        for i, action in enumerate(word):
            measured = sul.step(action)
            predicted = hypothesis.step(action)
            if measured != predicted:
                sul.post()
                return tuple(word[:i + 1]), {
                    "candidate_count": len(words), "tested": actual_tests,
                    "wp_candidate_sha256": source_digest,
                    "ordered_sha256": order_digest,
                    "reordered": ranked != words,
                    "memory_component": use_memory,
                }
        sul.post()
    return None, {
        "candidate_count": len(words), "tested": actual_tests,
        "wp_candidate_sha256": source_digest,
        "ordered_sha256": order_digest,
        "reordered": ranked != words,
        "memory_component": use_memory,
    }


def run_gate(hypothesis, oracle_target, verifier, prior_prefixes=()):
    """Independent bounded physical test. No perfect-equivalence oracle."""
    if verifier not in VERIFIERS:
        raise ValueError("unknown preregistered verification policy")
    alphabet = sorted(hypothesis.get_input_alphabet(), key=str)
    # P1 gate is the ONLY Omega additional cost; it cannot access the truth.
    metered = MeteredBlackBox(oracle_target, with_p1=(verifier in ("Wp_coverage_ranked", "Wp_memory_ranked")))
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    metadata = {}
    cex = None
    try:
        if verifier == "W":
            oracle = WMethodEqOracle(alphabet, metered, max_number_of_states=len(hypothesis.states) + 1)
            cex = oracle.find_cex(hypothesis)
            metadata["aalpy_native_oracle"] = "WMethodEqOracle"
        elif verifier == "Wp":
            oracle = WpMethodEqOracle(alphabet, metered, max_number_of_states=len(hypothesis.states) + 1)
            cex = oracle.find_cex(hypothesis)
            metadata["aalpy_native_oracle"] = "WpMethodEqOracle"
        else:
            cex, metadata = ranked_wp_gate(
                hypothesis, metered, alphabet, prior_prefixes,
                use_memory=(verifier == "Wp_memory_ranked"),
            )
            metadata["aalpy_native_oracle"] = "AALpy_Wp_test_generators_with_PR110_ranking"
        status = ("REFUTED_BY_MEASURED_COUNTEREXAMPLE" if cex else
                  "NO_COUNTEREXAMPLE_WITHIN_BOUNDED_SUITE")
    except VerificationBudgetExceeded as e:
        status = "BUDGET_EXHAUSTED"
        metadata["budget_reason"] = str(e)
    cpu, wall = time.process_time() - start_cpu, time.perf_counter() - start_wall
    result = {
        "verifier": verifier, "status": status,
        "counterexample": list(cex) if cex is not None else None,
        "measured_counterexample_length": len(cex) if cex is not None else None,
        "max_extra_states_assumed": 1, "true_state_count_used_by_gate": False,
        "physical_resets": metered.physical_resets,
        "physical_symbols": metered.physical_symbols,
        "p1_calls": metered.p1_calls,
        "cpu_seconds": round(cpu, 6), "wall_seconds": round(wall, 6),
        "universal_equivalence_certified": False, "novel_omega_algorithm": False,
        **metadata,
    }
    assert result["physical_resets"] <= RESET_BUDGET
    assert result["physical_symbols"] <= SYMBOL_BUDGET
    if verifier in ("Wp_coverage_ranked", "Wp_memory_ranked"):
        assert result["p1_calls"] == result["physical_resets"]
    else:
        assert result["p1_calls"] == 0
    return result


def run(sources):
    lock = json.loads((HERE.parent / "obs_col11" / "SOURCE_SHA_LOCK.json").read_text())["sha256"]
    previous = json.loads((HERE.parent / "obs_col11" / "FROZEN_FIRST_RUN.json").read_text())["models"]
    samples = []
    for name in SOURCE_NAMES:
        for arm in FROZEN_ARMS[name]:
            results = {}
            for verifier in VERIFIERS:
                # New, identically trained candidate per verifier: isolate
                # AALpy characterization_set mutation and P1 accounting.
                source, _ = load_pinned_moore(Path(sources) / name, lock[name])
                hypothesis, training = fit_one(source, arm, name, list(lock).index(name))
                locked = previous[name][arm]
                if (training["physical_resets"], training["physical_symbols"],
                    training["learned_states"]) != tuple(locked[:3]):
                    raise AssertionError("original training is not reproducible for " + name + "/" + arm)
                # Fresh target access via physical oracle only.
                target, _ = load_pinned_moore(Path(sources) / name, lock[name])
                res = run_gate(hypothesis, target, verifier,
                               prior_prefixes=training["_physical"].observed_prefixes)
                # Posthoc check witness only AFTER returned measurement:
                if res["counterexample"] is not None:
                    w = tuple(res["counterexample"])
                    from_target = target.execute_sequence(target.initial_state, w)[-1]
                    from_model = hypothesis.execute_sequence(hypothesis.initial_state, w)[-1]
                    if from_target == from_model:
                        raise AssertionError("verifier reported a non-witness")
                    res["witness_verified_after_measurement"] = True
                else:
                    res["witness_verified_after_measurement"] = False
                # Training metrics explicitly separated; never hide total costs.
                res["learning_resets"] = locked[0]
                res["learning_symbols"] = locked[1]
                res["total_resets"] = res["physical_resets"] + locked[0]
                res["total_symbols"] = res["physical_symbols"] + locked[1]
                results[verifier] = res
            samples.append({
                "source_name": name, "learned_arm": arm,
                "model_is_known_exact_from_prior_posthoc_audit": (
                    not (name == "register5.dot" and arm in ("coverage_only", "omega_candidate", "KV"))
                ),
                "verifiers": results,
            })
    return {
        "pilot": "OBS-COL-12",
        "prereg_commit": "9b8c6a39e4f28a8e8e0e076d6ffbdbdb74ff6430",
        "mode": "CALIBRATION_ON_PREVIOUSLY_REVEALED_ERRORS",
        "source_is_public_and_old": True,
        "no_new_blind_holdout": True,
        "no_known_witness_inserted_in_probe_suite": True,
        "omega_candidate_ranking_from_pr110": True,
        "practical_detection_not_equivalence_certification": True,
        "max_verification_resets": RESET_BUDGET,
        "max_verification_symbols": SYMBOL_BUDGET,
        "samples": samples,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: blackbox_gate.py <locked_source_directory>")
    print(json.dumps(run(sys.argv[1]), indent=2, ensure_ascii=False, default=str))
