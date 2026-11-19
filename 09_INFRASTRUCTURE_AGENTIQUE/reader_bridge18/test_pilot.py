#!/usr/bin/env python3
"""Offline regression tests for Reader18: real Git blobs, blind retrieval, toy oracle."""
import json
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pilot import (
    MAX_CANDIDATES, MAX_SELECTED, ROOT,
    audit_toy_oracle, build_report, exact_arithmetic_oracle,
    grounded_claims, load_manifest, number_sections,
    round_robin_by_section, source_policies, synthetic_arithmetic,
)
from gate import gate
from read import safe_read


class Reader18SourceAndOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_manifest()
        cls.policies = [source_policies(d) for d in cls.docs]

    def test_three_new_immutable_documents(self):
        self.assertEqual(len(self.docs), 3)
        paths = [d["path"] for d in self.docs]
        self.assertEqual(len(set(paths)), 3)
        self.assertFalse(any("temps_regle90" in p for p in paths))
        self.assertFalse(any("RECONCILIATION_CL_DYN" in p for p in paths))
        for ref, p in zip(self.docs, self.policies):
            self.assertEqual(p["blob"], ref["blob"])
            self.assertEqual(len(safe_read(ROOT / ref["path"], ref["blob"])), ref["bytes"])

    def test_known_round_robin_spans_more_sections_than_first12(self):
        # In-memory fixture independent of the real-source cohort.
        source = ([{"line": n, "section": "A"} for n in range(1, 11)]
                  + [{"line": 11, "section": "B"}]
                  + [{"line": 12, "section": "C"}])
        balanced = round_robin_by_section(source, 5)
        self.assertEqual([x["line"] for x in balanced], [1, 11, 12, 2, 3])
        self.assertEqual(number_sections(balanced), 3)
        self.assertEqual(number_sections(source[:5]), 1)
        self.assertEqual(round_robin_by_section([], 12), [])

    def test_policies_source_only_deterministic_and_cap(self):
        for ref, result in zip(self.docs, self.policies):
            repeat = source_policies(ref)
            self.assertEqual(repeat, result)
            names = set(result["policies"])
            self.assertEqual(names, {
                "D_title_bound_first12",
                "E_headings_agnostic_first12",
                "E_headings_agnostic_balanced12",
            })
            e_pool = result["policies"]["E_headings_agnostic_balanced12"]
            control_pool = result["policies"]["E_headings_agnostic_first12"]
            self.assertEqual(e_pool["total_candidates_after_gate"],
                             control_pool["total_candidates_after_gate"])
            for p in result["policies"].values():
                self.assertLessEqual(p["submitted_count"], MAX_CANDIDATES)
                self.assertEqual(p["submitted_count"], len(p["submitted"]))
                self.assertLessEqual(p["submitted_sections"], p["total_sections_after_gate"])
                self.assertEqual(p["truncated_count"],
                                 p["total_candidates_after_gate"] - p["submitted_count"])
                self.assertEqual(len({c["line"] for c in p["submitted"]}),
                                 p["submitted_count"])
                self.assertEqual(p["model"]["status"], "NOT_RUN")
            self.assertEqual(result["balanced_section_coverage_delta"],
                             e_pool["submitted_sections"]-control_pool["submitted_sections"])

    def test_reconstruction_only_from_sources_and_no_certification(self):
        for ref, record in zip(self.docs, self.policies):
            raw = safe_read(ROOT / ref["path"], ref["blob"])
            for policy in record["policies"].values():
                offered = policy["submitted"]
                picks = [c["line"] for c in offered[:MAX_SELECTED]]
                proposal = grounded_claims(ref, offered, picks)
                staged = gate(raw, str(ROOT / ref["path"]), proposal, provider="unit-test")
                self.assertEqual(staged["accepted_count"], len(picks))
                self.assertEqual(staged["rejected_count"], 0)
                self.assertFalse(staged["horn_rules"])
                self.assertEqual(staged["automatic_promotions"], 0)
                self.assertTrue(all(not claim["promotable"] for claim in staged["accepted"]))
                with self.assertRaisesRegex(ValueError, "UNAUTHORIZED"):
                    grounded_claims(ref, offered, [999999])
                if picks:
                    with self.assertRaisesRegex(ValueError, "UNAUTHORIZED"):
                        grounded_claims(ref, offered, [picks[0]]*2)

    def test_arithmetic_oracle_valid_invalid_and_scope(self):
        self.assertEqual(exact_arithmetic_oracle("Résultat : 17 * 19 = 323")["status"],
                         "ARITHMETIC_IDENTITY_TRUE")
        self.assertEqual(exact_arithmetic_oracle("Résultat : 17 * 19 = 324")["status"],
                         "ARITHMETIC_IDENTITY_FALSE")
        for text in (
            "17 * 19 = 323", "Preuve : 17 * 19 = 323", "Résultat : -4 * 2 = -8",
            "Résultat : 1000 * 2 = 2000", "Résultat : 3 / 3 = 1",
            "Résultat : x * 8 = 24", "Résultat : 2 * 3 = 6 ; même si faux",
            None,
        ):
            with self.subTest(text=text):
                self.assertEqual(exact_arithmetic_oracle(text)["status"], "NOT_APPLICABLE")
        cases = synthetic_arithmetic()
        self.assertEqual(len(cases), 8)
        self.assertEqual(sum(bool(x["expected_truth"]) for x in cases), 4)
        self.assertEqual(audit_toy_oracle()["correct"], 8)
        self.assertEqual(audit_toy_oracle()["false_equalities_detected"], 4)

    def test_no_source_gold_and_no_false_scientific_status(self):
        report = build_report(self.docs)
        self.assertEqual(report["mode"], "OFFLINE")
        self.assertEqual(report["model_calls_made"], 0)
        self.assertFalse(report["source_labels_available"])
        self.assertFalse(report["human_independent_annotations"])
        self.assertFalse(report["cost_equalized"])
        self.assertEqual(report["scientific_claims_certified"], 0)
        self.assertEqual(report["horn_rules"], 0)
        self.assertEqual(report["H2_status"], "PASS_TOY_ARITHMETIC_ONLY")
        self.assertEqual(len(report["items"]), 3)

    def test_mock_model_uses_same_prompt_and_never_publishes(self):
        for ref in self.docs:
            attempts = []
            def dummy(messages):
                attempts.append(messages)
                self.assertEqual([x["role"] for x in messages], ["system", "user"])
                return {"raw_reply": "NONE", "duration_s": 0.0, "tokens": {}}
            report = build_report([ref], caller=dummy)
            self.assertLessEqual(len(attempts), 2)
            self.assertEqual(report["model_calls_made"], len(attempts))
            self.assertEqual(report["scientific_claims_certified"], 0)
            for name in ("D_title_bound_first12","E_headings_agnostic_balanced12"):
                model = report["items"][0]["policies"][name]["model"]
                if model["status"] != "NO_CANDIDATES":
                    self.assertEqual(model["status"], "VALID_REPLY")
                    self.assertEqual(model["source_citations_admitted"], 0)
                    self.assertFalse(model["semantic_accuracy_verified"])

    def test_mock_forged_model_line_rejected(self):
        def fake(_):
            return {"raw_reply": "999999", "duration_s": 0.0, "tokens": {}}
        report = build_report(self.docs, caller=fake)
        for row in report["items"]:
            for name in ("D_title_bound_first12","E_headings_agnostic_balanced12"):
                model = row["policies"][name]["model"]
                if model["status"] != "NO_CANDIDATES":
                    self.assertEqual(model["status"], "INVALID_REPLY")
                    self.assertEqual(model["selected"], [])
                    self.assertNotIn("source_citations_admitted", model)


if __name__ == "__main__":
    unittest.main(verbosity=2)
