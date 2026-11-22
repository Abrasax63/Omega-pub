"""Frozen SFT data contract checks; no model or paid API required."""
import ast
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parents[1]/"learning_lab"))
from data_guard import load_train,load_holdout,EPOCHS,MAX_LENGTH
import prog_reconstruction_pilot as safe
import evaluate


class TrainingContractTests(unittest.TestCase):
    def test_train_frozen_and_full_provenance(self):
        rows=load_train()
        self.assertEqual(len(rows),62)
        self.assertEqual(len({x["family"] for x in rows}),22)
        self.assertEqual(sum(x["provenance"]=="OMEGA_V3_ORIGINAL_VERIFIED" for x in rows),2)
        self.assertEqual(EPOCHS,2)
        self.assertEqual(MAX_LENGTH,384)

    def test_holdout_new_semantic_families(self):
        rows=load_train()
        hidden=load_holdout()
        self.assertEqual(len(hidden),12)
        self.assertEqual(len({x["family"] for x in hidden}),6)
        self.assertFalse({x["family"] for x in rows}&{x["family"] for x in hidden})
        self.assertFalse({x["id"] for x in rows}&{x["id"] for x in hidden})

    def test_every_training_label_is_executable_and_exact_on_reference_cases(self):
        for item in load_train():
            with self.subTest(item=item["id"]):
                target=item["target"]
                self.assertTrue(safe.validate_program(target))
                cases=item["verification_cases"]
                got=safe.execute_student(target,[x["input"] for x in cases])
                self.assertEqual([r.get("value") for r in got],
                                 [x["expected"] for x in cases])

    def test_holdout_reference_truth_recomputes_exactly(self):
        for item in load_holdout():
            with self.subTest(item=item["id"]):
                program=item["reference_code_eval_only"]
                self.assertTrue(safe.validate_program(program))
                got=safe.execute_student(program,[x["input"] for x in item["hidden_cases"]])
                self.assertEqual([x.get("value") for x in got],
                                 [x["expected"] for x in item["hidden_cases"]])

    def test_broken_code_is_genuinely_invalid_not_untouched_gold(self):
        for row in list(load_train())+list(load_holdout()):
            with self.subTest(row=row["id"]):
                broken=row["prompt"].split("Broken source:\n",1)[1].split(
                    "\nObserved examples:",1)[0]
                with self.assertRaises(SyntaxError):
                    ast.parse(broken)

    def test_old_validated_model_codes_reused_exactly(self):
        index=__import__("json").loads(
            (HERE.parent/"VERIFIED_SKILL_INDEX_2026-11-22.json").read_text())
        prior={r["family_id"]:r["best_code"] for r in index["verified_candidates"]}
        rows={r["id"]:r for r in load_train()}
        self.assertEqual(rows["V3-PY-INDENTATION"]["target"],prior["py-syntax-indentation"])
        self.assertEqual(rows["V3-PY-QUOTES"]["target"],prior["py-syntax-quotes"])

    def test_training_script_never_imports_test_gold(self):
        source=(HERE/"train_lora.py").read_text()
        self.assertNotIn("load_holdout",source)
        self.assertNotIn("HOLDOUT_EVAL_ONLY.json",source)
        self.assertNotIn("evaluation_cases",source)

    def test_model_output_rejects_malformed_and_unsafe(self):
        self.assertEqual(evaluate.parse_generated("random answer")[1],"NO_COMPLETE_FUNCTION")
        self.assertEqual(evaluate.parse_generated(
            "def transform(s):\n    return open('secret')")[0],None)
        self.assertEqual(evaluate.parse_generated(
            "def transform(s):\n    return [s.upper()]")[1],"SAFE_PYTHON")

    def test_score_reference_program_as_positive_control(self):
        item=load_holdout()[0]
        gold=item["reference_code_eval_only"]
        row=evaluate.evaluate_generated(item,gold)
        self.assertTrue(row["complete_correct"])
        self.assertEqual(row["correct_hidden"],5)

    def test_score_invalid_python_as_negative_control(self):
        item=load_holdout()[0]
        row=evaluate.evaluate_generated(item,"def transform(s):\n    return }\n")
        self.assertFalse(row["complete_correct"])
        self.assertFalse(row["python_safe"])
        self.assertEqual(row["correct_hidden"],0)


if __name__=="__main__":
    unittest.main()
