#!/usr/bin/env python3
import sqlite3,json,hashlib,shutil,sys,os
from pathlib import Path
from datetime import datetime,timezone

DB=Path("/mnt/data/ravi13_work/RESEARCH_MEMORY.sqlite")
BACKUP=Path("/mnt/data/ravi13_work/RESEARCH_MEMORY_PRE_TREE_CORE.sqlite")
REPORT=Path("/mnt/data/ravi13_work/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md")
ARCHIVE=Path("/mnt/data/ravi13_work/PREUVES_AFFINE_TREE_CORE_BRIDGE_2026-10-16.zip")
RESULTS=Path("/mnt/data/ravi13_work/AFFINE_TREE_CORE_BRIDGE_RESULTS_2026-10-16.json")
BRICK=Path("/mnt/data/ravi13_work/BR-AFFINE-TREE-CORE_BRIQUE.md")
CID="COMMIT-RAVI2-2026-10-16-AFFINE-TREE-CORE-17"
RID="BR-AFFINE-TREE-CORE"
TS=datetime.now(timezone.utc).isoformat()

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

for p in [REPORT,ARCHIVE,RESULTS,BRICK]:
    assert p.exists(),p
shutil.copy2(DB,BACKUP)

c=sqlite3.connect(DB)
c.row_factory=sqlite3.Row
c.execute("PRAGMA foreign_keys=ON")
before={
    "results":c.execute("select count(*) from results").fetchone()[0],
    "admissible":c.execute("select count(*) from certified_active_results").fetchone()[0],
    "dep":c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
    "versions":c.execute("select count(*) from result_versions").fetchone()[0],
}
assert before=={"results":74,"admissible":70,"dep":38,"versions":84},before
assert not c.execute("select 1 from results where result_id=?",(RID,)).fetchone()
for dep in ["BR-AFFINE-TREE-GLUE","BR-AFFINE-GROUP-CORE"]:
    assert c.execute("select 1 from certified_active_results where result_id=?",(dep,)).fetchone(),dep

statement=("Pour une famille finie de relations affines sur F₂ portée par un arbre satisfaisant l’intersection courante, "
           "le filtrage exact de BR-AFFINE-TREE-GLUE décide le joint global et fournit le comptage/prolongement lorsqu’il est non vide. "
           "Si le joint est vide, représenter chaque module par son groupe équivalent d’équations affines puis appliquer "
           "BR-AFFINE-GROUP-CORE fournit un sous-ensemble de modules minimal par inclusion dont la conjonction est incompatible, "
           "avec certificat XOR 0=1 et témoin satisfaisant après suppression de chaque module du noyau.")
domain=("Familles finies de relations affines binaires sur un arbre de portées satisfaisant l’intersection courante ; "
        "variables partagées identifiées littéralement ; groupes d’équations exacts sur F₂.")
