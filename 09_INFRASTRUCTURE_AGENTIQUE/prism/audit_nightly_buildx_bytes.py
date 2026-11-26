"""Check buildx source and archive digests without executing the downloaded build."""
from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile


def digest(data):
    return sha256(data).hexdigest()


def same_destination(source, observed):
    if observed is None:
        return None
    return observed == source


def main():
    inventory = json.loads(Path("inventory.json").read_text())
    upload = Path("upload.log").read_text()
    install = Path("install.log").read_text()
    digest_hex = inventory["digest"].removeprefix("sha256:")
    archive = Path("buildx.zip")
    assert archive.stat().st_size == inventory["size_in_bytes"]
    assert digest(archive.read_bytes()) == digest_hex
    assert f"Artifact buildx successfully finalized. Artifact ID {inventory['id']}" in upload
    assert f"uploaded artifact is {digest_hex}" in upload
    assert f" - buildx (ID: {inventory['id']}," in install
    assert f"downloaded artifact is {digest_hex}" in install
    with zipfile.ZipFile(archive) as items:
        assert sorted(items.namelist()) == ["buildx", "provenance.json"]
        assert items.getinfo("buildx").file_size <= 80_000_000
        binary = items.read("buildx")
        report = json.loads(items.read("provenance.json"))
    binary_hash = digest(binary)
    assert report["subject"] == [{"name": "buildx", "digest": {"sha256": binary_hash}}]
    assert "install -m 0755" in install and "github.com/docker/buildx v" in install
    observed = re.findall(r"(?m)\b([a-f0-9]{64})  (?:[^\n ]*/)?docker-buildx$", install)
    decision = same_destination(binary_hash, observed[0] if len(observed) == 1 else None)
    assert same_destination(binary_hash, binary_hash) is True
    assert same_destination(binary_hash, digest(binary[:-1] + bytes([binary[-1] ^ 1]))) is False
    assert same_destination(binary_hash, None) is None
    print(json.dumps(dict(archive_sha256=digest_hex, source_sha256=binary_hash,
                          binary_size=len(binary), destination_exact=decision,
                          matched_receipts=2, controls_passed=3),indent=2))


if __name__ == "__main__":
    main()
