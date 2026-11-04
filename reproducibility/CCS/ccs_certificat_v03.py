"""CCS v0.3 : profil d'écarts, exact ou estimé, avec provenance explicite."""
import json, random, math
from collections import Counter

def compare(reference, traduction, univers, mode="exhaustif", taille=1000, seed=42):
    """Chaque fonction retourne (admissible: bool, conclusion: bool)."""
    population=list(univers)
    if not population: raise ValueError("Univers vide")
    if mode=="exhaustif":
        echantillon=population
    elif mode=="sondage":
        if taille<1: raise ValueError("Taille invalide")
        rng=random.Random(seed)
        echantillon=[rng.choice(population) for _ in range(taille)]
    else: raise ValueError("Mode inconnu")
    categories=Counter()
    temoins={}
    for x in echantillon:
        a,v=reference(x); b,w=traduction(x)
        categorie=None
        if a!=b: categorie="domaine_ou_hypothese"
        elif a and v!=w: categorie="conclusion"
        if categorie:
            categories[categorie]+=1
            temoins.setdefault(categorie,{"entree":x,"reference":[a,v],"traduction":[b,w]})
    n=len(echantillon)
    erreurs=sum(categories.values())
    p=erreurs/n
    # Intervalle Wilson 95 %, indicatif, uniquement pour tirages iid avec remise.
    z=1.959963984540054
    d=1+z*z/n
    centre=(p+z*z/(2*n))/d
    demi=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return {
      "mode":mode,"univers_taille":len(population),"evaluations":n,
      "ecarts":erreurs,"taux_ecart":p,"categories":dict(categories),
      "temoins":temoins,
      "intervalle_wilson_95":([max(0,centre-demi),min(1,centre+demi)] if mode=="sondage" else None),
      "verdict":("NON_EQUIVALENT_TEMOIN" if erreurs else
                 "EQUIVALENT_SUR_UNIVERS_FINI" if mode=="exhaustif" else "INDETERMINE"),
      "portee":"Équivalence des paires (admissibilité, conclusion) sur l'univers indiqué ; non une équivalence PDF-Lean.",
      "hypotheses_statistiques":"Tirages uniformes indépendants avec remise ; intervalle approximatif Wilson." if mode=="sondage" else None
    }

def experience():
    U=list(range(100))
    reference=lambda x:(True, x%2==0)
    traduction=lambda x:(x>=10, x%2==0 if x<90 else False)
    exact=compare(reference,traduction,U)
    estime=compare(reference,traduction,U,mode="sondage",taille=1000,seed=42)
    return {"exact":exact,"estime":estime}

if __name__=="__main__":
    print(json.dumps(experience(),indent=2,ensure_ascii=False))