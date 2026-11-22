"""First source-scoped Riemann reading benchmark for existing Omega logic engine.

Truth in this test: an independently enumerated finite Horn abstraction of a
manually annotated conditional reduction in Rubinstein's working guide.
This does NOT parse the PDF automatically, recheck Alpoge's Lean proof,
prove RH, or establish broad mathematical understanding.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
from math import comb, prod
import json
from pathlib import Path
import sys

MAX_CASES = 24
MAX_ATOMS = 7


def rules_for(manifest, variant):
    base = manifest["manual_controlled_rules"]["standard"]
    if variant == "standard":
        return list(base)
    if variant == "reverse_order":
        return list(reversed(base))
    if variant == "paraphrase":
        return list(manifest["manual_controlled_rules"]["paraphrase"])
    if variant == "first_only":
        return [base[0]]
    if variant == "second_only":
        return [base[1]]
    if variant == "extra_unrelated":
        return list(base) + [{"ref": "EXTRA", "text": "Si x, alors y.",
                              "premises": ["x"], "conclusion": "y"}]
    if variant == "unsupported_correlation":
        return list(base) + [{"ref": "FALSE-ASSOCIATION",
                              "text": "m est corrélé à rh.",
                              "premises": [], "conclusion": None}]
    if variant == "unsupported_disjunction":
        return [{"ref": "UNSUPPORTED-OR", "text": "Si m et b ou c, alors rh.",
                 "premises": [], "conclusion": None}]
    raise ValueError(f"Unknown variant: {variant}")


def boolean_oracle(facts, goal, reference_rules):
    """Exact truth-table oracle independent of existing Omega proof_closure."""
    atoms = set(facts) | {goal}
    for rule in reference_rules:
        atoms.update(rule["premises"])
        atoms.add(rule["conclusion"])
    atoms = sorted(atoms)
    if len(atoms) > MAX_ATOMS:
        raise ValueError("Boolean oracle budget exceeded")
    valid_models = 0
    counter = None
    for bits in product((False, True), repeat=len(atoms)):
        valuation = dict(zip(atoms, bits))
        if not all(valuation[x] for x in facts):
            continue
        if not all(not all(valuation[x] for x in rule["premises"])
                   or valuation[rule["conclusion"]] for rule in reference_rules):
            continue
        valid_models += 1
        if not valuation[goal] and counter is None:
            counter = {x: v for x, v in valuation.items() if v}
    if valid_models == 0:
        raise ValueError("Unsatisfiable manually declared source logic")
    return {"verdict": "NOT_ENTAILED" if counter is not None else "ENTAILED",
            "satisfying_models": valid_models, "countermodel_true_atoms": counter}


def is_prime(p):
    return p >= 2 and all(p % d != 0 for d in range(2, int(p ** 0.5) + 1))


def chebyshev_exact(max_n=48):
    """Finite witnesses to Chebyshev's *elementary* example, not to RH."""
    checks = 0
    for n in range(1, max_n + 1):
        c = comb(2*n, n)
        if c > 4 ** n:
            raise ValueError(f"Known elementary size inequality failed at {n}")
        primes = [p for p in range(n+1, 2*n+1) if is_prime(p)]
        for p in primes:
            checks += 1
            if c % p != 0:
                raise ValueError(f"Prime in (n,2n] did not divide central binomial: n={n}, p={p}")
        if c % prod(primes) != 0 or prod(primes) > 4 ** n:
            raise ValueError("Finite Chebyshev witness contradictory")
    # Counterfactuals: neither reverse implication nor a gratuitously
    # strengthened bound may be assumed from the source.
    n, p = 4, 2
    if not is_prime(p) or comb(2*n, n) % p != 0 or n < p:
        raise ValueError("The inverse-implication counterexample was lost")
    boundary = (3, 3, comb(6, 3))
    if not is_prime(boundary[1]) or boundary[2] % boundary[1] == 0:
        raise ValueError("The strict lower boundary test was lost")
    bad_bound_n = next((n for n in range(1, max_n + 1)
                        if comb(2*n, n) > 3 ** n), None)
    if bad_bound_n is None:
        raise ValueError("The stronger bound was not refuted")
    return {
        "kind": "ELEMENTARY_EXACT_FINITE_ONLY",
        "source_section": "Rubinstein working guide, Part I.0 p.3",
        "n_range": [1, max_n],
        "prime_divisibility_checks": checks,
        "tested_size_inequality": "binom(2n,n) <= 4^n",
        "finite_violations": 0,
        "inverse_counterexample": {"n": n, "p": p, "central_binomial": comb(2*n, n)},
        "strict_boundary_counterexample": {"n": boundary[0], "p": boundary[1],
                                           "central_binomial": boundary[2]},
        "false_strengthening_counterexample": {
            "n": bad_bound_n, "central_binomial": comb(2*bad_bound_n, bad_bound_n),
            "false_claim": "binom(2n,n) <= 3^n for all n"},
        "inference_to_RH": "NOT_SUPPORTED_BY_FINITE_CHECKS",
    }


