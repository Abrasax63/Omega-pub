"""Compare signed SLSA build *claims* across two independently verified artifacts.

Only parse outputs produced by slsa_attestation_pilot.py. This cannot itself
validate signatures or turn named dependencies into authenticated artifacts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

UNKNOWN = "INDETERMINATE"


def _evidence(report):
    if not isinstance(report, dict) or report.get("signature_verified") is not True:
        return None
    if report.get("status") != "VERIFIED_BUILD_PROVENANCE_ONLY":
        return None
    items = report.get("evidence")
    if not isinstance(items, list) or not items:
        return None
    evidence = items[0]
    if not isinstance(evidence, dict):
        return None
    if not isinstance(evidence.get("reported_dependencies"), list):
        return None
    return evidence


def compare_reports(left, right):
    """Observational report with explicit trust boundary and two-node graph."""
    base = {
        "status": UNKNOWN,
        "scientific_correctness": "NOT_ESTABLISHED",
        "scientific_independence": "NOT_ESTABLISHED",
        "origin_claim_completeness": "NOT_ESTABLISHED",
        "claim_authentication": "REQUIRES_EXTERNAL_VERIFIER_FOR_EACH_INPUT",
    }
    a, b = _evidence(left), _evidence(right)
    if a is None or b is None:
        return {**base, "reason": "UNVERIFIED_OR_INCOMPLETE_INPUT"}
    repo_ids = [a.get("certificate_repository_id"), b.get("certificate_repository_id")]
    if not all(isinstance(v, str) and v.isdecimal() and int(v) > 0 for v in repo_ids):
        return {**base, "reason": "MISSING_CERTIFIED_REPOSITORY_ID"}
    def normalized(evidence):
        deps = []
        for entry in evidence["reported_dependencies"]:
            if not isinstance(entry, dict):
                continue
            uri = entry.get("uri")
            sha = entry.get("sha256")
            if not isinstance(uri, str) or not uri:
                continue
            if sha is not None and (not isinstance(sha, str) or len(sha) != 64
                                    or any(ch not in "0123456789abcdef" for ch in sha)):
                sha = None
            deps.append((uri, sha))
        return set(deps)
    dep_a, dep_b = normalized(a), normalized(b)
    overlap = sorted(dep_a & dep_b, key=lambda item: (item[0], item[1] or ""))
    conflicting_uri = sorted({u for u, h in dep_a if h is not None}
                             & {u for u, h in dep_b if h is not None}
                             - {u for u, h in overlap})
    names = ["artifact_A", "artifact_B"]
    return {
        **base,
        "status": "SIGNED_PROVENANCE_CLAIMS_COMPARED",
        "distinct_certified_repositories": repo_ids[0] != repo_ids[1],
        "subjects": [
            {"id": names[i], "certificate_repository_id": repo_ids[i],
             "artifact_sha256": v.get("subject_sha256"),
             "claimed_build_type": v.get("claimed_build_type"),
             "claimed_builder_id": v.get("claimed_builder_id"),
             "claimed_invocation_id": v.get("claimed_invocation_id"),
             "reported_dependency_count": v.get("listed_dependency_count"),
             "dependencies_truncated": v.get("dependencies_truncated")}
            for i, v in enumerate((a, b))
        ],
        "reported_dependency_edges": len(dep_a) + len(dep_b),
        "shared_claimed_dependencies": [{"uri": uri, "sha256": sha}
                                        for uri, sha in overlap],
        "shared_claimed_dependency_count": len(overlap),
        "same_uri_without_matching_digest": conflicting_uri,
        "unresolved_dependency_provenance": True,
        "interpretation": (
            "Repository identities and artifact digests were validated by the external "
            "verifier before input reports were emitted. Dependency URI/digest edges are "
            "signed, signer-controlled claims only; no dependency origin has been "
            "independently verified here. No scientific replication conclusion."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    reports = [json.loads(p.read_text(encoding="utf-8")) for p in (args.first, args.second)]
    result = compare_reports(*reports)
    message = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(message, encoding="utf-8")
    print(message)


if __name__ == "__main__":
    main()
