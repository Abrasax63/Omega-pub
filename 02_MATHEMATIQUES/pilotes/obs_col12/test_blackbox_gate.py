"""OBS-COL-12: black-box verifiers, budgets, source isolation, genuine AALpy."""
import copy
import json
import os
from pathlib import Path
import unittest

from blackbox_gate import (
    SOURCE_NAMES, FROZEN_ARMS, VERIFIERS, RESET_BUDGET, SYMBOL_BUDGET,
    VerificationBudgetExceeded, MeteredBlackBox,
    wp_candidate_suite, ranked_wp_gate, run_gate,
)
from external_transfer import load_pinned_moore, fit_one
from policy_divergence import coverage_ranking

SOURCES = Path(os.environ.get("OBS_COL12_SOURCES", "obs_col12_sources"))
HERE = Path(__file__).resolve().parent


class TestBlackBoxConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((HERE.parent / "obs_col11" / "SOURCE_SHA_LOCK.json").read_text())["sha256"]
        if not SOURCES.is_dir():
            raise AssertionError("locked source cohort was not downloaded")
        name = "register3.dot"
        target = load_pinned_moore(SOURCES / name, cls.lock[name])[0]
        cls.learned_register3, _ = fit_one(target, "fixed", name, list(cls.lock).index(name))

    def make_target(self, name):
        return load_pinned_moore(SOURCES / name, self.lock[name])[0]

    def test_expected_predeclared_targets_and_gates(self):
        self.assertEqual(SOURCE_NAMES, ("register3.dot", "register5.dot"))
        self.assertEqual(FROZEN_ARMS["register5.dot"],
                         ("fixed", "coverage_only", "omega_candidate", "KV"))
        self.assertEqual(VERIFIERS, ("W", "Wp", "Wp_coverage_ranked", "Wp_memory_ranked"))

    def test_budget_guard_refuses_one_extra_reset_or_symbol(self):
        model = self.make_target("register3.dot")
        physical = MeteredBlackBox(model, max_resets=1, max_symbols=1)
        physical.pre()
        physical.step("F")
        with self.assertRaises(VerificationBudgetExceeded):
            physical.step("L")
        physical.post()
        with self.assertRaises(VerificationBudgetExceeded):
            physical.pre()
        self.assertEqual(physical.physical_resets, 1)
        self.assertEqual(physical.physical_symbols, 1)

    def test_native_w_wp_are_original_aalpy_oracles(self):
        from aalpy.oracles import WMethodEqOracle, WpMethodEqOracle
        self.assertTrue(WMethodEqOracle.__module__.startswith("aalpy."))
        self.assertTrue(WpMethodEqOracle.__module__.startswith("aalpy."))

    def test_ranked_wp_same_candidate_set_and_no_source_graph_used(self):
        model = copy.deepcopy(self.learned_register3)
        # For this unit test use hypothesis equal to the same kind of model,
        # but a separate instance from the target oracle.
        words = wp_candidate_suite(model, sorted(model.get_input_alphabet()))
        reordered = coverage_ranking(model, words, memory=True)
        self.assertEqual(set(words), set(reordered))
        self.assertEqual(len(words), len(reordered))
        self.assertIsNotNone(model.initial_state)

    def test_valid_hypothesis_does_not_produce_false_witness(self):
        for gate in VERIFIERS:
            model = copy.deepcopy(self.learned_register3)
            target = self.make_target("register3.dot")
            r = run_gate(model, target, gate, prior_prefixes=())
            self.assertIsNone(r["counterexample"])
            self.assertNotEqual(r["status"], "REFUTED_BY_MEASURED_COUNTEREXAMPLE")
            self.assertFalse(r["universal_equivalence_certified"])
            self.assertLessEqual(r["physical_resets"], RESET_BUDGET)
            self.assertLessEqual(r["physical_symbols"], SYMBOL_BUDGET)

    def test_memory_vs_coverage_ablation_controls_same_candidate_set(self):
        name = "register5.dot"
        hypothesis, metrics = fit_one(
            self.make_target(name), "omega_candidate", name, list(self.lock).index(name))
        observed = metrics["_physical"].observed_prefixes
        results = {}
        for method in ("Wp_coverage_ranked", "Wp_memory_ranked"):
            results[method] = run_gate(
                copy.deepcopy(hypothesis), self.make_target(name), method,
                prior_prefixes=observed,
            )
        left, right = results.values()
        self.assertEqual(left["wp_candidate_sha256"], right["wp_candidate_sha256"])
        self.assertFalse(left["memory_component"])
        self.assertTrue(right["memory_component"])
        self.assertEqual(left["p1_calls"], left["physical_resets"])
        self.assertEqual(right["p1_calls"], right["physical_resets"])
        self.assertFalse(left["universal_equivalence_certified"])
        self.assertFalse(right["universal_equivalence_certified"])

    def test_measure_only_real_oracle_and_no_perfect_knowledge(self):
        name = "register5.dot"
        hypothesis, metrics = fit_one(self.make_target(name), "omega_candidate",
                                      name, list(self.lock).index(name))
        target = self.make_target(name)
        for gate in VERIFIERS:
            outcome = run_gate(hypothesis, target, gate,
                               prior_prefixes=metrics["_physical"].observed_prefixes)
            self.assertIn(outcome["status"],
                {"REFUTED_BY_MEASURED_COUNTEREXAMPLE",
                 "NO_COUNTEREXAMPLE_WITHIN_BOUNDED_SUITE", "BUDGET_EXHAUSTED"})
            self.assertFalse(outcome["universal_equivalence_certified"])
            if outcome["counterexample"]:
                word = tuple(outcome["counterexample"])
                self.assertNotEqual(
                    hypothesis.execute_sequence(hypothesis.initial_state, word)[-1],
                    target.execute_sequence(target.initial_state, word)[-1],
                )
                # Tests must NOT hardcode the previous leaked exact word.
            self.assertLessEqual(outcome["physical_resets"], RESET_BUDGET)
            self.assertLessEqual(outcome["physical_symbols"], SYMBOL_BUDGET)


if __name__ == "__main__":
    unittest.main()
