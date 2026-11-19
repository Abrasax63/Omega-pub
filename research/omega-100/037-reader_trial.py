"""Exercise the pinned reader CLI with synthetic model fixtures and offline transport."""
from contextlib import redirect_stdout, redirect_stderr
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter_ns
from unittest.mock import patch
import argparse
import json
import os
import sys

import model
import pipeline
from read import blob, packetize


def build(root):
    source = root / "document.md"
    line = "Pour n pair, le carré de n est divisible par quatre."
    raw = ("# Assertions\n\n" + line + "\n").encode()
    source.write_bytes(raw)
    digest = blob(raw)
    packet = packetize(raw,source.as_posix())["packets"][0]["packet_id"]

    def payload(i):
        return dict(source_blob=digest, claims=[dict(claim_id=f"C{i}",packet_id=packet,
            evidence=[dict(role="conclusion",packet_id=packet,line=3,literal=line)])])

    valid = [json.dumps(payload(i),ensure_ascii=False) for i in range(96)]
    base = valid[0]
    dup = [
        base.replace('"source_blob": ', '"source_blob": "previous", "source_blob": ',1),
        base.replace('"line": 3', '"line": 4, "line": 3',1),
        base.replace('"line": 3', r'"lin\u0065": 4, "line": 3',1),
        base.replace('"claim_id": "C0"', '"claim_id": "C0", "claim_id": "C0"',1),
    ]
    inputs=[]
    for label,answers in [('valid',valid),('duplicate',dup),('truncated',[base[:-1],base[:-20]])]:
        for i,answer in enumerate(answers):
            path = root/f'{label}-{i}.json'
            path.write_bytes(answer.encode())
            inputs.append((label,path))
    return source,digest,inputs


def invoke(source, digest, path, archive=None):
    out,err=StringIO(),StringIO()
    args=['pipeline','--source',str(source),'--source-blob',digest,'--mode','fixture','--model-json',str(path)]
    if archive is not None:
        args += ['--rejection-dir',str(archive)]
    with patch.object(sys,'argv',args), redirect_stdout(out), redirect_stderr(err):
        try:
            pipeline.main()
        except SystemExit as exc:
            assert exc.code==2 and not out.getvalue()
            return json.loads(err.getvalue())
        except json.JSONDecodeError:
            assert not out.getvalue()
            return dict(status='UNSTRUCTURED_PARSE_ERROR')
    result=json.loads(out.getvalue())
    assert result['auto_certifications']==0
    assert result['quarantine']['accepted_count']==1
    return dict(status='QUARANTINE')


class Transport:
    status=200

    def __init__(self, data):
        self.data=data

    def read(self, count):
        return self.data[:count]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def transport_check(valid, is_candidate):
    plain = json.dumps({"response":valid}).encode()
    inner = valid.replace('"line": 3', '"line": 7, "line": 3')
    dup_payload = json.dumps({"response":inner}).encode()
    dup_envelope = ('{"response":"{}", "response":'+json.dumps(valid)+'}').encode()
    cases=[(plain,None,None),(dup_payload,'DUPLICATE_JSON_KEY','ollama_payload'),
           (dup_envelope,'DUPLICATE_JSON_KEY','ollama_envelope'),
           (plain[:-1],'INVALID_JSON','ollama_envelope')]
    statuses=[]
    for raw,reason,stage in cases:
        with patch.object(model.urllib.request,'urlopen',return_value=Transport(raw)):
            try:
                result=model.ollama_generate([],json.loads(valid)['source_blob'],'local-test')
            except ValueError as exc:
                if is_candidate:
                    verdict=exc.report()
                    assert verdict['reason']==reason and verdict['stage']==stage
                    assert verdict['sha256']==sha256(raw).hexdigest()
                    statuses.append(reason)
                else:
                    assert reason=='INVALID_JSON'
                    statuses.append('UNSTRUCTURED_PARSE_ERROR')
            else:
                assert not (is_candidate and reason) and result==json.loads(valid)
                statuses.append('PARSED')
    return statuses


def main(is_candidate):
    with TemporaryDirectory() as folder:
        root=Path(folder)
        source,digest,fixtures=build(root)
        archive=root/'rejections'
        archive.mkdir()
        good, blocked, traced, archived, silent, errors = 0,0,0,0,0,0
        for label,path in fixtures:
            if is_candidate and label!='valid':
                with patch.object(pipeline,'pipeline',side_effect=AssertionError('entered verifier')):
                    result=invoke(source,digest,path,archive)
            else:
                result=invoke(source,digest,path)
            status=result['status']
            raw=path.read_bytes()
            if label=='valid':
                assert status=='QUARANTINE'
                good+=1
            elif status=='MODEL_JSON_REJECTED':
                assert result['sha256']==sha256(raw).hexdigest()
                assert result['stage']=='fixture'
                assert result['next_action']=='REQUEST_UNAMBIGUOUS_JSON'
                saved=Path(result['review_file'])
                assert saved.parent==archive and saved.read_bytes()==raw
                assert os.stat(saved).st_mode & 0o077 == 0
                archived+=1
                if label=='duplicate':
                    assert result['reason']=='DUPLICATE_JSON_KEY'
                    blocked+=1
                else:
                    assert result['reason']=='INVALID_JSON'
                    traced+=1
            elif status=='QUARANTINE':
                assert label=='duplicate'
                silent+=1
            else:
                assert status=='UNSTRUCTURED_PARSE_ERROR' and label=='truncated'
                errors+=1
        assert len(list(archive.iterdir()))==archived
        first=fixtures[0][1]
        # An explicitly reformulated, unambiguous fixture can be read normally.
        assert invoke(source,digest,first)['status']=='QUARANTINE'
        t=perf_counter_ns()
        for label,path in fixtures:
            if label=='valid':
                assert invoke(source,digest,path)['status']=='QUARANTINE'
        batch=perf_counter_ns()-t
        return dict(valid=good,blocked_duplicates=blocked,traced_truncations=traced,
            exact_archives=archived,silent_duplicates=silent,unstructured_parse_errors=errors,
            valid_batch_ns=batch,transport=transport_check(first.read_text(),is_candidate))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',action='store_true')
    print(json.dumps(main(p.parse_args().candidate)))
