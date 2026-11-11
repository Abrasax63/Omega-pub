"""Guard computation-cost and invalid-input regression tests."""
from fractions import Fraction
import unittest

from legacy_guard_cost_sensitivity import compare_costs,run


class LegacyGuardCostSensitivityTests(unittest.TestCase):
    def test_cost_threshold_is_exact_and_numerically_honest(self):
        result=run()
        self.assertEqual(
            result["break_even_guard_cost_per_case_probe_equivalents"],"94/125")
        self.assertTrue(result["known_models_price_not_measured"])
        self.assertTrue(result["baseline_has_same_relative_completeness"])
        self.assertEqual(compare_costs(Fraction(3,4))["guarded_vs_fixed"],
                         "cheaper")
        self.assertEqual(compare_costs(Fraction(94,125))["guarded_vs_fixed"],
                         "tie")
        self.assertEqual(compare_costs(Fraction(4,5))["guarded_vs_fixed"],
                         "more_expensive")
        self.assertEqual(compare_costs(Fraction(0))["guarded_all_case_cost"],
                         "156")
        self.assertEqual(compare_costs(Fraction(1))["guarded_all_case_cost"],
                         "281")

    def test_invalid_negative_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            compare_costs(Fraction(-1,8))


if __name__=="__main__":
    unittest.main()
