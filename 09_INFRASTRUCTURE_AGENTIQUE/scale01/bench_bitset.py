"""COMPRESS01: compare pair-witness vs exact bitset witness memory on frozen workloads."""
import json
from pathlib import Path
from time import perf_counter
import tracemalloc
from bitset_witness_cache import ExactBitsetWitnessCache
from witness_cache import WitnessCache
from bench_finite import make_cases

SIZES=(32,128,512,1024,2048)
LENGTH=12
REQUESTS=24


def measure(engine_cls,cases):
    tracemalloc.start()
    t0=perf_counter()
    obj=(engine_cls(max_entries=2048) if engine_cls is WitnessCache
         else engine_cls(max_systems=8,max_prefixes=2048,max_states=8192))
    verdicts=[obj.check(*case) for case in cases]
    seconds=round(perf_counter()-t0,6)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return obj,verdicts,seconds,peak


def check_all_witnesses(cases,legacy,compressed,left,right):
    for (T,pi,w),old,new in zip(cases,left,right):
        if (old.admissible!=new.admissible or old.witness_start!=new.witness_start
            or old.observed_trace!=new.observed_trace
            or old.first_empty_length!=new.first_empty_length):
            raise ValueError("BITSET_LOST_OR_CHANGED_AN_EXACT_WITNESS_VERDICT")
        original=legacy.memo[(T,pi,w)]
        exact_starts=tuple(sorted(s for s,_ in original.pairs))
        recovered=compressed.all_initial_witnesses(T,pi,w)
        if exact_starts!=recovered or len(exact_starts)!=new.survivor_count:
            raise ValueError("COMPRESSED_MULTIPLICITY_OR_WITNESS_SET_IS_WRONG")


def run():
    rows=[]
    for n in SIZES:
        for profile in ("repeated", "unique_systems") if n==512 else ("repeated",):
            cases=make_cases(n,profile)
            original,oa,t_old,mem_old=measure(WitnessCache,cases)
            compressed,ob,t_bit,mem_bit=measure(ExactBitsetWitnessCache,cases)
            check_all_witnesses(cases,original,compressed,oa,ob)
            stats=compressed.counters()
            rows.append({
                "n_states":n,"profile":profile,
                "requests":len(cases),"word_length":LENGTH,
                "all_original_witnesses_preserved":True,
                "legacy_pairs":{"time_traced_seconds":t_old,
                    "peak_traced_python_bytes":mem_old,"prefix_entries":len(original.memo)},
                "exact_bitsets":{"time_traced_seconds":t_bit,
                    "peak_traced_python_bytes":mem_bit,
                    **stats},
                "memory_saving_traced_bytes":mem_old-mem_bit,
                "memory_saving_percent":round((mem_old-mem_bit)*100/mem_old,2),
            })
    return {"status":"EXACT_ALL_WITNESSES_PRESERVED",
            "method":"bit masks for each initial state and time horizon",
            "scope":"single-run Python tracemalloc, not RSS, no LLM and no energy conclusion",
            "rows":rows}

def main():
    r=run()
    file=Path("/tmp/omega-compress01/benchmark.json")
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("STATUS",r["status"],flush=True)
    for x in r["rows"]:
        print("MEMORY",x["n_states"],x["profile"],
              "pair",x["legacy_pairs"]["peak_traced_python_bytes"],
              "bitset",x["exact_bitsets"]["peak_traced_python_bytes"],
              "saving_percent",x["memory_saving_percent"],
              "times",x["legacy_pairs"]["time_traced_seconds"],
              x["exact_bitsets"]["time_traced_seconds"],flush=True)
if __name__=="__main__":main()
