"""Public-source integration rehearsal, NOT a model-quality evaluation or blind holdout.

Eight factual yes/no questions have source pointers to primary publications.
The asserted reference verdicts are public and curated with this script;
the policy does NOT fetch or understand their contents, so no benefit of
autonomous external research is claimed.
"""
from urllib.parse import urljoin

from action_planning_two_step import plan_with_variable_horizon


SOURCES = (
    {
        "id": "rfc9110-ims-inm", "question": "Si If-None-Match est present, HTTP doit-il ignorer If-Modified-Since ?",
        "url": "https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.3",
        "section": "RFC 9110, 13.1.3", "gold": "yes",
    },
    {
        "id": "rfc9110-ius-im", "question": "Si If-Match est present, HTTP doit-il ignorer If-Unmodified-Since ?",
        "url": "https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.4",
        "section": "RFC 9110, 13.1.4", "gold": "yes",
    },
    {
        "id": "rfc9110-ims-post", "question": "If-Modified-Since doit-il etre ignore sur une methode POST ?",
        "url": "https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.3",
        "section": "RFC 9110, 13.1.3", "gold": "yes",
    },
    {
        "id": "rfc3986-dot", "question": "La resolution relative d'URI elimine-t-elle les segments '..' du chemin ?",
        "url": "https://www.rfc-editor.org/rfc/rfc3986.html#section-5.2.4",
        "section": "RFC 3986, 5.2.4", "gold": "yes",
    },
    {
        "id": "rfc3986-join", "question": "Depuis http://a/b/c/d;p?q, ../g devient-il http://a/b/g ?",
        "url": "https://www.rfc-editor.org/rfc/rfc3986.html#section-5.4.1",
        "section": "RFC 3986, 5.4.1", "gold": "yes",
    },
    {
        "id": "python-isinstance", "question": "isinstance(True, int) vaut-il True en Python 3 ?",
        "url": "https://docs.python.org/3.11/reference/datamodel.html#the-standard-type-hierarchy",
        "section": "Python 3.11 data model, bool subtype of integer", "gold": "yes",
    },
    {
        "id": "python-type", "question": "type(True) is int vaut-il True en Python 3 ?",
        "url": "https://docs.python.org/3.11/reference/datamodel.html#the-standard-type-hierarchy",
        "section": "Python 3.11 data model, bool type", "gold": "no",
    },
    {
        "id": "python-int-eq", "question": "bool est-il une classe totalement distincte de int, sans heritage ?",
        "url": "https://docs.python.org/3.11/reference/datamodel.html#the-standard-type-hierarchy",
        "section": "Python 3.11 data model, bool subtype of integer", "gold": "no",
    },
)


def _source_verdict_checks():
    # Runnable cross-checks for the Python and URI examples; the HTTP
    # semantics cases are grounded in the pinned RFC, not evaluated by Python.
    return {
        "rfc3986-join": "yes" if (
            urljoin("http://a/b/c/d;p?q", "../g") == "http://a/b/g"
        ) else "no",
        "python-isinstance": "yes" if isinstance(True, int) else "no",
        "python-type": "yes" if type(True) is int else "no",
        "python-int-eq": "yes" if not issubclass(bool, int) else "no",
    }


def run_pilot():
    python_oracle = _source_verdict_checks()
    result = []
    for row in SOURCES:
        if row["id"] in python_oracle and row["gold"] != python_oracle[row["id"]]:
            raise AssertionError("stated public gold conflicts with runtime cross-check")
        case = {
            "case_id": row["id"], "question": row["question"],
            "mission_type": "documentary",
            "uncertainty": "La source officielle n'a pas ete lue par le planificateur.",
            "hypotheses": [
                {"id": "h-yes", "decision": "yes", "weight": 1},
                {"id": "h-no", "decision": "no", "weight": 1},
            ],
            "checks": [
                {
                    "id": "01-secondary-summary", "action": "verify",
                    "available": True, "cost_milli": 5,
                    "method": "inconclusive_secondary", "step": "Lire un resume non decisif.",
                    "observations": ["unknown", "unknown"],
                },
                {
                    "id": "02-read-primary", "action": "verify",
                    "available": True, "cost_milli": 20,
                    "method": "manual_primary_source", "step": "Lire " + row["url"],
                    "observations": ["yes", "no"],
                },
            ],
        }
        run = plan_with_variable_horizon(case, max_depth=4)
        policy = run["optimization"]["policy"]
        if policy["check_id"] != "02-read-primary":
            raise AssertionError("expected public-source check not chosen")
        branch = policy["branches"][row["gold"]]
        if branch["action"] != "answer":
            raise AssertionError("cannot close the case after gold source observation")
        result.append({
            "id": row["id"], "question": row["question"],
            "ground_truth": row["gold"], "source": row["url"],
            "first_action": policy["action"], "selected": policy["check_id"],
            "risk_after_primary_source": run["optimization"]["expected_decision_risk"],
        })
    return {
        "cases": len(result), "kind": "public_source_curated_rehearsal",
        "runnable_cross_checks": len(python_oracle),
        "source_check_selected": sum(r["selected"] == "02-read-primary" for r in result),
        "limits": ("Source gold is public and authored together with the hypotheses. "
                   "Primary-source checks are simulated; no web calls, no model responses, "
                   "no blind external graders, no evidence of real-world superiority."),
        "results": result,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_pilot(), ensure_ascii=False, indent=2))
