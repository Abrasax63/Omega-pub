"""Adversarial tests: provenance signature and scientific verdict remain separate."""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from attested_evidence_bridge import select_with_attested_artifact, UNKNOWN
from provenance_selection import Piece

REPO = "Abrasax63/Omega-pub"
COMMIT = "a"*40


class BridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.artifact = self.root / "result.json"
        self.artifact.write_bytes(b"observed controlled result")
        self.bundle = self.root / "bundle.jsonl"
        self.bundle.write_text("FAKE")
        self.trusted_root = self.root / "root.jsonl"
        self.trusted_root.write_text("FAKE")
        self.digest = sha256(self.artifact.read_bytes()).hexdigest()
        self.pieces = [Piece("trace", "execution", "job1", "result.json")]

    def record(self, **change):
        return {"job": "job1", "output": "result.json", "complete": True,
                "success": True, "operation": "recalcul",
                "artifact_sha256": self.digest} | change

    def run_case(self, records=None, outcome="VERIFIED_BUILD_ONLY",
                 pieces=None, **kwargs):
        inputs = self.__dict__
        if records is None:
            records = {"trace": self.record()}
        verification_calls = []
        def verifier(*args):
            verification_calls.append(args)
            if outcome == "VERIFY_FAILED":
                return {"status": "INDETERMINATE", "signature_verified": False}
            return {"status": "VERIFIED_BUILD_PROVENANCE_ONLY",
                    "signature_verified": True,
                    "artifact_sha256": self.digest}
        def reader(key):
            return records[key]
        opts = {"job": "job1", "output": "result.json", "budget": 2,
                "artifact": self.artifact, "bundle": self.bundle,
                "trusted_root": self.trusted_root, "repository": REPO,
                "repository_id": 1309584710,
                "signer_workflow": REPO + "/.github/workflows/smoke.yml",
                "source_commit": COMMIT, "verifier": verifier}
        opts.update(kwargs)
        result = select_with_attested_artifact(self.pieces if pieces is None else pieces,
                                               reader, **opts)
        return result, verification_calls

    def test_valid_attestation_does_not_certify_science_or_log(self):
        result, calls = self.run_case()
        self.assertEqual(result["operation_from_untrusted_log"], "recalcul")
        self.assertEqual(result["signed_build_provenance"], "VERIFIED_BUILD_ONLY")
        self.assertEqual(result["log_artifact_digest_agreement"],
                         "MATCHES_LOG_CLAIM_NOT_ATTESTED")
        self.assertEqual(result["scientific_verdict"], "INDETERMINATE")
        self.assertEqual(result["scientific_independence"], "NOT_ESTABLISHED")
        self.assertEqual(result["routing"],
                         "AUDIT_LOG_SOURCE_AND_INDEPENDENT_REPRODUCTION")
        self.assertEqual(result["logs_read"], ["trace"])
        self.assertEqual(result["signature_verification_attempts"], 1)
        self.assertEqual(len(calls), 1)

    def test_crypto_failure_preserves_only_untrusted_log_observation(self):
        result, calls = self.run_case(outcome="VERIFY_FAILED")
        self.assertEqual(result["operation_from_untrusted_log"], "recalcul")
        self.assertEqual(result["signed_build_provenance"], "INDETERMINATE")
        self.assertEqual(result["scientific_verdict"], "INDETERMINATE")
        self.assertEqual(result["routing"], "REVIEW_SIGNATURE_OR_IDENTITY")

    def test_signature_without_execution_log_requires_more_evidence(self):
        result, calls = self.run_case(pieces=[], records={})
        self.assertEqual(result["signed_build_provenance"], "VERIFIED_BUILD_ONLY")
        self.assertEqual(result["operation_from_untrusted_log"], UNKNOWN)
        self.assertEqual(result["log_read_count"], 0)
        self.assertEqual(result["routing"], "LINK_LOG_OUTPUT_TO_SIGNED_BYTES")

    def test_digest_mismatch_and_missing_field_cannot_upgrade(self):
        for record in (self.record(artifact_sha256="f"*64),
                       self.record(artifact_sha256=None)):
            with self.subTest(record=record):
                result,_=self.run_case(records={"trace": record})
                self.assertEqual(result["log_artifact_digest_agreement"], "UNVERIFIED")
                self.assertEqual(result["routing"], "LINK_LOG_OUTPUT_TO_SIGNED_BYTES")

    def test_name_mismatch_blocks_signature_verifier(self):
        result, calls = self.run_case(output="another.json")
        self.assertEqual(result["routing"], "FIX_OUTPUT_ARTIFACT_NAME_BINDING")
        self.assertEqual(result["signature_verification_attempts"], 0)
        self.assertEqual(len(calls), 0)

    def test_budget_zero_is_not_science_positive(self):
        result, calls = self.run_case(budget=0)
        self.assertEqual(result["operation_from_untrusted_log"], UNKNOWN)
        self.assertEqual(result["scientific_verdict"], "INDETERMINATE")
        self.assertEqual(result["log_read_count"], 0)

    def test_missing_artifact_fail_closed(self):
        self.artifact.unlink()
        result, calls = self.run_case()
        self.assertEqual(result["routing"], "LOCATE_ARTIFACT_BYTES")
        self.assertEqual(result["signature_verification_attempts"], 0)

    def test_conflicting_execution_logs_abstain(self):
        pieces = self.pieces + [Piece("second","execution","job1","result.json")]
        data={"trace":self.record(),"second":self.record(operation="copie")}
        result,_=self.run_case(records=data,pieces=pieces)
        self.assertEqual(result["operation_from_untrusted_log"], UNKNOWN)
        self.assertEqual(result["log_artifact_digest_agreement"], "UNVERIFIED")
        self.assertEqual(result["log_read_count"], 2)

    def test_unread_candidates_make_selector_abstain(self):
        pieces = self.pieces + [Piece("second","execution","job1","result.json")]
        result,_=self.run_case(pieces=pieces,budget=1)
        self.assertEqual(result["operation_from_untrusted_log"], UNKNOWN)
        self.assertEqual(result["log_read_count"],1)

    def test_untrusted_log_does_not_become_certification_with_bad_flag(self):
        result,_=self.run_case(records={"trace":self.record(complete=False)})
        self.assertEqual(result["operation_from_untrusted_log"], UNKNOWN)
        self.assertEqual(result["scientific_verdict"], "INDETERMINATE")


if __name__ == "__main__":
    unittest.main()
