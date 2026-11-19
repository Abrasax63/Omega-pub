"""Manual arithmetic AST checker over a fixed finite domain, never a theorem prover."""
DOMAIN=[-16,16]

def check(obligation):
    budget=[0]
    def validate(x,kind,depth=0):
        budget[0]+=1
        if budget[0]>64 or depth>12:raise ValueError('AST budget')
        if kind=='int':
            if x=='n' or type(x) is int and abs(x)<=1000000:return
            if not isinstance(x,list) or not x:raise ValueError('integer expression')
            if x[0]=='square' and len(x)==2:validate(x[1],'int',depth+1);return
            if x[0]=='mod' and len(x)==3 and type(x[2]) is int and 0<x[2]<=1000000:
                validate(x[1],'int',depth+1);return
        elif isinstance(x,list) and x:
            if x[0] in ('le','eq') and len(x)==3:
                validate(x[1],'int',depth+1);validate(x[2],'int',depth+1);return
            if x[0]=='and' and 3<=len(x)<=8:
                for child in x[1:]:validate(child,'bool',depth+1)
                return
        raise ValueError('unsupported AST')
    def ev(x,n):
        if x=='n':return n
        if type(x) is int:return x
        op=x[0]
        if op=='square':return ev(x[1],n)**2
        if op=='mod':return ev(x[1],n)%x[2]
        if op=='eq':return ev(x[1],n)==ev(x[2],n)
        if op=='le':return ev(x[1],n)<=ev(x[2],n)
        return all(ev(child,n) for child in x[1:])
    try:
        if not isinstance(obligation,dict) or set(obligation)!={'domain','if','then'} or obligation['domain']!=DOMAIN:
            raise ValueError('fixed integer domain required')
        validate(obligation['if'],'bool');validate(obligation['then'],'bool')
    except (ValueError,TypeError,RecursionError):
        return dict(status='ABSTAIN',reason='UNSUPPORTED_OR_INVALID_CONTRACT',universal_proof=False)
    tested=0
    for n in range(-16,17):
        tested+=1
        if ev(obligation['if'],n) and not ev(obligation['then'],n):
            return dict(status='COUNTEREXAMPLE',witness=n,tested=tested,universal_proof=False)
    return dict(status='NO_COUNTEREXAMPLE_WITHIN_DOMAIN',tested=tested,domain=DOMAIN.copy(),universal_proof=False)
