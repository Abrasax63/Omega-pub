"""Experimental append-only records and keyed independent-review attestations.

Not integrated with Omega scheduler. The trusted reviewer must keep its HMAC
key outside the record store and outside this repository.
"""
import hashlib
import hmac
import json
from pathlib import Path
from tools.repro_fingerprint import fingerprint, reusable


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def record_run(directory, manifest, result, validator):
    """Write a new pending record, never overwrite existing evidence."""
    digest = fingerprint(manifest)
    if not isinstance(validator, str) or not validator:
        raise ValueError("validator must identify an independent process")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    existing = list(directory.glob("*.json"))
    sequence = max((int(p.stem) for p in existing if p.stem.isdigit()), default=0) + 1
    path = directory / f"{sequence:08d}.json"
    payload = {"fingerprint": digest, "manifest": manifest,
               "result": result, "validator": validator,
               "validation_status": "PENDING_INDEPENDENT_REVIEW"}
    with path.open("x", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return path


def sign_review(record, reviewer_id, key):
    """Trusted reviewer only; calling this does not perform scientific review."""
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("review key must contain at least 32 bytes")
    if not isinstance(reviewer_id, str) or not reviewer_id:
        raise ValueError("reviewer_id required")
    if record.get("validation_status") != "PENDING_INDEPENDENT_REVIEW":
        raise ValueError("only pending records may be reviewed")
    if fingerprint(record["manifest"]) != record["fingerprint"]:
        raise ValueError("record fingerprint mismatch")
    claim = {"schema_version": 1, "reviewer_id": reviewer_id,
             "record_digest": _digest(record), "decision": "ACCEPTED"}
    signature = hmac.new(key, _canonical(claim), hashlib.sha256).hexdigest()
    return {"claim": claim, "signature": signature}


def find_reusable(directory, current_manifest, attestations=None, trusted_keys=None):
    """Fail closed unless a valid keyed attestation matches the full record."""
    attestations = attestations or {}
    trusted_keys = trusted_keys or {}
    for path in sorted(Path(directory).glob("*.json"), reverse=True):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("validation_status") != "PENDING_INDEPENDENT_REVIEW":
                continue
            if not reusable(record["manifest"], record["fingerprint"], current_manifest):
                continue
            attestation = attestations.get(path.name)
            if not isinstance(attestation, dict):
                continue
            claim = attestation["claim"]
            reviewer_id = claim["reviewer_id"]
            key = trusted_keys.get(reviewer_id)
            if not isinstance(key, bytes) or len(key) < 32:
                continue
            if claim != {"schema_version": 1, "reviewer_id": reviewer_id,
                          "record_digest": _digest(record), "decision": "ACCEPTED"}:
                continue
            expected = hmac.new(key, _canonical(claim), hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, attestation["signature"]):
                return record
        except (ValueError, TypeError, KeyError, OSError, OverflowError):
            continue
    return None
