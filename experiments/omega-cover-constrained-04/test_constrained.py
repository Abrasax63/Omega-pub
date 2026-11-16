"""Eight fail-closed controls for a new, budget-constrained OMEGA-COVER holdout."""
from __future__ import annotations
from unittest.mock import patch
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import constrained_lab as q


class ConstrainedTests(unittest.TestCase):
    def test_true_four_arm_policy_unchanged(self):
        self.assertEqual(q.ARMS,(
            "RANDOM_LEN10","FIXED_LEN10","OLD_OMEGA_LEN10",
            "COVER_DISTINGUISH_LEN10"))
        self.assertEqual(q.c.EQ_LENGTH,10)
        self.assertEqual(q.c.EQ_ROUND_WORDS,32)
        self.assertEqual(q.CAPS,(300,500))

    def test_1136_old_worlds_excluded(self):
        self.assertEqual(len(q.old_signatures()),1136)

    def test_all_new_worlds_disjoint_and_fully_minimal(self):
        old=q.old_signatures()
        rows=q.fresh_worlds()
        self.assertEqual(len(rows),12)
        self.assertEqual([x["n"] for x in rows],[4]*4+[5]*4+[6]*4)
        for row in rows:
            self.assertNotIn(row["signature"],old)
            old.add(row["signature"])
            self.assertEqual(len(q.c.reachable(row["world"])),row["n"])
            self.assertTrue(q.c.distinguishable(row["world"]))
        self.assertEqual(len(old),1148)

    def test_world_generators_have_exact_seed_replay(self):
        a=q.fresh_worlds()
        b=q.fresh_worlds()
        self.assertEqual([x["signature"] for x in a],
                         [x["signature"] for x in b])

    def test_heldout_words_separate_and_frozen(self):
        for n in (4,5,6):
            a=q.reserved_words(n,0)
            self.assertEqual(len(a),128)
            self.assertEqual(len(set(a)),128)
            self.assertTrue(all(12<=len(x)<=20 for x in a))
            self.assertEqual(a,q.reserved_words(n,0))
            self.assertNotEqual(a,q.reserved_words(n,1))

    def test_budget_under_ten_in_eq_fails_closed(self):
        world=q.c.resilience.cycle_marker_machine(4)
        from types import SimpleNamespace
        s=SimpleNamespace(state_id="single",output_fun={0:0,1:0})
        s.transitions={0:s,1:s}
        hypothesis=SimpleNamespace(initial_state=s,states=[s])
        for arm in q.ARMS:
            sul=q.c.b.MeteredBlackBox(world,9)
            oracle=q.c.MatchedOracle(sul,arm,seed=123)
            with self.assertRaises(q.c.b.BudgetExhausted):
                oracle.find_cex(hypothesis)
            self.assertEqual(sul.spent,0)

    def test_exact_model_not_used_during_training(self):
        world=q.c.resilience.cycle_marker_machine(4)
        with patch.object(q.c.b,"exact_equivalence",
                          side_effect=RuntimeError("EXACT_ORACLE_LEAK")),\
             patch.object(q.c.b,"truth_trace",
                          side_effect=RuntimeError("WORLD_LEAK")):
            for i,arm in enumerate(q.ARMS):
                _,_,row=q.c.train(world,arm,200,500+i)
                self.assertLessEqual(row["ledger"]["spent_symbols"],200)

    def test_real_smoke_300_symbols_is_metered_and_audited(self):
        world=q.c.resilience.cycle_marker_machine(5)
        words=q.reserved_words(5,0)
        for arm in q.ARMS:
            result=q.c.evaluate_one(world,arm,300,999,words)
            t=result["training"]
            led=t["ledger"]
            self.assertTrue(0<led["spent_symbols"]<=300)
            self.assertEqual(sum(z["charge"] for z in led["query_log"]),
                             led["spent_symbols"])
            self.assertEqual(sum(z["phase"]=="EQ"
                                 for z in led["query_log"]),t["eq_words_tested"])
            self.assertTrue(all(len(z["inputs"])==10
                                for z in led["query_log"] if z["phase"]=="EQ"))


if __name__=="__main__":
    unittest.main()
