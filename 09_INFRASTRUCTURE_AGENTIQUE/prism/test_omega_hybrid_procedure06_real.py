"""Real Qwen evidence regression, not independent holdout tasks.

Frozen run #45279117106 / artifact #14869256476. Reuse of these cases
for future scientific confirmation is explicitly forbidden.
"""
import json
import unittest

from omega_hybrid_procedure06 import make_manifest, valid_answer


class RealProcedure06Regression(unittest.TestCase):
    def test_wrong_negative_certificate_rejected_even_with_correct_label(self):
        questions, oracle = make_manifest()
        # Actual Qwen P reply on first case (a genuinely negative relation).
        answer = {"holds":False,"failed_axioms":["transitive"],
                  "certificate":{"kind":"missing_transitive_edge",
                                 "triple":["v1","v2","v3"]}}
        edges=frozenset(map(tuple,questions["questions"][0]["edges"]))
        truth=oracle["answers"][0]
        self.assertFalse(truth["holds"])
        result=valid_answer(json.dumps(answer),truth,"P",edges)
        self.assertTrue(result["full_axioms_correct"])
        self.assertFalse(result["certificate_valid"])

    def test_actual_true_negative_witness_is_accepted_as_bounded_certificate(self):
        questions, oracle = make_manifest()
        # This one real Qwen witness was exact: the fifth case.
        answer = {"holds":False,"failed_axioms":["transitive"],
                  "certificate":{"kind":"missing_transitive_edge",
                                 "triple":["v1","v2","v3"]}}
        edges=frozenset(map(tuple,questions["questions"][4]["edges"]))
        truth=oracle["answers"][4]
        self.assertFalse(truth["holds"])
        result=valid_answer(json.dumps(answer),truth,"P",edges)
        self.assertTrue(result["certificate_valid"])
        self.assertTrue(result["full_axioms_correct"])

    def test_positive_case_false_negative_never_passes(self):
        questions, oracle = make_manifest()
        answer = {"holds":False,"failed_axioms":["transitive"],
                  "certificate":{"kind":"missing_transitive_edge",
                                 "triple":["v0","v1","v0"]}}
        edges=frozenset(map(tuple,questions["questions"][2]["edges"]))
        truth=oracle["answers"][2]
        self.assertTrue(truth["holds"])
        result=valid_answer(json.dumps(answer),truth,"P",edges)
        self.assertFalse(result["full_axioms_correct"])
        self.assertFalse(result["certificate_valid"])


if __name__=="__main__":
    unittest.main()
