"""P5-EVID-06: three NEW ClaimDB sentences executed on real BIRD superhero.

Manually authored, preregistered SQL. Comparisons use independent SQL forms
on the SAME database. No claim of independent semantic review or truth source.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import json

from p5_evid05_bird_sql import check_source,_conn,schema_check,_query
from p5_evid06_budgeted_routing import FILES,_read

SENTINELS=(15601,3730,3971)
SQL={
 15601:{
  "semantics":"exactly 40 distinct heroes have the maximal Speed attribute score",
  "sql_a":"""SELECT COUNT(DISTINCT ha.hero_id)=40 FROM hero_attribute ha
    JOIN attribute a ON a.id=ha.attribute_id
    WHERE lower(trim(a.attribute_name))='speed'
      AND ha.attribute_value=(SELECT MAX(v.attribute_value) FROM
          hero_attribute v JOIN attribute av ON av.id=v.attribute_id
          WHERE lower(trim(av.attribute_name))='speed')""",
  "sql_b":"""SELECT (SELECT COUNT(DISTINCT hero_id) FROM hero_attribute
    WHERE attribute_id IN (SELECT id FROM attribute
                           WHERE lower(trim(attribute_name))='speed')
      AND attribute_value=(SELECT MAX(attribute_value) FROM hero_attribute
        WHERE attribute_id IN (SELECT id FROM attribute
                               WHERE lower(trim(attribute_name))='speed')))=40
    FROM attribute LIMIT 1""",
  "count":"""SELECT COUNT(DISTINCT ha.hero_id) FROM hero_attribute ha
    JOIN attribute a ON a.id=ha.attribute_id
    WHERE lower(trim(a.attribute_name))='speed'
      AND ha.attribute_value=(SELECT MAX(v.attribute_value) FROM
          hero_attribute v JOIN attribute av ON av.id=v.attribute_id
          WHERE lower(trim(av.attribute_name))='speed')""",
  "other":"""SELECT MAX(ha.attribute_value) FROM hero_attribute ha
    JOIN attribute a ON a.id=ha.attribute_id
    WHERE lower(trim(a.attribute_name))='speed'""",
  "witness":"""SELECT s.id,s.superhero_name,ha.attribute_value FROM superhero s
    JOIN hero_attribute ha ON ha.hero_id=s.id JOIN attribute a
    ON a.id=ha.attribute_id WHERE lower(trim(a.attribute_name))='speed'
    AND ha.attribute_value=(SELECT MAX(x.attribute_value) FROM
      hero_attribute x JOIN attribute ax ON x.attribute_id=ax.id
      WHERE lower(trim(ax.attribute_name))='speed')
    ORDER BY s.id LIMIT 3""",
  "true_label":"ENTAILED","false_label":"CONTRADICTED",
 },
 3730:{
  "semantics":"exactly 42 distinct superheroes with Super Strength power exceed 200 cm",
  "sql_a":"""SELECT COUNT(DISTINCT s.id)=42 FROM superhero s
    JOIN hero_power hp ON hp.hero_id=s.id
    JOIN superpower p ON p.id=hp.power_id
    WHERE lower(trim(p.power_name))='super strength' AND s.height_cm>200""",
  "sql_b":"""SELECT COUNT(*)=42 FROM superhero
    WHERE height_cm>200 AND id IN (SELECT hp.hero_id FROM hero_power hp
    WHERE hp.power_id IN (SELECT id FROM superpower
    WHERE lower(trim(power_name))='super strength'))""",
  "count":"""SELECT COUNT(DISTINCT s.id) FROM superhero s
    JOIN hero_power hp ON hp.hero_id=s.id JOIN superpower p
    ON p.id=hp.power_id WHERE lower(trim(p.power_name))='super strength'
    AND s.height_cm>200""",
  "witness":"""SELECT DISTINCT s.id,s.superhero_name,s.height_cm FROM superhero s
    JOIN hero_power hp ON hp.hero_id=s.id JOIN superpower p
    ON p.id=hp.power_id WHERE lower(trim(p.power_name))='super strength'
    AND s.height_cm>200 ORDER BY s.id LIMIT 3""",
  "true_label":"ENTAILED","false_label":"CONTRADICTED",
 },
 3971:{
  "semantics":"Invisibility has more distinct heroes than Super Strength (necessary not sufficient for globally most widespread)",
  "sql_a":"""SELECT
     (SELECT COUNT(DISTINCT hp.hero_id) FROM hero_power hp
      JOIN superpower p ON p.id=hp.power_id
      WHERE lower(trim(p.power_name))='invisibility') >
     (SELECT COUNT(DISTINCT hp.hero_id) FROM hero_power hp
      JOIN superpower p ON p.id=hp.power_id
      WHERE lower(trim(p.power_name))='super strength')
     FROM superpower LIMIT 1""",
  "sql_b":"""SELECT
     (SELECT COUNT(DISTINCT hero_id) FROM hero_power
      WHERE power_id IN (SELECT id FROM superpower
                         WHERE lower(trim(power_name))='invisibility')) >
     (SELECT COUNT(DISTINCT hero_id) FROM hero_power
      WHERE power_id IN (SELECT id FROM superpower
                         WHERE lower(trim(power_name))='super strength'))
     FROM superpower LIMIT 1""",
  "counts":"""SELECT p.power_name,COUNT(DISTINCT hp.hero_id) AS heroes
     FROM superpower p JOIN hero_power hp ON hp.power_id=p.id
     WHERE lower(trim(p.power_name)) IN ('invisibility','super strength')
     GROUP BY p.power_name ORDER BY lower(trim(p.power_name))""",
  "global_top":"""SELECT p.power_name,COUNT(DISTINCT hp.hero_id) AS heroes
     FROM superpower p JOIN hero_power hp ON p.id=hp.power_id
     GROUP BY p.id,p.power_name ORDER BY heroes DESC, p.power_name ASC LIMIT 3""",
  "true_label":None, # Need global-most-widespread condition, not pairwise only.
  "false_label":"CONTRADICTED", # A failed necessary comparison refutes entire claim.
 },
}


def _value(conn,sql,kind="bool"):
    if kind=="bool":
        return _query(conn,sql,"bool")
    if kind=="count":
        return _query(conn,sql,"count")
    return _query(conn,sql)


def verify_source_claims(path):
    maps,_=_read(path,FILES["gold"][1])
    rows=[]
    for claim_id in SENTINELS:
        row=maps[claim_id]
        if row["db_name"]!="superhero":
            raise ValueError("new sentinel sourced from wrong database")
        rows.append({
            "claim_id":claim_id,"claim":row["claim"],
            "extra_info":row.get("extra_info") or "",
            "annotation_evaluator_only":row["label"],
            "db_name":row["db_name"],
        })
    return rows


def run(db_path,gold_path):
    source=check_source(db_path)
    claims=verify_source_claims(gold_path)
    with _conn(db_path) as conn:
        schema=schema_check(conn)
        # Verify every additional relation needed by the new claims.
        for table,fields in {
            "hero_attribute":{"hero_id","attribute_id","attribute_value"},
            "attribute":{"id","attribute_name"},
            "hero_power":{"hero_id","power_id"},
            "superpower":{"id","power_name"},
        }.items():
            got={x[1] for x in conn.execute(f"PRAGMA table_info({table})")}
            if not fields<=got:
                raise ValueError(f"STOP_SCHEMA_OR_QUERY_MISMATCH: {table}")
        output=[]
        for row in claims:
            entry=SQL[row["claim_id"]]
            a=_value(conn,entry["sql_a"])
            b=_value(conn,entry["sql_b"])
            if a!=b:
                decision="ABSTAIN_METHOD_CONFLICT"
            elif not a:
                decision="CONTRADICTED"
            elif entry["true_label"] is None:
                decision="ABSTAIN_INSUFFICIENT_GLOBAL_PREVALENCE_CHECK"
            else:
                decision="ENTAILED"
            other={}
            for name in ("count","other"):
                if name in entry:
                    other[name]=_value(conn,entry[name],"count")
            for name in ("witness","counts","global_top"):
                if name in entry:
                    # Only the supplied text of these read-only queries executes.
                    from p5_evid05_bird_sql import select_only
                    sql=select_only(entry[name])
                    extra=conn.execute(sql).fetchall()
                    if name=="witness":
                        other[name]=[list(x) for x in extra[:3]]
                    else:
                        other[name]=[list(x) for x in extra[:4]]
            # WITNESS CHECK for positive existence: an affirmative statement
            # with no sample witnesses must not be promoted silently.
            if row["claim_id"]==15601 and a and not other["witness"]:
                decision="ABSTAIN_MISSING_POSITIVE_WITNESS"
            # Pairwise failure refutes "most widespread" regardless of
            # unexamined powers; pairwise success alone would not prove it.
            output.append({
                "claim_id":row["claim_id"],"claim":row["claim"],
                "external_annotation_evaluator_only":row["annotation_evaluator_only"],
                "predicate":entry["semantics"],
                "sql_a":entry["sql_a"],"sql_b":entry["sql_b"],
                "sql_a_result":a,"sql_b_result":b,
                "methods_agree":a==b,
                "extra_evidence":other,
                "provenance":"real BIRD SQLite; 1 data provider; 2 SQL formulations",
                "independent_semantic_review":False,
                "certified_clause_only":True,
                "decision":decision,
                "matches_external_annotation_if_published":
                    decision==row["annotation_evaluator_only"]
                    if decision in ("ENTAILED","CONTRADICTED") else None,
            })
    return {
      "protocol":"P5-EVID-06-BIRD-3",
      "status":"REAL_BIRD_SQL_THREE_NEW_PRESELECTED_SENTINELS_INTERNAL_SEMANTICS_ONLY",
      "db_source":source,
      "db_schema":schema,
      "one_provider_not_independent":True,
      "new_sql_cases":len(output),
      "methods_agree_all":all(x["methods_agree"] for x in output),
      "independently_semantically_reviewed_count":0,
      "published":sum(x["decision"] in ("ENTAILED","CONTRADICTED") for x in output),
      "matched_external_annotations":sum(x["matches_external_annotation_if_published"] is True for x in output),
      "cases":output,
      "limitations":[
          "Original ClaimDB labels available before selecting these specific IDs",
          "New hand-authored SQL not reviewed by an external human adjudicator",
          "The same real BIRD DB is queried twice; no independent data provider",
          "No evidence of adaptive Omega learning or performance advantage",
          "The universal 'most common' condition is stronger than pairwise comparison",
      ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--database",type=Path,required=True)
    p.add_argument("--claimdb-original",type=Path,required=True)
    p.add_argument("--output",type=Path)
    opt=p.parse_args()
    result=run(opt.database,opt.claimdb_original)
    if opt.output:
        opt.output.parent.mkdir(parents=True,exist_ok=True)
        opt.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                                         indent=2)+"\n",encoding="utf-8")
    print("EVID06_NEW_BIRD_SQL",json.dumps({
      "status":result["status"],"new_cases":result["new_sql_cases"],
      "methods_agree_all":result["methods_agree_all"],
      "published":result["published"],
      "matched":result["matched_external_annotations"],
      "cases":[{"id":c["claim_id"],"predicate":c["predicate"],
         "sql_a":c["sql_a_result"],"sql_b":c["sql_b_result"],
         "evidence":c["extra_evidence"],"decision":c["decision"],
         "annotation":c["external_annotation_evaluator_only"]}
        for c in result["cases"]],
    },ensure_ascii=False,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
