"""Audit test verdicts independently of a successful build-record upload."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter
from audit_attempt_scope import records

ANSI=re.compile(r"\x1b\[[0-9;]*m")
PACKAGE=re.compile(r"^\S+Z\s+(PASS|FAIL) Package internal/e2e \([^)]+\)$")
SUMMARY=re.compile(r"^\S+Z DONE (\d+) tests(?:, \d+ skipped)?(?:, (\d+) failures?)? in [\d.]+s$")


def verdict(lines):
    package=[]
    totals=[]
    for line in lines:
        plain=ANSI.sub("",line)
        if m:=PACKAGE.fullmatch(plain):
            package.append(m[1])
        if m:=SUMMARY.fullmatch(plain):
            totals.append((int(m[1]),int(m[2] or 0)))
    if len(package)!=1 or len(totals)!=1 or not totals[0][0]:
        return "abstention"
    return {("PASS",False):"success",("FAIL",True):"failure"}.get((package[0],bool(totals[0][1])),"abstention")


def main():
    start=perf_counter()
    raw_inventory=Path("compose-test-inventory.json").read_bytes()
    inv=json.loads(raw_inventory)
    assert len(inv["artifacts"])==inv["count"]
    stamp="2026-11-24T14:35:55.000Z "
    assert verdict([stamp+"DONE 7 tests, 1 failure in 1.6s"])=="abstention"
    assert verdict([stamp+"Artifact docker~compose~ABC.dockerbuild successfully finalized. Artifact ID 4"])=="abstention"
    cases=[]
    for case in json.loads(Path("compose-test-cases.json").read_bytes()):
        raw=Path(str(case["id"])+".log").read_bytes()
        lines=raw.decode().splitlines()
        low,high=(datetime.fromisoformat(case[k]) for k in ("started_at","completed_at"))
        linked=records(lines,inv["artifacts"],low,high)
        cases.append(dict(case=case,reference="success" if linked else "abstention",
                          candidate=verdict(lines),artifact_ids=linked,sha256=sha256(raw).hexdigest(),
                          cp_av=raw.count(b"cp -av")))
    print(json.dumps(dict(cases=cases,inventory_sha256=sha256(raw_inventory).hexdigest(),
                          controls=2,seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
