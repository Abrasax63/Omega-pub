"""Reconcile archived and direct uploads against a same-run inventory."""
import hashlib
import json
from pathlib import Path
import re
from time import perf_counter

STAMP = r"^\S+Z "
GROUP = re.compile(STAMP + r"##\[group\]Run (.+)")
PATH = re.compile(STAMP + r"  path: (.+)")
DIRECT = re.compile(STAMP + r"  archive: false")
DIGEST = re.compile(STAMP + r"SHA256 digest of uploaded artifact(?: zip)? is ([0-9a-f]{64})")
RECEIPT = re.compile(STAMP + r"Artifact (.+) has been successfully uploaded!"
                     r" Final size is \d+ bytes\. Artifact ID is (\d+)")


def extract(log, expected_path):
    upload, path, direct, digest = False, None, False, None
    found = []
    for line in log.splitlines():
        group = GROUP.fullmatch(line)
        if group:
            upload = group[1].startswith("actions/upload-artifact@")
            path, direct, digest = None, False, None
        if not upload:
            continue
        if match := PATH.fullmatch(line):
            path = match[1].replace("\\", "/")
        elif DIRECT.fullmatch(line):
            direct = True
        elif match := DIGEST.fullmatch(line):
            digest = match[1]
        elif match := RECEIPT.fullmatch(line):
            if path == expected_path:
                found.append((match[1], int(match[2]), digest, direct))
            upload = False
    return found[0] if len(found) == 1 else None


def match_record(receipt, inventory, direct):
    if receipt is None or receipt[2] is None:
        return None
    name, identifier, digest, raw_direct = receipt
    if direct and not raw_direct:
        return None
    matches = [a for a in inventory if a["id"] == identifier]
    if len(matches) != 1 or matches[0]["digest"] != "sha256:" + digest:
        return None
    actual_name = matches[0]["name"]
    return actual_name if direct or actual_name == name else None


def main():
    started = perf_counter()
    raw_inventory = Path("cjk-inventory.json").read_bytes()
    inventory = json.loads(raw_inventory)
    assert inventory["total_count"] == len(inventory["artifacts"])
    records, controls = [], 0
    for case in json.loads(Path("cjk-cases.json").read_bytes()):
        raw = Path(str(case["job"]) + ".log").read_bytes()
        receipt = extract(raw.decode(), case["path"])
        fixed = match_record(receipt, inventory["artifacts"], False)
        candidate = match_record(receipt, inventory["artifacts"], case["direct"])
        if receipt and receipt[2]:
            _, ident, digest, _ = receipt
            bad_id = [dict(id=-1, name=case["name"], digest="sha256:" + digest)]
            bad_digest = [dict(id=ident, name=case["name"], digest="sha256:" + "0" * 64)]
            assert match_record(receipt, bad_id, case["direct"]) is None
            assert match_record(receipt, bad_digest, case["direct"]) is None
            controls += 2
        records.append(dict(case=case, receipt=receipt, reference=fixed, candidate=candidate,
                            sha256=hashlib.sha256(raw).hexdigest(),
                            cp_av_markers=raw.count(b"cp -av")))
    print(json.dumps(dict(cases=records, contradictory_controls=controls,
                          inventory_sha256=hashlib.sha256(raw_inventory).hexdigest(),
                          seconds=round(perf_counter()-started, 5)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
