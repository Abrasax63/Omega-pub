"""Audit CCS v1.0 : calcul fini indépendant + provenance, sans prétendre compiler Lean."""
import json,hashlib,sys
from pathlib import Path
def audit(folder):
 d=Path(folder);m=json.loads((d/"ccs_manifest_v09.json").read_text())
 for key,filename in (("source_sha256",m["source_file"]),("formal_sha256",m["formal_file"])):
  if hashlib.sha256((d/filename).read_bytes()).hexdigest()!=m[key]:return {"status":"REJECTED","reason":"hash mismatch"}
 A=[0,1,2,3];B=[10,11,12,13];f=lambda x:x+10
 h1=lambda x:x>0;h2=lambda y:y>10
 p1=lambda x:x%2==0;p2=lambda y:y%2==0
 checks={
 "mapping": [f(x) for x in A]==B,
 "hypotheses":all(h1(x)==h2(f(x)) for x in A),
 "conclusions_guarded":all(not h1(x) or p1(x)==p2(f(x)) for x in A),
 "statement_equivalence":(all(not h1(x) or p1(x) for x in A)==all(not h2(y) or p2(y) for y in B)),
 }
 return {"status":"FINITE_CHECK_PASSED" if all(checks.values()) else "REJECTED","checks":checks,
         "lean_status":"NOT_EXECUTED","translation_status":"NOT_CERTIFIED"}
if __name__=="__main__":
 print(json.dumps(audit(sys.argv[1]),indent=2))