"""P5 parser V2 — FUTURE-ONLY exploratory design, NOT REAL-03 scoring.

Observed forms are from the archived REAL-02 and REAL-03 public experiments.
This module must NOT change REAL-03 frozen metrics or select a winner on its
evaluated output. A new data set is required to claim validated V2 accuracy.
"""
from __future__ import annotations

import re
import unicodedata

from p5_real03_semantic import extract as frozen_extract

VERSION="P5-SEMANTIC-V2-POSTHOC-FUTURE-ONLY"

def _normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKD",text)
                   if not unicodedata.combining(c)).casefold()

def extract(text,kind):
    """Return (candidate, extraction_reason), NEVER consults answer keys."""
    baseline,reason=frozen_extract(text,kind)
    if baseline is not None:
        return baseline,"accepted_by_frozen_v1"
    if not isinstance(text,str) or not text.strip():
        return None,reason
    first=_normalize(text.splitlines()[0]).strip()
    if len(first)>350:
        return None,"overlong_first_line"
    if kind=="RATE":
        match=re.match(
            r"^(?:(?:le|la|l')\s*)?(?:groupe|equipe)\s+([ab])\b",first)
        if match:
            chosen=match.group(1).upper()
            tail=first[match.end():]
            opposite="b" if chosen=="A" else "a"
            if re.search(r"\b(?:groupe|equipe)\s+"+opposite+r"\b",tail):
                return None,"contradictory_teams"
            return chosen,"posthoc_group_or_team"
    if kind in ("MUL","CRT"):
        # Treat the literal model-produced number after = as its *claim*,
        # NEVER solve or correct the expression to the true product here.
        m=re.fullmatch(
            r"\s*[0-9]+\s*[*x×]\s*[0-9]+\s*=\s*([0-9]+)\s*[.]?\s*",
            first,
        )
        if m:return str(int(m.group(1))),"posthoc_explicit_expression"
        m=re.fullmatch(r"(?:elle|cela|ca)\s+vaut\s+([0-9]+)\s*[.]?",first)
        if m:return str(int(m.group(1))),"posthoc_result_phrase"
    return None,reason
