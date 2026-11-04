#!/usr/bin/env python3
import sqlite3,json,hashlib,shutil,datetime
from pathlib import Path
ROOT=Path('/mnt/data/qpred_20261020')
DB=ROOT/'RESEARCH_MEMORY.sqlite'
BACKUP=ROOT/'RESEARCH_MEMORY_PRE_QPRED24.sqlite'
CARD=ROOT/'BR-Q-PRED-HIDDEN-01_BRIQUE.md'
AUDIT=ROOT/'AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md'
CHECKS=ROOT/'Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json'
RID='BR-Q-PRED-HIDDEN-01'
CID='COMMIT-RAVI2-2026-10-20-Q-PRED-HIDDEN-24'
TS=datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

shutil.copy2(ROOT/'input'/'RESEARCH_MEMORY.sqlite',DB)
shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('pragma foreign_keys=on')
before={'results':c.execute('select count(*) from results').fetchone()[0],
        'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
        'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
        'relations':c.execute('select count(*) from relations').fetchone()[0],
        'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert before=={'results':87,'admissible':83,'dep':49,'relations':81,'versions':97},before
assert not c.execute('select 1 from results where result_id=?',(RID,)).fetchone()
assert c.execute("select 1 from certified_active_results where result_id='BR-STATE-01'").fetchone()
assert c.execute("select 1 from certified_active_results where result_id='BR-Q-SWAP-MEM-01'").fetchone()
checks=json.load(open(CHECKS))
assert checks['experiment_1_product_and_correlated_perfect_predictive_labels']['pass']
assert checks['experiment_2_raw_predictive_class_count_is_not_dimension_bounded']['pass']

statement=("Pour dim(S)=dim(E)=d>=2, parmi des histoires ayant le même état réduit instantané sur S, définir N_perf comme le nombre maximal d'histoires parfaitement distinguables par une même expérience future. "
           "Dans la classe produit sigma_S⊗tau_i^E, N_perf<=d et la borne est atteinte par des étiquettes orthogonales de E suivies de SWAP. "
           "En autorisant les corrélations S-E avec réduit I/d, N_perf<=d^2 et la borne est atteinte par les d^2 états de Bell généralisés, décodables par une continuation commune. "
           "En revanche le nombre brut de classes prédictives n'est pas borné par la dimension: déjà d_E=2 admet un continuum de classes via des états environnementaux non orthogonaux et SWAP.")
ass=[
 'S et E de dimension finie; pour les bornes exactes dim(S)=dim(E)=d>=2',
 'même état réduit instantané de S pour les histoires comparées',
 'même expérience future pour la distinguabilité parfaite',
 'la continuation peut contenir évolution conjointe fixe, mesure de S, reset de S et SWAP',
 'N_perf compte des histoires parfaitement distinguables, distinct du cardinal brut du quotient prédictif'
]
note=("Preuve exacte par orthogonalité des supports dans le cas produit, borne de dimension d^2 et base de Bell généralisée dans le cas corrélé. "
      "Checker d=2..10: orthogonalité, réduits I/d, décodeur et SWAP, erreur max <4e-15; branche continue d_E=2 échantillonnée sur 1001 points et preuve analytique P(0|theta)=cos^2(theta). "
      "Originalité externe connue/classique: dense coding/Bell, process tensors et témoins de dimension temporelle. Brique utile comme raccordement interne BR-STATE-01 / BR-Q-SWAP-MEM-01.")
row=(RID,'QUANTIQUE','THEOREM_BRIDGE','Séparation prédictive cachée : produit, corrélations et cardinalité',statement,
     'Processus quantiques finis; état réduit instantané versus prédiction multitemporelle; distinguabilité parfaite et mémoire environnementale.',
     json.dumps(ass,ensure_ascii=False),'DÉMONTRÉ','CONNU_OU_CLASSIQUE',note,1,TS,TS)
c.execute('insert into results values(?,?,?,?,?,?,?,?,?,?,?,?,?)',row)
r=dict(c.execute('select * from results where result_id=?',(RID,)).fetchone())
c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values(?,?,?,?,?,?,?)',
          (RID,1,json.dumps(r,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))

sources=[
 ('SRC-QPRED-AUDIT-20261020','INTERNAL_AUDIT','Audit RAVI-2 — séparation prédictive cachée quantique',None,2026,'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md',0,TS,'Preuve, deux expériences décisives, redondance et audit bibliographique.'),
 ('SRC-QPRED-CHECKS-20261020','EXECUTED_CHECKER','Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json',None,2026,'/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json',0,TS,'Contrôles exacts numériques d=2..10 et adversaire continuum.'),
 ('SRC-CARD-'+RID,'LIBRARY_CARD','BR-Q-PRED-HIDDEN-01_BRIQUE.md',None,2026,'/Recherche/01_BRIQUES_REUTILISABLES/BR-Q-PRED-HIDDEN-01_BRIQUE.md',0,TS,'Carte atomique réutilisable.'),
 ('SRC-QPRED-VIEIRA2024','PEER_REVIEWED_ARTICLE','Witnessing environment dimension through temporal correlations','Lucas B. Vieira; Simon Milz; Giuseppe Vitagliano; Costantino Budroni',2024,'DOI:10.22331/q-2024-01-10-1224',1,TS,'Cadre de témoins de dimension environnementale par corrélations temporelles.'),
 ('SRC-QPRED-PRXQ2021','PEER_REVIEWED_ARTICLE','Quantum Stochastic Processes and Quantum non-Markovian Phenomena',None,2021,'DOI:10.1103/PRXQuantum.2.030201',1,TS,'Process tensor, mémoire et dimension effective environnementale / MPO.'),
 ('SRC-QPRED-DENSE2010','PEER_REVIEWED_ARTICLE','Overcoming a limitation of deterministic dense coding with a nonmaximally entangled initial state','P. S. Bourdon; E. Gerjuoy',2010,'DOI:10.1103/PhysRevA.81.022314',1,TS,'Rappelle la capacité d^2 du dense coding avec état maximalement intriqué.'),
 ('SRC-QPRED-ELLIOTT2026','PREPRINT','Causal memory and structural complexity of correlated quantum sequences','Thomas J. Elliott',2026,'arXiv:2610.06519v2',0,TS,'Contexte récent sur mémoire causale minimale de séquences quantiques corrélées.')]
for s in sources: c.execute('insert or replace into sources values(?,?,?,?,?,?,?,?,?)',s)
for sid,role in [
 ('SRC-QPRED-AUDIT-20261020','AUDIT'),('SRC-QPRED-CHECKS-20261020','VALIDATION'),('SRC-CARD-'+RID,'INTERFACE_CARD'),
 ('SRC-QPRED-VIEIRA2024','BIBLIOGRAPHY'),('SRC-QPRED-PRXQ2021','BIBLIOGRAPHY'),('SRC-QPRED-DENSE2010','BIBLIOGRAPHY'),('SRC-QPRED-ELLIOTT2026','BIBLIOGRAPHY')]:
 c.execute('insert into result_sources(result_id,source_id,role) values(?,?,?)',(RID,sid,role))

ev=[
 ('EVID-CARD-'+RID,RID,'REUSABLE_CARD','/Recherche/01_BRIQUES_REUTILISABLES/BR-Q-PRED-HIDDEN-01_BRIQUE.md',sha(CARD),'Carte réutilisable du raccordement prédictif quantique.','CARD_REVIEWED',TS),
 ('EVID-CHECK-'+RID,RID,'EXACT_RECHECK','/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json',sha(CHECKS),'Deux expériences décisives; d=2..10 et branche continue.','EXECUTED',TS),
 ('EVID-AUDIT-'+RID,RID,'RAVI2_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md',sha(AUDIT),'Audit preuve, portée, métrique, redondance et bibliographie.','INTERNAL_REVIEWED',TS)]
for x in ev:c.execute('insert into evidence values(?,?,?,?,?,?,?,?)',x)
c.execute('insert into audits values(?,?,?,?,?,?,?,?,?)',(
 'AUD-QPRED-HIDDEN-24',RID,'QUANTIQUE','RAVI2_PROOF_SCOPE_REDUNDANCY_BIBLIOGRAPHY','PASS',
 'proof_reconstruction;bell_family_check;continuum_counterexample;targeted_bibliography',
 '/Recherche/03_AUDITS_CERTIFICATS/AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md',note,TS))
c.execute('insert into regression_tests values(?,?,?,?,?,?,?,?)',(
 'TEST-QPRED-HIDDEN-24',RID,'Bell/SWAP predictive separation d=2..10 + continuum','EXACT_NUMERIC','PASS',
 '/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json',TS,'Erreur max <4e-15; 1001/1001 réponses distinctes dans échantillon continuum.'))
# Informative, non-causal relations only; no DEPEND_DE inflation.
c.execute('insert into relations(source_result_id,relation_type,target_result_id,note,created_at) values(?,?,?,?,?)',(
 RID,'GENERALISE','BR-Q-SWAP-MEM-01','Le cas produit d=2 redonne exactement le témoin SWAP binaire; le résultat étend à d et distingue le régime corrélé d^2.',TS))
c.execute('insert into relations(source_result_id,relation_type,target_result_id,note,created_at) values(?,?,?,?,?)',(
 RID,'ILLUSTRE','BR-STATE-01','Instanciation quantique du quotient prédictif: même réduit instantané mais lois futures distinctes; correction du cardinal brut par N_perf.',TS))
c.execute("insert or replace into meta(key,value) values('last_scientific_commit',?)",(CID,))
c.execute("insert or replace into meta(key,value) values('last_scientific_commit_at',?)",(TS,))
c.commit()
integ=c.execute('pragma integrity_check').fetchone()[0]; fk=c.execute('pragma foreign_key_check').fetchall()
after={'results':c.execute('select count(*) from results').fetchone()[0],
       'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
       'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
       'relations':c.execute('select count(*) from relations').fetchone()[0],
       'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert after=={'results':88,'admissible':84,'dep':49,'relations':83,'versions':98},after
assert integ=='ok' and not fk,(integ,fk)
# cycle test only DEPEND_DE
edges=c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'").fetchall(); g={}
for a,b in edges:g.setdefault(a,[]).append(b)
seen=set(); stack=set()
def dfs(v):
 if v in stack:return True
 if v in seen:return False
 seen.add(v); stack.add(v)
 if any(dfs(u) for u in g.get(v,[])):return True
 stack.remove(v); return False
cyc=any(dfs(v) for v in list(g))
assert not cyc
out={'commit':CID,'timestamp':TS,'before':before,'after':after,'integrity':integ,'foreign_key_errors':len(fk),'causal_cycles':int(cyc),
     'new_result':RID,'new_depend_de':0,'informative_relations':['GENERALISE -> BR-Q-SWAP-MEM-01','ILLUSTRE -> BR-STATE-01'],
     'originality':'CONNU_OU_CLASSIQUE','checks':checks,'main_sha256':sha(DB),'backup_sha256':sha(BACKUP),'card_sha256':sha(CARD),'audit_sha256':sha(AUDIT)}
(ROOT/'Q_PREDICTIVE_HIDDEN_COMMIT_CONTROLS_2026-10-20.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps({'before':before,'after':after,'integrity':integ,'commit':CID},indent=2,ensure_ascii=False))
c.close()