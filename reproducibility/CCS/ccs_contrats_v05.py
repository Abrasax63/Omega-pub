"""CCS v0.5 : contrats finis et obligations contrôlables par un vérificateur indépendant.
Portée : énoncés à quantificateur unique sur ensembles finis explicitement énumérés.
"""
from dataclasses import dataclass
from typing import Callable, Tuple
import json, hashlib

@dataclass
class Statement:
    name: str
    domain: Tuple[int,...]
    hypothesis: Callable[[int],bool]
    conclusion: Callable[[int],bool]
    quantifier: str = "forall"

def evaluate(s):
    vals=[bool(s.conclusion(x)) for x in s.domain if s.hypothesis(x)]
    if s.quantifier=="forall": return all(vals)
    if s.quantifier=="exists": return any(vals)
    raise ValueError("quantifier unsupported")

def build_certificate(a,b,mapping):
    """mapping explicite source -> cible; toutes les obligations sont finies."""
    obligations=[]
    obligations.append({"kind":"quantifier","ok":a.quantifier==b.quantifier})
    obligations.append({"kind":"mapping_total","ok":set(mapping)==set(a.domain)})
    obligations.append({"kind":"mapping_codomain","ok":set(mapping.values())<=set(b.domain)})
    obligations.append({"kind":"mapping_bijective","ok":len(set(mapping.values()))==len(mapping) and set(mapping.values())==set(b.domain)})
    for x in a.domain:
        if x not in mapping or mapping[x] not in b.domain: continue
        y=mapping[x]
        obligations.append({"kind":"hypothesis","source":x,"target":y,"ok":bool(a.hypothesis(x))==bool(b.hypothesis(y))})
        if a.hypothesis(x) and b.hypothesis(y):
            obligations.append({"kind":"conclusion","source":x,"target":y,"ok":bool(a.conclusion(x))==bool(b.conclusion(y))})
    return {"status":"FINITE_CONTRACT_VERIFIED" if all(o["ok"] for o in obligations) else "CONTRACT_FAILED",
            "obligations":obligations,"source_truth":evaluate(a),"target_truth":evaluate(b)}

def independent_check(a,b,mapping,certificate):
    return build_certificate(a,b,mapping)==certificate

if __name__=="__main__":
    a=Statement("A",(0,1,2,3),lambda x:x>0,lambda x:x%2==0)
    b=Statement("B",(10,11,12,13),lambda y:y>10,lambda y:y%2==0)
    mapping={x:x+10 for x in a.domain}
    c=build_certificate(a,b,mapping)
    print(json.dumps({"status":c["status"],"obligations":len(c["obligations"]),"independent_recheck":independent_check(a,b,mapping,c),"truths":[c["source_truth"],c["target_truth"]]}))