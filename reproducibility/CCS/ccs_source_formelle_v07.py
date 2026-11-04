"""CCS v0.7 : expressions arithmétiques finies, évaluées par vérificateur autonome.
Les tables du certificat ne sont jamais considérées comme des axiomes.
"""
import json,sys
def ev(e,x):
    if type(e) is bool:return e
    if type(e) is int:return e
    if e=="x":return x
    if not isinstance(e,list):raise ValueError("AST")
    op,*a=e
    if op=="mod" and len(a)==2:return ev(a[0],x)%ev(a[1],x)
    if op=="add" and len(a)==2:return ev(a[0],x)+ev(a[1],x)
    if op=="gt" and len(a)==2:return ev(a[0],x)>ev(a[1],x)
    if op=="eq" and len(a)==2:return ev(a[0],x)==ev(a[1],x)
    if op=="and" and len(a)==2:return bool(ev(a[0],x)) and bool(ev(a[1],x))
    if op=="not" and len(a)==1:return not bool(ev(a[0],x))
    raise ValueError("unsupported")
def verify(c):
    try:
        a,b=c["source"],c["target"]
        if a["quantifier"]!=b["quantifier"] or a["quantifier"] not in ("forall","exists"):return False
        da,db=a["domain"],b["domain"];pairs=c["pairs"]
        if not all(type(v)==int for v in da+db):return False
        if len(set(da))!=len(da) or len(set(db))!=len(db):return False
        if len(pairs)!=len(da) or set(map(tuple,pairs))!=set(map(tuple,pairs)):return False
        if set(x for x,y in pairs)!=set(da) or set(y for x,y in pairs)!=set(db):return False
        if len(set(y for x,y in pairs))!=len(db):return False
        for x,y in pairs:
            h1,h2=ev(a["hypothesis"],x),ev(b["hypothesis"],y)
            if type(h1)!=bool or type(h2)!=bool or h1!=h2:return False
            if h1:
                v1,v2=ev(a["conclusion"],x),ev(b["conclusion"],y)
                if type(v1)!=bool or type(v2)!=bool or v1!=v2:return False
        return True
    except (KeyError,ValueError,TypeError,ZeroDivisionError,IndexError):return False
if __name__=="__main__":
    c=json.load(open(sys.argv[1],encoding="utf8"))
    ok=verify(c)
    print("VERIFIE" if ok else "REJETE")
    sys.exit(0 if ok else 1)