import sqlite3, json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('/mnt/data/time_predictive_commit')
DB=ROOT/'RESEARCH_MEMORY.sqlite'
BACKUP=ROOT/'RESEARCH_MEMORY_PRE_TIME_PREDICTIVE.sqlite'
CID='COMMIT-RAVI2-2026-10-19-TIME-PREDICTIVE-21'
TS=datetime.now(timezone.utc).isoformat()
AUDIT=ROOT/'AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md'
CHECKS=ROOT/'TIME_PREDICTIVE_CHECKS_2026-10-19.json'
CHECKER=ROOT/'time_predictive_checks_2026-10-19.py'
CARD1=ROOT/'BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md'
CARD2=ROOT/'BR-TIME-FINDET-BRIDGE-01_BRIQUE.md'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in [DB,AUDIT,CHECKS,CHECKER,CARD1,CARD2]: assert p.exists(),p
assert json.load(open(CHECKS,encoding='utf-8'))['all_pass'] is True
shutil.copy2(DB,BACKUP)

rows=[
 dict(result_id='BR-TIME-FACTOR-COMPLEX-01',project_id='TEMPS_REGLE90',result_type='THEOREM',
      title='Complexité prédictive exacte du compteur réversible sparse',
      statement=('Pour le mot cyclique binaire s_m de BR-TIME-01, m>=5 impair, T=m^2, le nombre p_m(L) de facteurs cycliques distincts de longueur L vaut: L+1 pour 1<=L<=2m; 2L-2m+1 pour 2m<L<3m; L+m pour 3m<=L<=T-m; T pour T-m<L<=T. En particulier p_m(3m)=4m=4sqrt(T).'),
      domain='Mot cyclique binaire observé de la famille réversible BR-TIME-01 ; complexité en facteurs / résumés prédictifs finis-horizons.',
      assumptions=['m impair >=5','T=m^2','mot observé s_m de BR-TIME-01','facteurs cycliques exacts de longueur L'],
      originality='INDÉTERMINÉ',
      note='Preuve par structure des écarts 2m,...,2m,3m puis réduction au mot cyclique 0101...0 à unique défaut 00. 5446 cas exhaustifs + 489 tests adversariaux, zéro échec.',
      card=CARD1),
 dict(result_id='BR-TIME-FINDET-BRIDGE-01',project_id='TEMPS_REGLE90',result_type='BRIDGE_THEOREM',
      title='Distinguabilité de phase versus détection persistante à mémoire finie',
      statement=('Pour m>=5 impair, sous la loi nulle P_m obtenue par phase initiale uniforme du mot s_m, toute probabilité conditionnelle positive du prochain symbole est >=1/T. Ainsi tout détecteur déterministe fini à alerte absorbante et risque total P_m(tau<inf)<=alpha<1 satisfait, pour les changements de phase Q_{m,n,d} identiques au nul pendant n observations, sup_d P(n<tau<inf | tau>n)->0 quand n->inf. Pourtant les décalages non multiples de m sont distinguables en au plus 3m observations et p_m(3m)=4m.'),
      domain='Processus périodique réversible à phase aléatoire ; détection séquentielle par automate fini avec probabilité totale de fausse alarme.',
      assumptions=['m impair >=5','phase initiale uniforme sur Z_T','détecteur déterministe fini','alerte absorbante','risque total alpha<1','changement de phase identique au nul pendant n observations'],
      originality='INDÉTERMINÉ',
      note='Interface DET-FIN vérifiée: 280941 probabilités conditionnelles positives >=1/T et 70440 préfixes pré-changement identiques. DET-FIN-01 utilisé comme prémisse certifiée, non réaudité.',
      card=CARD2)
]

