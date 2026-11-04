import sqlite3,json,hashlib,shutil,datetime
from pathlib import Path
ROOT=Path(__file__).parent
REPORT=ROOT.parent/'REPRISE_MULTI_GAP_2026-10-20.md'
RID='BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01'
CID='COMMIT-RAVI2-2026-10-20-TWO-EQUAL-GAPS-25'
TS=datetime.datetime.now(datetime.timezone.utc).isoformat()
def js(x): return json.dumps(x,ensure_ascii=False,sort_keys=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(c,t): return sorted([tuple(r) for r in c.execute('select * from "'+t+'"')],key=repr)
def tables(c): return {r[0] for r in c.execute("select name from sqlite_master where type='table' and name!='sqlite_sequence'")}
main=sqlite3.connect(ROOT/'RESEARCH_MEMORY.sqlite');exp=sqlite3.connect(ROOT/'RESEARCH_MEMORY_RAVI2_V13_TEST.sqlite')
for c in [main,exp]:c.execute('pragma foreign_keys=on')
common=sorted(tables(main)&tables(exp))
assert len(common)==25,len(common)
assert all(rows(main,t)==rows(exp,t) for t in common)
old={t:rows(main,t) for t in common}
assert main.execute('select count(*) from results').fetchone()[0]==88
assert main.execute('select count(*) from certified_active_results').fetchone()[0]==84
assert not main.execute('select 1 from results where result_id=?',(RID,)).fetchone()
for name in ['RESEARCH_MEMORY.sqlite','RESEARCH_MEMORY_RAVI2_V13_TEST.sqlite']:
 shutil.copy2(ROOT/name,ROOT/(name+'.before_two_gap'))
domain='Mots binaires cycliques W=P^a0^delta P^b0^delta avec deux gaps exceptionnels identiques et separations inegales.'
ass=['g et delta entiers >=1','a,b entiers avec 1<=a<b','P=10^(g-1)','T=(a+b)g+2delta','facteurs cycliques de W ou facteurs de W infini periodique','1<=L<=T']
statement=('Pour g,delta>=1 et 1<=a<b entiers, P=10^(g-1), W=P^a0^delta P^b0^delta, T=(a+b)g+2delta, '
 'la complexite cyclique vaut p(L)=2+min(L-1,g+delta-2)+min(max(L-g,0),(b-1)g)+min(max(L-(a+1)g,0),ag+delta), 1<=L<=T. '
 'Les facteurs speciaux sont exactement Z_L pour 1<=L<=g+delta-2, B_L pour g<=L<=bg-1, C_L pour (a+1)g<=L<=(2a+1)g+delta-1. '
 'W est primitif et le premier horizon distinguant toutes les phases est max(bg,(2a+1)g+delta).')
note=('Preuve exhaustive par comparaison des contextes aux deux coupures exceptionnelles avec les coupures ordinaires; '
 'lcs=(min(c,j)+1)g-1 si c!=j; cas aligne c=j=a: (2a+1)g+delta-1. '
 'Deux algorithmes de controle: 288 familles/6720 longueurs et 1080 familles/40500 longueurs, reproduits depuis le code archive. '
 'Revue et calculs internes par le meme assistant; aucune revue humaine, autre modele ou verification formelle. '
 'Audit bibliographique cible effectue tardivement, non-conformite de sequence conservee; originalite indeterminee.')
report_locator='/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/REPRISE_MULTI_GAP_2026-10-20.md'
card_locator='/Recherche/01_BRIQUES_REUTILISABLES/'+RID+'_BRIQUE.md'
checks_locator='/Recherche/04_CODE_DONNEES/TWO_EQUAL_GAPS_CHECKS_2026-10-20.json'
cert_locator='/Recherche/03_AUDITS_CERTIFICATS/TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json'
script_locator='/Recherche/04_CODE_DONNEES/two_equal_gap_reproduce_20261020.py'
certificate={'result_id':RID,'commit_id':CID,'version':1,'validity':'DEMONSTRATED_INTERNAL','originality':'INDETERMINEE',
 'scope':domain,'assumptions':ass,'proof':report_locator,'proof_review':'EXHAUSTIVE_SUFFIX_CASE_ANALYSIS_INTERNAL',
 'independence':{'two_algorithmic_checks':True,'different_human_or_model_reviewer':False,'formal_proof_assistant':False},
 'checks':checks_locator,'budget':{'experiments':2,'reproduction_is_not_new_experiment':True},
 'procedure_nonconformity':'Targeted bibliography was completed after formula development; not retroactively described as an initial audit.',
 'nonconformity_disposition':'Explicitly retained; certification concerns internal mathematical validity, not novelty or external validation.',
 'bibliography_sources':['https://www.maths.tcd.ie/EMIS/journals/BBMS/Bulletin/bul971/cassaigne.pdf','https://arxiv.org/pdf/math/0512256','https://www.numdam.org/article/ITA_2013__47_2_195_0.pdf'],
 'redundancy':{'case_g_eq_delta_eq_1':'Existing single-gap theorem after complementation, no novelty claimed','general_case':'Not found among consulted internal cards; no exhaustive claim about all conversations'},
 'limits':['a=b excluded; repeated shorter period','no physical arrow of time','no arbitrary multiple-gap theorem','no scientific priority established'],
 'new_depend_de':0,'created_at':TS}
(ROOT/'TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json').write_text(json.dumps(certificate,ensure_ascii=False,indent=2)+'\n')
code=REPORT.read_text().split('```python\n')[-1].split('```')[0]
(ROOT/'two_equal_gap_reproduce_20261020.py').write_text(code)
checks={'result_id':RID,'status':'PASS','reproduced_from_persisted_source':True,'script_sha256':sha(ROOT/'two_equal_gap_reproduce_20261020.py'),
 'experiment1':{'g_delta_a':[1,4],'b':'a+1..7','families':288,'lengths':6720,'failures':0},
 'experiment2':{'g_delta':[1,6],'a':[1,5],'b':'a+1..9','families':1080,'lengths':40500,'failures':0},
 'arithmetic':'integer/string enumeration','executed_at':TS,'reproduction_output':['direct 288 6720','special 1080 40500']}
(ROOT/'TWO_EQUAL_GAPS_CHECKS_2026-10-20.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
card='# '+RID+' — Complexite cyclique a deux grands gaps identiques\n\nStatut : DÉMONTRÉ interne, certification interne RAVI-2 de validité. Originalité : INDÉTERMINÉE.\n\n'+statement+'\n\n## Domaine et hypotheses\n\n'+'\n'.join('- '+x for x in ass)+'\n\n## Preuve et limites\n\n'+note+'\n\nLa preuve autonome et ses sources sont dans '+report_locator+'. Aucun DEPEND_DE ajoute. Le cas g=delta=1 est deja couvert par la brique SINGLE-GAP apres complement. Le cas a=b est exclu.\n\nCertificat : '+cert_locator+'\nControles : '+checks_locator+'\nCode : '+script_locator+'\n'
(ROOT/(RID+'_BRIQUE.md')).write_text(card)
row=(RID,'TEMPS_REGLE90','THEOREM','Complexite cyclique et horizon de phase a deux gaps exceptionnels identiques',statement,domain,js(ass),'DÉMONTRÉ','INDÉTERMINÉ',note,1,TS,TS)
source_rows=[
 ('SRC-TWO-GAP-PROOF-20261020','INTERNAL_PROOF','Preuve par contextes de coupures',None,2026,report_locator,0,TS,note),
 ('SRC-TWO-GAP-CHECKS-20261020','EXECUTED_CHECKER','Reproduction des deux controles entiers',None,2026,checks_locator,0,TS,'288/6720 et 1080/40500; zero echec.'),
 ('SRC-TWO-GAP-CARD-20261020','LIBRARY_CARD',RID+'_BRIQUE.md',None,2026,card_locator,0,TS,'Carte atomique.'),
 ('SRC-TWO-GAP-CASSAIGNE1997','PEER_REVIEWED_ARTICLE','Complexite et facteurs speciaux','Julien Cassaigne',1997,'DOI:10.36045/bbms/1105730624',1,TS,'Methode classique; definitions et lien differences/facteurs speciaux consultes.'),
 ('SRC-TWO-GAP-GHEORGHICIUC2005','PREPRINT','The subword complexity of a class of infinite binary words','Irina Gheorghiciuc',2005,'https://arxiv.org/abs/math/0512256',0,TS,'Hypotheses injective/blockwise injective ne couvrent pas directement nos gaps periodiques non constants.'),
 ('SRC-TWO-GAP-BSCM2013','PEER_REVIEWED_ARTICLE','A note on constructing infinite binary words with polynomial subword complexity','F. Blanchet-Sadri; B. Chen; S. Munteanu',2013,'DOI:10.1051/ita/2013033',1,TS,'Texte consulte; construction de mots infinis a croissance polynomiale, pas notre formule cyclique.')]
ev=[
 ('EVID-TWO-GAP-PROOF',RID,'INTERNAL_PROOF',report_locator,sha(REPORT),note,'INTERNAL_REVIEWED',TS),
 ('EVID-TWO-GAP-CHECKS',RID,'EXACT_RECHECK',checks_locator,sha(ROOT/'TWO_EQUAL_GAPS_CHECKS_2026-10-20.json'),'Deux implementations algorithmiques; meme assistant.','EXECUTED',TS),
 ('EVID-TWO-GAP-CERT',RID,'RAVI2_AUDIT',cert_locator,sha(ROOT/'TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json'),'Certificat interne de validite; originalite separee.','INTERNAL_REVIEWED',TS),
 ('EVID-TWO-GAP-CARD',RID,'REUSABLE_CARD',card_locator,sha(ROOT/(RID+'_BRIQUE.md')),'Carte reutilisable.','CARD_REVIEWED',TS)]
strict={'result_id':RID,'result_version':1,'domain_family':'CYCLIC_BINARY_TWO_EQUAL_EXCEPTIONAL_GAPS',
 'preconditions_json':js(ass),'numeric_preconditions_json':js({'g':['ge',1],'delta':['ge',1],'a':['ge',1],'b':['gt','a'],'L':['in','1..T']}),
 'outputs_json':js(['EXACT_FACTOR_COMPLEXITY','THREE_RIGHT_SPECIAL_FAMILIES','PRIMITIVE_PERIOD_T','EXACT_PHASE_HORIZON']),
 'source_locator':card_locator,'review_status':'VERIFIED','reviewed_at':TS}
lock='LOCK-TWO-EQUAL-GAPS-FORMULA-20261020'
for c in [main,exp]:
 c.execute('insert into results values(?,?,?,?,?,?,?,?,?,?,?,?,?)',row)
 rd=dict(zip([x[1] for x in c.execute('pragma table_info(results)')],row))
 c.execute('insert into result_versions values(?,?,?,?,?,?,?)',(RID,1,js(rd),'ACTIVE',1,CID,TS))
 for sr in source_rows:c.execute('insert into sources values(?,?,?,?,?,?,?,?,?)',sr)
 for sr in source_rows:c.execute('insert into result_sources values(?,?,?)',(RID,sr[0],'PROOF' if sr[1]=='INTERNAL_PROOF' else 'VALIDATION' if sr[1]=='EXECUTED_CHECKER' else 'INTERFACE_CARD' if sr[1]=='LIBRARY_CARD' else 'BIBLIOGRAPHY'))
 for e in ev:c.execute('insert into evidence values(?,?,?,?,?,?,?,?)',e)
 c.execute('insert into audits values(?,?,?,?,?,?,?,?,?)',('AUD-TWO-GAP-RAVI2-25',RID,'TEMPS_REGLE90','PROOF_SCOPE_REPRODUCIBILITY_REDUNDANCY_BIBLIOGRAPHY','PASS_WITH_PROCEDURAL_RESERVATION','single_assistant_internal_review;two_algorithmic_checks',cert_locator,note,TS))
 c.execute('insert into regression_tests values(?,?,?,?,?,?,?,?)',('TEST-TWO-GAP-25',RID,'Two archived integer checks reproduced','EXACT_ENUMERATION','PASS',checks_locator,TS,'No new experiment; reproduction of declared domains.'))
 c.execute('insert into bibliography_passes values(?,?,?,?,?,?,?)',('BIB-TWO-GAP-20261020','TEMPS_REGLE90','RETROSPECTIVE_TARGETED','factor complexity; gap function; periodic words; two equal exceptional gaps','Cassaigne1997;Gheorghiciuc2005;Blanchet-SadriChenMunteanu2013','Method classical; exact formula not located in consulted sources; originality INDETERMINEE; initial targeted audit absent.',TS))
 c.execute('insert into lock_decisions values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(lock,'TEMPS_REGLE90',statement,domain,'forall integer parameters in declared domain',cert_locator,'CONJECTURED_THEN_PROVED',2,2,'CERTIFIE','No mathematical premise missing; originality remains indeterminate independently','New counterexample or failed proof audit; not another enumeration grid',TS,TS))
 for i,desc in [(1,'Direct factor enumeration: 288 families/6720 lengths'),(2,'Right-extension set reconstruction: 1080 families/40500 lengths')]:
  c.execute('insert into lock_experiments values(?,?,?,?,?,?,?,?,?,?)',(lock+'-E'+str(i),lock,1,1,1,desc,'PASS',checks_locator,1,TS))
 for k,v in [('last_scientific_commit',CID),('last_scientific_commit_at',TS)]:
  c.execute('insert or replace into meta values(?,?)',(k,v))
 c.execute('insert into events(entity_type,entity_id,event_type,payload_json,created_at) values(?,?,?,?,?)',('result',RID,'CERTIFIED_INTERNAL_WITH_ORIGINALITY_INDETERMINATE',js(certificate),TS))
 c.commit()
exp.execute('insert into result_scope values(?,?,?)',(RID,'THEOREME',domain))
exp.execute('insert into result_contracts values(?,?,?,?,?,?,?,?,?)',(RID,1,'TEMPS_REGLE90','THEOREM',domain,js(ass),'[]','MANUAL',TS))
exp.execute('insert into v13_strict_contracts values(?,?,?,?,?,?,?,?,?)',tuple(strict.values()))
exp.execute('insert into certification_records values(?,?,?,?,?,?,?)',('RAVI2-RESULT-'+RID+'-V1',RID,None,1,'CERTIFIED',cert_locator,TS))
exp.commit()
registry=ROOT/'ravi2_strict_registry_phase8.json';reg=json.loads(registry.read_text())
assert len(reg['contracts'])==51
reg['contracts'].append(strict);registry.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
for c in [main,exp]:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert not c.execute('pragma foreign_key_check').fetchall()
 assert c.execute('select count(*) from results').fetchone()[0]==89
 assert c.execute('select count(*) from certified_active_results').fetchone()[0]==85
 assert c.execute("select count(*) from relations where relation_type='DEPEND_DE'").fetchone()[0]==49
 assert not c.execute("select * from result_versions where result_id=? and premise_allowed!=1",(RID,)).fetchall()
assert all(rows(main,t)==rows(exp,t) for t in common)
for t in common:
 if t=='meta':continue
 now=rows(main,t)
 assert all(r in now for r in old[t]),('old rows altered',t)
edges=main.execute("select source_result_id,target_result_id from relations where relation_type='DEPEND_DE'").fetchall();graph={}
for a,b in edges:graph.setdefault(a,[]).append(b)
def dfs(v,trail):
 assert v not in trail,('cycle',v)
 for u in graph.get(v,[]):dfs(u,trail|{v})
for v in graph:dfs(v,set())
strict_count=exp.execute('select count(*) from v13_strict_contracts').fetchone()[0]
assert strict_count==52
stats={'commit_id':CID,'results':89,'admissible':85,'depend_de':49,'common_tables_identical':25,'strict_contracts':52,
 'integrity':'ok','foreign_key_errors':0,'causal_cycles':0,'all_old_non_meta_rows_preserved':True,
 'originality':'INDETERMINEE','independence':'two algorithms; no separate human/model reviewer','bibliography_sequence_deviation_recorded':True,
 'main_sha256':sha(ROOT/'RESEARCH_MEMORY.sqlite'),'experimental_sha256':sha(ROOT/'RESEARCH_MEMORY_RAVI2_V13_TEST.sqlite')}
(ROOT/'TWO_EQUAL_GAPS_COMMIT_VERIFY_2026-10-20.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
for name in ['MEMORY_INDEX.md','RESEARCH_SNAPSHOT_ACTIVE.md','INDEX_BRIQUES.md']:
 p=ROOT/name;s=p.read_text()
 header=('## Commit actif TWO-EQUAL-GAPS-25 — 20 octobre 2026\n\n'+RID+' v1 : **DÉMONTRÉ interne**, originalité **INDÉTERMINÉE**. '+statement+'\n\n'
 'Preuve autonome; aucun nouveau DEPEND_DE. Deux contrôles archivés reproduits : 288 familles/6720 longueurs et 1080 familles/40500 longueurs, zéro échec. '
 'Revue interne par le même assistant, pas de validation externe. Audit bibliographique ciblé rétrospectif : déviation de séquence explicitement conservée. '
 'Certificat : '+cert_locator+'. Carte : '+card_locator+'. Preuve : '+report_locator+'.\n\n'
 'État courant après ce commit : **89 cartes / 85 admissibles / 49 DEPEND_DE** ; miroir identique sur les **25 tables communes**, **52 contrats stricts**. '
 'Les paragraphes datés antérieurs décrivent des états historiques. Discovery/Structural Graph non régénérés pour ce commit ; leurs compteurs demeurent ceux du précédent état, à 84 résultats admissibles. Aucun automatisme interinterfaces configuré.\n\n')
 lines=s.splitlines(keepends=True);p.write_text(lines[0]+'\n'+header+''.join(lines[1:]))
main.close();exp.close()
print(json.dumps(stats,ensure_ascii=False,indent=2))