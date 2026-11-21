"""Synthetic harness tests; no held-out source is read by the development suite."""
import json
from pathlib import Path
import unittest
from copy import deepcopy
import run_blind as e


class BlindProtocolTests(unittest.TestCase):
    def test_frozen_holdout_ids_and_balanced_tasks(self):
        manifest=e.get_manifest()
        self.assertEqual(len(manifest["holdout_ids"]),12)
        self.assertEqual(len(manifest["tasks"]),18)
        self.assertFalse(set(manifest["holdout_ids"])&e.ORIGINAL_OLD)

    def make_fakes(self):
        data=e.get_manifest()
        sources={
            i:{"id":i,
               "informal_exact":("Prove that this polynomial is irreducible"
                                if i%2==0 else "The group is simple"),
               "lean_reference_exact":("theorem abc : Irreducible P := by\n sorry"
                                       if i%2==0 else
                                       "theorem abc : IsSimpleGroup G := by\n sorry"),
               "raw_git_blob":(f"{i:040x}")}
            for i in e.EXPECTED_IDS
        }
        return data,sources

    def test_gold_is_never_forwarded_to_signature(self):
        manifest,sources=self.make_fakes()
        inputs=e.freeze_inputs(manifest,sources)
        self.assertEqual(len(inputs),18)
        for x in inputs:
            self.assertNotIn("gold",x)
            self.assertNotIn("correct",x)
            self.assertNotIn("id",x)
            self.assertIn("natural",x)
        manifest["tasks"][0]["gold"]="HIDDEN"
        self.assertEqual(inputs,e.freeze_inputs(manifest,sources))

    def test_ir_does_not_pretend_to_certify_even_if_right(self):
        m,s=self.make_fakes()
        inputs=e.freeze_inputs(m,s)
        result=e.run_structural(inputs)
        self.assertEqual(len(result),18)
        self.assertTrue(all(x["source_semantics_proved"] is False for x in result))
        self.assertTrue(all(x["prediction"] in ("A","B","NONE") for x in result))

    def test_metrics_from_frozen_labels_are_separate(self):
        m,s=self.make_fakes()
        inp=e.freeze_inputs(m,s)
        r=e.run_structural(inp)
        fake=[{"task_id":q["task"],"source_blob":x["source_blob"],
               "input_sha256":x["input_sha256"],
               "raw_reply":q["gold"],"prediction":q["gold"]}
              for q,x in zip(m["tasks"],r)]
        report=e.analyse(m,inp,r,fake)
        self.assertEqual(report["compare"]["raw_qwen_0p5b_cache_off"]["correct"],18)
        self.assertFalse(report["semantic_equivalence_proven"])
        self.assertEqual(report["ir_thresholds_frozen"]["min_score"],2.5)
        self.assertEqual(report["ir_thresholds_frozen"]["min_margin"],1.0)

    def test_changed_scientific_source_blocks_scoring(self):
        m,s=self.make_fakes()
        inp=e.freeze_inputs(m,s)
        r=e.run_structural(inp)
        fake=[{"task_id":q["task"],"source_blob":x["source_blob"],
               "input_sha256":x["input_sha256"],
               "raw_reply":"NONE","prediction":"NONE"}
              for q,x in zip(m["tasks"],r)]
        fake[0]["input_sha256"]="corrupted"
        with self.assertRaisesRegex(ValueError,"SEMANTIC_SOURCE_CHANGED"):
            e.analyse(m,inp,r,fake)

    def test_gold_is_identity_not_semantic_equivalence(self):
        m,s=self.make_fakes()
        inp=e.freeze_inputs(m,s)
        r=e.run_structural(inp)
        fake=[{"task_id":q["task"],"source_blob":x["source_blob"],
               "input_sha256":x["input_sha256"],
               "raw_reply":"NONE","prediction":"NONE"}
              for q,x in zip(m["tasks"],r)]
        stats=e.analyse(m,inp,r,fake)["compare"]["raw_qwen_0p5b_cache_off"]
        self.assertEqual(stats["none_correct"],6)
        self.assertEqual(stats["positive_correct"],0)
        self.assertEqual(stats["abstained_none_on_positives"],12)


if __name__=="__main__":unittest.main()
