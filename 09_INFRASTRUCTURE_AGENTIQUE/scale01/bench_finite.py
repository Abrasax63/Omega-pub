"""SCALE01: exact finite-state scaling, cache benefit and adversarial overhead."""
import argparse
import json
from pathlib import Path
import random
from time import perf_counter
import tracemalloc
from exact_router import ExactGluingRouter
from witness_cache import trace

SIZES=(8,32,128,512)
BATCH=24
LENGTH=12
MODES=("off","on","adaptive")
PROFILES=("repeated","unique_systems")


def make_cases(n,profile):
    pi=tuple(i%2 for i in range(n))
    rng=random.Random(n*100019+37)
    if profile=="repeated":
        T=tuple(rng.randrange(n) for _ in range(n))
        rows=[]
        for k in range(BATCH):
            word=trace(T,pi,k%n,LENGTH)
            if k%5==0:
                word=word[:-1]+(1-word[-1],)
            rows.append((T,pi,word))
        return rows
    assert profile=="unique_systems"
    out=[]; seen=set()
    for k in range(BATCH):
        T=tuple(rng.randrange(n) for _ in range(n))
        while T in seen:
            T=tuple(rng.randrange(n) for _ in range(n))
        seen.add(T)
        word=trace(T,pi,k%n,LENGTH)
        if k%5==0:
            word=word[:-1]+(1-word[-1],)
        out.append((T,pi,word))
    return out


def evaluate(cases,mode):
    router=ExactGluingRouter(mode=mode,max_prefixes=2048,max_systems=32)
    tracemalloc.start()
    start=perf_counter()
    outcomes=[router.check(*case) for case in cases]
    duration=round(perf_counter()-start,6)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return outcomes,{
        **router.counters(),
        "elapsed_seconds_python_with_tracemalloc":duration,
        "peak_traced_python_allocations_bytes":peak,
        "responses":len(cases),
    }


def report():
    runs=[]
    for n in SIZES:
        for profile in PROFILES:
            cases=make_cases(n,profile)
            outcomes={}
            metrics={}
            for mode in MODES:
                outcomes[mode],metrics[mode]=evaluate(cases,mode)
            assert outcomes["off"]==outcomes["on"]==outcomes["adaptive"],(
                "STATE_WITNESS_OR_FIRST_EMPTY_PREFIX_REGRESSION",n,profile)
            if profile=="unique_systems":
                for mode in ("on","adaptive"):
                    assert metrics[mode]["cache_hits"]==0,("INCORRECT_CACHE_HIT",n,mode)
                assert metrics["adaptive"]["cached_calls"]==0
                assert metrics["adaptive"]["prefix_cache_entries"]==0
            # Positive witnesses and negative first-empty-prefix certificates must
            # agree *object for object*, not just a boolean success counter.
            runs.append({
                "n_states":n,"profile":profile,"word_length":LENGTH,
                "requests":len(cases),"all_three_verdicts_and_witnesses_equal":True,
                "positive_words":sum(x.admissible for x in outcomes["off"]),
                "negative_words":sum(not x.admissible for x in outcomes["off"]),
                "modes":metrics,
                "adaptive_avoided_direct_propagation_steps":
                    metrics["off"]["steps"]-metrics["adaptive"]["steps"],
                "always_cache_avoided_direct_propagation_steps":
                    metrics["off"]["steps"]-metrics["on"]["steps"],
            })
    return {
        "status":"SCALE_FINITE_EXACT_PASS",
        "data":"synthetic deterministic systems, not production Omega requests",
        "states":SIZES,"requests_per_profile_size":BATCH,
        "word_length":LENGTH,"profiles":PROFILES,
        "no_model_inference":True,"no_energy_claim":True,
        "runs":runs,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result=report()
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    for r in result["runs"]:
        off=r["modes"]["off"];on=r["modes"]["on"];ad=r["modes"]["adaptive"]
        print("FINITE",r["n_states"],r["profile"],
              "steps off/on/adaptive",off["steps"],on["steps"],ad["steps"],
              "hits",on["cache_hits"],ad["cache_hits"],
              "alloc bytes",off["peak_traced_python_allocations_bytes"],
              on["peak_traced_python_allocations_bytes"],
              ad["peak_traced_python_allocations_bytes"],flush=True)
    print("RESULT",result["status"],flush=True)

if __name__=="__main__": main()
