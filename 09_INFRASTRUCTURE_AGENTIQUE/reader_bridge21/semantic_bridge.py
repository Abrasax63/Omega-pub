#!/usr/bin/env python3
"""Reader21: six anchored French formulations -> Reader20 AST, otherwise abstain.

Does NOT claim broad natural-language understanding, human-reviewed equivalence
or autonomous proof of a mathematical theorem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reader_bridge20"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from router import parse_claim, evaluate_exact, UnsupportedContract
from read import safe_read, blob

SOURCE = HERE / "FR_CASES_FROZEN.md"
BLOB = "91ddd3a736c0a6cf8019d52bd843263ad5b80139"
HEADER = re.compile(r"## Cas (\d\d)")
PRODUCT_A = re.compile(r"Sur les entiers naturels a=(\d+) et b=(\d+), chacun dans \[0,999\], j'affirme que (\d+) fois (\d+) vaut (\d+)\.")
PRODUCT_B = re.compile(r"Pour les entiers naturels a=(\d+) et b=(\d+), compris dans \[0,999\], le produit de (\d+) par (\d+) vaut (\d+)\.")
CONGRUENCES = re.compile(r"Pour l'application T=\[([\d,]+)\] sur (\d+) états \{([\d,]+)\}, avec 2<=n<=6, (?:le nombre de congruences est (\d+)|il existe exactement (\d+) congruences)\.")
BIPARTITE = re.compile(r"Sur un graphe n=(\d+) avec les différences \[([^\]]*)\], n compris entre 2 et 12 et couleurs binaires, ce graphe (est|n'est pas) deux-colorable\.")


def split_sentences(raw: bytes) -> list[dict]:
    cases = []
    current = None
    for lineno, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        m = HEADER.fullmatch(line)
        if m:
            if current:
                cases.append(current)
            current = {"id": "C"+m.group(1), "lines": []}
        elif current and line.strip():
            current["lines"].append((lineno,line))
    if current:
        cases.append(current)
    if len(cases) != 12 or len({c["id"] for c in cases}) != 12:
        raise ValueError("FROZEN_FRENCH_COHORT_DRIFT")
    return cases


def translate(s: str) -> list[str]:
    if not isinstance(s,str) or len(s)>1000 or "\n" in s:
        raise UnsupportedContract("UNSAFE_SENTENCE")
    m = PRODUCT_A.fullmatch(s) or PRODUCT_B.fullmatch(s)
    if m:
        a,b,x,y,target=m.groups()
        return [f"Hypothèses: a={a}; b={b}; domaine=N[0,999]",
                f"Énoncé: {x} * {y} = {target}",
                "Limites: entier naturel borné"]
    m=CONGRUENCES.fullmatch(s)
    if m:
        t,n,domain,claim_a,claim_b=m.groups()
        claimed=claim_a if claim_a is not None else claim_b
        if int(n) not in range(2,7) or domain!=",".join(map(str,range(int(n)))):
            raise UnsupportedContract("FINITE_DOMAIN_INCONSISTENT")
        return [f"Hypothèses: T=[{t}]; domaine={{0,...,{int(n)-1}}}",
                f"Énoncé: nombre_congruences(T) = {claimed}",
                "Limites: 2<=n<=6; partitions finies"]
    m=BIPARTITE.fullmatch(s)
    if m:
        n,edges,claim=m.groups()
        return [f"Hypothèses: n={n}; differences=[{edges}]",
                f"Énoncé: deux_colorable = {'oui' if claim=='est' else 'non'}",
                "Limites: 2<=n<=12; valeurs binaires"]
    raise UnsupportedContract("UNKNOWN_OR_INCOMPLETE_FRENCH_ASSERTION")


def process(raw: bytes) -> dict:
    sha=blob(raw)
    if sha!=BLOB:
        raise ValueError("FROZEN_SOURCE_BLOB_CHANGED")
    outcomes=[]
    for item in split_sentences(raw):
        evidence=[{"line":n,"literal":s,
                   "literal_sha256":hashlib.sha256(s.encode("utf-8")).hexdigest()}
                  for n,s in item["lines"]]
        row={"id":item["id"],"source_blob":sha,"source_evidence":evidence,
             "status":"ABSTAIN_UNSUPPORTED","reason":None,"ast":None,
             "contract":None,"result":None,"selected_verifier":None,
             "automatic_promotion":False,"independent_human_semantics":False}
        try:
            if len(evidence)!=1:
                raise UnsupportedContract("EXTRA_LINE_OR_PROMPT_INJECTION")
            lines=translate(evidence[0]["literal"])
            parsed=parse_claim({"lines":lines})
            verified=evaluate_exact(parsed)
            if verified["general_theorem_proved"] or verified["automatic_scientific_promotion"]:
                raise AssertionError("UNSAFE_PROMOTION")
            row.update({"status":"EXACT_CHECKED_RESTRICTED","contract":lines,
                        "ast":parsed["ast"],"selected_verifier":parsed["verifier"],
                        "result":verified})
        except UnsupportedContract as err:
            row["reason"]=str(err)
        outcomes.append(row)
    return {"experiment":"OMEGA_READER21_CONSERVATIVE_FRENCH_TO_AST",
            "source_git_blob":sha,"sentence_count":len(outcomes),
            "accepted_count":sum(x["status"]=="EXACT_CHECKED_RESTRICTED" for x in outcomes),
            "abstained_count":sum(x["status"]=="ABSTAIN_UNSUPPORTED" for x in outcomes),
            "natural_language_generalization_verified":False,
            "independent_human_annotation":False,"new_theorems_certified":0,
            "paid_api_calls":0,"outcomes":outcomes}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    opts=p.parse_args()
    try:
        result=process(safe_read(SOURCE,BLOB))
        result["run_status"]="FINISHED_CONTROLLED_FRENCH"
    except Exception:
        result={"run_status":"FAILED","error":traceback.format_exc()}
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(result["run_status"],result.get("accepted_count"),result.get("abstained_count"),flush=True)
    if result["run_status"]=="FAILED":
        raise SystemExit(1)


if __name__=="__main__":
    main()
