"""Join an Actions upload and download receipt with the live inventory."""
from pathlib import Path
import json
import re

NAME = "docs-yaml"
HEX = r"[0-9a-f]{64}"


def receipt(upload, validate):
    ids = re.findall(r"Artifact docs-yaml successfully finalized\. Artifact ID (\d+)", upload)
    hashes = re.findall(r"SHA256 digest of uploaded artifact is (" + HEX + r")", upload)
    expected = re.findall(r" - docs-yaml \(ID: (\d+), Size: \d+, Expected Digest: sha256:(" + HEX + r")\)", validate)
    actual = re.findall(r"SHA256 digest of downloaded artifact is (" + HEX + r")", validate)
    if len(ids) == len(hashes) == len(expected) == len(actual) == 1:
        if expected[0] == (ids[0], hashes[0]) and actual == hashes:
            return int(ids[0]), "sha256:" + hashes[0]
    raise ValueError("RECEIPTS_DISAGREE")


def inventory_match(inventory, result):
    artifacts = inventory["artifacts"]
    if inventory["total_count"] != len(artifacts):
        raise ValueError("INCOMPLETE_INVENTORY")
    return sum(a["name"] == NAME and (a["id"], a["digest"]) == result
               and a["expired"] is False for a in artifacts) == 1


def main():
    upload, validate = (Path(f).read_text() for f in ("upload.log", "validate.log"))
    inventory = json.loads(Path("inventory.json").read_text())
    got = receipt(upload, validate)
    hit = inventory_match(inventory, got)
    spec = dict(id=got[0], digest=got[1], expired=False, name=NAME)
    assert inventory_match(dict(total_count=1, artifacts=[spec]),got)
    assert not inventory_match(dict(total_count=1, artifacts=[dict(spec, id=got[0]+1)]),got)
    print(json.dumps(dict(receipts_agree=True, asset_id=got[0], inventory_count=inventory["total_count"],
                          independent_inventory_match=hit, controls_passed=2, bytes_verified=0),indent=2))


if __name__ == "__main__":
    main()
