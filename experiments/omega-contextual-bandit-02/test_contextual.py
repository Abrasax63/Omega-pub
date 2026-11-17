"""14 controls. Never evaluate the reserved 24 machines in unit tests."""
import random
import unittest
from itertools import product
from unittest.mock import patch
import contextual_lab as c


class ContextControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = c.s.six_zero_observations()
        cls.space, _ = c.s.enumerate_consistent_models(
            c.s.validate_observations(cls.obs))
        cls.train, cls.reserved, cls.eligible, cls.excluded = c.select_new_cohorts(cls.space)

    def test_01_contract_and_budget(self):
        self.assertEqual(c.PREREG_COMMIT, "10f94b228d1806f9576dda9078be226d8bba07a6")
        self.assertEqual((c.TRAIN_N, c.HOLDOUT_N, c.MAX_QUERIES), (48, 24, 8))
        self.assertEqual(c.POLICIES, ("ACTIVE", "COST_AWARE", "GLOBAL", "CONTEXTUAL"))
        self.assertEqual(c.TARIFFS, ((1, 4), (4, 1)))

    def test_02_prerecorded_holdout_exclusions(self):
        past_train, past_test, _, _ = c.old.select_cohorts(self.space)
        earlier, _ = c.a.new_cohort(self.space)
        earliest = {c.s.canonical(c.s.delayed_marker(x))
                    for x in product(c.s.ALPHABET, repeat=3)}
        current = set(self.train + self.reserved)
        self.assertEqual(len(current), 72)
        self.assertEqual(len(self.train), 48)
        self.assertEqual(len(self.reserved), 24)
        self.assertFalse(current & (set(past_train + past_test + earlier) | earliest))

    def test_03_cohorts_reproducible_and_score_free(self):
        self.assertEqual((self.train, self.reserved, self.eligible, self.excluded),
                         c.select_new_cohorts(self.space))
        self.assertGreaterEqual(self.eligible, 72)

    def test_04_models_fit_public_six_traces(self):
        rows = c.s.validate_observations(self.obs)
        for world in self.train[:5]:
            self.assertTrue(c.a.distinguishable(world))
            self.assertEqual(len(world[0]), 3)
            self.assertTrue(all(c.s.trace(world, w) == outputs for w, outputs in rows))

    def test_05_tariff_is_actual_symbol_cost(self):
        word = (0,) * 7 + (1,) * 3
        self.assertEqual(c.price(word, (1, 4)), 19)
        self.assertEqual(c.price(word, (4, 1)), 31)
        with self.assertRaises(ValueError):
            c.price((0, 1), (1, 4))

    def test_06_context_depends_only_on_observed_price_and_belief(self):
        self.assertEqual(c.context_key((1, 4), 64), "ZERO_CHEAP_LARGE")
        self.assertEqual(c.context_key((4, 1), 63), "ONE_CHEAP_SMALL")

    def test_07_candidate_words_match_known_hypothesis_space(self):
        options = c.candidate_choices(self.space, self.obs, (1, 4))
        self.assertIn("ACTIVE", options)
        self.assertTrue(set(options) <= set(c.DECISIONS))
        self.assertTrue(all(len(w) == 10 for w in options.values()))
        self.assertTrue(all(tuple(row["inputs"]) not in options.values() for row in self.obs))

    def test_08_cell_update_separate_from_global(self):
        b = c.MeanBandit(contextual=True)
        b.observe("ACTIVE", "ZERO_CHEAP_LARGE", 2.5)
        self.assertEqual(b.global_counts["ACTIVE"], 1)
        self.assertEqual(b.cell_counts["ZERO_CHEAP_LARGE"]["ACTIVE"], 1)
        self.assertEqual(b.estimate("ACTIVE", "ZERO_CHEAP_LARGE"), 2.5)
        self.assertEqual(b.estimate("ACTIVE", "ONE_CHEAP_LARGE"), 2.5)

    def test_09_global_policy_learns_without_cells(self):
        b = c.MeanBandit(contextual=False)
        b.observe("COST_AWARE", "ZERO_CHEAP_LARGE", 2.0)
        b.observe("ACTIVE", "ONE_CHEAP_SMALL", -1.0)
        self.assertEqual(b.cell_counts, {})
        self.assertEqual(b.choose({"ACTIVE": (0,), "COST_AWARE": (1,)},
                                  "ZERO_CHEAP_LARGE", False, None), "COST_AWARE")

    def test_10_training_updates_real_observed_rewards(self):
        b = c.MeanBandit(contextual=True)
        ep = c.run_episode("CONTEXTUAL", self.train[0], self.obs, self.space,
                           c.TARIFFS[0], b, True, random.Random(c.CONTEXT_SEED))
        self.assertGreater(ep["queries_paid"], 0)
        self.assertEqual(ep["queries_paid"], len(ep["log"]))
        self.assertEqual(sum(b.global_counts.values()), sum(
            e["updated_model"] for e in ep["log"]))
        for row in ep["log"]:
            value = (4 * int(row["detected"]) +
                     2 * (row["before"]-row["after"]) / row["before"] -
                     row["paid"] / 10)
            self.assertAlmostEqual(row["reward_training"], value)

    def test_11_evaluation_never_updates_weights(self):
        b = c.MeanBandit(contextual=True)
        b.observe("COST_AWARE", "ZERO_CHEAP_LARGE", 1.0)
        frozen = b.snapshot()
        ep = c.run_episode("CONTEXTUAL", self.train[1], self.obs, self.space,
                           c.TARIFFS[1], b, False)
        self.assertEqual(b.snapshot(), frozen)
        self.assertTrue(all(row["reward_training"] is None and
                            not row["updated_model"] for row in ep["log"]))

    def test_12_paired_cost_budgets_and_no_duplicate_payments(self):
        world = self.train[2]
        for arm in c.POLICIES:
            b = c.MeanBandit(contextual=(arm == "CONTEXTUAL"))
            ep = c.run_episode(arm, world, self.obs, self.space,
                               c.TARIFFS[0], b)
            self.assertLessEqual(ep["queries_paid"], c.MAX_QUERIES)
            self.assertLessEqual(ep["cost_paid"], 320)
            self.assertEqual(ep["cost_paid"], sum(e["paid"] for e in ep["log"]))
            words = [tuple(e["word"]) for e in ep["log"]]
            self.assertEqual(len(words), len(set(words)))

    def test_13_post_paid_outputs_verified_and_rejection_of_forgery(self):
        world = self.train[3]
        ep = c.run_episode("ACTIVE", world, self.obs, self.space, c.TARIFFS[0])
        self.assertTrue(all(tuple(row["outputs"]) == c.s.trace(world, row["word"])
                            for row in ep["log"]))
        with patch.object(c.a, "paid_query", return_value=(9,) * 10):
            with self.assertRaises(AssertionError):
                c.run_episode("ACTIVE", world, self.obs, self.space, c.TARIFFS[0])

    def test_14_scores_include_all_undetected_cases(self):
        def row(hit, cost, q):
            return {"detected": hit, "false_certificate": False,
                    "cost_paid": cost, "queries_paid": q}
        trials = [
            {"arms": {name: row(True, 20, 1) for name in c.POLICIES}},
            {"arms": {name: row(False, 80, 8) for name in c.POLICIES}},
        ]
        scores = c.summarize(trials)
        self.assertEqual(scores["CONTEXTUAL"]["detected"], 1)
        self.assertEqual(scores["CONTEXTUAL"]["mean_cost"], 50)
        self.assertEqual(scores["CONTEXTUAL"]["mean_queries"], 4.5)


if __name__ == "__main__":
    unittest.main()
