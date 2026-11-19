#!/usr/bin/env python3
import argparse, json, statistics, sys, time
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

def med(fn,n):
    laps=[]; last=None
    for _ in range(n):
        t=time.perf_counter_ns(); last=fn(); laps.append(time.perf_counter_ns()-t)
    return statistics.median(laps)/1000,last

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--reader",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    sys.path.insert(0,a.reader)
    from pipeline import pipeline
    from read import blob, packetize
    from json_intake import decode,RejectedJSON
    rows=[]
    with TemporaryDirectory() as d:
        root=Path(d)
        for target in (1024,16384,65536):
            line="Pour n pair, le carré de n est divisible par quatre."
            raw=("# Assertions\n\n"+line+"\n\n# Données\n\n"+"x"*(target-len(line)-30)+"\n").encode()
            source=root/f"doc-{target}.md"; source.write_bytes(raw); digest=blob(raw)
            packet=packetize(raw,source.as_posix())["packets"][0]["packet_id"]
            obj={"source_blob":digest,"claims":[{"claim_id":"C","packet_id":packet,
                 "evidence":[{"role":"conclusion","packet_id":packet,"line":3,"literal":line}]}]}
            valid=json.dumps(obj,separators=(",",":")).encode()
            ref=lambda: pipeline(source,digest,model_json=json.loads(valid),provider="fixture")
            cand=lambda: pipeline(source,digest,model_json=decode(valid,"fixture",original=valid),provider="fixture")
            ref_us,ref_out=med(ref,100)
            cand_us,cand_out=med(cand,100)
            rows.append({"target_bytes":target,"actual_bytes":len(raw),"json_bytes":len(valid),
              "reference_us":round(ref_us,3),"candidate_us":round(cand_us,3),
              "overhead_pct":round((cand_us/ref_us-1)*100,2),
              "exact_output_equal":ref_out==cand_out})
        duplicate=valid.replace(b'{"source_blob":',b'{"source_blob":"wrong","source_blob":',1)
        reference_accepted=isinstance(json.loads(duplicate),dict)
        candidate_rejected=False
        try: decode(duplicate,"fixture",original=duplicate)
        except RejectedJSON as e: candidate_rejected=e.reason=="DUPLICATE_JSON_KEY"
        result={"rows":rows,"negative":{"reference_accepted":reference_accepted,
          "candidate_rejected":candidate_rejected},"calls":600}
        Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__": main()

