"""Fifteen regression controls for OMEGA-COUNTEREXAMPLE-COVER-03."""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import cover_lab as c
from mealy_lab import Mealy,digest


def known_machine():
    return c.resilience.cycle_marker_machine(4)


def hypothesis_from_machine(machine):
    from types import SimpleNamespace
    states=[SimpleNamespace(
        state_id=f"s{i}",
        output_fun={a:machine.outputs[i][a] for a in c.b.ALPHABET}
    ) for i in range(machine.size)]
    for i,st in enumerate(states):
        st.transitions={a:states[machine.transitions[i][a]]
                        for a in c.b.ALPHABET}
    return SimpleNamespace(initial_state=states[0],states=states)


class Cover03Controls(unittest.TestCase):

    def test_pinned_AALpy_and_exact_prereg(self):
        self.assertEqual(c.b.version("aalpy"),"1.6.2")
        self.assertEqual(c.EQ_LENGTH,10)
        self.assertEqual(c.PRIMARY,1800)

    def test_exact_historical_1124_signature_inventory(self):
        self.assertEqual(len(c.old_signatures()),1124)

    def test_new_cohort_not_isomorphic_to_old_or_other_new_machines(self):
        new=c.new_worlds()
        self.assertEqual(len(new),12)
        used=c.old_signatures()
        for row in new:
            self.assertNotIn(row["sig"],used)
            used.add(row["sig"])
        self.assertEqual(len(used),1136)

    def test_all_new_worlds_fully_reachable_and_minimal(self):
        cohort=c.new_worlds()
        self.assertEqual([x["n"] for x in cohort],[4]*4+[5]*4+[6]*4)
        for entry in cohort:
            m=entry["world"]
            self.assertEqual(len(c.reachable(m)),m.size)
            self.assertTrue(c.distinguishable(m))

    def test_minimality_filter_detects_indistinguishable_state_pair(self):
        zero=Mealy(
            ((1,0),(0,1),(1,2),(0,2)),
            ((0,0),(0,0),(0,0),(0,0)),
        )
        self.assertFalse(c.distinguishable(zero))

    def test_structural_generator_replay_is_deterministic(self):
        a=c.new_worlds()
        d=c.new_worlds()
        self.assertEqual([r["sig"] for r in a],[r["sig"] for r in d])
        self.assertEqual([r["draws"] for r in a],[r["draws"] for r in d])

    def test_all_four_methods_propose_exactly_ten_symbols(self):
        hypothesis=hypothesis_from_machine(known_machine())
        for arm in c.ARMS:
            oracle=c.MatchedOracle(
                c.b.MeteredBlackBox(known_machine(),2000),arm,100)
            words=[oracle.next_word(hypothesis) for _ in range(34)]
            self.assertTrue(all(len(w)==10 for w in words))
            self.assertTrue(all(set(w)<=set(c.b.ALPHABET) for w in words))

    def test_generated_cover_has_every_hypothesis_transition(self):
        model=hypothesis_from_machine(known_machine())
        oracle=c.MatchedOracle(
            c.b.MeteredBlackBox(known_machine(),2000),
            "COVER_DISTINGUISH_LEN10",100)
        scheduled=oracle.generate_cover_schedule(model)
        self.assertGreaterEqual(len(scheduled),2*len(model.states))
        self.assertEqual(len(oracle.cover_transition_keys),8)
        self.assertGreater(len(oracle.cover_pair_keys),0)

    def test_cover_and_matched_old_omega_proposals_are_replayable(self):
        model=hypothesis_from_machine(known_machine())
        for arm in ("COVER_DISTINGUISH_LEN10","OLD_OMEGA_LEN10"):
            t=c.MatchedOracle(c.b.MeteredBlackBox(known_machine(),3000),
                              arm,seed=501)
            v=c.MatchedOracle(c.b.MeteredBlackBox(known_machine(),900),
                              arm,seed=501)
            self.assertEqual([t.next_word(model) for _ in range(20)],
                             [v.next_word(model) for _ in range(20)])

    def test_budget_fail_closed_has_no_fake_eq_acceptance(self):
        model=hypothesis_from_machine(known_machine())
        for arm in c.ARMS:
            sul=c.b.MeteredBlackBox(known_machine(),9)
            oracle=c.MatchedOracle(sul,arm,seed=101)
            with self.assertRaises(c.b.BudgetExhausted):
                oracle.find_cex(model)
            self.assertEqual(sul.spent,0)
            self.assertEqual(oracle.words_tested,0)
            self.assertEqual(oracle.eq_rounds,1)

    def test_true_SUL_outputs_and_costs_are_recomputed_independently(self):
        world=known_machine()
        for arm in c.ARMS:
            model,queried,t=c.train(world,arm,1200,107)
            ledger=t["ledger"]
            self.assertEqual(c.audit_truth(world,ledger),
                             len(ledger["query_log"]))
            self.assertLessEqual(ledger["spent_symbols"],1200)
            eq=[x for x in ledger["query_log"] if x["phase"]=="EQ"]
            self.assertTrue(all(len(x["inputs"])==10 for x in eq))
            self.assertEqual(len(eq),t["eq_words_tested"])

    def test_no_truth_or_exact_equivalence_leaks_during_training(self):
        world=known_machine()
        with patch.object(c.b,"exact_equivalence",
                          side_effect=RuntimeError("EXACT_ORACLE_LEAK")),\
             patch.object(c.b,"truth_trace",
                          side_effect=RuntimeError("WORLD_EVALUATOR_LEAK")),\
             patch.object(c.b,"heldout_score",
                          side_effect=RuntimeError("HELDOUT_LEAK")):
            for arm in c.ARMS:
                _,_,row=c.train(world,arm,1000,33)
                self.assertGreater(row["ledger"]["spent_symbols"],0)

    def test_truth_equivalence_detects_witness_after_learning(self):
        world=known_machine()
        for arm in c.ARMS:
            model,queried,training=c.train(world,arm,1800,444)
            result=c.b.exact_equivalence(world,model)
            self.assertIn(result["status"],(
                "EXACT_EQUIVALENT","NOT_EQUIVALENT","NO_HYPOTHESIS",
            ))
            if result["status"]=="NOT_EQUIVALENT":
                word=result["counterexample"]
                self.assertNotEqual(
                    c.b.truth_trace(world,word),
                    c.b.predict_mealy(model,word)
                )

    def test_reserved_words_independent_and_never_trained_on(self):
        words=c.test_words(5,1)
        self.assertEqual(len(words),128)
        self.assertEqual(len(set(words)),128)
        self.assertTrue(all(12<=len(x)<=20 for x in words))
        self.assertEqual(words,c.test_words(5,1))
        self.assertNotEqual(words,c.test_words(5,2))

    def test_all_frozen_evaluation_measures_preserve_negative_status(self):
        results=c.run()
        self.assertEqual(results["experiment"],c.EXPERIMENT)
        self.assertEqual(results["prereg_commit"],c.PREREG)
        self.assertEqual(len(results["cases"]),12)
        self.assertEqual(results["arms"],list(c.ARMS))
        self.assertEqual(results["budgets"],[900,1800])
        self.assertEqual(results["all_EQ_words_matched_length"],10)
        self.assertFalse(results["general_gain_proven"])
        self.assertFalse(results["main_modified"])
        self.assertTrue(results["exact_oracle_evaluation_only"])
        self.assertIn(results["status"],(
            "DESCRIPTIVE_COVER_GAIN","NO_DEMONSTRATED_COVER_GAIN"
        ))
        for row in results["cases"]:
            self.assertEqual(row["accessible_states"],row["n"])
            self.assertTrue(row["all_states_distinguishable"])
            for cap in c.BUDGETS:
                for arm in c.ARMS:
                    result=row["budgets"][str(cap)][arm]
                    ledger=result["training"]["ledger"]
                    self.assertLessEqual(ledger["spent_symbols"],cap)
                    self.assertEqual(sum(x["charge"] for x in ledger["query_log"]),
                                     ledger["spent_symbols"])
                    self.assertEqual(sum(x["phase"]=="EQ"
                                         for x in ledger["query_log"]),
                                     result["training"]["eq_words_tested"])
                    self.assertTrue(all(
                        len(x["inputs"])==10
                        for x in ledger["query_log"] if x["phase"]=="EQ"
                    ))


if __name__=="__main__":
    unittest.main()
