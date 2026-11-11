"""Read-only planner adapter for version-scoped evidence dependencies.

This module does NOT fetch Git, hash source contents, authenticate an author,
certify mathematical truth, or update any persistent scientific memory.
It only identifies *potentially affected* claims from a caller-declared diff.
A malicious or incomplete manifest can lead to missed effects; consequently
unaffected claims are NOT certified as current by this adapter.

The actual Git history experiment verifies source metadata separately via
Git tree/diff consistency and SHA-256 content hashes.
"""
from __future__ import annotations

import re
from typing import Any

MAX_CLAIMS = 256
MAX_CHANGED_PATHS = 256
MAX_DEPENDENCIES_PER_CLAIM = 16
MAX_PATH_CHARS = 512
SHA1_HEX = re.compile(r"^[a-f0-9]{40}$")


class VersionedEvidenceInputError(ValueError):
    pass


def _fields(obj: Any, required: set[str], label: str):
    if not isinstance(obj, dict) or set(obj)!=required:
        raise VersionedEvidenceInputError(
            f"{label} must contain exactly {sorted(required)}")
    return obj


def _path(text: Any, label: str):
    if not isinstance(text,str) or not text or len(text)>MAX_PATH_CHARS:
        raise VersionedEvidenceInputError(f"{label}: invalid path length or type")
    if (text.startswith("/") or "\" in text or
        any(part in ("", ".", "..") for part in text.split("/")) or
        any(ord(ch)<32 or ord(ch)==127 for ch in text)):
        raise VersionedEvidenceInputError(f"{label}: unsafe or noncanonical path")
    return text


def _sha(obj, label):
    if not isinstance(obj,str) or not SHA1_HEX.fullmatch(obj):
        raise VersionedEvidenceInputError(f"{label} must be a lowercase 40-digit Git SHA")
    return obj


def audit_reported_source_change(spec: Any):
    """Return advisory potential impacts, never scientific certification."""
    data=_fields(spec,{
        "previous_commit","target_commit","changed_paths",
        "claims","declared_diff_complete",
    },"source_revision_audit")
    previous=_sha(data["previous_commit"],"previous_commit")
    target=_sha(data["target_commit"],"target_commit")
    if type(data["declared_diff_complete"]) is not bool:
        raise VersionedEvidenceInputError("declared_diff_complete must be boolean")
    paths=data["changed_paths"]
    claims=data["claims"]
    if (not isinstance(paths,list) or len(paths)>MAX_CHANGED_PATHS or
        not isinstance(claims,list) or not claims or len(claims)>MAX_CLAIMS):
        raise VersionedEvidenceInputError("invalid changed_paths or claims length")
    normalized=[_path(p,"changed_paths") for p in paths]
    if len(set(normalized))!=len(normalized):
        raise VersionedEvidenceInputError("duplicate changed path")
    if previous==target and normalized:
        raise VersionedEvidenceInputError("same commit cannot have changed paths")
    changed=set(normalized)
    affected=[];unaffected=[];seen=set()
    for i,c in enumerate(claims):
        c=_fields(c,{"id","dependencies"},f"claims[{i}]")
        cid=c["id"]
        if (not isinstance(cid,str) or not cid or len(cid)>128 or
            any(ord(ch)<32 or ord(ch)==127 for ch in cid) or cid in seen):
            raise VersionedEvidenceInputError("invalid or duplicate claim id")
        seen.add(cid)
        deps=c["dependencies"]
        if (not isinstance(deps,list) or not deps or
            len(deps)>MAX_DEPENDENCIES_PER_CLAIM):
            raise VersionedEvidenceInputError("invalid claim dependencies")
        clean=[_path(p,f"claims[{i}].dependencies") for p in deps]
        if len(set(clean))!=len(clean):
            raise VersionedEvidenceInputError("duplicate claim dependency")
        (affected if changed.intersection(clean) else unaffected).append(cid)
    return {
        "mode":"read_only_advisory_opt_in",
        "previous_commit_declared":previous,
        "target_commit_declared":target,
        "metadata_completeness_declared":data["declared_diff_complete"],
        "changed_paths_reported":len(changed),
        "claim_ids_needing_revalidation":sorted(affected),
        "claim_ids_without_reported_change":sorted(unaffected),
        "source_metadata_authentication_performed":False,
        "source_content_verifications_performed":0,
        "historical_certificates_modified":False,
        "durable_memory_writes_performed":0,
        "scientific_certificate_issued":False,
        "unaffected_claims_certified_as_current":False,
        "limitation":(
            "Only a path dependency index over caller-supplied metadata. "
            "No source fetch, author attestation, semantic verification, "
            "or check that the claimed changed-path list is exhaustive."),
    }
