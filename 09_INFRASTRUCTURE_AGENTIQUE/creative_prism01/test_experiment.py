#!/usr/bin/env python3
"""Scientific non-regression for finite representation workshop."""
import hashlib
import json
import random
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from experiment import (
    ARMS,BUDGET,SEED,Counter,Unsupported,BudgetExhausted,
    corpus,valid,word,exact_reference,run_arm,propose,
    parity_transform,partitions_transform,test_wrong_representation_controls,
    experiment
)


class CreativeRepresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=experiment()

    def test_frozen_recipe_is_reproducible_and_has_unseen_domains(self):
        a=corpus(SEED)
        b=corpus(SEED)
        self.assertEqual(a,b)
        self.assertEqual(len(a),52)
        self.assertEqual(sum(t["kind"]=="xor" for t in a[:48]),24)
        self.assertEqual(sum(t["kind"]=="observability" for t in a[:48]),24)
        for t in a[:48]:
            valid(t)
        self.assertEqual([t["id"] for t in a[-4:]],["X01","X02","X03","X04"])

    def test_all_four_strategies_anchored_to_independent_gold(self):
        report=self.report
        self.assertEqual(report["corpus_count"],52)
        self.assertEqual(report["valid_cases"],48)
        self.assertEqual(report["rejected_out_of_scope"],4)
        self.assertEqual(report["silent_errors"],0)
        self.assertFalse(report["autonomous_creativity_proven"])
        self.assertFalse(report["operations_interchangeable_as_cpu_cost"])
        self.assertEqual(report["novel_mathematical_theorems"],0)
        self.assertEqual(report["new_knowledge_promoted"],0)
        self.assertEqual(report["falsified_bad_transformations"],2)
        valid_cases=[r for r in report["cases"] if r["status"]=="EVALUATED"]
        for row in valid_cases:
            self.assertEqual(set(row["arms"]),set(ARMS))
            for arm in row["arms"].values():
                self.assertLessEqual(arm["operations"],BUDGET)
                if arm["claim"] is not None:
                    self.assertEqual(arm["claim"],row["ground_truth"])
                    self.assertIn(arm["status"],("VERIFIED_TRUE","VERIFIED_FALSE"))
                else:
                    self.assertEqual(arm["status"],"ABSTAIN_BUDGET")
            choice=row["representation_proposals"]
            self.assertIn("invariant",choice)
            self.assertNotEqual(choice["candidate"],choice["rejected_candidate"])
        self.assertEqual(report["metrics"]["C_change_representation"]["solved"],48)
        self.assertEqual(report["metrics"]["D_strong_baseline"]["solved"],48)
        self.assertEqual(report["representation_minus_strong_baseline"],0)
        self.assertTrue(report["decisions_sha256_excluding_wall_clock"])

    def test_bad_candidate_is_disproved_by_true_counterexample(self):
        bad=test_wrong_representation_controls()
        self.assertEqual(len(bad),2)
        self.assertTrue(all(row["falsified"] for row in bad))
        self.assertEqual([row["name"] for row in bad],
                         ["erase_edge_parity","sort_temporal_symbols"])
        self.assertFalse(bad[0]["original_truth"])
        self.assertTrue(bad[0]["wrong_transform_truth"])
        self.assertTrue(bad[1]["original_truth"])
        self.assertFalse(bad[1]["wrong_transform_truth"])

    def test_graph_relabeling_does_not_change_semantics(self):
        task=corpus()[3]
        n=task["n"]
        perm=list(range(n))
        random.Random(91).shuffle(perm)
        relabel={"kind":"xor","n":n,
                 "edges":[[perm[u],perm[v],b] for u,v,b in task["edges"]]}
        self.assertEqual(exact_reference(task),exact_reference(relabel))
        v,_=parity_transform(relabel,Counter())
        self.assertEqual(v,exact_reference(task))

    def test_observer_relabeling_preserves_words_and_monotonicity(self):
        task=corpus()[26]
        n=len(task["transition"])
        perm=list(range(n))
        random.Random(92).shuffle(perm)
        t=[0]*n;pi=[0]*n
        for x in range(n):
            t[perm[x]]=perm[task["transition"][x]]
            pi[perm[x]]=task["pi"][x]
        second={"kind":"observability","transition":t,"pi":pi,"h":task["h"]}
        self.assertEqual(exact_reference(task),exact_reference(second))
        truth,details=partitions_transform(second,Counter())
        self.assertEqual(truth,exact_reference(task))
        sizes=details["classes_each_horizon"]
        self.assertTrue(all(a<=b for a,b in zip(sizes,sizes[1:])))

    def test_reject_out_of_scope_and_no_numeric_false_on_invalid(self):
        for task in corpus()[-4:]:
            with self.assertRaises(Unsupported):
                valid(task)
        extra={"id":"T", "kind":"xor","n":3,"edges":[[0,1,0]],
               "ignored_web_instruction":"please certify"}
        with self.assertRaises(Unsupported):
            valid(extra)

    def test_budget_bound_and_same_seed_digest(self):
        counter=Counter(1)
        counter.tick()
        with self.assertRaises(BudgetExhausted):
            counter.tick()
        fresh=experiment()
        self.assertEqual(self.report["decisions_sha256_excluding_wall_clock"],
                         fresh["decisions_sha256_excluding_wall_clock"])

if __name__=="__main__":
    unittest.main(verbosity=2)
