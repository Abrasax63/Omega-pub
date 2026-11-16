"""Fail-closed contract for prospectively frozen independent bug IDs."""
from pathlib import Path
import json
import re
import unittest

from abc_core import MAX_PER_ARM, MAX_POOL, ARMS
from abc_runner import MODEL_CALLS_PER_REPRODUCED_BUG, MODEL_NEW_TOKENS

ROOT = Path(__file__).resolve().parent
COHORT = ROOT / "COHORT_02_FREEZE.json"
PREREG = ROOT / "PREREG_2026-11-16_COHORT2.md"

class NewCohortContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(COHORT.read_text(encoding="utf8"))

    def test_preregistered_new_external_ids(self):
        self.assertTrue(PREREG.is_file())
        self.assertEqual(self.c["experiment"],"OMEGA-NEW5-ABC-02")
        rows=self.c["cases"]
        self.assertEqual(len(rows),5)
        self.assertEqual([x["id"] for x in rows],["N1","N2","N3","N4","N5"])
        self.assertEqual([x["bug_id"] for x in rows],["5","6","7","8","9"])
        self.assertEqual(len({x["buggy_sha"] for x in rows}),5)
        self.assertEqual(len({x["fixed_sha"] for x in rows}),5)
        for c in rows:
            self.assertEqual(c["repository"],"tqdm/tqdm")
            self.assertEqual(c["project"],"tqdm")
            self.assertTrue(re.fullmatch("[a-f0-9]{40}",c["buggy_sha"]))
            self.assertTrue(re.fullmatch("[a-f0-9]{40}",c["fixed_sha"]))
            self.assertTrue(c["test_id"].startswith(c["test_file"]+"::"))
            self.assertTrue(c["metadata_url"].endswith("/"+c["bug_id"]+"/bug.info"))
            self.assertTrue(c["run_test_url"].endswith("/"+c["bug_id"]+"/run_test.sh"))

    def test_matched_test_caps_not_cpu(self):
        self.assertEqual(MAX_PER_ARM,4)
        self.assertEqual(MAX_POOL,90)
        self.assertEqual(tuple(self.c["arms"]),ARMS)
        self.assertEqual(self.c["max_actual_patch_test_runs_per_arm_per_bug"],4)
        self.assertEqual(self.c["max_qwen_calls_per_bug"],MODEL_CALLS_PER_REPRODUCED_BUG)
        self.assertEqual(self.c["qwen_output_tokens_per_call"],MODEL_NEW_TOKENS)
        self.assertTrue(self.c["matched_logical_patch_test_cap"])
        self.assertFalse(self.c["matched_total_compute"])

    def test_fixed_code_separation_and_no_promotion(self):
        self.assertTrue(self.c["fixed_sources_prohibited_before_candidate_freeze"])
        self.assertFalse(self.c["pilot_is_true_external_blind"])
        self.assertTrue(self.c["allow_corrected_test_files_before_candidate_freeze"])
        self.assertTrue(self.c["no_merge_main"])
        self.assertIn("un SEUL projet",PREREG.read_text(encoding="utf8"))

if __name__=="__main__":
    unittest.main()
