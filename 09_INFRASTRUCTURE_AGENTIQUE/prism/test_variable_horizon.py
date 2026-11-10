"""Adversarial tests for Omega's variable planning horizon.

All results are exact, but conditional on artificial hypotheses and costs.
"""
import copy
import unittest
from fractions import Fraction
from itertools import product

from action_planning_two_step import (
    optimize_policy, plan_with_variable_horizon,
)
from action_planning_challenge import (
    make_challenge_cases, make_seeded_stress_cases,
)
from variable_horizon_oracle import (
    enumerate_policies, evaluate_independent_oracle,
)


def parity_case(n, cost=10):
    bits = list(product((0, 1), repeat=n))
    return {
        "case_id": f"parity-{n}",
        "question": f"Quelle est la parite de {n} bits inconnus ?",
        "mission_type": "mathematical",
        "uncertainty": "La parite ne peut pas etre determinee par ces observations.",
        "hypotheses": [
            {"id": f"h{i}", "decision": str(sum(b) % 2), "weight": 1}
            for i, b in enumerate(bits)
        ],
        "checks": [
            {"id": f"bit-{j}", "action": "verify",
             "step": f"Lire le bit {j}", "method": "synthetic_bit",
             "available": True, "cost_milli": cost,
             "observations": [str(b[j]) for b in bits]}
            for j in range(n)
        ],
    }


class VariableHorizonTests(unittest.TestCase):
    def test_full_120_cases_against_separate_policy_tree_enumerator(self):
        cases = make_challenge_cases() + make_seeded_stress_cases()
        stats = evaluate_independent_oracle(cases)["statistics"]
        self.assertEqual(stats["cases"], 120)
        self.assertEqual(stats["exact_matches"], 480)
        print("VARIABLE-HORIZON: 120 synthetic models x 4 depths; "
              f"depth3-vs2 strict improvements={stats['depth3_better_than2']}; "
              "480 exact independent oracle agreements.")

    def test_three_bit_parity_requires_horizon_three(self):
        case = parity_case(3)
        for depth in (0, 1, 2):
            self.assertEqual(optimize_policy(case, max_depth=depth)["action"],
                             "insufficient_evidence")
        r = optimize_policy(case, max_depth=3)
        self.assertEqual(r["action"], "verify")
        self.assertEqual(r["expected_decision_risk"], "0")
        self.assertEqual(r["expected_action_cost"], "3/100")
        self.assertEqual(r["expected_steps"], "3")
        oracle, mass = enumerate_policies(case, depth=3)
        self.assertEqual((oracle[0] + oracle[1]) / mass, Fraction(3, 100))

    def test_four_bit_parity_needs_four_steps(self):
        case = parity_case(4)
        self.assertEqual(optimize_policy(case, max_depth=3)["action"],
                         "insufficient_evidence")
        r = optimize_policy(case, max_depth=4)
        self.assertEqual(r["expected_total_loss"], "1/25")
        self.assertEqual(r["expected_decision_risk"], "0")
        self.assertEqual(r["expected_steps"], "4")

    def test_hard_path_budget_blocks_parity_then_allows_it(self):
        case = parity_case(3)
        for budget in (0, 9, 10, 20, 29):
            result = optimize_policy(case, max_depth=4,
                                     max_cost_milli=budget)
            self.assertEqual(result["action"], "insufficient_evidence")
        r = optimize_policy(case, max_depth=4, max_cost_milli=30)
        self.assertEqual(r["expected_total_loss"], "3/100")
        self.assertEqual(r["expected_steps"], "3")

    def test_budget_zero_can_still_take_free_informative_check(self):
        case = copy.deepcopy(make_challenge_cases()[2])
        case["checks"][1]["cost_milli"] = 0
        r = optimize_policy(case, max_depth=3, max_cost_milli=0)
        self.assertEqual(r["action"], "verify")
        self.assertEqual(r["expected_total_loss"], "0")

    def test_variable_horizon_stops_after_one_when_sufficient(self):
        case = next(x for x in make_challenge_cases()
                    if x["case_id"] == "next-C-03")
        results = [optimize_policy(case, max_depth=d) for d in range(1, 5)]
        self.assertEqual({r["expected_total_loss"] for r in results}, {"9/200"})
        self.assertEqual({r["expected_steps"] for r in results}, {"1"})

    def test_zero_depth_never_tests(self):
        for case in make_challenge_cases():
            r = optimize_policy(case, max_depth=0)
            self.assertEqual(r["expected_steps"], "0")
            self.assertNotIn(r["action"], ("ask", "verify"))

    def test_depth_monotonicity_and_budget_monotonicity(self):
        for case in make_challenge_cases() + make_seeded_stress_cases()[:16]:
            old = None
            for depth in range(5):
                loss = Fraction(optimize_policy(case, max_depth=depth)["expected_total_loss"])
                if old is not None:
                    self.assertLessEqual(loss, old)
                old = loss
            old = None
            for budget in (0, 50, 100, 200, 500, 4000):
                loss = Fraction(optimize_policy(
                    case, max_depth=3, max_cost_milli=budget
                )["expected_total_loss"])
                if old is not None:
                    self.assertLessEqual(loss, old)
                old = loss

    def test_reordering_invariance_three_steps(self):
        for case in make_challenge_cases():
            original = optimize_policy(case, max_depth=3, max_cost_milli=150)
            altered = copy.deepcopy(case)
            altered["hypotheses"].reverse()
            altered["checks"].reverse()
            for c in altered["checks"]:
                c["observations"].reverse()
            actual = optimize_policy(altered, max_depth=3, max_cost_milli=150)
            self.assertEqual(actual["policy"], original["policy"])
            self.assertEqual(actual["expected_total_loss"],
                             original["expected_total_loss"])

    def test_bridge_keeps_planning_only(self):
        for case in make_challenge_cases():
            r = plan_with_variable_horizon(case, max_depth=4)
            self.assertEqual(r["p1"]["next_action"]["action"],
                             r["optimization"]["action"])
            execution = r["p1"]["execution_model"]
            self.assertEqual(execution["model_calls_performed"], 0)
            self.assertEqual(execution["memory_writes_performed"], 0)
            self.assertFalse(execution["scientific_validation_performed"])

    def test_reject_invalid_limits(self):
        case = parity_case(3)
        for invalid in (-1, 5, True, 3.0, "4"):
            with self.subTest(depth=invalid), self.assertRaises(ValueError):
                optimize_policy(case, max_depth=invalid)
        for invalid in (-1, 4001, True, 20.0, "20"):
            with self.subTest(budget=invalid), self.assertRaises(ValueError):
                optimize_policy(case, max_cost_milli=invalid)


if __name__ == "__main__":
    unittest.main()
