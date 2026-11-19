#!/usr/bin/env python3
"""DUAL25: blind-within-packet independent reviewer intake is NEVER auto-certified."""
from __future__ import annotations
import copy
import unittest

from experiment import controlled,external,review_packet
from review_intake import (
    build_blank_template, validate_submission_schema, validate_two_reviews
)


class HumanAnnotationSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c,bc=controlled()
        e,be=external()
        cls.packet=review_packet(bc,be)
        cls.blank=build_blank_template(cls.packet)

    def fake_filled_schema(self,pseudonym:str)->dict:
        # A synthetic fixture to validate the software schema, NOT a genuine
        # submission or evidence of an actual reviewer.
        form=copy.deepcopy(self.blank)
        form["reviewer_pseudonym"]=pseudonym
        form["reviewer_declares_independence"]=True
        form["reviewer_saw_formalizer_outputs"]=False
        byid={x["id"]:x for x in self.packet["items"]}
        for row in form["labels"]:
            source=byid[row["id"]]
            text=source.get("source_text_original",source.get("literal_quote",""))
            row["human_decision"]="CONTEXT_INSUFFICIENT"
            row["reasoning_citation_from_source"]=text[:min(20,len(text))]
        return form

    def test_frozen_packet_contains_42_source_items_not_proposals(self):
        self.assertEqual(self.packet["source_count"],42)
        self.assertEqual(len(self.packet["items"]),42)
        self.assertTrue(self.packet["labels_and_machine_proposals_excluded"])

    def test_blank_form_is_incomplete_and_cannot_pass_as_human_review(self):
        self.assertEqual(self.blank["submission_status"],"NOT_STARTED_NO_HUMAN_LABELS")
        self.assertEqual(len(self.blank["labels"]),42)
        self.assertTrue(all(x["human_decision"]=="NOT_REVIEWED" for x in self.blank["labels"]))
        with self.assertRaisesRegex(ValueError,"REVIEWER_ATTESTATIONS_MISSING"):
            validate_submission_schema(self.packet,self.blank)

    def test_schema_fixtures_never_certify_human_independence_or_fidelity(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        result=validate_submission_schema(self.packet,form)
        self.assertEqual(result["labels_count"],42)
        self.assertFalse(result["independent_reviewer_identity_verified"])
        self.assertFalse(result["human_fidelity_metrics_certified"])
        self.assertEqual(result["automatic_promotions"],0)

    def test_source_hash_mismatch_rejected(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        form["labels"][0]["source_digest"]="0"*40
        with self.assertRaisesRegex(ValueError,"REVIEW_SOURCE_DIGEST_MISMATCH"):
            validate_submission_schema(self.packet,form)

    def test_missing_or_duplicate_ids_rejected(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        form["labels"][-1]["id"]=form["labels"][0]["id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_UNKNOWN_REVIEW_ID"):
            validate_submission_schema(self.packet,form)

    def test_missing_context_evidence_rejected(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        form["labels"][0]["reasoning_citation_from_source"]="made-up reference"
        with self.assertRaisesRegex(ValueError,"HUMAN_CITATION_NOT_IN_SOURCE"):
            validate_submission_schema(self.packet,form)

    def test_false_independence_attestation_rejected(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        form["reviewer_saw_formalizer_outputs"]=True
        with self.assertRaisesRegex(ValueError,"REVIEWER_ATTESTATIONS_MISSING"):
            validate_submission_schema(self.packet,form)

    def test_two_distinct_fixture_pseudonyms_do_not_become_fidelity_certification(self):
        a=self.fake_filled_schema("synthetic_test_only_a")
        b=self.fake_filled_schema("synthetic_test_only_b")
        result=validate_two_reviews(self.packet,a,b)
        self.assertEqual(result["n_annotated"],42)
        self.assertFalse(result["actual_human_identity_independence_verified"])
        self.assertIsNone(result["human_semantic_fidelity_estimate"])
        self.assertEqual(result["certifications"],0)

    def test_same_reviewer_id_cannot_count_as_two_reviewers(self):
        a=self.fake_filled_schema("synthetic_test_only_a")
        with self.assertRaisesRegex(ValueError,"SAME_PSEUDONYM"):
            validate_two_reviews(self.packet,a,copy.deepcopy(a))

    def test_determinate_review_must_have_explicit_typed_meaning(self):
        form=self.fake_filled_schema("synthetic_test_only_a")
        form["labels"][0]["human_decision"]="DETERMINATE"
        with self.assertRaisesRegex(ValueError,"DETERMINATE_REVIEW_WITHOUT_TYPED_MEANING"):
            validate_submission_schema(self.packet,form)

if __name__=="__main__":
    unittest.main()
