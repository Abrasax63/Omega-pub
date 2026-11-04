"""CCS v0.2 : tests finis exhaustifs des domaines, hypotheses et quantificateurs."""
from itertools import product

def verifier(reference, traduction, univers):
    """Compare les prédicats d'admissibilité et les résultats sur l'univers explicite."""
    differences=[]
    for x in univers:
        ar,vr=reference(x)
        at,vt=traduction(x)
        if ar != at:
            differences.append({"x":x,"type":"DOMAINE_OU_HYPOTHESE","reference_admis":ar,"traduction_admis":at})
        elif ar and vr != vt:
            differences.append({"x":x,"type":"CONCLUSION","reference":vr,"traduction":vt})
    return {"statut":"NON_EQUIVALENT" if differences else "EQUIVALENT_SUR_UNIVERS_FINI",
            "temoin":differences[0] if differences else None,
            "nombre_ecarts":len(differences)}

def quantificateur(pred, domaine, q):
    valeurs=[pred(x) for x in domaine]
    if q=="forall": return all(valeurs)
    if q=="exists": return any(valeurs)
    raise ValueError(q)

def essais():
    U=list(range(-2,3))
    base=lambda x:(True,x*x>=0)
    domaine=lambda x:(x>=0,x*x>=0)
    hypothese=lambda x:(x!=0,x*x>=0)
    conclusion=lambda x:(True,x>0)
    tests={
      "controle_identique":verifier(base,base,U),
      "restriction_domaine":verifier(base,domaine,U),
      "hypothese_cachee":verifier(base,hypothese,U),
      "conclusion_modifiee":verifier(base,conclusion,U)
    }
    P=lambda x:x==0
    tests["forall_vers_exists"]={
      "statut":"NON_EQUIVALENT" if quantificateur(P,U,"forall")!=quantificateur(P,U,"exists") else "EQUIVALENT_SUR_UNIVERS_FINI",
      "reference_forall":quantificateur(P,U,"forall"),
      "traduction_exists":quantificateur(P,U,"exists"),
      "temoin_exists":next((x for x in U if P(x)),None),
      "contre_exemple_forall":next((x for x in U if not P(x)),None)}
    return tests

if __name__=="__main__":
    from pprint import pprint
    pprint(essais())