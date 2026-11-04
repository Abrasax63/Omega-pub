"""CCS v0.4 — noyau logique fini, sans dépendance externe.
Certifie uniquement des comparaisons exhaustives sur univers fini.
"""
from dataclasses import dataclass
from typing import Callable, Tuple

@dataclass(frozen=True)
class Enonce:
    nom: str
    domaine: Tuple[int, ...]
    hypothese: Callable[[int], bool]
    conclusion: Callable[[int], bool]
    quantificateur: str = "forall"

def verifier(e: Enonce) -> bool:
    valeurs = [e.conclusion(x) for x in e.domaine if e.hypothese(x)]
    if e.quantificateur == "forall":
        return all(valeurs)
    if e.quantificateur == "exists":
        return any(valeurs)
    raise ValueError("Quantificateur non pris en charge")

def comparer(a: Enonce, b: Enonce) -> dict:
    if a.domaine != b.domaine:
        return {"verdict":"INDETERMINE", "motif":"domaines distincts : pas de bijection certifiée"}
    if a.quantificateur != b.quantificateur:
        return {"verdict":"INDETERMINE", "motif":"quantificateurs distincts : vérifier le sens global"}
    ecarts = []
    for x in a.domaine:
        va=(bool(a.hypothese(x)), bool(a.conclusion(x)))
        vb=(bool(b.hypothese(x)), bool(b.conclusion(x)))
        if va != vb:
            ecarts.append({"x":x, "reference":va, "traduction":vb})
    return {
        "verdict": "EQUIVALENCE_EXTENSIONNELLE_FINIE" if not ecarts else "NON_EQUIVALENCE_EXTENSIONNELLE",
        "nombre":len(a.domaine), "ecarts":len(ecarts),
        "taux":len(ecarts)/len(a.domaine) if a.domaine else None,
        "temoins":ecarts,
        "verite_reference":verifier(a), "verite_traduction":verifier(b)
    }

if __name__ == "__main__":
    u=tuple(range(100))
    a=Enonce("reference",u,lambda x:True,lambda x:x%2==0)
    b=Enonce("traduction",u,lambda x:True,lambda x:x%2==0 and x<90)
    import json
    print(json.dumps(comparer(a,b),indent=2))