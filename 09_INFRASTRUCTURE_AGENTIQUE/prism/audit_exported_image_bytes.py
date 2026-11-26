"""Inspect a small OCI build record without extracting or executing its members."""
from collections import Counter
from hashlib import sha256
from io import BytesIO
import gzip
import json
from pathlib import Path
import tarfile

LIMIT = 4 * 1024 * 1024
IMAGE = "sha256:fcc44163e80d943ba50d89ccf04f22910ff553268a93ac8e40644f4199211673"


def ident(payload):
    return "sha256:" + sha256(payload).hexdigest()


def image_graph(blobs, root):
    pending = [(root, True)]
    seen = set()
    counts = Counter()
    while pending:
        digest, descriptor = pending.pop()
        if (digest, descriptor) in seen:
            continue
        seen.add((digest, descriptor))
        payload = blobs.get(digest)
        if payload is None:
            counts["missing"] += 1
            continue
        if ident(payload) != digest:
            counts["mismatch"] += 1
            continue
        counts["verified"] += 1
        if not descriptor:
            continue
        node = json.loads(payload)
        if "manifests" in node:
            pending.extend((entry["digest"], True) for entry in node["manifests"])
        elif "config" in node and "layers" in node:
            pending.append((node["config"]["digest"], False))
            pending.extend((entry["digest"], False) for entry in node["layers"])
        else:
            counts["invalid"] += 1
    return dict(present=root in blobs, complete=not any(counts[k] for k in ("missing", "mismatch", "invalid")),
                verified=counts["verified"], missing=counts["missing"],
                mismatch=counts["mismatch"], invalid=counts["invalid"])


def main():
    record = Path("record.zip")
    with gzip.open(record, "rb") as compressed:
        payload = compressed.read(LIMIT + 1)
    assert len(payload) <= LIMIT
    with tarfile.open(fileobj=BytesIO(payload), mode="r:") as archive:
        files = [x for x in archive if x.isfile()]
        assert len({x.name for x in files}) == len(files)
        blobs = {"sha256:" + x.name.removeprefix("blobs/sha256/"): archive.extractfile(x).read()
                 for x in files if x.name.startswith("blobs/sha256/")}
    result = image_graph(blobs, IMAGE)
    data = b"layer placeholder"
    layer = ident(data)
    config = ident(b"{}")
    manifest = json.dumps(dict(config={"digest": config}, layers=[{"digest": layer}])).encode()
    key = ident(manifest)
    sample = {config: b"{}", key: manifest}
    assert not image_graph(sample, key)["complete"]
    assert image_graph(sample | {layer: data}, key)["complete"]
    assert not image_graph(sample | {layer: b"mutated"}, key)["complete"]
    print(json.dumps(dict(image=result, record_blobs=len(blobs), controls_passed=3), indent=2))


if __name__ == "__main__":
    main()
