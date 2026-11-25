import importlib
import json
from statistics import median
from time import perf_counter_ns

oracle_module = importlib.import_module("054_trial")
chunked = importlib.import_module("055_trial").chunked
engine = importlib.import_module("051_trial")
ARMS = {"orbit": None, "direct": None, "verified": None,
        "full": oracle_module.full, "chunked": chunked}
PROFILES = {"dense": "DDDDDDDD", "sparse": "UUUUUUUU", "switch": "DDUODDID"}


def stream(n, phases):
    mapping = tuple((i * 2 + 1) % n for i in range(n))
    wrong = (n,) + mapping[1:]
    for w, phase in enumerate(phases):
        for i in range(128):
            k = i % 3 if phase in "DOI" else w*128+i
            fault = "offline" if phase == "O" or phase == "D" and i == 31 else "ok"
            yield (wrong if phase == "I" else mapping), k % n, 99 - k//n, fault


def correct(row):
    mapping, state, steps, fault = row
    if mapping[0] == len(mapping):
        return "invalid", None
    if fault == "offline":
        return "unavailable", None
    return "exact", engine.binary(mapping, state, steps)


def run(rows, name):
    choice = ARMS[name]
    solver = engine.Run(name if choice is None else "orbit")
    outputs, window, decisions = [], [], []
    hits = clears = 0
    for mapping, state, steps, fault in rows:
        if len(solver.cache) >= 128:
            solver.cache.clear()
            clears += 1
        result = solver.solve(mapping, state, steps, fault)
        outputs.append(result)
        if choice is None:
            continue
        window.append(((mapping, state, steps), result[0]))
        if len(window) == 128:
            on = choice(window)
            decisions.append(on)
            if on != (solver.arm == "verified"):
                hits += solver.hits
                solver = engine.Run("verified" if on else "orbit")
            window.clear()
    return outputs, decisions, hits + solver.hits, clears


def audit(n, phases):
    rows = list(stream(n, phases))
    values = list(map(correct, rows))
    keys = [((m,s,h), value[0]) for (m,s,h,_), value in zip(rows, values, strict=True)]
    decisions = [oracle_module.oracle(keys[i:i+128]) for i in range(0,len(rows),128)]
    stats = {name: [] for name in ARMS}
    for repeat in range(7):
        for name in (tuple(ARMS) if repeat % 2 == 0 else tuple(reversed(ARMS))):
            start = perf_counter_ns()
            out, selected, hits, clears = run(rows, name)
            duration = perf_counter_ns() - start
            stats[name].append(dict(ns=duration, errors=sum(a != b for a,b in zip(out,values,strict=True)),
                                    decision_errors=sum(a!=b for a,b in zip(selected,decisions)),
                                    hits=hits, clears=clears, decisions=selected))
    return {name: dict(samples[0], ns=median(s["ns"] for s in samples),
                       errors=max(s["errors"] for s in samples),
                       decision_errors=max(s["decision_errors"] for s in samples))
            for name,samples in stats.items()}


def main():
    tick = perf_counter_ns()
    results = {n: {name: audit(n, phases) for name,phases in PROFILES.items()} for n in (37,41)}
    for cohorts in results.values():
        assert cohorts["switch"]["chunked"]["decisions"] == [True,True,False,False,True,True,False,True]
        assert all(r["errors"] == r["decision_errors"] == 0 for group in cohorts.values() for r in group.values())
    print(json.dumps(dict(results=results, elapsed_ns=perf_counter_ns()-tick), indent=2))


if __name__ == "__main__":
    main()
