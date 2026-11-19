#!/usr/bin/env python3
"""Non-regression tests for the representation lab and its scientific scope."""
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from representations import (
    SOURCE_PATH,SOURCE_BLOB, direct_oracle, pair_pullback,
    partition_refinement, unordered_histogram, current_only, future_only,
    propose_alternative_views, exhaustive_cases, reserved_cases,
    evaluate_phase, FAMILIES, make_counterexample,
)
from read import safe_read


class RepresentationLabTests(unittest.TestCase):
    def test_exact_source_anchor_and_valid_grammar(self):
        raw=safe_read(SOURCE_PATH,SOURCE_BLOB)
        self.assertIn("observabilité",raw.decode("utf-8").lower())
        cases=propose_alternative_views((1,0),(0,1))
        self.assertEqual(tuple(x["id"] for x in cases),FAMILIES)
        self.assertTrue(all(x["candidate_only"] and
                            not x["certified_without_check"] for x in cases))
        with self.assertRaises(ValueError):
            propose_alternative_views((0,2),(0,1))

    def test_direct_observation_from_start_is_not_future_only(self):
        t=(0,0)
        pi=(0,1)
        self.assertEqual(direct_oracle(t,pi,1),frozenset())
        self.assertEqual(future_only(t,pi,1),frozenset({(0,1)}))
        cx=make_counterexample(2,t,pi,1,direct_oracle(t,pi,1),future_only(t,pi,1))
        self.assertFalse(cx["oracle_equivalent"])
        self.assertTrue(cx["candidate_equivalent"])

    def test_histogram_can_lose_order(self):
        t=(1,0)
        pi=(0,1)
        self.assertEqual(direct_oracle(t,pi,2),frozenset())
        self.assertEqual(unordered_histogram(t,pi,2),frozenset({(0,1)}))

    def test_current_only_cannot_split_same_color_states(self):
        t=(1,2,2)
        pi=(0,0,1)
        self.assertIn((0,1),direct_oracle(t,pi,1))
        self.assertNotIn((0,1),direct_oracle(t,pi,2))
        self.assertIn((0,1),current_only(t,pi,2))

    def test_two_alternative_representations_agree_on_crafted_cases(self):
        crafted=[
            ((1,2,2),(0,0,1)),
            ((0,1,1,3),(0,1,0,1)),
            ((2,3,0,1),(0,0,1,1)),
            ((0,0),(0,0)),
        ]
        for t,pi in crafted:
            for h in range(1,len(t)+2):
                with self.subTest(t=t,pi=pi,h=h):
                    expected=direct_oracle(t,pi,h)
                    self.assertEqual(pair_pullback(t,pi,h),expected)
                    self.assertEqual(partition_refinement(t,pi,h),expected)

    def test_small_exact_enumeration_and_mutations(self):
        cases=[(t,pi) for t,pi in exhaustive_cases() if len(t)<=3]
        self.assertEqual(len(cases),232)
        result=evaluate_phase(cases,"SMALL_EXACT")
        self.assertEqual(result["invariant_failure_count"],0)
        for name in ("pair_pullback","partition_refinement"):
            self.assertEqual(result["mismatches"][name],0)
        for name in ("current_only","future_only","unordered_histogram"):
            self.assertGreater(result["mismatches"][name],0)
            self.assertIsNotNone(result["minimal_counterexamples"][name])

    def test_reserved_cases_are_not_in_exhaustive_calibration(self):
        cases=list(reserved_cases())
        self.assertEqual(len(cases),128)
        self.assertEqual([c[0] for c in cases[:64]],[5]*64)
        self.assertEqual([c[0] for c in cases[64:]],[6]*64)
        self.assertEqual(len({(c[0],c[1]) for c in cases}),128)
        self.assertTrue(all(len(c[2])==c[0] and len(c[3])==c[0] for c in cases))

if __name__=="__main__":
    unittest.main(verbosity=2)
