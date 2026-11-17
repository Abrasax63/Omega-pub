#!/usr/bin/env python3
"""Append-only, tamper-evident JSONL memory for exploratory hypothesis records.

A Git-committed ledger can be resumed across cycles. GitHub Actions artifacts
alone are NOT persistent memory and are not automatically reimported.
Scientific verification is intentionally prohibited without a separate oracle.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path

ZERO = "0" * 64
CANDIDATE_STATES = frozenset(("PROPOSED", "UNDETERMINED", "REJECTED_PROVENANCE"))
MAX_EVENTS = 3000

class LedgerError(ValueError):
    pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))

def sha(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

def checked_entry(entry):
    if type(entry) is not dict or set(entry) != {
        "sequence", "previous_hash", "candidate_id", "status",
        "evidence", "event_hash"
    }:
        raise LedgerError("invalid event fields")
    if type(entry["sequence"]) is not int or entry["sequence"] < 1:
        raise LedgerError("invalid sequence")
    if not isinstance(entry["candidate_id"], str) or not (
        8 <= len(entry["candidate_id"]) <= 80):
        raise LedgerError("invalid candidate ID")
    if entry["status"] not in CANDIDATE_STATES:
        raise LedgerError("unverified science cannot be promoted in this ledger")
    evidence = entry["evidence"]
    if not isinstance(evidence, dict):
        raise LedgerError("missing evidence")
    required=("source_sha256","question_sha256","raw_generation_sha256")
    if not all(isinstance(evidence.get(k), str) and
               len(evidence[k]) == 64 and
               all(c in "0123456789abcdef" for c in evidence[k]) for k in required):
        raise LedgerError("bad provenance digests")
    proposal = {k: v for k,v in entry.items() if k != "event_hash"}
    if entry["event_hash"] != sha(proposal):
        raise LedgerError("event hash mismatch")
    return entry

def replay(text):
    """Reconstruct strictly ordered events and latest statuses."""
    events, latest = [], {}
    if not text:
        return events, latest
    if len(text.encode("utf-8")) > 3_000_000:
        raise LedgerError("ledger too large")
    previous=ZERO
    for line in text.splitlines():
        if not line.strip():
            raise LedgerError("empty event line")
        try:
            item=checked_entry(json.loads(line))
        except (ValueError, TypeError) as exc:
            raise LedgerError("corrupt ledger") from exc
        if item["sequence"] != len(events)+1 or item["previous_hash"] != previous:
            raise LedgerError("broken append-only hash chain")
        cid=item["candidate_id"]
        prior=latest.get(cid)
        if prior is not None:
            if prior["status"] == "REJECTED_PROVENANCE":
                raise LedgerError("cannot revive rejected provenance")
            if item["status"] == "PROPOSED":
                raise LedgerError("duplicate proposal")
            if item["evidence"] != prior["evidence"]:
                raise LedgerError("provenance changed during transition")
        elif item["status"] != "PROPOSED" and item["status"] != "REJECTED_PROVENANCE":
            raise LedgerError("missing initial proposal")
        events.append(item)
        latest[cid]=item
        previous=item["event_hash"]
        if len(events)>MAX_EVENTS:
            raise LedgerError("too many events")
    return events, latest

def make_event(events, candidate_id, status, evidence):
    item={"sequence":len(events)+1,
          "previous_hash":events[-1]["event_hash"] if events else ZERO,
          "candidate_id":candidate_id, "status":status, "evidence":evidence}
    item["event_hash"]=sha(item)
    checked_entry(item)
    return item

def append(path: Path, candidate_id: str, status: str, evidence: dict):
    """Atomic write; reject duplicates, rather than overwriting evidence."""
    path=Path(path)
    if path.is_symlink():
        raise LedgerError("symlink ledger not allowed")
    if path.exists() and not path.is_file():
        raise LedgerError("not a regular file")
    existing=path.read_text(encoding="utf-8") if path.exists() else ""
    events, latest=replay(existing)
    if candidate_id in latest and latest[candidate_id]["status"] == status:
        if latest[candidate_id]["evidence"] == evidence:
            return {"added":False, "sequence":latest[candidate_id]["sequence"],
                    "head_hash":events[-1]["event_hash"]}
        raise LedgerError("duplicate candidate with conflicting evidence")
    event=make_event(events,candidate_id,status,evidence)
    # Validate entire appended chain before writing.
    next_content=existing + canonical(event) + "\n"
    replay(next_content)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(prefix=".ledger.",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            handle.write(next_content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"added":True,"sequence":event["sequence"],"head_hash":event["event_hash"]}

def summary(path: Path):
    events, latest=replay(Path(path).read_text(encoding="utf-8"))
    return {"events":len(events),"unique_candidates":len(latest),
            "latest_statuses":{key:sum(
                1 for val in latest.values() if val["status"]==key
            ) for key in sorted(CANDIDATE_STATES)},
            "head_hash":events[-1]["event_hash"] if events else ZERO}
