"""OMEGA code repair: public-test-guided *candidate* search, not training.

This is a deliberately narrow program-repair tool for transform(s) exercises
and reuses the already-audited parser and sandbox. It is not an AGI and never
reads gold or hidden holdout. No model, API, gradient, or Git operations.

Crucial fix vs the original SEMANTIC04 one-edit baseline:
ALL occurrence positions are tried, rather than only str.replace(...,1)
for the first matching occurrence in a whole source file. Some first
occurrences are keywords in a Python 'for' statement.

If several proposals fit the visible examples, this tool DOES NOT silently
certify one. It proposes a discriminating input requiring a NEW oracle
observation, or abstains. A candidate passing public examples is not proven
correct on an untested input distribution.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core

MAX_CANDIDATES=160
MAX_PROBE_INPUTS=80
PROBE_INPUTS=(
    "","a","b","c","d","A","B","C","D","0","1","9","ab","ba","ac","ca",
    "abc","cab","aab","abb","ccb","cba","bc","aaa","bbb","ccc","aBc",
    "ABC","bAc","acb","abcc","aaab","aabb","bbaa","cabc","abca",
    "a|b","a:b","a,b","a a","c c","ab!","b0c","c1a","09a","abc123",
    "0123","a1b2","abbc","A|b","c|a","xxy","xyxy","zzab","caac",
)


def all_occurrences(source, old):
    """Return disjoint edit offsets, including later occurrences in same code."""
    start=0
    while True:
        index=source.find(old,start)
        if index<0:
            break
        yield index
        start=index+len(old)


def candidate_codes(source, edits=None, limit=MAX_CANDIDATES):
    if edits is None:
        edits=core.EDITS
    if not isinstance(source,str) or len(source)>core.sandbox.MAX_CODE_CHARS:
        raise ValueError("INVALID_SOURCE")
    if not 1<=limit<=MAX_CANDIDATES:
        raise ValueError("INVALID_EDIT_BUDGET")
    seen=set()
    out=[]
    def add(label, code):
        if code in seen or len(out)>=limit:
            return
        seen.add(code)
        parsed,_=core.allowed(code)
        if parsed is not None:
            out.append({"edit":label,"code":parsed,
                        "sha256":sha256(parsed.encode()).hexdigest()})

    add("unchanged",source)
    for i,(old,new) in enumerate(edits):
        if len(out)>=limit:
            break
        for pos in all_occurrences(source,old):
            if len(out)>=limit:
                break
            candidate=source[:pos]+new+source[pos+len(old):]
            add("replacement_"+str(i)+"_at_"+str(pos),candidate)
    # Reuse existing bounded appended-line modifications instead of
    # creating a second mutation engine; core.candidates includes 1st
    # occurrence only, but provides the duplicate-append operators.
    for label,code in core.candidates(source):
        if len(out)>=limit:
            break
        if label in ("remove_duplicate","duplicate_append"):
            add(label,code)
    return out


def run_public(code, observations):
    if not 1<=len(observations)<=12:
        raise ValueError("INVALID_PUBLIC_OBSERVATION_COUNT")
    for x in observations:
        if (not isinstance(x,dict) or not isinstance(x.get("input"),str)
                or len(x["input"])>24 or not isinstance(x.get("output"),list)):
            raise ValueError("INVALID_PUBLIC_EXAMPLE")
    got=core.sandbox.execute_student(code,[x["input"] for x in observations])
    return len(got)==len(observations) and all(
        g.get("value")==x["output"] for g,x in zip(got,observations))


def collect_agreeing(source,observations,limit=MAX_CANDIDATES):
    trials=0
    agreed=[]
    for row in candidate_codes(source,limit=limit):
        trials+=1
        if run_public(row["code"],observations):
            agreed.append(row)
    return agreed,trials


def probe_disagreement(agreed):
    """Find an input where PUBLIC-admissible candidates disagree.

    A disagreement is not an oracle answer: never call an oracle hidden
    behind the evaluator, never use it to pick a candidate, and never
    assert that the apparent majority answer is true.
    """
    if len(agreed)<2:
        return None
    for s in PROBE_INPUTS[:MAX_PROBE_INPUTS]:
        outputs=[]
        for row in agreed:
            actual=core.sandbox.execute_student(row["code"],[s])
            if not actual or "value" not in actual[0]:
                outputs.append({"error":actual[0].get("error","NO_OUTPUT") if actual else "NO_OUTPUT"})
            else:
                outputs.append(actual[0]["value"])
        serial=[json.dumps(x,sort_keys=True) for x in outputs]
        if len(set(serial))>1:
            return {"proposed_input":s,"outputs_by_candidate_hash":{
                row["sha256"]:out for row,out in zip(agreed,outputs)},
                "oracle_answer_provided":False}
    return None


def resolve(broken,observations,model_text=None,limit=MAX_CANDIDATES):
    """One public-only resolution attempt, optional *untrusted* model text.

    Does not inspect test gold, hidden answers or source class names.
    Multiple matching candidates => abstention + request for new oracle
    observation, rather than arbitrarily use the first match.
    """
    if not isinstance(observations,list):
        raise ValueError("INVALID_PUBLIC_OBSERVATIONS")
    sources=[("broken",broken)]
    if model_text is not None:
        code,_=core.permissive(model_text)
        if code is not None and code!=broken:
            sources.append(("model",code))
    matches=[]
    tried=0
    seen=set()
    for origin,src in sources:
        candidates,examined=collect_agreeing(src,observations,limit=limit)
        tried+=examined
        for item in candidates:
            if item["sha256"] in seen:
                continue
            seen.add(item["sha256"])
            matches.append({**item,"origin":origin})
    result={"status":"NO_VERIFIED_CANDIDATE","selected_code":None,
            "examined":tried,"matching_public_count":len(matches),
            "seed_count":len(sources),"hidden_tests_seen":0,
            "new_model_calls":0,"training_steps":0,
            "bounded":True,"scientific_proof":False,
            "provenance":"PUBLIC_EXAMPLES_ONLY",
            "candidate_hashes":[x["sha256"] for x in matches]}
    if len(matches)==1:
        result.update(status="UNIQUE_PUBLIC_CANDIDATE_NEEDS_INDEPENDENT_TEST",
                      selected_code=matches[0]["code"],
                      chosen_edit=matches[0]["edit"])
    elif len(matches)>1:
        probe=probe_disagreement(matches)
        if probe is None:
            result["status"]="AMBIGUOUS_CANDIDATES_NO_PROBE_FOUND"
        else:
            result["status"]="NEEDS_ORACLE_RESPONSE"
            result["suggested_probe"]=probe
    return result


def extend_public(observations,new_input,new_output):
    """A genuinely NEW trusted observation can reduce ambiguity.

    This is only permitted for development and live environments with
    authorized oracle access. Heldout cases are never admissible here.
    """
    if any(x["input"]==new_input for x in observations):
        raise ValueError("REUSED_PROBE_NOT_NEW_INFORMATION")
    if not isinstance(new_input,str) or len(new_input)>24 or not isinstance(new_output,list):
        raise ValueError("INVALID_NEW_ORACLE_OBSERVATION")
    return observations+[{"input":new_input,"output":new_output}]
