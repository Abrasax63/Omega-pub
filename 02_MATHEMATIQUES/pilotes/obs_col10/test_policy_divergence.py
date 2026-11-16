"""OBS-COL-10: pre-holdout policy divergence gate, real L# / Omega P1."""
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction

from generate_manifests import generate
from common_eq import FIXTURES
from benchmark import external_fixture
from policy_divergence import (
    AdaptiveEqOracle, coverage_ranking, model_probe_features, run,
)


class TestPolicyDivergence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        generate(cls.dir)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_ranking_never_queries_target(self):
        model, _ = external_fixture(*FIXTURES[0])
        words = (("a",), ("b",), ("a", "b"), ("b", "a"))
        original = model.current_state
        ranked = coverage_ranking(model, words, memory=True)
        self.assertEqual(set(ranked), set(words))
        self.assertEqual(model.current_state, original)
        self.assertTrue(len(ranked) == len(words))

    def test_scores_exactly_follow_preregistered_fraction(self):
        model, _ = external_fixture(*FIXTURES[0])
        words = (("a",), ("b",), ("a", "b"), ("b", "a"))
        known = {("a",)}
        ranking = coverage_ranking(model, words, known, memory=True)
        score = {}
        for w in words:
            cov, flips = model_probe_features(model, w)
            novelty = sum(tuple(w[:i]) not in known for i in range(1, len(w)+1))
            score[w] = Fraction(4*cov+2*flips)+Fraction(novelty,len(w)+1)
        self.assertEqual(ranking, tuple(sorted(words, key=lambda w: (-score[w],len(w),words.index(w)))))

    def test_policy_does_not_change_candidate_universe(self):
        model, _ = external_fixture(*FIXTURES[0])
        words = (("a",), ("b",), ("a", "b"), ("b", "a"))
        for policy in ("fixed", "coverage_only", "omega_candidate"):
            from aalpy.SULs import AutomatonSUL
            obj = AdaptiveEqOracle(["a","b"], AutomatonSUL(model), words, policy=policy)
            selected = obj.proposed_order(model)
            self.assertEqual(len(selected), len(words))
            self.assertEqual(set(selected), set(words))
            self.assertEqual(obj.known_prefixes, set())

    def test_malformed_policy_fails(self):
        model, _ = external_fixture(*FIXTURES[0])
        from aalpy.SULs import AutomatonSUL
        with self.assertRaises(ValueError):
            AdaptiveEqOracle(["a", "b"], AutomatonSUL(model), (("a",),), policy="secret")

    def test_actual_learning_three_arm_calibration(self):
        result = run(self.dir)
        self.assertEqual(result["pilot"], "OBS-COL-10")
        self.assertTrue(result["calibration_only_public_models"])
        self.assertFalse(result["omega_p1_selects_probes"])
        self.assertTrue(result["omega_like_eq_policy_selects_probes"])
        self.assertFalse(result["new_independent_blind_holdout_executed"])
        self.assertEqual(len(result["results"]), 9)
        for filename, _ in FIXTURES:
            rows = [r for r in result["results"] if r["fixture"] == filename]
            self.assertEqual(set(r["requested_policy"] for r in rows),
                             {"fixed", "coverage_only", "omega_candidate"})
            for r in rows:
                self.assertEqual(r["evaluation_count"], 256)
                self.assertGreater(r["evaluation_unseen_count"], 0)
                self.assertLessEqual(r["physical_resets"], 10000)
                self.assertLessEqual(r["physical_symbols"], 50000)
                self.assertEqual(r["eq_policy"], r["requested_policy"])
                self.assertFalse(r["omega_gains_demonstrated"])
                self.assertFalse(r["equivalence_certified"])
            adapted = next(r for r in rows if r["requested_policy"]=="omega_candidate")
            self.assertEqual(adapted["p1_calls"], adapted["physical_resets"])
            self.assertEqual(next(r for r in rows if r["requested_policy"]=="fixed")["p1_calls"], 0)


if __name__ == "__main__":
    unittest.main()
