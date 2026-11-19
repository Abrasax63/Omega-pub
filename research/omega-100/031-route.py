"""Experimental source-to-manual-contract-to-finite-oracle routing, never certification."""
from source_ast_contract import accepts
from finite_oracle import check

def route(raw,contract,translation,*,require_binding=True):
    if require_binding and not accepts(raw,contract,translation):
        return dict(status='REJECTED_SOURCE_AST_BINDING',universal_proof=False)
    try:
        terms=[x['ast'] for x in translation['premises']]
        premise=terms[0] if len(terms)==1 else ['and']+terms
        result=check(dict(domain=[-16,16],**{'if':premise,'then':translation['conclusion']['ast']}))
    except (KeyError,TypeError,ValueError):
        return dict(status='ABSTAIN',reason='INVALID_TRANSLATION',universal_proof=False)
    return dict(result,source_ast_binding='MANUAL_CONTRACT_MATCH' if require_binding else 'NOT_CHECKED')
