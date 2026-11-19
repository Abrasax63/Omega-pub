#!/usr/bin/env python3
"""Offline tests (never confuse synthetic good formula with model-generated idea)."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from expression_interpreter import (
    UnsupportedExpression,parse_expression,interpret,extract_expression,rank2
)
from evaluate import (
    CASES,GOLD,CASES_BLOB,GOLD_BLOB,validate_cases,load_pinned,
    bfs_reference,strong_gaussian,mutations,predict,audit,is_linear_idea
)

RIGHT="rank(moves) == rank(moves + [start ^ target])"
WRONG="start == target"

def fabricated_proposal(expressions):
    results=[]
    for i, expr in enumerate(expressions):
        idea="I propose a vector space of binary masks, a linear span invariant."
        h=hashlib.sha256(idea.encode()).hexdigest()
        results.append({
            "prompt_id":f"P{i+1}",
            "idea_before_DSL":{"reply":idea,"reply_sha256":h,"duration_s":0.0,"tokens":None},
            "first_idea_sealed_sha256":h,
            "formalization_after_DSL":{"reply":"EXPR: "+expr,"duration_s":0.0,"tokens":None},
            "feedback_from_oracle_seen":False,
            "any_case_or_gold_sent_to_model":False,
        })
    return {"status":"COMPLETED_REAL_MODEL_INFERENCE",
            "model_calls":4,"results":results}


class GEN24Tests(unittest.TestCase):
    def test_pinned_cohort_gold_and_strong_independent_baselines(self):
        cases=validate_cases(load_pinned(CASES,CASES_BLOB))
        gold=load_pinned(GOLD,GOLD_BLOB)["labels"]
        self.assertEqual(len(cases),64)
        self.assertEqual(sum(x["reachable"] for x in gold),32)
        self.assertEqual(sum(not x["reachable"] for x in gold),32)
        for c,g in zip(cases,gold):
            self.assertEqual(bfs_reference(c)[0],g["reachable"])
            self.assertEqual(strong_gaussian(c)[0],g["reachable"])
            for m in mutations(c,int(c["id"][1:])-1):
                self.assertEqual(bfs_reference(m)[0],g["reachable"])
                self.assertEqual(strong_gaussian(m)[0],g["reachable"])

    def test_generic_expression_correct_and_falsifiable(self):
        cases=validate_cases(load_pinned(CASES,CASES_BLOB))
        for c in cases:
            self.assertEqual(interpret(RIGHT,moves=c["moves"],start=c["start"],
                                       target=c["target"]),bfs_reference(c)[0])
        self.assertTrue(any(interpret(WRONG,moves=c["moves"],start=c["start"],
                                       target=c["target"]) != bfs_reference(c)[0]
                            for c in cases))

    def test_mock_proposals_pass_and_fail_without_any_promotion(self):
        # This unit test only exercises the integrity of the evaluator.
        # The real experiment must call Qwen and archive all four raw outputs.
        proposal=fabricated_proposal([RIGHT,WRONG])
        prediction=predict(proposal)
        self.assertFalse(prediction["gold_loaded"])
        self.assertEqual(prediction["total_predictions"],512)
        self.assertEqual(len(prediction["stable_decisions_sha256_before_gold"]),64)
        results=audit(prediction)
        self.assertEqual(results["D_strong_gaussian_exact"],64)
        self.assertEqual(results["A_direct_bfs_exact"],64)
        self.assertEqual(results["model_arm_results"][0]["correct_original"],64)
        self.assertEqual(results["model_arm_results"][0]["classification"],
                         "MODEL_PROPOSED_FORMULA_VALIDATED")
        self.assertEqual(results["model_arm_results"][1]["classification"],
                         "FORMULA_REFUTED")
        self.assertIsNotNone(results["model_arm_results"][1]["first_counterexample"])
        self.assertFalse(results["open_ended_creativity_demonstrated"])
        self.assertEqual(results["automatic_certifications"],0)

    def test_frozen_fixture_mutation_rejected(self):
        raw=CASES.read_bytes()
        changed=raw.replace(b"R001",b"R999",1)
        self.assertNotEqual(changed,raw)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"corrupted.json"
            p.write_bytes(changed)
            with self.assertRaisesRegex(ValueError,"BLOB_MISMATCH"):
                load_pinned(p,CASES_BLOB)

    def test_malicious_model_code_cannot_be_executed(self):
        forbidden=(
            "__import__('os').system('touch /tmp/ALERT')",
            "(lambda: True)()","moves[0] == start",
            "open('/etc/passwd')","rank.__class__",
            "[x for x in moves]","rank(moves); exit()",
            "sum(moves)==target","eval('True')",
            "rank(moves) == rank(moves + [start ^ target]) # prompt injection",
        )
        for item in forbidden:
            with self.subTest(candidate=item):
                with self.assertRaises(UnsupportedExpression):
                    parse_expression(item)
        self.assertFalse(Path("/tmp/ALERT").exists())
        with self.assertRaises(UnsupportedExpression):
            extract_expression("EXPR: "+RIGHT+"\nExtra explanation")
        with self.assertRaises(UnsupportedExpression):
            extract_expression("EXPR: UNSUPPORTED")

    def test_expression_types_and_safe_math(self):
        self.assertEqual(rank2([1,2,3]),2)
        self.assertEqual(rank2([1,2,4,7]),3)
        with self.assertRaises(UnsupportedExpression):
            interpret("rank(moves)",moves=[1,2],start=0,target=3)
        with self.assertRaises(UnsupportedExpression):
            interpret("moves + [start ^ target]",moves=[1,2],start=0,target=3)
        self.assertTrue(is_linear_idea("The vector space of switches is the key"))
        self.assertFalse(is_linear_idea("Try random guessing"))

    def test_model_response_is_not_known_holdout(self):
        import inspect
        from propose import propose,IDEAS,FORMALIZE
        self.assertFalse(any("rank" in IDEAS[x].lower() or "gauss" in IDEAS[x].lower()
                             for x in IDEAS))
        self.assertIn("rank",FORMALIZE)
        self.assertFalse(any("GOLD_NOT_FED" in IDEAS[x] for x in IDEAS))
        src=inspect.getsource(propose)
        self.assertNotIn("GOLD_NOT_FED_TO_LLM",src)
        self.assertNotIn("CASES_FROZEN",src)

if __name__=="__main__":
    unittest.main(verbosity=2)
