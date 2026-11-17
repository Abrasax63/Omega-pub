"""Controls for the frozen three-policy experiment, without consuming the main holdout."""
import unittest
from itertools import product
from unittest.mock import patch

import pilot as p


class ThreePolicyControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observations = p.s.six_zero_observations()
        cls.space, _ = p.s.enumerate_consistent_models(
            p.s.validate_observations(cls.observations))
        cls.train, cls.holdout, cls.eligible, cls.prior = p.select_cohorts(cls.space)

    def test_01_prereg_frozen_configuration(self):
        self.assertEqual(p.PREREG_COMMIT, "8b94886315d463f2e4585ae4576b92f4c2fcfa2e")
        self.assertEqual((p.TRAIN_N, p.HOLDOUT_N), (48, 24))
        self.assertEqual((p.COST_PER_QUERY, p.MAX_QUERIES), (10, 8))
        self.assertEqual((p.COHORT_SEED, p.POLICY_SEED), (54117, 54118))
        self.assertEqual(p.ARMS, ("FIXED", "ACTIVE", "BANDIT"))

    def test_02_cohort_isolation_and_exclusion(self):
        self.assertEqual(len(self.train), 48)
        self.assertEqual(len(self.holdout), 24)
        self.assertEqual(len(set(self.train + self.holdout)), 72)
        prior, _ = p.previous.new_cohort(self.space)
        historical = {p.s.canonical(p.s.delayed_marker(pattern))
                      for pattern in product(p.s.ALPHABET, repeat=3)}
        self.assertFalse(set(prior) & set(self.train + self.holdout))
        self.assertFalse(historical & set(self.train + self.holdout))
        self.assertTrue(all(p.previous.distinguishable(x) and len(x[0]) == 3
                            for x in self.train + self.holdout))

    def test_03_selection_reproducible_without_scores(self):
        again = p.select_cohorts(self.space)
        self.assertEqual((self.train, self.holdout, self.eligible, self.prior), again)

    def test_04_all_worlds_consistent_with_six_public_traces(self):
        records = p.s.validate_observations(self.observations)
        self.assertTrue(all(p.s.trace(world, word) == out
                            for world in self.train + self.holdout
                            for word, out in records))

    def test_05_bandit_updates_only_selected_arm(self):
        b = p.ObservedBandit()
        b.observe("FIXED", 2.5)
        self.assertEqual(b.counts, {"FIXED": 1, "ACTIVE": 0})
        self.assertEqual(b.snapshot()["mean_reward"]["ACTIVE"], None)
        self.assertEqual(b.snapshot()["mean_reward"]["FIXED"], 2.5)
        self.assertEqual(b.choose({"FIXED": (0,), "ACTIVE": (1,)},
                                  False, None), "FIXED")

    def test_06_train_updates_and_records_only_real_paid_actions(self):
        import random
        b = p.ObservedBandit()
        outcome = p.run_episode("BANDIT", self.train[0], self.observations,
                                 self.space, bandit=b, training=True,
                                 rng=random.Random(p.POLICY_SEED))
        self.assertEqual(sum(b.counts.values()), outcome["queries_paid"])
        self.assertGreater(outcome["queries_paid"], 0)
        self.assertEqual(sum(b.total_reward.values()),
                         sum(x["training_reward"] for x in outcome["query_log"]))

    def test_07_holdout_cannot_modify_bandit(self):
        b = p.ObservedBandit()
        b.observe("ACTIVE", 2.0)
        before = b.snapshot()
        result = p.run_episode("BANDIT", self.holdout[0], self.observations,
                                self.space, bandit=b, training=False)
        self.assertEqual(before, b.snapshot())
        self.assertTrue(all(x["training_reward"] is None
                            for x in result["query_log"]))

    def test_08_equal_symbol_budget_and_no_repeat_payments(self):
        for arm in p.ARMS:
            b = p.ObservedBandit()
            result = p.run_episode(arm, self.train[1], self.observations,
                                    self.space, bandit=b)
            self.assertLessEqual(result["symbols_paid"], 80)
            self.assertEqual(result["symbols_paid"], sum(
                x["cost"] for x in result["query_log"]))
            words = [tuple(x["word"]) for x in result["query_log"]]
            self.assertEqual(len(words), len(set(words)))
            self.assertTrue(all(len(word) == 10 for word in words))

    def test_09_independent_post_paid_exact_trace(self):
        world = self.train[2]
        outcome = p.run_episode("ACTIVE", world, self.observations, self.space)
        for row in outcome["query_log"]:
            self.assertEqual(tuple(row["observed_outputs"]),
                             p.s.trace(world, row["word"]))
            self.assertEqual(row["detected"], tuple(row["observed_outputs"]) !=
                             p.s.trace(p.previous.BASE, row["word"]))
            self.assertGreater(row["after"], 0)
            self.assertLessEqual(row["after"], row["before"])

    def test_10_fail_closed_on_forged_paid_response(self):
        world = self.train[0]
        with patch.object(p.previous, "paid_query",
                          return_value=(9,) * 10):
            with self.assertRaises(AssertionError):
                p.run_episode("FIXED", world, self.observations, self.space)

    def test_11_invalid_arm_and_training_rejected(self):
        with self.assertRaises(ValueError):
            p.run_episode("UNKNOWN", self.train[0], self.observations, self.space)
        with self.assertRaises(ValueError):
            p.run_episode("ACTIVE", self.train[0], self.observations,
                          self.space, training=True)

    def test_12_paired_score_counters_include_failures(self):
        def row(detected, cost):
            return {"detected": detected, "false_certificate": False,
                    "symbols_paid": cost}
        trials = [
            {"arms": {"FIXED": row(True, 20),
                      "ACTIVE": row(True, 10), "BANDIT": row(True, 10)}},
            {"arms": {"FIXED": row(False, 80),
                      "ACTIVE": row(True, 20), "BANDIT": row(False, 80)}},
        ]
        scores = p.scores_for(trials)
        self.assertEqual(scores["BANDIT"]["detected"], 1)
        self.assertEqual(scores["BANDIT"]["mean_paid_symbols"], 45)
        self.assertEqual(scores["FIXED"]["total_paid_symbols"], 100)
        self.assertEqual(scores["ACTIVE"]["mean_paid_symbols"], 15)


if __name__ == "__main__":
    unittest.main()
