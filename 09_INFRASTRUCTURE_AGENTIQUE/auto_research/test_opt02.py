"""Tests of locked optimization protocol; no model calls in these tests."""
import copy
from hashlib import sha256
import itertools
import unittest

from gate import digest
from model_proposal import validate_source
from opt02_generator import CALLS, TOKENS_PER_CALL, TRAINING_SEEDS, make_training, prompt_for
from opt02_evaluator import (ARMS, BATCH, CLASSICAL, HORIZONS, MODES, REPEATS,
                             SOURCE_NAMES, build_holdout, canonical_hash, rows_from_graph,
                             score)
from reference import walks_exact
from variant_factory import generate


class Opt02ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.graph_info = build_holdout()
        cls.development = make_training()

    def test_external_nx35_cohort_and_sizes(self):
        self.assertEqual(len(self.cases), 48)
        self.assertEqual(sum(c["timed"] for c in self.cases), 32)
        self.assertEqual(len({c["group_id"] for c in self.cases}), 8)
        self.assertEqual(set(x["dataset"] for x in self.cases), set(SOURCE_NAMES))
        self.assertEqual(set(x["mode"] for x in self.cases), set(MODES))
        self.assertEqual(set(x["steps"] for x in self.cases), set(HORIZONS))
        self.assertEqual({c["n"] for c in self.cases}, {15, 32, 34, 77})

    def test_corpus_deterministic_and_not_prior_64_case_syntax(self):
        other,_ = build_holdout()
        self.assertEqual(self.cases, other)
        self.assertFalse(any(c["case_id"].startswith("cycle-12") for c in self.cases))

    def test_training_families_distinct_from_external_corpus(self):
        self.assertEqual(len(self.development), 30)
        self.assertEqual(len(TRAINING_SEEDS), 6)
        self.assertFalse({c["id"] for c in self.development}.intersection(
            {c["case_id"] for c in self.cases}))

    def test_fixed_budget_prompt_no_holdout_labels(self):
        self.assertEqual(CALLS, 3)
        self.assertEqual(TOKENS_PER_CALL, 800)
        for n in range(CALLS):
            p=prompt_for(n, None)
            self.assertIn("def classical_reference(rows, steps)",p)
            self.assertIn("def q_power(rows, steps)",p)
            self.assertNotIn("karate_club_graph",p)
            self.assertNotIn("les_miserables_graph",p)

    def test_benchmark_repetition_contract(self):
        self.assertEqual(REPEATS, 9)
        self.assertEqual(BATCH, 20)
        self.assertEqual(set(CLASSICAL), {"square-scan", "square-lowbit"})

    def test_short_exact_witnesses_match_classical(self):
        variants=generate()
        for width in (3,5,8):
            for edges in ([], [(i,(i+1)%width) for i in range(width)]):
                rows=[0]*width
                for i,j in edges:
                    rows[i] |= 1 << j
                for h in (0,1,2,5,16,31):
                    truth=walks_exact(rows,h)
                    for arm in CLASSICAL:
                        namespace={}
                        exec(variants[arm]["source"],namespace)
                        self.assertEqual(namespace["q_power"](rows,h),truth)

    def test_external_graph_rows_valid_bitmasks(self):
        for case in self.cases:
            self.assertEqual(len(case["rows"]),case["n"])
            self.assertTrue(all(0 <= bit < (1<<case["n"]) for bit in case["rows"]))

    def test_slow_candidate_must_be_rejected(self):
        payload=self.fake_payload()
        report=score(self.cases,self.graph_info,payload,"test-source",
                     {"winner_source_sha256":"test-source","model_attempts":3,
                      "external_corpus_opened":False},"test-image")
        self.assertEqual(report["status"],"NO_DEMONSTRATED_ADVANTAGE")
        self.assertEqual(report["timed_cases"],32)
        self.assertFalse(report["correctness_errors"])
        self.assertEqual(report["positive_families"],0)

    def test_wrong_answer_must_not_pass(self):
        payload=self.fake_payload()
        payload["results"][0]["values"]["model_candidate"][0] ^= 1
        report=score(self.cases,self.graph_info,payload,"test-source",
                     {"winner_source_sha256":"test-source","model_attempts":3,
                      "external_corpus_opened":False},"test-image")
        self.assertEqual(report["status"],"NO_DEMONSTRATED_ADVANTAGE")
        self.assertTrue(report["correctness_errors"])

    def test_mutated_input_hash_rejected(self):
        payload=self.fake_payload()
        payload["input_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"input SHA"):
            score(self.cases,self.graph_info,payload,"test-source",
                 {"winner_source_sha256":"test-source","model_attempts":3,
                  "external_corpus_opened":False},"test-image")

    def test_unselected_candidate_rejected(self):
        payload=self.fake_payload()
        with self.assertRaisesRegex(ValueError,"champion"):
            score(self.cases,self.graph_info,payload,"test-source",
                 {"winner_source_sha256":"other","model_attempts":3,
                  "external_corpus_opened":False},"test-image")

    def fake_payload(self):
        results=[]
        for case in self.cases:
            gold=walks_exact(case["rows"],case["steps"])
            results.append({"case_id":case["case_id"],
                            "values":{arm:gold[:] for arm in ARMS},
                            "samples_ns":{arm:[200000 if arm=="model_candidate"
                                                else 100000]*REPEATS
                                          for arm in ARMS}})
        return {
            "source_sha256":"test-source",
            "input_sha256":canonical_hash([{k:v for k,v in row.items() if k!="timed"}
                                          for row in self.cases]),
            "classic_sha256":{name:generate()[name]["sha256"] for name in CLASSICAL},
            "results":results}


if __name__ == "__main__":
    unittest.main()
