"""Enforce independent citation lines only when the contract requests them."""
from premise_guard import route as reference


def route(raw, contract, translation, *, require_binding=True):
    if require_binding and isinstance(contract, dict) and contract.get('distinct_premise_lines') is True:
        try:
            lines = [entry['line'] for entry in contract['premises']]
            valid = all(type(line) is int for line in lines) and len(set(lines)) == len(lines)
        except (KeyError, TypeError):
            valid = False
        if not valid:
            return dict(status='REJECTED_SOURCE_AST_BINDING', universal_proof=False)
    return reference(raw, contract, translation, require_binding=require_binding)
