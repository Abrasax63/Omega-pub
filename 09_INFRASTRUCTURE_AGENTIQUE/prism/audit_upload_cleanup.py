"""Compare completed uploads with post-cleanup presence in one Actions run."""
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime
from time import perf_counter

STAMP = r"(?P<time>\S+Z) "
UPLOAD = re.compile(STAMP + r"Artifact (?P<name>[\w.-]+) has been successfully uploaded!"
                    r" Final size is \d+ bytes\. Artifact ID is (?P<id>\d+)")
DELETE = re.compile(STAMP + r"Deleted artifact '(?P<name>[\w.-]+)'")
DIGEST = re.compile(STAMP + r"SHA256 digest of uploaded artifact is (?P<digest>[a-f0-9]{64})")


def receipts(data, names):
    matches = []
    pending = None
    for line in data.splitlines():
        fingerprint = DIGEST.fullmatch(line)
        if fingerprint:
            pending = fingerprint["digest"]
        upload = UPLOAD.fullmatch(line)
        if upload:
            if upload["name"] in names:
                matches.append((datetime.fromisoformat(upload["time"]), int(upload["id"]), pending))
            pending = None
    return max(matches) if matches else None


def deletion_times(data, name):
    return [datetime.fromisoformat(m["time"]) for line in data.splitlines()
            if (m := DELETE.fullmatch(line)) and m["name"] == name]


def classify(receipt, deleted, current):
    if receipt is None:
        return "abstention", "abstention"
    time, identifier, digest = receipt
    present = (len(current) == 1 and current[0]["id"] == identifier
               and (digest is None or current[0]["digest"] == "sha256:" + digest))
    prior = "present" if present else "abstention"
    if not any(t > time for t in deleted):
        return prior, prior
    return prior, "abstention" if current else "deleted"


def main():
    start = perf_counter()
    inventory_bytes = Path("inventory.json").read_bytes()
    inventory = json.loads(inventory_bytes)
    assert inventory["total_count"] == len(inventory["artifacts"])
    cases = json.loads(Path("cases.json").read_bytes())
    cleanup = Path("cleanup.log").read_bytes()
    results = []
    for case in cases:
        log = Path(str(case["job"]) + ".log").read_bytes()
        receipt = receipts(log.decode(), case["log_names"])
        name = case["name"]
        current = [a for a in inventory["artifacts"] if a["name"] == name]
        deleted = deletion_times(cleanup.decode(), name)
        comparison, candidate = classify(receipt, deleted, current)
        results.append(dict(job=case["job"], name=name, truth="present" if current else "absent",
                            upload_id=receipt[1] if receipt else None, receipt_digest=receipt[2] if receipt else None,
                            deletion_receipts=len(deleted), fixed="present" if case["step_success"] else "abstention",
                            positive_join=comparison, candidate=candidate,
                            log_sha256=hashlib.sha256(log).hexdigest(), cp_av_markers=log.count(b"cp -av")))
        if receipt and deleted and not current:
            replacement = [dict(id=receipt[1] + 1, digest=None)]
            assert classify(receipt, deleted, replacement)[1] == "abstention"
            error = f"{deleted[0].isoformat().replace('+00:00', 'Z')} Could not delete artifact '{name}': denied"
            assert not deletion_times(error, name)
            assert classify(receipt, deletion_times(error, name), current)[1] == "abstention"
    print(json.dumps(dict(cases=results, cleanup_sha256=hashlib.sha256(cleanup).hexdigest(),
                          inventory_sha256=hashlib.sha256(inventory_bytes).hexdigest(),
                          cleanup_cp_av_markers=cleanup.count(b"cp -av"),
                          seconds=round(perf_counter()-start, 5)), indent=2))


if __name__ == "__main__":
    main()
