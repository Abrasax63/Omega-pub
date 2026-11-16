"""Minimal read-only bridge between Omega evidence selection and SLSA build provenance.

This does NOT authenticate raw execution logs and never upgrades a
copy/recompute observation into scientific certification. Verifier must operate
on the artifact's actual bytes, not on user-supplied verification-result JSON.
"""
from __future__ import annotations

from pathlib import Path

from provenance_selection import select_verdict
from slsa_attestation_pilot import file_sha256, verify_artifact

UNKNOWN = "indéterminé"


def select_with_attested_artifact(
    pieces, read, *, job, output, budget,
    artifact, bundle, trusted_root, repository, repository_id,
    signer_workflow, source_commit, verifier=None,
):
    """Reuse the existing selector unchanged, then independently verify bytes.

    A complete raw-log observation remains a *log statement*, never an
    attested execution. Explicitly bind log output to the artifact filename and
    its SHA-256 before even reporting an exact-byte agreement.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be nonnegative integer")
    observations = []
    def inspect(name):
        observation = read(name)
        observations.append(observation)
        return observation
    selected = select_verdict(pieces, inspect, job=job, output=output, budget=budget)
    result = {
        "operation_from_untrusted_log": selected["verdict"],
        "logs_read": list(selected["pieces_lues"]),
        "log_read_count": len(selected["pieces_lues"]),
        "signature_verification_attempts": 0,
        "signed_build_provenance": "INDETERMINATE",
        "log_artifact_digest_agreement": "UNVERIFIED",
        "scientific_verdict": "INDETERMINATE",
        "scientific_independence": "NOT_ESTABLISHED",
        "routing": "VERIFY_ARTIFACT_SIGNATURE",
        "raw_selector_modified": False,
    }
    artifact = Path(artifact)
    if not output or Path(output).name != artifact.name:
        result["routing"] = "FIX_OUTPUT_ARTIFACT_NAME_BINDING"
        return result
    try:
        digest = file_sha256(artifact)
    except (OSError, ValueError):
        result["routing"] = "LOCATE_ARTIFACT_BYTES"
        return result

    # Important: do NOT accept a serialized report with signature_verified=True.
    # In production this function calls the underlying pinned verifier on bytes.
    check = verifier or verify_artifact
    result["signature_verification_attempts"] = 1
    att = check(artifact, bundle, trusted_root, repository, repository_id,
                signer_workflow, source_commit)
    if (not isinstance(att, dict) or att.get("signature_verified") is not True
            or att.get("status") != "VERIFIED_BUILD_PROVENANCE_ONLY"
            or att.get("artifact_sha256") != digest):
        result["routing"] = "REVIEW_SIGNATURE_OR_IDENTITY"
        return result
    result["signed_build_provenance"] = "VERIFIED_BUILD_ONLY"

    # A correct checksum reported in an untrusted log is at most a concordance,
    # never an authenticated proof that the observed command produced the bytes.
    relevant = [r for r in observations if isinstance(r, dict)
                and r.get("job") == job and r.get("output") == output
                and r.get("complete") is True and r.get("success") is True
                and r.get("operation") in ("copie", "recalcul")]
    if (selected["verdict"] != UNKNOWN and relevant
            and len(relevant) == len(observations)
            and all(r.get("artifact_sha256") == digest for r in relevant)):
        result["log_artifact_digest_agreement"] = "MATCHES_LOG_CLAIM_NOT_ATTESTED"
        result["routing"] = "AUDIT_LOG_SOURCE_AND_INDEPENDENT_REPRODUCTION"
    else:
        result["routing"] = "LINK_LOG_OUTPUT_TO_SIGNED_BYTES"
    return result
