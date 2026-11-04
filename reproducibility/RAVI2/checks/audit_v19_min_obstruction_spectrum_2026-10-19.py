import json, itertools, hashlib, sqlite3, os, datetime
from pathlib import Path

ROOT=Path('/mnt/data/v19_audit_20261019')
SRC=ROOT/'V19_COEXISTENCE_REGION_SUMMARY_2026-10-15.json'
GRAPH=ROOT/'current'/'RAVI2_RESEARCH_GRAPH.sqlite'
SCI=ROOT/'current'/'RESEARCH_MEMORY.sqlite'
OUT=ROOT/'V19_MIN_OBSTRUCTION_SPECTRUM_AUDIT_CHECKS_2026-10-19.json'

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def admissible(v,caps):
    return all(x<=c for x,c in zip(v,caps))

def minimal_nonmember(v,caps):
    if admissible(v,caps): return False
    for i,x in enumerate(v):
        if x>0:
            u=list(v); u[i]-=1
            if not admissible(u,caps): return False
    return True

def exhaustive_small_boxes():
    boxes=0; vectors=0; failures=[]
    for d in range(1,5):
        for caps in itertools.product(range(4), repeat=d):
            boxes+=1
            got=[]
            ranges=[range(c+2) for c in caps]
            for v in itertools.product(*ranges):
                vectors+=1
                if minimal_nonmember(v,caps): got.append(v)
            exp=[]
            for i,c in enumerate(caps):
                v=[0]*d; v[i]=c+1; exp.append(tuple(v))
            if sorted(got)!=sorted(exp):
                failures.append({'caps':caps,'got':got,'expected':exp})
    return {'boxes_checked':boxes,'vectors_checked':vectors,'failures':failures,'pass':not failures}

def direct_v19(data):
    finite=data['class_region_finite_caps']
    unbounded=set(data['class_region_unbounded'])
    families=[]
    for lab,cap in sorted(finite.items()):
        families.append({'label':lab,'capacity':cap,'minimal_forbidden_multiplicity':cap+1})
    spectrum=sorted(set(x['minimal_forbidden_multiplicity'] for x in families))
    expected=[11,21,41,61,81,161]
    labels=set(finite)|unbounded
    expected_labels={f'C5O-{i:02d}' for i in range(14)}
    return {
      'finite_labels':len(finite),'unbounded_labels':len(unbounded),
      'all_14_labels_accounted_for': labels==expected_labels,
      'families':families,'spectrum':spectrum,'expected_spectrum':expected,
      'pass':len(finite)==10 and len(unbounded)==4 and labels==expected_labels and spectrum==expected
    }

