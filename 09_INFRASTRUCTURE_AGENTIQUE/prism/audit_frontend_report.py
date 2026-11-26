"""Join public GitHub Actions report uploads to the run artifact inventory."""
import hashlib
import json
from pathlib import Path
import re
import sys
from time import perf_counter

STAMP = r"^\S+Z "
UPLOAD = re.compile(STAMP + r"Uploading artifact: (test-reports-[\w.-]+)\.zip$")
DIGEST = re.compile(STAMP + r"SHA256 digest of uploaded artifact is ([a-f0-9]{64})$")
TERMINAL = re.compile(
    STAMP + r"Artifact (test-reports-[\w.-]+) has been successfully uploaded!"
    r" Final size is \d+ bytes\. Artifact ID is (\d+)$"
)


def extract(log):
    report = None
    fingerprints = []
    uploads = []
    for line in log.splitlines():
        start = UPLOAD.fullmatch(line)
        if start:
            report, fingerprints = start[1], []
        elif report is not None:
            fingerprint = DIGEST.fullmatch(line)
            if fingerprint:
                fingerprints.append(fingerprint[1])
            terminal = TERMINAL.fullmatch(line)
            if terminal:
                uploads.append(
                    (int(terminal[2]), report, "sha256:" + fingerprints[0])
                    if terminal[1] == report and len(fingerprints) == 1 else None
                )
                report = None
    return uploads[0] if len(uploads) == 1 else None


def joined(record, inventory):
    if record is None:
        return "abstention"
    identifier, name, digest = record
    matches = [a for a in inventory if a["id"] == identifier]
    if len(matches) != 1:
        return "abstention"
    return "confirmed" if (matches[0]["name"], matches[0]["digest"]) == (name, digest) else "rejected"


def main():
    inventory_path, jobs_path, *logs = map(Path, sys.argv[1:])
    inventory_bytes = inventory_path.read_bytes()
    inventory = json.loads(inventory_bytes)
    jobs = json.loads(jobs_path.read_bytes())
    cases = []
    started = perf_counter()
    for log, job in zip(logs, jobs, strict=True):
        raw = log.read_bytes()
        content = raw.decode("utf-8")
        record = extract(content)
        cases.append({
            "job_id": job["id"],
            "log_sha256": hashlib.sha256(raw).hexdigest(),
            "record": record,
            "comparator": "confirmed" if job["upload_step"] == "success" else "abstention",
            "candidate": joined(record, inventory),
            "cp_av_markers": content.count("cp -av"),
        })
    record = cases[1]["record"]
    if record is not None:
        adverse = [
            {**entry, "digest": "sha256:" + "0" * 64}
            if entry["id"] == record[0] else entry
            for entry in inventory
        ]
    else:
        adverse = inventory
    print(json.dumps({
        "cases": cases,
        "adverse": {"comparator": cases[1]["comparator"], "candidate": joined(record, adverse)},
        "inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "measured_seconds": round(perf_counter() - started, 5),
    }, indent=2))


if __name__ == "__main__":
    main()
