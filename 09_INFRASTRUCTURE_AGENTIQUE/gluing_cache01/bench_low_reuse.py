"""Adversarial cache-miss workload with no repeated systems or prefixes.

On unique systems a cache should not save any exact propagation work. Any
observed wall-time and RAM overhead must not be hidden by the prefix-rich test.
"""
import json
from itertools import islice,product
from pathlib import Path
from time import perf_counter
import tracemalloc
from witness_cache import NaiveExact,WitnessCache

SYSTEMS=list(islice(product(range(5),repeat=5),1000))
PI=(0,1,0,1,0)
WORD=(0,1,0,1,0)

def measure(engine):
    tracemalloc.start()
    started=perf_counter()
    output=[engine.check(T,PI,WORD) for T in SYSTEMS]
    seconds=round(perf_counter()-started,6)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return output,seconds,peak

def main():
    baseline=NaiveExact()
    expected,seconds_no,peak_no=measure(baseline)
    cache=WitnessCache(max_entries=2048)
    actual,seconds_cache,peak_cache=measure(cache)
    assert actual==expected, "MICRO_WITNESS_MISMATCH_ON_CACHE_MISS"
    assert baseline.update_steps==cache.update_steps
    assert baseline.pair_visits==cache.pair_visits
    assert cache.cache_hits==0
    report={
        "status":"NO_REUSE_COST_IS_VISIBLE",
        "test_cases":len(SYSTEMS),
        "workload":"1000 different finite functions T, identical pi and word, zero cache hits",
        "identical_outputs_and_witnesses":True,
        "baseline":{"seconds_with_tracemalloc":seconds_no,
                    "peak_traced_bytes":peak_no,
                    "steps":baseline.update_steps,
                    "micro_pair_visits":baseline.pair_visits},
        "cache":{"seconds_with_tracemalloc":seconds_cache,
                 "peak_traced_bytes":peak_cache,
                 "steps":cache.update_steps,
                 "micro_pair_visits":cache.pair_visits,
                 "hits":cache.cache_hits,
                 "entries_in_ram":len(cache.memo),
                 "evictions":cache.evictions},
        "limitations":"Single run; tracemalloc measures Python allocations, not RSS. Latency indicative, not production prediction."
    }
    out=Path("/tmp/omega-gluing-cache01/low-reuse.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
