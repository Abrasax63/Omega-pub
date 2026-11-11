"""Regression and falsification tests for preregistered WPMS transfer.

No WPMS test-fold outcomes are used in unit-test hyperparameter fitting.
The toy XOR construction confirms lookahead may outperform greedy *on train*
but does not assert a gain on a real external scenario.
"""
import copy
from fractions import Fraction
import math
import unittest

from aslib_wpms_cost_sensitive import (
    SOURCE_COMMIT,SHA,EXPECTED_CASES,EXPECTED_SOLVERS,
    validate_description,tree_fit,tree_predict,train_medians,
    POLICIES,
)
from aslib_external_benchmark import train_normalizer,normalize,score_measurement


class CostSensitiveTreeTests(unittest.TestCase):
    @staticmethod
    def sample():
        ids=["00","01","10","11"]
        coords={"00":(0.0,0.0),"01":(0.0,1.0),
                "10":(1.0,0.0),"11":(1.0,1.0)}
        data={
            "features":coords,
            "algorithms":("A","B"),
            "runs":{},
            "costs":{id:0.15 for id in ids},
            "folds":{id:1 for id in ids},
            "ids":ids,
        }
        for id in ids:
            preferred="A" if id in ("00","11") else "B"
            data["runs"][id]={
                "A":(1.0 if preferred=="A" else 10.0,"ok"),
                "B":(1.0 if preferred=="B" else 10.0,"ok"),
            }
        return data,ids

    def test_xor_requires_two_step_cost_lookahead(self):
        data,ids=self.sample()
        vectors={id:data["features"][id] for id in ids}
        thresholds=train_medians(ids,vectors)
        self.assertEqual(thresholds,(0.5,0.5))
        c0,n0=tree_fit(ids,data,vectors,thresholds,depth=1)
        cg,ng=tree_fit(ids,data,vectors,thresholds,depth=2,mode="greedy")
        co,no=tree_fit(ids,data,vectors,thresholds,depth=2,mode="lookahead")
        self.assertEqual((c0,cg,co),(22.0,22.0,4.0))
        self.assertEqual(ng["action"],"solve")
        self.assertEqual(no["action"],"split")
        self.assertEqual(no["feature"],0)
        for id in ids:
            desired="A" if id in ("00","11") else "B"
            self.assertEqual(tree_predict(vectors[id],no),desired)

    def test_tree_order_invariance_and_no_test_label_leakage(self):
        data,ids=self.sample()
        vectors=data["features"]
        thresholds=train_medians(ids,vectors)
        original=tree_fit(ids,data,vectors,thresholds,mode="lookahead")
        self.assertEqual(original,tree_fit(ids[::-1],data,vectors,thresholds,
                                          mode="lookahead"))
        altered=copy.deepcopy(data)
        altered["runs"]["11"]["A"]=(18000.,"timeout")
        altered["runs"]["11"]["B"]=(5.,"ok")
        # Train on three examples; the fourth is a held-out target.
        train=ids[:3]
        a=tree_fit(train,data,vectors,thresholds,mode="lookahead")
        b=tree_fit(train,altered,vectors,thresholds,mode="lookahead")
        self.assertEqual(a,b)

    def test_costs_charged_once_and_source_sha_pinned(self):
        data,ids=self.sample()
        self.assertEqual(score_measurement("00","A",data,True),
                         (1.15,True,1.0,0.15))
        self.assertEqual(score_measurement("00","A",data,False),
                         (1.0,True,1.0,0.0))
        self.assertEqual(len(SOURCE_COMMIT),40)
        self.assertEqual(len(SHA),5)
        self.assertTrue(all(len(v)==40 for v in SHA.values()))
        self.assertEqual((EXPECTED_CASES,EXPECTED_SOLVERS),(630,18))
        self.assertIn("KNN5",POLICIES)
        self.assertIn("OMEGA_cost_lookahead2",POLICIES)

    def test_declares_exact_external_par10_semantics(self):
        s="""scenario_id: MAXSAT-WPMS-2016
performance_measures:
    - PAR10
maximize:
    - false
performance_type: runtime
algorithm_cutoff_time: 1800
number_of_feature_steps: 1
feature_steps:
    base:
"""
        validate_description(s)
        with self.assertRaises(ValueError):
            validate_description(s.replace("algorithm_cutoff_time: 1800",
                                           "algorithm_cutoff_time: 1600"))
        with self.assertRaises(ValueError):
            validate_description(s.replace("MAXSAT-WPMS-2016",
                                           "MAXSAT-PMS-2016"))


if __name__=="__main__":
    unittest.main()
