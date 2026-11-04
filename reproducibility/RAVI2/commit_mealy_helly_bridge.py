#!/usr/bin/env python3
import sqlite3,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone

BASE=Path('/mnt/data/ravi13_discovery2')
DB=BASE/'RESEARCH_MEMORY.sqlite'
BACKUP=BASE/'RESEARCH_MEMORY_PRE_MEALY_HELLY.sqlite'
REPORT=BASE/'MEALY_HELLY_BRIDGE_2026-10-16.md'
ARCHIVE=BASE/'PREUVES_MEALY_HELLY_2026-10-16.zip'
RESULTS=BASE/'MEALY_HELLY_RESULTS_2026-10-16.json'
BRICK=BASE/'BR-MEALY-HELLY-01_BRIQUE.md'
CID='COMMIT-RAVI2-2026-10-16-MEALY-HELLY-19'
RID='BR-MEALY-HELLY-01'
TS=datetime.now(timezone.utc).isoformat()

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in [REPORT,ARCHIVE,RESULTS,BRICK]: assert p.exists(),p
shutil.copy2(DB,BACKUP)

c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={
 'results':c.execute('select count(*) from results').fetchone()[0],
 'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
 'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
 'versions':c.execute('select count(*) from result_versions').fetchone()[0],
}
assert before=={'results':76,'admissible':72,'dep':42,'versions':86},before
assert not c.execute('select 1 from results where result_id=?',(RID,)).fetchone()
for dep in ['OBS-M27-FERTILE','OBS-M27-SPECTRUM']:
    assert c.execute('select 1 from certified_active_results where result_id=?',(dep,)).fetchone(),dep

statement=("Pour toute machine de Mealy finie complète déterministe avec q sorties et r_IO=1, pour tout état de connaissance accessible K et toute entrée a, "
           "le nerf formé par les langages de résolution preset non vides des branches K(a,y) est (q-1)-Helly : toute non-face minimale a taille au plus q-1. "
           "Pour q=2 il est 1-Helly. Pour q>=3 la borne q-1 est optimale, et chaque arité 2..q-1 est réalisable par la famille C(q,k).")
domain=("Machines de Mealy finies, complètes et déterministes ; langage observable exactement 1-step (r_IO=1) ; "
        "états de connaissance accessibles ; nerf restreint aux branches individuellement résolubles par PDS.")
ass=[
 'machine finie complète déterministe','r_IO=1 exact','q=taille de l alphabet de sorties',
 'etat de connaissance accessible','branches K(a,y) non vides','langages de resolution preset individuels non vides',
 'OBS-M27-FERTILE','OBS-M27-SPECTRUM'
]
row=dict(result_id=RID,project_id='OBSERVABILITE',result_type='THEOREM',
 title='Borne de Helly du nerf de compatibilité des résolveurs Mealy',
 statement=statement,domain=domain,assumptions_json=json.dumps(ass,ensure_ascii=False),
 epistemic_status='DÉMONTRÉ',originality_status='INDÉTERMINÉ',
 confidence_note=("Corollaire de raccordement : une non-face minimale ne peut contenir que des branches fertiles, donc taille <=q-1 ; "
                  "sharpness par C(q,q-1). Validation indépendante sur 21 machines C(q,k), 492 états de connaissance et 1337 nerfs ; zéro violation. "
                  "Recherche bibliographique ciblée sans correspondance exacte ; aucune priorité revendiquée."),
 version=1,created_at=TS,updated_at=TS)
