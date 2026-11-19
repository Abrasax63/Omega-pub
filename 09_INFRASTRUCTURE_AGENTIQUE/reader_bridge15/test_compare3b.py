#!/usr/bin/env python3
"""Offline safeguards and replay for Reader15; localhost request mocked."""
import json
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from compare3b import GOLD, MAX_NEW_TOKENS, evaluate, messages_for, MODEL


class Local3BAblationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs=json.loads(GOLD.read_text(encoding="utf-8"))["documents"]

    def test_model_and_budget_frozen(self):
        self.assertEqual(MODEL,"Qwen2.5-Coder-3B-Instruct-Q4_K_M")
        self.assertEqual(MAX_NEW_TOKENS,64)
        self.assertEqual(len(self.refs),2)

    def test_mock_valid_lines_and_no_promotion(self):
        from selector import evaluate_document
        ref=self.refs[0]
        reference=evaluate_document(ref)
        chosen=reference["candidates"][0]["line"]
        calls=[]
        def fake(messages):
            calls.append(messages)
            return {"raw_reply":str(chosen),"seconds":0.0,"token_usage":{"completion_tokens":2}}
        actual=evaluate(ref,call=fake)
        self.assertEqual(actual["model_3b"]["status"],"REPLY_VALID")
        self.assertEqual(actual["model_3b"]["accepted_count"],1)
        self.assertFalse(actual["model_3b"]["semantic_fidelity_verified"])
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0],messages_for(reference["candidates"]))
        self.assertFalse(actual["model_3b"]["mathematical_validity_verified"])

    def test_mock_fake_line_rejected_without_repair(self):
        def fake(_):
            return {"raw_reply":"999","seconds":0.0,"token_usage":{}}
        result=evaluate(self.refs[0],call=fake)
        self.assertEqual(result["model_3b"]["status"],"REPLY_REJECTED")
        self.assertEqual(result["model_3b"]["selected"],[])
        self.assertNotIn("accepted_count",result["model_3b"])

    def test_mock_abstain_is_valid_but_not_scientific_success(self):
        def fake(_):
            return {"raw_reply":"NONE","seconds":0.0,"token_usage":{}}
        result=evaluate(self.refs[1],call=fake)
        self.assertEqual(result["model_3b"]["status"],"REPLY_VALID")
        self.assertEqual(result["model_3b"]["accepted_count"],0)
        self.assertEqual(result["model_3b"]["metrics"]["recall"],0.0)
        self.assertIsNone(result["model_3b"]["metrics"]["precision"])


if __name__=="__main__":
    unittest.main(verbosity=2)
