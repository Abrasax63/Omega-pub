"""Reject mistyped values of an optional trusted contract policy."""
from distinct_guard import route as incumbent

POLICY = 'distinct_premise_lines'


def route(raw, contract, translation, *, require_binding=True):
    if (require_binding and isinstance(contract,dict)
            and POLICY in contract and type(contract[POLICY]) is not bool):
        return dict(status='REJECTED_SOURCE_AST_BINDING',universal_proof=False)
    return incumbent(raw,contract,translation,require_binding=require_binding)
