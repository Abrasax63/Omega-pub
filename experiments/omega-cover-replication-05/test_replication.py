"""Ten lightweight scientific controls; the 384-run holdout runs ONCE in CI."""
from __future__ import annotations

from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import replication_lab as r


def synthetic_rows():
    """Construct 48 paired fake observations, not any heldout machine truth."""
    rows=[]
    for n in (4,5,6):
        for j in range(16):
            rows.append({
                "size":n,"name":f"S{n}-{j}",
                "exact":{
                    "RANDOM_LEN10":j%2==0,
                    "FIXED_LEN10":j%3==0,
                    "OLD_OMEGA_LEN10":j%5==0,
                    "COVER_DISTINGUISH_LEN10":j%2==0,
                },
                "accuracy":{arm:(0.0 if j%2 else 1.0) for arm in r.ARMS},
            })
    return rows


class ReplicationControls(unittest.TestCase):

    def test_frozen_four_policies_two_caps_and_library_version(self):
        self.assertEqual(r.ARMS,(
            "RANDOM_LEN10","FIXED_LEN10","OLD_OMEGA_LEN10",
            "COVER_DISTINGUISH_LEN10",
        ))
        self.assertEqual(r.CAPS,(300,500))
        self.assertEqual(r.c.EQ_LENGTH,10)
        self.assertEqual(r.c.EQ_ROUND_WORDS,32)
        self.assertEqual(r.c.b.version("aalpy"),"1.6.2")

    def test_all_previous_1148_signatures_accounted_for(self):
        old=r.historical_signatures()
        self.assertEqual(len(old),1148)

    def test_all_new_48_worlds_are_minimal_reachable_and_isomorphism_disjoint(self):
        old=r.historical_signatures()
        result=r.fresh_worlds()
        self.assertEqual(len(result),48)
        self.assertEqual([x["size"] for x in result],[4]*16+[5]*16+[6]*16)
        for row in result:
            self.assertNotIn(row["signature"],old)
            old.add(row["signature"])
            self.assertEqual(len(r.c.reachable(row["world"])),row["size"])
            self.assertTrue(r.c.distinguishable(row["world"]))
        self.assertEqual(len(old),1196)

    def test_world_generation_is_deterministic_and_unselected_by_scores(self):
        first=r.fresh_worlds()
        second=r.fresh_worlds()
        self.assertEqual([x["signature"] for x in first],
                         [x["signature"] for x in second])
        self.assertEqual([x["attempts_cumulative"] for x in first],
                         [x["attempts_cumulative"] for x in second])

    def test_reserved_words_are_128_distinct_and_independent_of_learning(self):
        words=r.reserved_words(6,7)
        self.assertEqual(len(words),128)
        self.assertEqual(len(set(words)),128)
        self.assertTrue(all(12<=len(x)<=20 for x in words))
        self.assertEqual(words,r.reserved_words(6,7))
        self.assertNotEqual(words,r.reserved_words(6,8))

    def test_one_sided_exact_mcnemar_direction_and_ties(self):
        self.assertEqual(r.exact_one_sided_mcnemar(0,0),1)
        self.assertEqual(r.exact_one_sided_mcnemar(3,0),1/8)
        self.assertEqual(r.exact_one_sided_mcnemar(0,3),1)
        self.assertEqual(r.exact_one_sided_mcnemar(2,2),11/16)
        self.assertEqual(r.exact_one_sided_mcnemar(8,0),1/256)
        with self.assertRaises(ValueError):
            r.exact_one_sided_mcnemar(-1,3)

    def test_holm_three_comparator_adjustments_monotone(self):
        names=r.REFS
        result=r.holm_adjust({
            names[0]:0.01,names[1]:0.03,names[2]:0.08})
        self.assertAlmostEqual(result[names[0]],0.03)
        self.assertAlmostEqual(result[names[1]],0.06)
        self.assertAlmostEqual(result[names[2]],0.08)
        self.assertEqual(r.holm_adjust({x:1.0 for x in names}),
                         {x:1.0 for x in names})

    def test_paired_stratified_bootstrap_is_deterministic_and_must_preserve_size(self):
        data=synthetic_rows()
        a=r.paired_stratified_bootstrap(data,r.REFS[0],r.BOOTSTRAP_SEED)
        b=r.paired_stratified_bootstrap(data,r.REFS[0],r.BOOTSTRAP_SEED)
        self.assertEqual(a,b)
        self.assertEqual(a["lower_95"],0)
        self.assertEqual(a["upper_95"],0)
        with self.assertRaises(AssertionError):
            r.paired_stratified_bootstrap(data[:-1],r.REFS[0],r.BOOTSTRAP_SEED)

    def test_budget_failclosed_and_no_evaluation_oracle_during_learning(self):
        from types import SimpleNamespace
        world=r.q.c.resilience.cycle_marker_machine(4)
        for i,arm in enumerate(r.ARMS):
            sul=r.c.b.MeteredBlackBox(world,9)
            state=SimpleNamespace(state_id="single",output_fun={0:0,1:0})
            state.transitions={0:state,1:state}
            hypothesis=SimpleNamespace(initial_state=state,states=[state])
            eq=r.c.MatchedOracle(sul,arm,105+i)
            with self.assertRaises(r.c.b.BudgetExhausted):
                eq.find_cex(hypothesis)
            self.assertEqual(sul.spent,0)
        with patch.object(r.c.b,"exact_equivalence",
                          side_effect=RuntimeError("EXACT_ORACLE_LEAK")),\
             patch.object(r.c.b,"truth_trace",
                          side_effect=RuntimeError("TRUE_WORLD_LEAK")),\
             patch.object(r.c.b,"heldout_score",
                          side_effect=RuntimeError("HELDOUT_LEAK")):
            for arm in r.ARMS:
                _,_,entry=r.c.train(world,arm,200,342)
                self.assertLessEqual(entry["ledger"]["spent_symbols"],200)

    def test_small_real_smoke_has_same_eq_length_and_billed_queries(self):
        world=r.q.c.resilience.cycle_marker_machine(5)
        wordset=r.reserved_words(5,0)
        for idx,arm in enumerate(r.ARMS):
            item=r.c.evaluate_one(world,arm,300,411+idx,wordset)
            t=item["training"]
            ledger=t["ledger"]
            self.assertTrue(0<ledger["spent_symbols"]<=300)
            self.assertEqual(
                sum(x["charge"] for x in ledger["query_log"]),
                ledger["spent_symbols"])
            self.assertEqual(
                t["eq_words_tested"],
                sum(x["phase"]=="EQ" for x in ledger["query_log"]),
            )
            self.assertTrue(all(
                len(x["inputs"])==10
                for x in ledger["query_log"] if x["phase"]=="EQ"
            ))
            self.assertIn(item["exact_equivalence"]["status"],(
                "EXACT_EQUIVALENT","NOT_EQUIVALENT","NO_HYPOTHESIS"))
            if item["exact_equivalence"]["status"]=="EXACT_EQUIVALENT":
                self.assertEqual(item["reserved"]["whole_word_accuracy"],1.0)


if __name__=="__main__":
    unittest.main()
