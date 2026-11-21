"""Infrastructure-only: extract paired NL and Lean *declaration statement*.

Unlike EXTERNAL-MEMORY-01, new pinned upstream files may contain complete
Lean proof bodies instead of 'sorry'. Extracting only the declaration header
(before ':= by') avoids sending the proof answer as an inference hint.
This does NOT run Lean, check the proof, or establish NL↔Lean equivalence.

Added after the first failed source-audit run due to a genuine source-format
difference; structural scoring rules, gold, IDs and thresholds remain frozen.
"""
from __future__ import annotations
from hashlib import sha256
import re

UPSTREAM="marcusm117/ProofNet-Verified"
COMMIT="b7ca411a2abaa6caf3580192b30d865e5bd10bc4"
NL_RE=re.compile(r"(?m)^/-Informal Statement[ \t]*\n([\s\S]*?)\n-/$")
FORMAL_HEAD_RE=re.compile(r"(?ms)^theorem[ \t]+.*?:=[ \t]*by\b")


def git_blob(data:bytes)->str:
    from hashlib import sha1
    return sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def independent_lines(text:str)->tuple[str,str]:
    lines=text.splitlines()
    starts=[i for i,x in enumerate(lines) if x.strip()=="/-Informal Statement"]
    heads=[i for i,x in enumerate(lines) if x.startswith("theorem ")]
    if len(starts)!=1 or len(heads)!=1:
        raise ValueError("PAIRING_COUNT_AMBIGUOUS")
    end_nl=[i for i in range(starts[0]+1,len(lines)) if lines[i].strip()=="-/"]
    if len(end_nl)!=1 or end_nl[0]>=heads[0]:
        raise ValueError("INFORMAL_STATEMENT_BOUNDARY_INVALID")
    nl="\n".join(lines[starts[0]+1:end_nl[0]])
    theorem=[]
    found=False
    for line in lines[heads[0]:]:
        if ":= by" in line:
            theorem.append(line[:line.index(":= by")])
            found=True
            break
        theorem.append(line)
    if not found:
        raise ValueError("NO_THEOREM_DECLARATION_TERMINATOR")
    return nl,"\n".join(theorem).rstrip()


def extract(raw:bytes,item:dict)->dict:
    if not isinstance(raw,bytes) or not 40<len(raw)<100001:
        raise ValueError("PINNED_SOURCE_LENGTH_INVALID")
    if git_blob(raw)!=item["git_blob"]:
        raise ValueError("PINNED_SOURCE_GIT_BLOB_MISMATCH")
    text=raw.decode("utf8",errors="strict")
    nl=list(NL_RE.finditer(text))
    theorem=list(FORMAL_HEAD_RE.finditer(text))
    if len(nl)!=1 or len(theorem)!=1 or nl[0].end()>=theorem[0].start():
        raise ValueError("UNIQUE_SOURCE_PAIR_NOT_FOUND")
    source_nl=nl[0].group(1)
    formal=theorem[0].group(0).rsplit(":= by",1)[0].rstrip()
    second_nl,second_formal=independent_lines(text)
    if (source_nl!=second_nl or formal!=second_formal
        or not source_nl.strip() or not formal.startswith("theorem ")):
        raise ValueError("INDEPENDENT_PAIR_EXTRACTORS_DISAGREE")
    rest=text[theorem[0].end():]
    # The original file has a body; this is a descriptive flag only.
    has_sorry=bool(re.search(r"\bsorry\b",rest))
    return {
        "id":item["id"],"raw_git_blob":item["git_blob"],
        "informal_exact":source_nl,"lean_reference_exact":formal,
        "informal_sha256":sha256(source_nl.encode("utf8")).hexdigest(),
        "formal_sha256":sha256(formal.encode("utf8")).hexdigest(),
        "source_url":f"https://github.com/{UPSTREAM}/blob/{COMMIT}/{item['path']}",
        "lean_contains_sorry":has_sorry,
        "proof_body_excluded_from_model_input":True,
        "lean_proof_compiled_by_omega":False,
        "upstream_pairing_only_not_independent_semantic_gold":True,
    }
