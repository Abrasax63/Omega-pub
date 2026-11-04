import sqlite3,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path('/mnt/data/single_gap_commit')
DB=ROOT/'RESEARCH_MEMORY.sqlite'
BACKUP=ROOT/'RESEARCH_MEMORY_PRE_SINGLE_GAP22.sqlite'
CARD=ROOT/'BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md'
AUDIT=ROOT/'AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md'
CHECKS=ROOT/'SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json'
CHECKER=ROOT/'single_gap_factor_complexity_checks_2026-10-19.py'
OUT=ROOT/'SINGLE_GAP_COMMIT_CONTROLS_2026-10-19.json'
CID='COMMIT-RAVI2-2026-10-19-SINGLE-GAP-COMPLEX-22'
TS=datetime.now(timezone.utc).isoformat()
RID='BR-WORD-SINGLE-GAP-COMPLEX-01'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def rowdict(c,rid):
 r=c.execute('select * from results where result_id=?',(rid,)).fetchone()
 return dict(r) if r else None

for p in [DB,CARD,AUDIT,CHECKS,CHECKER]: assert p.exists(),p
checks=json.loads(CHECKS.read_text())
assert checks['all_pass'] is True
assert checks['experiment_1_formula_exhaustive']['length_cases']==253330
assert checks['experiment_2_right_special_classification']['length_cases']==75375

