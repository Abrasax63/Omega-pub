#!/usr/bin/env python3
import sqlite3,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('/mnt/data/ravi13_discovery')
DB=ROOT/'RESEARCH_MEMORY.sqlite'
BACKUP=ROOT/'RESEARCH_MEMORY_PRE_GAUGE_CORE.sqlite'
REPORT=ROOT/'GAUGE_CORE_BRIDGE_2026-10-16.md'
ARCHIVE=ROOT/'PREUVES_AFFINE_GAUGE_CORE_2026-10-16.zip'
RESULTS=ROOT/'GAUGE_CORE_BRIDGE_RESULTS_2026-10-16.json'
BRICK=ROOT/'BR-AFFINE-GAUGE-CORE_BRIQUE.md'
DISC=ROOT/'GAUGE_CORE_DISCOVERY_AUDIT_2026-10-16.json'
CID='COMMIT-RAVI2-2026-10-16-AFFINE-GAUGE-CORE-18'
RID='BR-AFFINE-GAUGE-CORE'
TS=datetime.now(timezone.utc).isoformat()

def sha(p):
 h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
for p in [REPORT,ARCHIVE,RESULTS,BRICK,DISC]: assert p.exists(),p
shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={
 'results':c.execute('select count(*) from results').fetchone()[0],
 'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
 'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
 'versions':c.execute('select count(*) from result_versions').fetchone()[0],
}
assert before=={'results':75,'admissible':71,'dep':40,'versions':85},before
assert not c.execute('select 1 from results where result_id=?',(RID,)).fetchone()
for dep in ['BR-AFFINE-GAUGE-GLUE','BR-AFFINE-GROUP-CORE']:
 assert c.execute('select 1 from certified_active_results where result_id=?',(dep,)).fetchone(),dep
statement=("Pour des familles affines binaires cohérentes A_i,B_i ayant les mêmes espaces de lignes S_i et phases relatives δ_i, "
           "former, pour une base B_i de chaque S_i, le groupe d'équations g·s=δ_i(s) en la translation commune inconnue g. "
           "Une translation commune existe si et seulement si l'union de ces groupes est compatible, indépendamment du choix des bases. "
           "Sinon BR-AFFINE-GROUP-CORE fournit un sous-ensemble d'étiquettes minimal par inclusion sans translation commune, avec certificat XOR 0=1 et témoin après chaque suppression. "
           "Un tel noyau peut être choisi de taille au plus d+1 en dimension d, et cette borne est serrée.")
domain=("Familles finies de sous-espaces S_i de F2^d et phases linéaires δ_i issues de deux familles affines cohérentes ayant les mêmes espaces de lignes par étiquette ; "
        "translation commune dans les mêmes coordonnées ; dimension finie.")
ass=['BR-AFFINE-GAUGE-GLUE','BR-AFFINE-GROUP-CORE','F2','famille finie','mêmes espaces de lignes par étiquette','phases relatives linéaires cohérentes','minimalité par inclusion seulement']
row=dict(result_id=RID,project_id='OBSERVABILITE',result_type='THEOREM',
 title="Diagnostic de translation commune ou noyau minimal d'étiquettes",
 statement=statement,domain=domain,assumptions_json=json.dumps(ass,ensure_ascii=False),
 epistemic_status='DÉMONTRÉ',originality_status='CONNU_OU_CLASSIQUE',
 confidence_note=('Corollaire composé de GAUGE-GLUE et GROUP-CORE. Validation indépendante : 242270 familles exhaustives, '
                  '160754 incompatibles, 10000 familles aléatoires, 5000 changements de base ; trois méthodes concordantes. '
                  'Borne d+1 prouvée et exemples serrés d=1..6. Aucune priorité, performance ou minimalité en cardinalité revendiquée.'),
 version=1,created_at=TS,updated_at=TS)
