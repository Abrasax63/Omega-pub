"""Fast Lane: quality controls on generated semantic-training examples, no LLM."""
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import fastlane as f


class FastLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=f.produce()

    def test_reuses_prior_train_not_prior_holdouts(self):
        d=self.data
        self.assertEqual(d["schema"],f.SCHEMA)
        self.assertEqual(d["status"],"TRAINING_CANDIDATES_ONLY")
        self.assertTrue(d["train_only_no_independent_holdout"])
        self.assertEqual(d["model_generated_new_targets"],0)
        self.assertEqual(d["inference_calls"],0)
        self.assertEqual(d["training_updates"],0)
        self.assertGreaterEqual(d["families"],f.MIN_FAMILIES)
        self.assertGreaterEqual(d["examples"],f.MIN_EXAMPLES)

    def test_unique_identifiers_and_source_families(self):
        rows=self.data["training_samples"]
        self.assertEqual(len(rows),self.data["examples"])
        self.assertEqual(len({r["id"] for r in rows}),len(rows))
        self.assertFalse({r["family"] for r in rows}&set(f.CONSUMED_HOLDOUTS))
        self.assertTrue(all(r["teacher_code_provenance"]==
                            "CURATED_REFERENCE_NOT_MODEL_PROPOSAL" for r in rows))
        self.assertLessEqual(max(sum(r["family"]==fam for r in rows)
                         for fam in set(x["family"] for x in rows)),f.MAX_PER_FAMILY)

    def test_generated_labels_and_failures_replay(self):
        for row in self.data["training_samples"][:10]:
            with self.subTest(row=row["id"]):
                gold=row["target"]
                prompt=row["prompt"]
                self.assertTrue(f.sandbox.validate_program(gold))
                self.assertTrue(f.verified(gold,row["previous_train_public_examples"]))
                broken=prompt.split("BROKEN SOURCE:\n",1)[1].split(
                    "\nVISIBLE OBSERVATIONS:",1)[0]
                self.assertTrue(f.sandbox.validate_program(broken))
                self.assertFalse(f.verified(broken,row["previous_train_public_examples"]))
                self.assertNotEqual(broken.strip(),gold.strip())

    def test_novel_faults_are_semantic_and_safe(self):
        samples=self.data["training_samples"][:10]
        for row in samples:
            src=row["prompt"].split("BROKEN SOURCE:\n",1)[1].split(
                "\nVISIBLE OBSERVATIONS:",1)[0]
            self.assertTrue(f.sandbox.validate_program(src))
            self.assertEqual(row["source_kind"],
              "SYNTHETIC_SEMANTIC_MUTATION_OF_PREVIOUS_SFT_TRAIN")
            self.assertFalse(row["new_generalization_demonstrated"])

    def test_deterministic_manifest(self):
        repeat=f.produce()
        self.assertEqual(repeat["dataset_sha256"],self.data["dataset_sha256"])
        self.assertEqual(repeat["examples"],self.data["examples"])
        self.assertEqual(repeat["training_samples"],self.data["training_samples"])

    def test_training_is_always_blocked_without_new_holdout(self):
        gate=f.promotion_gate(self.data)
        self.assertTrue(gate["blocked"])
        self.assertIn("NO_FRESH_INDEPENDENT_HOLDOUT",gate["block_reasons"])
        self.assertIn("NO_AUTO_TRAINING_PERMISSION",gate["block_reasons"])
        self.assertEqual(gate["status"],
                         "DATA_READY_FOR_HUMAN_REVIEW_NOT_FOR_AUTO_TRAINING")

    def test_does_not_use_old_hidden_answers_or_model_inference(self):
        src=(HERE/"fastlane.py").read_text()
        self.assertNotIn("load_holdout(",src)
        self.assertNotIn("HOLDOUT_EVAL_ONLY.json",src)
        self.assertNotIn("HOLDOUT_SEMANTIC_FROZEN.json",src)
        self.assertNotIn("torch.optim",src)
        self.assertNotIn("from peft",src)
        self.assertNotIn("from transformers",src)

    def test_failed_candidate_is_not_admitted_as_correct_program(self):
        a="def transform(s):\n    return []\n"
        cases=[{"input":"a","expected":["a"]}]
        self.assertFalse(f.verified(a,cases))

    def test_public_extraction_is_frozen_sft01_only(self):
        train=f.load_train()
        prompt=train[0]["prompt"]
        items=f.public_from_prompt(prompt)
        self.assertEqual(len(items),2)
        self.assertTrue(all("input" in item and "expected" in item for item in items))

    def test_no_duplicate_fault_outputs_by_family(self):
        groups={}
        for row in self.data["training_samples"]:
            groups.setdefault(row["family"],set())
            self.assertNotIn(row["broken_sha256"],groups[row["family"]])
            groups[row["family"]].add(row["broken_sha256"])


if __name__=="__main__":
    unittest.main()
