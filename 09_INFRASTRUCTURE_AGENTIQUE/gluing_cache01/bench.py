"""Predefined prefix-rich synthetic workload; exact proof witnesses compared.

Not a representative Omega LLM workload, nor a power/FLOP measurement.
Wall clock varies by runner; logical update counts are reproducible.
"""
import json
from pathlib import Path
from time import perf_counter
from witness_cache import NaiveExact,WitnessCache

CASES=(
    ("P2_NOT_P1",(0,0,2),(0,1,1)),
    ("DEEP_OBSTRUCTION",(0,3,1,3),(0,0,0,1)),
    ("SAME_MACRO_A",(0,0,2,2),(0,1,1,0)),
    ("SAME_MACRO_B",(1,0,0,1),(0,1,0,1)),
)
WORDS=[tuple([0]*k+[1]*m) for k in range(1,7) for m in range(1,4)]
WORDS += [(1,1,0),(0,0,1),(0,0,0,1),(0,0,0),(0,0,1)]
REQUESTS=[(name,T,p,w) for name,T,p in CASES for _ in range(3) for w in WORDS]

def run(engine):
    start=perf_counter()
    outputs=[]
    for name,T,p,w in REQUESTS:
        a=engine.check(T,p,w)
        outputs.append((name,w,a.admissible,a.witness_start,
                        a.observed_trace,a.first_empty_length))
    return outputs,round(perf_counter()-start,6)

def main():
    baseline=NaiveExact();original,baseline_seconds=run(baseline)
    cache=WitnessCache(max_entries=4096);memoized,cache_seconds=run(cache)
    assert original==memoized,"GLUING_RESULT_OR_WITNESS_MISMATCH"
    report={
        "status":"EXACT_WITNESS_PARITY_VERIFIED",
        "workload":"4 finite systems, repeated prefix-rich synthetic requests",
        "counted_requests":len(REQUESTS),
        "all_outputs_and_witnesses_identical":True,
        "uncached":{"steps":baseline.update_steps,"microscopic_pair_visits":baseline.pair_visits,
                    "seconds":baseline_seconds},
        "cached":{"steps":cache.update_steps,"microscopic_pair_visits":cache.pair_visits,
                  "seconds":cache_seconds,"cache_hits":cache.cache_hits,
                  "entries_in_ram":len(cache.memo),"evictions":cache.evictions},
        "saved_steps":baseline.update_steps-cache.update_steps,
        "saved_microscopic_pair_visits":baseline.pair_visits-cache.pair_visits,
        "status_qualifier":"No general speed claim; workload intentionally prefix-rich. No LLM, API, GPU, FLOPs or power measured."
    }
    path=Path("/tmp/omega-gluing-cache01/report.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
