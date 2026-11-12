"""P5-EVID-04 — third-party ClaimDB annotations with strict witness provenance.

Only a small public CC BY-SA 4.0 sample is included. Dataset labels are
evaluator-only and NEVER constitute an executed database proof.
A separate, tightly scoped SQLite adapter tests actual query results against
an identified file hash. Two SQL computations on one DB do NOT count as two
independent evidence providers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1,sha256
import json
from pathlib import Path
import re
import sqlite3

SAMPLE=Path(__file__).resolve().with_name("evid04_claimdb_public_sample_36.json")
LABELS=("ENTAILED","CONTRADICTED","NOT ENOUGH INFO")
NEI_CATEGORIES=("OUT-OF-SCHEMA","COUNTERFACTUAL","SUBJECTIVE")
SOURCE_COMMIT="e06c3a22cc14a8ef6858bb5d40bca7925241b98d"
SOURCE_BLOB="a017545623508c0090cf2148716b8d26a6f8c337"
STATUS="REAL_THIRD_PARTY_ANNOTATIONS_PROVENANCE_ONLY_NO_WITNESS"
STRATA=(("ENTAILED",None,12),("CONTRADICTED",None,12),
        ("NOT ENOUGH INFO","OUT-OF-SCHEMA",4),
        ("NOT ENOUGH INFO","COUNTERFACTUAL",4),
        ("NOT ENOUGH INFO","SUBJECTIVE",4))


def _source_git_blob_sha(raw):
    """Exact Git blob hash, rather than guessing source content from a URL."""
    return sha1(f"blob {len(raw)}\0".encode("ascii")+raw).hexdigest()


def sample_rank(row):
    return (row["claim_id"]*2654435761+
            row["bird_id"]*1597334677)%(2**32)


def deterministic_sample(rows):
    chosen=[]
    seen=set()
    for label,category,n in STRATA:
        candidates=sorted((r for r in rows if r["label"]==label and
                       (category is None or r.get("category")==category)),
                       key=lambda r:(sample_rank(r),r["claim_id"]))
        taken=0
        for row in candidates:
            ident=(row["db_name"],row["bird_id"])
            if ident in seen:
                continue
            seen.add(ident)
            chosen.append({
                "claim_id":row["claim_id"],"bird_id":row["bird_id"],
                "db_name":row["db_name"],"claim":row["claim"],
                "extra_info":row.get("extra_info") or "",
                "annotated_label_evaluator_only":row["label"],
                "annotated_category_evaluator_only":row.get("category"),
                "independent_source_count":0,
                "observed_evidence_records":0,
            })
            taken+=1
            if taken==n:break
        if taken!=n:
            raise ValueError(f"stratum insufficient {label}/{category}: {taken}/{n}")
    if len(chosen)!=36:
        raise AssertionError("unexpected sample size")
    return chosen


def _load_sample(path=SAMPLE):
    snapshot=json.loads(Path(path).read_text(encoding="utf-8"))
    if snapshot.get("protocol")!="P5-EVID-04" or snapshot.get("status")!=STATUS:
        raise ValueError("unexpected dataset or status")
    source=snapshot["source"]
    if (source["commit"]!=SOURCE_COMMIT or source["git_blob_sha"]!=SOURCE_BLOB
            or source["license"]!="CC-BY-SA-4.0"):
        raise ValueError("unrecognized source commitment or license")
    rows=snapshot["cases"]
    if len(rows)!=36:
        raise ValueError("incorrect cohort size")
    if len(set(x["claim_id"] for x in rows))!=36:
        raise ValueError("duplicate claims")
    if len(set((x["db_name"],x["bird_id"]) for x in rows))!=36:
        raise ValueError("duplicate underlying questions")
    counts=Counter(r["annotated_label_evaluator_only"] for r in rows)
    if counts!={k:12 for k in LABELS}:
        raise ValueError("unbalanced label distribution")
    nei=Counter(r["annotated_category_evaluator_only"] for r in rows
                if r["annotated_label_evaluator_only"]=="NOT ENOUGH INFO")
    if nei!={k:4 for k in NEI_CATEGORIES}:
        raise ValueError("unbalanced NEI categories")
    if any(x["independent_source_count"]!=0 or
           x["observed_evidence_records"]!=0 for x in rows):
        raise ValueError("labels presented as evidence")
    if snapshot["selection"]["selected_count"]!=36:
        raise ValueError("selection manifest disagrees")
    return snapshot


def source_reproduction(original_path):
    """Recreate every selected field from the pinned 1000-line original."""
    snap=_load_sample()
    raw=Path(original_path).read_bytes()
    blob=_source_git_blob_sha(raw)
    if blob!=SOURCE_BLOB:
        raise ValueError("downloaded public source does not match pinned Git blob")
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows)!=1000:
        raise ValueError("source split is not exactly 1000 rows")
    reconstructed=deterministic_sample(rows)
    if reconstructed!=snap["cases"]:
        raise AssertionError("source sampling is not faithfully reproducible")
    return {
        "source_blob_verified":True,"source_records":len(rows),
        "source_sha256":sha256(raw).hexdigest(),
        "exact_sample_reproduced":True,
        "sample_cases":len(reconstructed),
    }


def policy_input(row):
    """Prevent any annotated label and category from reaching an evaluator."""
    expected={"claim_id","bird_id","db_name","claim","extra_info",
              "annotated_label_evaluator_only",
              "annotated_category_evaluator_only",
              "independent_source_count","observed_evidence_records"}
    if set(row)!=expected:
        raise ValueError("unexpected row schema")
    return {
        "claim_id":row["claim_id"],"bird_id":row["bird_id"],
        "db_name":row["db_name"],"claim":row["claim"],
        "extra_info":row["extra_info"],
    }


def decide_without_db(public_row,receipt=None):
    """No witness access => ABSTAIN, NOT ClaimDB's NOT ENOUGH INFO label."""
    if set(public_row)!={"claim_id","bird_id","db_name","claim","extra_info"}:
        raise ValueError("evaluator label leaked into policy")
    if receipt is not None:
        # A claimed result or raw label is never accepted as a proof. Only
        # execute_sql_witness() below is permitted to certify a local DB.
        raise ValueError("unexecuted receipt cannot be promoted")
    return {
        "action":"ABSTAIN_MISSING_EVIDENCE",
        "reason":"Database rows and reproducible SQL checks are not in this dataset",
        "calculated_label":None,"witness_count":0,
        "independent_provider_count":0,
    }