ass=[
    "BR-AFFINE-TREE-GLUE",
    "BR-AFFINE-GROUP-CORE",
    "relations affines finies sur F2",
    "arbre de portées avec intersection courante",
    "représentation exacte de chaque module par ses équations affines",
]
row=dict(
    result_id=RID,project_id="OBSERVABILITE",result_type="THEOREM",
    title="Diagnostic complet sur arbre : composition ou noyau incompatible minimal",
    statement=statement,domain=domain,assumptions_json=json.dumps(ass,ensure_ascii=False),
    epistemic_status="DÉMONTRÉ",originality_status="CONNU_OU_CLASSIQUE",
    confidence_note=("Corollaire composé de deux briques certifiées. Validation exhaustive : 15972 familles, "
                     "7470 joints vides, 7470 noyaux minimaux par inclusion revérifiés par énumération brute ; "
                     "aucune revendication de nouveauté, performance ou minimalité en cardinalité."),
    version=1,created_at=TS,updated_at=TS
)
cols=list(row)
c.execute("BEGIN IMMEDIATE")
try:
    c.execute(f"insert into results({','.join(cols)}) values ({','.join('?'*len(cols))})",[row[k] for k in cols])
    c.execute("""insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at)
                 values (?,?,?,?,?,?,?)""",
              (RID,1,json.dumps(row,ensure_ascii=False,sort_keys=True),"ACTIVE",1,CID,TS))
    rels=[
        ("BR-AFFINE-TREE-GLUE","Le diagnostic positif et le filtrage exact sur arbre sont ceux de TREE-GLUE."),
        ("BR-AFFINE-GROUP-CORE","Le certificat négatif minimal par inclusion est fourni par GROUP-CORE après représentation équationnelle exacte.")
    ]
    for target,note in rels:
        c.execute("""insert into relations(source_result_id,relation_type,target_result_id,note,created_at)
                     values (?,?,?,?,?)""",(RID,"DEPEND_DE",target,note,TS))
    evid=[
        ("EVID-TREECORE17-REPORT","PROOF_REPORT","/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md",sha(REPORT),
         "Preuve du raccordement, domaine, limites, provenance et audit de redondance.","INTERNAL_PROOF_REVIEWED"),
        ("EVID-TREECORE17-ARCHIVE","REPRODUCIBILITY_ARCHIVE","/PREUVES_AFFINE_TREE_CORE_BRIDGE_2026-10-16.zip",sha(ARCHIVE),
         "Script, sortie exacte, manifeste des sources et note de preuve.","INTERNAL_RECHECKED"),
        ("EVID-TREECORE17-RESULTS","EXACT_COMPUTATION","/AFFINE_TREE_CORE_BRIDGE_RESULTS_2026-10-16.json",sha(RESULTS),
         "15972 familles ; 7470 cas incompatibles ; minimalité de 7470 noyaux revérifiée indépendamment.","EXECUTED"),
        ("EVID-TREECORE17-CARD","RESULT_CARD","/Recherche/01_BRIQUES_REUTILISABLES/BR-AFFINE-TREE-CORE_BRIQUE.md",sha(BRICK),
         "Carte atomique réutilisable du raccordement.","CARD_REVIEWED"),
    ]
    c.executemany("""insert into evidence(evidence_id,result_id,evidence_type,locator,sha256,description,verification_status,created_at)
                     values (?,?,?,?,?,?,?,?)""",[(e[0],RID,e[1],e[2],e[3],e[4],e[5],TS) for e in evid])
    c.execute("""insert into audits(audit_id,result_id,project_id,audit_type,outcome,performed_by,artifact_locator,notes,created_at)
                 values (?,?,?,?,?,?,?,?,?)""",
              ("AUD-BR-AFFINE-TREE-CORE-17",RID,"OBSERVABILITE","PROOF_CALCULATION_REDUNDANCY_BIBLIOGRAPHY",
               "PASS","bridge_proof;brute_enumeration;database_guard",
               "/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md",
               "Preuve par composition de contrats ; représentation équationnelle locale vérifiée ; 15972 verdicts bruts concordants ; "
               "7470 noyaux minimaux par inclusion vérifiés par retrait ; sources classiques des deux briques réutilisées ; aucune priorité revendiquée.",TS))
    c.execute("""insert into regression_tests(test_id,result_id,name,kind,status,artifact_locator,last_run_at,notes)
                 values (?,?,?,?,?,?,?,?)""",
              ("REG-BR-AFFINE-TREE-CORE-17",RID,
               "Pipeline arbre : comptage ou noyau minimal par inclusion","EXACT","PASS",
               "/PREUVES_AFFINE_TREE_CORE_BRIDGE_2026-10-16.zip",TS,
               "Chaîne1331 + étoile14641 ; brute force indépendante pour verdict, représentation et minimalité."))
    for sid,role in [
        ("SRC-FAGIN-TREE16","BACKGROUND"),
        ("SRC-BFMY-TREE16","BACKGROUND"),
        ("SRC-JUNKER-CORE15","BACKGROUND"),
    ]:
        c.execute("insert into result_sources(result_id,source_id,role) values (?,?,?)",(RID,sid,role))
    c.execute("""insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at)
                 values (?,?,?,?,?,?,?)""",
              ("BIB-TREECORE17","OBSERVABILITE","FINAL_EXISTING_SOURCES",
               "Sources primaires déjà vérifiées des deux briques composées",
               "SRC-FAGIN-TREE16;SRC-BFMY-TREE16;SRC-JUNKER-CORE15",
               "Le raccordement est traité comme corollaire/application interne de mécanismes classiques ; aucune nouveauté ou priorité revendiquée.",TS))
    c.execute("""insert into events(entity_type,entity_id,event_type,payload_json,created_at)
                 values (?,?,?,?,?)""",
              ("result",RID,"CREATED",json.dumps({"commit":CID,"report":"/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md",
                                                   "internal_only":True,"no_global_novelty_claim":True},ensure_ascii=False),TS))
    for target,_ in rels:
        c.execute("""insert into events(entity_type,entity_id,event_type,payload_json,created_at)
                     values (?,?,?,?,?)""",
                  ("relation",f"{RID} DEPEND_DE {target}","ADDED",
                   json.dumps({"commit":CID,"source":RID,"relation":"DEPEND_DE","target":target},ensure_ascii=False),TS))
    c.execute("""insert into events(entity_type,entity_id,event_type,payload_json,created_at)
                 values (?,?,?,?,?)""",
              ("method_test","AFFINE_TREE_CORE_BRIDGE_01","LOCAL_TEST_COMPLETED",
               json.dumps({"commit":CID,"families":15972,"unsat":7470,"minimal_cores_verified":7470,
                           "new_scientific_card":RID},ensure_ascii=False),TS))
    # project next experiment: no scientific status change
    c.execute("""update projects set last_branch=?, next_experiment=?, updated_at=? where project_id='OBSERVABILITE'""",
              ("AFFINE_TREE_CORE_BRIDGE",
               "Structurer les contrats v1.3 (quantificateurs, constantes, interfaces) puis tester les candidats affines cycliques, "
               "notamment TREE-GLUE / GAUGE-GLUE / GROUP-CORE, sans promotion automatique.",TS))
    c.commit()
