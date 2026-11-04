"""Contrôle de provenance et contrôle extensionnel fini, sans prétention de lecture sémantique."""
import json,hashlib,sys
from pathlib import Path
from ccs_source_formelle_v07 import verify
def check(certpath,sourcepath):
    c=json.loads(Path(certpath).read_text(encoding="utf8"))
    p=c["provenance"]
    lines=Path(sourcepath).read_text(encoding="utf8").splitlines()
    digest=hashlib.sha256(Path(sourcepath).read_bytes()).hexdigest()
    if digest!=p["sha256"] or Path(sourcepath).name!=p["file"]:return False
    if not all(1<=b["line"]<=len(lines) and b["statement"] in ("source","target","mapping") for b in p["bindings"]):return False
    return verify(c)
if __name__=="__main__":
    ok=check(sys.argv[1],sys.argv[2]);print("TRACE ET CONTRAT FINI VALIDES" if ok else "REJETE");sys.exit(0 if ok else 1)