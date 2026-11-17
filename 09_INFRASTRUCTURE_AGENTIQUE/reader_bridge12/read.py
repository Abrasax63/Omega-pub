#!/usr/bin/env python3
"""Omega reader12: generic source-pinned Markdown / LaTeX packet inventory.

Produces exact source spans only. This is document parsing, NOT mathematical
meaning extraction. The content is never promoted to a theorem.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DANGER = re.compile(
    r"(?:\bpreuve\b|\bdémonstration\b|\bréfut[ée]\b|"
    r"non[-‑\s]?théorème|contre[- ]exemple|"
    r"\blimites?\b|\bbarrière\b|\bincertitude\b)", re.I)
MAX_BYTES = 150000
MAX_PACKETS = 500
MAX_LINES_PER_PACKET = 30


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def safe_read(path: Path, expected: str) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("source path missing, symlinked or oversized")
    if not re.fullmatch(r"[a-f0-9]{40}", expected):
        raise ValueError("source requires immutable 40-character Git blob")
    raw = path.read_bytes()
    if blob(raw) != expected:
        raise ValueError("source changed after pin")
    return raw


def packetize(raw: bytes, source_path: str) -> dict:
    if len(raw) > MAX_BYTES:
        raise ValueError("oversized Markdown")
    lines = raw.decode("utf-8").splitlines()
    sha = blob(raw)
    packets = []
    heading_levels = []
    buffer: list[tuple[int, str]] = []
    math_open = False

    def flush():
        nonlocal buffer
        if not buffer:
            return
        start = buffer[0][0]
        end = buffer[-1][0]
        excerpt = "\n".join(line for _, line in buffer)
        # packet ID determined by verified source position and content
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        path = [h["title"] for h in heading_levels]
        context = "BLOCKED_SOURCE_CONTEXT" if any(DANGER.search(s) for s in path) else "SOURCE_CONTEXT_UNREVIEWED"
        packets.append({
            "packet_id": "P"+str(len(packets)+1).zfill(4)+"_"+digest[:10],
            "source_path": source_path, "source_blob": sha,
            "start_line": start, "end_line": end,
            "section_path": path,
            "source_quote": excerpt, "quote_sha256": digest,
            "contains_display_math": r"\[" in excerpt or "$$" in excerpt,
            "context_status": context,
            "scientific_status": "UNREVIEWED_SOURCE_PACKET",
        })
        buffer = []
        if len(packets) > MAX_PACKETS:
            raise ValueError("too many source packets")

    def push(i: int, text: str):
        buffer.append((i, text))
        if len(buffer) >= MAX_LINES_PER_PACKET:
            flush()

    for i, line in enumerate(lines, 1):
        h = HEADING.match(line)
        if h and not math_open:
            flush()
            level = len(h.group(1))
            heading_levels = [h0 for h0 in heading_levels if h0["level"] < level]
            heading_levels.append({"level": level, "title": h.group(2)})
            continue
        if not line.strip() and not math_open:
            flush()
            continue
        push(i, line)
        # Separate \[ and \] display lines are common; a single-line pair
        # must not incorrectly leave the parser inside math mode.
        math_open = (math_open or r"\[" in line or "$$" in line)
        if r"\]" in line or (line.count("$$") == 2):
            math_open = False
            flush()
    flush()
    return {
        "format": "OMEGA_READER12_EXACT_SOURCE_PACKETS",
        "source_blob": sha, "source_path": source_path,
        "source_lines": len(lines), "packets": packets,
        "stats": {
            "packet_count": len(packets),
            "packets_with_display_math": sum(p["contains_display_math"] for p in packets),
            "blocked_context_packets": sum(p["context_status"] == "BLOCKED_SOURCE_CONTEXT" for p in packets),
        },
        "automatic_formal_rules": [],
        "reading_semantics": "STRUCTURE_ONLY_NO_NATURAL_LANGUAGE_UNDERSTANDING",
    }


def verify_packets(raw: bytes, result: dict) -> list[str]:
    """Recompute exact packetization, not a semantic verifier."""
    expected = packetize(raw, result.get("source_path", ""))
    if result != expected:
        return ["PACKET_PROVENANCE_OR_BOUNDARY_MISMATCH"]
    lines = raw.decode("utf-8").splitlines()
    problems = []
    for p in result["packets"]:
        a, b = p["start_line"], p["end_line"]
        if not 1 <= a <= b <= len(lines) or "\n".join(lines[a-1:b]) != p["source_quote"]:
            problems.append(p["packet_id"]+":FALSE_SOURCE_SPAN")
        if hashlib.sha256(p["source_quote"].encode("utf-8")).hexdigest() != p["quote_sha256"]:
            problems.append(p["packet_id"]+":FALSE_DIGEST")
    return problems


def run(path: Path, expected_blob: str) -> dict:
    raw = safe_read(path, expected_blob)
    out = packetize(raw, path.as_posix())
    errors = verify_packets(raw, out)
    if errors:
        raise ValueError("source packet replay failed: "+str(errors))
    out["source_citations_valid"] = True
    return out
