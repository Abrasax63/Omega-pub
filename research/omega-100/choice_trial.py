"""Audit a local model choosing one exact search method under a common cap."""
import itertools
import json
import random
import statistics
import sys
import time
from collections import deque
from pathlib import Path
from urllib.request import Request, urlopen

CAP = 64


class OutOfBudget(Exception):
    pass


class Cap:
    def __init__(self):
        self.used = 0

    def tick(self):
        if self.used == CAP:
            raise OutOfBudget
        self.used += 1


def direct_parity(case, meter):
    for mask in range(1 << case['n']):
        meter.tick()
        for a,b,p in case['edges']:
            meter.tick()
            if ((mask>>a)^(mask>>b))&1 != p:
                break
        else:
            return True,mask
    return False,None


def graph_parity(case, meter):
    n = case['n']
    adj = [[] for _ in range(n)]
    for a,b,p in case['edges']:
        meter.tick()
        adj[a].append((b,p))
        adj[b].append((a,p))
    colors = [None]*n
    for root in range(n):
        if colors[root] is not None:
            continue
        meter.tick()
        colors[root] = 0
        ready = deque([root])
        while ready:
            a = ready.popleft()
            for b,p in adj[a]:
                meter.tick()
                want = colors[a]^p
                if colors[b] is None:
                    colors[b] = want
                    ready.append(b)
                elif colors[b] != want:
                    return False,None
    return True,sum(color<<i for i,color in enumerate(colors))


def direct_sum(case, meter):
    values = case['values']
    for mask in range(1 << len(values)):
        meter.tick()
        total = 0
        for i,value in enumerate(values):
            if mask>>i&1:
                meter.tick()
                total += value
        if total == case['target']:
            return True,mask
    return False,None


def dynamic_sum(case, meter):
    target = case['target']
    reachable = {0:0}
    if target == 0:
        return True,0
    for i,value in enumerate(case['values']):
        for total,mask in tuple(reachable.items()):
            meter.tick()
            new = total+value
            if new == target:
                return True,mask|(1<<i)
            if new < target:
                reachable.setdefault(new,mask|(1<<i))
    return False,None


def solve(case, choice):
    methods = {'parity':(direct_parity,graph_parity), 'subset':(direct_sum,dynamic_sum)}
    meter = Cap()
    start = time.perf_counter()
    answer, witness = None,None
    try:
        if choice in ('A','B'):
            answer,witness = methods[case['kind']][choice=='B'](case,meter)
    except OutOfBudget:
        pass
    return dict(answer=answer,witness=witness,steps=meter.used,seconds=time.perf_counter()-start)


def truth(case):
    if case['kind']=='parity':
        return any(all(values[a]!=values[b] if p else values[a]==values[b]
                       for a,b,p in case['edges'])
                   for values in itertools.product((False,True),repeat=case['n']))
    values = case['values']
    return any(sum(group)==case['target'] for length in range(len(values)+1)
               for group in itertools.combinations(values,length))


def verify(case, run, label):
    if run['answer'] is None:
        return 'abstain'
    if run['answer'] != label:
        return 'error'
    if run['answer']:
        mask = run['witness']
        size = case['n'] if case['kind']=='parity' else len(case['values'])
        if type(mask) is not int or not 0<=mask<1<<size:
            return 'error'
        if case['kind']=='parity':
            colors = [bool(mask & (1<<i)) for i in range(size)]
            valid = all((colors[a]!=colors[b]) == bool(p) for a,b,p in case['edges'])
        else:
            valid = sum(v for i,v in enumerate(case['values']) if mask>>i&1)==case['target']
        if not valid:
            return 'error'
    return 'correct'


def select(case):
    rules = (
        'Choisis une méthode pour résoudre exactement cette instance avant un plafond de 64 étapes. '
        'Parité: [a,b,p] impose couleur(a) XOR couleur(b)=p. '
        'A parcourt les masques de couleurs croissants, coût un par masque et un par relation testée; '
        'B construit le graphe puis propage, coût un par arête insérée, sommet racine et arête orientée parcourue. '
        'Somme: choisir un sous-ensemble de valeurs positives. '
        'A parcourt les masques croissants, coût un par masque et valeur additionnée; '
        'B maintient les sommes atteignables sous la cible, coût un par addition à partir de chaque somme atteinte. '
        'Rends A, B ou aucune. Données: '+json.dumps(case,ensure_ascii=False,separators=(',',':'))
    )
    schema = dict(type='object',properties=dict(method=dict(type='string',enum=['A','B','aucune'])),
                  required=['method'],additionalProperties=False)
    payload = dict(messages=[dict(role='user',content=rules)],max_tokens=8,temperature=0,seed=71,
                   response_format=dict(type='json_schema',schema=schema))
    req = Request('http://127.0.0.1:18725/v1/chat/completions',data=json.dumps(payload).encode(),
                  headers={'Content-Type':'application/json'})
    start = time.perf_counter()
    with urlopen(req,timeout=90) as f:
        response=json.load(f)
    cost=time.perf_counter()-start
    try:
        choice=json.loads(response['choices'][0]['message']['content'])['method']
    except (KeyError, IndexError, TypeError, ValueError):
        choice='aucune'
    return choice,cost,response['usage']


def main():
    control=dict(kind='parity',n=3,edges=[(0,1,0),(1,2,1)])
    assert all(verify(control,solve(control,m),truth(control))=='correct' for m in 'AB')
    bad=dict(kind='subset',values=[4,8,12],target=3)
    assert not truth(bad) and all(verify(bad,solve(bad,m),False)=='correct' for m in 'AB')
    assert verify(control,solve(control,'aucune'),True)=='abstain'
    cases=json.loads(Path(sys.argv[1]).read_text())
    assert len(cases)==16 and sum(c['kind']=='parity' for c in cases)==8
    controls = []
    for i,case in enumerate(cases):
        label=truth(case)
        methods = {m:solve(case,m) for m in 'AB'}
        controls.append((case,label,methods))
    for i,(case,label,methods) in enumerate(controls):
        choice,cost,usage=select(case)
        observed=solve(case,choice)
        row=dict(case=i,family=case['kind'],selector_choice=choice,
            selector_seconds=cost,tokens=usage,
            fixed={m:dict(status=verify(case,r,label),steps=r['steps'],seconds=r['seconds']) for m,r in methods.items()},
            selected=dict(status=verify(case,observed,label),steps=observed['steps'],seconds=observed['seconds']))
        print(json.dumps(row),flush=True)


if __name__=='__main__':
    main()