def _query_exact_boolean(connection,sql):
    """Execute one trusted read-only scalar query; fail closed on ambiguity."""
    if not isinstance(sql,str) or not re.match(r"^\s*SELECT\b",sql,re.I):
        raise ValueError("SQL witness must be a SELECT scalar")
    if ";" in sql or re.search(r"\b(ATTACH|DETACH|PRAGMA|UPDATE|INSERT|DELETE|DROP|ALTER)\b",
                                sql,re.I):
        raise ValueError("unsafe or compound SQL")
    rows=connection.execute(sql).fetchall()
    if len(rows)!=1 or len(rows[0])!=1:
        raise ValueError("non-scalar SQL result")
    result=rows[0][0]
    if result not in (0,1) or type(result) not in (int,bool):
        raise ValueError("SQL does not establish a Boolean verdict")
    return bool(result)


def execute_sql_witness(public_row,db_path,expected_sha256,sql_a,sql_b):
    """Tightly scoped demonstrator, with a real local DB; no invented facts.

    The SQL queries themselves must be supplied by a trusted verifier.
    Equal outputs establish procedural agreement on the SAME database,
    not independent providers, nor completeness for NOT ENOUGH INFO.
    """
    if set(public_row)!={"claim_id","bird_id","db_name","claim","extra_info"}:
        raise ValueError("label leak or invalid public row")
    p=Path(db_path).resolve(strict=True)
    if not p.is_file():
        raise ValueError("expected SQLite database file")
    digest=sha256(p.read_bytes()).hexdigest()
    if len(expected_sha256)!=64 or digest!=expected_sha256:
        raise ValueError("database changed since witness commitment")
    if not sql_a.strip() or not sql_b.strip() or sql_a.strip()==sql_b.strip():
        raise ValueError("two distinct query methods required")
    with sqlite3.connect(p.as_uri()+"?mode=ro",uri=True) as conn:
        conn.execute("PRAGMA query_only=ON")
        a=_query_exact_boolean(conn,sql_a)
        b=_query_exact_boolean(conn,sql_b)
    if a!=b:
        return {
            "status":"CONTRADICTORY_SQL_WITNESSES",
            "calculated_label":None,"db_sha256":digest,
            "independent_provider_count":1,"independent_method_count":2,
            "claim_semantics_independently_reviewed":False,
            "independent_fact_verification":False,
        }
    return {
        "status":"EXECUTED_SQL_AGREEMENT_SINGLE_DB_PROVIDER",
        # A SQL boolean is NOT a certified ClaimDB label unless a separate
        # reviewer has checked that BOTH queries express the natural-language
        # claim. A constant or irrelevant SELECT can agree without proving it.
        "calculated_label":"ENTAILED" if a else "CONTRADICTED",
        "claim_semantics_independently_reviewed":False,
        "independent_fact_verification":False,
        "db_sha256":digest,
        "sql_method_sha256":[sha256(x.encode()).hexdigest()
                             for x in (sql_a,sql_b)],
        "independent_provider_count":1,
        "independent_method_count":2,
        "limit":"Queries executed on one local DB; their correspondence to the claim is NOT validated",
    }


