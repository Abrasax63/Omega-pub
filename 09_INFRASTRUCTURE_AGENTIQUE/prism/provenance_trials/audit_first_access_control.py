"""Controlled application-level write receipts and a first-access projection.

This does not execute Buildcage or provide kernel tracing.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

WRITER = """import os,sys,json
fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
receipts=[]
try:
    for _ in range(int(sys.argv[2])):
        assert os.lseek(fd,0,os.SEEK_SET)==0
        written=os.write(fd,b"constant\\n")
        assert written==9
        receipts.append(dict(operation="write",returned_bytes=written,offset=0))
finally:
    os.close(fd)
print(json.dumps(receipts))
"""

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    target=(args.output/"target.bin").resolve()
    report=[]
    for count in (1,2):
        result=subprocess.run([sys.executable,"-I","-c",WRITER,str(target),str(count)],
                              check=True,capture_output=True,text=True)
        receipts=json.loads(result.stdout)
        assert len(receipts)==count and all(r["returned_bytes"]==9 for r in receipts)
        receipt_path=args.output/f"receipts-{count}.json"
        receipt_path.write_text(result.stdout)
        report.append(dict(requested_writes=count,reported_successful_writes=len(receipts),
                           first_access=receipts[:1],final_sha256=sha256(target.read_bytes()).hexdigest(),
                           receipt_sha256=sha256(result.stdout.encode()).hexdigest()))
    assert report[0]["first_access"]==report[1]["first_access"]
    assert report[0]["final_sha256"]==report[1]["final_sha256"]
    print(json.dumps(report,sort_keys=True,indent=2))
if __name__=="__main__":
    main()