except Exception:
    c.rollback()
    c.close()
    shutil.copy2(BACKUP,DB)
    raise

def check_cycle():
    graph={}
    for s,t in c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'"):
        graph.setdefault(s,[]).append(t)
    visiting=set();done=set()
    def dfs(u):
        if u in visiting: raise AssertionError("causal cycle at "+u)
        if u in done:return
        visiting.add(u)
        for v in graph.get(u,[]):dfs(v)
        visiting.remove(u);done.add(u)
    for u in list(graph):dfs(u)

integrity=c.execute("pragma integrity_check").fetchone()[0]
fk=c.execute("pragma foreign_key_check").fetchall()
check_cycle()
forbidden=c.execute("""select r.source_result_id,r.target_result_id from relations r
                       left join certified_active_results c on c.result_id=r.target_result_id
                       where r.relation_type='DEPEND_DE' and c.result_id is null""").fetchall()
after={
    "results":c.execute("select count(*) from results").fetchone()[0],
    "admissible":c.execute("select count(*) from certified_active_results").fetchone()[0],
    "dep":c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
    "versions":c.execute("select count(*) from result_versions").fetchone()[0],
    "status_counts":dict(c.execute("select epistemic_status,count(*) from results group by epistemic_status")),
}
assert integrity=="ok" and not fk and not forbidden
assert after["results"]==75 and after["admissible"]==71 and after["dep"]==40 and after["versions"]==85,after
assert c.execute("select count(*) from result_versions where result_id=? and lifecycle='ACTIVE' and premise_allowed=1",(RID,)).fetchone()[0]==1
c.close()
out={
    "commit":CID,"before":before,"after":after,"integrity":integrity,
    "foreign_key_errors":len(fk),"causal_cycles":0,"forbidden_targets":len(forbidden),
    "main_sha256":sha(DB),"backup_sha256":sha(BACKUP),
    "new_result":RID,
}
Path("/mnt/data/ravi13_work/AFFINE_TREE_CORE_COMMIT_CONTROLS_2026-10-16.json").write_text(
    json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(out,indent=2,ensure_ascii=False))