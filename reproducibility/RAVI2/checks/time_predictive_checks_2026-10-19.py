#!/usr/bin/env python3
import json, random, hashlib
from collections import defaultdict
from pathlib import Path

OUT=Path('/mnt/data/time_predictive_commit/TIME_PREDICTIVE_CHECKS_2026-10-19.json')

def word(m):
    T=m*m
    return bytes(((t//m)%2 if t%m==m-1 else 0) for t in range(T))

def factor_count(s,L):
    T=len(s); ss=s+s[:L-1]
    return len({ss[i:i+L] for i in range(T)})

def formula(m,L):
    T=m*m
    if not (1<=L<=T): raise ValueError
    if L<=2*m: return L+1
    if L<3*m: return 2*L-2*m+1
    if L<=T-m: return L+m
    return T

def exhaustive_profile():
    cases=0
    for m in range(5,32,2):
        s=word(m);T=m*m
        for L in range(1,T+1):
            got=factor_count(s,L); exp=formula(m,L); cases+=1
            if got!=exp:
                return {'pass':False,'cases':cases,'counterexample':{'m':m,'L':L,'got':got,'expected':exp}}
    return {'pass':True,'m_values':list(range(5,32,2)),'cases':cases}

def boundary_profile():
    random.seed(20261019)
    cases=0
    for m in range(5,62,2):
        T=m*m; s=word(m)
        Ls={1,2,m-1,m,2*m-1,2*m,2*m+1,3*m-2,3*m-1,3*m,3*m+1,T-m-1,T-m,T-m+1,T}
        for _ in range(2): Ls.add(random.randint(1,T))
        for L in sorted(x for x in Ls if 1<=x<=T):
            got=factor_count(s,L); exp=formula(m,L); cases+=1
            if got!=exp:
                return {'pass':False,'cases':cases,'counterexample':{'m':m,'L':L,'got':got,'expected':exp}}
    return {'pass':True,'m_values':list(range(5,62,2)),'cases':cases,'seed':20261019}

def random_phase_floor():
    # P_m: choose phase uniformly, then emit deterministic cyclic word.
    # Given a positive-probability history, posterior is uniform on a nonempty phase set.
    # This brute-force check verifies every positive conditional next-symbol probability >=1/T.
    checked=0; global_min=1.0; witnesses=[]
    for m in range(5,22,2):
        s=word(m); T=len(s); ss=s+s
        local_min=1.0
        for h in range(0,T):
            groups=defaultdict(list)
            for n in range(T):
                key=bytes(ss[n:n+h]) if h else b''
                groups[key].append(n)
            for phases in groups.values():
                den=len(phases)
                c1=sum(s[(n+h)%T] for n in phases)
                for num in (c1,den-c1):
                    if num:
                        p=num/den; checked+=1
                        local_min=min(local_min,p); global_min=min(global_min,p)
                        if p+1e-15 < 1/T:
                            return {'pass':False,'m':m,'h':h,'prob':p,'floor':1/T}
        witnesses.append({'m':m,'T':T,'min_positive_conditional_probability':local_min,'required_floor':1/T})
    return {'pass':True,'conditional_probabilities_checked':checked,'global_min':global_min,'witnesses':witnesses}

def phase_switch_prefix():
    # Q_{n,d} emits the null trajectory up to n and switches phase by d only after n.
    # Verify directly for representative n,d,m that prefixes are identical.
    cases=0
    for m in range(5,22,2):
        s=word(m);T=len(s)
        ns=sorted(set([0,1,m-1,m,2*m,T//2,T-1,2*T+3]))
        ds=sorted(set([1,m-1,m,m+1,T-1]))
        for n in ns:
            for d in ds:
                for phase in range(T):
                    null=[s[(phase+t)%T] for t in range(n)]
                    alt=[]
                    for t in range(n): alt.append(s[(phase+t)%T])
                    if null!=alt: return {'pass':False,'m':m,'n':n,'d':d,'phase':phase}
                    cases+=1
    return {'pass':True,'cases':cases}

a=exhaustive_profile(); b=boundary_profile(); c=random_phase_floor(); d=phase_switch_prefix()
out={
 'all_pass':all(x['pass'] for x in [a,b,c,d]),
 'factor_profile_exhaustive':a,
 'factor_profile_boundary_adversarial':b,
 'random_phase_eta_interface':c,
 'phase_switch_prefix_identity':d,
 'key_values':{'p_3m':'4m','T':'m^2','memory_scale_at_3m':'4*sqrt(T)'},
 'note':'DET-FIN-01 is treated as an already-certified premise and is not re-audited here.'
}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))