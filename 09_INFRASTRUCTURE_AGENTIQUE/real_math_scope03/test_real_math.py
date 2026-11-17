import copy
import json
import unittest
from pathlib import Path

from engine import ROOT, evaluate_case, git_blob, verify_sources
from evaluate import (
    INPUT, GOLD, INPUT_SHA, GOLD_SHA, frozen, majority_uniform_exact,
    rule90_finite_invariant, run,
)


class RealMathScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = verify_sources(ROOT)
        cls.cases = {c["id"]: c for c in frozen(INPUT, INPUT_SHA)["cases"]}

    def test_original_documents_pinned_and_unchanged(self):
        self.assertEqual(len(self.notes), 3)
        self.assertEqual(len(self.cases), 24)
        self.assertEqual(len(frozen(GOLD, GOLD_SHA)["cases"]), 24)
        for note in self.notes.values():
            self.assertEqual(git_blob((ROOT / note["path"]).read_bytes()), note["blob"])

    def test_gf2_gaussian_elimination_not_formula(self):
        self.assertEqual(rule90_finite_invariant(12, 2, "kernel"), 4)
        self.assertEqual(rule90_finite_invariant(10, 3, "rank"), 8)
        self.assertEqual(rule90_finite_invariant(9, 0, "kernel"), 0)
        for n in range(2, 17):
            for t in range(5):
                # Only a *test* compares this independent algorithm to the
                # asserted general formula; no proof of universality follows.
                a = n & -n
                self.assertEqual(rule90_finite_invariant(n, t, "kernel"), min(2*t, a))

    def test_majority_full_state_enumeration_on_finite_scoped_cases(self):
        for n, h in ((5, 1), (7, 2), (9, 3)):
            uniform, buckets = majority_uniform_exact(n, h)
            self.assertTrue(uniform)
            self.assertEqual(sum(buckets), 1 << n)
            self.assertEqual(len(set(buckets)), 1)

    def test_formulation_variants_and_truth_by_card_scope(self):
        for identifier in ("K01", "K02", "K03", "K04", "K07",
                           "W01", "W02", "W03", "W05",
                           "C01", "C03", "C08"):
            self.assertEqual(evaluate_case(self.cases[identifier], self.notes)["verdict"], "SUPPORTED", identifier)
        for identifier in ("K05", "K06", "W04", "W08", "C02", "C05"):
            self.assertEqual(evaluate_case(self.cases[identifier], self.notes)["verdict"], "CONTRADICTED", identifier)
        for identifier in ("K08", "W06", "W07", "C04", "C06", "C07"):
            self.assertEqual(evaluate_case(self.cases[identifier], self.notes)["verdict"], "ABSTAIN", identifier)

    def test_no_converse_from_majority_sufficient_condition(self):
        for identifier in ("W06", "W07"):
            answer = evaluate_case(self.cases[identifier], self.notes)
            self.assertEqual(answer["verdict"], "ABSTAIN")
            self.assertIn("sufficient", answer["reason"])

    def test_c4_scope_fails_closed_on_missing_v19(self):
        x = copy.deepcopy(self.cases["C03"])
        x["question"] = x["question"].replace("V19(2)", "")
        self.assertEqual(evaluate_case(x, self.notes)["verdict"], "ABSTAIN")

    def test_evidence_lines_and_source_are_resolvable(self):
        x = evaluate_case(self.cases["K05"], self.notes)
        ev = x["evidence"]
        note = self.notes["BR-R90-01"]
        self.assertEqual(ev["source_blob"], note["blob"])
        self.assertEqual(note["text"].splitlines()[ev["line"]-1].strip(), ev["excerpt"])

    def test_no_source_file_writes_and_exact_report(self):
        original = (ROOT / self.notes["BR-R90-01"]["path"]).read_bytes()
        report = run()
        self.assertEqual(original, (ROOT / self.notes["BR-R90-01"]["path"]).read_bytes())
        self.assertEqual(report, run())
        self.assertTrue(report["finite_checks_passed"])
        self.assertTrue(report["all_source_citations_valid"])
        self.assertEqual(report["engine_metrics"]["total"], 24)


if __name__ == "__main__":
    unittest.main()
