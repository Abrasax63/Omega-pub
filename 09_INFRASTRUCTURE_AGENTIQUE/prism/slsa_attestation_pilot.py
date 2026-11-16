"""Offline SLSA pilot: gh verifies signatures, Omega checks supplemental policy.

Do not infer scientific correctness or independent reproduction from build attestations.
All cryptographic and transparency verification is DELEGATED to gh attestation verify.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

STATEMENT = "https://in-toto.io/Statement/v1"
PREDICATE = "https://slsa.dev/provenance/v1"
GITHUB_OIDC = "https://token.actions.githubusercontent.com"
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMIT = re.compile(r"^[a-f0-9]{40}$")
MAX_OUTPUT = 2_000_000


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe_verified_entry(entry, digest, repository_id):
    """Policy ONLY. Does not prove signatures from a bare JSON object."""
    if not isinstance(entry, dict):
        return None
    verified = entry.get("verificationResult")
    if not isinstance(verified, dict):
        return None
    signature = verified.get("signature")
    certificate = signature.get("certificate") if isinstance(signature, dict) else None
    if not isinstance(certificate, dict):
        return None
    if str(certificate.get("sourceRepositoryIdentifier", "")) != str(repository_id):
        return None
    statement = verified.get("statement")
    if not isinstance(statement, dict):
        return None
    if statement.get("_type") != STATEMENT or statement.get("predicateType") != PREDICATE:
        return None
    subjects = statement.get("subject")
    if not isinstance(subjects, list) or not any(
        isinstance(s, dict) and isinstance(s.get("digest"), dict)
        and s["digest"].get("sha256") == digest for s in subjects
    ):
        return None
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        return None
    definition, details = predicate.get("buildDefinition"), predicate.get("runDetails")
    if not isinstance(definition, dict) or not isinstance(details, dict):
        return None
    builder = details.get("builder")
    if (not isinstance(definition.get("buildType"), str) or not definition["buildType"]
            or not isinstance(definition.get("externalParameters"), dict)
            or not isinstance(builder, dict) or not isinstance(builder.get("id"), str)
            or not builder["id"]):
        return None
    dependencies = definition.get("resolvedDependencies")
    if dependencies is not None and not isinstance(dependencies, list):
        return None
    # The list below is *reported by the signer*, not independently reconstructed.
    # Bound size and strings before echoing into a machine-readable report.
    reported_deps = []
    if isinstance(dependencies, list):
        for entry in dependencies[:100]:
            if not isinstance(entry, dict):
                continue
            uri = entry.get("uri")
            digest_map = entry.get("digest")
            if not isinstance(uri, str) or len(uri) > 1024:
                continue
            sha256_value = digest_map.get("sha256") if isinstance(digest_map, dict) else None
            if sha256_value is not None and (not isinstance(sha256_value, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", sha256_value)):
                sha256_value = None
            reported_deps.append({"uri": uri, "sha256": sha256_value})
    metadata = details.get("metadata")
    invocation = metadata.get("invocationId") if isinstance(metadata, dict) else None
    return {
        "subject_sha256": digest,
        "certificate_repository_id": str(repository_id),
        "claimed_builder_id": builder["id"],
        "claimed_build_type": definition["buildType"],
        "claimed_invocation_id": invocation if isinstance(invocation, str) else None,
        "listed_dependency_count": len(dependencies) if isinstance(dependencies, list) else None,
        "reported_dependencies": reported_deps,
        "dependencies_truncated": isinstance(dependencies, list) and len(dependencies) > 100,
        "dependency_trust": "SIGNED_STATEMENT_SIGNER_CLAIM_NOT_INDEPENDENTLY_RECONSTRUCTED",
        "scientific_independence": "NOT_ESTABLISHED",
        "scientific_correctness": "NOT_ESTABLISHED",
    }


def verify_artifact(artifact, bundle, trusted_root, repository, repository_id,
                    signer_workflow, source_commit, *, executor=None):
    """Verify local artifact with an external pinned CLI verifier and root.

    A supplied executor is ONLY a test seam. No arbitrary source is executed.
    """
    result = {"status": "INDETERMINATE", "signature_verified": False,
              "scientific_status": "INDETERMINATE",
              "origin_independence": "NOT_ESTABLISHED", "repository": repository}
    if (not isinstance(repository, str) or not REPO.fullmatch(repository)
            or not str(repository_id).isdigit() or int(repository_id) < 1
            or not isinstance(signer_workflow, str)
            or not signer_workflow.startswith(repository + "/.github/workflows/")
            or not signer_workflow.endswith((".yml", ".yaml"))
            or not isinstance(source_commit, str) or not COMMIT.fullmatch(source_commit)):
        return {**result, "reason": "INVALID_PINNED_POLICY"}
    paths = (Path(artifact), Path(bundle), Path(trusted_root))
    if not all(path.is_file() for path in paths):
        return {**result, "reason": "MISSING_LOCAL_ARTIFACT_BUNDLE_OR_ROOT"}
    artifact_digest = file_sha256(paths[0])
    result["artifact_sha256"] = artifact_digest
    binary = shutil.which("gh") if executor is None else "gh"
    if binary is None:
        return {**result, "reason": "GH_CLI_NOT_INSTALLED"}
    argv = [binary, "attestation", "verify", str(paths[0]),
            "--bundle", str(paths[1]),
            "--custom-trusted-root", str(paths[2]),
            "--repo", repository,
            "--signer-workflow", signer_workflow,
            "--source-digest", source_commit,
            "--cert-oidc-issuer", GITHUB_OIDC,
            "--predicate-type", PREDICATE,
            "--format", "json"]
    call = executor or subprocess.run
    try:
        completed = call(argv, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return {**result, "reason": "GH_VERIFIER_UNAVAILABLE_OR_TIMEOUT"}
    if completed.returncode != 0:
        return {**result, "reason": "GH_VERIFICATION_FAILED"}
    if not isinstance(completed.stdout, str) or len(completed.stdout) > MAX_OUTPUT:
        return {**result, "reason": "INVALID_VERIFIER_OUTPUT"}
    try:
        items = json.loads(completed.stdout)
    except (TypeError, ValueError):
        return {**result, "reason": "INVALID_VERIFIER_OUTPUT"}
    if not isinstance(items, list) or not items:
        return {**result, "reason": "NO_VERIFIED_ATTESTATION"}
    accepted = [x for item in items
                if (x := describe_verified_entry(item, artifact_digest, repository_id)) is not None]
    if not accepted:
        return {**result, "reason": "SIGNED_STATEMENT_POLICY_MISMATCH"}
    return {**result, "status": "VERIFIED_BUILD_PROVENANCE_ONLY",
            "signature_verified": True, "reason": "GH_SIGNATURE_AND_LOCAL_POLICY_PASS",
            "verified_statement_count": len(accepted), "evidence": accepted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--trusted-root", required=True, type=Path)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--signer-workflow", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    output = verify_artifact(args.artifact, args.bundle, args.trusted_root, args.repo,
                             args.repo_id, args.signer_workflow, args.source_commit)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output["signature_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
