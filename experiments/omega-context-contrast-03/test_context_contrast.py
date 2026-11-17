"""Fifteen pre-holdout controls. No test executes the reserved-world episodes."""
import random
import unittest
from itertools import product
from unittest.mock import patch

import context_contrast as c


class ContrastControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.menu = c.menu_words()
        cls.space, _ = c.s.enumerate_consistent_models(
            c.s.validate_observations(c.s.six_zero_observations()))
        cls.pools, cls.eligible, cls.excluded = c.partition_models(cls.space, cls.menu)
        cls.train = c.build_instances(cls.pools["train"], c.TRAIN_N, 0)
        cls.calib = c.build_instances(cls.pools["calib"], c.CALIB_N, 1000)

    def test_01_preregistered_constants(self):
        self.assertEqual(c.PREREG_COMMIT, "05017609751aeae1a3d181e9ef6eefc000d833e4")
        self.assertEqual(c.N_CANDIDATES, 16)
        self.assertEqual((c.TRAIN_N, c.CALIB_N, c.HOLDOUT_N), (48, 24, 24))
        self.assertEqual(c.POLICIES, ("BALANCED", "PRICE_AWARE", "GLOBAL", "CONTEXTUAL"))
        self.assertEqual(c.MAX_QUERIES, 12)

    def test_02_menu_64_fixed_and_reproducible(self):
        self.assertEqual(len(self.menu), 64)
        self.assertEqual(len(set(self.menu)), 64)
        self.assertEqual(self.menu, c.menu_words())
        self.assertTrue(all(len(x) == 10 for x in self.menu))
        self.assertEqual(self.menu[:8], tuple(c.s.seed_words()))

    def test_03_three_nonoverlapping_model_pools(self):
        pools = self.pools
        self.assertEqual(tuple(len(pools[x]) for x in ("train", "calib", "test")),
                         (64, 32, 32))
        self.assertEqual(len(set(pools["train"] + pools["calib"] + pools["test"])), 128)
        self.assertGreaterEqual(self.eligible, 128)

    def test_04_models_exclude_all_previous_heldout_cohorts(self):
        pr145, _ = c.a.new_cohort(self.space)
        p157, q157, _, _ = c.old.select_cohorts(self.space)
        p158, q158, _, _ = c.previous.select_new_cohorts(self.space)
        pr143 = {c.s.canonical(c.s.delayed_marker(x))
                 for x in product(c.s.ALPHABET, repeat=3)}
        current = set(sum((self.pools[k] for k in ("train","calib","test")), []))
        self.assertFalse(current & (set(pr145+p157+q157+p158+q158)|pr143))

    def test_05_pools_unique_behavioral_signatures(self):
        all_models = sum((self.pools[k] for k in ("train","calib","test")), [])
        patterns = {tuple(c.s.trace(model,word)[-1] for word in self.menu)
                    for model in all_models}
        self.assertEqual(len(patterns), 128)
        self.assertTrue(all(any(p) and not all(p) for p in patterns))

    def test_06_instances_have_hidden_and_exactly_sixteen(self):
        for row in self.train[:5] + self.calib[:5]:
            self.assertEqual(len(row["candidates"]), 16)
            self.assertEqual(len(set(row["candidates"])), 16)
            self.assertIn(row["hidden"], row["candidates"])
            self.assertEqual(row["tariff"], c.TARIFFS[row["index"] % 2])

    def test_07_cost_depends_on_symbol_and_tariff(self):
        word = (0,)*7 + (1,)*3
        self.assertEqual(c.query_price(word, (1,5)), 22)
        self.assertEqual(c.query_price(word, (5,1)), 38)
        with self.assertRaises(ValueError):
            c.query_price((0,1), (1,5))

    def test_08_proposers_see_only_candidates_and_public_tariff(self):
        row = self.train[0]
        options = c.propose(row["candidates"], set(), self.menu, row["tariff"])
        self.assertEqual(set(options), {"BALANCED","PRICE_AWARE"})
        self.assertTrue(all(w in self.menu for w in options.values()))
        self.assertEqual(options, c.propose(row["candidates"], set(), self.menu, row["tariff"]))

    def test_09_observed_last_bit_only(self):
        row = self.train[1]
        q = self.menu[3]
        self.assertEqual(c.paid_last_bit(row["hidden"], q),
                         c.s.trace(row["hidden"],q)[-1])
        self.assertIsInstance(c.paid_last_bit(row["hidden"],q),int)

    def test_10_fail_closed_on_forged_output(self):
        row = self.train[0]
        with patch.object(c,"paid_last_bit",return_value=9):
            with self.assertRaises(AssertionError):
                c.episode("BALANCED", row, self.menu)

    def test_11_bandit_updates_only_executed_action_and_cell(self):
        b = c.RewardBandit(contextual=True)
        b.observe("BALANCED","ZERO_CHEAP_LARGE",1.25)
        self.assertEqual(b.counts, {"BALANCED":1,"PRICE_AWARE":0})
        self.assertEqual(b.cell_counts["ZERO_CHEAP_LARGE"]["PRICE_AWARE"],0)
        self.assertEqual(b.value("BALANCED","ZERO_CHEAP_LARGE"),1.25)
        self.assertEqual(b.value("BALANCED","ONE_CHEAP_LARGE"),1.25)

    def test_12_equal_proposals_do_not_train_preference(self):
        row = self.train[2]
        b = c.RewardBandit(contextual=True)
        word = self.menu[8]
        with patch.object(c,"propose",side_effect=[
            {"BALANCED":word,"PRICE_AWARE":word},{}
        ]):
            result = c.episode("CONTEXTUAL",row,self.menu,b,True,random.Random(1))
        self.assertEqual(sum(b.counts.values()),0)
        self.assertEqual(result["queries_paid"],1)
        self.assertFalse(result["log"][0]["updated"])

    def test_13_costs_posterior_no_repeat_probes(self):
        row = self.train[3]
        for arm in c.POLICIES:
            b = c.RewardBandit(contextual=(arm == "CONTEXTUAL"))
            result = c.episode(arm,row,self.menu,b)
            self.assertLessEqual(result["queries_paid"],12)
            self.assertEqual(result["cost_paid"],sum(x["paid"] for x in result["log"]))
            words = [tuple(x["word"]) for x in result["log"]]
            self.assertEqual(len(set(words)),len(words))
            self.assertTrue(all(x["before"]>x["after"]>0 for x in result["log"]))
            self.assertEqual(result["certified"],result["remaining"]==1)

    def test_14_freeze_on_evaluation(self):
        row = self.train[4]
        b = c.RewardBandit(contextual=True)
        b.observe("PRICE_AWARE","ONE_CHEAP_SMALL",0.5)
        snapshot = b.snapshot()
        result = c.episode("CONTEXTUAL",row,self.menu,b,False)
        self.assertEqual(snapshot,b.snapshot())
        self.assertTrue(all(x["reward_training"] is None and not x["updated"]
                            for x in result["log"]))

    def test_15_gate_negative_is_not_a_success(self):
        calibration = c.calibration_stage(self.calib,self.menu)
        self.assertEqual(len(calibration["runs"]),24)
        self.assertIn(calibration["gate"],("INFORMATIVE_CALIBRATION","UNINFORMATIVE_CONTEXTS"))
        self.assertEqual(sum(r["tariff"]==list(c.TARIFFS[0]) for r in calibration["runs"]),12)
        self.assertEqual(sum(r["tariff"]==list(c.TARIFFS[1]) for r in calibration["runs"]),12)
        d=calibration["initial_price_disagreements"]
        w=calibration["paired_wins_both_certified"]
        expected=(d["ZERO_CHEAP"]>=6 and d["ONE_CHEAP"]>=6 and
                  w["BALANCED"]>=1 and w["PRICE_AWARE"]>=1)
        self.assertEqual(calibration["gate"]=="INFORMATIVE_CALIBRATION", expected)


if __name__ == "__main__":
    unittest.main()