c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={'results':c.execute('select count(*) from results').fetchone()[0],
        'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
        'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
        'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert before=={'results':83,'admissible':79,'dep':44,'versions':93},before
for r in rows: assert not c.execute('select 1 from results where result_id=?',(r['result_id'],)).fetchone(),r['result_id']
for prem in ['BR-TIME-01','DET-FIN-01']:
    assert c.execute('select 1 from certified_active_results where result_id=?',(prem,)).fetchone(),prem

sources=[
 ('SRC-TIME-PRED-AUDIT-20261019','INTERNAL_AUDIT','Audit RAVI-2 — complexité prédictive et détecteurs finis',None,2026,'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md',0,TS,'Audit preuve, redondance, bibliographie et limites.'),
 ('SRC-TIME-PRED-CHECKS-20261019','EXECUTED_CHECKER','TIME_PREDICTIVE_CHECKS_2026-10-19.json',None,2026,'/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/TIME_PREDICTIVE_CHECKS_2026-10-19.json',0,TS,'Contrôles exacts exécutés le 19 octobre 2026.'),
 ('SRC-CARD-BR-TIME-FACTOR-COMPLEX-01','LIBRARY_CARD','BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md',None,2026,'/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md',0,TS,'Carte atomique du théorème de complexité prédictive.'),
 ('SRC-CARD-BR-TIME-FINDET-BRIDGE-01','LIBRARY_CARD','BR-TIME-FINDET-BRIDGE-01_BRIQUE.md',None,2026,'/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FINDET-BRIDGE-01_BRIQUE.md',0,TS,'Carte atomique du raccordement temps/détection finie.')
]

c.execute('BEGIN IMMEDIATE')
try:
    for s in sources:
        c.execute('insert into sources(source_id,source_type,title,authors,year,locator,peer_reviewed,verified_at,notes) values (?,?,?,?,?,?,?,?,?)',s)
    for r in rows:
        dbrow=dict(result_id=r['result_id'],project_id=r['project_id'],result_type=r['result_type'],title=r['title'],statement=r['statement'],domain=r['domain'],assumptions_json=json.dumps(r['assumptions'],ensure_ascii=False),epistemic_status='DÉMONTRÉ',originality_status=r['originality'],confidence_note=r['note'],version=1,created_at=TS,updated_at=TS)
        cols=list(dbrow)
        c.execute(f"insert into results({','.join(cols)}) values ({','.join(['?']*len(cols))})",[dbrow[k] for k in cols])
        c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values (?,?,?,?,?,?,?)',(r['result_id'],1,json.dumps(dbrow,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))
        card_sid='SRC-CARD-'+r['result_id']
        source_links=[(card_sid,'INTERFACE_CARD'),('SRC-TIME-PRED-AUDIT-20261019','AUDIT'),('SRC-TIME-PRED-CHECKS-20261019','VALIDATION')]
        if r['result_id']=='BR-TIME-FACTOR-COMPLEX-01': source_links.append(('SRC-PROOF-R90-AUDIT','PRIMARY_INTERNAL'))
        else: source_links.extend([('SRC-CARD-DET-FIN-01','PREMISE_INTERFACE'),('SRC-CARD-BR-TIME-FACTOR-COMPLEX-01','PREMISE_INTERFACE')])
        for sid,role in source_links:
            c.execute('insert into result_sources(result_id,source_id,role) values (?,?,?)',(r['result_id'],sid,role))
        evid=[
          ('EVID-CARD-'+r['result_id'],'REUSABLE_CARD','/Recherche/01_BRIQUES_REUTILISABLES/'+r['card'].name,sha(r['card']),'Carte atomique réutilisable.','CARD_REVIEWED'),
          ('EVID-CHECK-'+r['result_id'],'EXACT_RECHECK','/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/TIME_PREDICTIVE_CHECKS_2026-10-19.json',sha(CHECKS),'Contrôles indépendants exacts et d interface.','EXECUTED'),
          ('EVID-AUDIT-'+r['result_id'],'RAVI2_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md',sha(AUDIT),'Audit de preuve, redondance, littérature et décision.','INTERNAL_REVIEWED')]
        c.executemany('insert into evidence(evidence_id,result_id,evidence_type,locator,sha256,description,verification_status,created_at) values (?,?,?,?,?,?,?,?)',[(a,r['result_id'],b,d,e,f,g,TS) for a,b,d,e,f,g in evid])
        c.execute('insert into audits(audit_id,result_id,project_id,audit_type,outcome,performed_by,artifact_locator,notes,created_at) values (?,?,?,?,?,?,?,?,?)',('AUD-TIME-PRED-'+r['result_id'],r['result_id'],r['project_id'],'RAVI2_PROOF_SCOPE_REDUNDANCY_BIBLIOGRAPHY','PASS','proof_reconstruction;exact_checker;interface_checker;targeted_bibliography','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md',r['note'],TS))
        c.execute('insert into regression_tests(test_id,result_id,name,kind,status,artifact_locator,last_run_at,notes) values (?,?,?,?,?,?,?,?)',('REG-TIME-PRED-'+r['result_id'],r['result_id'],'Régression '+r['result_id'],'EXACT','PASS','/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/TIME_PREDICTIVE_CHECKS_2026-10-19.json',TS,'Tests propres à la brique consignés dans le JSON de validation.'))
        c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',('result',r['result_id'],'CREATED',json.dumps({'commit':CID,'audit':'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md','internal_only':True},ensure_ascii=False),TS))
    deps=[
      ('BR-TIME-FACTOR-COMPLEX-01','BR-TIME-01','La formule de complexité utilise la construction et la borne de résolution de BR-TIME-01.'),
      ('BR-TIME-FINDET-BRIDGE-01','BR-TIME-FACTOR-COMPLEX-01','Le raccordement utilise le profil exact p_m et son corollaire p_m(3m)=4m.'),
      ('BR-TIME-FINDET-BRIDGE-01','DET-FIN-01','La perte de sensibilité tardive est obtenue par application de DET-FIN-01 après vérification du plancher eta=1/T.')]
    for s,t,note in deps:
        c.execute('insert into relations(source_result_id,relation_type,target_result_id,note,created_at) values (?,?,?,?,?)',(s,'DEPEND_DE',t,note,TS))
    c.execute('insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at) values (?,?,?,?,?,?,?)',('BIB-TIME-PRED-20261019','TEMPS_REGLE90','FINAL_TARGETED','factor complexity periodic binary gap word 2m 3m; finite-state change detection periodic random phase total false alarm','Web targeted search + internal library','Factor complexity is classical (Morse-Hedlund, Allouche-Shallit; gap-function methods incl. Gheorghiciuc 2007). No exact match to the four-regime profile was located. Periodic/change detection literature exists, but no exact match to the finite-state random-phase total-risk bridge was located. Originality remains INDÉTERMINÉE.',TS))
    c.execute("insert or replace into meta(key,value) values ('last_scientific_commit_at',?)",(TS,))
    c.execute("insert or replace into meta(key,value) values ('last_scientific_commit',?)",(CID,))
    c.commit()
except Exception:
    c.rollback(); c.close(); shutil.copy2(BACKUP,DB); raise

# post controls
integrity=c.execute('pragma integrity_check').fetchone()[0]
fk=c.execute('pragma foreign_key_check').fetchall()
# dependency DAG
graph={}
for s,t in c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'"): graph.setdefault(s,[]).append(t)
vis=set();done=set()
def dfs(u):
    if u in vis: raise AssertionError('cycle '+u)
    if u in done:return
    vis.add(u)
    for v in graph.get(u,[]): dfs(v)
    vis.remove(u);done.add(u)
for u in list(graph): dfs(u)
forbidden=c.execute("select count(*) from relations r left join certified_active_results x on x.result_id=r.target_result_id where r.relation_type='DEPEND_DE' and x.result_id is null").fetchone()[0]
after={'results':c.execute('select count(*) from results').fetchone()[0],
       'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
       'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
       'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert integrity=='ok' and not fk and forbidden==0
assert after=={'results':85,'admissible':81,'dep':47,'versions':95},after
for rid in [r['result_id'] for r in rows]: assert c.execute('select 1 from certified_active_results where result_id=?',(rid,)).fetchone()
c.close()
out={'commit':CID,'timestamp':TS,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':0,'forbidden_targets':forbidden,'main_sha256':sha(DB),'backup_sha256':sha(BACKUP),'new_results':[r['result_id'] for r in rows],'new_dependencies':deps}
(ROOT/'TIME_PREDICTIVE_COMMIT_CONTROLS_2026-10-19.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=False))