"""Frozen, task-typed first-line answer parser for P5-REAL-03.

Calibrated on PUBLIC REAL-02 OUTPUT FORMS only, not their answer keys.
No runtime answer/reference lookup. Rejected/ambiguous content stays unscored.
This file is frozen before any new REAL-03 model response generation.
"""
from __future__ import annotations

import re
import unicodedata

PARSER_VERSION="REAL03-TYPED-PARSER-V1"
KINDS=("MUL","CRT","RATE","INJ")

def _ascii(text):
    return "".join(c for c in unicodedata.normalize("NFKD",text)
                   if not unicodedata.combining(c)).casefold()

def extract(text,kind):
    """Returns (answer, category), category describes success or reason."""
    if kind not in KINDS:
        raise ValueError("unknown question family")
    if not isinstance(text,str) or not text.strip():
        return None,"empty"
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    if not lines:
        return None,"empty"
    first=_ascii(lines[0].replace("’","'")).strip()
    first=first.strip('"\u00ab\u00bb ').strip()
    if len(first)>350:
        return None,"overlong_first_line"
    if kind in ("MUL","CRT"):
        # Numeric output must be a CLEAR stand-alone final value, never a
        # number extracted from a long ambiguous computation or percentage.
        patterns=(
            r"^(?:reponse(?:\s+finale)?\s*[:=]\s*|"
            r"resultat(?:\s+final)?\s*[:=]\s*|"
            r"le\s+(?:produit|resultat)\s+est\s+)?([0-9]+)\s*[.!]?$",
            r"^(?:reponse\s*:\s*)?([0-9]+)\s*[.!]?$",
        )
        for pattern in patterns:
            m=re.fullmatch(pattern,first)
            if m:
                return str(int(m.group(1))),"numeric_explicit"
        return None,"numeric_ambiguous_or_wrong_type"
    if kind=="RATE":
        # Accept clear first mention of the selected team, including
        # phrases with extra explanatory numbers, but reject competing
        # initial claims (A/B). Never read the known correct team.
        patterns=(
            r"^(?:reponse(?:\s+finale)?\s*[:=]\s*)?"
            r"(?:equipe\s+)?([ab])\b(?:\s*[.!]?|\s+(?:avec|a|est|possede|pour|car|parce|ayant|dont)\b.*)$",
            r"^(?:l[' ]equipe\s+|la\s+meilleure\s+(?:equipe\s+)?est\s+)([ab])\b.*$",
        )
        for pattern in patterns:
            m=re.fullmatch(pattern,first)
            if m:
                value=m.group(1).upper()
                # A repeated, explicit contradictory conclusion on the first
                # line means this is NOT safe to auto-grade.
                tail=first[m.end(1):]
                competing="b" if value=="A" else "a"
                if re.search(r"\bequipe\s+"+competing+r"\b",tail):
                    return None,"conflicting_teams"
                return value,"team_explicit"
        return None,"team_ambiguous_or_wrong_type"
    # INJ: the first word is an explicit yes/no answer. A reply such as
    # "Oui, elle n'est pas injective" is self-contradictory, so reject it.
    first=re.sub(r"^(?:reponse(?:\s+finale)?\s*[:=]\s*)","",first)
    m=re.match(r"^(oui|non)\b",first)
    if not m:
        return None,"binary_ambiguous_or_wrong_type"
    value=m.group(1).upper()
    if value=="OUI" and re.search(r"n[' ](?:est|etait)\s+pas\s+injective",first):
        return None,"binary_contradiction"
    if value=="NON" and re.search(r"\best\s+injective\b",first) and not re.search(
        r"n[' ](?:est|etait)\s+pas\s+injective",first
    ):
        return None,"binary_contradiction"
    return value,"binary_explicit"
