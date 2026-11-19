#!/usr/bin/env python3
"""Reader16 offline tests: source-only ablation; no model and no certification."""
import json
import sys
from pathlib import Path
from unittest import TestCase, main

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit import GOLD, ROOT, build_report, score_ceiling, source_policies


class SourceCoverageAuditTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.references = json.loads(GOLD.read_text(encoding="utf-8"))
        cls.blind = [
            source_policies(ROOT / r["path"], r["blob"])
            for r in cls.references["documents"]
        ]

    def test_source_hash_and_replay_are_stable(self):
        for r, p in zip(self.references["documents"], self.blind):
            repeat = source_policies(ROOT / r["path"], r["blob"])
            self.assertEqual(p["candidate_sets_sha256"], repeat["candidate_sets_sha256"])
            self.assertEqual(p["A_original"]["lines"], repeat["A_original"]["lines"])
            self.assertEqual(p["B_all_lines_in_reader13_packets"]["lines"],
                             repeat["B_all_lines_in_reader13_packets"]["lines"])
            self.assertEqual(p["C_all_lines_in_statement_packets"]["lines"],
                             repeat["C_all_lines_in_statement_packets"]["lines"])
            self.assertEqual(p["source_blob"], r["blob"])

    def test_no_gold_dependency_in_source_candidate_generation(self):
        # The blind function only accepts immutable source path + blob; no gold
        # or score, even when reference labels are deliberately altered.
        r = dict(self.references["documents"][0])
        p = self.blind[0]
        fabricated = dict(r, conclusion_lines=[99999])
        scored_original = score_ceiling(p, r)
        scored_fabricated = score_ceiling(p, fabricated)
        self.assertEqual(scored_original["candidate_sets_sha256"],
                         scored_fabricated["candidate_sets_sha256"])
        for key in scored_original["policies"]:
            self.assertEqual(scored_original["policies"][key]["lines_offered"],
                             scored_fabricated["policies"][key]["lines_offered"])

    def test_all_policies_remain_quarantined_and_source_bound(self):
        for r, p in zip(self.references["documents"], self.blind):
            max_lines = p["source_lines"]
            for name in ("A_original", "B_all_lines_in_reader13_packets",
                         "C_all_lines_in_statement_packets"):
                out = p[name]
                self.assertEqual(out["automatic_promotions"], 0)
                self.assertEqual(out["horn_rules"], [])
                self.assertEqual(len(out["lines"]), out["accepted_count"])
                self.assertTrue(all(1 <= n <= max_lines for n in out["lines"]))
                self.assertEqual(len(set(out["lines"])), len(out["lines"]))

    def test_diagnostic_known_bottlenecks_are_not_promoted(self):
        # Post-hoc regression on *known* documents, not scientific holdout.
        p = self.blind[0]
        self.assertNotIn(30, p["A_original"]["lines"])
        self.assertIn(30, p["B_all_lines_in_reader13_packets"]["lines"])
        self.assertNotIn(35, p["visible_lines"])
        self.assertIn(35, p["C_all_lines_in_statement_packets"]["lines"])

    def test_aggregates_and_author_label_status(self):
        report = build_report(self.references)
        self.assertEqual(report["totals"]["gold_total"], 7)
        self.assertEqual(report["totals"]["gold_visible_reader13"], 6)
        self.assertEqual(report["label_status"], "AUTHOR_LABELS_UNREVIEWED_NOT_INDEPENDENT")
        self.assertFalse(report["scientific_certification"])
        self.assertTrue(report["no_neural_inference"])
        for key in ("A_original", "B_all_lines_in_reader13_packets",
                    "C_all_lines_in_statement_packets"):
            x = report["totals"][key]
            self.assertLessEqual(x["gold_recoverable"], report["totals"]["gold_total"])
            self.assertLessEqual(x["max_oracle_top3_correct"], x["gold_recoverable"])


if __name__ == "__main__":
    main(verbosity=2)
