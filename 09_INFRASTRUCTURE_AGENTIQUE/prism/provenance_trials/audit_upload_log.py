"""Inspect public archived logs without treating displayed scripts as execution."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from provenance_xtrace import extract,fixed_verdict
p=argparse.ArgumentParser();p.add_argument('log',type=Path);a=p.parse_args()
raw=a.log.read_bytes();log=raw.decode('utf-8')
rows=[]
for output in ('path/to/dir-1/file1.txt','some/new/path/file1.txt'):
    case=extract(log,output)
    rows.append(dict(output=output,complete=case['complete'],writers=len(case['writers']),fixed=fixed_verdict(case)))
print(json.dumps(dict(decoded_log_sha256=sha256(raw).hexdigest(),rows=rows),ensure_ascii=False,indent=2))
