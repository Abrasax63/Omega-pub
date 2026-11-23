"""Contract tests: conditional model calling without accessing hidden tests."""
import ast
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import adaptive_policy
import contract

class FakeModel:
    def __init__(self,replies):
        self.replies=list(replies)
        self.calls=[]
    def ask(self,messages,tag):
        self.calls.append((messages,tag))
        if not self.replies:
            raise AssertionError("UNEXPECTED_EXTRA_MODEL_REQUEST")
        return self.replies.pop(0)

class AdaptivePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=contract.public_view()[0]
        cls.reference=contract.evaluator_view()[0]["reference_source_evaluator_only"]

    def test_first_draft_correct_skips_second_call(self):
        c=FakeModel([self.reference])
        r=adaptive_policy.repair_one(c,self.public)
        self.assertEqual(r["model_calls_used"],1)
        self.assertTrue(r["revision_skipped"])
        self.assertEqual(r["code"],self.reference.strip())
        self.assertEqual(len(c.calls),1)
        self.assertEqual(r["hidden_cases_used"],0)

    def test_first_draft_wrong_second_right_with_execution_feedback(self):
        c=FakeModel([self.public["broken"],self.reference])
        r=adaptive_policy.repair_one(c,self.public)
        self.assertEqual(r["model_calls_used"],2)
        self.assertFalse(r["revision_skipped"])
        self.assertEqual(r["code"],self.reference.strip())
        self.assertEqual(r["public_feedback_first"]["correct"],0)
        self.assertEqual(r["public_feedback_final"]["correct"],2)
        self.assertIn("ACTUAL RESULTS",c.calls[1][0][1]["content"])

    def test_wrong_second_draft_must_abstain(self):
        c=FakeModel([self.public["broken"],self.public["broken"]])
        r=adaptive_policy.repair_one(c,self.public)
        self.assertEqual(r["model_calls_used"],2)
        self.assertEqual(r["status"],"PUBLIC_REPAIR_FAILED_ABSTAIN")
        self.assertIsNone(r["code"])
        self.assertEqual(r["hidden_cases_used"],0)

    def test_invalid_initial_model_code_uses_one_feedback_call(self):
        c=FakeModel(["not Python",self.reference])
        r=adaptive_policy.repair_one(c,self.public)
        self.assertEqual(r["model_calls_used"],2)
        self.assertIsNotNone(r["code"])
        self.assertEqual(r["public_feedback_first"]["status"],
                         "UNSAFE_OR_INVALID_CODE")

    def test_public_data_only_in_candidate_and_prompts(self):
        c=FakeModel([self.reference])
        adaptive_policy.repair_one(c,self.public)
        text=str(c.calls)
        self.assertNotIn("reference_source_evaluator_only",text)
        self.assertNotIn("hidden_tests",text)
        self.assertNotIn("evaluator_view",text)

    def test_policy_exposes_no_holding_oracle_and_model_not_created(self):
        src=(HERE/"adaptive_policy.py").read_text()
        tree=ast.parse(src)
        names={node.attr for node in ast.walk(tree)
               if isinstance(node,ast.Attribute)}
        self.assertNotIn("evaluator_view",names)
        self.assertNotIn("load_holdout",names)
        self.assertNotIn("MODEL_URL",src)
        self.assertNotIn("Client(",src)

    def test_nonpublic_task_rejected(self):
        c=FakeModel([])
        with self.assertRaisesRegex(ValueError,"EXPECTED_SANITIZED_PUBLIC_TASK"):
            adaptive_policy.repair_one(c,{"id":"x"})
        self.assertEqual(len(c.calls),0)

if __name__=="__main__":
    unittest.main()
