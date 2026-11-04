import sqlite3,json,hashlib,shutil,os
from pathlib import Path
from datetime import datetime,timezone

DB=Path('/mnt/data/audit_db/RESEARCH_MEMORY.sqlite')
BACKUP=Path('/mnt/data/audit_db/RESEARCH_MEMORY_PRE_CATCHUP20.sqlite')
CID='COMMIT-RAVI2-2026-10-19-CATCHUP-20'
TS=datetime.now(timezone.utc).isoformat()
AUDIT=Path('/mnt/data/catchup_commit/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md')
CHECKS=Path('/mnt/data/CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json')
CHECKER=Path('/mnt/data/catchup_commit_checker.py')
CARD_DIR=Path('/mnt/data/catchup_commit/cards')
SCHSRC=Path('/mnt/data/catchup_domains/fermeture_mathematique_extensions_2026-10-13.md')
TRSRC=Path('/mnt/data/catchup_domains/theorie_transformations_2026-10-12.md')
DETSRC=Path('/mnt/data/catchup_domains/detection_correlations_2026-10-14.md')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in [AUDIT,CHECKS,CHECKER,SCHSRC,TRSRC,DETSRC]: assert p.exists(),p

rows=[
 dict(result_id='SCH-POLY-CLOSURE-01',project_id='DELTA_H_FERMETURE',result_type='THEOREM',
      title="Fermeture polynomiale d'un opérateur d'ordre deux",
      statement=("Pour L=-P(z)D_z^2+A(z)D_z+B(z) et P_N=span{1,...,z^N}, N>=2 : invariance de P_N ssi deg(P,A,B)<= (4,3,2) et A3=2(N-1)P4, B2=-N(N-1)P4, B1=N(N-1)P3-NA2. Deux indices distincts N,M imposent deg P<=3, deg A<=2, B affine, A2=(N+M-1)P3, B1=-NM P3. Trois indices distincts imposent deg P<=2, deg A<=1, B constant et donc invariance de tous P_n. Deux secteurs seuls ne suffisent pas en général."),
      domain="Opérateur différentiel scalaire d'ordre deux dans une même variable z et une même représentation ; modules polynomiaux complets P_N, N>=2.",
      assumptions=['même opérateur','même coordonnée z','même jauge/représentation','N,M,K entiers >=2 distincts lorsque requis'],
      originality='INDÉTERMINÉ',
      note="Preuve directe par coefficients de degré. Contrôle indépendant 2026-10-19 : T1 792 images, T2 880, T3 1092, contre-exemples 483. Classifications générales antérieures Post–Turbiner/Turbiner ; aucune priorité exacte revendiquée.",
      card='SCH-POLY-CLOSURE-01_BRIQUE.md',src='SCH'),
 dict(result_id='SCH-SEXTIC-PARITY-01',project_id='DELTA_H_FERMETURE',result_type='THEOREM_EXAMPLE',
      title='Secteur polynomial régulier du potentiel sextique',
      statement=("Pour sigma in {0,1}, g=ax^4/4+bx^2/2 et M_{N,sigma}=x^sigma e^{-g}P_N(x^2), H=-D_x^2+V préserve M_{N,sigma} exactement si V=a^2x^6+2abx^4+[b^2-a(4N+2sigma+3)]x^2+E-(2sigma+1)b. Si a!=0, le même potentiel et la même jauge ne préservent pas deux secteurs distincts (N,sigma); si a=0, on retrouve une suite complète pour les deux parités."),
      domain="Schrödinger unidimensionnel formel/régulier ; N>=2 ; sigma=0 ou 1 ; jauge quartique-paire fixée.",
      assumptions=['N>=2','sigma in {0,1}','g=ax^4/4+bx^2/2','même potentiel et même jauge pour la comparaison de secteurs'],
      originality='CONNU_OU_CLASSIQUE',
      note="Famille quasi-exactement soluble connue. Contrôle rationnel indépendant : 4752 images de monômes. Ne traite pas la normalisabilité globale ni les domaines auto-adjoints.",
      card='SCH-SEXTIC-PARITY-01_BRIQUE.md',src='SCH'),
 dict(result_id='BR-STATE-COST-01',project_id='TRANSFORMATIONS_AUTONOMIE',result_type='THEOREM',
      title="Coût minimal d'extension par fermeture des comportements",
      statement=("Si F_old est un ensemble fini de comportements d'un dispositif déterministe total fermé sous dérivées et B_req un ensemble de comportements exacts requis, alors pour C=Der(F_old union B_req), le nombre minimal d'états ajoutés sans modifier les anciens vaut |C\\F_old| lorsque cet ensemble est fini ; s'il est infini, aucune extension déterministe finie ne convient."),
      domain="Dispositifs déterministes totaux ; comportements exacts sous toutes les continuations admises ; coût = nombre d'états ajoutés.",
      assumptions=['ancien dispositif fini déterministe total','F_old fermé sous dérivées','réponses requises exactes','anciens comportements inchangés','coût compte seulement les états ajoutés'],
      originality='CONNU_OU_CLASSIQUE',
      note="Preuve par distinction des comportements dérivés et construction réciproque un état par dérivée nouvelle. 124 contrôles finis indépendants sur systèmes de dérivées jouets.",
      card='BR-STATE-COST-01_BRIQUE.md',src='TRANS'),
 dict(result_id='DET-FIN-01',project_id='TRANSFORMATIONS_AUTONOMIE',result_type='THEOREM',
      title="Perte asymptotique de sensibilité d'un détecteur fini à risque total borné",
      statement=("Pour un détecteur déterministe à mémoire finie avec alerte absorbante, si sous le nul chaque symbole conditionnel admissible a probabilité >=eta>0 et P0(T<infty)<=alpha<1, alors pour toute loi Q_n identique au nul pendant n observations puis arbitraire sur le même alphabet, sup_Qn P_Qn(n<T<infty | T>n) -> 0 quand n->infty."),
      domain="Détection séquentielle par automate déterministe fini ; alphabet fini ; critère de probabilité totale de fausse alarme.",
      assumptions=['mémoire persistante et horloge incluses dans un état fini','alerte absorbante','alphabet fini','plancher conditionnel eta>0 sous le nul','risque total alpha<1','changement identique au nul jusqu à n'],
      originality='INDÉTERMINÉ',
      note="Preuve par masse des états encore capables d atteindre l alerte et chemin simple de longueur <=M. Lemme de graphe revérifié exhaustivement sur 4181 automates binaires à 1-3 états non-alertes et 12454 états.",
      card='DET-FIN-01_BRIQUE.md',src='DETECT'),
 dict(result_id='BR-Q-SWAP-MEM-01',project_id='QUANTIQUE',result_type='THEOREM_EXAMPLE',
      title='Témoin SWAP de mémoire relative aux continuations',
      statement=("Pour V=SWAP et H=(pi*hbar/(2tau))(I-V), U(tau)=V et U(2tau)=I. Depuis |b,0>, l état réduit de S à tau est |0><0| pour b=0,1, mais la même continuation restitue b sur S. Sans mémoire extérieure, un environnement de dimension 1 est impossible pour ce témoin et dimension 2 suffit."),
      domain="Deux qubits, évolution unitaire SWAP ; comparaison de continuations après réduction du système S.",
      assumptions=['évolution unitaire fermée sur S⊗E','même continuation pour les deux préparations','aucune mémoire extérieure au système décrit pour la borne de dimension'],
      originality='CONNU_OU_CLASSIQUE',
      note="Identités matricielles exactes revérifiées. Le témoin n établit pas une mémoire irréductiblement quantique : deux étiquettes classiques reproduisent les deux préparations.",
      card='BR-Q-SWAP-MEM-01_BRIQUE.md',src='TRANS'),
 dict(result_id='DESC-CLIP-01',project_id='TRANSFORMATIONS_AUTONOMIE',result_type='THEOREM',
      title="Projection locale d'un facteur d'évidence robuste",
      statement=("Pour un nul Bernoulli p dans [l,u] et une candidate q, poser p*=clip(q,[l,u]), f*(1)=q/p*, f*(0)=(1-q)/(1-p*). Alors E_p f*(Y)<=1 pour tout p dans [l,u]; f* domine point par point la règle conservatrice q/u,(1-q)/(1-l); à prédicteurs/resets/seuils identiques le temps de première alarme projeté est <= l ancien; et f* maximise localement E_q log f parmi les facteurs continus valides sur l intervalle."),
      domain="Facteurs d'évidence binaires robustes sous intervalle nul ; supermartingales de test ; même prédicteur et même mécanique de score pour la dominance temporelle.",
      assumptions=['0<l<=u<1','q in [0,1]','nul conditionnel p in [l,u]','mêmes prédicteurs, resets et seuils pour la comparaison temporelle'],
      originality='NON_EVALUE',
      note="Preuve analytique reconstruite ; 50 cas rationnels indépendants vérifient validité et dominance. Aucun registre persistant supplémentaire requis. Dominance d alarme != garantie uniforme de puissance post-changement.",
      card='DESC-CLIP-01_BRIQUE.md',src='DETECT'),
]

