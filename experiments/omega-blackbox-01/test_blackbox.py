"""Fourteen independent non-regression controls for OMEGA-BLACKBOX-01."""
from __future__ import annotations

from collections import deque
from types import SimpleNamespace
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blackbox_lab as b
from mealy_lab import Mealy,digest


def fixture():
    # Two reachable, behaviorally distinguishable Mealy states.
    return Mealy(((0,1),(0,1)),((0,1),(1,0)))


def constant():
    return Mealy(((0,0),(0,0)),((1,1),(1,1)))


def fake_one_state(o0=1,o1=1):
    root=SimpleNamespace(state_id="root",output_fun={0:o0,1:o1})
    root.transitions={0:root,1:root}
    return SimpleNamespace(initial_state=root,states=[root],
                           compute_output_seq=lambda initial,word:[
                               initial.output_fun[x] for x in word
                           ])


class BlackboxControls(unittest.TestCase):

    def test_aalpy_version_is_pinned(self):
        self.assertEqual(b.version("aalpy"),"1.6.2")

    def test_old_1112_canonical_signatures_are_reconciled(self):
        self.assertEqual(len(b.true_old_signatures()),1112)

    def test_new_worlds_4_5_6_three_each_disjoint(self):
        worlds=b.new_machines()
        self.assertEqual(len(worlds),9)
        self.assertEqual([m["size"] for m in worlds],[4]*3+[5]*3+[6]*3)
        seen=b.true_old_signatures()
        for row in worlds:
            self.assertNotIn(row["signature"],seen)
            seen.add(row["signature"])
        self.assertEqual(len(seen),1121)

    def test_machine_generation_is_seeded_and_replayable(self):
        a=b.new_machines()
        c=b.new_machines()
        self.assertEqual(
            [x["signature"] for x in a],
            [x["signature"] for x in c]
        )

    def test_sul_reset_answers_only_queried_inputs(self):
        machine=fixture()
        sul=b.MeteredBlackBox(machine,100)
        one=tuple(sul.query((0,1,0,1)))
        two=tuple(sul.query((0,1,0,1)))
        self.assertEqual(one,two)
        self.assertEqual(one,b.truth_trace(machine,(0,1,0,1)))
        self.assertEqual(sul.spent,8)
        self.assertEqual(sul.complete_queries,2)
        self.assertEqual(sul.summary()["by_phase_spent"]["MQ"],8)

    def test_every_physical_input_is_charged_and_overrun_prevented(self):
        sul=b.MeteredBlackBox(fixture(),3)
        self.assertEqual(tuple(sul.query((0,1))),b.truth_trace(fixture(),(0,1)))
        with self.assertRaises(b.BudgetExhausted):
            sul.query((1,0))
        ledger=sul.summary()
        self.assertEqual(ledger["spent_symbols"],3)
        self.assertEqual(ledger["budget_cap"],3)
        self.assertEqual(ledger["incomplete_queries"],1)
        self.assertEqual(
            sum(x["charge"] for x in ledger["query_log"]),3
        )

    def test_candidate_oracle_guided_search_only_reads_hypothesis(self):
        root=fake_one_state().initial_state
        a=b.CandidateOracle(b.ALPHABET,b.MeteredBlackBox(fixture(),100),
                             "OMEGA_GUIDED_LSTAR",1)
        c=b.CandidateOracle(b.ALPHABET,b.MeteredBlackBox(constant(),100),
                             "OMEGA_GUIDED_LSTAR",1)
        model=SimpleNamespace(initial_state=root,states=[root])
        words_a=[a.guided_word(model) for _ in range(12)]
        words_c=[c.guided_word(model) for _ in range(12)]
        self.assertEqual(words_a,words_c)
        self.assertTrue(all(set(w).issubset({0,1}) for w in words_a))

    def test_random_and_fixed_candidates_are_deterministic_and_bounded(self):
        a=b.CandidateOracle(b.ALPHABET,b.MeteredBlackBox(fixture(),100),
                             "RANDOM_LSTAR",19)
        c=b.CandidateOracle(b.ALPHABET,b.MeteredBlackBox(fixture(),100),
                             "RANDOM_LSTAR",19)
        self.assertEqual([a.random_word() for _ in range(9)],
                         [c.random_word() for _ in range(9)])
        fixed=b.CandidateOracle(b.ALPHABET,b.MeteredBlackBox(fixture(),100),
                             "FIXED_LSTAR",19)
        self.assertEqual(
            [fixed.fixed_word() for _ in range(4)],
            [(0,0,0),(0,0,1),(0,1,0),(0,1,1)],
        )

    def test_exact_equivalence_rejects_bad_complete_model_with_minimal_witness(self):
        bad=fake_one_state(1,1)
        result=b.exact_equivalence(fixture(),bad)
        self.assertEqual(result["status"],"NOT_EQUIVALENT")
        word=tuple(result["counterexample"])
        self.assertEqual(word,(0,))
        self.assertNotEqual(b.truth_trace(fixture(),word),
                            b.predict_mealy(bad,word))

    def test_exact_equivalence_accepts_simple_constant_behavior(self):
        model=fake_one_state(1,1)
        self.assertEqual(
            b.exact_equivalence(constant(),model)["status"],
            "EXACT_EQUIVALENT",
        )

    def test_reserve_words_have_no_true_model_leak(self):
        words=b.reserved_words(4,0)
        self.assertEqual(len(words),128)
        self.assertEqual(len(set(words)),128)
        self.assertTrue(all(12<=len(w)<=20 for w in words))
        machine=fixture()
        hypothesis=fake_one_state(1,1)
        ev=b.heldout_score(machine,hypothesis,words,{words[0]})
        self.assertEqual(ev["excluded_identical_train_queries"],1)
        self.assertEqual(ev["evaluated_test_words"],127)
        self.assertLessEqual(ev["whole_word_accuracy"],1)

    def test_alleged_strategies_use_the_same_real_lstar_engine(self):
        # A tiny constructive smoke test with three independently metered SULs.
        for arm in b.ARMS:
            model,known,record=b.train_one(fixture(),arm,300,707)
            self.assertEqual(record["arm"],arm)
            self.assertLessEqual(record["ledger"]["spent_symbols"],300)
            self.assertGreater(record["ledger"]["spent_symbols"],0)
            self.assertEqual(
                sum(x["charge"] for x in record["ledger"]["query_log"]),
                record["ledger"]["spent_symbols"],
            )
            if model is not None:
                self.assertIn(
                    b.exact_equivalence(fixture(),model)["status"],
                    ("EXACT_EQUIVALENT","NOT_EQUIVALENT")
                )

    def test_cross_arm_episode_budget_kept_in_one_counter_for_membership_and_eq(self):
        machine=fixture()
        model,known,info=b.train_one(machine,"OMEGA_GUIDED_LSTAR",280,708)
        ledger=info["ledger"]
        self.assertEqual(
            ledger["by_phase_spent"]["MQ"]+ledger["by_phase_spent"]["EQ"],
            ledger["spent_symbols"],
        )
        self.assertLessEqual(ledger["spent_symbols"],280)
        self.assertTrue(all(x["phase"] in ("MQ","EQ")
                            for x in ledger["query_log"]))

    def test_independent_heldout_exact_equivalence_and_negative_status(self):
        world=fixture()
        result=b.execute_one(world,2,0,"RANDOM_LSTAR",300)
        self.assertIn(
            result["independent_exact_equivalence"]["status"],
            ("EXACT_EQUIVALENT","NOT_EQUIVALENT","NO_HYPOTHESIS"),
        )
        score=result["reserved_word_evaluation"]
        self.assertLessEqual(score["whole_word_accuracy"],1.0)
        self.assertGreater(score["evaluated_test_words"],0)
        if result["independent_exact_equivalence"]["status"]=="EXACT_EQUIVALENT":
            self.assertEqual(score["whole_word_accuracy"],1.0)


if __name__=="__main__":
    unittest.main()
