#!/usr/bin/env python3
"""Source-to-proof 07. Explicit source grammar, finite instances, independent audit.
Experimental; DOES NOT read unrestricted mathematical prose or certify new theorems.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import re
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[1]
SOURCES=BASE/"cross_domain_math05"/"source_snapshot"
spec=importlib.util.spec_from_file_location("bridge_v2", BASE/"source_logic_bridge06"/"bridge.py")
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
ATOM=r"[a-z][a-z0-9_]*"
TICK=chr(96)
RULE_RE=re.compile(r"^Si ("+TICK+ATOM+TICK+r"(?: et "+TICK+ATOM+TICK+r")*), alors "+TICK+r"((?:not:)?"+ATOM+r")"+TICK+r"\.$")
WORD=re.compile(TICK+r"("+ATOM+r")"+TICK)
BOUND="0≤m_ω≤ν(ω)"
PRECONDITION="On autorise la sélection arbitraire d'un sous-ensemble de témoins distincts"
PRODUCT="C(P,σ) = ∏"

class ContractError(ValueError):
    pass

def hash_json(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,
                                     separators=(",",":")).encode()).hexdigest()

def discover(roots=None):
    """Existing read-only source discovery; accept *unknown* IDs automatically."""
    roots=roots if roots is not None else (SOURCES,HERE)
    found={}
    for root in roots:
        for sid,doc in bridge.discover(root).items():
            if sid in found:
                raise ContractError("duplicate source: "+sid)
            found[sid]=doc
    return found

def source_for(question,docs):
    sid=question.get("source_id")
    if not isinstance(sid,str):
        raise ContractError("missing source_id")
    d=docs.get(sid)
    if d and question.get("expected_source_blob")!=d["blob"]:
        raise ContractError("source content changed or unpinned: "+sid)
    return d

def extract_horn(doc):
    """Parse only exact Si + backtick-atom + alors syntax, not generic French."""
    out=[]
    for line_no,raw in enumerate(doc["lines"],1):
        line=raw.strip()
        if len(line)>200:
            continue
        match=RULE_RE.fullmatch(line)
        if not match:
            continue
        premises=WORD.findall(match.group(1))
        if len(set(premises))!=len(premises):
            continue
        rule_id="rule-"+hashlib.sha256((doc["blob"]+":"+str(line_no)+":"+line).encode()).hexdigest()[:14]
        out.append({"rule_id":rule_id,"source_id":doc["id"],"premises":premises,
                    "conclusion":match.group(2),"source_blob":doc["blob"],
                    "source_file":doc["path"],"line":line_no,"excerpt":line,
                    "interpretation_status":"AUTO_PATTERN_CANDIDATE_UNVERIFIED"})
    return out

def audit_truth_table(facts,rules,goal):
    """Exact model enumeration independently checks material-implication semantics."""
    names={goal,*facts}
    for r in rules:
        names.update(r["premises"])
        names.add(r["conclusion"].removeprefix("not:"))
    if len(names)>14:
        return {"status":"LIMIT","verdict":"ABSTAIN"}
    ordered=sorted(names)
    def val(atom,assignment):
        return not assignment[atom[4:]] if atom.startswith("not:") else assignment[atom]
    surviving=positive=0
    for bits in itertools.product((False,True),repeat=len(ordered)):
        a=dict(zip(ordered,bits))
        if not all(a[f] for f in facts):
            continue
        if any(all(val(p,a) for p in r["premises"]) and not val(r["conclusion"],a)
               for r in rules):
            continue
        surviving+=1
        positive+=int(a[goal])
    if not surviving:
        verdict="ABSTAIN"
    elif positive==surviving:
        verdict="SUPPORTED"
    elif positive==0:
        verdict="CONTRADICTED"
    else:
        verdict="ABSTAIN"
    return {"status":"EXHAUSTIVE_TRUTH_TABLE","models":surviving,
            "positive_models":positive,"verdict":verdict}

def missing_base_assumptions(goal,facts,rules):
    """Expand a missing intermediate fact into the underlying missing premises.

    Diagnostic only: never turns an abstention into a positive/negative proof.
    Cycles and undefined relations are not silently assumed true.
    """
    by_head={}
    for r in rules:
        by_head.setdefault(r["conclusion"],[]).append(r["premises"])
    def missing(atom,seen):
        if atom in facts:
            return frozenset()
        if atom in seen or atom not in by_head:
            return frozenset((atom,))
        candidates=[]
        for premises in by_head[atom]:
            leaves=frozenset().union(*(missing(p,seen|{atom}) for p in premises))
            candidates.append(leaves)
        return min(candidates,key=lambda x:(len(x),tuple(sorted(x))))
    options=[missing(head,frozenset()) for head in (goal,"not:"+goal)
             if head in by_head]
    if not options:
        return []
    return sorted(min(options,key=lambda x:(len(x),tuple(sorted(x)))))

def horn(question,doc,docs):
    facts=question.get("facts")
    goal=question.get("goal")
    if (not isinstance(facts,list) or len(facts)>14 or len(set(facts))!=len(facts)
        or any(not isinstance(f,str) or not re.fullmatch(ATOM,f) for f in facts)
        or not isinstance(goal,str) or not re.fullmatch(ATOM,goal)):
        raise ContractError("invalid facts or goal")
    rules=extract_horn(doc)
    by_source={doc["id"]:rules} if rules else {}
    q={"source_id":doc["id"],"facts":facts,"goal":goal}
    derived=bridge.assess(q,docs,by_source)
    proof_valid=bridge.check_proof(q,derived,docs,by_source)
    audit=audit_truth_table(facts,rules,goal)
    if derived["verdict"]=="ABSTAIN" and rules:
        derived["missing_assumptions"]=missing_base_assumptions(goal,set(facts),rules)
    if audit["status"]!="EXHAUSTIVE_TRUTH_TABLE" or derived["verdict"]!=audit["verdict"]:
        derived["verdict"]="ABSTAIN"
        derived["proof"]=[]
        derived["reason"]="INDEPENDENT_ORACLE_MISMATCH"
        proof_valid=False
    return {**derived,"kind":"horn","independent_check":audit,
            "certificate_valid":proof_valid,
            "representation":{"kind":"HORN_AST","rules":rules,
                              "grammar":"CONTROLLED_SYNTAX_NOT_GENERAL_NLU"}}

def extract_bound(doc):
    required=(PRECONDITION,PRODUCT,BOUND)
    result=[]
    for token in required:
        lines=[{"line":i,"excerpt":line.strip(),"source_blob":doc["blob"]}
               for i,line in enumerate(doc["lines"],1) if token in line]
        if not lines:
            return []
        result.append(lines[0])
    return result

def oracle_subsets(witnesses,requested):
    """Separate explicit search over every possible subset of indexed witnesses."""
    for mask in range(1<<len(witnesses)):
        indices=[i for i in range(len(witnesses)) if mask & (1<<i)]
        got=Counter(witnesses[i] for i in indices)
        if all(got.get(k,0)==v for k,v in requested.items()) and all(
                got.get(k,0)==0 for k in set(witnesses)-set(requested)):
            return True,indices
    return False,[]

def capacity(question,doc):
    anchors=extract_bound(doc)
    base={"kind":"capacity","representation":{"kind":"COORDINATE_CAPACITY_BOUND",
          "anchors":anchors,"source_blob":doc["blob"],
          "grammar":"EXPLICIT_EQUATION_WITH_PRECONDITION_ONLY"}}
    if not anchors:
        return {**base,"verdict":"ABSTAIN","reason":"FORMULA_OR_SCOPE_NOT_FOUND",
                "certificate_valid":True,"proof":[]}
    if question.get("independent_selection") is not True or question.get("additional_constraints"):
        return {**base,"verdict":"ABSTAIN","reason":"UNVERIFIED_EXTRA_CONSTRAINTS",
                "certificate_valid":True,"proof":[]}
    witnesses=question.get("witness_motifs")
    requested=question.get("requested")
    if (not isinstance(witnesses,list) or len(witnesses)>12 or not all(
            isinstance(s,str) and re.fullmatch(ATOM,s.lower()) for s in witnesses)
        or not isinstance(requested,dict) or len(requested)>12 or not all(
            isinstance(k,str) and re.fullmatch(ATOM,k.lower()) and type(v) is int
            and 0<=v<=12 for k,v in requested.items())):
        raise ContractError("invalid finite instance")
    counts=Counter(witnesses)
    # Analytic computation from the extracted coordinate bounds.
    feasible=all(v<=counts.get(k,0) for k,v in requested.items())
    selected=[]
    allocated=Counter()
    if feasible:
        for i,motif in enumerate(witnesses):
            if allocated[motif]<requested.get(motif,0):
                allocated[motif]+=1
                selected.append(i)
    exact,independent_witness=oracle_subsets(witnesses,requested)
    valid=feasible==exact and (not feasible or
         all(Counter(witnesses[i] for i in selected).get(k,0)==v
             for k,v in requested.items()))
    if not valid:
        return {**base,"verdict":"ABSTAIN","reason":"EXACT_ORACLE_DISAGREEMENT",
                "certificate_valid":False,"proof":[]}
    return {**base,"verdict":"SUPPORTED" if feasible else "CONTRADICTED",
            "reason":"FINITE_COORDINATE_CAPACITY",
            "proof":{"source_anchors":anchors,"counts":dict(counts),
                     "requested":requested,"selected_indices":selected},
            "independent_check":{"status":"EXHAUSTIVE_SUBSET_ENUMERATION",
                                 "feasible":exact,"checked_masks":1<<len(witnesses),
                                 "witness":independent_witness if exact else []},
            "certificate_valid":True}

def answer(q,documents):
    doc=source_for(q,documents)
    if not doc:
        return {"id":q.get("id"),"verdict":"ABSTAIN","reason":"SOURCE_UNKNOWN",
                "certificate_valid":True}
    kind=q.get("kind")
    if kind=="horn":
        response=horn(q,doc,documents)
    elif kind=="capacity":
        response=capacity(q,doc)
    else:
        response={"verdict":"ABSTAIN","reason":"KIND_NOT_SUPPORTED",
                  "certificate_valid":True}
    return {"id":q.get("id"),"source_id":doc["id"],"source_blob":doc["blob"],
            **response,"epistemic_status":"INSTANCE_CHECKED_NOT_SCIENCE_CERTIFIED"}

def run(cases,documents=None):
    docs=documents if documents is not None else discover()
    # Strip gold before inference and hash all choices before scoring.
    questions=[{k:v for k,v in c.items() if k!="expected"} for c in cases]
    outputs=[answer(q,docs) for q in questions]
    choice_hash=hash_json([{"id":r["id"],"verdict":r["verdict"]} for r in outputs])
    for result,original in zip(outputs,cases):
        result["expected"]=original["expected"]
        result["match"]=result["verdict"]==original["expected"]
    return {"experiment":"OMEGA-SOURCE-TO-PROOF-07",
            "status":"BOUNDED_PATTERN_EXPERIMENT_NOT_GENERAL_REASONING",
            "choices_sha256_before_scoring":choice_hash,
            "cases_sha256":hash_json(cases),
            "cases":len(cases),"correct":sum(r["match"] for r in outputs),
            "answered":sum(r["verdict"]!="ABSTAIN" for r in outputs),
            "false_confident":sum(r["verdict"]!="ABSTAIN" and not r["match"] for r in outputs),
            "invalid_certificates":sum(not r["certificate_valid"] for r in outputs),
            "always_abstain_baseline_correct":sum(c["expected"]=="ABSTAIN" for c in cases),
            "results":outputs,"auto_promotion":False,"model_weights_changed":False,
            "limitations":["Only controlled Horn grammar and one formula family",
                           "No general text interpretation or neural reasoning",
                           "Source mathematics are not newly proved",
                           "Same-author cases; no external blind replication",
                           "Not wired to native RCE or hourly agent"]}

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cases",type=Path,default=HERE/"CASES_FROZEN.json")
    cli.add_argument("--output",type=Path)
    opts=cli.parse_args()
    report=run(json.loads(opts.cases.read_text(encoding="utf-8"))["cases"])
    payload=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if opts.output:
        dest=opts.output.resolve()
        if dest.is_relative_to(ROOT):
            cli.error("output must be outside repository")
        dest.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")

if __name__=="__main__":
    main()
