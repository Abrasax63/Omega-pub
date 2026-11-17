"""Eight falsifiable controls; passing tests does not replace the 8/8 gate."""
import unittest
from itertools import product
from unittest.mock import patch
import state_split as s


class ScientificControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observed = s.six_zero_observations()
        cls.records = s.validate_observations(cls.observed)
        cls.models, cls.counts = s.enumerate_consistent_models(cls.records)
        cls.reps, cls.classes = s.diversify(cls.models)

    def test_conflicting_prefix_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "CONTRADICTORY"):
            s.validate_observations([
                {"inputs": [1], "outputs": [0]},
                {"inputs": [1,0], "outputs": [1,0]},
            ])

    def test_bad_observations_are_rejected(self):
        invalid = [
            [], [{"inputs": [1,2], "outputs": [0,0]}],
            [{"inputs": [1,0], "outputs": [0]}],
            [{"inputs": [1], "outputs": [2]}],
        ]
        for rows in invalid:
            with self.assertRaises(ValueError):
                s.validate_observations(rows)

    def test_canonical_is_renaming_invariant(self):
        source = s.delayed_marker((1,1,1))
        permutation = (0,2,1)
        t = tuple(tuple(permutation[source[0][permutation[i]][a]]
                        for a in s.ALPHABET) for i in range(3))
        o = tuple(tuple(source[1][permutation[i]][a]
                        for a in s.ALPHABET) for i in range(3))
        self.assertEqual(s.canonical(source), s.canonical((t,o)))

    def test_bounded_space_has_distinct_sizes_and_is_consistent(self):
        self.assertIn((((0,0),), ((0,0),)), self.models)
        self.assertTrue(any(len(m[0]) == 3 for m in self.models))
        self.assertEqual(len(self.models), sum(self.counts.values()))
        for model in self.models:
            self.assertTrue(all(s.trace(model,w) == expected
                                for w,expected in self.records))

    def test_disagreement_for_ten_symbol_word(self):
        word = (1,1,1)+(0,)*7
        self.assertGreater(len({s.trace(m,word) for m in self.models}), 1)
        self.assertLessEqual(len(self.reps), s.MAX_REPRESENTATIVES)
        self.assertGreaterEqual(self.classes, len(self.reps))

    def test_rank_is_deterministic_and_cannot_read_evaluator(self):
        with patch.object(s,"delayed_marker",side_effect=AssertionError("LEAK")):
            a,_ = s.rank_queries(self.reps,self.observed)
            b,_ = s.rank_queries(self.reps,self.observed)
        self.assertEqual(a,b)
        self.assertEqual(len(a),len(set(a)))
        self.assertLessEqual(len(a),32)
        self.assertTrue(all(len(word)==10 for word in a))

    def test_saturated_zero_observations_have_no_false_disagreement(self):
        observations = [{"inputs": list(w), "outputs": [0]*len(w)}
                        for n in (1,2,3) for w in product(s.ALPHABET,repeat=n)]
        models,_ = s.enumerate_consistent_models(
            s.validate_observations(observations))
        reps,classes = s.diversify(models)
        words,_ = s.rank_queries(reps,observations)
        self.assertEqual(classes,1)
        self.assertEqual(words,[])

    def test_8_test_only_sources_and_accounting(self):
        report = s.run_experiment()
        rows = report["eight_test_only_delayed_markers"]
        self.assertEqual(len(rows),8)
        self.assertLessEqual(report["proposed_eq_symbol_cost"],320)
        self.assertEqual(report["proposed_eq_symbol_cost"],
                         10*len(report["selected_eq_words"]))
        hits = sum(row["detected"] for row in rows)
        self.assertEqual(report["all_eight_detected"], hits==8)
        self.assertEqual(report["mechanism_status"],
            "STATE_SPLIT_LOCAL_MECHANISM_VERIFIED" if hits==8 else "NOT_VERIFIED")


if __name__=="__main__":
    unittest.main()
