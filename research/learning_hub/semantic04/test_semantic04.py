"""One-shot SEMANTIC04 contract and negative controls, no model inference."""
import inspect
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sft01"))
import core
import data_guard
import model_run


class SemanticTransferTests(unittest.TestCase):

    def test_immutable_new_data_and_novel_families(self):
        rows = core.frozen_cases()
        self.assertEqual(len(rows), 12)
        self.assertEqual(len(set(x["family"] for x in rows)), 6)
        self.assertEqual(len({x["id"] for x in rows}), 12)
        self.assertEqual({x["kind"] for x in rows}, {"SEMANTIC_VALID_PYTHON"})
        training = data_guard.load_train()
        old_eval = data_guard.load_holdout()
        prior = {r["family"] for r in training + old_eval}
        self.assertFalse(prior & {r["family"] for r in rows})
        self.assertTrue(all(len(x["hidden_cases"]) == 5 and
                            len(x["public_examples"]) == 2 for x in rows))

    def test_reference_code_compiles_and_exactly_passes_hidden_and_public(self):
        for row in core.frozen_cases():
            with self.subTest(id=row["id"]):
                ref, status = core.allowed(row["reference_code_eval_only"])
                self.assertEqual(status, "SAFE_PYTHON")
                self.assertTrue(core.matches_public(ref, row["public_examples"]))
                self.assertTrue(core.grade(ref, row["hidden_cases"])["all_correct"])

    def test_every_bug_compiles_but_fails_at_least_one_visible_case(self):
        for row in core.frozen_cases():
            with self.subTest(id=row["id"]):
                broken, status = core.allowed(row["broken_source"])
                self.assertEqual(status, "SAFE_PYTHON")
                self.assertFalse(core.matches_public(broken, row["public_examples"]))
                self.assertNotEqual(broken, row["reference_code_eval_only"])

    def test_public_view_omits_hidden_and_reference(self):
        view = core.public_only(core.frozen_cases())
        self.assertEqual(len(view), 12)
        self.assertTrue(all(set(item) == {"id","family","defect","prompt",
                                         "broken","public"} for item in view))
        self.assertTrue(all("hidden_cases" not in json.dumps(item)
                            for item in view))
        self.assertTrue(all("reference_code_eval_only" not in json.dumps(item)
                            for item in view))
        self.assertTrue(all(item["broken"] in item["prompt"] for item in view))

    def test_strict_vs_permissive_fenced_code(self):
        good = core.frozen_cases()[0]["reference_code_eval_only"]
        wrapped = "Here is my result:\n" + chr(96) * 3 + "python\n" + good + chr(96) * 3 + "\nExplanation."
        self.assertIsNone(core.strict(wrapped)[0])
        self.assertEqual(core.permissive(wrapped)[0], good.strip())
        self.assertEqual(core.strict(good)[0], good.strip())

    def test_permissive_extracts_single_function_after_explanation(self):
        good = core.frozen_cases()[0]["reference_code_eval_only"]
        response = "I fixed the condition.\n" + good + "\nThis is the output."
        self.assertEqual(core.permissive(response)[0], good.strip())

    def test_permissive_rejects_multiple_fences_or_dynamic_execution(self):
        good = core.frozen_cases()[0]["reference_code_eval_only"]
        fence = chr(96) * 3
        double = fence + "python\n" + good + fence + "\n" + fence + "python\n" + good + fence
        self.assertEqual(core.permissive(double)[1], "AMBIGUOUS_FENCES")
        bad = "def transform(s):\n    return [open('secret')]\n"
        self.assertIsNone(core.strict(bad)[0])
        self.assertIsNone(core.permissive("Answer:\n" + bad)[0])

    def test_symbolic_repair_selects_from_public_only(self):
        examples = core.frozen_cases()
        for row in examples:
            with self.subTest(id=row["id"]):
                candidate = core.symbolic(row["broken_source"], row["public_examples"])
                self.assertEqual(candidate["hidden_tests_for_selection"], 0)
                self.assertLessEqual(candidate["attempts"], core.MAX_EDITS)
                if candidate["code"] is not None:
                    self.assertTrue(core.matches_public(candidate["code"],
                                                        row["public_examples"]))

    def test_symbolic_catalog_is_bounded_and_no_oracle_argument(self):
        params = list(inspect.signature(core.symbolic).parameters)
        self.assertEqual(params, ["broken", "public"])
        self.assertLessEqual(len(core.EDITS), core.MAX_EDITS)

    def test_grade_all_keeps_same_hidden_cases_for_three_arms(self):
        rows = core.frozen_cases()
        candidate = {}
        for row in rows:
            gold = row["reference_code_eval_only"]
            candidate[row["id"]] = {
                "base": {"raw": gold, "prompt_tokens": 1,
                         "generated_tokens": 2, "seconds": 0.01},
                "lora": {"raw": "no code", "prompt_tokens": 1,
                         "generated_tokens": 2, "seconds": 0.01},
                "symbolic": {"code": None, "edit": None, "attempts": 0,
                             "hidden_tests_for_selection": 0}}
        score = core.score(rows, candidate)
        self.assertEqual(score["summary"]["base"]["strict"]["exact_programs"], 12)
        self.assertEqual(score["summary"]["lora"]["permissive"]["exact_programs"], 0)
        self.assertEqual(score["summary"]["symbolic"]["strict"]["exact_programs"], 0)
        self.assertTrue(score["fresh_semantic_holdout_now_consumed"])

    def test_evaluation_does_not_train_and_checks_old_adapter(self):
        source = (HERE / "model_run.py").read_text()
        self.assertNotIn("torch.optim", source)
        self.assertNotIn("loss.backward(", source)
        self.assertNotIn("get_peft_model(", source)
        self.assertIn("PeftModel.from_pretrained", source)
        with self.assertRaises(Exception):
            model_run.check_adapter(HERE / "no_such_adapter")


if __name__ == "__main__":
    unittest.main()
