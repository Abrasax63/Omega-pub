"""Reject premise IDs outside the experimental string/integer contract."""
from line_guard import route as incumbent


def route(raw, contract, translation, *, require_binding=True):
    if require_binding:
        try:
            valid = all(
                type(entry['id']) in (str, int)
                for document in (contract, translation)
                for entry in document['premises']
            )
        except (KeyError, TypeError):
            valid = False
        if not valid:
            return dict(status='REJECTED_SOURCE_AST_BINDING', universal_proof=False)
    return incumbent(raw, contract, translation, require_binding=require_binding)
