"""Exact cost threshold for the finite terminal-guard comparison.

The 125-case result prices probes, NOT computation that inspects known models.
Let c be the cost of one actual probe and g the cost of evaluating the
guard once. 125 cases yield 156 probes for guarded and 250 for fixed-both.

At equal correctness, guarded beats fixed-both iff 125g < 94c.
No empirical values for g/c are assumed or inferred here.
"""
from fractions import Fraction
import json

from legacy_guard_benchmark import run_audit


def compare_costs(guard_price_in_probe_units):
    g=Fraction(guard_price_in_probe_units)
    if g<0:
        raise ValueError("guard price must be nonnegative")
    result=run_audit()["primary"]
    cases=result["cases"]
    guarded=Fraction(result["guarded_probe_calls"])+cases*g
    fixed=Fraction(result["fixed_both_probe_calls"])
    naive=Fraction(result["naive_probe_calls"])
    return {
        "guard_cost_per_case":str(g),
        "guarded_all_case_cost":str(guarded),
        "fixed_both_all_case_cost":str(fixed),
        "naive_all_case_cost":str(naive),
        "guarded_vs_fixed":(
            "cheaper" if guarded<fixed else
            "tie" if guarded==fixed else "more_expensive"),
        "guarded_correct":result["guarded_correct"],
        "fixed_correct":result["fixed_both_correct"],
        "naive_correct":result["naive_correct"],
    }


def run():
    data=run_audit()["primary"]
    assert data=={
        "cases":125,"naive_correct":94,"guarded_correct":125,
        "fixed_both_correct":125,
        "naive_probe_calls":125,"guarded_probe_calls":156,
        "fixed_both_probe_calls":250,"guarded_second_probes":31,
    }
    threshold=Fraction(250-156,125)
    profiles=[compare_costs(value) for value in
              (Fraction(0),Fraction(1,2),Fraction(3,4),threshold,
               Fraction(1),Fraction(2))]
    assert [x["guarded_vs_fixed"] for x in profiles]==[
        "cheaper","cheaper","cheaper","tie","more_expensive","more_expensive"]
    return {
        "status":"SYMBOLIC_SENSITIVITY_NOT_MEASURED_RUNTIME",
        "break_even_guard_cost_per_case_probe_equivalents":str(threshold),
        "criterion":"guarded cheaper iff guard cost per case is less than 94/125 of one actual probe cost",
        "baseline_has_same_relative_completeness":True,
        "known_models_price_not_measured":True,
        "results":profiles,
    }


if __name__=="__main__":
    print("LEGACY_GUARD_COST_THRESHOLD "+json.dumps(run(),sort_keys=True))
