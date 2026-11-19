"""Compare the same prompt with and without typed expression constraints."""
import copy
import json
import runpy
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

import baseline
import pilot

DOMAIN = [-16, 16]


def tuple_schema(operator, *arguments):
    return {
        'type': 'array',
        'prefixItems': [{'const': operator}, *arguments],
        'minItems': 1 + len(arguments),
        'maxItems': 1 + len(arguments),
    }


def apply_ast_constraints(schema, fields):
    schema = copy.deepcopy(schema)
    integer = {'type': 'integer', 'minimum': -1000000, 'maximum': 1000000}
    modulus = {'type': 'integer', 'minimum': 1, 'maximum': 1000000}
    leaf = {'anyOf': [{'const': 'n'}, integer]}

    def ref(name):
        return {'$ref': f'#/$defs/{name}'}

    schema['$defs'] = {'leaf': leaf}
    for name, child in [('term1', 'leaf'), ('term2', 'term1')]:
        schema['$defs'][name] = {'anyOf': [
            ref('leaf'), tuple_schema('square', ref(child)),
            tuple_schema('mod', ref(child), modulus),
        ]}
    schema['$defs']['predicate'] = {'anyOf': [
        tuple_schema(operator, ref('term2'), ref('term2'))
        for operator in ('le', 'eq')
    ]}
    for field in fields:
        schema['properties'][field] = ref('predicate')
    return schema


def send(prompt, schema):
    payload = dict(messages=[dict(role='user', content=prompt)],
        max_tokens=384, temperature=0, seed=71,
        response_format=dict(type='json_schema', schema=schema))
    request = Request(f'http://127.0.0.1:{pilot.PORT}/v1/chat/completions',
        data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
    with urlopen(request, timeout=150) as response:
        return json.load(response)


def result(source, contract, chat):
    form, direct, verified, status = pilot.inspect(source, contract, chat, 'candidate')
    fields, _, _ = pilot.candidate_request(contract)
    reply = pilot.parsed_reply(chat)
    valid_fields = sum(
        baseline.check({'domain': DOMAIN, 'if': ['eq',0,0],
                        'then': reply.get(field)})['status'] != 'ABSTAIN'
        for field in fields
    )
    return dict(form=form, direct=direct, verified=verified, status=status,
                valid_fields=valid_fields, total_fields=len(fields))


def control():
    case = ([('n est au moins 3', ['le',3,'n'])], ('n est au plus 6',['le','n',6]),
            lambda n:n>=3, lambda n:n<=6)
    source, contract, expected, _ = baseline.pack(case)
    def response(premise):
        payload = dict(P1=premise, C=contract['conclusion']['ast'], verdict=expected)
        return dict(choices=[dict(message=dict(content=json.dumps(payload)))])
    assert result(source,contract,response(['le',3,'n']))['verified'] == expected
    bad = result(source,contract,response(['le','n',3]))
    assert bad['form'] and bad['valid_fields']==bad['total_fields']
    assert bad['status']=='REJECTED_SOURCE_AST_BINDING'


def main():
    control()
    cases = [baseline.pack(c) for c in runpy.run_path(sys.argv[1])['CASES']]
    for source, contract, expected, counter in cases:
        terms = [r['ast'] for r in contract['premises']]
        truth = baseline.check({'domain':DOMAIN,'if':terms[0] if len(terms)==1 else ['and',*terms],
            'then':contract['conclusion']['ast']})
        assert baseline.LABELS[truth['status']] == expected
        assert truth.get('witness') == (counter[0] if counter else None)
    for arm in ('reference','candidate'):
        for i,(source,contract,expected,_) in enumerate(cases,1):
            fields,prompt,schema = pilot.candidate_request(contract)
            if arm=='candidate':
                schema=apply_ast_constraints(schema,fields)
            start=time.perf_counter()
            chat=send(prompt,schema)
            seconds=time.perf_counter()-start
            start=time.perf_counter()
            outcome=result(source,contract,chat)
            row=dict(arm=arm,case=i,expected=expected,**outcome,seconds=seconds,
                evaluation_seconds=time.perf_counter()-start,usage=chat['usage'],
                finish=chat['choices'][0]['finish_reason'])
            Path(f'private-{arm}-{i}.json').write_text(json.dumps(dict(response=chat,row=row)))
            print(json.dumps(row),flush=True)


if __name__=='__main__':
    main()
