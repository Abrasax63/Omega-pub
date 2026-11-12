"""P5-EVID-05 — authentic BIRD SQLite / external ClaimDB assertion checking.

Five hand-selected public ClaimDB claims, TWO equivalent SQL computations per
testable predicate. The dataset labels are NEVER passed to query execution.
One SQLite file = ONE data provider. 4 SQL-verifiable fragments + 1 counterfactual.
This is exploratory and *not* a verified independent ClaimDB benchmark.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1,sha256
import json
from pathlib import Path
import re
import sqlite3

HERE=Path(__file__).resolve().parent
FROZEN=HERE/"evid05_claimdb_5_preselected.json"
PROTOCOL="P5-EVID-05"
STATUS="REAL_BIRD_SQL_REPLAY_EXPLORATORY_SINGLE_PROVIDER"
DB_SHA256="75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1"
DB_GIT_BLOB="4cfbee0ba8b6033a7415184caff90d363fe444c2"
DB_SIZE=237568
CLAIMDB_SOURCE_BLOB="a017545623508c0090cf2148716b8d26a6f8c337"
REQUIRED_SCHEMA={
    "superhero":("id","superhero_name","full_name","gender_id","hair_colour_id",
                "race_id","publisher_id","height_cm"),
    "gender":("id","gender"),
    "colour":("id","colour"),
    "race":("id","race"),
    "publisher":("id","publisher_name"),
}
CLAIM_IDS=(4267,4179,4324,3930,4419)

# Written before executing the public BIRD SQLite database. Every pair is
# expected to answer the SAME precisely stated predicate, not necessarily
# the entire natural-language claim.
SQL={
4267:{
 "semantics":"EXISTS blue-haired male superhero classified exactly as Mutant",
 "a":"""SELECT EXISTS (SELECT 1 FROM superhero s
          JOIN gender g ON g.id=s.gender_id
          JOIN colour h ON h.id=s.hair_colour_id
          JOIN race r ON r.id=s.race_id
          WHERE lower(trim(g.gender))='male'
            AND lower(trim(h.colour))='blue'
            AND lower(trim(r.race))='mutant')""",
 "b":"""SELECT COUNT(*) > 0 FROM superhero
          WHERE gender_id IN (SELECT id FROM gender WHERE lower(trim(gender))='male')
            AND hair_colour_id IN (SELECT id FROM colour WHERE lower(trim(colour))='blue')
            AND race_id IN (SELECT id FROM race WHERE lower(trim(race))='mutant')""",
 "witness":"""SELECT s.id,s.superhero_name FROM superhero s
          JOIN gender g ON g.id=s.gender_id
          JOIN colour h ON h.id=s.hair_colour_id
          JOIN race r ON r.id=s.race_id
          WHERE lower(trim(g.gender))='male' AND lower(trim(h.colour))='blue'
            AND lower(trim(r.race))='mutant' ORDER BY s.id LIMIT 3""",
 "true_label":"ENTAILED","false_label":"CONTRADICTED",
},
4179:{
 "semantics":"NATURAL no publisher = NULL, no valid FK, or blank/N/A/Unknown/None publisher name",
 "a":"""SELECT EXISTS (SELECT 1 FROM superhero s
          LEFT JOIN publisher p ON p.id=s.publisher_id
          WHERE s.publisher_id IS NULL OR p.id IS NULL
            OR lower(trim(coalesce(p.publisher_name,''))) IN ('','n/a','unknown','none'))""",
 "b":"""SELECT COUNT(*) > 0 FROM superhero s
          WHERE s.publisher_id IS NULL
          OR s.publisher_id NOT IN (SELECT id FROM publisher WHERE id IS NOT NULL)
          OR s.publisher_id IN (SELECT id FROM publisher
               WHERE lower(trim(coalesce(publisher_name,''))) IN ('','n/a','unknown','none'))""",
 "witness":"""SELECT s.id,s.superhero_name,s.publisher_id,p.publisher_name
          FROM superhero s LEFT JOIN publisher p ON p.id=s.publisher_id
          WHERE s.publisher_id IS NULL OR p.id IS NULL
            OR lower(trim(coalesce(p.publisher_name,''))) IN ('','n/a','unknown','none')
          ORDER BY s.id LIMIT 3""",
 "true_label":"CONTRADICTED","false_label":"ENTAILED",
},
4324:{
 "semantics":"Exactly 111 female superheroes whose publisher is Marvel Comics",
 "a":"""SELECT COUNT(*)=111 FROM superhero s
          JOIN publisher p ON p.id=s.publisher_id
          JOIN gender g ON g.id=s.gender_id
          WHERE lower(trim(p.publisher_name))='marvel comics'
            AND lower(trim(g.gender))='female'""",
 "b":"""SELECT (SELECT COUNT(*) FROM superhero
          WHERE publisher_id IN (SELECT id FROM publisher
                                 WHERE lower(trim(publisher_name))='marvel comics')
            AND gender_id IN (SELECT id FROM gender WHERE lower(trim(gender))='female'))=111""",
 "count":"""SELECT COUNT(*) FROM superhero s JOIN publisher p ON p.id=s.publisher_id
          JOIN gender g ON g.id=s.gender_id
          WHERE lower(trim(p.publisher_name))='marvel comics'
            AND lower(trim(g.gender))='female'""",
 "true_label":"ENTAILED","false_label":"CONTRADICTED",
},
3930:{
 "semantics":"COUNTEREXAMPLE EXISTS Human superhero exactly 185cm tall",
 "a":"""SELECT EXISTS (SELECT 1 FROM superhero s JOIN race r ON r.id=s.race_id
          WHERE lower(trim(r.race))='human' AND s.height_cm=185)""",
 "b":"""SELECT COUNT(*)>0 FROM superhero
          WHERE height_cm=185 AND race_id IN (
             SELECT id FROM race WHERE lower(trim(race))='human')""",
 "witness":"""SELECT s.id,s.superhero_name,s.height_cm,h.colour
          FROM superhero s JOIN race r ON r.id=s.race_id
          LEFT JOIN colour h ON h.id=s.hair_colour_id
          WHERE lower(trim(r.race))='human' AND s.height_cm=185
          ORDER BY s.id LIMIT 3""",
 "true_label":"CONTRADICTED",
 "false_label":None,  # False cannot settle the second causal hair-colour clause.
},
# No code for 4419. The dataset text is a COUNTERFACTUAL; do not infer its
# outcome from an ordinary SELECT and do not map it to NOT ENOUGH INFO by oracle.
}
PUB_4179={
 "semantics":"ClaimDB extra_info convention: no publisher means publisher.id=1",
 "a":"""SELECT EXISTS(SELECT 1 FROM superhero s JOIN publisher p
          ON s.publisher_id=p.id WHERE p.id=1)""",
 "b":"""SELECT COUNT(*)>0 FROM superhero WHERE publisher_id IN
          (SELECT id FROM publisher WHERE id=1)""",
 "witness":"""SELECT s.id,s.superhero_name,p.id,p.publisher_name
          FROM superhero s JOIN publisher p ON s.publisher_id=p.id
          WHERE p.id=1 ORDER BY s.id LIMIT 3""",
}


def git_blob_sha(raw):
    return sha1(f"blob {len(raw)}\0".encode("ascii")+raw).hexdigest()


def check_source(db_path):
    p=Path(db_path).resolve(strict=True)
    data=p.read_bytes()
    if len(data)!=DB_SIZE or sha256(data).hexdigest()!=DB_SHA256 or git_blob_sha(data)!=DB_GIT_BLOB:
        raise ValueError("STOP_SOURCE_UNVERIFIED: BIRD binary size/SHA256/Git blob differ")
    return {
        "path_not_redistributed":p.name,
        "size":len(data),"sha256":sha256(data).hexdigest(),
        "git_blob_sha1":git_blob_sha(data),
    }


def select_only(sql):
    if not isinstance(sql,str) or not re.match(r"^\s*SELECT\b",sql,re.I):
        raise ValueError("SQL must be read-only SELECT")
    if ";" in sql or re.search(
        r"\b(ATTACH|DETACH|PRAGMA|INSERT|UPDATE|DELETE|DROP|ALTER|VACUUM|REPLACE)\b",sql,re.I
    ):
        raise ValueError("unsafe SQL")
    if not re.search(r"\bFROM\b",sql,re.I):
        raise ValueError("no source table for SQL claim witness")
    return sql


def _query(conn,sql,rows_expected=None):
    sql=select_only(sql)
    # SQL templates are the only inputs; do NOT send claim text as a SQL fragment.
    rows=conn.execute(sql).fetchall()
    if rows_expected=="bool":
        if len(rows)!=1 or len(rows[0])!=1 or type(rows[0][0]) is not int or rows[0][0] not in (0,1):
            raise ValueError("not exactly one Boolean SQL result")
        return bool(rows[0][0])
    if rows_expected=="count":
        if len(rows)!=1 or len(rows[0])!=1 or type(rows[0][0]) is not int:
            raise ValueError("invalid count")
        return rows[0][0]
    if len(rows)>3:
        raise ValueError("witness projection must be LIMIT 3")
    return [list(row) for row in rows]


def _conn(db_path):
    p=Path(db_path).resolve(strict=True)
    con=sqlite3.connect(p.as_uri()+"?mode=ro&immutable=1",uri=True)
    con.execute("PRAGMA query_only=ON")
    return con


def schema_check(conn):
    result={}
    for table,cols in REQUIRED_SCHEMA.items():
        found={r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        missing=set(cols)-found
        if missing:
            raise ValueError(f"STOP_SCHEMA_OR_QUERY_MISMATCH {table}: {sorted(missing)}")
        result[table]=sorted(found)
    n=conn.execute("SELECT COUNT(*) FROM superhero").fetchone()[0]
    if n<100:
        raise ValueError("unexpectedly incomplete real BIRD superhero database")
    return {"tables_verified":len(result),"schema":result,"superhero_rows":n}


def _exercise(conn,entry):
    a=_query(conn,entry["a"],"bool")
    b=_query(conn,entry["b"],"bool")
    witness=_query(conn,entry["witness"]) if a and "witness" in entry else []
    count=_query(conn,entry["count"],"count") if "count" in entry else None
    return {
        "predicate":entry["semantics"],"method_join":a,
        "method_subquery":b,"two_methods_agree":a==b,
        "supporting_rows_top3":witness,
        "reported_count":count,
        "sql_join":entry["a"].strip(),
        "sql_subquery":entry["b"].strip(),
        "sql_hashes":[sha256(entry[k].encode()).hexdigest() for k in ("a","b")],
        "witness_query":entry.get("witness"),
        "count_query":entry.get("count"),
        "single_data_provider":"BIRD superhero SQLite",
        "independent_data_provider_count":1,
        "independent_semantic_review":False,
    }


def _load_claims(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if (obj["protocol"]!=PROTOCOL or obj["git_blob_sha"]!=CLAIMDB_SOURCE_BLOB
        or [x["claim_id"] for x in obj["cases"]]!=list(CLAIM_IDS)
        or any(x["db_name"]!="superhero" for x in obj["cases"])):
        raise ValueError("ClaimDB cohort changed")
    return obj["cases"]


def claimdb_source_verify(source_path,claims):
    raw=Path(source_path).read_bytes()
    if git_blob_sha(raw)!=CLAIMDB_SOURCE_BLOB:
        raise ValueError("ClaimDB source unverified")
    original={x["claim_id"]:x for line in raw.splitlines() if line.strip()
              for x in (json.loads(line),)
              if x["claim_id"] in CLAIM_IDS}
    if len(original)!=5:
        raise ValueError("missing source claims")
    for case in claims:
        orig=original[case["claim_id"]]
        for a,b in (
            ("claim","claim"),("extra_info","extra_info"),
            ("bird_id","bird_id"),("db_name","db_name"),
            ("label_evaluator_only","label"),
        ):
            if case[a]!=orig.get(b):
                raise ValueError(f"ClaimDB source mismatch {case['claim_id']} {a}")
    return {"verified":True,"git_blob_sha1":CLAIMDB_SOURCE_BLOB,
            "five_claims_exactly_reproduced":True,
            "source_records":len(raw.splitlines())}


def _interpret(case_id,primary,alternative=None):
    """All labels generated from SQL truth; NEVER read ClaimDB label."""
    if case_id==4419:
        return {
            "single_sql_method":"ABSTAIN_MISSING_OBSERVABLE_COUNTERFACTUAL",
            "two_sql_agreement":"ABSTAIN_MISSING_OBSERVABLE_COUNTERFACTUAL",
            "omega_provenance_gate":"ABSTAIN_MISSING_OBSERVABLE_COUNTERFACTUAL",
        }
    if not primary["two_methods_agree"]:
        return {"single_sql_method":_mapped_label(case_id,primary["method_join"]),
                "two_sql_agreement":"ABSTAIN_METHOD_CONFLICT",
                "omega_provenance_gate":"ABSTAIN_METHOD_CONFLICT"}
    mapped=_mapped_label(case_id,primary["method_join"])
    out={"single_sql_method":mapped,"two_sql_agreement":mapped,
         "omega_provenance_gate":mapped}
    if case_id==4179:
        # Explicit source semantics are different from the preregistered
        # natural reading. Do not choose whichever score is higher.
        out["omega_provenance_gate"]="ABSTAIN_SEMANTIC_CONVENTION"
    if case_id==3930 and not primary["method_join"]:
        out["omega_provenance_gate"]="ABSTAIN_UNTESTED_CAUSAL_HAIR_CLAUSE"
    if case_id in (4267,3930) and primary["method_join"]:
        if not primary["supporting_rows_top3"]:
            out["omega_provenance_gate"]="ABSTAIN_NO_POSITIVE_WITNESS"
    return out


def _mapped_label(case_id,truth):
    if case_id==4419:
        raise ValueError("no SQL mapping for counterfactual")
    return SQL[case_id]["true_label"] if truth else (
        SQL[case_id]["false_label"] or "ABSTAIN_PARTIAL_CLAIM")


def run(db_path,claimdb_original):
    source=check_source(db_path)
    claims=_load_claims(FROZEN)
    origin=claimdb_source_verify(claimdb_original,claims)
    with _conn(db_path) as conn:
        schema=schema_check(conn)
        result=[]
        for claim in claims:
            key=claim["claim_id"]
            primary=_exercise(conn,SQL[key]) if key in SQL else None
            alternative=_exercise(conn,PUB_4179) if key==4179 else None
            decisions=_interpret(key,primary,alternative)
            # The reference label is loaded only AFTER the SQL decisions.
            result.append({
                "claim_id":key,
                "claim":claim["claim"],
                "external_annotation_evaluator_only":claim["label_evaluator_only"],
                "claimdb_extra_info_evaluator_only":claim["extra_info"],
                "executed":primary is not None,
                "primary":primary,"extra_info_convention_4179":alternative,
                "policies":decisions,
                "procedural_review":"author_predefined_not_independently_reviewed",
                "source_db_validated":True,
            })
    by_policy={}
    for policy in ("single_sql_method","two_sql_agreement","omega_provenance_gate"):
        values=[r["policies"][policy] for r in result]
        supported=[(r,v) for r,v in zip(result,values) if v in (
            "ENTAILED","CONTRADICTED","NOT ENOUGH INFO")]
        by_policy[policy]={
            "published":len(supported),"abstained":len(result)-len(supported),
            "agreement_with_external_annotation_not_independent_accuracy":
                sum(r["external_annotation_evaluator_only"]==value
                    for r,value in supported),
            "decisions":[{"id":r["claim_id"],"decision":v}
                         for r,v in zip(result,values)],
        }
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "db_source":source,"db_schema_check":schema,
        "claimdb_source":origin,
        "selected_cases":len(result),
        "executed_real_db_claims":sum(r["executed"] for r in result),
        "counterfactual_abstentions":sum(not r["executed"] for r in result),
        "two_method_conflicts":sum(r["primary"] is not None and
                                    not r["primary"]["two_methods_agree"] for r in result),
        "single_provider_count":1,"independent_external_fact_verifications":0,
        "claim_semantics_independently_reviewed":False,
        "all_cases":result,"policy_results":by_policy,
        "limitations":[
            "All claims hand-selected AFTER their public labels were known; no blind evaluation",
            "Only a pinned rehost of an authentic BIRD development SQLite file was executed",
            "Two SQL formulations on one DB are NOT two independent data providers",
            "Query-to-English semantic correspondence has not been independently reviewed",
            "ClaimDB publisher.id=1 convention differs from NULL/N/A natural reading",
            "Composite 185cm Human claim checked only for its falsifying existence",
            "No learned selection or multi-agent execution by Omega/P1",
            "No population-level conclusions from five hand-selected claims",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--database",required=True,type=Path)
    p.add_argument("--claimdb-original",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=run(args.database,args.claimdb_original)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print("EVID05_REAL_SQL",json.dumps({
        "status":report["status"],
        "db_sha256":report["db_source"]["sha256"],
        "executed":report["executed_real_db_claims"],
        "two_method_conflicts":report["two_method_conflicts"],
        "policies":report["policy_results"],
        "evidence":[{"id":x["claim_id"],
                     "sql_a":x["primary"]["method_join"] if x["primary"] else None,
                     "sql_b":x["primary"]["method_subquery"] if x["primary"] else None,
                     "witness":x["primary"]["supporting_rows_top3"] if x["primary"] else [],
                     "label":x["external_annotation_evaluator_only"],
                     "omega":x["policies"]["omega_provenance_gate"],
                     "alternate_4179":x["extra_info_convention_4179"] and x["extra_info_convention_4179"]["method_join"]}
                    for x in report["all_cases"]],
    },ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
