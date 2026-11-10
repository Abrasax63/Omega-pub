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
        for invalid in (-1, 5, True, 1.0, "2"):
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


    def test_wrong_observation_model_can_make_two_steps_worse(self):
        # The optimizer expects complementary tests, and chooses both.
        # In the actual world the second test duplicates the first; there
        # is no decision information, but both costs are paid.
        from collections import Counter, defaultdict

        assumed = copy.deepcopy(self.cases["next-M-01"])
        planned = optimize_policy(assumed, max_depth=2)
        self.assertEqual(planned["expected_total_loss"], "1/50")
        self.assertTrue(all(
            child["action"] == "ask"
            for child in planned["policy"]["branches"].values()
        ))
        actual = copy.deepcopy(assumed)
        actual["checks"][1]["observations"] = list(
            actual["checks"][0]["observations"]
        )
        observed = defaultdict(Counter)
        for i, h in enumerate(actual["hypotheses"]):
            pair = tuple(c["observations"][i] for c in actual["checks"])
            observed[pair][h["decision"]] += h["weight"]
        missed = sum(sum(counts.values()) - max(counts.values())
                     for counts in observed.values())
        paid_cost = sum(c["cost_milli"] for c in actual["checks"])
        actual_loss = Fraction(missed, 4) + Fraction(paid_cost, 1000)
        self.assertEqual(actual_loss, Fraction(13, 25))
        self.assertGreater(actual_loss, Fraction(1, 2))

    def test_three_way_synergy_defeats_any_two_checks(self):
        from itertools import product
        case = copy.deepcopy(self.cases["next-M-01"])
        bits = list(product((0, 1), repeat=3))
        case["hypotheses"] = [
            {"id": f"h{i}", "decision": "A" if sum(b) % 2 == 0 else "B",
             "weight": 1}
            for i, b in enumerate(bits)
        ]
        case["checks"] = [
            {"id": f"bit-{j}", "action": "verify", "step": f"Read bit {j}",
             "method": "synthetic_bit", "available": True, "cost_milli": 1,
             "observations": [str(b[j]) for b in bits]}
            for j in range(3)
        ]
        # Every observed pair leaves two opposite decision labels.
        for j in range(3):
            for k in range(j + 1, 3):
                self.assertEqual(len({(b[j], b[k]) for b in bits}), 4)
                for pair in {(b[j], b[k]) for b in bits}:
                    matches = [sum(b) % 2 for b in bits if (b[j], b[k]) == pair]
                    self.assertEqual(sorted(matches), [0, 1])
        self.assertEqual(optimize_policy(case, max_depth=2)["action"],
                         "insufficient_evidence")
        self.assertEqual(len(set(bits)), 8)
        # All three observations jointly reveal the parity decision.
        # The planner is explicitly restricted to depth <= 2.


if __name__ == "__main__":
    unittest.main()