def main():
    data=json.load(open(SRC))
    sci_before=sha256(SCI); graph_before=sha256(GRAPH); source_sha=sha256(SRC)
    small=exhaustive_small_boxes(); v19=direct_v19(data)
    c=sqlite3.connect(GRAPH); c.execute('PRAGMA foreign_keys=ON')
    integrity_before=c.execute('PRAGMA integrity_check').fetchone()[0]
    fk_before=c.execute('PRAGMA foreign_key_check').fetchall()
    row=c.execute("select staging_id,status,originality_status,eligible_for_scientific_commit,statement,proof_note from staging_results where staging_id=?",('STG-V19-MIN-OBSTRUCTION-SPECTRUM-01',)).fetchone()
    source_statement=data.get('exact_region')
    internal_redundancy=(source_statement is not None and v19['pass'])
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    c.execute('''CREATE TABLE IF NOT EXISTS staging_audits(
      audit_id TEXT PRIMARY KEY,
      staging_id TEXT NOT NULL REFERENCES staging_results(staging_id) ON DELETE CASCADE,
      audit_type TEXT NOT NULL,
      outcome TEXT NOT NULL,
      evidence_json TEXT NOT NULL,
      artifact_path TEXT,
      created_at TEXT NOT NULL
    )''')
    evidence={
      'source_summary_sha256':source_sha,
      'generic_box_exhaustive':small,
      'v19_direct':v19,
      'internal_redundancy':'Immediate corollary of OBS-V19-COEX-REGION exact product box under componentwise/submultiset order.',
      'bibliography_assessment':{
        'abstract_mechanism':'CLASSICAL',
        'application_specific_exact_match':'NOT_FOUND_IN_TARGETED_SEARCH__NOT_PROOF_OF_NOVELTY',
        'standalone_novelty':'INSUFFICIENT_FOR_NEW_BRICK'
      }
    }
    outcome='REDUNDANT_AS_STANDALONE_BRICK' if small['pass'] and v19['pass'] and internal_redundancy else 'INDETERMINATE'
    c.execute('INSERT OR REPLACE INTO staging_audits VALUES(?,?,?,?,?,?,?)',(
      'AUD-STG-V19-MIN-OBS-SPECTRUM-20261019','STG-V19-MIN-OBSTRUCTION-SPECTRUM-01','SCIENTIFIC+BIBLIOGRAPHIC_REDUNDANCY',outcome,json.dumps(evidence,ensure_ascii=False,sort_keys=True),'/Recherche/03_AUDITS_CERTIFICATS/AUDIT_STG_V19_MIN_OBSTRUCTION_SPECTRUM_2026-10-19.md',now))
    if outcome=='REDUNDANT_AS_STANDALONE_BRICK':
        c.execute("update staging_results set originality_status=?, eligible_for_scientific_commit=0 where staging_id=?",(
          'ABSTRACT_CLASSICAL__DERIVED_FROM_OBS-V19-COEX-REGION__EXTERNAL_APPLICATION_NOVELTY_INDETERMINATE','STG-V19-MIN-OBSTRUCTION-SPECTRUM-01'))
    c.execute('INSERT OR REPLACE INTO conjecture_meta(key,value) VALUES(?,?)',('stg_v19_min_obstruction_audit',outcome))
    c.commit()
    integrity_after=c.execute('PRAGMA integrity_check').fetchone()[0]
    fk_after=c.execute('PRAGMA foreign_key_check').fetchall()
    audit_row=c.execute('select audit_id,outcome from staging_audits where staging_id=?',('STG-V19-MIN-OBSTRUCTION-SPECTRUM-01',)).fetchone()
    staged_after=c.execute('select status,originality_status,eligible_for_scientific_commit from staging_results where staging_id=?',('STG-V19-MIN-OBSTRUCTION-SPECTRUM-01',)).fetchone()
    c.close()
    sci_after=sha256(SCI); graph_after=sha256(GRAPH)
    out={
      'date':'2026-10-19','staging_id':'STG-V19-MIN-OBSTRUCTION-SPECTRUM-01',
      'verdict':outcome,
      'generic_box_exhaustive':small,'v19_direct':v19,
      'scientific_db_sha256_before':sci_before,'scientific_db_sha256_after':sci_after,'scientific_db_unchanged':sci_before==sci_after,
      'graph_sha256_before':graph_before,'graph_sha256_after':graph_after,
      'integrity_before':integrity_before,'integrity_after':integrity_after,
      'foreign_key_errors_before':len(fk_before),'foreign_key_errors_after':len(fk_after),
      'staging_before':row[:4] if row else None,'staging_after':staged_after,
      'audit_row':audit_row,
      'bibliographic_verdict':{
        'abstract_structure':'KNOWN_OR_CLASSICAL',
        'exact_V19_application':'INDETERMINATE_EXTERNAL_NOVELTY',
        'standalone_promotion':'NO__REDUNDANT_DERIVED_COROLLARY'
      },
      'all_pass': small['pass'] and v19['pass'] and sci_before==sci_after and integrity_after=='ok' and not fk_after and outcome=='REDUNDANT_AS_STANDALONE_BRICK'
    }
    json.dump(out,open(OUT,'w'),ensure_ascii=False,indent=2,sort_keys=True)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__': main()