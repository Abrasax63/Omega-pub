"""STRAT-003: frozen new-parameter cases and executable certificate adapters.

No source retrieval/LLM calls during replay. Task outages are known only
to the simulator run_method(), NEVER to a trained policy or baseline.
"""
import json
from pathlib import Path
from strategic_methods_executable import (
    METHODS, oracle as previous_oracle, run_method as previous_method,
    _euler_dfs, _euler_theorem,
)

DATA = Path(__file__).with_name("certification_cases_v01.json")
HEADER_NORM = "https://www.rfc-editor.org/rfc/rfc9110#section-13.1.3"


def cases():
    envelope = json.loads(DATA.read_text(encoding="utf-8"))
    rows = envelope["cases"]
    if len(rows) != 48 or len({r["id"] for r in rows}) != 48:
        raise ValueError("frozen case list must contain 48 unique cases")
    return rows


def header_rule(params):
    # Question explicitly assumes a syntactically valid HTTP-date and
    # an available Last-Modified value. RFC 9110 sec. 13.1.3.
    return (params["has_ims"] and not params["has_inm"]
            and params["method"] in ("GET", "HEAD"))


def truth(task):
    if task["kind"] == "header":
        return header_rule(task["params"])
    return previous_oracle(task)


def run_method(task, method):
    if method not in METHODS:
        raise ValueError("unknown method")
    if task["kind"] != "header":
        return previous_method(task, method)
    if task["simulated_outage"] == method:
        return {"observation": "unknown", "certificate": "synthetic method outage"}
    if method != "source":
        return {"observation": "unknown",
                "certificate": "normative source not applicable to this method"}
    accepted = header_rule(task["params"])
    return {
        "observation": "yes" if accepted else "no",
        "certificate": "RFC 9110 13.1.3 eligibility predicate: " + HEADER_NORM,
    }


def outcome_key(result):
    """Use ONLY returned certificate/status, never a target label or outage flag."""
    value = result["observation"]
    if value in ("yes", "no"):
        if not isinstance(result["certificate"], str) or not result["certificate"]:
            raise ValueError("missing decisive certificate")
        return value
    if value != "unknown":
        raise ValueError("bad method observation")
    message = result["certificate"].lower()
    if "synthetic method outage" in message:
        return "unknown:outage"
    if any(x in message for x in
           ("no bounded witness", "no obstruction", "no collision",
            "no constructive witness", "finite search cannot prove",
            "no contradiction found")):
        return "unknown:no_proof"
    return "unknown:not_applicable"


def independent_checks():
    """Executable consistency controls distinct where mathematically possible."""
    rows = cases()
    from fractions import Fraction
    for row in rows:
        params = row["params"]
        if row["kind"] == "euler":
            if _euler_dfs(params["edges"]) != _euler_theorem(params["edges"]):
                raise AssertionError(row["id"] + " Euler paths disagree")
        if row["kind"] == "ratio":
            a, b = params["a"], params["b"]
            if (Fraction(*a) > Fraction(*b)) != (a[0]*b[1] > b[0]*a[1]):
                raise AssertionError(row["id"] + " rational paths disagree")
        if row["kind"] == "mod":
            # A universal linear congruence is true iff b and a are both 0
            # modulo m; verify the equivalent k=0 and k=1 conditions.
            a,b,m = params["a"],params["b"],params["m"]
            if truth(row) != (b%m == 0 and (a+b)%m == 0):
                raise AssertionError(row["id"] + " congruence paths disagree")
        for method in METHODS:
            result = run_method(row, method)
            if result["observation"] in ("yes","no"):
                if (result["observation"] == "yes") != truth(row):
                    raise AssertionError((row["id"],method,"unsound certificate"))
    return {"checked_cases": len(rows), "validated_methods": 4*len(rows)}
