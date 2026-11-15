#!/usr/bin/env python3
"""OBS-COL-09: external AALpy Moore fixtures, real L*/KV/L#, real P1 gate.

Target automata are copied verbatim from DES-Lab/AALpy's published DotModels.
Learning code never receives the true graph, state count or evaluation words.
The EQ oracle is AALpy's bounded randomized oracle, NOT perfect equivalence.
The P1 wrapper authorizes resets; it DOES NOT invent any queries.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRISM = ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism"
if str(PRISM) not in sys.path:
    sys.path.insert(0, str(PRISM))
from planner import plan_mission  # the real Omega P1 module

from aalpy.base import SUL
from aalpy.utils import load_automaton_from_file
from aalpy.SULs import AutomatonSUL
from aalpy.oracles import RandomWalkEqOracle
from aalpy.learning_algs import run_Lstar, run_KV, run_Lsharp

FIXTURES = (
    ("Angluin_Moore.dot", "4ed5251c5580b1d115823486083ddc88b3e2a5ce"),
    ("coffee_moore.dot", "91edc61c18e5624e937b7b7c1c1bf5970432dbfa"),
    ("mooreModel.dot", "d494040778647da551ea7131fdc72350041ee76f"),
)
ALGORITHMS = ("Lstar", "KV", "Lsharp", "Lsharp_P1")
MAX_RESETS = 10000
MAX_SYMBOLS = 50000
EQUIV_RANDOM_WALK_STEPS = 2000
EVAL_COUNT = 256


class PhysicalCounter(SUL):
    """Instrument every physical reset and action including EQ checks.

    Counts accesses to an actual AutomatonSUL, below any AALpy caching.
    The trace fingerprint catches changes to the query stream with P1 gating.
    """
    def __init__(self, target, use_p1):
        super().__init__()
        self.delegate = AutomatonSUL(target)
        self.use_p1 = use_p1
        self.physical_resets = 0
        self.physical_symbols = 0
        self.p1_calls = 0
        self.observed_prefixes = set()
        self._current = ()
        self._fingerprint = hashlib.sha256()

    def pre(self):
        if self.physical_resets >= MAX_RESETS:
            raise RuntimeError("physical reset budget exhausted")
        if self.use_p1:
            ordinal = self.physical_resets
            result = plan_mission({
                "mission_id": f"OBS-COL-09-UNLABELED-{ordinal:08d}",
                "question": "Prepare a controlled black-box observation",
                "mission_type": "mathematical",
                "decision_context": {
                    "blocking_uncertainty": "The current automaton model may be wrong",
                    "verification": "Reset the hidden system, execute a proposed input history, and record outputs",
                    "verification_effect": "The new measured trace may refute the current model",
                },
            })
            if result["next_action"]["action"] != "verify":
                raise AssertionError("actual Omega P1 did not request verification")
            self.p1_calls += 1
        self.delegate.pre()
        self.physical_resets += 1
        self._current = ()
        self._fingerprint.update(b"\x00")

    def step(self, letter):
        if letter is not None and self.physical_symbols >= MAX_SYMBOLS:
            raise RuntimeError("physical action-symbol budget exhausted")
        result = self.delegate.step(letter)
        if letter is not None:
            self.physical_symbols += 1
            self._current += (letter,)
            self.observed_prefixes.add(self._current)
            self._fingerprint.update(repr(letter).encode("utf8") + b";")
        return result

    def post(self):
        self.delegate.post()

    def fingerprint(self):
        return self._fingerprint.hexdigest()


def git_blob_sha(content):
    header = b"blob " + str(len(content)).encode() + b"\x00"
    return hashlib.sha1(header + content).hexdigest()


def external_fixture(model_name, expected_blob):
    path = Path(__file__).parent / "external_fixtures" / model_name
    content = path.read_bytes()
    if git_blob_sha(content) != expected_blob:
        raise AssertionError("external model differs from pinned Git blob")
    model = load_automaton_from_file(str(path), automaton_type="moore")
    if not model.is_input_complete():
        raise AssertionError("external automaton is not input complete")
    return model, {
        "filename": model_name, "git_blob_sha": expected_blob,
        "sha256": hashlib.sha256(content).hexdigest(),
        "published_by": "DES-Lab/AALpy",
        "source_url": f"https://github.com/DES-Lab/AALpy/blob/master/DotModels/{model_name}",
    }


def evaluation_words(alphabet, fixture_index):
    """Predeclared 256 distinct words, unseen in the learner configuration."""
    rng = random.Random(20261116 + fixture_index)
    words = set()
    while len(words) < EVAL_COUNT:
        length = rng.randint(12, 18)
        words.add(tuple(rng.choice(alphabet) for _ in range(length)))
    return sorted(words, key=lambda x: (len(x), x))


def run_algorithm(fixture_index, model_name, expected_blob, algorithm):
    model, provenance = external_fixture(model_name, expected_blob)
    alphabet = sorted(model.get_input_alphabet(), key=str)
    physical = PhysicalCounter(model, use_p1=algorithm == "Lsharp_P1")
    # Each algorithm starts from same RNG state and same black-box model.
    seed = 20261115 + fixture_index
    random.seed(seed)
    equivalence = RandomWalkEqOracle(
        alphabet, physical, num_steps=EQUIV_RANDOM_WALK_STEPS,
        reset_prob=0.12, reset_after_cex=True,
    )
    runner = {
        "Lstar": run_Lstar,
        "KV": run_KV,
        "Lsharp": run_Lsharp,
        "Lsharp_P1": run_Lsharp,
    }[algorithm]

    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    learned, library_info = runner(
        alphabet, physical, equivalence, automaton_type="moore",
        return_data=True, print_level=0, max_learning_rounds=40,
    )
    wall_s = time.perf_counter() - start_wall
    cpu_s = time.process_time() - start_cpu

    # Scores computed only AFTER training/model choice is final.
    words = evaluation_words(alphabet, fixture_index)
    overlaps = [w for w in words if w in physical.observed_prefixes]
    error_all = 0
    error_unseen = 0
    count_unseen = 0
    for word in words:
        target_last = model.execute_sequence(model.initial_state, word)[-1]
        learned_last = learned.execute_sequence(learned.initial_state, word)[-1]
        mismatch = target_last != learned_last
        error_all += mismatch
        if word not in physical.observed_prefixes:
            count_unseen += 1
            error_unseen += mismatch

    return {
        "algorithm": algorithm,
        "fixture": provenance,
        "target_states_posthoc": len(model.states),
        "learned_states": len(learned.states),
        "alphabet": [str(x) for x in alphabet],
        "seed": seed,
        "random_equivalence_steps_per_round": EQUIV_RANDOM_WALK_STEPS,
        "physical_resets": physical.physical_resets,
        "physical_symbols": physical.physical_symbols,
        "physical_trace_sha256": physical.fingerprint(),
        "p1_calls": physical.p1_calls,
        "p1_only_gate": algorithm == "Lsharp_P1",
        "wall_seconds": round(wall_s, 6),
        "cpu_seconds": round(cpu_s, 6),
        "library_counters": library_info,
        "heldout_words_total": len(words),
        "heldout_overlap_seen_during_training": len(overlaps),
        "heldout_unseen_scored": count_unseen,
        "heldout_errors_unseen": error_unseen,
        "heldout_errors_total": error_all,
        "holdout_selection_seed": 20261116 + fixture_index,
        "status": "COMPLETED" if count_unseen > 0 else "UNSEEN_EVALUATION_INDETERMINATE",
        "equivalence_certified": False,
        "omega_superiority_demonstrated": False,
    }


def run():
    if importlib.metadata.version("aalpy") != "2.0.0":
        raise AssertionError("AALpy dependency must match pinned version 2.0.0")
    data = []
    for i, (name, sha) in enumerate(FIXTURES):
        for algo in ALGORITHMS:
            data.append(run_algorithm(i, name, sha, algo))
    for name, _ in FIXTURES:
        lsharp = next(x for x in data if x["fixture"]["filename"] == name and x["algorithm"] == "Lsharp")
        gated = next(x for x in data if x["fixture"]["filename"] == name and x["algorithm"] == "Lsharp_P1")
        for field in ("physical_resets", "physical_symbols", "physical_trace_sha256",
                      "learned_states", "heldout_errors_unseen",
                      "heldout_errors_total", "heldout_unseen_scored"):
            if lsharp[field] != gated[field]:
                raise AssertionError(f"Omega P1 gating changed the Lsharp experiment on {name}: {field}")
        if gated["p1_calls"] != gated["physical_resets"] or lsharp["p1_calls"] != 0:
            raise AssertionError("actual P1 call accounting invalid")
    return {
        "experiment": "OBS-COL-09",
        "status": "EXTERNAL_PUBLIC_BENCHMARK_NOT_BLIND",
        "aalpy_version": importlib.metadata.version("aalpy"),
        "algorithms_executed": list(ALGORITHMS),
        "ttt_status": "NOT_EXECUTED_IN_THIS_PYTHON_STAGE",
        "p1_selects_queries": False, "model_calls": 0,
        "preregistered_commit": "2701c24c4b81605e2a619ba1430bed8c6fab6e1c",
        "prerun_overlap_amendment": "d5f6e1dd22c81a656a90b4b95b76cb0b270e93fc",
        "limitation": "AALpy published public fixtures, random (not perfect) equivalence, no natural or blind independent evaluation. P1 is an extra per-reset gate.",
        "results": data,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False, default=str))