# Backup and connect
shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
before={'results':c.execute('select count(*) from results').fetchone()[0],
        'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
        'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
        'versions':c.execute('select count(*) from result_versions').fetchone()[0]}
assert before=={'results':77,'admissible':73,'dep':44,'versions':87},before
for r in rows: assert not c.execute('select 1 from results where result_id=?',(r['result_id'],)).fetchone(),r['result_id']
assert json.load(open(CHECKS))['all_pass'] is True

# reusable sources
source_rows=[
 ('SRC-CATCHUP-SCHR-20261019','INTERNAL_RESEARCH_NOTE','Fermeture mathématique : parité, coordonnées et espaces lacunaires',None,2026,'/Recherche/02_PROGRAMMES_ACTIFS/Delta_h_Fermeture/Notes/fermeture_mathematique_extensions_2026-10-13.md',0,TS,'Preuves directes et contrôles exacts ; portée algébrique/localement Schrödinger.'),
 ('SRC-CATCHUP-TRANS-20261019','INTERNAL_RESEARCH_NOTE','Théorie des transformations — reconstruction et audit 0.2',None,2026,'/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/theorie_transformations_2026-10-12.md',0,TS,'Source P5 et témoin SWAP ; audit de portée inclus.'),
 ('SRC-CATCHUP-DETECT-20261019','INTERNAL_RESEARCH_NOTE','Détection de corrélations et surveillance de description',None,2026,'/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md',0,TS,'Source DET-FIN-01 et facteur projeté.'),
 ('SRC-CATCHUP-AUDIT-20261019','INTERNAL_AUDIT','Audit RAVI-2 — commit de rattrapage des briques orphelines',None,2026,'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md',0,TS,'Audit du commit catchup20.'),
 ('SRC-CATCHUP-CHECKS-20261019','EXECUTED_CHECKER','CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json',None,2026,'/Recherche/04_CODE_DONNEES/CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json',0,TS,'Contrôles exacts exécutés le 19 octobre 2026.')]

