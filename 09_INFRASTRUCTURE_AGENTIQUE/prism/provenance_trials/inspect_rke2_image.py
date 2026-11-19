"""Read an archived test image and nested bundles as data, with explicit budgets."""
import argparse,tarfile,json,io,time
from pathlib import Path
from hashlib import sha256
MAX_BYTES=2_000_000_000

def inspect(path):
    start=time.monotonic();budget=[0];matches=[];archives=[];layer_count=0
    def scan(fileobj,label,depth=0):
        with tarfile.open(fileobj=fileobj,mode='r|*') as t:
            for m in t:
                budget[0]+=m.size
                if budget[0]>MAX_BYTES or time.monotonic()-start>60:raise ValueError('inspection budget exceeded')
                if not m.isfile():continue
                lower=m.name.lower()
                if 'license' in lower and m.size<100000:
                    b=t.extractfile(m).read()
                    matches.append(dict(container=label,path=m.name,size=m.size,sha256=sha256(b).hexdigest()))
                if depth<1 and 'rke2' in lower and lower.endswith(('.tar.gz','.tgz')) and m.size<100000000:
                    b=t.extractfile(m).read();archives.append(dict(container=label,path=m.name,size=m.size,sha256=sha256(b).hexdigest()))
                    scan(io.BytesIO(b),label+'!'+m.name,depth+1)
    with tarfile.open(path) as outer:
        manifest=json.loads(outer.extractfile('manifest.json').read())
        names=sorted({name for image in manifest for name in image['Layers']})
        for name in names:
            stream=outer.extractfile(name);raw=stream.read()
            assert sha256(raw).hexdigest()==name.rsplit('/',1)[1]
            scan(io.BytesIO(raw),name);layer_count+=1
    return dict(layers=layer_count,expanded_declared_bytes=budget[0],seconds=time.monotonic()-start,nested_bundles=archives,license_matches=matches)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args()
    print(json.dumps(inspect(a.archive),sort_keys=True,indent=2))
