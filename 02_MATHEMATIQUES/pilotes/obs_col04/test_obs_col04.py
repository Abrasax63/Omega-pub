"""OBS-COL-04 reproducible tests; actual inherited Omega modules, no mocks."""
import unittest
from fractions import Fraction
from obs_col04 import (
    ACTIONS, TARGETS, Rule, Oracle, hypothesis_catalog, full_invariants,
    invariant_masks, prediction, consistent, make_case, observer_advisory,
    independent_two_step_oracle, plan_with_variable_horizon, run
)


class TestObsCol04(unittest.TestCase):
    def test_catalog_structure(self):
        models = hypothesis_catalog()
        self.assertEqual(len(models), 36)
        self.assertEqual(len(set(models)), 36)
        self.assertTrue(any(full_invariants(m) for m in models))
        self.assertTrue(any(not full_invariants(m) for m in models))

    def test_interaction_group_changes_with_state(self):
        model = Rule(2, 3, 1, 6)
        x1 = model.outcome(0, "pulse")
        x2 = model.outcome(x1, "bind")
        self.assertEqual(model.interaction(0, "pulse"), (0, 1))
        self.assertEqual(model.interaction(x2, "pulse"), (0,))

    def test_false_initial_invariant(self):
        model = Rule(2, 3, 1, 6)
        edges = tuple((0, model.outcome(0, action)) for action in ACTIONS)
        self.assertIn(7, invariant_masks(edges))
        self.assertNotIn(7, full_invariants(model))

    def test_positive_controls(self):
        self.assertIn(7, full_invariants(Rule(2, 3, 5, 6)))
        self.assertIn(1, full_invariants(Rule(1, 6, 2, 2)))

    def test_independent_two_step_equals_real_omega(self):
        target = Rule(2, 3, 1, 6)
        obs = [(0, a, m, prediction(target, 0, a, m))
               for a in ACTIONS for m in (1, 2, 4)]
        remaining = tuple(model for model in hypothesis_catalog()
                          if consistent(model, obs))
        case = make_case(remaining, obs, "test-two-step")
        exact = independent_two_step_oracle(case)
        omega = plan_with_variable_horizon(case, max_depth=2, max_cost_milli=144)
        self.assertEqual(Fraction(exact["expected_total_loss"]),
                         Fraction(omega["optimization"]["expected_total_loss"]))
        self.assertEqual(omega["p1"]["next_action"]["action"],
                         omega["optimization"]["action"])

    def test_readonly_observer_gate(self):
        target = Rule(2, 3, 1, 6)
        obs = [(0, a, m, prediction(target, 0, a, m))
               for a in ACTIONS for m in (1, 2, 4)]
        remaining = tuple(model for model in hypothesis_catalog()
                          if consistent(model, obs))
        case = make_case(remaining, obs, "test-advisory")
        report = observer_advisory(case, case["checks"][0]["id"])
        self.assertIs(report["source_authenticity_verified"], False)
        self.assertIs(report["scientific_certificate_issued"], False)

    def test_true_world_stays_in_version_space(self):
        for parameters in TARGETS:
            model = Rule(*parameters)
            observations = [(0, a, m, prediction(model, 0, a, m))
                            for a in ACTIONS for m in (1, 2, 4)]
            self.assertIn(model, tuple(r for r in hypothesis_catalog()
                                       if consistent(r, observations)))

    def test_six_cases_measure_direct_falsifications(self):
        cases = run()["results"]
        self.assertEqual(len(cases), 6)
        self.assertEqual([c["direct_falsification"] for c in cases],
                         [True, False, True, False, True, False])
        for c in cases:
            self.assertFalse(c["false_robust_claim"])
            self.assertTrue(c["confirmation"] is not None)
            self.assertLessEqual(c["omega_extra_probes"], 3)
            self.assertTrue(all(Fraction(x) == 1
                                for x in c["initial_walsh_pr86"].values()))
            self.assertFalse(c["scientifically_certified"])
            self.assertEqual(c["model_calls"], 0)

    def test_invalid_oracle_queries(self):
        oracle = Oracle(Rule(0, 3, 5, 6))
        with self.assertRaises(ValueError):
            oracle.ask(0, "pulse", 0)
        with self.assertRaises(ValueError):
            oracle.ask(9, "pulse", 7)

    def test_no_open_world_or_model_gain_claim(self):
        result = run()
        self.assertTrue(result["no_claim_of_open_world_learning"])
        self.assertEqual(result["rules_total"], 36)
        self.assertEqual(result["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
