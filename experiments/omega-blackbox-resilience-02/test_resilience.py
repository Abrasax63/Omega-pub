"""Fourteen independent Blackbox-01 resilience and oracle controls."""
from __future__ import annotations

from itertools import product
from types import SimpleNamespace
from unittest.mock import patch
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import resilience_lab as t
b=t.b
from mealy_lab import Mealy


def candidate_machine(machine):
    """A deliberately independent fully specified Mealy hypothesis object."""
    states=[SimpleNamespace(state_id=f"q{i}",
                            output_fun={0:machine.outputs[i][0],
                                        1:machine.outputs[i][1]})
            for i in range(machine.size)]
    for i,state in enumerate(states):
        state.transitions={
            a:states[machine.transitions[i][a]] for a in b.ALPHABET
        }
    return SimpleNamespace(initial_state=states[0],states=states)


def exhaustive_shortest_witness(truth,guess):
    """Enumerates actual words rather than using BFS implementation under test."""
    # At most n_truth * n_guess state pairs can be visited in the product.
    for length in range(1,truth.size*len(guess.states)+1):
        for word in product(b.ALPHABET,repeat=length):
            actual=t.hidden_trace_from(truth,0,word)
            state=guess.initial_state
            predicted=[]
            for a in word:
                predicted.append(state.output_fun[a])
                state=state.transitions[a]
            if actual!=tuple(predicted):
                return tuple(word)
    return None


def basic():
    return t.cycle_marker_machine(4)


