import json
import tempfile
import unittest
from pathlib import Path

from evaluate import (
    ENGINE_PATH, ENGINE_SHA, GOLD, GOLD_SHA, INPUT, INPUT_SHA,
    SOURCES, finite_access_example, finite_fiber_example,
    git_blob, load_engine_frozen, pinned_file, run, verify_snapshots,
)


class CrossDomainTransferTests(unittest.TestCase):
    def test_frozen_files_and_four_new_sources(self):
        self.assertEqual(git_blob(ENGINE_PATH.read_bytes()), ENGINE_SHA)
        self.assertEqual(git_blob(INPUT.read_bytes()), INPUT_SHA)
        self.assertEqual(git_blob(GOLD.read_bytes()), GOLD_SHA)
        self.assertEqual(set(verify_snapshots()), set(SOURCES))

    def test_no_source_modifications(self):
        first = {k: v["historical_git_blob"] for k, v in verify_snapshots().items()}
        self.assertEqual(run(), run())
        second = {k: v["historical_git_blob"] for k, v in verify_snapshots().items()}
        self.assertEqual(first, second)

    def test_independent_finite_accessibility(self):
        result = finite_access_example()
        self.assertTrue(result["all_match"])
        self.assertEqual(result["checked_lengths"], 6)
        self.assertTrue(result["one_symbol_access_defect"])
        self.assertIn("1", result["per_length"][0]["words_H"])
        self.assertNotIn("1", ["0"])

    def test_independent_finite_fiber_box(self):
        result = finite_fiber_example()
        self.assertTrue(result["all_match"])
        self.assertEqual(result["subsets_enumerated"], 16)
        self.assertEqual(result["distinct_multiplicity_vectors"], 9)

    def test_corrupted_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "fake.md"
            file.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "source/gold modified"):
                pinned_file(file, SOURCES["BR-ACC-01"][1])

    def test_no_claim_of_semantic_transfer_from_abstaining(self):
        report = run()
        self.assertEqual(report["gold_class_distribution"],
                         {"SUPPORTED": 6, "CONTRADICTED": 6, "ABSTAIN": 4})
        self.assertEqual(report["frozen_engine"]["total"], 16)
        self.assertEqual(report["frozen_engine"]["false_confident"], [])
        self.assertEqual(report["abstain_all_baseline"]["correct"], 4)
        self.assertTrue(report["finite_microchecks_passed"])
        self.assertFalse(report["pre_registered_transfer_criterion_met"])
        self.assertEqual(len(report["unrecognized_source_ids_by_engine"]), 4)


if __name__ == "__main__":
    unittest.main()
