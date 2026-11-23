"""Offline preflight for first new-family ACTIVE-DEBUG01 model experiment."""
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"semantic04"))
import contract
import core
import inference
import grade


class ActiveDebug01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=contract.evaluator_view()

    def test_frozen_git_blob_and_exact_new_families(self):
        self.assertEqual(len(self.rows),6)
        self.assertEqual({x["family"] for x in self.rows},contract.FAMILIES)
        self.assertTrue(all(len(x["public_examples"])==2 and
                            len(x["hidden_tests"])==5 for x in self.rows))
        self.assertEqual(contract.FROZEN_BLOB,"73ba10b629206dd3d771cb03048031157645ab38")

    def test_reference_passes_all_oracle_cases_sandbox(self):
        for x in self.rows:
            with self.subTest(id=x["id"]):
                gold=x["reference_source_evaluator_only"]
                self.assertTrue(core.sandbox.validate_program(gold))
                got=core.sandbox.execute_student(
                    gold,[z["input"] for z in x["public_examples"]+x["hidden_tests"]])
                self.assertEqual([v.get("value") for v in got],
                                 [v["output"] for v in
                                  x["public_examples"]+x["hidden_tests"]])

    def test_broken_is_safe_valid_python_but_wrong_on_public(self):
        for x in self.rows:
            with self.subTest(id=x["id"]):
                bad=x["broken_source"]
                self.assertTrue(core.sandbox.validate_program(bad))
                self.assertNotEqual(bad,x["reference_source_evaluator_only"])
                f=inference.public_feedback("def transform(s):\n"+bad.split("def transform(s):\n",1)[-1],
                                              x["public_examples"])
                self.assertEqual(f["status"],"COMPILED_EXECUTED_RESTRICTED_SANDBOX")
                self.assertLess(f["correct"],2)

    def test_model_view_never_includes_holdout_or_teacher_code(self):
        views=contract.public_view()
        self.assertEqual(len(views),6)
        self.assertTrue(all(set(x)=={"id","family","broken","public","prompt"}
                            for x in views))
        for x in views:
            self.assertFalse("reference_source_evaluator_only" in json.dumps(x))
            self.assertFalse("hidden_tests" in json.dumps(x))
            self.assertTrue(x["broken"] in x["prompt"])

    def test_new_holdouts_not_in_old_family_list(self):
        old={
            "lower_each","upper_each","digits_only","uppercase_to_lower",
            "lowercase_to_upper","alpha_lower","alpha_upper","omit_pipe",
            "omit_spaces","only_letter_a","duplicate_chars","prefix_x",
            "suffix_bang","even_index","odd_index","punct_only",
            "unique_chars","nondigits","lower_alpha_unique","switch_case",
            "v3_python_reverse","v3_python_upper_list",
            "unique_digits","split_colon","third_index","ord_each",
            "vowels_up","reverse_upper_lower",
            "double_vowels","even_distinct_lower","pipe_alpha_upper",
            "reverse_nonzero_digits","overlap_bigrams","indexed_upper_alpha",
        }
        self.assertFalse(contract.FAMILIES & old)

    def test_model_url_and_sha_are_pinned(self):
        self.assertEqual(len(contract.MODEL_SHA256),64)
        self.assertEqual(contract.MAX_MODEL_CALLS,6*3)
        self.assertEqual(contract.MAX_TOKENS_PER_CALL,400)
        self.assertEqual(contract.SEED,20261123)

    def test_no_nonlocal_model_api(self):
        with self.assertRaisesRegex(ValueError,"LOCAL_LOOPBACK"):
            inference.Client("https://api.openai.com")
        with self.assertRaisesRegex(ValueError,"LOCAL_LOOPBACK"):
            inference.Client("http://localhost:9999")

    def test_direct_feedback_only_known_public_cases(self):
        x=contract.public_view()[0]
        raw=x["broken"]
        detail=inference.public_feedback(raw,x["public"])
        self.assertEqual(len(detail["examples"]),2)
        prompt=inference.feedback_review_prompt(x,raw,detail)
        self.assertIn("ACTUAL RESULTS",prompt)
        self.assertNotIn("hidden_tests",prompt)
        self.assertNotIn("reference_source_evaluator_only",prompt)
        prompt2=inference.direct_review_prompt(x,raw)
        self.assertNotIn("ACTUAL RESULTS",prompt2)

    def test_private_oracle_import_forbidden_in_model_runner(self):
        import ast
        src=(HERE/"inference.py").read_text()
        tree=ast.parse(src)
        calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)]
        used=[(c.func.attr if isinstance(c.func,ast.Attribute) else c.func.id)
              for c in calls if isinstance(c.func,(ast.Attribute,ast.Name))]
        for forbidden in ("evaluator_view","load_holdout","train_lora","exec","eval"):
            self.assertNotIn(forbidden,used)
        # Audit field names and comments may mention hidden data, but
        # the executable model path must only call the sanitized view.
        self.assertIn("public_view",used)
        self.assertNotIn("reference_source_evaluator_only",src)
        self.assertNotIn("torch.optim",src)

    def test_test_parser_accepts_safe_and_rejects_imports(self):
        good=self.rows[0]["reference_source_evaluator_only"]
        self.assertIsNotNone(inference.parse_code(good)[0])
        bad="def transform(s):\n    import os\n    return []\n"
        self.assertIsNone(inference.parse_code(bad)[0])

    def test_hidden_grading_positive_and_negative_controls(self):
        for x in self.rows:
            with self.subTest(id=x["id"]):
                p=grade.grade(x["reference_source_evaluator_only"],x["hidden_tests"])
                self.assertTrue(p["all_correct"])
                self.assertEqual(p["correct_cases"],5)
                blank=grade.grade(None,x["hidden_tests"])
                self.assertFalse(blank["all_correct"])
                self.assertEqual(blank["correct_cases"],0)

    def test_model_and_symbolic_selection_do_not_auto_train(self):
        s=(HERE/"inference.py").read_text()
        self.assertIn("resolve_guarded(",s)
        self.assertFalse("optimizer.step" in s)
        self.assertFalse("from_pretrained" in s)
        self.assertFalse("update_file" in s)

if __name__=="__main__":
    unittest.main()
