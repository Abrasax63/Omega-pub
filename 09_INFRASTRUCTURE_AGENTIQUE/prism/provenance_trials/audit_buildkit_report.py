import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
archive = parser.parse_args().archive
with ZipFile(archive) as z:
    name=next(n for n in z.namelist() if n.startswith("go-test-report") and n.endswith(".json"))
    raw=z.read(name)
    rows=[json.loads(line) for line in raw.splitlines()]
outputs=[row.get("Output","") for row in rows if isinstance(row.get("Output",""),str)]
print("member",name,"sha256",sha256(raw).hexdigest())
print("records",len(rows),"output_records",sum("Output" in row for row in rows))
lines="".join(outputs).splitlines()
print("native_progress",sum(bool(re.match(r"#\d+ ",l)) for l in lines),
      "cp_av",sum("+ cp -av " in l for l in lines),
      "copy_lines",sum("COPY " in l for l in lines))
print("test_outcomes",sum(row.get("Action")=="pass" and "Test" in row for row in rows),
      sum(row.get("Action")=="fail" for row in rows))
