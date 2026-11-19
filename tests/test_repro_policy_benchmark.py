import unittest
from tools.repro_policy_benchmark import Case, evaluate


class PolicyBenchmarkTests(unittest.TestCase):
    def test_baseline_counts(self):
        observed = evaluate()
        self.assertEqual(observed["strict"]["recomputes"], 3)
        self.assertEqual(observed["strict"]["wrong_reuses"], 0)
        self.assertEqual(observed["fast"]["recomputes"], 0)
        self.assertEqual(observed["fast"]["wrong_reuses"], 1)
        self.assertEqual(observed["adaptive"]["recomputes"], 2)
        self.assertEqual(observed["adaptive"]["wrong_reuses"], 0)
        self.assertEqual(observed["strict"]["simulated_cost"], 30)
        self.assertEqual(observed["adaptive"]["simulated_cost"], 23)

    def test_no_certificate_fail_closed(self):
        cases = [Case("unverified-change", True, True, False),
                 Case("real-change", True, False, False)]
        self.assertEqual(evaluate(cases)["adaptive"]["recomputes"], 2)

    def test_no_free_adaptive_advantage_if_review_expensive(self):
        self.assertGreater(evaluate(verify_cost=20)["adaptive"]["simulated_cost"],
                           evaluate(verify_cost=20)["strict"]["simulated_cost"])


if __name__ == "__main__":
    unittest.main()
