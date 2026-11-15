import unittest
from itertools import combinations, permutations
from collective_observability import (
    parity_world, trajectories, projected_distribution, walsh,
    inspect_observations, endpoint_relation, pair_only_baseline,
    independent_support_audit, run)


class CollectiveObservabilityTests(unittest.TestCase):
    def test_all_lower_order_marginals_equal(self):
        for n in range(3, 7):
            a = trajectories(parity_world(n, 0), n)
            b = trajectories(parity_world(n, 1), n)
            for size in range(1, n):
                for coords in combinations(range(n), size):
                    self.assertEqual(projected_distribution(a, coords),
                                     projected_distribution(b, coords))

    def test_walsh_first_full_order(self):
        for n in range(3, 7):
            a = trajectories(parity_world(n, 0), n)
            b = trajectories(parity_world(n, 1), n)
            self.assertEqual(walsh(a, tuple(range(n))), 1)
            self.assertEqual(walsh(b, tuple(range(n))), -1)
            self.assertEqual(inspect_observations(a, b)["first_separating_horizon"], n)

    def test_endpoint_relation_same_even_at_long_horizons(self):
        for n in range(3, 7):
            a = trajectories(parity_world(n, 0), 3*n + 1)
            b = trajectories(parity_world(n, 1), 3*n + 1)
            for h in range(1, 3*n + 1):
                self.assertEqual(endpoint_relation(a, h), endpoint_relation(b, h))

    def test_pair_only_baseline_cannot_distinguish(self):
        for n in range(3, 7):
            a = trajectories(parity_world(n, 0), n)
            b = trajectories(parity_world(n, 1), n)
            self.assertEqual(pair_only_baseline(a, b), "indistinguishable")
            self.assertTrue(independent_support_audit(a,b,n-1)["equal"])
            self.assertFalse(independent_support_audit(a,b,n)["equal"])

    def test_permutation_invariance_and_negative_controls(self):
        a = trajectories(parity_world(3,0),3)
        b = trajectories(parity_world(3,1),3)
        for order in permutations(range(3)):
            aa = tuple(tuple(row[i] for i in order) for row in a)
            bb = tuple(tuple(row[i] for i in order) for row in b)
            self.assertEqual(inspect_observations(aa, bb)["first_separating_horizon"], 3)
        self.assertIsNone(inspect_observations(a, a)["first_separating_horizon"])
        self.assertEqual(pair_only_baseline(a, a), "indistinguishable")
        self.assertEqual(pair_only_baseline(((0,0,0),), ((1,0,0),)), "different")

    def test_output_does_not_claim_omega_run(self):
        for n in range(3, 7):
            result = run(n)
            self.assertEqual(result["first_separating_horizon"], n)
            self.assertFalse(result["omega_planner_executed"])
            self.assertEqual(result["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
