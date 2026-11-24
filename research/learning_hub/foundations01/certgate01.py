"""Exact six-bit certification; no neural extraction or oracle authenticity claim."""
import hashlib,json,random
from collections import Counter
from pathlib import Path
FULL=(1<<64)-1
SCOPE='six-ordered-relation-bits/v1'

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def evidence_map(evidence):
    d={}
    for m,y in evidence:
        if type(m) is not int or not 0<=m<64 or type(y) is not int or y not in (0,1): raise ValueError('INVALID_EVIDENCE')
        if m in d and d[m]!=y: raise ValueError('CONTRADICTORY_EVIDENCE')
        d[m]=y
    return d

def certify(evidence,scope=SCOPE):
    if scope!=SCOPE: raise ValueError('SCOPE')
    d=evidence_map(evidence)
    if len(d)!=64: return None
    payload={'scope':scope,'evidence':[[i,d[i]] for i in range(64)],'table':format(sum(y<<m for m,y in d.items()),'016x')}
    return dict(payload,sha256=digest(payload))

def verify(cert,evidence,scope=SCOPE):
    try:
        if scope!=SCOPE or not isinstance(cert,dict) or set(cert)!={'scope','evidence','table','sha256'}: return False
        d=evidence_map(evidence)
        if len(d)!=64 or cert['scope']!=scope or cert['evidence']!=[[i,d[i]] for i in range(64)]: return False
        table=''.join(format(sum(d[4*i+j]<<j for j in range(4)),'x') for i in reversed(range(16)))
        return cert['table']==table and cert['sha256']==digest({k:v for k,v in cert.items() if k!='sha256'})
    except (ValueError,TypeError,KeyError): return False

def library():
    leaves=[sum(1<<m for m in range(64) if m>>i&1) for i in range(6)]
    levels={1:set(leaves)};cost={f:1 for f in leaves}
    for c in range(2,8):
        cur={FULL^f for f in levels[c-1]}
        for a in range(1,c-1):
            for f in levels[a]:
                for g in levels[c-1-a]:cur.update((f&g,f|g,f^g))
        levels[c]=cur-cost.keys();cost.update({f:c for f in levels[c]})
    return leaves,cost

def teachers(seed,leaves,cost,excluded=()):
    rng=random.Random(seed);used=set(excluded);rows=[]
    def add(k,f):used.add(f);rows.append((k,f))
    def support(f):return sum(any((f>>m&1)!=(f>>(m^(1<<i))&1) for m in range(64)) for i in range(6))
    for k,c,s in [('IN',5,3),('EXT',7,4)]:
        for f in rng.sample(sorted(f for f in cost if cost[f]==c and support(f)>=s and f not in used),12):add(k,f)
    def tree(xs):
        if len(xs)==1:return leaves[xs[0]]
        p=rng.randrange(1,len(xs));f=tree(xs[:p]);g=tree(xs[p:]);return (f&g,f|g,f^g)[rng.randrange(3)]
    for k in ('FAR','NEAR'):
        inside=[f for t,f in rows if t=='IN']
        for _ in range(10000):
            if sum(t==k for t,f in rows)==12:break
            f=tree(rng.sample(range(6),5)) if k=='FAR' else rng.choice(inside)^(1<<rng.randrange(64))
            if f not in cost and f not in used and (k=='NEAR' or support(f)>=4):add(k,f)
        else:raise ValueError('TARGET_BUDGET')
    return rows

def run(ask,small,large,order):
    evidence=[];state=set(small);expanded=False;confirmed=0;available=list(order);records={}
    for step in range(1,65):
        n=len(state)
        m=max(available,key=lambda i:min(sum(f>>i&1 for f in state),n-sum(f>>i&1 for f in state))) if n>1 else available[0]
        available.remove(m);y=ask(m);evidence.append((m,y));old=state
        state={f for f in state if f>>m&1==y}
        if not state and not expanded:
            expanded=True;state={f for f in large if all(f>>i&1==v for i,v in evidence)};confirmed=0
        elif n==1 and state==old:confirmed+=1
        else:confirmed=0
        if step in (16,32,64):
            cert=certify(evidence)
            records[step]={'status':'FINITE_TABLE_CERTIFIED' if cert else 'GRAMMAR_REFUTED' if not state else 'CONDITIONAL_HYPOTHESIS' if len(state)==1 else 'AMBIGUOUS','candidate':next(iter(state)) if len(state)==1 else None,'remaining':len(state),'expanded':expanded,'old_accept':len(state)==1 and confirmed>=4,'certificate':cert,'evidence':list(evidence)}
    return records

def mutations():
    e=[(i,i%2) for i in range(64)];c=certify(e)
    def rejects(fn):
        try:fn();return False
        except ValueError:return True
    return {'valid':verify(c,e),'duplicate_not_coverage':certify(e[:-1]+[e[0]]) is None,'missing':certify(e[:-1]) is None,'duplicate_consistent':certify(e+[e[0]])==c,'conflict':rejects(lambda:certify(e+[(0,1)])),'invalid_motif':rejects(lambda:certify(e+[(64,0)])),'invalid_label':rejects(lambda:certify(e+[(0,2)])),'bool_rejected':rejects(lambda:certify(e+[(True,1)])),'wrong_scope':not verify(c,e,'other'),'wrong_table':not verify(dict(c,table='0'*16),e),'wrong_digest':not verify(dict(c,sha256='0'*64),e),'wrong_evidence':not verify(c,[(i,1-y) for i,y in e])}

def main(out):
    leaves,cost=library();small={f for f,c in cost.items() if c<=5};large=set(cost)
    old=teachers(20261205,leaves,cost);targets=teachers(20261206,leaves,cost,[f for _,f in old]);assert len(set(f for _,f in old+targets))==96
    records=[];summary={str(b):Counter() for b in (16,32,64)}
    for t,(kind,target) in enumerate(targets):
        order=list(range(64));random.Random(20261206+50000+t).shuffle(order)
        trace=run(lambda m:target>>m&1,small,large,order)
        for b,r in trace.items():
            c=summary[str(b)];c[r['status']]+=1
            if r['candidate'] is not None:c['candidate_exact' if r['candidate']==target else 'candidate_wrong']+=1
            if r['old_accept']:c['old_exact' if r['candidate']==target else 'old_false_accept']+=1
            if r['certificate']:
                assert verify(r['certificate'],r['evidence']);c['certificate_exact' if int(r['certificate']['table'],16)==target else 'certificate_wrong']+=1
        records.append(dict(task=t,stratum=kind,target=target,trace=trace))
    tests=mutations();passed=all(tests.values()) and all(summary[str(b)]['FINITE_TABLE_CERTIFIED']==0 for b in (16,32)) and summary['64']['certificate_exact']==48 and summary['64']['certificate_wrong']==0
    result=dict(passed=passed,library5=len(small),library7=len(large),summary=summary,mutation_tests=tests,records=records)
    Path(out).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':
    import sys
    main(sys.argv[1])
