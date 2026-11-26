"""Reconcile a scoped libuv MinGW Build log with its source and archive."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import re
from time import perf_counter
from zipfile import ZipFile

from provenance_xtrace import extract, fixed_verdict

SOURCE = "test/fixtures/empty_file"
TARGET = "build/usr/" + SOURCE
UNKNOWN = "indéterminé"
COPY = "copie"
LOG_LINE = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
ARROW = re.compile(r"'([^']+)' -> '([^']+)'")
CASES = (
    (45648645238, 139326604089, 15038013841, "4c2b4fb39faee3012e369cab1689562c2932afb330357e3a8ad4b578cab08560"),
    (45626954314, 139249569021, 15029161097, "c68c2071f8160621976b18983ad2dfcc122e63686d7f4d1d45785e0f25650e39"),
    (45624074460, 139239547843, 15026642853, "7e9175c7c0ba2ee8c2d6a1b5c5d9f4c6e36e3798af1abfc532870b4481f0f64e"),
)


def scoped_build(log):
    lines = [LOG_LINE.sub("", line) for line in log.splitlines()]
    starts = [i for i, line in enumerate(lines) if line.startswith("##[group]Run cmake -B build -G Ninja ")]
    if len(starts) != 1:
        return ()
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("##[group]Run ")), len(lines))
    if end == len(lines) or not lines[end].startswith("##[group]Run actions/upload-artifact@"):
        return ()
    block = lines[start + 1:end]
    ends = [i for i, line in enumerate(block) if line == "##[endgroup]"]
    if not ends or "shell: /usr/bin/bash -e {0}" not in block[:ends[0]]:
        return ()
    if not any(line.strip("\x1b[0123456789;m ") == "cp -av test/fixtures build/usr/test" for line in block[:ends[0]]):
        return ()
    return block[ends[0] + 1:]


def candidate(log, corroborated):
    arrows = [m.groups() for line in scoped_build(log) if (m := ARROW.fullmatch(line))]
    return COPY if corroborated and [src for src, dst in arrows if dst == TARGET] == [SOURCE] else UNKNOWN


def fixed_with_same_evidence(lines, corroborated):
    expected = f"'{SOURCE}' -> '{TARGET}'"
    hits = [line for line in lines if line.endswith(f" -> '{TARGET}'")]
    return COPY if corroborated and hits == [expected] else UNKNOWN


def main():
    start = perf_counter()
    report = []
    for i, (run, job, artifact, archive_sha) in enumerate(CASES):
        log_bytes = Path(f"job{i}.log").read_bytes()
        log = log_bytes.decode("utf-8")
        zip_path = Path(f"job{i}.zip")
        assert sha256(zip_path.read_bytes()).hexdigest() == archive_sha
        with ZipFile(zip_path) as archive:
            assert archive.namelist().count(SOURCE) == 1
            data = archive.read(SOURCE)
        git_oid = sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        assert git_oid == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
        expected_arrow = f"'{SOURCE}' -> '{TARGET}'"
        ref = fixed_verdict(extract(log, TARGET))
        proposed = candidate(log, True)
        fixed = fixed_with_same_evidence(scoped_build(log), True)
        adverse = [candidate(log.replace(expected_arrow, expected_arrow + "\n" + expected_arrow), True),
                   candidate(log.replace(expected_arrow, expected_arrow.replace(SOURCE, SOURCE + "2")), True),
                   candidate(log, False)]
        assert proposed == fixed == COPY and adverse == [UNKNOWN] * 3
        report.append(dict(run=run, job=job, artifact=artifact, log_sha256=sha256(log_bytes).hexdigest(),
                           zip_sha256=archive_sha, file_sha256=sha256(data).hexdigest(),
                           reference=ref, candidate=proposed, fixed_same_evidence=fixed, adverse=adverse))
    print(json.dumps(dict(cases=report, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
