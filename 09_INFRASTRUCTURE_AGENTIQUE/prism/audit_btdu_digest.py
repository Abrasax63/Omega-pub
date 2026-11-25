"""Read-only comparison of a scoped digest, checksum sidecar and artifact member."""
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter
from zipfile import ZipFile

from provenance_xtrace import extract, fixed_verdict

NAME = "btdu-static-x86_64"
UNKNOWN = "indéterminé"
PIN = (
    "767b9e371d9ad7a8671ec7009484b3f2494d13f21b8f650ef291f7c742186d72",
    "2d7daae39c6faea82a619c7542a27ba8a28e4b5bc2f2a9a6884ee444e014e56d",
    "f647206166472437bdd2ace03ef1d0c0c87b63774195894d50175865820fc0a1",
)
STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ROW = re.compile(r"([0-9a-f]{64})  " + NAME)


def scopes(log):
    lines = [ANSI.sub("", STAMP.sub("", l)) for l in log.splitlines()]
    needles = (f"##[group]Run nix build .#{NAME} ", f"##[group]Run sha256sum {NAME} ",
               "##[group]Run actions/upload-artifact@")
    matches = [[i for i,l in enumerate(lines) if l.startswith(s)] for s in needles]
    assert all(len(m) == 1 for m in matches)
    a,b,c = [m[0] for m in matches]
    assert a < b < c and f"cp result/bin/btdu {NAME}" in lines[a:b]
    assert "shell: /usr/bin/bash -e {0}" in lines[a:b]
    end = lines.index("##[endgroup]", b+1, c)
    return lines[end+1:c]


def candidate(lines, file_hash, sidecar):
    records = [m[1] for l in lines if (m := ROW.fullmatch(l))]
    return "empreinte vérifiée" if records == [file_hash] and sidecar == [file_hash, NAME] else UNKNOWN


def fixed(lines, file_hash, sidecar):
    line = f"{file_hash}  {NAME}"
    related = [l for l in lines if l.endswith(f"  {NAME}")]
    return "empreinte vérifiée" if related == [line] and " ".join(sidecar) == f"{file_hash} {NAME}" else UNKNOWN


def main():
    start = perf_counter()
    result = []
    for i, pin in enumerate(PIN):
        zip_path = Path(f"bt{i}.zip")
        assert sha256(zip_path.read_bytes()).hexdigest() == pin
        with ZipFile(zip_path) as z:
            assert sorted(z.namelist()) == sorted([NAME, NAME+".sha256sum"])
            file_hash = sha256(z.read(NAME)).hexdigest()
            sidecar = z.read(NAME+".sha256sum").decode().split()
        raw = Path(f"bt{i}.log").read_bytes()
        log = raw.decode("utf-8")
        digest_lines = scopes(log)
        a,b = candidate(digest_lines, file_hash, sidecar),fixed(digest_lines, file_hash,sidecar)
        assert a == b == "empreinte vérifiée"
        contradiction = [l.replace(NAME, NAME+".other") for l in digest_lines]
        assert candidate(contradiction, file_hash, sidecar) == fixed(contradiction,file_hash,sidecar) == UNKNOWN
        assert fixed_verdict(extract(log, NAME)) == UNKNOWN
        result.append(dict(log_sha256=sha256(raw).hexdigest(), zip_sha256=pin, member_sha256=file_hash))
    assert result[0]["member_sha256"] == result[1]["member_sha256"]
    assert result[0]["member_sha256"] != result[2]["member_sha256"]
    print(json.dumps(dict(evidence=result, candidate_confirmations=3, fixed_confirmations=3,
                          wrong_path_abstentions=3, old_copy_abstentions=3,
                          seconds=perf_counter()-start), indent=2))

if __name__ == "__main__":
    main()
