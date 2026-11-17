"""Fifteen frozen local guards; these do not execute the new reserved holdout."""
import random
import unittest
from itertools import product
from unittest.mock import patch
import cost_to_go as c


class CostToGoControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.menu = c.previous.menu_words()
        cls.space, _ = c.s.enumerate_consistent_models(
            c.s.validate_observations(c.s.six_zero_observations()))
        cls.pools, cls.eligible, cls.excluded, cls.prior = c.fresh_pools(
            cls.space, cls.menu)
        cls.train = c.build_instances(cls.pools["train"], c.TRAIN_N, 0)

    def test_01_frozen_protocol_and_actions(self):
        self.assertEqual(c.PREREG_COMMIT,
                         "df94bba543d5e661005efcb892935dab1ecf6d89")
        self.assertEqual((c.TRAIN_N, c.TEST_N, c.MAX_QUERIES), (48, 24, 12))
        self.assertEqual(c.POLICIES, ("BALANCED", "PRICE_AWARE",
            "IMMEDIATE_CONTEXTUAL", "RETURN_GLOBAL", "RETURN_CONTEXTUAL"))
        self.assertEqual(c.UNRESOLVED_PENALTY, 150)

    def test_02_fresh_worlds_and_no_train_test_overlap(self):
        self.assertGreaterEqual(self.eligible, 72)
        self.assertEqual(len(self.pools["train"]), 48)
        self.assertEqual(len(self.pools["test"]), 24)
        self.assertEqual(len(set(self.pools["train"] + self.pools["test"])), 72)

    def test_03_exclusion_of_every_previous_cohort(self):
        p159, _, _ = c.previous.partition_models(self.space, self.menu)
        seen = set(sum((p159[k] for k in ("train", "calib", "test")), []))
        p145, _ = c.previous.a.new_cohort(self.space)
        t157, v157, _, _ = c.previous.old.select_cohorts(self.space)
        t158, v158, _, _ = c.previous.previous.select_new_cohorts(self.space)
        seen.update(p145 + t157 + v157 + t158 + v158)
        seen.update(c.s.canonical(c.s.delayed_marker(p))
                    for p in product(c.s.ALPHABET, repeat=3))
        self.assertFalse(seen & set(self.pools["train"] + self.pools["test"]))

    def test_04_unique_terminal_signatures_and_nonconstant(self):
        models = self.pools["train"] + self.pools["test"]
        signatures = [tuple(c.s.trace(x, word)[-1] for word in self.menu)
                      for x in models]
        self.assertEqual(len(set(signatures)), 72)
        self.assertTrue(all(any(w) and not all(w) for w in signatures))

    def test_05_deterministic_cohorts(self):
        self.assertEqual((self.pools, self.eligible, self.excluded, self.prior),
                         c.fresh_pools(self.space, self.menu))

    def test_06_training_instances_have_sixteen_real_candidates(self):
        self.assertEqual(len(self.train), 48)
        for row in self.train:
            self.assertEqual(len(row["candidates"]), 16)
            self.assertIn(row["hidden"], row["candidates"])
            self.assertEqual(len(set(row["candidates"])), 16)
            self.assertEqual(row["tariff"], c.TARIFFS[row["index"] % 2])

    def test_07_cost_to_go_action_and_cell_distinct(self):
        policy = c.CostToGo(contextual=True)
        policy.observe("BALANCED", "ZERO_CHEAP_LARGE", 71)
        policy.observe("PRICE_AWARE", "ZERO_CHEAP_LARGE", 26)
        self.assertEqual(policy.counts, {"BALANCED": 1, "PRICE_AWARE": 1})
        self.assertEqual(policy.choose(c.ACTIONS, "ZERO_CHEAP_LARGE", False, None),
                         "PRICE_AWARE")
        self.assertEqual(policy.estimate("BALANCED", "ZERO_CHEAP_LARGE"), 71)
        self.assertEqual(policy.estimate("BALANCED", "ONE_CHEAP_LARGE"), 71)

    def test_08_training_observes_only_selected_action(self):
        row = self.train[0]
        policy = c.CostToGo(contextual=False)
        out = c.run_episode("RETURN_GLOBAL", row, self.menu, policy,
                            True, random.Random(c.GLOBAL_SEED))
        self.assertEqual(sum(policy.counts.values()),
                         sum(x["updated"] for x in out["log"]))
        self.assertTrue(all(x["action"] in c.ACTIONS for x in out["log"]))

    def test_09_exact_post_paid_last_bit_and_survivors(self):
        row = self.train[1]
        ep = c.run_episode("PRICE_AWARE", row, self.menu)
        candidates = list(row["candidates"])
        for event in ep["log"]:
            self.assertEqual(event["observed_last_bit"],
                             c.s.trace(row["hidden"], event["word"])[-1])
            survivors = [m for m in candidates
                         if c.s.trace(m, event["word"])[-1] ==
                         event["observed_last_bit"]]
            self.assertEqual(len(candidates), event["before"])
            self.assertEqual(len(survivors), event["after"])
            candidates = survivors
        self.assertEqual(len(candidates), ep["remaining_models"])

    def test_10_equivalent_proposals_never_learn_preference(self):
        row = self.train[2]
        opts = c.previous.propose(row["candidates"], set(), self.menu,
                                  row["tariff"])
        word = opts["PRICE_AWARE"]
        b = c.CostToGo(contextual=True)
        with patch.object(c.previous, "propose",
                          side_effect=[{"BALANCED": word, "PRICE_AWARE": word}, {}]):
            result = c.run_episode("RETURN_CONTEXTUAL", row, self.menu,
                                   b, True, random.Random(1))
        self.assertEqual(sum(b.counts.values()), 0)
        self.assertEqual(result["queries_paid"], 1)
        self.assertFalse(result["log"][0]["updated"])

    def test_11_monte_carlo_targets_are_true_suffix_costs(self):
        row = self.train[3]
        b = c.CostToGo(contextual=True)
        result = c.run_episode("RETURN_CONTEXTUAL", row, self.menu, b,
                                True, random.Random(1))
        costs = [x["paid"] for x in result["log"]]
        penalty = 0 if result["certified"] else c.UNRESOLVED_PENALTY
        for i, event in enumerate(result["log"]):
            expected = sum(costs[i:]) + penalty
            if event["updated"]:
                self.assertEqual(event["cost_to_go_target"], expected)
            else:
                self.assertIsNone(event["cost_to_go_target"])

    def test_12_immediate_target_uses_only_paid_one_step(self):
        row = self.train[4]
        b = c.previous.RewardBandit(contextual=True)
        result = c.run_episode("IMMEDIATE_CONTEXTUAL", row, self.menu,
                                b, True, random.Random(1))
        for step in result["log"]:
            expected = 4*int(step["after"]==1) + 2*(
                step["before"]-step["after"])/step["before"] - step["paid"]/20
            self.assertAlmostEqual(step["immediate_reward"], expected)
            self.assertIsNone(step["cost_to_go_target"])

    def test_13_frozen_evaluation_cannot_change_parameters(self):
        row = self.train[5]
        for policy in ("IMMEDIATE_CONTEXTUAL", "RETURN_GLOBAL", "RETURN_CONTEXTUAL"):
            b = (c.previous.RewardBandit(contextual=True)
                 if policy == "IMMEDIATE_CONTEXTUAL"
                 else c.CostToGo(contextual=policy=="RETURN_CONTEXTUAL"))
            before = b.snapshot()
            result = c.run_episode(policy, row, self.menu, b, False)
            self.assertEqual(b.snapshot(), before)
            self.assertTrue(all(x["cost_to_go_target"] is None and
                                x["immediate_reward"] is None and not x["updated"]
                                for x in result["log"]))

    def test_14_wrong_paid_answer_is_fatal(self):
        row = self.train[6]
        with patch.object(c.previous, "paid_last_bit", return_value=9):
            with self.assertRaises(AssertionError):
                c.run_episode("PRICE_AWARE", row, self.menu)

    def test_15_every_cost_and_failure_counted(self):
        def ep(hit, cost):
            return {"certified":hit, "false_certificates":0,
                    "queries_paid": 2, "cost_paid":cost}
        trials = [
            {"arms":{k:ep(True,20) for k in c.POLICIES}},
            {"arms":{k:ep(False,80) for k in c.POLICIES}},
        ]
        scores = c.summarize(trials, c.POLICIES)
        self.assertEqual(scores["RETURN_CONTEXTUAL"]["certified"],1)
        self.assertEqual(scores["RETURN_CONTEXTUAL"]["total_cost"],100)
        self.assertEqual(scores["RETURN_CONTEXTUAL"]["mean_cost"],50)


if __name__ == "__main__":
    unittest.main()
