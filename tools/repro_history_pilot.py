"""Append-only pilot record store; no connection to Omega's production scheduler."""
import json
from pathlib import Path
from tools.repro_fingerprint import fingerprint, reusable


def record_run(directory, manifest, result, validator):
    """Record every run without overwriting history; validation is external."""
    digest = fingerprint(manifest)
    if not isinstance(validator, str) or not validator:
        raise ValueError("validator must identify an independent validation process")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # Unique event names prevent silent overwrite; no timestamps needed.
    existing = list(directory.glob("*.json"))
    sequence = max((int(p.stem) for p in existing if p.stem.isdigit()), default=0) + 1
    path = directory / f"{sequence:08d}.json"
    payload = {"fingerprint": digest, "manifest": manifest,
               "result": result, "validator": validator,
               "validation_status": "PENDING_INDEPENDENT_REVIEW"}
    # exclusive creation: never replace earlier evidence
    with path.open("x", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return path


def find_reusable(directory, current_manifest):
    """Return only independently ACCEPTED records; never promote pending runs."""
    for path in sorted(Path(directory).glob("*.json"), reverse=True):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if (record.get("validation_status") == "ACCEPTED_INDEPENDENTLY"
                    and reusable(record["manifest"], record["fingerprint"], current_manifest)):
                return record
        except (ValueError, TypeError, KeyError, OSError):
            continue
    return None
