"""One-shot real experiment harness: zero-network structural tests."""
import json
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest
from real_abstraction_trial import (
    TARGET_PAGES, SEED_TAG, HOLDOUT_TASKS, MODEL, finite_holdout,
    predict_axioms, eval_blind, extract_document_pages,
)
from concept_abstraction_lab import check_axioms


class TrialContractTests(unittest.TestCase):
    def test_model_declared_and_fixed_page_selection_budget(self):
        self.assertEqual(MODEL,"Qwen2.5-3B-Instruct-Q4_K_M")
        self.assertEqual(TARGET_PAGES,3)
        self.assertEqual(HOLDOUT_TASKS,4)
        self.assertIn("REAL-01",SEED_TAG)

    def test_holdout_generated_without_solutions_or_concept_hints(self):
        one=finite_holdout("a"*64)
        two=finite_holdout("a"*64)
        self.assertEqual(one,two)
        self.assertEqual(len(one),4)
        self.assertEqual(len({json.dumps(t,sort_keys=True) for t in one}),4)
        for task in one:
            self.assertEqual(task["universe"],["a","b","c"])
            self.assertNotIn("oracle_axioms",task)

    def test_holdout_changes_with_pdf_hash(self):
        self.assertNotEqual(finite_holdout("a"*64),finite_holdout("b"*64))

    def test_strict_format_and_abstention(self):
        self.assertEqual(predict_axioms('{"axioms":["reflexive","serial"]}'),
                         ["reflexive","serial"])
        for x in ('garbage','{"axioms":["magical"]}',
                  '{"axioms":["serial","serial"]}',
                  '{"abstain":true}', '{}', '{"axioms":"reflexive"}'):
            self.assertIsNone(predict_axioms(x))

    def test_no_abstraction_leaves_zero_test_calls(self):
        class NoModel:
            def __call__(self,*_):
                raise AssertionError("must not call model")
        out=eval_blind(NoModel(),{"status":"MODEL_ABSTAINED_OR_INVALID_JSON"},"x")
        self.assertEqual(out["model_calls"],0)
        self.assertNotIn("A",out)

    def test_gold_after_answers_experiment_in_always_private_oracle(self):
        # This harness test does NOT verify mathematical learning, only
        # the evaluation report is internally consistent.
        class Scripted:
            def __init__(self):
                self.calls=[]
            def __call__(self, messages,tokens):
                self.calls.append(messages)
                return {"text":'{"axioms":["reflexive"]}',
                        "usage":{"prompt_tokens":100,"completion_tokens":10},
                        "time_s":0.1}
        model=Scripted()
        report={"status":"STRUCTURAL_CHECKS_PASSED_SEMANTICS_UNVERIFIED",
                "analysis":{"common_axioms_on_inputs":["transitive"],
                            "model_proposed_axioms":["transitive"]}}
        out=eval_blind(model,report,"pdfhash")
        self.assertEqual(len(out["tasks"]),4)
        self.assertEqual(len(model.calls),8)
        self.assertEqual(out["A"]["n"],4)
        self.assertFalse(out["prompt_tokens_equal"])
        for t in out["tasks"]:
            node=t["universe"]
            es={tuple(e) for e in t["edges"]}
            actual=sorted([k for k,x in check_axioms(node,es).items() if x["holds"]])
            self.assertEqual(t["oracle_axioms"],actual)
            self.assertEqual(t["A_direct"]["parsed"],["reflexive"])


if __name__=="__main__":
    unittest.main()
