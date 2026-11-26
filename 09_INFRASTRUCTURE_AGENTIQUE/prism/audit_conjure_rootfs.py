"""Development-only diagnostic for the archived Conjure rootfs witness."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import tarfile
from time import perf_counter
import zipfile

from provenance_xtrace import extract_buildkit_copy, fixed_verdict

TARGET = "/opt/conjure"
INSTRUCTION = f"COPY --from=builder {TARGET} {TARGET}"
ARTIFACT_HASH = "d773314e5f84a43d4910b0d0e6ca0886f6894bf359b98e8b0f579beb3ddb583a"


def trace_present(log, dockerfile, members):
    if INSTRUCTION not in dockerfile.splitlines() or not members:
        return False
    lines = [line.split(" ", 1)[1] for line in log.splitlines()]
    step = re.fullmatch(r"(#\d+) \[stage-1 1/1\] " + re.escape(INSTRUCTION), lines[0])
    return bool(step and len(lines) == 2
                and re.fullmatch(step[1] + r" DONE \d+(?:\.\d+)?s", lines[1]))


def main():
    start = perf_counter()
    archive = Path("conjure-dev.zip").read_bytes()
    assert sha256(archive).hexdigest() == ARTIFACT_HASH
    with zipfile.ZipFile(BytesIO(archive)) as outer:
        payload = outer.read("solver-wmaxcdcl-arm64.tar.gz")
    with tarfile.open(fileobj=BytesIO(payload), mode="r:gz") as inner:
        members = sorted(member.name for member in inner if member.isfile()
                         and member.name.removeprefix("./").startswith("opt/conjure/"))
    log = Path("conjure-excerpt.log").read_text()
    dockerfile = Path("Dockerfile.wmaxcdcl").read_text()
    rows = []
    for label, specimen in [("original", log), ("cached", re.sub(r"DONE \d+(?:\.\d+)?s", "CACHED", log))]:
        rows.append(dict(case=label, fixed=fixed_verdict(extract_buildkit_copy(specimen, TARGET)),
                         trace_present=trace_present(specimen, dockerfile, members)))
    assert [row["trace_present"] for row in rows] == [True, False]
    print(json.dumps(dict(rows=rows, regular_files=len(members), source_stage_bytes=None,
                          artifact_sha256=ARTIFACT_HASH, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
