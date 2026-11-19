"""Strict object member decoding for the experimental 035 input boundary."""
import json

from policy_guard import route as incumbent


class DuplicateKey(ValueError):
    """Two decoded member names in the same JSON object are equal."""


def unique_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise DuplicateKey
        result[key] = value
    return result


def route(raw, contract_json, translation_json):
    try:
        contract = json.loads(contract_json,object_pairs_hook=unique_object)
        translation = json.loads(translation_json,object_pairs_hook=unique_object)
    except DuplicateKey:
        return dict(status='REJECTED_DUPLICATE_JSON_KEY',universal_proof=False)
    except (ValueError, TypeError, RecursionError):
        return dict(status='REJECTED_INVALID_JSON',universal_proof=False)
    return incumbent(raw,contract,translation)
