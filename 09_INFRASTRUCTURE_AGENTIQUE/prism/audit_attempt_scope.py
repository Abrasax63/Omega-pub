"""Separate success of a test attempt from upload of a build record."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter

TS=r"(?P<stamp>\S+Z) "
PASS=re.compile(TS+r"ok\s+github\.com/moby/buildkit/client\s+\S+")
RUN=re.compile(TS+r"=== RUN\s+TestCompatibilityIntegration(?:/.*)?")
ERROR=re.compile(TS+r"##\[error\]buildx bake failed with: failed to solve: .+")
DIGEST=re.compile(TS+r"SHA256 digest of uploaded artifact is (?P<digest>[0-9a-f]{64})")
RECEIPT=re.compile(TS+r"Artifact (?P<name>[\w~.-]+\.dockerbuild) successfully finalized\. Artifact ID (?P<id>\d+)")


def verdict(lines):
    ran=any(RUN.fullmatch(line) for line in lines)
    passed=any(PASS.fullmatch(line) for line in lines)
    failed=any(ERROR.fullmatch(line) for line in lines)
    if ran and passed and not failed:
        return "success"
    if failed and not ran and not passed:
        return "blocked"
    return "abstention"


def records(lines, inventory, low, high):
    linked=[]
    digest=None
    for line in lines:
        if m:=DIGEST.fullmatch(line):
            digest="sha256:"+m["digest"]
        if m:=RECEIPT.fullmatch(line):
            matches=[a for a in inventory if a["id"]==int(m["id"])]
            if len(matches)==1:
                a=matches[0]
                when=datetime.fromisoformat(a["created_at"])
                if a["name"]==m["name"] and a["digest"]==digest and low<=when<=high:
                    linked.append(a["id"])
            digest=None
    return linked


def main():
    start=perf_counter()
    raw_catalog=Path("attempt-inventory.json").read_bytes()
    catalog=json.loads(raw_catalog)
    assert catalog["count"]==len(catalog["artifacts"])
    stamp="2026-11-25T02:00:00Z "
    sample=[stamp+"=== RUN   TestCompatibilityIntegration",stamp+"ok github.com/moby/buildkit/client 1s"]
    bad=stamp+"##[error]buildx bake failed with: failed to solve: log control"
    assert verdict([stamp+"Artifact moby~buildkit~ABC.dockerbuild successfully finalized. Artifact ID 123"])=="abstention"
    assert verdict([*sample,bad])=="abstention"
    out=[]
    for case in json.loads(Path("attempt-cases.json").read_bytes()):
        raw=Path(str(case["id"])+".log").read_bytes()
        lines=raw.decode().splitlines()
        truth=("success" if case["test"]=="success" else
               "blocked" if case["base_build"]=="failure" and case["test"] in ("skipped",None)
               else "unknown")
        low,high=(datetime.fromisoformat(case[k]) for k in ("started_at","completed_at"))
        out.append(dict(case=case,reference="success",oracle=truth,candidate=verdict(lines),
                        records=records(lines,catalog["artifacts"],low,high),
                        sha256=sha256(raw).hexdigest(),cp_av=raw.count(b"cp -av")))
    print(json.dumps(dict(cases=out,controls=2,inventory_sha256=sha256(raw_catalog).hexdigest(),
                          seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
