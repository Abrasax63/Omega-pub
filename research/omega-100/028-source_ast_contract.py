"""Experimental exact binding to a trusted manual source/AST contract."""
import json
from hashlib import sha256

def accepts(raw,contract,translation,*,bind_ast=True):
    try:
        digest=sha256(raw).hexdigest();lines=raw.decode('utf-8').splitlines()
        if contract['source_sha256']!=digest or translation['source_sha256']!=digest:return False
        expected=contract['premises'];given=translation['premises']
        if len(given)!=len(expected):return False
        ids=[x['id'] for x in given]
        if len(set(ids))!=len(ids) or set(ids)!={x['id'] for x in expected}:return False
        def canonical(ast):return json.dumps(ast,sort_keys=True,separators=(',',':'),allow_nan=False)
        def matches(need,actual):
            line=need['line'];literal=need['literal']
            if type(line) is not int or not 1<=line<=len(lines):return False
            if lines[line-1]!=literal:return False
            if actual['line']!=line or actual['literal']!=literal:return False
            return not bind_ast or canonical(actual['ast'])==canonical(need['ast'])
        lookup={x['id']:x for x in given}
        return all(matches(x,lookup[x['id']]) for x in expected) and matches(contract['conclusion'],translation['conclusion'])
    except (KeyError,TypeError,ValueError,UnicodeError,RecursionError):
        return False
