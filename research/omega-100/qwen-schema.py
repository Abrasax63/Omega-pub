"""Paired local trial. Private fixture file is required as a separate argument."""
import copy
import json
import runpy
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

import baseline

PORT = 18723
LABELS = tuple(baseline.LABELS.values())


def candidate_request(contract):
    fields = [f"P{p['id']}" for p in contract['premises']] + ['C']
    lines = [f"P{p['id']} : {p['literal']}" for p in contract['premises']]
    lines.append(f"C : {contract['conclusion']['literal']}")
    prompt = (
        "Sur les entiers de -16 à 16, les lignes P sont les seules prémisses et C est la conclusion. "
        "Traduis chaque ligne dans sa clé, avec exactement un AST par ligne. "
        'AST : ["le",a,b] pour a<=b, ["eq",a,b] pour a=b, ["mod",a,m] pour le reste euclidien, '
        '["square",a] pour le carré. Les feuilles sont "n" ou un entier. '
        "Verdict : counterexample si un entier admissible contredit C, empty si aucun n'est admissible, "
        "holds sinon. Réponds uniquement avec l’objet JSON.\n" + "\n".join(lines)
    )
    schema = {
        'type': 'object',
        'properties': dict(
            {field: {'type': 'array', 'minItems': 2, 'maxItems': 3} for field in fields},
            verdict={'type': 'string', 'enum': list(LABELS)}),
        'required': [*fields, 'verdict'],
        'additionalProperties': False,
    }
    return fields, prompt, schema


def send_candidate(contract):
    _, prompt, schema = candidate_request(contract)
    data = json.dumps(dict(messages=[dict(role='user',content=prompt)],
        max_tokens=384, temperature=0, seed=71,
        response_format=dict(type='json_schema', schema=schema))).encode()
    request = Request(f'http://127.0.0.1:{PORT}/v1/chat/completions',data=data,
                      headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=150) as response:
        return json.load(response)


def parsed_reply(chat):
    try:
        content = chat['choices'][0]['message']['content'].strip()
        if content.startswith('```') and content.endswith('```'):
            content = '\n'.join(content.splitlines()[1:-1])
        value = json.loads(content)
        return value if isinstance(value, dict) else {}
    except (ValueError, KeyError, TypeError, AttributeError, IndexError):
        return {}


def inspect(source, contract, chat, arm):
    parsed = parsed_reply(chat)
    if arm == 'reference':
        premises = parsed.get('premises')
        format_ok = (isinstance(premises, list)
                     and len(premises) == len(contract['premises'])
                     and all(isinstance(p, list) for p in premises)
                     and isinstance(parsed.get('conclusion'), list)
                     and parsed.get('verdict') in LABELS)
        direct, verified, status = baseline.evaluate(source, contract, chat)
    else:
        fields, _, _ = candidate_request(contract)
        format_ok = (set(parsed) == {*fields, 'verdict'}
                     and all(isinstance(parsed[f], list) and 2 <= len(parsed[f]) <= 3 for f in fields)
                     and parsed['verdict'] in LABELS)
        direct = parsed.get('verdict') if parsed.get('verdict') in LABELS else 'abstain'
        if not format_ok:
            return format_ok, direct, 'abstain', 'SCHEMA'
        adapted = dict(premises=[parsed[f] for f in fields[:-1]],
                       conclusion=parsed['C'], verdict=direct)
        envelope = dict(choices=[dict(message=dict(content=json.dumps(adapted)))])
        direct, verified, status = baseline.evaluate(source, contract, envelope)
    return format_ok, direct, verified, status


def main():
    cases = runpy.run_path(sys.argv[1])['CASES']
    packed = [baseline.pack(case) for case in cases]
    for source, contract, expected, counter in packed:
        terms = [p['ast'] for p in contract['premises']]
        truth = baseline.check({'domain':[-16,16],
            'if': terms[0] if len(terms)==1 else ['and', *terms],
            'then': contract['conclusion']['ast']})
        assert baseline.LABELS[truth['status']] == expected
        assert truth.get('witness') == (counter[0] if counter else None)
    source, contract, expected, _ = packed[0]
    witness = {f"P{p['id']}":copy.deepcopy(p['ast']) for p in contract['premises']}
    witness.update(C=contract['conclusion']['ast'], verdict=expected)
    def reply(obj):
        return dict(choices=[dict(message=dict(content=json.dumps(obj)))])
    assert inspect(source, contract, reply(witness), 'candidate')[2] == expected
    witness['C'] = ['eq', 0, 1] if witness['C'] != ['eq', 0, 1] else ['eq', 1, 1]
    assert inspect(source, contract, reply(witness), 'candidate')[3] == 'REJECTED_SOURCE_AST_BINDING'
    for arm in ('reference', 'candidate'):
        for i, (source, contract, expected, _) in enumerate(packed, 1):
            start = time.perf_counter()
            chat = baseline.send(source) if arm == 'reference' else send_candidate(contract)
            duration = time.perf_counter() - start
            start = time.perf_counter()
            form, direct, verified, status = inspect(source, contract, chat, arm)
            evaluation = time.perf_counter() - start
            row = dict(arm=arm, case=i, expected=expected, form=form, direct=direct,
                       verified=verified, status=status, seconds=duration,
                       evaluation_seconds=evaluation, usage=chat['usage'],
                       finish=chat['choices'][0]['finish_reason'])
            Path(f'private-{arm}-{i}.json').write_text(json.dumps({'response':chat,'row':row}))
            print(json.dumps(row),flush=True)


if __name__ == '__main__':
    main()
