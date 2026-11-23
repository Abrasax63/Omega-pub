"""Permanent negative regression from Qwen3B one-shot run 45274034725.

These examples were ALREADY exposed, so they are diagnostic regression
fixtures only. They must never be presented as independent holdout data.
"""
import json
import unittest
from omega_hybrid_schema_retry import schema_retry


class ActualQwenReal01Regression(unittest.TestCase):
    def test_original_unmodified_reply_fails_transitivity(self):
        original = {"concept":"Equivalence Relations",
                    "formal_axioms":["reflexive","symmetric","transitive"]}
        output = json.dumps({
            "positive_edges":[["a","a"],["b","b"],["c","c"],
                              ["a","b"],["b","a"],["b","c"],["c","b"]],
            "negative_edges":[]})
        r=schema_retry(original,lambda *_:{"text":output})
        self.assertEqual(r["status"],"QUARANTINE")
        self.assertEqual(r["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertEqual(r["after"]["positive"]["witnesses"]["transitive"],["a","b","c"])
        self.assertEqual(r["after"]["negative"]["status"],"CORRECT")
        self.assertEqual(r["scientific_claims_certified"],0)
        self.assertEqual(r["calls"],1)


if __name__=="__main__":unittest.main()
