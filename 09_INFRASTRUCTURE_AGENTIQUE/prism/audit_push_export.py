"""Inspect BuildKit progress and independent file evidence without executing logs."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import tarfile
from time import perf_counter_ns

PROGRESS = re.compile(r"^#(\d+) (.*)$")
COPY = re.compile(r"\] COPY --from=\S+ ")


def verdict(log, payload=None, subject=None):
    copy = local = False
    copy_steps = set()
    export_steps = set()
    for line in log.splitlines():
        line = re.sub(r"^\d{4}-\d\d-\d\dT\S+Z ", "", line).strip()
        match = PROGRESS.fullmatch(line)
        if match is None:
            continue
        step, event = match.groups()
        if COPY.search(event):
            copy_steps.add(step)
        if event == "exporting to client directory":
            export_steps.add(step)
        if event.startswith("DONE "):
            copy |= step in copy_steps
            local |= step in export_steps
    fixed = "exported" if copy else "unknown"
    if not copy or not local:
        return fixed, "unknown"
    if payload is None or subject is None:
        return fixed, "unknown"
    candidate = "exported" if sha256(payload).hexdigest() == subject else "contradiction"
    return fixed, candidate


def main():
    start = perf_counter_ns()
    header = "#1 [end 1/1] COPY --from=base /a /\n#1 DONE 0.0s\n"
    export = "#2 exporting to client directory\n#2 DONE 0.0s\n"
    payload = b"fixture content"
    digest = sha256(payload).hexdigest()
    assert verdict(header + "#2 exporting to image\n#2 DONE 0.0s\n", payload, digest) == ("exported", "unknown")
    assert verdict(header + export, payload, digest) == ("exported", "exported")
    assert verdict(header + export, b"swapped", digest) == ("exported", "contradiction")
    journal = Path("test.log").read_text()
    with tarfile.open("test.zip", "r:gz") as archive:
        members = archive.getnames()
        assert "oci-layout" in members and "index.json" in members
        verified_blobs = []
        for name in members:
            if re.fullmatch(r"blobs/sha256/[a-f0-9]{64}", name):
                digest = sha256(archive.extractfile(name).read()).hexdigest()
                assert name.rsplit("/", 1)[-1] == digest
                verified_blobs.append(digest)
        index = json.load(archive.extractfile("index.json"))
        record, = index["manifests"]
        manifest = json.load(archive.extractfile("blobs/" + record["digest"].replace(":", "/", 1)))
        layers = manifest["layers"]
        layer_types = [layer["mediaType"] for layer in layers]
        provenance, = [layer for layer in layers if layer["mediaType"] == "application/vnd.in-toto+json"]
        predicate = json.load(archive.extractfile("blobs/" + provenance["digest"].replace(":", "/", 1)))
        assert "subject" not in predicate
        assert not any("rootfs" in t or "image.layer" in t for t in layer_types)
        direct_evidence = any(name.endswith("/clover.xml") for name in members)
    assert not direct_evidence
    print(json.dumps(dict(archive_blobs=len(verified_blobs), layer_types=layer_types,
                          direct_file_member=direct_evidence,
                          external_comparison=verdict(journal),
                          cp_av=len(re.findall(r"\+ cp -av\b", journal)),
                          elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
