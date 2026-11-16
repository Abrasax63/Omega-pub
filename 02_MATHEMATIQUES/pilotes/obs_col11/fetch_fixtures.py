#!/usr/bin/env python3
"""Retrieve exactly six preregistered Radboud benchmark files.

No target file is executed. No hidden transition or label is supplied to
learning policies. Provenance, successes and failures stay inspectable.
"""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://automata.cs.ru.nl/pmwiki/uploads/BenchmarkMoore-RivestShapire1993/"
FILENAMES = (
    "crossword2x2.dot",
    "crossword3x3.dot",
    "register2.dot",
    "register3.dot",
    "register4.dot",
    "register5.dot",
)
def retrieve(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    events = []
    for file in FILENAMES:
        url = BASE + file
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Omega-OBS-COL-11-research/1.0"})
            with urllib.request.urlopen(req, timeout=18) as stream:
                data = stream.read(5_000_001)
                ctype = stream.headers.get("Content-Type", "")
            if len(data) > 5_000_000 or len(data) < 40 or b"digraph" not in data[:400]:
                raise ValueError("unexpected length or missing DOT header")
            path = dest / file
            path.write_bytes(data)
            events.append({"name": file, "url": url, "status": "DOWNLOADED",
                           "sha256": hashlib.sha256(data).hexdigest(),
                           "bytes": len(data), "mime": ctype})
        except (OSError, urllib.error.URLError, ValueError) as e:
            events.append({"name": file, "url": url, "status": "BLOCKED",
                           "reason": type(e).__name__ + ": " + str(e)[:300]})
    (dest / "download_manifest.json").write_text(json.dumps(
        events, indent=2, ensure_ascii=False), encoding="utf8")
    return events

if __name__ == "__main__":
    print(json.dumps(retrieve(sys.argv[1]), ensure_ascii=False, indent=2))
