import json, hashlib, time
from pathlib import Path

OUT=Path('/mnt/data/single_gap_work/SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json')

def word(g,h,k):
    T=(k-1)*g+h
    a=['0']*T
    for i in range(k): a[i*g]='1'
    return ''.join(a)

def factors(s,L):
    T=len(s)
    ss=s+s[:max(0,L-1)]
    return {ss[i:i+L] for i in range(T)}

def p_exact(s,L): return len(factors(s,L))

def p_formula(g,h,k,L):
    return 1 + min(L,h-1) + min(max(L-g,0),(k-1)*g)

def right_specials(s,L):
    T=len(s)
    d={}
    for i in range(T):
        u=''.join(s[(i+j)%T] for j in range(L))
        d.setdefault(u,set()).add(s[(i+L)%T])
    return {u for u,e in d.items() if len(e)>1}

def periodic_boundary_factor(g,L):
    period='1'+'0'*(g-1)
    q=(L//g)+3
    z=period*q
    return z[-L:]

def experiment_formula():
    families=0; length_cases=0; failures=[]
    # Broad exhaustive box, including exceptional gaps much larger than regular gaps.
    for g in range(1,12):
        for h in range(g+1,8*g+8):
            for k in range(2,9):
                families+=1
                s=word(g,h,k); T=len(s)
                for L in range(1,T+1):
                    length_cases+=1
                    got=p_exact(s,L); exp=p_formula(g,h,k,L)
                    if got!=exp:
                        failures.append({'g':g,'h':h,'k':k,'T':T,'L':L,'got':got,'expected':exp})
                        if len(failures)>=20: return {'families':families,'length_cases':length_cases,'failures':failures,'pass':False}
    return {'families':families,'length_cases':length_cases,'failures':failures,'pass':not failures}

def experiment_right_specials():
    families=0; length_cases=0; failures=[]; rs_total=0
    for g in range(1,10):
        for h in range(g+1,6*g+7):
            for k in range(2,8):
                families+=1
                s=word(g,h,k); T=len(s)
                for L in range(1,T):
                    length_cases+=1
                    got=right_specials(s,L); rs_total+=len(got)
                    exp=set()
                    if L<=h-2: exp.add('0'*L)
                    if g<=L<=k*g-1: exp.add(periodic_boundary_factor(g,L))
                    if got!=exp:
                        failures.append({'g':g,'h':h,'k':k,'T':T,'L':L,'got':sorted(got),'expected':sorted(exp)})
                        if len(failures)>=20: return {'families':families,'length_cases':length_cases,'right_special_instances':rs_total,'failures':failures,'pass':False}
    return {'families':families,'length_cases':length_cases,'right_special_instances':rs_total,'failures':failures,'pass':not failures}

def specialization_check():
    failures=[]; cases=0
    for m in range(5,62,2):
        g=2*m; h=3*m; k=(m-1)//2; T=m*m
        assert (k-1)*g+h==T
        for L in [1,g,g+1,h-1,h,min(T-m,T),T-m+1,T]:
            if 1<=L<=T:
                cases+=1
                general=p_formula(g,h,k,L)
                if L<=2*m: old=L+1
                elif L<3*m: old=2*L-2*m+1
                elif L<=T-m: old=L+m
                else: old=T
                if general!=old: failures.append({'m':m,'L':L,'general':general,'old':old})
    return {'cases':cases,'failures':failures,'pass':not failures}

def main():
    t=time.time()
    e1=experiment_formula()
    e2=experiment_right_specials()
    spec=specialization_check()
    out={
      'theorem':'single-exceptional-gap cyclic binary factor complexity',
      'formula':'p(L)=1+min(L,h-1)+min(max(L-g,0),(k-1)g)',
      'domain':'integers k>=2, g>=1, h>g, 1<=L<=T=(k-1)g+h',
      'experiment_1_formula_exhaustive':e1,
      'experiment_2_right_special_classification':e2,
      'specialization_BR_TIME_FACTOR_COMPLEX_01':spec,
      'all_pass':bool(e1['pass'] and e2['pass'] and spec['pass']),
      'elapsed_seconds':round(time.time()-t,3),
      'guards':['two decisive experiments only','specialization check is algebraic regression, not a third research lock experiment']
    }
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()