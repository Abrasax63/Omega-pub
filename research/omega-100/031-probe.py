import copy,hashlib,json,time
from route import route

def case(name,lower,upper,then,expected,mutation=None):
    raw=f'{name}: n est entier.\n{lower} <= n <= {upper}.\nConclusion formalisée manuellement: {then!r}.\n'.encode()
    c=dict(source_sha256=hashlib.sha256(raw).hexdigest(),premises=[dict(id='bounds',line=2,literal=raw.decode().splitlines()[1],ast=['and',['le',lower,'n'],['le','n',upper]])],conclusion=dict(line=3,literal=raw.decode().splitlines()[2],ast=then))
    t=copy.deepcopy(c)
    if mutation=='source':raw+=b'Source modifiee apres annotation.\n'
    if mutation=='ast':t['conclusion']['ast']=['le',0,['square','n']]
    return dict(name=name,raw=raw,contract=c,translation=t,expected=expected)

def run(x,binding):return route(x['raw'],x['contract'],x['translation'],require_binding=binding)
# Development cases are distinct from the reserved corpus.
dev=[case('dev-valid',0,1,['le',0,'n'],'NO_COUNTEREXAMPLE_WITHIN_DOMAIN'),case('dev-source',1,2,['le',0,'n'],'REJECTED_SOURCE_AST_BINDING','source')]
assert all(run(x,True)['status']==x['expected'] for x in dev)
reserved=[case('reserve-source',2,4,['le',0,'n'],'REJECTED_SOURCE_AST_BINDING','source'),case('reserve-ast',-3,-1,['le',0,'n'],'REJECTED_SOURCE_AST_BINDING','ast'),case('reserve-false',-2,2,['le',0,'n'],'COUNTEREXAMPLE'),case('reserve-vacuous',20,22,['eq','n',20],'NO_ADMISSIBLE_INPUT_WITHIN_DOMAIN'),case('reserve-true',-4,4,['le',0,['square','n']],'NO_COUNTEREXAMPLE_WITHIN_DOMAIN'),case('reserve-unsupported',3,5,['opaque','n'],'ABSTAIN')]
# Independent predicates check the three supported arithmetic obligations.
for idx,lo,hi,pred in [(2,-2,2,lambda n:n>=0),(3,20,22,lambda n:n==20),(4,-4,4,lambda n:n*n>=0)]:
    admissible=[n for n in range(-16,17) if lo<=n<=hi]
    failures=[n for n in admissible if not pred(n)]
    result=run(reserved[idx],True)
    assert result['admissible_inputs']==len(admissible)
    assert result.get('witness')==(failures[0] if failures else None)
outputs={}
for version,binding in [('reference',False),('candidate',True)]:
    start=time.perf_counter()
    for _ in range(1000):observed=[run(x,binding) for x in reserved]
    elapsed=time.perf_counter()-start
    assert elapsed<30
    outputs[version]=dict(correct=sum(r['status']==x['expected'] for x,r in zip(reserved,observed)),total=6,seconds=elapsed,calls=6000,statuses=[r['status'] for r in observed],universal_promotions=sum(r['universal_proof'] for r in observed),results=observed)
assert outputs['reference']['correct']==4 and outputs['candidate']['correct']==6
assert all(not r['universal_proof'] for v in outputs.values() for r in v['results'])
print(json.dumps(dict(experiment='031',results=outputs,source_hashes={x['name']:hashlib.sha256(x['raw']).hexdigest() for x in reserved},oracle='independent explicit Python predicates on range(-16,17)',scope='synthetic manual contracts; no language model; no universal proof'),sort_keys=True))