cols=list(row)
c.execute('BEGIN IMMEDIATE')
try:
 c.execute(f"insert into results({','.join(cols)}) values ({','.join('?'*len(cols))})",[row[k] for k in cols])
 c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values (?,?,?,?,?,?,?)',
           (RID,1,json.dumps(row,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))
 rels=[
  ('BR-AFFINE-GAUGE-GLUE','Le critère sémantique translation commune ⇔ annulation de la phase sur les relations est celui de GAUGE-GLUE.'),
  ('BR-AFFINE-GROUP-CORE','La branche incompatible applique GROUP-CORE aux groupes d’équations en g pour extraire un noyau minimal par inclusion et ses certificats.')]
 for target,note in rels:
  c.execute('insert into relations(source_result_id,relation_type,target_result_id,note,created_at) values (?,?,?,?,?)',(RID,'DEPEND_DE',target,note,TS))
 evid=[
  ('EVID-GAUGECORE18-REPORT','PROOF_REPORT','/GAUGE_CORE_BRIDGE_2026-10-16.md',sha(REPORT),'Preuve, domaine, limites, audit de redondance et littérature.','INTERNAL_PROOF_REVIEWED'),
  ('EVID-GAUGECORE18-ARCHIVE','REPRODUCIBILITY_ARCHIVE','/PREUVES_AFFINE_GAUGE_CORE_2026-10-16.zip',sha(ARCHIVE),'Script reproductible, résultats, carte, audit découverte et note de preuve.','INTERNAL_RECHECKED'),
  ('EVID-GAUGECORE18-RESULTS','EXACT_COMPUTATION','/GAUGE_CORE_BRIDGE_RESULTS_2026-10-16.json',sha(RESULTS),'242270 familles exhaustives ; 160754 incompatibles ; 10000 aléatoires ; 5000 changements de base.','EXECUTED'),
  ('EVID-GAUGECORE18-CARD','RESULT_CARD','/Recherche/01_BRIQUES_REUTILISABLES/BR-AFFINE-GAUGE-CORE_BRIQUE.md',sha(BRICK),'Carte réutilisable du raccordement jauge→noyau minimal.','CARD_REVIEWED'),
  ('EVID-GAUGECORE18-DISCOVERY','DISCOVERY_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/GAUGE_CORE_DISCOVERY_AUDIT_2026-10-16.json',sha(DISC),'Triage des raccordements, redondances transitives et contrôles négatifs.','INTERNAL_RECHECKED')]
 c.executemany('insert into evidence(evidence_id,result_id,evidence_type,locator,sha256,description,verification_status,created_at) values (?,?,?,?,?,?,?,?)',[(e[0],RID,e[1],e[2],e[3],e[4],e[5],TS) for e in evid])
 c.execute('insert into audits(audit_id,result_id,project_id,audit_type,outcome,performed_by,artifact_locator,notes,created_at) values (?,?,?,?,?,?,?,?,?)',
           ('AUD-BR-AFFINE-GAUGE-CORE-18',RID,'OBSERVABILITE','PROOF_CALCULATION_REDUNDANCY_BIBLIOGRAPHY','PASS','bridge_proof;brute_force;gaussian_provenance;transitive_filter','/GAUGE_CORE_BRIDGE_2026-10-16.md',
            'Preuve par prolongement de formes et système affine groupé ; trois méthodes indépendantes ; minimalité et certificats revérifiés ; QuickXplain/MUS comme antécédent classique ; aucune priorité revendiquée.',TS))
 c.execute('insert into regression_tests(test_id,result_id,name,kind,status,artifact_locator,last_run_at,notes) values (?,?,?,?,?,?,?,?)',
           ('REG-BR-AFFINE-GAUGE-CORE-18',RID,'Translation commune ou noyau minimal de jauge','EXACT','PASS','/PREUVES_AFFINE_GAUGE_CORE_2026-10-16.zip',TS,
            '242270 exhaustifs +10000 aléatoires +5000 changements de base ; borne d+1 et exemples serrés.'))
 for sid,role in [('SRC-JUNKER-CORE15','BACKGROUND'),('SRC-ODONNELL-DRAFT-SIGNED11','BACKGROUND'),('SRC-MACWILLIAMS-MALLOWS-SLOANE-THIRD14','BACKGROUND')]:
  c.execute('insert into result_sources(result_id,source_id,role) values (?,?,?)',(RID,sid,role))
 c.execute('insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at) values (?,?,?,?,?,?,?)',
           ('BIB-GAUGECORE18','OBSERVABILITE','FINAL_EXISTING_AND_WEB_SOURCES','minimal conflict/MUS + affine local-global gauge obstruction','SRC-JUNKER-CORE15;GAUGE-GLUE sources;AAAI QuickXplain',
            'Conflits minimaux et obstruction local-global sont des mécanismes classiques. Le présent résultat est classé application interne composée ; aucune nouveauté ou priorité revendiquée.',TS))
 c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',('result',RID,'CREATED',json.dumps({'commit':CID,'report':'/GAUGE_CORE_BRIDGE_2026-10-16.md','internal_only':True,'no_global_novelty_claim':True},ensure_ascii=False),TS))
 for target,_ in rels:
  c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',('relation',f'{RID} DEPEND_DE {target}','ADDED',json.dumps({'commit':CID,'source':RID,'relation':'DEPEND_DE','target':target},ensure_ascii=False),TS))
 c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',('method_test','GAUGE_CORE_DISCOVERY_01','LOCAL_TEST_COMPLETED',json.dumps({'commit':CID,'exhaustive':242270,'incompatible':160754,'random':10000,'basis_tests':5000,'new_scientific_card':RID},ensure_ascii=False),TS))
 c.execute("update projects set last_branch=?, next_experiment=?, updated_at=? where project_id='OBSERVABILITE'",('AFFINE_GAUGE_CORE_BRIDGE','Étendre le moteur de découverte strict aux 72 briques admissibles, chercher des ponts non transitifs et conserver séparément candidats réfutés, relations alternatives et nouvelles briques certifiées.',TS))
 c.commit()
