"""Tests for exact one- vs two-check strategies and negative examples."""
import copy
import unittest
from fractions import Fraction

from action_planning_two_step import optimize_policy, plan_with_two_step_evidence
from action_planning_challenge import (
    assess, exhaustive_policy_reference, make_challenge_cases,
    make_seeded_stress_cases,
)


class TwoStepPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["case_id"]: case for case in make_challenge_cases()}

    def test_24_new_authored_cases_and_96_seeded_stress_cases(self):
        authored = assess(make_challenge_cases())
        stress = assess(make_seeded_stress_cases())
        self.assertEqual(authored["cases"], 24)
        self.assertEqual(authored["oracle_agreements"], 24)
        self.assertEqual(authored["two_step_better"], 8)
        self.assertEqual(authored["equal"], 16)
        self.assertEqual(authored["rescued_abstentions"], 4)
        self.assertEqual(stress["cases"], 96)
        self.assertEqual(stress["oracle_agreements"], 96)
        print("TWO-STEP DECISION: 24 authored + 96 seeded, "
              f"authored improvements={authored['two_step_better']}, "
              f"seeded improvements={stress['two_step_better']}; "
              "all exact exhaustive oracle matches; no model calls.")

    def test_synergy_beats_one_step_without_immediate_gain(self):
        case = self.cases["next-M-01"]
        one = optimize_policy(case, max_depth=1)
        two = optimize_policy(case, max_depth=2)
        self.assertEqual(one["action"], "insufficient_evidence")
        self.assertEqual(one["expected_total_loss"], "1/2")
        self.assertEqual(two["action"], "verify")
        self.assertEqual(two["policy"]["check_id"], "01-parity")
        self.assertEqual(two["expected_decision_risk"], "0")
        self.assertEqual(two["expected_total_loss"], "1/50")
        self.assertEqual(exhaustive_policy_reference(case, depth=2)["objective"], "1/50")

    def test_adaptive_contingent_second_test(self):
        case = self.cases["next-D-02"]
        two = optimize_policy(case, max_depth=2)
        self.assertEqual(two["policy"]["check_id"], "01-group")
        self.assertEqual(two["policy"]["branches"]["x"]["check_id"], "02-local-x")
        self.assertEqual(two["policy"]["branches"]["y"]["check_id"], "03-local-y")
        self.assertEqual(two["expected_total_loss"], "17/200")
        self.assertEqual(exhaustive_policy_reference(case, depth=2)["objective"], "17/200")

    def test_two_step_does_not_force_a_second_check(self):
        case = self.cases["next-C-03"]
        two = optimize_policy(case, max_depth=2)
        self.assertEqual(two["action"], "verify")
        self.assertEqual(two["policy"]["check_id"], "02-decisive")
        self.assertTrue(all(v["action"] == "answer" for v in two["policy"]["branches"].values()))
        self.assertEqual(two["expected_total_loss"], "9/200")

    def test_costly_synergy_abstains(self):
        case = self.cases["next-E-06"]
        self.assertEqual(optimize_policy(case, max_depth=1)["action"],
                         "insufficient_evidence")
        self.assertEqual(optimize_policy(case, max_depth=2)["action"],
                         "insufficient_evidence")

    def test_no_information_refuses_premature_decision(self):
        case = self.cases["next-C-04"]
        self.assertEqual(optimize_policy(case, max_depth=2)["action"],
                         "insufficient_evidence")
        self.assertEqual(optimize_policy(case, max_depth=2)["expected_total_loss"], "1/2")

    def test_p1_still_only_plans(self):
        for case in make_challenge_cases():
            output = plan_with_two_step_evidence(case)
            self.assertEqual(output["p1"]["next_action"]["action"],
                             output["optimization"]["action"])
            execution = output["p1"]["execution_model"]
            self.assertEqual(execution["model_calls_performed"], 0)
            self.assertEqual(execution["memory_writes_performed"], 0)
            self.assertFalse(execution["scientific_validation_performed"])

    def test_reorder_invariance_and_reference(self):
        for case in make_challenge_cases() + make_seeded_stress_cases()[:20]:
            baseline = optimize_policy(case, max_depth=2)
            permuted = copy.deepcopy(case)
            permuted["checks"].reverse()
            permuted["hypotheses"].reverse()
            for check in permuted["checks"]:
                check["observations"].reverse()
            observed = optimize_policy(permuted, max_depth=2)
            self.assertEqual(baseline["expected_total_loss"],
                             observed["expected_total_loss"])
            self.assertEqual(baseline["policy"], observed["policy"])

    def test_input_rejection_for_depth(self):
        for invalid in (-1, 3, True, 1.0, "2"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                optimize_policy(self.cases["next-M-01"], max_depth=invalid)

    def test_larger_cost_cannot_reduce_optimal_total_loss(self):
        for case in make_challenge_cases():
            baseline = Fraction(optimize_policy(case, max_depth=2)["expected_total_loss"])
            altered = copy.deepcopy(case)
            for check in altered["checks"]:
                check["cost_milli"] += 1
            after = Fraction(optimize_policy(altered, max_depth=2)["expected_total_loss"])
            self.assertGreaterEqual(after, baseline)


if __name__ == "__main__":
    unittest.main()
