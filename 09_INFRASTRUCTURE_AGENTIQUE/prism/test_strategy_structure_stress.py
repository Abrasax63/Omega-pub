"""Independent stress tests of strategy ordering and smoothing sensitivity.

The mathematical structure is binary AND with unit-cost perfect observations.
This is not a search over target labels and cannot improve held-out scores.
"""
import itertools
import unittest

import strategic_first_check_transfer as lab
from action_planning_two_step import optimize_policy


class StrategyStructureStressTests(unittest.TestCase):
    def test_eighty_one_weighted_worlds_match_exact_short_circuit_rule(self):
        rows = lab.train_snapshot()
        for weights in itertools.product((1,2,3), repeat=4):
            with self.subTest(weights=weights):
                model = lab.make_model(rows, "weight-grid")
                for h, w in zip(model["hypotheses"], weights):
                    h["weight"] = w
                p = optimize_policy(model, max_depth=2, max_cost_milli=2)
                true_merged = sum(w for (m,t),w in zip(lab.WORLD_ORDER,weights) if m)
                true_test = sum(w for (m,t),w in zip(lab.WORLD_ORDER,weights) if t)
                expected_id = ("00-merged" if true_merged <= true_test else "01-tests")
                self.assertEqual(p["policy"].get("check_id"), expected_id)
                self.assertEqual(p["expected_decision_risk"], "0")
                # Derivation independent from the optimizer:
                # expected tests = 1 + P(first check is true)
                self.assertEqual(p["expected_steps"],
                    str(__import__("fractions").Fraction(
                        sum(weights) + min(true_merged, true_test),
                        sum(weights))))

    def test_laplace_pseudocount_two_does_not_change_precommitted_orders(self):
        train = lab.train_snapshot()
        original = lab.training_policies(train)
        old_alpha = lab.ALPHA
        try:
            lab.ALPHA = 2
            doubled = lab.training_policies(train)
        finally:
            lab.ALPHA = old_alpha
        self.assertEqual(original["global"]["omega"]["policy"].get("check_id"),
                         doubled["global"]["omega"]["policy"].get("check_id"))
        for repo in original["by_repo"]:
            self.assertEqual(
                original["by_repo"][repo]["omega"]["policy"].get("check_id"),
                doubled["by_repo"][repo]["omega"]["policy"].get("check_id"))


if __name__ == "__main__":
    unittest.main()