c.execute('BEGIN IMMEDIATE')
try:
  for srow in source_rows:
    c.execute('insert into sources(source_id,source_type,title,authors,year,locator,peer_reviewed,verified_at,notes) values (?,?,?,?,?,?,?,?,?)',srow)
  for r in rows:
    row={k:r[k] for k in []}
    dbrow=dict(result_id=r['result_id'],project_id=r['project_id'],result_type=r['result_type'],title=r['title'],statement=r['statement'],domain=r['domain'],assumptions_json=json.dumps(r['assumptions'],ensure_ascii=False),epistemic_status='DÉMONTRÉ',originality_status=r['originality'],confidence_note=r['note'],version=1,created_at=TS,updated_at=TS)
    cols=list(dbrow)
    c.execute(f"insert into results({','.join(cols)}) values ({','.join(['?']*len(cols))})",[dbrow[k] for k in cols])
    c.execute('insert into result_versions(result_id,version,row_json,lifecycle,premise_allowed,commit_id,archived_at) values (?,?,?,?,?,?,?)',(r['result_id'],1,json.dumps(dbrow,ensure_ascii=False,sort_keys=True),'ACTIVE',1,CID,TS))
    # card source
    sid='SRC-CARD-'+r['result_id']
    card= CARD_DIR/r['card']
    final_card='/Recherche/01_BRIQUES_REUTILISABLES/'+r['card']
    c.execute('insert into sources(source_id,source_type,title,authors,year,locator,peer_reviewed,verified_at,notes) values (?,?,?,?,?,?,?,?,?)',(sid,'LIBRARY_CARD',r['card'],None,2026,final_card,0,TS,'Carte créée lors du rattrapage RAVI-2 du 19 octobre 2026.'))
    srcid={'SCH':'SRC-CATCHUP-SCHR-20261019','TRANS':'SRC-CATCHUP-TRANS-20261019','DETECT':'SRC-CATCHUP-DETECT-20261019'}[r['src']]
    for sr,role in [(sid,'INTERFACE_CARD'),(srcid,'PRIMARY_INTERNAL'),('SRC-CATCHUP-AUDIT-20261019','AUDIT'),('SRC-CATCHUP-CHECKS-20261019','VALIDATION')]:
      c.execute('insert into result_sources(result_id,source_id,role) values (?,?,?)',(r['result_id'],sr,role))
    srcpath={'SCH':SCHSRC,'TRANS':TRSRC,'DETECT':DETSRC}[r['src']]
    evid=[
      ('EVID-CARD-'+r['result_id'],'REUSABLE_CARD',final_card,sha(card),'Carte atomique réutilisable.','CARD_REVIEWED'),
      ('EVID-SRC-'+r['result_id'],'PRIMARY_INTERNAL_ARTIFACT',source_rows[[x[0] for x in source_rows].index(srcid)][5],sha(srcpath),'Source interne contenant la preuve/reconstruction originale.','SOURCE_REVIEWED'),
      ('EVID-CHECK-'+r['result_id'],'EXACT_RECHECK','/Recherche/04_CODE_DONNEES/CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json',sha(CHECKS),'Contrôle indépendant exact du commit de rattrapage.','EXECUTED'),
      ('EVID-AUDIT-'+r['result_id'],'RAVI2_AUDIT','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md',sha(AUDIT),'Audit de portée, redondance, limites et décision de promotion.','INTERNAL_REVIEWED')]
    c.executemany('insert into evidence(evidence_id,result_id,evidence_type,locator,sha256,description,verification_status,created_at) values (?,?,?,?,?,?,?,?)',[(a,r['result_id'],b,d,e,f,g,TS) for a,b,d,e,f,g in evid])
    c.execute('insert into audits(audit_id,result_id,project_id,audit_type,outcome,performed_by,artifact_locator,notes,created_at) values (?,?,?,?,?,?,?,?,?)',('AUD-CATCHUP20-'+r['result_id'],r['result_id'],r['project_id'],'RAVI2_CATCHUP_PROOF_SCOPE_REDUNDANCY','PASS','proof_reconstruction;exact_checker;library_crosscheck;targeted_bibliography','/Recherche/03_AUDITS_CERTIFICATS/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md',r['note'],TS))
    c.execute('insert into regression_tests(test_id,result_id,name,kind,status,artifact_locator,last_run_at,notes) values (?,?,?,?,?,?,?,?)',('REG-CATCHUP20-'+r['result_id'],r['result_id'],'Rattrapage exact '+r['result_id'],'EXACT','PASS','/Recherche/04_CODE_DONNEES/CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json',TS,'Contrôles propres à la brique consignés dans le JSON de validation.'))
    c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values (?,?,?,?,?)',('result',r['result_id'],'CREATED',json.dumps({'commit':CID,'audit':'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md','internal_only':True,'catchup':True},ensure_ascii=False),TS))
  # bibliography passes
  c.execute('insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at) values (?,?,?,?,?,?,?)',('BIB-CATCHUP20-SCHR','DELTA_H_FERMETURE','FINAL_TARGETED','invariant polynomial subspace second order differential operator; quasi-exactly solvable Schrödinger sextic','Internal note + Post–Turbiner 1993 + Turbiner 1994/2016','Classifications générales et famille sextique ont des antécédents clairs. Aucune nouveauté générale revendiquée; priorité exacte des formules T1–T3 laissée INDÉTERMINÉE.',TS))
  c.execute('insert into bibliography_passes(pass_id,project_id,stage,query,corpus_scope,findings,created_at) values (?,?,?,?,?,?,?)',('BIB-CATCHUP20-TRANS','TRANSFORMATIONS_AUTONOMIE','FINAL_CONSERVATIVE','finite-state behavior closure extension cost; finite-memory late change detector; robust e-value projection','Internal reports; no exhaustive priority search for exact formulations','P5/SWAP classés connus/classiques. DET-FIN-01 garde originalité INDÉTERMINÉE. DESC-CLIP-01 sans revendication de nouveauté générale.',TS))
  c.execute("insert or replace into meta(key,value) values ('last_scientific_commit_at',?)",(TS,))
  c.execute("insert or replace into meta(key,value) values ('last_scientific_commit',?)",(CID,))
  c.commit()
