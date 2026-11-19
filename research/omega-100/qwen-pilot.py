import copy
import hashlib
import json
import runpy
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

from finite_oracle import check
from route import route

D = range(-16, 17)
LABELS = {'COUNTEREXAMPLE':'counterexample','NO_ADMISSIBLE_INPUT_WITHIN_DOMAIN':'empty','NO_COUNTEREXAMPLE_WITHIN_DOMAIN':'holds'}
ROOT = Path(__file__).parent

def send(source):
    instruction = ("Sur les entiers de -16 à 16 inclus, analyse le texte. "
        "Réponds uniquement en JSON avec premises (liste des AST, dans l’ordre), conclusion (AST) et verdict "
        "(counterexample si un entier admissible contredit, empty si aucun entier admissible, holds sinon). "
        'AST autorisés : ["le",a,b] pour a<=b, ["eq",a,b] pour a=b, '
        '["mod",a,m] pour le reste euclidien et ["square",a] pour le carré. Les feuilles sont "n" ou un entier.\n')
    data = json.dumps(dict(messages=[dict(role='user',content=instruction+source)],
        max_tokens=384, temperature=0, seed=71)).encode()
    request = Request('http://127.0.0.1:18722/v1/chat/completions',
                      data=data,headers={'Content-Type':'application/json'})
    with urlopen(request, timeout=150) as response:
        return json.load(response)

def pack(case):
    premises, conclusion, premise_fn, conclusion_fn = case
    lines = [s for s,_ in premises] + [conclusion[0]]
    source = '\n'.join(lines)+'\n'
    raw = source.encode()
    entries = [dict(id=str(i),line=i,literal=s,ast=ast)
               for i,(s,ast) in enumerate(premises,1)]
    contract = dict(source_sha256=hashlib.sha256(raw).hexdigest(),
        premises=entries, conclusion=dict(line=len(lines),literal=lines[-1],ast=conclusion[1]))
    allowed = [n for n in D if premise_fn(n)]
    counter = [n for n in allowed if not conclusion_fn(n)]
    label = 'counterexample' if counter else 'holds' if allowed else 'empty'
    return source, contract, label, counter

def evaluate(source, contract, chat):
    try:
        content = chat['choices'][0]['message']['content'].strip()
        if content.startswith('```') and content.endswith('```'):
            content = '\n'.join(content.splitlines()[1:-1])
        parsed = json.loads(content)
        verdict = parsed['verdict']
    except (ValueError, KeyError, TypeError, AttributeError):
        return 'abstain', 'abstain', 'JSON_OR_VERDICT'
    if verdict not in ('holds','empty','counterexample'):
        verdict = 'abstain'
    try:
        proposed = parsed['premises']
        if not isinstance(proposed,list) or len(proposed)!=len(contract['premises']):
            return verdict,'abstain','PREMISE_COUNT'
        translated = copy.deepcopy(contract)
        for row,ast in zip(translated['premises'], proposed):
            row['ast']=ast
        translated['conclusion']['ast'] = parsed['conclusion']
    except (KeyError, TypeError):
        return verdict,'abstain','INVALID_TRANSLATION'
    result = route(source.encode(),contract,translated)
    assert result['universal_proof'] is False
    return verdict, LABELS.get(result['status'],'abstain'), result['status']

def main():
    cases = runpy.run_path(sys.argv[1])["CASES"]
    source, contract, _, _ = pack(cases[0])
    mutated = copy.deepcopy(contract['premises'][0]['ast'])
    mutated = ['eq', 0, 1] if mutated != ['eq', 0, 1] else ['eq', 1, 1]
    premises = [row['ast'] for row in contract['premises']]
    premises[0] = mutated
    negative = dict(choices=[dict(message=dict(content=json.dumps(dict(
        premises=premises, conclusion=contract['conclusion']['ast'], verdict='holds'))))])
    assert evaluate(source, contract, negative)[2] == 'REJECTED_SOURCE_AST_BINDING'
    for idx, case in enumerate(cases,1):
        source, contract, expected, counter = pack(case)
        terms = [r['ast'] for r in contract['premises']]
        ceiling = check({'domain':[-16,16],'if':terms[0] if len(terms)==1 else ['and',*terms],
                         'then':contract['conclusion']['ast']})
        assert LABELS[ceiling['status']]==expected
        assert ceiling.get('witness')==(counter[0] if counter else None)
        start = time.perf_counter()
        response = send(source)
        elapsed = time.perf_counter()-start
        start = time.perf_counter()
        direct, omega, status = evaluate(source,contract,response)
        control = time.perf_counter()-start
        row=dict(case=idx,expect=expected,direct=direct,omega=omega,status=status,
                 seconds=elapsed,control_seconds=control,tokens=response.get('usage'))
        (ROOT/f'private-{idx}.json').write_text(json.dumps(dict(source=source,contract=contract,
            response=response,result=row),ensure_ascii=False))
        print(json.dumps(row),flush=True)
if __name__=='__main__':
    main()
