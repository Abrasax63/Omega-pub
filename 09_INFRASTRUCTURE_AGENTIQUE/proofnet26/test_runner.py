#!/usr/bin/env python3
"""PROOFNET26: safety, provenance and comparator honesty, network-free tests."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from runner import (
    manifest,extract_original_pair,run_frontends,fetch_pinned,
    _wrapper,git_blob,INDICES,SOURCE_COMMIT,NL_COMMENT,FORMAL_THEOREM,
)


def fixture()->bytes:
    return (
        "import Mathlib\n\n"
        "/-Informal Statement\n\n"
        "Let H be a finite group. Prove that H contains an identity element.\n"
        "-/\n\n"
        "theorem synthetic_group_example {H : Type*} [Group H] :\n"
        "  ∃ x : H, x = 1 := by\n"
        "  sorry\n"
    ).encode("utf8")


class ProofNetExternalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pinned=manifest()

    def test_16_external_cases_and_blobs_frozen_before_code(self):
        self.assertEqual(self.pinned["n_cases"],16)
        self.assertEqual(tuple(x["index"] for x in self.pinned["items"]),INDICES)
        self.assertEqual(self.pinned["source_commit"],SOURCE_COMMIT)
        self.assertEqual(len({x["git_blob"] for x in self.pinned["items"]}),16)

    def test_reference_is_external_human_plus_ai_not_two_fresh_humans(self):
        self.assertIn("NOT two independent new human annotations",
                      self.pinned["upstream_review_description"])
        self.assertEqual(self.pinned["upstream_license"],"Apache-2.0")
        self.assertEqual(self.pinned["reference_kind"],
                         "PAIRED_CURATED_NATURAL_LANGUAGE_AND_LEAN4_THEOREM")

    def test_each_reference_uses_immutable_url(self):
        for item in self.pinned["items"]:
            self.assertIn(SOURCE_COMMIT,item["source_url"])
            self.assertIn("proofnet-"+str(item["index"])+".lean",item["source_url"])
            self.assertEqual(len(item["git_blob"]),40)

    def test_complete_source_with_original_pair_and_exact_spans(self):
        raw=fixture()
        pair=extract_original_pair(raw,{"index":999,"source_url":"fixture.lean","git_blob":git_blob(raw)})
        self.assertIn("finite group",pair["informal_statement_exact"])
        self.assertIn("theorem synthetic_group_example",pair["reference_lean_theorem_exact"])
        self.assertEqual(pair["external_source_sha"],git_blob(raw))
        self.assertTrue(pair["original_source_replayed"])

    def test_plain_natural_language_is_not_a_formal_proof(self):
        raw=fixture()
        pair=extract_original_pair(raw,{"index":999,"source_url":"fixture.lean","git_blob":git_blob(raw)})
        out=run_frontends(pair["informal_statement_exact"].encode("utf8"),source_path="fixture-nl")
        self.assertNotEqual(out["comparison_gate"],"AGREED_LOCAL_CONTRACT_AWAITING_HUMAN")
        self.assertEqual(out["human_fidelity_to_reference"],"NOT_COMPARABLE_TYPE_SYSTEMS")

    def test_no_fabricated_domain_in_neutral_layout(self):
        source=fixture()
        pair=extract_original_pair(source,{"index":999,"source_url":"fixture.lean","git_blob":git_blob(source)})
        wrapper=_wrapper(pair["informal_statement_exact"],999).decode("utf8")
        self.assertIn(pair["informal_statement_exact"],wrapper)
        self.assertNotIn("On travaille dans",wrapper)
        self.assertNotIn("f(x) =",wrapper)
        r=run_frontends(wrapper.encode("utf8"),source_path="fixture-wrapper")
        self.assertNotEqual(r["comparison_gate"],"AGREED_LOCAL_CONTRACT_AWAITING_HUMAN")

    def test_source_mutation_is_not_repaired_from_context(self):
        with tempfile.TemporaryDirectory() as folder:
            testpath=Path(folder)/"1.lean"
            raw=fixture()
            item={"index":1,"git_blob":git_blob(raw)}
            testpath.write_bytes(raw)
            self.assertEqual(fetch_pinned(item,cache_dir=Path(folder)),raw)
            testpath.write_bytes(raw+b" " + b"fake")
            with self.assertRaisesRegex(ValueError,"UPSTREAM_SOURCE_GIT_HASH_MISMATCH"):
                fetch_pinned(item,cache_dir=Path(folder))

    def test_missing_lean_reference_is_an_error_not_an_abstention(self):
        raw=fixture().replace(b"theorem synthetic_group_example",b"def synthetic_group_example")
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_EXTERNAL_NL_LEAN_PAIR"):
            extract_original_pair(raw,{"index":999,"source_url":"fixture","git_blob":git_blob(raw)})

    def test_missing_natural_language_is_an_error_not_guessed(self):
        raw=fixture().replace(b"Informal Statement",b"Informal Solution")
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_EXTERNAL_NL_LEAN_PAIR"):
            extract_original_pair(raw,{"index":999,"source_url":"fixture","git_blob":git_blob(raw)})

    def test_duplicate_natural_language_markers_refused(self):
        raw=fixture().replace(b"/-Informal Statement",b"/-Informal Statement")
        fake=(raw+b"\n"+b"/-Informal Statement\nSecond statement\n-/\n")
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_EXTERNAL_NL_LEAN_PAIR"):
            extract_original_pair(fake,{"index":999,"source_url":"fixture","git_blob":git_blob(fake)})

    def test_no_leakage_of_reference_lean_into_a_b(self):
        raw=fixture()
        pair=extract_original_pair(raw,{"index":999,"source_url":"fixture","git_blob":git_blob(raw)})
        nl_only=pair["informal_statement_exact"].encode("utf8")
        self.assertNotIn(b"theorem ",nl_only)
        self.assertNotIn(b"sorry",nl_only)
        a=run_frontends(nl_only,source_path="proofnet-test")
        self.assertNotIn("lean_proof_verification",a)
        self.assertEqual(a["reference_lean_compared"],"NO_IR_TO_LEAN_EQUIVALENCE_IMPLEMENTED")

    def test_plain_unknown_short_statement_abstains(self):
        out=run_frontends(b"x",source_path="external-short")
        self.assertNotEqual(out["comparison_gate"],"AGREED_LOCAL_CONTRACT_AWAITING_HUMAN")

    def test_unverified_lean_reference_cannot_claim_omega_typecheck(self):
        raw=fixture()
        report=extract_original_pair(raw,{"index":999,"source_url":"fixture","git_blob":git_blob(raw)})
        self.assertEqual(report["formal_lean_status"],
             "EXTERNALLY_AUDITED_REFERENCE_NOT_COMPILED_BY_OMEGA")

    def test_missing_offline_file_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,"EXPECTED_PINNED_OFFLINE_CACHE_FILE"):
                fetch_pinned({"index":1,"git_blob":"f"*40},cache_dir=Path(folder))


if __name__=="__main__":
    unittest.main()
