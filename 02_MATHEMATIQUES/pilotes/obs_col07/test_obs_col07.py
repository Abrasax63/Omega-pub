"""OBS-COL-07: test actual model synthesis, bounded oracle and real P1."""
import unittest
from obs_col07 import (
    WORLDS, generator, truth, BlackBox, Membership, BoundedLStar,
    predict, independent_minimal_count, all_words, episode, run,
    H, EVAL_LENGTHS,
)


class TestObsCol07(unittest.TestCase):
    def test_registered_worlds(self):
        self.assertEqual(len(WORLDS), 6)
        self.assertEqual([len(generator(w)[2]) for w in WORLDS],
                         [2, 3, 4, 2, 3, 9])

    def test_generator_semantics(self):
        self.assertEqual([truth(generator("CYCLE3"), "p"*k)
                          for k in range(5)], [0, 1, 1, 0, 1])
        self.assertEqual([truth(generator("DELAY9_OOD"), "p"*k)
                          for k in range(9)], [0]*8 + [1])
        self.assertEqual(truth(generator("MIX3"), "ppr"), 0)

    def test_oracle_enforces_holdout_split(self):
        box = BlackBox("TOGGLE2")
        with self.assertRaises(ValueError):
            box.membership("p"*8)
        with self.assertRaises(ValueError):
            box.evaluate("p"*7)
        self.assertEqual(box.membership("pp"), 0)

    def test_membership_cache_and_no_world_label(self):
        box = BlackBox("CYCLE3")
        memo = Membership(box, use_p1=True)
        self.assertEqual(memo("p"), 1)
        self.assertEqual(memo("p"), 1)
        self.assertEqual(memo.p1_calls, 1)
        self.assertEqual(box.train_log, ["p"])
        self.assertTrue(memo.mission_ids[0].startswith("OBS-COL-07-"))
        self.assertNotIn("CYCLE3", memo.mission_ids[0])

    def test_independent_minimization(self):
        self.assertEqual([independent_minimal_count(generator(w)) for w in WORLDS],
                         [2, 3, 4, 2, 3, 9])

    def test_lstar_constructs_states_without_target_count_input(self):
        result = episode("CYCLE3")
        self.assertEqual(result["learned_states"], 3)
        self.assertEqual(result["holdout_errors"], 0)
        self.assertTrue(result["same_model_as_classical"])
        self.assertTrue(result["same_probe_order_as_classical"])

    def test_out_of_horizon_falsification(self):
        result = episode("DELAY9_OOD")
        self.assertEqual(result["learned_states"], 1)
        self.assertGreater(result["holdout_errors"], 0)
        self.assertEqual(result["status"], "OUT_OF_HORIZON_WARNING")
        self.assertIn("p"*8, result["first_errors"])

    def test_training_queries_do_not_use_reserved_sequences(self):
        box = BlackBox("MIX3")
        memo = Membership(box, use_p1=True)
        BoundedLStar(memo).learn()
        self.assertTrue(all(len(s) <= H for s in box.train_log))
        self.assertEqual(box.eval_log, [])
        self.assertEqual(memo.p1_calls, len(memo.cache))

    def test_correct_holdout_count(self):
        self.assertEqual(len(list(all_words(8, 10))), 1792)
        self.assertEqual(EVAL_LENGTHS, (8, 9, 10))

    def test_full_comparison(self):
        report = run()
        self.assertEqual(report["model_calls"], 0)
        self.assertTrue(report["no_true_equivalence_oracle"])
        self.assertFalse(report["p1_selects_probes"])
        self.assertEqual(len(report["worlds"]), 6)
        for item, expected_states in zip(report["worlds"][:5], (2, 3, 4, 2, 3)):
            self.assertEqual(item["learned_states"], expected_states)
            self.assertEqual(item["holdout_errors"], 0)
            self.assertEqual(item["holdout_total"], 1792)
            self.assertEqual(item["p1_calls"], item["query_count"])
            self.assertEqual(item["query_count"], item["baseline_query_count"])
            self.assertTrue(item["same_model_as_classical"])
            self.assertTrue(item["same_probe_order_as_classical"])
            self.assertFalse(item["scientifically_certified"])
            self.assertEqual(item["model_calls"], 0)
        self.assertEqual(report["worlds"][-1]["status"], "OUT_OF_HORIZON_WARNING")


if __name__ == "__main__":
    unittest.main()
