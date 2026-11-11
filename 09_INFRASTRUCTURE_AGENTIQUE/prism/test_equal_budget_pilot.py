"""Regression tests for equal-budget benchmark on Omega's actual policy."""
import unittest
from equal_budget_pilot import run_benchmark, make_cases, case_digest, FROZEN_SHA256


class EqualBudgetPilotTests(unittest.TestCase):
    def test_frozen_tables(self):
        self.assertEqual(case_digest(make_cases()), FROZEN_SHA256)

    def test_actual_omega_equals_independent_oracle(self):
        report = run_benchmark()
        self.assertEqual(report["model_calls"], 0)
        self.assertEqual(report["real_observation_calls"], 0)
        random = report["strata"]["random"]
        conditional = report["strata"]["conditional_constructed"]
        self.assertEqual(random["cases"],200)
        self.assertEqual(random["oracle_matches"],200)
        self.assertEqual(random["hidden_states"],1391)
        self.assertEqual(random["fixed_correct"],777)
        self.assertEqual(random["omega_correct"],793)
        self.assertEqual(random["improved_cases"],16)
        self.assertEqual(conditional["cases"],60)
        self.assertEqual(conditional["oracle_matches"],60)
        self.assertEqual(conditional["hidden_states"],360)
        self.assertEqual(conditional["fixed_correct"],180)
        self.assertEqual(conditional["omega_correct"],240)
        self.assertEqual(conditional["improved_cases"],60)


if __name__ == "__main__":
    unittest.main()