def evaluate(manifest, omega_root):
    if manifest.get("benchmark_id") != "OMEGA-RH-READING-01" or manifest.get("schema") != 1:
        raise ValueError("Unknown or corrupted preregistration")
    cases = manifest.get("cases", [])
    if not 10 <= len(cases) <= MAX_CASES or len({x["id"] for x in cases}) != len(cases):
        raise ValueError("Unexpected case set")
    script = Path(omega_root) / "09_INFRASTRUCTURE_AGENTIQUE/controlled_entailment"
    sys.path.insert(0, str(script))
    try:
        from engine import evaluate_case, verify_certificate
        counts = {"omega": Counter(), "one_pass": Counter(), "conditions": Counter()}
        outputs = []
        for c in cases:
            rules = rules_for(manifest, c["variant"])
            controlled = {"facts": c["facts"], "goal": c["goal"],
                          "sources": [{"ref": r["ref"], "text": r["text"]} for r in rules]}
            if any(r["conclusion"] is None for r in rules):
                reference = {"verdict": "ABSTAIN", "source_logic": "UNSUPPORTED_GRAMMAR"}
            else:
                reference = boolean_oracle(c["facts"], c["goal"], rules)
            if reference["verdict"] != c["expect"]:
                raise ValueError("Contradictory manually preregistered reference: " + c["id"])
            omega = evaluate_case(controlled)
            baseline = evaluate_case(controlled, one_pass=True)
            for name, answer in (("omega", omega), ("one_pass", baseline)):
                counts[name]["correct"] += int(answer["verdict"] == reference["verdict"])
                counts[name]["incorrect"] += int(answer["verdict"] != reference["verdict"])
                counts[name]["abstain"] += int(answer["verdict"] == "ABSTAIN")
                counts[name]["false_entailed"] += int(
                    answer["verdict"] == "ENTAILED" and reference["verdict"] != "ENTAILED")
            if reference["verdict"] != "ABSTAIN" and omega["verdict"] != "ABSTAIN":
                if not verify_certificate(controlled, omega):
                    raise ValueError("Omega produced an unverified logic certificate in " + c["id"])
                counts["conditions"]["certificates_checked"] += 1
            outputs.append({
                "id": c["id"], "category": c["tag"],
                "gold_from_manual_rules_and_truth_table": reference["verdict"],
                "omega": omega["verdict"], "one_pass": baseline["verdict"],
                "status": "CONTROLLED_LOGIC_NOT_FREE_TEXT_COMPREHENSION",
            })
        arithmetic = chebyshev_exact(manifest["protocol"]["max_arithmetic_n"])
        return {
            "status": "BOUNDED_RH_READING_FALSIFICATION_NOT_RH_PROOF",
            "source_documents": manifest["source_documents"],
            "semantic_limits": manifest["distinctions"],
            "source_translation": "MANUAL_HORN_ABSTRACTION_NOT_INDEPENDENT_PDF_READER",
            "case_count": len(cases),
            "metrics": {x: dict(k) for x, k in counts.items()},
            "controlled_cases": outputs,
            "chebyshev": arithmetic,
            "scientific_discoveries": 0,
            "proofs_of_RH_generated": 0,
            "machine_verified_Lean_proof_rechecked": False,
        }
    finally:
        sys.path.pop(0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--omega100", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = evaluate(json.loads(a.manifest.read_text(encoding="utf-8")), a.omega100)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cases": report["case_count"],
                      "logic": report["metrics"], "arithmetic_checks": report["chebyshev"]["prime_divisibility_checks"],
                      "new_theorems": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
