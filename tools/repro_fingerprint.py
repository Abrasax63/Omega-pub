"""Fail-closed fingerprint for reproducible scientific runs (stdlib only)."""
import hashlib
import json

REQUIRED = ("result_id", "code_sha256", "data_sha256", "parameters",
            "dependencies", "execution", "schema_version")


def fingerprint(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    missing = [k for k in REQUIRED if k not in manifest]
    if missing:
        raise ValueError("missing fields: " + ", ".join(missing))
    if set(manifest) != set(REQUIRED):
        raise ValueError("unknown fields: " + ", ".join(sorted(set(manifest) - set(REQUIRED))))
    if manifest["schema_version"] != 1:
        raise ValueError("unsupported schema version")
    if not isinstance(manifest["result_id"], str) or not manifest["result_id"]:
        raise ValueError("invalid result_id")
    for k in ("code_sha256", "data_sha256"):
        v = manifest[k]
        if not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
            raise ValueError("invalid " + k)
    for k in ("parameters", "dependencies", "execution"):
        if not isinstance(manifest[k], dict):
            raise ValueError(k + " must be an object")
    def validate(x):
        if x is None or isinstance(x, (bool, int, str)):
            return
        if isinstance(x, float):
            raise ValueError("floats forbidden: encode with exact strings")
        if isinstance(x, list):
            for item in x: validate(item)
            return
        if isinstance(x, dict) and all(isinstance(k, str) for k in x):
            for item in x.values(): validate(item)
            return
        raise ValueError("unsupported value")
    validate(manifest)
    payload = json.dumps(manifest, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(b"omega-repro-manifest-v1\\0" + payload).hexdigest()


def reusable(previous_manifest, previous_fingerprint, current_manifest):
    """Never reuse on malformed input or missing/mismatched fingerprint."""
    try:
        return (isinstance(previous_fingerprint, str)
                and len(previous_fingerprint) == 64
                and fingerprint(previous_manifest) == previous_fingerprint
                and fingerprint(current_manifest) == previous_fingerprint)
    except (ValueError, TypeError, OverflowError):
        return False
