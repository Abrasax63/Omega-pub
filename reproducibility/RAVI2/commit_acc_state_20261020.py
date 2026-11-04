import sqlite3,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('/mnt/data/acc_state_commit')
DB=ROOT/'RESEARCH_MEMORY.sqlite'
BACKUP=ROOT/'RESEARCH_MEMORY_PRE_ACC_STATE23.sqlite'
CARD=ROOT/'BR-ACC-STATE-COMMUTE-01_BRIQUE.md'
AUDIT=ROOT/'AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md'
BIB=ROOT/'AUDIT_ORIGINALITE_ACC_STATE_2026-10-20.md'
CHECK=ROOT/'ACCESS_PREDICTIVE_BRIDGE_CHECK.json'
OUT=ROOT/'ACC_STATE_COMMIT_CONTROLS_2026-10-20.json'
CID='COMMIT-RAVI2-2026-10-20-ACC-STATE-COMMUTE-23'
RID='BR-ACC-STATE-COMMUTE-01'
TS=datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def rowdict(c,rid):
 r=c.execute('select * from results where result_id=?',(rid,)).fetchone(); return dict(r) if r else None
for p in [DB,CARD,AUDIT,BIB,CHECK]: assert p.exists(),p
checks=json.loads(CHECK.read_text())
assert checks.get('all_pass') is True
pre_sha=sha(DB); shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={'results':c.execute('select count(*) from results').fetchone()[0],'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],'relations':c.execute('select count(*) from relations').fetchone()[0],'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert before=={'results':86,'admissible':82,'dep':47,'relations':79,'versions':96},before
assert not c.execute('select 1 from results where result_id=?',(RID,)).fetchone()
for prem in ['BR-ACC-01','BR-STATE-01']:
 assert c.execute('select 1 from certified_active_results where result_id=?',(prem,)).fetchone(),prem
statement=("Pour un système fini déterministe total avec observation pi et ensemble initial non vide E, soit ~= l'équivalence prédictive canonique par égalité de toutes les continuations observées, q:X->X/~ et H=Reach(E). Alors q(H)=Reach(q(E)) dans le quotient, l'équivalence prédictive du sous-système H est exactement ~ restreinte à H, et H/(~|H) est canoniquement isomorphe à la partie accessible du quotient global.")
ass=['système fini déterministe','actions totales','observation fixe','ensemble initial E non vide','équivalence prédictive définie sur toutes les continuations finies']
note=("Preuve directe par stabilité de l'équivalence prédictive et invariance avant de H. Contrôle indépendant: 41018 cas exhaustifs + 20000 aléatoires, zéro violation. Audit bibliographique: mécanisme connu/classique en minimisation d'automates et coalgebras; aucune priorité revendiquée.")
vals=(RID,'DELTA_H_FERMETURE','THEOREM_BRIDGE','Accessibilité et quotient prédictif commutent',statement,'Systèmes finis déterministes totaux à actions; observation fixe; ensemble initial non vide.',json.dumps(ass,ensure_ascii=False),'DÉMONTRÉ','CONNU_OU_CLASSIQUE',note,1,TS,TS)
c.execute('insert into results values(?,?,?,?,?,?,?,?,?,?,?,?,?)',vals)
r=rowdict(c,RID)
c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values(?,?,?,?,?,?,?)',(RID,1,json.dumps(r,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))
sources=[
 ('SRC-ACC-STATE-AUDIT-20261020','INTERNAL_AUDIT','Audit RAVI-2 — commutation accessibilité / quotient prédictif',None,2026,'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md',0,TS,'Audit preuve, robustesse, interfaces strictes et redondance.'),
 ('SRC-ACC-STATE-BIB-20261020','BIBLIOGRAPHIC_AUDIT','Audit originalité — ACC/STATE',None,2026,'/Recherche/05_BIBLIOGRAPHIE/AUDIT_ORIGINALITE_ACC_STATE_2026-10-20.md',0,TS,'Conclusion: connu/classique; aucune priorité.'),
 ('SRC-ACC-STATE-CHECK-20261019','EXECUTED_CHECKER','ACCESS_PREDICTIVE_BRIDGE_CHECK.json',None,2026,'/Recherche/04_CODE_DONNEES/RAVI2_DISCOVERY/ACCESS_PREDICTIVE_BRIDGE_CHECK.json',0,TS,'41018 exhaustifs + 20000 aléatoires; all_pass=true.'),
 ('SRC-CARD-'+RID,'LIBRARY_CARD','BR-ACC-STATE-COMMUTE-01_BRIQUE.md',None,2026,'/Recherche/01_BRIQUES_REUTILISABLES/BR-ACC-STATE-COMMUTE-01_BRIQUE.md',0,TS,'Carte atomique du raccordement.'),
 ('SRC-AMMS13-WELL-POINTED','PEER_REVIEWED','Well-Pointed Coalgebras','Jiří Adámek; Stefan Milius; Lawrence S. Moss; Lurdes Sousa',2013,'https://doi.org/10.2168/LMCS-9(3:2)2013',1,TS,'Example 3.19 / Remark 3.20: reachability et quotient comportemental dans les automates déterministes.'),
 ('SRC-WISSMANN22-MINIMALITY','PEER_REVIEWED','Minimality Notions via Factorization Systems and Examples','Thorsten Wißmann',2022,'https://doi.org/10.46298/LMCS-18(3:31)2022',1,TS,'Interaction abstraite reachability/observability et séquencement dans les deux ordres.')]
for s in sources: c.execute('insert or replace into sources values(?,?,?,?,?,?,?,?,?)',s)
for sid,role in [('SRC-ACC-STATE-AUDIT-20261020','AUDIT'),('SRC-ACC-STATE-BIB-20261020','BIBLIOGRAPHY'),('SRC-ACC-STATE-CHECK-20261019','VALIDATION'),('SRC-CARD-'+RID,'INTERFACE_CARD'),('SRC-AMMS13-WELL-POINTED','PRIOR_ART'),('SRC-WISSMANN22-MINIMALITY','PRIOR_ART')]:
 c.execute('insert into result_sources(result_id,source_id,role) values(?,?,?)',(RID,sid,role))
for sid in ['SRC-CARD-BR-ACC-01','SRC-CARD-BR-STATE-01']:
 if c.execute('select 1 from sources where source_id=?',(sid,)).fetchone(): c.execute('insert or ignore into result_sources(result_id,source_id,role) values(?,?,?)',(RID,sid,'PREMISE_INTERFACE'))
ev=[('EVID-CARD-'+RID,RID,'REUSABLE_CARD','/Recherche/01_BRIQUES_REUTILISABLES/BR-ACC-STATE-COMMUTE-01_BRIQUE.md',sha(CARD),'Carte atomique réutilisable.','CARD_REVIEWED',TS),('EVID-CHECK-'+RID,RID,'EXACT_RECHECK','/Recherche/04_CODE_DONNEES/RAVI2_DISCOVERY/ACCESS_PREDICTIVE_BRIDGE_CHECK.json',sha(CHECK),'41018 cas exhaustifs et 20000 aléatoires; zéro violation.','EXECUTED',TS),('EVID-AUDIT-'+RID,RID,'RAVI2_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md',sha(AUDIT),'Audit preuve, interfaces, redondance et décision.','INTERNAL_REVIEWED',TS),('EVID-BIB-'+RID,RID,'BIBLIOGRAPHIC_AUDIT','/Recherche/05_BIBLIOGRAPHIE/AUDIT_ORIGINALITE_ACC_STATE_2026-10-20.md',sha(BIB),'Antériorité générale identifiée; statut connu/classique.','INTERNAL_REVIEWED',TS)]
for x in ev: c.execute('insert into evidence values(?,?,?,?,?,?,?,?)',x)
c.execute('insert into audits values(?,?,?,?,?,?,?,?,?)',('AUD-ACC-STATE-COMMUTE-23',RID,'DELTA_H_FERMETURE','RAVI2_PROOF_SCOPE_REDUNDANCY_BIBLIOGRAPHY','PASS','proof_reconstruction;independent_checker;strict_interface_design;targeted_bibliography','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md',note,TS))
rels=[]
for tgt,note_rel in [('BR-ACC-01','Référence de définition pour H=Reach(E) et le cadre fini déterministe total.'),('BR-STATE-01','Référence de définition/théorème pour l’équivalence prédictive canonique et sa stabilité par les actions.')]:
 rid=c.execute('select coalesce(max(relation_id),0)+1 from relations').fetchone()[0]
 c.execute('insert into relations(relation_id,source_result_id,relation_type,target_result_id,note,created_at) values(?,?,?,?,?,?)',(rid,RID,'DEPEND_DE',tgt,note_rel,TS)); rels.append((rid,tgt))
c.execute("insert or replace into meta(key,value) values('last_scientific_commit',?)",(CID,)); c.execute("insert or replace into meta(key,value) values('last_scientific_commit_at',?)",(TS,)); c.commit()
integrity=c.execute('pragma integrity_check').fetchone()[0]; fk=c.execute('pragma foreign_key_check').fetchall()
after={'results':c.execute('select count(*) from results').fetchone()[0],'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],'relations':c.execute('select count(*) from relations').fetchone()[0],'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
# causal cycle check
edges=c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'").fetchall(); g={}
for a,b in edges:g.setdefault(a,[]).append(b)
def cyc(v,stack,seen):
 if v in stack:return True
 if v in seen:return False
 seen.add(v);stack.add(v)
 for u in g.get(v,[]):
  if cyc(u,stack,seen): return True
 stack.remove(v);return False
cycle=any(cyc(v,set(),set()) for v in list(g))
assert after=={'results':87,'admissible':83,'dep':49,'relations':81,'versions':97},after
assert integrity=='ok' and not fk and not cycle,(integrity,fk,cycle)
out={'commit':CID,'timestamp':TS,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':int(cycle),'new_result':RID,'new_relations':[{'relation_id':r,'target':t,'strict_class':'DEFINITION_REFERENCE'} for r,t in rels],'originality':'CONNU_OU_CLASSIQUE','checker':checks,'main_sha256_before':pre_sha,'main_sha256_after':sha(DB),'backup_sha256':sha(BACKUP),'card_sha256':sha(CARD),'audit_sha256':sha(AUDIT),'bibliography_sha256':sha(BIB)}
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8'); c.close(); print(json.dumps(out,indent=2,ensure_ascii=False))