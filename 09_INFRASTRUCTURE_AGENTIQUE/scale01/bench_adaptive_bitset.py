"""COMPRESS01 guard: bitset compression is adaptive, not forced on novel systems."""
from pathlib import Path
import json
import tracemalloc
from time import perf_counter
from bench_finite import make_cases
from adaptive_bitset import AdaptiveBitsetRouter


def measure(cases,mode):
    tracemalloc.start()
    start=perf_counter()
    router=AdaptiveBitsetRouter(mode,max_prefixes=2048,max_tracked_systems=32)
    answers=[router.check(*case) for case in cases]
    seconds=round(perf_counter()-start,6)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return answers,{"seconds_with_tracemalloc":seconds,
                    "peak_traced_python_bytes":peak,**router.counters()}


def run():
    out=[]
    for n,profile in ((512,"unique_systems"),(512,"repeated"),(2048,"repeated")):
        cases=make_cases(n,profile)
        answers={};metrics={}
        for mode in ("off","bitset","adaptive-bitset"):
            answers[mode],metrics[mode]=measure(cases,mode)
        assert answers["off"]==answers["bitset"]==answers["adaptive-bitset"]
        if profile=="unique_systems":
            assert metrics["adaptive-bitset"]["bitset_calls"]==0
            assert metrics["adaptive-bitset"]["bitset_prefix_entries"]==0
        out.append({"n_states":n,"profile":profile,"requests":len(cases),
                    "word_length":12,"all_verdicts_identical":True,
                    "measurements":metrics})
    return {"status":"ADAPTIVE_BITSET_VERDICT_PARITY",
            "scope":"three synthetic workloads, Python tracemalloc not full RAM or energy",
            "runs":out}


def main():
    report=run()
    path=Path("/tmp/omega-compress01/adaptive.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+"\n")
    for x in report["runs"]:
        print("ADAPTIVE",x["n_states"],x["profile"],json.dumps(x["measurements"]),flush=True)
    print("STATUS",report["status"])
if __name__=="__main__":main()
