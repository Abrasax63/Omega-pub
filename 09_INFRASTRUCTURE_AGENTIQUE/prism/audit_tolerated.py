"""Compare GitHub step conclusion with the observed action outcome."""
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter

TS=r"^\S+Z "
OUTCOME=re.compile(TS+r"  outcome: (success|failure),")
CONCLUSION=re.compile(TS+r"  conclusion: (success|failure)")
STATUS=re.compile(TS+r"Status:\s+(\w+)")


def verdict(lines,tolerated):
    outcome={m[1] for l in lines if (m:=OUTCOME.fullmatch(l))}
    conclusion={m[1] for l in lines if (m:=CONCLUSION.fullmatch(l))}
    running={m[1] for l in lines if (m:=STATUS.fullmatch(l))}
    if tolerated and outcome=={"failure"} and conclusion=={"success"}:
        return "failure_tolerated"
    if not tolerated and not outcome and running=={"running"}:
        return "success"
    return "abstention"


def main():
    start=perf_counter()
    ts="2026-11-25T10:00:00Z "
    assert verdict([ts+"  outcome: failure,"],True)=="abstention"
    assert verdict([ts+"  outcome: failure,",ts+"  outcome: success,",ts+"  conclusion: success"],True)=="abstention"
    out=[]
    for case in json.loads(Path("tolerated-cases.json").read_bytes()):
        raw=Path(str(case["id"])+".log").read_bytes()
        truth=("failure_tolerated" if case["tolerated"] else "success") if case["check"]=="success" else None
        out.append(dict(case=case,oracle=truth,reference=case["setup"],
                        candidate=verdict(raw.decode().splitlines(),case["tolerated"]),
                        sha256=sha256(raw).hexdigest(),cp_av=raw.count(b"cp -av")))
    print(json.dumps(dict(cases=out,controls=2,seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