def audit():
    snap=_load_sample()
    actions=[decide_without_db(policy_input(row)) for row in snap["cases"]]
    return {
        "protocol":"P5-EVID-04","status":STATUS,
        "source_commit":SOURCE_COMMIT,"source_blob_sha":SOURCE_BLOB,
        "source_license":"CC-BY-SA-4.0",
        "annotated_claims":len(actions),
        "annotated_classes":dict(Counter(r["annotated_label_evaluator_only"]
                                         for r in snap["cases"])),
        "nei_subtypes":dict(Counter(r["annotated_category_evaluator_only"]
                                  for r in snap["cases"]
                                  if r["annotated_label_evaluator_only"]=="NOT ENOUGH INFO")),
        "underlying_databases":len(set(r["db_name"] for r in snap["cases"])),
        "unique_underlying_questions":len(set((r["db_name"],r["bird_id"])
                                             for r in snap["cases"])),
        "actual_sql_queries_executed_on_claimdb_databases":0,
        "reproduced_independent_verdicts":0,
        "abstain_missing_evidence":sum(x["action"]=="ABSTAIN_MISSING_EVIDENCE"
                                       for x in actions),
        "claimdb_nei_is_not_policy_abstention":True,
        "has_source_db_rows":False,
        "has_trusted_sql_witness":False,
        "limitations":[
            "Public ACL 2026 third-party annotations, not an independent test split",
            "No ClaimDB underlying BIRD source database downloaded or executed",
            "Labels and extra_info are not verification evidence",
            "No measured agent accuracy, no Omega superiority claim",
            "SQLite execution adapter tested only on local synthetic fixture",
            "ClaimDB public license requires attribution and share-alike",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,help="Original pinned ClaimDB test-public.jsonl")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    x=audit()
    if args.source:
        x["source_reproduction"]=source_reproduction(args.source)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(x,ensure_ascii=False,indent=2,
                                          sort_keys=True)+"\n",encoding="utf-8")
    print("EVID04_CLAIMDB_PROVENANCE",json.dumps(x,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