cols=list(row)
c.execute('BEGIN IMMEDIATE')
try:
    c.execute(f"insert into results({','.join(cols)}) values ({','.join('?'*len(cols))})",[row[k] for k in cols])
    c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values (?,?,?,?,?,?,?)',
              (RID,1,json.dumps(row,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))
    rels=[
      ('OBS-M27-FERTILE','La borne de Helly vient du fait que chaque branche essentielle d une non-face minimale est fertile, puis largeur fertile <= q-1.'),
      ('OBS-M27-SPECTRUM','La famille C(q,k) fournit la sharpness q-1 et réalise chaque arité 2..q-1.')]
    for target,note in rels:
        c.execute('insert into relations(source_result_id,relation_type,target_result_id,note,created_at) values (?,?,?,?,?)',(RID,'DEPEND_DE',target,note,TS))
    evid=[
      ('EVID-MEALYHELLY19-REPORT','PROOF_REPORT','/MEALY_HELLY_BRIDGE_2026-10-16.md',sha(REPORT),'Preuve du corollaire Helly, limites, redondance et bibliographie.','INTERNAL_PROOF_REVIEWED'),
      ('EVID-MEALYHELLY19-ARCHIVE','REPRODUCIBILITY_ARCHIVE','/PREUVES_MEALY_HELLY_2026-10-16.zip',sha(ARCHIVE),'Script, résultats, carte et manifeste.','INTERNAL_RECHECKED'),
      ('EVID-MEALYHELLY19-RESULTS','EXACT_COMPUTATION','/MEALY_HELLY_RESULTS_2026-10-16.json',sha(RESULTS),'21 C(q,k), 492 états de connaissance, 1337 nerfs testés, zéro violation.','EXECUTED'),
      ('EVID-MEALYHELLY19-CARD','RESULT_CARD','/Recherche/01_BRIQUES_REUTILISABLES/BR-MEALY-HELLY-01_BRIQUE.md',sha(BRICK),'Carte atomique réutilisable.','CARD_REVIEWED')]
    c.executemany('insert into evidence(evidence_id,result_id,evidence_type,locator,sha256,description,verification_status,created_at) values (?,?,?,?,?,?,?,?)',
                  [(a,RID,b,d,e,f,g,TS) for a,b,d,e,f,g in [(x[0],x[1],x[2],x[3],x[4],x[5]) for x in evid]])
    # Above tuple construction is intentionally explicit to keep field order obvious.
    c.execute('insert into audits(audit_id,result_id,project_id,audit_type,outcome,performed_by,artifact_locator,notes,created_at) values (?,?,?,?,?,?,?,?,?)',
              ('AUD-BR-MEALY-HELLY-19',RID,'OBSERVABILITE','PROOF_CALCULATION_REDUNDANCY_BIBLIOGRAPHY','PASS',
               'proof_reconstruction;independent_pds_bfs;library_search;web_bibliography_search',
               '/MEALY_HELLY_BRIDGE_2026-10-16.md',
               'Preuve générale par largeur fertile; sharpness par spectre C(q,k); 1337 nerfs calculés indépendamment; formulation exacte non localisée dans la recherche ciblée; originalité maintenue INDÉTERMINÉE.',TS))
    c.execute('insert into regression_tests(test_id,result_id,name,kind,status,artifact_locator,last_run_at,notes) values (?,?,?,?,?,?,?,?)',
              ('REG-BR-MEALY-HELLY-19',RID,'Nerfs de compatibilité et borne de Helly q-1','EXACT','PASS',
               '/PREUVES_MEALY_HELLY_2026-10-16.zip',TS,
               'C(q,k), q=3..8, tous k; parcours de tous états de connaissance accessibles; recherche PDS commune par BFS.'))
    c.execute('insert into result_sources(result_id,source_id,role) values (?,?,?)',(RID,'SRC-COMMIT-MEALY','PRIMARY'))
    c.execute('insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at) values (?,?,?,?,?,?,?)',
              ('BIB-MEALYHELLY19','OBSERVABILITE','FINAL_TARGETED',
               'Mealy ADS PDS compatibility nerve Helly; Helly number regular-language intersections; minimal empty intersection DFA',
               'Internal Mealy note plus targeted public web search 2026-10-16',
               'Aucune correspondance exacte localisée pour la borne de Helly q-1 sur les langages de résolution de branches Mealy sous r_IO=1. Littérature générale Helly/automates existe; absence de match ne prouve pas nouveauté. Originalité laissée INDÉTERMINÉE.',TS))
    c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',
              ('result',RID,'CREATED',json.dumps({'commit':CID,'report':'/MEALY_HELLY_BRIDGE_2026-10-16.md','internal_only':True,'novelty':'INDETERMINATE'},ensure_ascii=False),TS))
    for target,_ in rels:
        c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',
                  ('relation',f'{RID} DEPEND_DE {target}','ADDED',json.dumps({'commit':CID,'source':RID,'relation':'DEPEND_DE','target':target},ensure_ascii=False),TS))
    c.execute("update projects set last_branch=?, next_experiment=?, updated_at=? where project_id='OBSERVABILITE'",
              ('MEALY_HELLY_NERVE',
               'Chercher des hypothèses structurelles supplémentaires donnant une borne de Helly strictement plus petite que q-1 ou une classe de nerfs réalisables; ne pas reclasser la nouveauté sans audit externe.',TS))
    c.commit()
except Exception:
    c.rollback(); c.close(); shutil.copy2(BACKUP,DB); raise

# integrity

def check_cycle():
    graph={}
    for s,t in c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'"):
        graph.setdefault(s,[]).append(t)
    visiting=set(); done=set()
    def dfs(u):
        if u in visiting: raise AssertionError('cycle '+u)
        if u in done:return
        visiting.add(u)
        for v in graph.get(u,[]): dfs(v)
        visiting.remove(u); done.add(u)
    for u in list(graph): dfs(u)

integrity=c.execute('pragma integrity_check').fetchone()[0]
fk=c.execute('pragma foreign_key_check').fetchall(); check_cycle()
forbidden=c.execute("""select r.source_result_id,r.target_result_id from relations r left join certified_active_results x on x.result_id=r.target_result_id where r.relation_type='DEPEND_DE' and x.result_id is null""").fetchall()
after={
 'results':c.execute('select count(*) from results').fetchone()[0],
 'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
 'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
 'versions':c.execute('select count(*) from result_versions').fetchone()[0],
 'status_counts':dict(c.execute('select epistemic_status,count(*) from results group by epistemic_status'))}
assert integrity=='ok' and not fk and not forbidden
assert after['results']==77 and after['admissible']==73 and after['dep']==44 and after['versions']==87,after
c.close()
out={'commit':CID,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':0,'forbidden_targets':len(forbidden),'main_sha256':sha(DB),'backup_sha256':sha(BACKUP),'new_result':RID}
(BASE/'MEALY_HELLY_COMMIT_CONTROLS_2026-10-16.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=False))