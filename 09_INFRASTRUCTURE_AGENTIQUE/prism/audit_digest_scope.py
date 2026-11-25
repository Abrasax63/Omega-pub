"""Check whether a content digest uniquely identifies an upload across runs."""
import hashlib
import json
from pathlib import Path
from time import perf_counter

from audit_direct_cjk import extract


def scoped(receipt, source, inventory):
    if receipt is None or receipt[2] is None or not receipt[3]:
        return None
    _, identifier, digest, _ = receipt
    matches = [a for a in inventory if (a["repo"], a["run"], a["id"], a["digest"])
               == (*source, identifier, "sha256:" + digest)]
    return matches[0] if len(matches) == 1 else None


def key(artifact):
    return [artifact[k] for k in ("repo", "run", "id", "name")] if artifact else None


def main():
    start = perf_counter()
    catalog = Path("digest-scope-inventory.json").read_bytes()
    inventory = []
    for run in json.loads(catalog):
        assert run["count"] == len(run["artifacts"])
        inventory.extend(dict(repo=run["repo"], run=run["run"], **a) for a in run["artifacts"])
    cases = json.loads(Path("digest-scope-cases.json").read_bytes())
    records, controls = [], 0
    for index, case in enumerate(cases):
        raw = Path(str(case["job"]) + ".log").read_bytes()
        receipt = extract(raw.decode(), case["path"])
        source = case["repo"], case["run"]
        truth, = [a for a in inventory if (a["repo"], a["run"], a["name"]) == (*source, case["name"])]
        matches = [a for a in inventory if receipt and a["digest"] == "sha256:" + str(receipt[2])]
        candidate = scoped(receipt, source, inventory)
        if index and receipt:
            other = cases[3-index]
            assert scoped(receipt, (other["repo"], other["run"]), inventory) is None
            wrong = (*receipt[:2], "0"*64, receipt[3])
            assert scoped(wrong, source, inventory) is None
            controls += 2
        records.append(dict(case=case, sha256=hashlib.sha256(raw).hexdigest(),
                            truth=key(truth), digest_match_count=len(matches),
                            fixed=key(matches[0] if len(matches)==1 else None),
                            forced_first=key(min(matches,key=lambda a:a["id"]) if matches else None),
                            candidate=key(candidate), cp_av_markers=raw.count(b"cp -av")))
    print(json.dumps(dict(cases=records, contradictory_controls=controls,
                          inventory_sha256=hashlib.sha256(catalog).hexdigest(),
                          seconds=round(perf_counter()-start,5)),ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
