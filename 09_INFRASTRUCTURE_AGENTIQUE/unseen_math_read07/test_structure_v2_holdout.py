import unittest
from pathlib import Path
from extract import git_blob
from structure_v2 import run, verify_structure_output
from evaluate_structure_v2 import ENGINE, ENGINE_BLOB, GOLD, GOLD_BLOB, SOURCE_ROOT, evaluate


class TwoNewMathHoldouts(unittest.TestCase):
    def test_frozen_program_and_gold_identity(self):
        self.assertEqual(git_blob(ENGINE.read_bytes()), ENGINE_BLOB)
        self.assertEqual(git_blob(GOLD.read_bytes()), GOLD_BLOB)

    def test_new_source_snapshots_unchanged(self):
        paths = {
            "BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md":
                "b7f79410a589dd8ba62a997860c924593e85a73c",
            "BR-OBS-01_ADAPTATIF_VS_PREDEFINI.md":
                "aa8425b35c8d9ad2175b9f05d42d4b624f51e75d",
        }
        for path, blob in paths.items():
            self.assertEqual(git_blob((SOURCE_ROOT / path).read_bytes()), blob)

    def test_independent_quote_replay_for_both_holdouts(self):
        for file in SOURCE_ROOT.glob("*.md"):
            result = run(file)
            self.assertTrue(result["citations_valid"])
            self.assertEqual(
                verify_structure_output(file.read_bytes(), result), []
            )

    def test_every_item_unreviewed_and_no_automatic_formal_claim(self):
        for file in SOURCE_ROOT.glob("*.md"):
            for item in run(file)["items"]:
                self.assertEqual(item["scientific_status"],
                                 "CANDIDATE_UNREVIEWED_NOT_A_PROOF")
                self.assertNotIn("formalized_lemma", item)

    def test_evaluation_determinism_and_provenance(self):
        a = evaluate()
        b = evaluate()
        self.assertEqual(a, b)
        self.assertEqual(a["salient_total"], 16)
        self.assertTrue(a["all_citations_valid"])
        self.assertEqual(a["false_warning_promotions"], [])


if __name__ == "__main__":
    unittest.main()
