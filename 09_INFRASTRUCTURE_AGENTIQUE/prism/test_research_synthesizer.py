"""Scoped tests of symbolic research proposal generation; no LLM or theorem claim."""
import unittest

from research_synthesizer import (FEATURES, exact_minimal_contradiction,
                                  structural_features, learn, conjunction, tally,
                                  invariance_checks, counterfactual_checks,
                                  raw_families)


class StructuralInductionTests(unittest.TestCase):
    def fixtures(self):
        forced = ()
        odd_cycle = ((0, 1, 0), (1, 2, 0), (2, 3, 0), (3, 0, 1))
        even_cycle = ((0, 1, 0), (1, 2, 0), (2, 3, 0), (3, 0, 0))
        return forced, odd_cycle, even_cycle

    def test_independent_oracle_distinguishes_signed_from_unsigned_cycles(self):
        forced, odd_cycle, even_cycle = self.fixtures()
        self.assertTrue(exact_minimal_contradiction(4, forced, odd_cycle))
        self.assertFalse(exact_minimal_contradiction(4, forced, even_cycle))
        self.assertTrue(structural_features(4, forced, odd_cycle)["cycle_four_quotient"])
        self.assertTrue(structural_features(4, forced, even_cycle)["cycle_four_quotient"])
        self.assertNotEqual(structural_features(4, forced, odd_cycle)["odd_signed_cycle"],
                            structural_features(4, forced, even_cycle)["odd_signed_cycle"])

    def test_learns_a_rule_not_hardcoded_verdicts(self):
        # Training labels are independently specified for every feature combination.
        sample = []
        for cycle, odd in ((True, True), (True, False), (False, True), (False, False)):
            f = {name: False for name in FEATURES}
            f["cycle_four_quotient"] = cycle
            f["odd_signed_cycle"] = odd
            sample.append({"features": f, "truth": cycle and odd})
        selected = learn(sample)
        self.assertEqual(set(selected["atoms"]),
                         {"cycle_four_quotient", "odd_signed_cycle"})
        self.assertEqual(selected["training_errors"], 0)
        self.assertEqual(tally(sample, lambda row: conjunction(row, selected["atoms"]))["FP"], 0)

    def test_cross_representational_invariance_and_counterfactual(self):
        forced, odd, even = self.fixtures()
        cases = [
            {"T": (1, 2, 3, 0), "pair": (0, 1), "forced": forced,
             "events": odd, "truth": True, "features": structural_features(4, forced, odd)},
            {"T": (1, 2, 3, 0), "pair": (0, 2), "forced": forced,
             "events": even, "truth": False, "features": structural_features(4, forced, even)},
        ]
        rule = ("cycle_four_quotient", "odd_signed_cycle")
        self.assertEqual(invariance_checks(cases, rule)["disagreements"], 0)
        counter = counterfactual_checks(cases, rule)
        self.assertEqual(counter["checked"], 2)
        self.assertEqual(counter["truth_changed"], 2)
        self.assertEqual(counter["disagreements"], 0)

    def test_wrong_structural_rule_is_refuted_by_counterexample(self):
        _, _, even_cycle = self.fixtures()
        features = structural_features(4, (), even_cycle)
        self.assertTrue(features["cycle_four_quotient"])
        self.assertFalse(exact_minimal_contradiction(4, (), even_cycle))

    def test_family_disjoint_and_scope_limited(self):
        train = list(raw_families("TRAIN-C4-C3-N8"))
        reserve = list(raw_families("RESERVE-C4-C3-N9"))
        self.assertEqual(len(train[0]), 8)
        self.assertEqual(len(reserve[0]), 9)
        self.assertFalse(set(train) & set(reserve))
        with self.assertRaises(ValueError):
            exact_minimal_contradiction(10, (), ((0, 1, 0),)*4)

    def test_incoherent_forced_system_cannot_claim_valid_oracle(self):
        forced = ((0, 1, 0), (0, 1, 1))
        events = ((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0))
        with self.assertRaises(ValueError):
            exact_minimal_contradiction(4, forced, events)
        with self.assertRaises(ValueError):
            structural_features(4, forced, events)


if __name__ == "__main__":
    unittest.main()
