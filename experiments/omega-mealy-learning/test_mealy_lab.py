"""Independent, no-network regression tests for the first learned Mealy pilot."""
from __future__ import annotations
from functools import cache
from itertools import combinations
from math import inf
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mealy_lab import (
    Mealy, NUM_STATES, PROBES, TRAIN_N, VALIDATION_N, TEST_N,
    exact_teacher, make_cohorts, training_examples, learn_weights,
    initial_weights, memory_items, select_action, features, episode,
    evaluate_cohort, informative, blocks, Check, solve, digest
)


class MealyLearningTests(unittest.TestCase):
    def simple(self):
        return Mealy(((0, 1), (1, 0)), ((0, 0), (1, 1)))

    def test_mealy_reset_and_word_cost(self):
        m=self.simple()
        self.assertEqual(m.observe(0,(1,0)),(0,1))
        self.assertEqual(m.observe(1,(1,0)),(1,0))
        checks=m.checks()
        self.assertEqual(len(checks),6)
        self.assertEqual(tuple(c.cost for c in checks),(1,1,2,2,2,2))
        self.assertEqual(tuple(c.name for c in checks),("0","1","00","01","10","11"))

    def test_known_exact_one_probe_identifies_two_states(self):
        m=self.simple()
        checks=m.checks()
        ref=solve((0,1),checks)
        self.assertEqual(ref["adaptive"],1)
        self.assertEqual(ref["fixed"],1)
        value,_=exact_teacher(checks)
        self.assertEqual(value((0,1)),1)
        for initial in (0,1):
            result=episode(m,initial,"A_fixed",initial_weights(),())
            self.assertEqual(result["cost"],1)
            self.assertEqual(result["belief"],(initial,))
            self.assertEqual(len(result["transcript"]),1)

    def test_nonidentifiable_correctly_abstains(self):
        m=Mealy(((0,0),(1,1)),((0,0),(0,0)))
        ref=solve((0,1),m.checks())
        self.assertIsNone(ref["adaptive"])
        self.assertEqual(informative((0,1),m.checks()),())
        for initial in (0,1):
            result=episode(m,initial,"A_fixed",initial_weights(),())
            self.assertFalse(result["success"])
            self.assertEqual(result["cost"],0)

    def test_canonical_isomorphism(self):
        m=Mealy(((1,2),(2,0),(1,1)),((0,1),(2,0),(1,1)))
        perm=(2,0,1)
        inv={old:new for new,old in enumerate(perm)}
        m2=Mealy(
            tuple(tuple(inv[m.transitions[old][i]] for i in range(2)) for old in perm),
            tuple(m.outputs[old] for old in perm),
        )
        self.assertEqual(m.signature(),m2.signature())
        self.assertNotEqual(m.transitions,m2.transitions)

    def test_group_partition_and_features_no_truth_leak(self):
        m=self.simple()
        group=(0,1)
        actions=informative(group,m.checks())
        self.assertTrue(actions)
        for c in actions:
            f=features(group,c)
            self.assertEqual(len(f),6)
            self.assertEqual(len(blocks(group,c)),2)
            self.assertTrue(all(isinstance(t,float) for t in f))
        self.assertIsNone(select_action((0,),m.checks(),"A_fixed",initial_weights(),()))

    def test_exact_teacher_vs_independent_subset_search(self):
        # Recurrence implemented independently of PR76 adapter for a machine
        # with multiple possible observations and all six probes.
        m=Mealy(((1,2),(2,0),(0,1)),((0,1),(1,0),(2,1)))
        checks=m.checks()
        value,_=exact_teacher(checks)
        @cache
        def brute(g):
            if len(g)==1:
                return 0
            alternatives=[]
            for check in checks:
                outcomes={}
                for state in g:
                    outcomes.setdefault(check.values[state],[]).append(state)
                if len(outcomes)<=1:
                    continue
                alternatives.append(check.cost+max(
                    brute(tuple(x)) for x in outcomes.values()))
            return min(alternatives,default=inf)
        for size in (2,3):
            for sub in combinations(range(3),size):
                self.assertEqual(value(sub),brute(sub))
        self.assertEqual(value((0,1,2)),solve((0,1,2),checks)["adaptive"])

    def test_predeclared_splits_unique_and_deterministic(self):
        a=make_cohorts()
        b=make_cohorts()
        expected={"train":TRAIN_N,"validation":VALIDATION_N,"test":TEST_N}
        seen=set()
        for name,count in expected.items():
            self.assertEqual(len(a[name]["machines"]),count)
            sa=[sig for sig,_ in a[name]["machines"]]
            sb=[sig for sig,_ in b[name]["machines"]]
            self.assertEqual(sa,sb)
            self.assertEqual(len(sa),len(set(sa)))
            self.assertFalse(seen.intersection(sa))
            seen.update(sa)

    def test_parameters_actually_update_using_training_only(self):
        # Simulate the same genuine pairwise optimization used by the pilot.
        examples=[{
            "machine_signature":"train_only",
            "belief_size":2,
            "actions":[
              ("a",(1.,1.,1.,1.,1.,-0.5),0.),
              ("b",(0.5,0.,0.,0.,0.,-1.0),2.),
            ],
        }]
        before=initial_weights()
        after, updates=learn_weights(examples)
        self.assertGreater(updates,0)
        self.assertNotEqual(before,after)
        self.assertGreater(sum(abs(x) for x in after),0)

    def test_holdout_policy_never_reads_hidden_initial(self):
        m=self.simple()
        for arm in ("A_fixed","C_learned"):
            for initial in (0,1):
                result=episode(m,initial,arm,initial_weights(),())
                self.assertTrue(result["success"])
                for step in result["transcript"]:
                    self.assertIn(initial,step["candidates_before"])
                    self.assertIn(initial,step["candidates_after"])

    def test_memory_and_learner_both_use_training_only(self):
        sample=make_cohorts()["train"]["machines"][:3]
        examples,refs=training_examples(sample)
        self.assertEqual(len(refs),3)
        memory=memory_items(examples)
        self.assertTrue(memory)
        self.assertTrue({item[2] for item in memory}.issubset({sig for sig,_ in sample}))
        weights,updates=learn_weights(examples)
        arms=(("A_fixed",initial_weights(),()),
              ("B_memory",initial_weights(),memory),
              ("C_learned",weights,()))
        evaluation=evaluate_cohort(sample,arms)
        self.assertEqual(evaluation["total"],3)
        self.assertLessEqual(evaluation["eligible"],3)
        for row in evaluation["rows"]:
            if row["identifiable_with_six_probes"]:
                for metric in row["arms"].values():
                    self.assertGreaterEqual(metric["worst_regret_to_exact"],0)
                    self.assertTrue(metric["all_states_correctly_identified"])


if __name__=="__main__":
    unittest.main()