except Exception:
 c.rollback(); c.close(); shutil.copy2(BACKUP,DB); raise

def check_cycle():
 graph={}
 for s,t in c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'"): graph.setdefault(s,[]).append(t)
 visiting=set(); done=set()
 def dfs(u):
  if u in visiting: raise AssertionError('causal cycle '+u)
  if u in done:return
  visiting.add(u)
  for v in graph.get(u,[]): dfs(v)
  visiting.remove(u); done.add(u)
 for u in list(graph): dfs(u)

integrity=c.execute('pragma integrity_check').fetchone()[0]; fk=c.execute('pragma foreign_key_check').fetchall(); check_cycle()
forbidden=c.execute("""select r.source_result_id,r.target_result_id from relations r left join certified_active_results c on c.result_id=r.target_result_id where r.relation_type='DEPEND_DE' and c.result_id is null""").fetchall()
after={'results':c.execute('select count(*) from results').fetchone()[0],'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],'versions':c.execute('select count(*) from result_versions').fetchone()[0],'status_counts':dict(c.execute('select epistemic_status,count(*) from results group by epistemic_status'))}
assert integrity=='ok' and not fk and not forbidden
assert after['results']==76 and after['admissible']==72 and after['dep']==42 and after['versions']==86,after
assert c.execute('select count(*) from result_versions where result_id=? and lifecycle="ACTIVE" and premise_allowed=1',(RID,)).fetchone()[0]==1
c.close()
out={'commit':CID,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':0,'forbidden_targets':len(forbidden),'main_sha256':sha(DB),'backup_sha256':sha(BACKUP),'new_result':RID}
(ROOT/'GAUGE_CORE_COMMIT_CONTROLS_2026-10-16.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=False))