#!/usr/bin/env python3
"""Omega 12: conservative automatic English->monadic clauses and bounded countermodels.

Unsupported prose is preserved and never silently dropped from reasoning.
A finite countermodel is a valid COUNTEREXAMPLE TO THE TRANSLATED CLAIM
conditional on the translation; absence of one is NOT a proof of entailment.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import re
import sys
import time
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[1]
SAMPLE = HERE / "FOLIO_VALIDATION_ROWS67_78_FROZEN.jsonl"
SAMPLE_BLOB = "fdb0d5ef7752577d09d84acd58328e91b409aa0a"
FOLIO_UPSTREAM_BLOB = "06244bd10b37eac73cba7aca6c336e96011ace58"
MAX_PREDICATES = 8
MAX_GROUND_ATOMS = 14
MAX_DOMAIN = 2
MAX_PREMISES = 12
RESTRICTED_TOKENS = re.compile(
    r"\b(?:who|that|which|and|or|either|neither|unless|except|only|not|"
    r"have|has|having|had|can|could|should|would|may|might|must|in|at|with|"
    r"than|between|from|by|because|if|then|when|where|whose)\b",
    flags=re.IGNORECASE
)
KEY = r"[A-Za-z][A-Za-z -]*"
ALL = re.compile(r"^All (?P<a>"+KEY+r") are (?P<b>"+KEY+r")\.$")
SOME = re.compile(r"^Some (?P<a>"+KEY+r") are (?P<b>"+KEY+r")\.$")
NO = re.compile(r"^No (?P<a>"+KEY+r") are (?P<b>"+KEY+r")\.$")
SIMPLE_IF = re.compile(
    r"^If something is (?:a |an )?(?P<a>"+KEY+r"), then it is "
    r"(?:a |an )?(?P<b>"+KEY+r")\.$"
)
PERSON_IMPLICATION = re.compile(
    r"^If (?P<name>[A-Z][a-z]+) is (?:a |an )?(?P<a>"+KEY+
    r"), then (?P=name) is (?P<neg>not )?(?:a |an )?(?P<b>"+KEY+r")\.$"
)
FACT = re.compile(
    r"^(?P<name>[A-Z][a-z]+) is (?P<neg>not )?(?:a |an )?(?P<cls>"+KEY+r")\.$"
)
LABEL_MAP = {"True":"SUPPORTED","False":"CONTRADICTED","Uncertain":"ABSTAIN"}


class FormalizationError(ValueError):
    pass


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def stable_hash(value) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
                                     separators=(",",":")).encode("utf-8")).hexdigest()


def normalize_class(value: str) -> str | None:
    """Mechanical morphology, no learned synonym or semantic substitution."""
    value = re.sub(r"\s+", " ", value.lower().strip())
    if not value or len(value) > 55 or RESTRICTED_TOKENS.search(value):
        return None
    if not re.fullmatch(r"[a-z]+(?:[ -][a-z]+)*", value):
        return None
    parts=value.split(" ")
    last=parts[-1]
    if len(last)>3 and last.endswith("ies"):
        parts[-1]=last[:-3]+"y"
    elif len(last)>3 and last.endswith("s") and not last.endswith(("ss","us","is")):
        parts[-1]=last[:-1]
    return " ".join(parts)


def parse_sentence(sentence: str, source_index: int | None) -> dict | None:
    if not isinstance(sentence,str) or len(sentence)>400:
        return None
    text=sentence.strip()
    specs=(("forall_imp",ALL),("exists_and",SOME),("forall_disjoint",NO),
           ("forall_imp",SIMPLE_IF),("person_imp",PERSON_IMPLICATION),
           ("fact",FACT))
    for kind,pattern in specs:
        match=pattern.fullmatch(text)
        if match is None:
            continue
        gd=match.groupdict()
        if kind=="fact":
            category=normalize_class(gd["cls"])
            if category is None:
                return None
            result={"kind":kind,"individual":gd["name"],
                    "predicate":category,"negative":bool(gd["neg"])}
        elif kind=="person_imp":
            a,b=normalize_class(gd["a"]),normalize_class(gd["b"])
            if a is None or b is None:
                return None
            result={"kind":kind,"individual":gd["name"],
                    "antecedent":a,"consequent":b,"negative":bool(gd["neg"])}
        else:
            a,b=normalize_class(gd["a"]),normalize_class(gd["b"])
            if a is None or b is None:
                return None
            result={"kind":kind,"a":a,"b":b}
        return {
            **result,
            "source_index":source_index,
            "source_excerpt":text,
            "source_sha256":hashlib.sha256(sentence.encode("utf-8")).hexdigest(),
            "interpretation_status":"AUTO_SYNTAX_CANDIDATE_NOT_SEMANTICALLY_CERTIFIED",
        }
    return None


def load_external():
    if not SAMPLE.is_file() or SAMPLE.is_symlink() or blob_sha(SAMPLE.read_bytes())!=SAMPLE_BLOB:
        raise FormalizationError("FOLIO sample changed")
    items=[json.loads(x) for x in SAMPLE.read_text(encoding="utf-8").splitlines()]
    if len(items)!=12 or any(not isinstance(q.get("premises"),list) or
                             not isinstance(q.get("conclusion"),str) or
                             q.get("label") not in LABEL_MAP for q in items):
        raise FormalizationError("FOLIO slice invalid")
    return items


def universe_of(clauses,goal):
    predicates=set()
    constants=set()
    for clause in [*clauses,goal]:
        if clause["kind"]=="fact":
            predicates.add(clause["predicate"])
            constants.add(clause["individual"])
        elif clause["kind"]=="person_imp":
            predicates.update((clause["antecedent"],clause["consequent"]))
            constants.add(clause["individual"])
        else:
            predicates.update((clause["a"],clause["b"]))
    return sorted(predicates),sorted(constants)


def eval_clause(clause,truths,domain):
    kind=clause["kind"]
    def pred(atom,person):
        return bool(truths.get((person,atom),False))
    if kind=="fact":
        truth=pred(clause["predicate"],clause["individual"])
        return not truth if clause["negative"] else truth
    if kind=="person_imp":
        person=clause["individual"]
        if not pred(clause["antecedent"],person):
            return True
        target=pred(clause["consequent"],person)
        return not target if clause["negative"] else target
    if kind=="forall_imp":
        return all(not pred(clause["a"],x) or pred(clause["b"],x) for x in domain)
    if kind=="forall_disjoint":
        return all(not (pred(clause["a"],x) and pred(clause["b"],x)) for x in domain)
    if kind=="exists_and":
        return any(pred(clause["a"],x) and pred(clause["b"],x) for x in domain)
    raise FormalizationError("unknown AST clause")


def bounded_countermodel(clauses,goal):
    """Enumerate ALL structures in 1-2 element domains up to a fixed budget.

    Uses only AST, not source/gold. Returns concrete, replayable model if any.
    No model found is UNDETERMINED, not a proof of entailment.
    """
    if len(clauses)>MAX_PREMISES:
        return {"status":"UNDETERMINED","reason":"CLAUSE_BUDGET_EXCEEDED"}
    predicates,constants=universe_of(clauses,goal)
    if not predicates or len(predicates)>MAX_PREDICATES or len(constants)>MAX_DOMAIN:
        return {"status":"UNDETERMINED","reason":"PREDICATE_OR_DOMAIN_BUDGET_EXCEEDED"}
    models_checked=0
    satisfiable=0
    for d in range(max(1,len(constants)),MAX_DOMAIN+1):
        domain=constants+[f"anonymous_{k}" for k in range(d-len(constants))]
        # Avoid accidental collision with a named constant.
        if len(set(domain))!=len(domain):
            return {"status":"UNDETERMINED","reason":"DOMAIN_NAME_COLLISION"}
        atoms=list(itertools.product(domain,predicates))
        if len(atoms)>MAX_GROUND_ATOMS:
            return {"status":"UNDETERMINED","reason":"GROUND_ATOM_BUDGET_EXCEEDED"}
        for values in itertools.product((False,True),repeat=len(atoms)):
            models_checked+=1
            assignment=dict(zip(atoms,values))
            if not all(eval_clause(c,assignment,domain) for c in clauses):
                continue
            satisfiable+=1
            if not eval_clause(goal,assignment,domain):
                witness={
                    person:{p:assignment[(person,p)] for p in predicates}
                    for person in domain
                }
                # Replay witness; never trust a model supplied by a generator.
                replay={(person,p):v for person,values in witness.items()
                        for p,v in values.items()}
                if not all(eval_clause(c,replay,domain) for c in clauses):
                    raise FormalizationError("internal countermodel failed replay")
                if eval_clause(goal,replay,domain):
                    raise FormalizationError("witness fails to refute goal")
                return {"status":"FINITE_COUNTERMODEL_FOUND",
                        "reason":"EXACT_BOUNDED_SEARCH_AND_REPLAY",
                        "domain":domain,"predicates":predicates,
                        "witness":witness,"models_checked":models_checked,
                        "satisfiable_models_seen":satisfiable,
                        "every_premise_replayed":True,
                        "goal_false_replayed":True,
                        "semantic_status":"CONDITIONAL_ON_UNCERTIFIED_TRANSLATION"}
    return {"status":"UNDETERMINED","reason":"NO_COUNTERMODEL_IN_FINITE_BOUND",
            "models_checked":models_checked,
            "satisfiable_models_seen":satisfiable}


def inspect(question,premises,case_id):
    if not isinstance(premises,list) or len(premises)>MAX_PREMISES:
        return {"id":case_id,"status":"UNDETERMINED",
                "reason":"PREMISE_BUDGET_EXCEEDED","source_count":len(premises)}
    clauses=[parse_sentence(raw,i) for i,raw in enumerate(premises)]
    goal=parse_sentence(question,None)
    missing=[i for i,c in enumerate(clauses) if c is None]
    base={
        "id":case_id,
        "premises_sha256":stable_hash(premises),
        "question_sha256":hashlib.sha256(question.encode("utf-8")).hexdigest(),
        "premises_count":len(premises),
        "clauses_parsed":len(premises)-len(missing),
        "unformalized_source_indices":missing,
        "goal_parsed":goal is not None,
        "parsed_clauses":[c for c in clauses if c is not None],
        "parsed_goal":goal,
        "scientific_claim_certified":False,
        "automatic_semantic_fidelity_proven":False,
    }
    if missing or goal is None:
        return {**base,"status":"UNDETERMINED",
                "reason":"INCOMPLETE_SOURCE_OR_GOAL_FORMALIZATION",
                "formalization_complete":False,"independent_tests_executed":0}
    model=bounded_countermodel(clauses,goal)
    return {**base,**model,"formalization_complete":True,
            "independent_tests_executed":int(model["status"]=="FINITE_COUNTERMODEL_FOUND"),
            "certification":"FINITE_WITNESS_RELATIVE_TO_AUTO_SYNTAX_ONLY"}


def run(rows):
    # Labels and curated FOL annotations are never supplied to parser or solver.
    inputs=[{"id":"FOLIO-%03d"%(67+i),"premises":r["premises"],
             "conclusion":r["conclusion"]} for i,r in enumerate(rows)]
    predictions=[inspect(q["conclusion"],q["premises"],q["id"]) for q in inputs]
    fingerprint=stable_hash([
        {"id":x["id"],"status":x["status"],
         "reason":x["reason"],"complete":x.get("formalization_complete",False)}
        for x in predictions])
    print("FORMALIZATIONS_FROZEN_BEFORE_GOLD_SHA256="+fingerprint,flush=True)
    for output,source in zip(predictions,rows):
        output["published_label"]=source["label"]
        output["published_reference"]=LABEL_MAP[source["label"]]
    return {
        "experiment":"OMEGA-AUTO-COUNTERMODEL-12",
        "provenance":"Yale-LILY/FOLIO validation 67-78 v0.0",
        "source_blob":FOLIO_UPSTREAM_BLOB,
        "sample_blob":SAMPLE_BLOB,
        "cases":len(rows),
        "distinct_theories":len({stable_hash(x["premises"]) for x in rows}),
        "automatic_parsed_premises":sum(x["clauses_parsed"] for x in predictions),
        "premises_total":sum(x["premises_count"] for x in predictions),
        "complete_formalizations":sum(x.get("formalization_complete",False) for x in predictions),
        "finite_countermodels_found":sum(x["status"]=="FINITE_COUNTERMODEL_FOUND" for x in predictions),
        "independent_witness_tests":sum(x.get("independent_tests_executed",0) for x in predictions),
        "new_scientific_theorems_certified":0,
        "unvalidated_translations":True,
        "label_distribution":dict(Counter(x["label"] for x in rows)),
        "predictions_hash_before_gold":fingerprint,
        "paid_api_calls":0,"model_training":False,"auto_promotion":False,
        "status":"PRELIMINARY_FINITE_WITNESS" if any(
            x["status"]=="FINITE_COUNTERMODEL_FOUND" for x in predictions
        ) else "NO_EXTERNAL_WITNESS",
        "limitations":[
            "Only English monadic statements matching explicitly conservative patterns",
            "Finite domain at most two individuals: no-model result never entails theorem",
            "Source-to-AST semantic fidelity is not independently certified",
            "Published FOLIO v0.0 labels are not a formal proof",
            "Some rows share premise theories and are statistically dependent",
            "No free Qwen generation is used in this separate, deterministic translator pilot",
        ],
        "rows":predictions
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    start=time.perf_counter()
    report=run(load_external())
    report["elapsed_seconds"]=round(time.perf_counter()-start,3)
    text=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        destination=args.output.resolve()
        if destination.is_relative_to(ROOT):
            parser.error("report path cannot be inside repository")
        destination.write_text(text,encoding="utf-8")
    else:
        print(text,end="")

if __name__=="__main__":
    main()
