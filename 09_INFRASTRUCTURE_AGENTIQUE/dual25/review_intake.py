#!/usr/bin/env python3
"""DUAL25 independent human review intake schema -- never auto-certifies humans.

Produces a blank review form from the blind-within-packet source documents.
Even two complete form submissions DO NOT establish reviewer independence or
true source meaning without manual identity, provenance and conflict audit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ALLOWED = {"DETERMINATE","AMBIGUOUS","CONTEXT_INSUFFICIENT","OUT_OF_SCOPE"}


def source_digest(record:dict)->str:
    if record["kind"]=="AUTHOR_DESIGNED_MATH_CONTRACT_NOT_NEW_HUMAN_SOURCE":
        return record["source_git_blob"]
    return record["quote_sha256"]


def build_blank_template(packet:dict)->dict:
    if (packet.get("human_annotation_status")!="PENDING_NOT_PERFORMED"
        or packet.get("source_count")!=42):
        raise ValueError("NOT_A_FROZEN_REVIEW_PACKET")
    return {
        "submission_status":"NOT_STARTED_NO_HUMAN_LABELS",
        "reviewer_pseudonym":"",
        "reviewer_declares_independence":None,
        "reviewer_saw_formalizer_outputs":None,
        "reviewer_notes":"",
        "instructions":"Provide your own interpretation from the original source, not model outputs. Do not claim a short fragment supplies full context. This form does not prove independence.",
        "labels":[{
            "id":item["id"],
            "source_digest":source_digest(item),
            "human_decision":"NOT_REVIEWED",
            "typed_definition":None,
            "typed_claim":None,
            "reasoning_citation_from_source":None,
            "ambiguity_notes":None,
        } for item in packet["items"]],
    }


def validate_submission_schema(packet:dict,form:dict)->dict:
    """Schema/provenance check only. Human identity and fidelity remain unknown."""
    originals={x["id"]:x for x in packet["items"]}
    if (packet["source_count"]!=42 or len(originals)!=42
        or not isinstance(form,dict)
        or not isinstance(form.get("labels"),list)
        or len(form["labels"])!=42):
        raise ValueError("INCOMPLETE_REVIEW_FORM_OR_PACKET")
    reviewer=form.get("reviewer_pseudonym")
    if (not isinstance(reviewer,str)
        or not re.fullmatch(r"[A-Za-z0-9_-]{4,80}",reviewer)
        or form.get("reviewer_declares_independence") is not True
        or form.get("reviewer_saw_formalizer_outputs") is not False):
        raise ValueError("REVIEWER_ATTESTATIONS_MISSING")
    seen=set()
    decisions={}
    for label in form["labels"]:
        if not isinstance(label,dict) or set(label)!={
            "id","source_digest","human_decision",
            "typed_definition","typed_claim",
            "reasoning_citation_from_source","ambiguity_notes",
        }:
            raise ValueError("UNSUPPORTED_ANNOTATION_FIELDS")
        ident=label["id"]
        if ident not in originals or ident in seen:
            raise ValueError("DUPLICATE_OR_UNKNOWN_REVIEW_ID")
        seen.add(ident)
        original=originals[ident]
        if label["source_digest"]!=source_digest(original):
            raise ValueError("REVIEW_SOURCE_DIGEST_MISMATCH")
        choice=label["human_decision"]
        if choice not in ALLOWED:
            raise ValueError("NOT_AN_ANNOTATED_DECISION")
        cite=label["reasoning_citation_from_source"]
        source_text=original.get("source_text_original",original.get("literal_quote",""))
        if not isinstance(cite,str) or not 3<=len(cite)<=300 or cite not in source_text:
            raise ValueError("HUMAN_CITATION_NOT_IN_SOURCE")
        if choice=="DETERMINATE" and not (
            isinstance(label["typed_definition"],dict) and
            isinstance(label["typed_claim"],dict)
        ):
            raise ValueError("DETERMINATE_REVIEW_WITHOUT_TYPED_MEANING")
        if choice=="AMBIGUOUS" and not (
            isinstance(label["ambiguity_notes"],str)
            and len(label["ambiguity_notes"].strip())>=12
        ):
            raise ValueError("AMBIGUOUS_REVIEW_WITHOUT_EXPLANATION")
        decisions[ident]=choice
    return {
        "status":"SUBMISSION_SCHEMA_VALID_INDEPENDENCE_NOT_AUTHENTICATED",
        "reviewer_pseudonym":reviewer,
        "labels_count":len(seen),
        "decisions":decisions,
        "independent_reviewer_identity_verified":False,
        "human_fidelity_metrics_certified":False,
        "automatic_promotions":0,
    }


def validate_two_reviews(packet:dict,first:dict,second:dict)->dict:
    a=validate_submission_schema(packet,first)
    b=validate_submission_schema(packet,second)
    if a["reviewer_pseudonym"]==b["reviewer_pseudonym"]:
        raise ValueError("BOTH_HUMAN_REVIEWS_HAVE_SAME_PSEUDONYM")
    disagreements=[ident for ident in a["decisions"]
                   if a["decisions"][ident]!=b["decisions"][ident]]
    return {
        "status":"TWO_REVIEW_SCHEMAS_ACCEPTED_MANUAL_ADJUDICATION_REQUIRED",
        "n_annotated":42,"n_decision_disagreements":len(disagreements),
        "disagreements":disagreements,
        "actual_human_identity_independence_verified":False,
        "human_semantic_fidelity_estimate":None,
        "certifications":0,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--packet",type=Path,required=True)
    parser.add_argument("--blank-form",type=Path,required=True)
    parser.add_argument("--status",type=Path,required=True)
    args=parser.parse_args()
    packet=json.loads(args.packet.read_text(encoding="utf8"))
    blank=build_blank_template(packet)
    args.blank_form.write_text(json.dumps(blank,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    status={
        "status":"PENDING_INDEPENDENT_HUMAN_ANNOTATIONS",
        "new_complete_external_holdout":"NOT_YET_COLLECTED",
        "human_semantic_fidelity_estimate":None,
        "human_annotations_submitted":0,
        "review_packet_size":packet["source_count"],
        "auto_certifications":0,
    }
    args.status.write_text(json.dumps(status,indent=2)+"\n",encoding="utf8")
    print("HUMAN_REVIEW",status["status"],flush=True)


if __name__=="__main__":
    main()