class ResilienceTests(unittest.TestCase):

    def test_actual_public_aalpy_pinned_version(self):
        self.assertEqual(b.version("aalpy"),"1.6.2")

    def test_three_worlds_all_physically_reachable(self):
        for n in t.STRESS_SIZES:
            machine=t.cycle_marker_machine(n)
            self.assertEqual(len(t.accessible_truth_states(machine)),n)

    def test_three_worlds_all_behaviorally_distinguishable(self):
        for n in t.STRESS_SIZES:
            machine=t.cycle_marker_machine(n)
            self.assertTrue(t.all_states_distinguishable(machine))
            for left in range(n):
                for right in range(left+1,n):
                    word=(0,)*n
                    self.assertNotEqual(
                        t.hidden_trace_from(machine,left,word),
                        t.hidden_trace_from(machine,right,word),
                    )

    def test_stress_machine_generation_replays_and_no_oracle_shortcut(self):
        a=[t.cycle_marker_machine(n).signature() for n in t.STRESS_SIZES]
        c=[t.cycle_marker_machine(n).signature() for n in t.STRESS_SIZES]
        self.assertEqual(a,c)
        self.assertEqual(len(set(a)),3)

    def test_exact_product_bfs_matches_exhaustive_brute_force_minimal_witness(self):
        rng=random.Random(9791)
        for size in (2,3):
            for _ in range(14):
                a=Mealy(
                    tuple(tuple(rng.randrange(size) for _ in range(2))
                          for _ in range(size)),
                    tuple(tuple(rng.randrange(3) for _ in range(2))
                          for _ in range(size)),
                )
                c=Mealy(
                    tuple(tuple(rng.randrange(size) for _ in range(2))
                          for _ in range(size)),
                    tuple(tuple(rng.randrange(3) for _ in range(2))
                          for _ in range(size)),
                )
                candidate=candidate_machine(c)
                gold=exhaustive_shortest_witness(a,candidate)
                observed=b.exact_equivalence(a,candidate)
                self.assertEqual(
                    observed["status"]=="EXACT_EQUIVALENT",gold is None
                )
                if gold is not None:
                    self.assertEqual(
                        tuple(observed["counterexample"]),gold
                    )
                    self.assertEqual(
                        observed["shortest_counterexample_length"],len(gold)
                    )

    def test_unreachable_physical_states_do_not_break_equivalence(self):
        truth=Mealy(
            ((0,0),(2,2),(1,1)),
            ((1,1),(2,2),(0,0)),
        )
        simple=Mealy(((0,0),(1,1)),((1,1),(0,0)))
        candidate=candidate_machine(simple)
        self.assertEqual(len(t.accessible_truth_states(truth)),1)
        self.assertEqual(
            b.exact_equivalence(truth,candidate)["status"],
            "EXACT_EQUIVALENT",
        )

    def test_deliberately_false_model_gives_real_shortest_witness(self):
        true=basic()
        guess=Mealy(((0,0),(1,1)),((0,0),(0,0)))
        hypothesis=candidate_machine(guess)
        answer=b.exact_equivalence(true,hypothesis)
        shortest=exhaustive_shortest_witness(true,hypothesis)
        self.assertEqual(tuple(answer["counterexample"]),shortest)
        self.assertGreaterEqual(len(shortest),1)

    def test_insufficient_budget_during_eq_must_interrupt_not_accept(self):
        # In PR #136, the selected EQ word is of length >=3 while remaining=2.
        # Returning None would silently declare 'no counterexample' despite
        # executing zero EQ checks, so this is a FAIL-CLOSED requirement.
        sul=b.MeteredBlackBox(basic(),2)
        eq=b.CandidateOracle(
            b.ALPHABET,sul,"FIXED_LSTAR",seed=91
        )
        hypothesis=candidate_machine(basic())
        with self.assertRaises(b.BudgetExhausted):
            eq.find_cex(hypothesis)
        self.assertEqual(eq.words_tested,0)
        self.assertEqual(sul.spent,0)
        self.assertEqual(eq.rounds_log[-1]["checks"],0)
        self.assertEqual(eq.rounds_log[-1]["remaining_budget"],2)

    def test_single_counter_shared_between_membership_and_eq_steps(self):
        sul=b.MeteredBlackBox(basic(),5)
        sul.phase="MQ"
        sul.query((0,1,0))
        sul.phase="EQ"
        with self.assertRaises(b.BudgetExhausted):
            sul.query((1,1,0))
        ledger=sul.summary()
        self.assertEqual(ledger["spent_symbols"],5)
        self.assertEqual(ledger["by_phase_spent"],{"MQ":3,"EQ":2})
        self.assertEqual(ledger["incomplete_queries"],1)
        self.assertEqual(t.assert_ledger_matches_truth(basic(),ledger),2)

    def test_membership_and_eq_query_outputs_independently_recomputed(self):
        for arm in b.ARMS:
            world=t.cycle_marker_machine(4)
            model,queried,record=b.train_one(world,arm,200,seed=333)
            ledger=record["ledger"]
            self.assertEqual(t.assert_ledger_matches_truth(world,ledger),
                             len(ledger["query_log"]))
            self.assertLessEqual(ledger["spent_symbols"],200)
            self.assertTrue(all(x["charge"]==len(x["inputs"])
                                for x in ledger["query_log"]))

    def test_no_exact_oracle_or_heldout_outcomes_during_learning(self):
        world=basic()
        with patch.object(b,"exact_equivalence",
                          side_effect=RuntimeError("ORACLE_LEAK")), \
             patch.object(b,"truth_trace",
                          side_effect=RuntimeError("TRUTH_LEAK")), \
             patch.object(b,"heldout_score",
                          side_effect=RuntimeError("HELDOUT_LEAK")):
            for arm in b.ARMS:
                model,_,record=b.train_one(world,arm,150,seed=103)
                self.assertLessEqual(record["ledger"]["spent_symbols"],150)

    def test_determinism_same_seed_budget_and_world(self):
        world=t.cycle_marker_machine(5)
        for arm in b.ARMS:
            first=b.train_one(world,arm,250,seed=300)
            second=b.train_one(world,arm,250,seed=300)
            self.assertEqual(first[2]["status"],second[2]["status"])
            self.assertEqual(first[2]["ledger"]["spent_symbols"],
                             second[2]["ledger"]["spent_symbols"])
            self.assertEqual(first[2]["ledger"]["queries_sha256"],
                             second[2]["ledger"]["queries_sha256"])
            self.assertEqual(
                b.exact_equivalence(world,first[0])["status"],
                b.exact_equivalence(world,second[0])["status"],
            )

    def test_no_hypothesis_must_be_explicit_and_never_certified(self):
        m=basic()
        model,_,training=b.train_one(m,"RANDOM_LSTAR",2,seed=10)
        result=b.exact_equivalence(m,model)
        self.assertLessEqual(training["ledger"]["spent_symbols"],2)
        if model is None:
            self.assertEqual(result["status"],"NO_HYPOTHESIS")
            self.assertIn("NO_CANDIDATE",training["status"])
        else:
            self.assertIn(result["status"],(
                "EXACT_EQUIVALENT","NOT_EQUIVALENT"))

    def test_external_real_lstar_on_full_six_state_minimal_system(self):
        world=t.cycle_marker_machine(6)
        for arm in b.ARMS:
            model,queried,training=b.train_one(world,arm,400,seed=201)
            ledger=training["ledger"]
            self.assertGreater(ledger["spent_symbols"],0)
            self.assertLessEqual(ledger["spent_symbols"],400)
            self.assertEqual(
                sum(x["charge"] for x in ledger["query_log"]),
                ledger["spent_symbols"]
            )
            exact=b.exact_equivalence(world,model)
            self.assertIn(exact["status"],(
                "EXACT_EQUIVALENT","NOT_EQUIVALENT","NO_HYPOTHESIS"))
            if exact["status"]=="NOT_EQUIVALENT":
                self.assertGreaterEqual(
                    exact["shortest_counterexample_length"],1)


if __name__=="__main__":
    unittest.main()
