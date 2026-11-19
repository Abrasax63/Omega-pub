#!/usr/bin/env python3
import argparse, json, statistics, sys, time
from pathlib import Path

def loads_ref(raw): return json.loads(raw)

def sample(size):
    padding="x"*size
    obj={"source_blob":"blob","claims":[{"claim_id":"c","packet_id":"p","evidence":[],"padding":padding}]}
    valid=json.dumps(obj,separators=(",",":")).encode()
    duplicate=valid.replace(b'{"source_blob":"blob",',b'{"source_blob":"wrong","source_blob":"blob",',1)
    return obj,valid,duplicate

def bench(fn,raw,n=100):
    laps=[]
    for _ in range(n):
        t=time.perf_counter_ns(); fn(raw); laps.append(time.perf_counter_ns()-t)
    return statistics.median(laps)/1000

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-path",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    sys.path.insert(0,a.candidate_path); from json_intake import decode,RejectedJSON
    rows=[]
    for target in (1024,16384,65536):
        obj,valid,dup=sample(target)
        ref_us=bench(loads_ref,valid)
        cand_us=bench(lambda b:decode(b,"fixture",original=b),valid)
        assert loads_ref(valid)==obj and decode(valid,"fixture",original=valid)==obj
        ref_accept=0; cand_reject=0
        for _ in range(100):
            loads_ref(dup); ref_accept+=1
            try: decode(dup,"fixture",original=dup)
            except RejectedJSON as e: cand_reject += e.reason=="DUPLICATE_JSON_KEY"
        rows.append({"target_padding":target,"bytes":len(valid),"valid_reference_us":round(ref_us,3),
          "valid_candidate_us":round(cand_us,3),"overhead_pct":round((cand_us/ref_us-1)*100,2),
          "valid_equal":True,"duplicate_reference_accept":ref_accept,"duplicate_candidate_reject":cand_reject})
    Path(a.output).write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
