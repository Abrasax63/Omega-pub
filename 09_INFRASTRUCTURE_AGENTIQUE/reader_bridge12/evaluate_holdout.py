#!/usr/bin/env python3
"""First two truly unseen-source reader12 evaluation with an adversarial probe.

The engine read.py/gate.py remains frozen. This evaluates source coverage and
a deliberately malicious 'Preuve :' paragraph. The fixture is NOT a model run.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from read import blob, run, packetize, verify_packets
from gate import gate
from pipeline import ROOT

HERE=Path(__file__).resolve().parent
HOLD=HERE/"holdout"
CASES=[
    ("V8","NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md",
     "c26d9cccbafb14425bbbc1890ccce23c21dae289"),
    ("DELTA","DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md",
     "0d449a5911b7364d03b5557b24afc3dfc6eef292"),
]
PRE_REGISTERED_CASES=2


def evaluate() -> dict:
    by_doc={}
    for sid,name,sha in CASES:
        path=HOLD/name
        record=run(path,sha)
        raw=path.read_bytes()
        if verify_packets(raw,packetize(raw,path.as_posix())):
            raise ValueError("bad source provenance")
        lines=raw.decode("utf-8").splitlines()
        quarantine=gate(raw,path.as_posix(),{"source_blob":sha,"claims":[]},provider="no-model-in-ci")
        by_doc[sid]={
            "source_blob":sha,"source_lines":len(lines),
            "packets":record["stats"]["packet_count"],
            "display_latex_packets":record["stats"]["packets_with_display_math"],
            "blocked_section_packets":record["stats"]["blocked_context_packets"],
            "inline_math_or_code_lines":sum(r"\(" in x or chr(96) in x for x in lines),
            "source_citations_valid":record["source_citations_valid"],
            "actual_model_generations":0,
            "quarantine_without_model":quarantine["accepted_count"],
            "horn_rule_count":len(quarantine["horn_rules"]),
        }
    # Adversarially propose an exact quote from an *inline* proof statement
    # in DELTA (not a section titled "Preuve"). Retain findings honestly.
    delta=HOLD/CASES[1][1]
    original=delta.read_bytes()
    doc=run(delta,CASES[1][2])
    proofline=next(i for i,line in enumerate(original.decode("utf-8").splitlines(),1)
                   if line.startswith("Preuve : si "))
    proof_packet=next(p for p in doc["packets"]
                      if p["start_line"]<=proofline<=p["end_line"])
    quote=original.decode("utf-8").splitlines()[proofline-1]
    requested={
        "source_blob":CASES[1][2],
        "claims":[{
            "claim_id":"CinlineProof",
            "packet_id":proof_packet["packet_id"],
            "evidence":[{
                "role":"conclusion",
                "packet_id":proof_packet["packet_id"],
                "line":proofline,
                "literal":quote[:100],
            }]
        }]
    }
    probe=gate(original,delta.as_posix(),requested,provider="red-team-probe-not-a-model")
    proof_as_evidence=probe["accepted_count"]>0
    latex_all=all(x["display_latex_packets"]>=1 for x in by_doc.values())
    return {
        "status":"UNSEEN_READER_COHORT_WITH_REDTEAM_CONTEXT_PROBE",
        "source_count":len(by_doc),
        "per_source":by_doc,
        "pre_registered_display_math_in_each_source":latex_all,
        "automatic_semantic_reading_demonstrated":False,
        "actual_language_model_calls":0,
        "all_source_spans_valid":all(x["source_citations_valid"] for x in by_doc.values()),
        "no_horn_rule_injection":all(x["horn_rule_count"]==0 for x in by_doc.values()),
        "adversarial_inline_proof_line":proofline,
        "adversarial_proof_context_status":proof_packet["context_status"],
        "proof_statement_allowed_as_quarantined_conclusion_evidence":proof_as_evidence,
        "context_protection_gate": "DEFECT_INLINE_PROOF_NOT_BLOCKED" if proof_as_evidence else "BLOCKED",
        "scientific_verdict":"INDETERMINATE_NOT_SEMANTICALLY_CHECKED",
        "interpretation":"Both documents are real held-out inputs selected before code. Readability and exact citations can be measured, but no generative model ran and no mathematical theorem was understood. A proof paragraph accepted as quoted claim evidence still remains unverified, but should be blocked proactively."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=evaluate()
    s=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:
        dest=a.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("write output outside repo")
        dest.write_text(s,encoding="utf-8")
    else:
        print(s,end="")


if __name__=="__main__":
    main()
