"""Inventory an archived OCI build record as data; do not execute or extract it."""
import argparse,json,tarfile,struct
from hashlib import sha256
from pathlib import Path

def inspect(path):
    raw=path.read_bytes()
    with tarfile.open(path,'r:gz') as t:
        entries={m.name:m for m in t.getmembers() if m.isfile()}
        if len(entries)>100 or sum(m.size for m in entries.values())>10000000:
            raise ValueError('inventory budget exceeded')
        blobs={n:t.extractfile(m).read() for n,m in entries.items()}
    checked=0
    for n,b in blobs.items():
        if n.startswith('blobs/sha256/'):
            assert sha256(b).hexdigest()==n.rsplit('/',1)[1]
            checked+=1
    def key(d):return 'blobs/'+d.replace(':','/')
    def resolve(d):return json.loads(blobs[key(d)])
    index=json.loads(blobs['index.json'])
    manifest=resolve(index['manifests'][0]['digest'])
    history=resolve(manifest['config']['digest'])
    image=next(x for x in manifest['layers'] if x.get('annotations',{}).get('vnd.export-build.descriptor.mediatype'))
    image_manifest=resolve(image['digest'])
    required=[image_manifest['config']]+image_manifest['layers']
    missing=[x['digest'] for x in required if key(x['digest']) not in blobs]
    log=blobs[key(history['logs']['digest'])]
    offset=0;frames=0
    while offset<len(log):
        if len(log)-offset<4:raise ValueError('truncated log framing')
        size=struct.unpack_from('<I',log,offset)[0];offset+=4
        if size>len(log)-offset:raise ValueError('truncated log frame')
        offset+=size;frames+=1
    return dict(archive_sha256=sha256(raw).hexdigest(),regular_members=len(blobs),verified_blob_digests=checked,
                source_context=history['FrontendAttrs']['context'],target=history['FrontendAttrs']['target'],
                log_bytes=len(log),log_frames=frames,log_media_type=history['logs']['media_type'],
                history_completed='CompletedAt' in history,history_cached=history.get('numCachedSteps'),
                history_total=history.get('numTotalSteps'),history_completed_steps=history.get('numCompletedSteps'),
                image_references=len(required),missing_image_references=len(missing),
                media_types=[x['mediaType'] for x in manifest['layers']])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path)
    print(json.dumps(inspect(p.parse_args().archive),sort_keys=True,indent=2))
