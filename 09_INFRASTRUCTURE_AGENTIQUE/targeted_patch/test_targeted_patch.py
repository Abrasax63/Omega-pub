"""Preflight for source-bound one-line patch. All model calls mocked."""
import hashlib
import types
import unittest
from unittest.mock import patch
from targeted_patch import (
    ROOT,ORIGINAL,FROZEN_ORIGINAL_SHA,OLD_LINE,ARMS,TEST_ONLY_CORRECT_CONDITION,
    notes_from_rce,prompt,parse_model_patch,apply_patch,model_patch,public_evaluate,
)
from reference import walks_exact

class TargetedPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes=notes_from_rce(ROOT)

    def test_historical_bug_has_exact_artifact_sha(self):
        self.assertEqual(hashlib.sha256(ORIGINAL.encode()).hexdigest(),FROZEN_ORIGINAL_SHA)
        self.assertEqual(ORIGINAL.count(OLD_LINE),1)

    def test_real_rce_source_and_sha(self):
        n=self.notes
        r=n["scientific_source"]
        self.assertTrue(r["path"].endswith("ALGORITHMIC_PILOT.md"))
        self.assertEqual(hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest(),r["source_blob_sha256"])
        self.assertTrue(n["public_tests_sha256"])

    def test_prompts_equal_chars_distinct_notes_and_no_hidden(self):
        a=prompt(ARMS[0],self.notes)
        b=prompt(ARMS[1],self.notes)
        self.assertEqual(len(a),len(b))
        self.assertNotEqual(a,b)
        self.assertIn(self.notes["memory"],b)
        self.assertNotIn(self.notes["memory"],a)
        self.assertNotIn("heldout_manifest",a+b)

    def test_parser_uses_model_continuation_not_echoed_bug(self):
        p=prompt(ARMS[1],self.notes)
        self.assertEqual(parse_model_patch(p+TEST_ONLY_CORRECT_CONDITION+"\n",p),TEST_ONLY_CORRECT_CONDITION)
        with self.assertRaises(ValueError):
            parse_model_patch(p,p)

    def test_correct_known_patch_only_changes_line_eleven(self):
        corrected=apply_patch(TEST_ONLY_CORRECT_CONDITION)
        a=ORIGINAL.splitlines()
        b=corrected.splitlines()
        self.assertEqual([i for i,(x,y) in enumerate(zip(a,b),1) if x!=y],[11])
        # A controlled unit-test source, never a model-produced source.
        namespace={}
        exec(corrected,namespace)
        fn=namespace["q_power"]
        for rows,h in [([6,4,4],2),([2,1],0),([2,1],2),([2,4,1],9)]:
            self.assertEqual(fn(rows,h),walks_exact(rows,h))

    def test_unchanged_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"no change"):
            apply_patch("rows[j] & (1 << i)")

    def test_dangerous_patch_rejected(self):
        for expr in ("__import__('os')","open('x')","rows[j]; import os","result[i] = 1"):
            with self.subTest(expr=expr):
                with self.assertRaises((ValueError,SyntaxError)):
                    apply_patch(expr)

    def test_no_multiline_patch(self):
        with self.assertRaises(ValueError):
            parse_model_patch("result[i]\nrows[j]")

    def test_real_model_output_wrapper_test_mocked(self):
        p=prompt(ARMS[1],self.notes)
        fake=types.SimpleNamespace(returncode=0,stdout=p+TEST_ONLY_CORRECT_CONDITION+"\n",stderr="")
        with patch("targeted_patch.subprocess.run",return_value=fake):
            row=model_patch("fake-cli","fake-model",ARMS[1],p)
        self.assertEqual(row["status"],"PATCH_VALID")
        self.assertEqual(row["changed_lines"],[11])
        self.assertNotEqual(row["source_sha256"],FROZEN_ORIGINAL_SHA)

    def test_error_from_model_not_called_success(self):
        p=prompt(ARMS[0],self.notes)
        fake=types.SimpleNamespace(returncode=2,stdout="",stderr="error")
        with patch("targeted_patch.subprocess.run",return_value=fake):
            row=model_patch("fake-cli","fake-model",ARMS[0],p)
        self.assertEqual(row["status"],"MODEL_CALL_FAILED")
        self.assertNotIn("source",row)

    def test_rejected_patch_never_opens_development(self):
        row={"status":"PATCH_REJECTED"}
        with patch("targeted_patch.public_check") as checks,patch("targeted_patch.score") as scores:
            public_evaluate(row,[],{})
        checks.assert_not_called()
        scores.assert_not_called()
        self.assertFalse(row["development_correct"])


    def test_actual_llama_cli_fenced_reply_extracted_without_console(self):
        transcript=(
            "llama.cpp banner\nmodel: /model.gguf\n"
            "> <|im_start|>system\nsource... (truncated)\n"
            + chr(96)*3 + "python\n"
            + "rows[j] & (1 << i) and rows[j] & (1 << i) == rows[j]\n"
            + chr(96)*3 + "\n\n[ Prompt: 52 t/s | Generation: 17 t/s ]\n"
            + "Exiting...\n"
        )
        expression=parse_model_patch(transcript, "not fully present")
        self.assertEqual(expression,"rows[j] & (1 << i) and rows[j] & (1 << i) == rows[j]")
        # Syntax acceptance != correct mathematical repair.
        changed=apply_patch(expression)
        self.assertIn("and",changed.splitlines()[10])

    def test_actual_memory_reply_fenced_but_unsafe_expression_rejected(self):
        transcript=(
            "banner\n> source... (truncated)\n"+chr(96)*3+"python\n"
            "if rows[j] & (1 << i) and rows[j] not in result[i]:\n"
            +chr(96)*3+"\n[ Prompt: generated ]\n"
        )
        with self.assertRaisesRegex(ValueError,"unapproved AST node"):
            parse_model_patch(transcript)

    def test_ambiguous_two_fences_rejected(self):
        block=chr(96)*3+"python\nresult[i] & (1 << j)\n"+chr(96)*3
        with self.assertRaisesRegex(ValueError,"multiple"):
            parse_model_patch(block+"\n"+block)

    def test_never_parse_just_echoed_cli_source_as_new_patch(self):
        raw="banner\n> def q_power(rows, steps):\n"+"  if rows[j] & (1 << i):\n"
        with self.assertRaisesRegex(ValueError,"boundary"):
            parse_model_patch(raw,"missing full prompt")

if __name__=="__main__":
    unittest.main()
