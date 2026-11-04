from pathlib import Path
import hashlib,json,sys
def check(directory):
    d=Path(directory)
    m=json.loads((d/"ccs_manifest_v09.json").read_text())
    src=d/m["source_file"]; lean=d/m["formal_file"]
    if hashlib.sha256(src.read_bytes()).hexdigest()!=m["source_sha256"]: return False
    if hashlib.sha256(lean.read_bytes()).hexdigest()!=m["formal_sha256"]: return False
    lines=src.read_text().splitlines()
    return all(1<=n<=len(lines) for n in m["line_bindings"].values())
if __name__=="__main__":
    ok=check(sys.argv[1]);print("PROVENANCE OK" if ok else "PROVENANCE REJETEE");sys.exit(0 if ok else 1)