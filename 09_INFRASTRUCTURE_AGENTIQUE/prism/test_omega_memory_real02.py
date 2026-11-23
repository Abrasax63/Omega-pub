"""Offline contract checks for REAL-02; no Web and no LLM."""
import unittest
from omega_memory_real02 import (
    source_seed, concept_name, TARGETS, holdout, inspect_bounded,
    parse_answer, is_example,
)

class Real02Tests(unittest.TestCase):
    def test_no_synthetic_seed_can_pass_immutable_upstream_hash(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB"):
            source_seed(b"<section/>")
    def test_known_and_unknown_concepts(self):
        self.assertEqual(concept_name("Equivalence relations"),"equivalence relation")
        self.assertEqual(concept_name("partial order"),"partial order")
        self.assertIsNone(concept_name("Riemann hypothesis"))
    def test_exact_holdout_balance_and_reproduction(self):
        for name in ("equivalence relation","partial order","preorder",
                     "symmetric","transitive","reflexive"):
            sample=holdout(TARGETS[name])
            self.assertEqual(sample,holdout(TARGETS[name]))
            self.assertEqual(len(sample),4)
            self.assertEqual(sum(t["truth"] for t in sample),2)
            self.assertEqual(len(set(t["mask"] for t in sample)),4)
    def test_oracle_rejects_invalid_self_examples(self):
        sig=TARGETS["equivalence relation"]
        correct=[["a","a"],["b","b"],["c","c"]]
        incorrect=[["a","b"]]
        self.assertTrue(is_example(correct,sig,True))
        self.assertTrue(is_example(incorrect,sig,False))
        self.assertFalse(is_example(correct+correct,sig,True))
        self.assertFalse(is_example(incorrect,sig,True))
    def test_model_fidelity_fail_closed(self):
        sig=list(TARGETS["equivalence relation"])
        card={"concept":"equivalence relation","formal_axioms":sig,
              "positive_edges":[["a","a"],["b","b"],["c","c"]],
              "negative_edges":[["a","b"]]}
        self.assertTrue(inspect_bounded(card,True,"An equivalence relation exists.")["bounded_pass"])
        self.assertFalse(inspect_bounded(card,False,"An equivalence relation exists.")["bounded_pass"])
        card["formal_axioms"]=["reflexive","transitive"]
        self.assertFalse(inspect_bounded(card,True,"An equivalence relation exists.")["bounded_pass"])
    def test_invalid_formats_count_as_abstentions(self):
        sig=TARGETS["equivalence relation"]
        self.assertIsNone(parse_answer("not json",sig))
        self.assertIsNone(parse_answer('{"abstain":true}',sig))
        self.assertIsNone(parse_answer('{"holds":true,"failed_axioms":["symmetric"]}',sig))
        self.assertTrue(parse_answer('{"holds":true,"failed_axioms":[]}',sig))
        self.assertFalse(parse_answer('{"holds":false,"failed_axioms":["symmetric"]}',sig))

if __name__=="__main__":
    unittest.main()
