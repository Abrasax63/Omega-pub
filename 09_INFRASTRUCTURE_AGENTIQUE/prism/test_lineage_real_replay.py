"""Controlled 2026-11-13 GitHub logs used previously in development: NOT a holdout."""
import json
from pathlib import Path
import unittest

from lineage_adapter import compare_pair
from lineage_pilot import UNKNOWN, DISTINCT

BASE = Path(__file__).resolve().parent / "fixtures"


class PublicLogReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((BASE / "lineage_dev_run_43489499229.json").read_text(encoding="utf-8"))
        cls.cases = json.loads((BASE / "lineage_dev_pairs.json").read_text(encoding="utf-8"))

    def test_recompute_pair_distinct_and_selector_agrees(self):
        item = self.cases[0]
        result = compare_pair(self.snapshot, item["outputs"], budget=2)
        self.assertEqual(result["lineage"], DISTINCT)
        self.assertEqual(result["selector_translation"], DISTINCT)
        self.assertEqual(result["reads_charged_each"], 2)
        self.assertEqual(result["provenance_status"], "DECLARED_SNAPSHOT_NOT_AUTHENTICATED")

    def test_two_copies_abstain_without_traced_parent(self):
        item = self.cases[1]
        result = compare_pair(self.snapshot, item["outputs"], budget=1)
        self.assertEqual(result["lineage"], UNKNOWN)
        self.assertEqual(result["selector_translation"], UNKNOWN)
        self.assertEqual(result["reads_charged_each"], 1)

    def test_mixed_pair_abstains(self):
        item = self.cases[2]
        result = compare_pair(self.snapshot, item["outputs"], budget=1)
        self.assertEqual(result["lineage"], UNKNOWN)
        self.assertEqual(result["selector_translation"], UNKNOWN)

    def test_cross_job_unknown_sources_abstain(self):
        item = self.cases[3]
        result = compare_pair(self.snapshot, item["outputs"], budget=2)
        self.assertEqual(result["lineage"], UNKNOWN)
        self.assertEqual(result["selector_translation"], UNKNOWN)
        self.assertEqual(result["reads_charged_each"], 2)

    def test_cross_job_budget_one_abstains_before_reads(self):
        item = self.cases[0]
        result = compare_pair(self.snapshot, item["outputs"], budget=1)
        self.assertEqual(result["lineage"], UNKNOWN)
        self.assertEqual(result["selector_translation"], UNKNOWN)
        self.assertEqual(result["reads_charged_each"], 0)
        self.assertEqual(result["reason"], "budget_exceeded")


if __name__ == "__main__":
    unittest.main()
