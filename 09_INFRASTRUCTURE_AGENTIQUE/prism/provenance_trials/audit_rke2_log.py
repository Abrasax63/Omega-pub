"""Inspect selected executed copy records; never infer whole-job writer coverage."""
import argparse,json,re
from pathlib import Path
from hashlib import sha256
from provenance_xtrace import extract,fixed_verdict
p=argparse.ArgumentParser();p.add_argument('log',type=Path);a=p.parse_args()
raw=a.log.read_bytes();log=raw.decode('utf-8')
records=[line for line in log.splitlines() if re.search(r'\+ cp -vf LICENSE dist/bundle/share/rke2/LICENSE.txt$',line)]
case=extract(log,'dist/bundle/share/rke2/LICENSE.txt')
print(json.dumps(dict(decoded_normalized_log_sha256=sha256(raw).hexdigest(),bytes=len(raw),
                     executed_cp_vf_license_records=records,
                     recognized_writers=len(case['writers']),complete=case['complete'],fixed=fixed_verdict(case)),ensure_ascii=False,indent=2))
