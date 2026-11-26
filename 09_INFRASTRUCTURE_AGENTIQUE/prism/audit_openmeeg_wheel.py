"""Compare Windows verbose copy basenames to RECORD in the archived wheel."""
from base64 import urlsafe_b64encode
import csv
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import re
from time import perf_counter
from zipfile import ZipFile

PINS = (
    "e5b201a053238d26891071354fb58b4916c468e808d777bb02c5b2de638ce286",
    "8383a96adffb9c1e70b784ca79134e2b1fcde67ead4b460f32d2aede9ec3a5db",
    "9bef8bccf11114d184f0f45788d150065052c324ea74934b060097c02de5f37c",
)
LINE = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
COPY = re.compile(r"'(libopenblas\.dll)' -> '(?:\.\./)?wrapping/python/openmeeg/(libopenblas\.dll)'")
RENAMED = re.compile(r"libopenblas-[0-9a-f]+\.dll")


def record_matches(data, digest, size):
    return digest == "sha256=" + urlsafe_b64encode(sha256(data).digest()).decode().rstrip("=") and size == str(len(data))


def candidate(log, records):
    sources = [COPY.fullmatch(LINE.sub("", l)) for l in log.splitlines()]
    paths = {p for p in records if p == "openmeeg/libopenblas.dll"}
    return bool(sum(m is not None for m in sources) == 1 and paths)


def main():
    start = perf_counter()
    cases = []
    for i,pin in enumerate(PINS):
        data = Path(f"om{i}.zip").read_bytes()
        assert sha256(data).hexdigest() == pin
        raw = Path(f"om{i}.log").read_bytes()
        log = raw.decode("utf-8")
        labels = [LINE.sub("", l) for l in log.splitlines()]
        hits = sum(COPY.fullmatch(l) is not None for l in labels)
        assert hits == 1
        with ZipFile(BytesIO(data)) as archive:
            [wheel] = archive.namelist()
            body = archive.read(wheel)
        with ZipFile(BytesIO(body)) as w:
            [record] = [p for p in w.namelist() if p.endswith(".dist-info/RECORD")]
            rows = {p: (digest, size) for p,digest,size in csv.reader(StringIO(w.read(record).decode()))}
            [path] = [p for p in rows if p.startswith("openmeeg.libs/") and RENAMED.fullmatch(PurePosixPath(p).name)]
            obj = w.read(path)
            assert record_matches(obj,*rows[path])
            assert not record_matches(obj+b"\x00",*rows[path])
            assert not record_matches(obj,"sha256=wrong",rows[path][1])
            assert path in log
            ref = any(PurePosixPath(p).name == "libopenblas.dll" and record_matches(w.read(p),*rows[p]) for p in rows)
            proposed = candidate(log, rows)
            assert ref == proposed == False
            assert not candidate(log.replace("libopenblas.dll' ->", "fake.dll' ->"), rows)
            cases.append(dict(log_sha256=sha256(raw).hexdigest(), zip_sha256=pin, record_verified=1,
                              target_size=len(obj), renamed_member_sha256=sha256(obj).hexdigest(),
                              copy_markers=hits, fixed_verdict="indéterminé", candidate_verdict="indéterminé"))
    print(json.dumps(dict(cases=cases, second_stage_record_checks=3, wrong_digest_controls=6,
                          seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
