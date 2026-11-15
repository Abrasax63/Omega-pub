import unittest
from obs_col05 import (
    N, ACTIONS, TRAIN, HELD_OUT, WORLDS, MAX_DEGREE,
    TransitionOracle, hidden_transition, monomials, feature_row, rank_gf2,
    fit_bit, fit_system, minimal_fit, predict, choose_probe,
    walsh_observed_invariants, score_world, run,
)


class TestObsCol05(unittest.TestCase):
    def test_split_exact_and_no_overlap(self):
        self.assertEqual(len(TRAIN), 26)
        self.assertEqual(len(HELD_OUT), 6)
        self.assertFalse(set(TRAIN) & set(HELD_OUT))
        self.assertEqual(set(TRAIN) | set(HELD_OUT), set(range(1 << N)))

    def test_training_oracle_rejects_heldout(self):
        o = TransitionOracle("quadratic")
        with self.assertRaises(ValueError):
            o.observe("pulse", 15)
        with self.assertRaises(ValueError):
            o.evaluate("pulse", 0)

    def test_feature_dimension_and_exact_rank(self):
        self.assertEqual([len(monomials(d)) for d in (1, 2, 3)], [6, 16, 26])
        for d in (1, 2, 3):
            design = [feature_row(x, d) for x in TRAIN]
            self.assertEqual(rank_gf2(design), len(monomials(d)))

    def test_gaussian_fit_inconsistency(self):
        self.assertIsNone(fit_bit([(0, 0), (0, 1)], 3, 0))
        self.assertIsNone(fit_system([(0, 0), (0, 1)], 3))

    def test_probe_selector_independent_of_world(self):
        for name in WORLDS:
            o = TransitionOracle(name)
            observations, remaining = [], list(TRAIN)
            while remaining:
                x = choose_probe(observations, remaining)
                observations.append((x, o.observe("pulse", x)))
                remaining.remove(x)
            self.assertEqual(tuple(x for x, _ in observations), TRAIN)
        self.assertEqual(len(set(TRAIN)), 26)

    def test_affine_control(self):
        r = score_world("affine")
        self.assertEqual(r["inferred_degrees"], {"pulse": 1, "bind": 1})
        self.assertEqual(r["holdout_correct"], 12)
        self.assertEqual(r["affine_baseline_correct"], 12)
        self.assertEqual(r["status"], "WITHIN_HOLDOUT_CHECKS")

    def test_quadratic_discovery(self):
        r = score_world("quadratic")
        self.assertEqual(r["inferred_degrees"], {"pulse": 2, "bind": 2})
        self.assertTrue(r["promotions"]["pulse"])
        self.assertTrue(r["promotions"]["bind"])
        self.assertEqual(r["holdout_correct"], 12)
        self.assertEqual(r["cubic_baseline_correct"], 12)

    def test_cubic_discovery(self):
        r = score_world("cubic")
        self.assertEqual(r["inferred_degrees"], {"pulse": 3, "bind": 3})
        self.assertTrue(any(x["to_degree"] == 3 for x in r["promotions"]["pulse"]))
        self.assertTrue(any(x["to_degree"] == 3 for x in r["promotions"]["bind"]))
        self.assertEqual(r["holdout_correct"], 12)

    def test_quartic_ood_guard(self):
        r = score_world("quartic_ood")
        self.assertEqual(r["status"], "OUT_OF_FAMILY_WARNING")
        self.assertEqual(r["inferred_degrees"], {"pulse": 2, "bind": 2})
        self.assertEqual(r["holdout_correct"], 10)
        self.assertEqual([e["state"] for e in r["heldout_mismatches"]], [15, 31])
        self.assertTrue(all(e["action"] == "pulse" for e in r["heldout_mismatches"]))

    def test_p1_used_and_no_llm_or_certificate(self):
        result = run()
        self.assertEqual(len(result["cases"]), 4)
        self.assertEqual(result["llm_calls"], 0)
        self.assertTrue(result["not_autonomous_open_world_discovery"])
        for case in result["cases"]:
            self.assertEqual(case["p1_calls"], 52)
            self.assertEqual(case["holdout_total"], 12)
            self.assertEqual(case["cubic_baseline_correct"], case["holdout_correct"])
            self.assertFalse(case["certified_universal_law"])
            self.assertEqual(case["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