pre_sha=sha(DB); shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={
 'results':c.execute('select count(*) from results').fetchone()[0],
 'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
 'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
 'relations':c.execute('select count(*) from relations').fetchone()[0],
 'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert before=={'results':85,'admissible':81,'dep':47,'relations':78,'versions':95},before
assert not c.execute('select 1 from results where result_id=?',(RID,)).fetchone()
assert c.execute("select 1 from certified_active_results where result_id='BR-TIME-FACTOR-COMPLEX-01'").fetchone()

statement=("Pour k>=2, g>=1, h>g, T=(k-1)g+h, soit le mot binaire cyclique de longueur T dont les 1 sont aux positions "
           "0,g,...,(k-1)g. Si p(L) est le nombre de facteurs cycliques distincts de longueur 1<=L<=T, alors "
           "p(L)=1+min(L,h-1)+min(max(L-g,0),(k-1)g). Equivalemment p(L+1)-p(L)=1[L<=h-2]+1[g<=L<=kg-1].")
assumptions=['k entier >=2','g entier >=1','h entier > g','facteurs cycliques exacts','alphabet binaire']
note=("Preuve par classification exhaustive des deux familles de facteurs spéciaux à droite: 0^L pour L<=h-2 et facteur de raccord g-périodique pour g<=L<=kg-1. "
      "Contrôles indépendants: 3773 familles/253330 quadruplets de formule et 1674 familles/75375 longueurs de facteurs spéciaux; zéro échec. "
      "Cadre factor-complexity classique; aucune antériorité exacte de la formule retrouvée dans l'audit ciblé.")
vals=(RID,'TEMPS_REGLE90','THEOREM','Complexité exacte d’un mot cyclique à gap exceptionnel unique',statement,
      'Combinatoire des mots binaires cycliques ; complexité en facteurs ; un unique gap exceptionnel.',
      json.dumps(assumptions,ensure_ascii=False),'DÉMONTRÉ','INDÉTERMINÉ',note,1,TS,TS)
c.execute('insert into results values(?,?,?,?,?,?,?,?,?,?,?,?,?)',vals)
r=rowdict(c,RID)
c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values(?,?,?,?,?,?,?)',
          (RID,1,json.dumps(r,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))

sources=[
 ('SRC-SINGLE-GAP-AUDIT-20261019','INTERNAL_AUDIT','Audit RAVI-2 — complexité à gap exceptionnel unique',None,2026,'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md',0,TS,'Preuve, deux expériences décisives, redondance et audit bibliographique ciblé.'),
 ('SRC-SINGLE-GAP-CHECKS-20261019','EXECUTED_CHECKER','SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json',None,2026,'/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json',0,TS,'Deux contrôles indépendants exacts exécutés le 19 octobre 2026.'),
 ('SRC-CARD-BR-WORD-SINGLE-GAP-COMPLEX-01','LIBRARY_CARD','BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md',None,2026,'/Recherche/01_BRIQUES_REUTILISABLES/BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md',0,TS,'Carte réutilisable du théorème général.')]
for s in sources:
 c.execute('insert or replace into sources values(?,?,?,?,?,?,?,?,?)',s)
for sid,role in [('SRC-SINGLE-GAP-AUDIT-20261019','AUDIT'),('SRC-SINGLE-GAP-CHECKS-20261019','VALIDATION'),('SRC-CARD-BR-WORD-SINGLE-GAP-COMPLEX-01','INTERFACE_CARD')]:
 c.execute('insert into result_sources(result_id,source_id,role) values(?,?,?)',(RID,sid,role))

ev=[
 ('EVID-CARD-'+RID,RID,'REUSABLE_CARD','/Recherche/01_BRIQUES_REUTILISABLES/BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md',sha(CARD),'Carte atomique réutilisable.','CARD_REVIEWED',TS),
 ('EVID-CHECK-'+RID,RID,'EXACT_RECHECK','/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json',sha(CHECKS),'Deux expériences décisives indépendantes.','EXECUTED',TS),
 ('EVID-AUDIT-'+RID,RID,'RAVI2_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md',sha(AUDIT),'Audit preuve, portée, redondance et bibliographie.','INTERNAL_REVIEWED',TS)]
for x in ev:c.execute('insert into evidence values(?,?,?,?,?,?,?,?)',x)

c.execute('insert into audits values(?,?,?,?,?,?,?,?,?)',(
 'AUD-SINGLE-GAP-COMPLEX-22',RID,'TEMPS_REGLE90','RAVI2_PROOF_SCOPE_REDUNDANCY_BIBLIOGRAPHY','PASS',
 'proof_reconstruction;factor_complexity_exhaustive;right_special_checker;targeted_bibliography',
 '/Recherche/03_AUDITS_CERTIFICATS/AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md',note,TS))

next_rel=c.execute('select coalesce(max(relation_id),0)+1 from relations').fetchone()[0]
c.execute('insert into relations(relation_id,source_result_id,relation_type,target_result_id,note,created_at) values(?,?,?,?,?,?)',(
 next_rel,RID,'GENERALISE','BR-TIME-FACTOR-COMPLEX-01',
 'Spécialisation k=(m-1)/2, g=2m, h=3m reproduit exactement le profil de BR-TIME-FACTOR-COMPLEX-01; relation non causale, aucun nouveau DEPEND_DE.',TS))

c.execute("insert or replace into meta(key,value) values('last_scientific_commit',?)",(CID,))
c.execute("insert or replace into meta(key,value) values('last_scientific_commit_at',?)",(TS,))
c.commit()

integrity=c.execute('pragma integrity_check').fetchone()[0]
fk=c.execute('pragma foreign_key_check').fetchall()
after={
 'results':c.execute('select count(*) from results').fetchone()[0],
 'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
 'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
 'relations':c.execute('select count(*) from relations').fetchone()[0],
 'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert after=={'results':86,'admissible':82,'dep':47,'relations':79,'versions':96},after
assert integrity=='ok' and not fk,(integrity,fk)
# causal cycle check only on DEPEND_DE
edges=c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'").fetchall()
g={}
for a,b in edges:g.setdefault(a,[]).append(b)
def cyc(v,stack,seen):
 if v in stack:return True
 if v in seen:return False
 seen.add(v);stack.add(v)
 for u in g.get(v,[]):
  if cyc(u,stack,seen):return True
 stack.remove(v);return False
has_cycle=any(cyc(v,set(),set()) for v in list(g))
assert not has_cycle
out={'commit':CID,'timestamp':TS,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':0,
     'main_sha256_before':pre_sha,'main_sha256_after':sha(DB),'backup_sha256':sha(BACKUP),'new_result':RID,
     'relation':{'type':'GENERALISE','target':'BR-TIME-FACTOR-COMPLEX-01','relation_id':next_rel},
     'checks_sha256':sha(CHECKS),'audit_sha256':sha(AUDIT),'card_sha256':sha(CARD)}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))