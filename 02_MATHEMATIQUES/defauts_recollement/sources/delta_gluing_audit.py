#!/usr/bin/env python3
"""Exact finite audit for endpoint defects and internal gluing.

No third-party dependencies. The exhaustive scans enumerate raw pairs (T,pi);
isomorphic presentations are intentionally not counted as different results in
any minimality claim. The direct trace and subset computations are independent.
"""
from collections import Counter, defaultdict
from itertools import product
import json

def trace(t, p, x, length):
    out = []
    for _ in range(length):
        out.append(p[x])
        x = t[x]
    return tuple(out)

def words(t, p, length):
    return {trace(t, p, x, length) for x in range(len(t))}

def q_edges(t, p):
    return {(p[x], p[t[x]]) for x in range(len(t))}

def local_words(w, q_edges_set):
    return all((w[i], w[i + 1]) in q_edges_set for i in range(len(w) - 1))

def delta_all_empty(t, p):
    """Unary product state (Q^h,T^h) proves the all-h claim, not a cutoff."""
    n = len(t)
    edge = frozenset(q_edges(t, p))
    q_power = edge
    t_power = tuple(t)
    seen = set()
    h = 1
    while (q_power, t_power) not in seen:
        seen.add((q_power, t_power))
        actual = {(p[x], p[t_power[x]]) for x in range(n)}
        if q_power - actual:
            return False, h, sorted(q_power - actual), len(seen)
        q_power = frozenset((a, c) for a, b in q_power for b2, c in edge if b == b2)
        t_power = tuple(t[t_power[x]] for x in range(n))
        h += 1
    return True, None, [], len(seen)

def behavioral_partition(t, p):
    """Refine equality of infinite futures until stable."""
    n = len(t)
    signatures = tuple((p[x],) for x in range(n))
    partitions = []
    while True:
        ids = {s: i for i, s in enumerate(sorted(set(signatures)))}
        classes = tuple(ids[s] for s in signatures)
        partitions.append(classes)
        new_signatures = tuple((p[x], classes[t[x]]) for x in range(n))
        if len(set(new_signatures)) == len(set(signatures)):
            return len(partitions), len(set(classes)), classes
        signatures = new_signatures

def forbidden_basis(t, p, q, max_length):
    all_words = [None] + [words(t, p, length) for length in range(1, max_length + 1)]
    basis = set()
    for length in range(2, max_length + 1):
        for w in product(range(q), repeat=length):
            if w not in all_words[length] and w[:-1] in all_words[length - 1] and w[1:] in all_words[length - 1]:
                basis.add(w)
    return basis

def invariants(t, p, q):
    lstar, k, classes = behavioral_partition(t, p)
    basis = forbidden_basis(t, p, q, lstar + 1)
    rcl = max((len(w) - 1 for w in basis), default=0)
    de, first, witness, period_states = delta_all_empty(t, p)
    w2 = words(t, p, 2)
    w3 = words(t, p, 3)
    w4 = words(t, p, 4)
    mu2 = tuple(sorted(Counter(trace(t, p, x, 2) for x in range(len(t))).items()))
    return {
        "K": k, "Lstar": lstar, "rcl": rcl, "basis": tuple(sorted(basis)),
        "Q": tuple(sorted(w2)), "mu2": mu2,
        "W3": tuple(sorted(w3)), "W4": tuple(sorted(w4)),
        "delta_all_empty": de, "first_delta_h": first,
        "delta_witness": witness, "unary_product_states": period_states,
        "behavioral_classes": classes,
    }

def family(m):
    """State 0: 0 loop; states 1..m: delay chain; state m+1: 1 loop."""
    t = (0,) + tuple((j - 1 if j > 1 else m + 1) for j in range(1, m + 1)) + (m + 1,)
    p = (0,) * (m + 1) + (1,)
    return t, p

def subset_accepts(t, p, w):
    """Independent forward filter: sets of states after reading a word."""
    available = set(range(len(t)))
    for label in w:
        available = {t[x] for x in available if p[x] == label}
    return bool(available)

def brute_audit(t, p, q, max_length):
    for length in range(1, max_length + 1):
        for w in product(range(q), repeat=length):
            assert subset_accepts(t, p, w) == (w in words(t, p, length)), (t, p, w)
    inv = invariants(t, p, q)
    basis = inv["basis"]
    for length in range(1, max_length + 1):
        for w in product(range(q), repeat=length):
            basis_accepts = not any(w[i:i+len(f)] == f for f in basis for i in range(length-len(f)+1))
            assert basis_accepts == (w in words(t, p, length)), (t, p, w)

def scan(n, q):
    totals = Counter()
    strongest = None
    mu_groups = defaultdict(dict)
    key_examples = {}
    for t in product(range(n), repeat=n):
        for p in product(range(q), repeat=n):
            if len(set(p)) != q:
                continue
            inv = invariants(t, p, q)
            totals["presentations"] += 1
            totals["all_delta_empty"] += inv["delta_all_empty"]
            totals[f"rcl_{inv['rcl']}"] += 1
            minimal = inv["K"] == n
            if minimal:
                totals["behaviorally_minimal"] += 1
            if inv["delta_all_empty"] and inv["W3"] != tuple(sorted(w for w in product(range(q), repeat=3) if local_words(w, set(inv["Q"])))):
                totals["delta_zero_gamma3_nonempty"] += 1
                key_examples.setdefault("delta_zero_gamma3", (t, p, inv))
            if inv["delta_all_empty"] and inv["rcl"] > 1:
                if strongest is None or (inv["rcl"], -n) > (strongest[2]["rcl"], -n):
                    strongest = (t, p, inv)
            if minimal and inv["delta_all_empty"]:
                gkey = (inv["Q"], inv["mu2"])
                if inv["W3"] not in mu_groups[gkey]:
                    mu_groups[gkey][inv["W3"]] = (t, p, inv)
                    if len(mu_groups[gkey]) >= 2:
                        key_examples.setdefault("same_Q_mu2_different_W3", list(mu_groups[gkey].values())[:2])
    return totals, strongest, key_examples

def short_example(item):
    if item is None:
        return None
    t, p, inv = item
    return {"T": t, "pi": p, "K": inv["K"], "Lstar": inv["Lstar"],
            "rcl": inv["rcl"], "basis": inv["basis"],
            "Q": inv["Q"], "mu2": inv["mu2"], "W3": inv["W3"]}

def main():
    output = {"scans": {}, "family": {}, "audits": []}
    for n, q in [(2, 2), (3, 2), (4, 2), (5, 2), (3, 3), (4, 3)]:
        totals, strongest, examples = scan(n, q)
        output["scans"][f"n{n}_q{q}"] = {
            "totals": dict(totals), "max_example": short_example(strongest),
            "examples": {key: ([short_example(x) for x in val] if isinstance(val, list) else short_example(val))
                         for key, val in examples.items()}}
        print(f"n={n}, q={q}: {dict(totals)}", flush=True)
    for m in [1, 2, 3, 4, 5]:
        t, p = family(m)
        inv = invariants(t, p, 2)
        brute_audit(t, p, 2, min(m+5, 9))
        assert inv["delta_all_empty"] and inv["K"] == m + 2
        assert inv["rcl"] == m + 1 and inv["Lstar"] == m + 1
        output["family"][str(m)] = short_example((t, p, inv))
        output["audits"].append(f"family_m{m}_independent_subset_vs_direct_vs_basis")
    with open("delta_gluing_audit.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("Wrote delta_gluing_audit.json", flush=True)

if __name__ == "__main__":
    main()
