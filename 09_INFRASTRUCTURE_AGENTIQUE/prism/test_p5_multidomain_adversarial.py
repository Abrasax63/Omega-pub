"""Falsifiable regression suite for the multidomain adversarial benchmark."""
import json
from pathlib import Path
from urllib.parse import urljoin
import unittest

from p5_multidomain_adversarial import DATA, evidence_model, run_case, summarize
from action_planning_two_step import optimize_policy


class MultidomainAdversarialP5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(DATA.read_text(encoding="utf-8"))
        cls.rows = cls.snapshot["cases"]

    def test_public_corpus_four_strata_and_frozen_attacks(self):
        self.assertEqual(len(self.rows), 24)
        self.assertEqual(len({r["id"] for r in self.rows}), 24)
        self.assertEqual({d:sum(r["domain"] == d for r in self.rows)
                          for d in ("github", "http", "uri", "python")},
                         {"github":6, "http":6, "uri":6, "python":6})
        self.assertEqual([i for i,r in enumerate(self.rows)
                          if r["spoof_primary_in_adversarial"]],
                         [0,3,6,9,12,15,18,21])
        self.assertEqual(sum(r["secondary_note_claim"] != r["truth"]
                             for r in self.rows), 8)
        self.assertTrue(all(r["secondary_note_is_fabricated"] for r in self.rows))

    def test_source_specific_independent_runtime_checks(self):
        # Separate observation route for URI RFC 3986 examples.
        for r in self.rows:
            if r["domain"] == "uri":
                actual = urljoin("http://a/b/c/d;p?q", r["reference_relative"])
                self.assertEqual(actual == r["candidate_url"], r["truth"])
        # Explicit expressions only: never eval arbitrary data from source JSON.
        py_expected = {
            "isinstance(True,int)": isinstance(True, int),
            "type(True) is int": type(True) is int,
            "issubclass(bool,int)": issubclass(bool, int),
            "True == 1": True == 1,
            "(True + True) == 2": (True + True) == 2,
            "type(False) is bool": type(False) is bool,
        }
        py_rows = [r for r in self.rows if r["domain"] == "python"]
        self.assertEqual(len(py_rows), len(py_expected))
        for r in py_rows:
            expr = r["expression"]
            self.assertIn(expr, py_expected)
            self.assertIs(py_expected[expr], r["truth"])

    def test_omega_policy_really_executes_and_single_check_budget(self):
        for row in self.rows:
            p = optimize_policy(evidence_model(row), max_depth=1,
                                max_cost_milli=5)
            self.assertEqual(p["action"], "verify")
            self.assertEqual(p["policy"]["check_id"], "00-primary-source")
            self.assertEqual(p["expected_total_loss"], "1/200")
            for condition in (False, True):
                actual = run_case(row, spoof=condition)
                self.assertEqual(actual["omega_calls"], 1)
                self.assertEqual(actual["fixed_calls"], 1)
                self.assertEqual(actual["omega"], actual["fixed"])
                self.assertEqual(
                    actual["omega"] != row["truth"],
                    bool(condition and row["spoof_primary_in_adversarial"]),
                )

    def test_adversarial_confidence_regression_and_diagnostic_abstention(self):
        report = summarize()
        clean = report["results"]["intact"]["total"]
        attacked = report["results"]["spoofed"]["total"]
        self.assertEqual((clean["cases"], attacked["cases"]), (24,24))
        self.assertEqual((clean["direct_correct"], attacked["direct_correct"]),
                         (16,16))
        self.assertEqual((clean["fixed_correct"], clean["omega_correct"]),
                         (24,24))
        self.assertEqual((attacked["fixed_correct"], attacked["omega_correct"]),
                         (16,16))
        self.assertEqual((clean["omega_false_certainties"],
                          attacked["omega_false_certainties"]), (0,8))
        self.assertEqual((clean["oracle_audit_correct"], clean["oracle_audit_abstentions"]),
                         (24,0))
        self.assertEqual((attacked["oracle_audit_correct"],
                          attacked["oracle_audit_abstentions"]), (16,8))
        self.assertEqual((attacked["fixed_calls"], attacked["omega_calls"]), (24,24))
        for domain, result in report["results"]["spoofed"]["by_domain"].items():
            self.assertEqual(result["cases"], 6)
            self.assertEqual(result["omega_false_certainties"], 2)


if __name__ == "__main__":
    unittest.main()
