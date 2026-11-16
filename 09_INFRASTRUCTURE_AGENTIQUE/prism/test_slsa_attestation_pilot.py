"""Synthetic unit tests of verifier/CLI trust boundary, NOT real signatures."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from slsa_attestation_pilot import (
    PREDICATE, STATEMENT, describe_verified_entry, verify_artifact,
)

REPO = "Abrasax63/Omega-pub"
REPO_ID = "1309584710"
WORKFLOW = REPO + "/.github/workflows/attest.yml"
COMMIT = "a" * 40


class Stub:
    def __init__(self, code=0, stdout="[]"):
        self.returncode = code
        self.stdout = stdout


class SlsaAttestationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.artifact = root / "artifact.bin"
        self.artifact.write_bytes(b"synthetic artifact")
        self.bundle = root / "fake-bundle.jsonl"
        self.bundle.write_text("NOT_A_SIGNATURE")
        self.trusted_root = root / "fake-trusted-root.jsonl"
        self.trusted_root.write_text("NOT_A_TRUST_ROOT")
        self.digest = sha256(self.artifact.read_bytes()).hexdigest()

    def entry(self):
        return {
            "verificationResult": {
                "signature": {"certificate": {"sourceRepositoryIdentifier": REPO_ID}},
                "verifiedTimestamps": [{"source": "mock"}],
                "statement": {
                    "_type": STATEMENT, "predicateType": PREDICATE,
                    "subject": [{"name": "artifact.bin", "digest": {"sha256": self.digest}}],
                    "predicate": {
                        "buildDefinition": {
                            "buildType": "https://example.invalid/test/v1",
                            "externalParameters": {},
                            "resolvedDependencies": [],
                        },
                        "runDetails": {"builder": {"id": "https://example.invalid/builder"},
                                       "metadata": {"invocationId": "UNTRUSTED"}}
                    },
                },
            }
        }

    def verify(self, executor=None, **changes):
        opts = {"repository": REPO, "repository_id": REPO_ID,
                "signer_workflow": WORKFLOW, "source_commit": COMMIT}
        opts.update(changes)
        return verify_artifact(self.artifact, self.bundle, self.trusted_root,
                               opts["repository"], opts["repository_id"],
                               opts["signer_workflow"], opts["source_commit"],
                               executor=executor)

    def mock_success(self, entry=None):
        payload = json.dumps([self.entry() if entry is None else entry])
        return lambda argv, **kwargs: Stub(stdout=payload)

    def test_mock_success_checks_complete_policy_not_real_crypto(self):
        result = self.verify(self.mock_success())
        self.assertTrue(result["signature_verified"])
        self.assertEqual(result["status"], "VERIFIED_BUILD_PROVENANCE_ONLY")
        self.assertEqual(result["scientific_status"], "INDETERMINATE")
        self.assertEqual(result["evidence"][0]["scientific_independence"], "NOT_ESTABLISHED")
        # Mock executor is not a crypto proof, even though policy function trusts success.

    def test_gh_is_required_in_real_mode(self):
        with patch("slsa_attestation_pilot.shutil.which", return_value=None):
            result = self.verify()
        self.assertFalse(result["signature_verified"])
        self.assertEqual(result["reason"], "GH_CLI_NOT_INSTALLED")

    def test_gh_nonzero_never_accepts_apparently_valid_json(self):
        result = self.verify(lambda argv, **kw: Stub(1, json.dumps([self.entry()])))
        self.assertFalse(result["signature_verified"])
        self.assertEqual(result["reason"], "GH_VERIFICATION_FAILED")

    def test_wrong_certificate_repository_id(self):
        bad = self.entry()
        bad["verificationResult"]["signature"]["certificate"]["sourceRepositoryIdentifier"] = "1"
        result = self.verify(self.mock_success(bad))
        self.assertEqual(result["reason"], "SIGNED_STATEMENT_POLICY_MISMATCH")

    def test_missing_certificate_cannot_pass(self):
        bad = self.entry()
        del bad["verificationResult"]["signature"]["certificate"]
        self.assertIsNone(describe_verified_entry(bad, self.digest, REPO_ID))
        self.assertFalse(self.verify(self.mock_success(bad))["signature_verified"])

    def test_edited_artifact_fails_subject_digest(self):
        old_entry = self.entry()
        self.artifact.write_bytes(b"tampered")
        result = self.verify(self.mock_success(old_entry))
        self.assertEqual(result["reason"], "SIGNED_STATEMENT_POLICY_MISMATCH")

    def test_bad_statement_type(self):
        bad = self.entry()
        bad["verificationResult"]["statement"]["_type"] = "not-in-toto"
        self.assertFalse(self.verify(self.mock_success(bad))["signature_verified"])

    def test_bad_predicate_type(self):
        bad = self.entry()
        bad["verificationResult"]["statement"]["predicateType"] = "https://example.org/wrong"
        self.assertFalse(self.verify(self.mock_success(bad))["signature_verified"])

    def test_bad_or_missing_slsa_fields(self):
        mutations = [
            ("buildDefinition", "externalParameters", []),
            ("buildDefinition", "buildType", ""),
            ("buildDefinition", "resolvedDependencies", "malformed"),
        ]
        for section, field, value in mutations:
            with self.subTest(field=field):
                bad = self.entry()
                bad["verificationResult"]["statement"]["predicate"][section][field] = value
                self.assertFalse(self.verify(self.mock_success(bad))["signature_verified"])
        bad = self.entry()
        bad["verificationResult"]["statement"]["predicate"]["runDetails"]["builder"]["id"] = ""
        self.assertFalse(self.verify(self.mock_success(bad))["signature_verified"])

    def test_missing_dependencies_does_not_claim_absence(self):
        entry = self.entry()
        del entry["verificationResult"]["statement"]["predicate"]["buildDefinition"]["resolvedDependencies"]
        result = self.verify(self.mock_success(entry))
        self.assertTrue(result["signature_verified"])
        self.assertIsNone(result["evidence"][0]["listed_dependency_count"])

    def test_trusted_root_is_mandatory(self):
        self.trusted_root.unlink()
        result = self.verify(self.mock_success())
        self.assertEqual(result["reason"], "MISSING_LOCAL_ARTIFACT_BUNDLE_OR_ROOT")

    def test_pinned_repository_workflow_and_commit_required(self):
        for kwargs in [{"repository_id": "no"},
                       {"repository": "another/repo"},
                       {"signer_workflow": "other/.github/workflows/attest.yml"},
                       {"source_commit": "not-a-commit"}]:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.verify(self.mock_success(), **kwargs)["reason"],
                                 "INVALID_PINNED_POLICY")

    def test_deny_empty_bogus_cli_json(self):
        for text in ["[]", "null", "{}", "not json", ""]:
            with self.subTest(output=text):
                result = self.verify(lambda argv, **kw: Stub(stdout=text))
                self.assertFalse(result["signature_verified"])

    def test_timeout_denied(self):
        def timeout(argv, **kwargs):
            raise subprocess.TimeoutExpired("gh", 60)
        self.assertEqual(self.verify(timeout)["reason"], "GH_VERIFIER_UNAVAILABLE_OR_TIMEOUT")

    def test_cli_exact_pins_and_no_shell(self):
        commands = []
        def capture(argv, **kwargs):
            commands.append((argv, kwargs))
            return Stub(stdout=json.dumps([self.entry()]))
        self.verify(capture)
        argv, kwargs = commands[0]
        self.assertIn("--bundle", argv)
        self.assertIn("--custom-trusted-root", argv)
        self.assertEqual(argv[argv.index("--repo") + 1], REPO)
        self.assertEqual(argv[argv.index("--signer-workflow") + 1], WORKFLOW)
        self.assertEqual(argv[argv.index("--source-digest") + 1], COMMIT)
        self.assertNotIn("shell", kwargs)
        self.assertFalse(kwargs["check"])

    def test_mixed_verified_output_requires_at_least_one_matching(self):
        wrong = copy.deepcopy(self.entry())
        wrong["verificationResult"]["statement"]["subject"][0]["digest"]["sha256"] = "0"*64
        result = self.verify(lambda argv, **kwargs: Stub(
            stdout=json.dumps([wrong, self.entry()])))
        self.assertEqual(result["verified_statement_count"], 1)


    def test_slsa_git_commit_dep_is_recorded_but_not_certified(self):
        entry = self.entry()
        entry["verificationResult"]["statement"]["predicate"]["buildDefinition"]["resolvedDependencies"] = [
            {"uri": "git+https://example.invalid/source@refs/tags/v1",
             "digest": {"gitCommit": "c" * 40}}
        ]
        result = self.verify(self.mock_success(entry))
        self.assertTrue(result["signature_verified"])
        evidence = result["evidence"][0]
        self.assertEqual(evidence["reported_dependencies"][0]["git_commit"], "c" * 40)
        self.assertIsNone(evidence["reported_dependencies"][0]["sha256"])
        self.assertIn("SIGNER_CLAIM", evidence["dependency_trust"])
        self.assertEqual(evidence["scientific_independence"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
