import argparse
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
from time import perf_counter
from provenance_offline import read_cases

def main():
    parser=argparse.ArgumentParser(description="Read-only native-format admission diagnostic")
    parser.add_argument("external",type=Path)
    parser.add_argument("raccord",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    root=args.output
    root.mkdir(exist_ok=True)
    archive=args.external
    assert sha256(archive.read_bytes()).hexdigest()=="309128af20bae722d0812cb1a9ccd126fc2eb7f08ba387228d1ad6d190bdd8e4"
    with ZipFile(archive) as z:
        raw=z.read("filesystem-audit.jsonl")
    (root/"external.jsonl").write_bytes(raw)
    rows=[json.loads(line) for line in raw.splitlines()]
    manifest=[dict(journal="external.jsonl",output="probe.txt",expected="indéterminé",
                   source="https://github.com/buildcage/isolated-run/actions/runs/44095200035",
                   truth_source="technical sentinel only; no scientific ground truth",
                   format="buildcage-jsonl",sha256=sha256(raw).hexdigest())]
    path=root/"native.json"
    path.write_text(json.dumps(manifest,ensure_ascii=False)+"\n")
    start=perf_counter()
    try:
        read_cases(path)
    except ValueError as error:
        assert str(error)=="Unsupported journal format."
        print("native_format",type(error).__name__,str(error))
    else:
        raise AssertionError("native format unexpectedly accepted")
    with ZipFile(args.raccord) as z:
        for n in ("training.json","train.log"):
            (root/n).write_bytes(z.read("rejeu/"+n))
    control,evidence=read_cases(root/"training.json")
    assert len(control)==len(evidence)==1
    print("control_read",len(control),"external_rows",len(rows),"seconds",round(perf_counter()-start,6))
    for p in (path,root/"external.jsonl"):
        print(p.name,sha256(p.read_bytes()).hexdigest())

if __name__=="__main__":
    main()
