"""OBS-COL-11: independent finite-product equivalence audit tests."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from audit_exact_equivalence import exact_equivalence_or_counterexample, run
from external_transfer import load_pinned_moore

HERE = Path(__file__).resolve().parent
SOURCES = Path(os.environ.get("OBS_COL11_SOURCES", "obs_col11_sources"))


class TestExactAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((HERE / "SOURCE_SHA_LOCK.json").read_text())["sha256"]
        cls.source = SOURCES

    def test_independent_same_machine_always_exact(self):
        name = "register3.dot"
        a, _ = load_pinned_moore(self.source / name, self.lock[name])
        b, _ = load_pinned_moore(self.source / name, self.lock[name])
        result = exact_equivalence_or_counterexample(a, b)
        self.assertEqual(result["status"], "EXACT_EQUIVALENT_FINITE_MOORE")
        self.assertIsNone(result["shortest_word"])

    def test_changed_start_output_is_zero_length_witness(self):
        name = "register2.dot"
        a, _ = load_pinned_moore(self.source / name, self.lock[name])
        b, _ = load_pinned_moore(self.source / name, self.lock[name])
        b.initial_state.output = "__altered_output__"
        result = exact_equivalence_or_counterexample(a, b)
        self.assertEqual(result["status"], "EXACT_COUNTEREXAMPLE")
        self.assertEqual(result["shortest_length"], 0)
        self.assertEqual(result["shortest_word"], [])

    def test_single_changed_reachable_output_has_witness(self):
        name = "register4.dot"
        a, _ = load_pinned_moore(self.source / name, self.lock[name])
        b, _ = load_pinned_moore(self.source / name, self.lock[name])
        state = next(s for s in b.states if s is not b.initial_state)
        state.output = "__unseen_value__"
        result = exact_equivalence_or_counterexample(a, b)
        self.assertEqual(result["status"], "EXACT_COUNTEREXAMPLE")
        self.assertGreater(result["shortest_length"], 0)
        # Verify the reported word really distinguishes true source and copy.
        self.assertNotEqual(
            a.execute_sequence(a.initial_state, result["shortest_word"])[-1],
            b.execute_sequence(b.initial_state, result["shortest_word"])[-1],
        )

    def test_posthoc_replay_guard_and_all_methods(self):
        report = run(self.source)
        self.assertEqual(report["original_run"], 43822021430)
        self.assertTrue(report["posthoc_not_preregistered_in_initial_trial"])
        self.assertEqual(len(report["models"]), 4)
        for model in report["models"]:
            self.assertEqual(len(model["cases"]), 5)
            for arm in model["cases"].values():
                self.assertTrue(arm["reproduced_training_costs"])
                self.assertIn(
                    arm["status"],
                    ("EXACT_EQUIVALENT_FINITE_MOORE", "EXACT_COUNTEREXAMPLE"),
                )
                self.assertTrue(arm["not_seen_by_policy"])
                self.assertLessEqual(
                    arm["visited_product_states"], arm["product_upper_bound"],
                )


if __name__ == "__main__":
    unittest.main()
