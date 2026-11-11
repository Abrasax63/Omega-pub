"""Post-result boundary test: what if evidence schema is visible for free?

NOT a legal comparator in the opaque experiment: it has stronger initial
information than all six preregistered arms. It assesses transportability
of the measured benefit to transparent real-world task descriptions.
"""
import json
from intermediate_evidence_gateway import (
    cases,run_check,ROUTE_TO_SPECIALIST,_route_from_payload,
    _actual_truth,independent_verify
)
from intermediate_evidence_policy import evaluate


def audit():
    target=[t for t in cases() if t["partition"]=="test"]
    correct=wrong=abstain=calls=0
    rows=[]
    for task in target:
        route=_route_from_payload(task["payload"])  # FREE extra metadata
        method=ROUTE_TO_SPECIALIST[route]
        receipt=run_check(task,method)
        if not independent_verify(task,receipt):
            raise AssertionError("not a valid certificate")
        calls+=1
        decision=receipt["outcome"] if receipt["outcome"] in ("yes","no") else None
        truth="yes" if _actual_truth(task) else "no"
        if decision is None:abstain+=1
        elif decision==truth:correct+=1
        else:wrong+=1
        rows.append({"id":task["id"],"method":method,"answer":decision,"truth":truth})
    opaque=evaluate()["scores"]["D_certificate"]
    return {
        "status":"POST_RESULT_ALTERNATIVE_INFORMATION_REGIME_NOT_FAIR_COMPETITOR",
        "description":"Case schema is given for free before choosing an action; original six arms did not have it",
        "visible_schema_correct":correct,
        "visible_schema_abstain":abstain,
        "visible_schema_wrong":wrong,
        "visible_schema_checks":calls,
        "opaque_certificate_correct":opaque["correct"],
        "opaque_certificate_checks":opaque["calls"],
        "potential_cost_savings_if_schema_visible":opaque["calls"]-calls,
        "cannot_compare_as_equal_information":True,
        "rows":rows,
    }


if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,indent=2,sort_keys=True))
