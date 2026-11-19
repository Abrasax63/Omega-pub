"""Require exact integer line numbers before routing a bound translation."""
from route import route as reference_route


def route(raw, contract, translation, *, require_binding=True):
    if require_binding:
        try:
            entries = [*translation['premises'], translation['conclusion']]
            lines_are_integers = all(type(entry['line']) is int for entry in entries)
        except (KeyError, TypeError):
            lines_are_integers = False
        if not lines_are_integers:
            return dict(status='REJECTED_SOURCE_AST_BINDING', universal_proof=False)
    return reference_route(raw, contract, translation, require_binding=require_binding)
