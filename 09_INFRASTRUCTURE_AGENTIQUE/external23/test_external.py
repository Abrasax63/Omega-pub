#!/usr/bin/env python3
"""EXT23: source provenance, honest unsupported classification, no SEM22 regression."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "semantic22"))
from checker import verify_source, select_verified, parse_predicate
from evaluate import evaluate, read_frozen, transplant, blob

class ExternalHumanWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=read_frozen()
        cls.outcome=evaluate()

    def test_12_authentic_external_text_records_are_frozen(self):
        self.assertEqual(len(self.sources),12)
        self.assertEqual(len(set(x["id"] for x in self.sources)),12)
        self.assertEqual(len(set(x["source_url"] for x in self.sources)),12)
        self.assertEqual(len(set(x["quote"] for x in self.sources)),12)

    def test_sources_have_real_external_urls_and_not_invented_truth_labels(self):
        for source in self.sources:
            self.assertTrue(
                source["source_url"].startswith("https://math.stackexchange.com/questions/")
                or source["source_url"].startswith("https://fr.wikipedia.org/wiki/")
            )
            self.assertIn(source["source_type"],
                ("mathstackexchange_post","mathstackexchange_answer","wikipedia_fr_article"))
            self.assertIn("notes",source)
        self.assertFalse(self.outcome["semantic_generalization_demonstrated"])

    def test_original_text_unchanged_in_report_with_sha256(self):
        src={x["id"]:x for x in self.sources}
        for r in self.outcome["rows"]:
            original=src[r["id"]]["quote"]
            self.assertEqual(r["original_quote"],original)
            self.assertEqual(r["quote_sha256"],
                 hashlib.sha256(original.encode("utf8")).hexdigest())

    def test_raw_sources_are_not_falsely_interpreted_as_sem22_documents(self):
        for source in self.sources:
            raw=source["quote"].encode("utf8")
            out=verify_source(raw,expected_blob=blob(raw),
                              source_path=source["source_url"])
            self.assertEqual(out["status"],"UNSUPPORTED_SOURCE")
            self.assertEqual(out["results"],[])
            self.assertEqual(out["theorems_certified"],0)

    def test_claim_language_returns_indeterminate_not_false_or_true(self):
        for x in self.sources:
            kind,num,why=parse_predicate(x["quote"])
            self.assertEqual(kind,"UNSUPPORTED")
            self.assertIsNone(num)
            self.assertTrue(why)

    def test_transplant_preserves_original_excerpt_byte_for_byte(self):
        for x in self.sources:
            raw=transplant(x["quote"],x["id"])
            lines=raw.decode("utf8").splitlines()
            self.assertEqual(lines[8],x["quote"])
            report=verify_source(raw,expected_blob=blob(raw),
                        source_path="synthetic-lexical-scope.md")
            self.assertEqual(report["status"],"EVALUATED_FINITE_SCOPE")
            self.assertFalse(report["all_claims_checked"])
            self.assertEqual(len(report["results"]),1)
            self.assertEqual(report["results"][0]["verdict"],"INDETERMINATE")

    def test_unknown_external_quotes_cannot_be_promoted_by_selector(self):
        for src in self.sources:
            raw=transplant(src["quote"],src["id"])
            report=verify_source(raw,expected_blob=blob(raw),
                        source_path="synthetic-lexical-scope.md")
            filtered=select_verified(report,[9])
            self.assertEqual(filtered["selected_true_lines"],[])
            self.assertEqual(filtered["suppressed"][0]["reason"],"INDETERMINATE")
            self.assertEqual(filtered["unverified_claims_promoted"],0)

    def test_modified_source_hash_is_rejected_even_if_quote_is_valid(self):
        for src in self.sources:
            raw=src["quote"].encode("utf8")
            with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_MISMATCH"):
                verify_source(raw+b" changed",expected_blob=blob(raw),
                              source_path=src["source_url"])

    def test_numerical_modulus_is_not_silent_support(self):
        sample=next(s for s in self.sources if s["id"]=="EX06")
        self.assertIn("12",sample["quote"])
        self.assertIn("3x+1",sample["quote"])
        self.assertEqual(parse_predicate(sample["quote"])[0],"UNSUPPORTED")
        # Structural extraction and truth must be established separately.

    def test_ambiguous_symbolic_parameters_never_auto_instantiate(self):
        for id in ("EX01","EX02","EX03","EX04","EX05","EX08"):
            s=next(x for x in self.sources if x["id"]==id)
            self.assertEqual(parse_predicate(s["quote"])[0],"UNSUPPORTED")

    def test_external_coverage_is_reported_as_failure_not_success(self):
        r=self.outcome
        self.assertEqual(r["source_count"],12)
        self.assertEqual(r["supported_external_claim_count"],0)
        self.assertEqual(r["raw_source_abstentions"],12)
        self.assertEqual(r["claim_transplant_abstentions"],12)
        self.assertEqual(r["unsafe_true_or_false_predictions"],0)
        self.assertFalse(r["semantic_generalization_demonstrated"])

    def test_existing_sem22_168_claims_still_correct(self):
        frozen=json.loads((HERE.parent/"semantic22"/"FROZEN_ORACLE.json").read_text())
        self.assertEqual(len(frozen["docs"]),24)
        n=0
        for x in frozen["docs"]:
            raw=(ROOT/x["path"]).read_bytes()
            report=verify_source(raw,expected_blob=x["blob"],source_path=x["path"])
            self.assertEqual(report["status"],"EVALUATED_FINITE_SCOPE")
            self.assertTrue(report["all_claims_checked"])
            self.assertEqual(
                [v["line"] for v in report["results"] if v["verdict"]=="TRUE"],
                x["oracle_true_lines"]
            )
            n+=len(report["results"])
        self.assertEqual(n,168)

    def test_no_online_access_or_llm_needed_to_replay(self):
        self.assertEqual(self.outcome["status"],"EXTERNAL_TEXT_AUDIT_COMPLETED")
        self.assertEqual(self.outcome["automatic_promotions"],0)
        self.assertEqual(self.outcome["formal_certifications"],0)
        self.assertEqual(self.outcome["horn_rules"],[])

if __name__=="__main__":
    unittest.main()