except Exception:
  c.rollback(); c.close(); shutil.copy2(BACKUP,DB); raise

# Controls
def cycle_check():
  graph={}
  for s,t in c.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'"):
    graph.setdefault(s,[]).append(t)
  visiting=set(); done=set()
  def dfs(u):
    if u in visiting: raise AssertionError('cycle:'+u)
    if u in done:return
    visiting.add(u)
    for v in graph.get(u,[]): dfs(v)
    visiting.remove(u);done.add(u)
  for u in list(graph): dfs(u)
cycle_check()
integrity=c.execute('pragma integrity_check').fetchone()[0]
fk=c.execute('pragma foreign_key_check').fetchall()
forbidden=c.execute("select count(*) from relations r left join certified_active_results x on x.result_id=r.target_result_id where r.relation_type='DEPEND_DE' and x.result_id is null").fetchone()[0]
after={'results':c.execute('select count(*) from results').fetchone()[0],
       'admissible':c.execute('select count(*) from certified_active_results').fetchone()[0],
       'dep':c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0],
       'versions':c.execute('select count(*) from result_versions').fetchone()[0],
       'status_counts':dict(c.execute('select epistemic_status,count(*) from results group by epistemic_status'))}
assert integrity=='ok' and not fk and forbidden==0
assert after['results']==83 and after['admissible']==79 and after['dep']==44 and after['versions']==93,after
for r in rows: assert c.execute('select 1 from certified_active_results where result_id=?',(r['result_id'],)).fetchone()
c.close()
out={'commit':CID,'before':before,'after':after,'integrity':integrity,'foreign_key_errors':len(fk),'causal_cycles':0,'forbidden_targets':forbidden,'main_sha256':sha(DB),'backup_sha256':sha(BACKUP),'new_results':[r['result_id'] for r in rows]}
Path('/mnt/data/catchup_commit/CATCHUP_COMMIT_CONTROLS_2026-10-19.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=False))