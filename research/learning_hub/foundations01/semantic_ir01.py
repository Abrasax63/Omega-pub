"""SEMANTIC-IR01: bounded French parser; separate typed guard from proposal."""
import re
import unicodedata
from toolroute01 import dispatch

def norm(s):
    if not isinstance(s,str):raise ValueError("TEXT")
    return " ".join(re.sub(r"[^a-z0-9]+"," ",unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()).split())

# Deliberately conservative lexical evidence, not a semantic model.
PAT={
 "projection":r"\b(projet\w*|orthogon\w*|noyau|contraint\w*|euclid\w*|produit scalaire|ajust\w*|corrig\w*|correct\w*|repar\w*|retir\w*|oter|enlev\w*|soustra\w*|annul\w*)\b",
 "closure":r"\b(fermeture|determin\w*|collision|indiscern\w*|observation\w*|mesure\w*|trace\w*)\b",
 "inverse":r"\b(primitive|integr\w*|invers\w*|antecedent|reconstru\w*|retrouv\w*|restitu\w*|dedui\w*|potentiel|niveaux)\b",
 "linear":r"\b(vecteur|coordonne\w*|matrice|lignes?|noyau|contraint\w*|scalaire|euclid\w*|norme|lineair\w*)\b",
 "cyclic":r"\b(cycl\w*|period\w*|circul\w*|boucle|anneau|cercle)\b",
 "difference":r"\b(increment\w*|difference\w*|ecart\w*|variation\w*|primitive|potentiel|signal|moyenne)\b",
 "future":r"\b(futur\w*|successeur\w*|transition\w*|evolution\w*|sortie\w*|lendemain|suite)\b",
 "zero":r"\b(somme nulle|somme zero|moyenne nulle|moyenne zero|moyenne|centr\w*|compatib\w*|integrable)\b",
 "bad":r"\b(analytique|continue?s?|droite reelle|sinus|sin x|laplace|geograph\w*|sphere|meteo|temperature|turbulence|navier|universel\w*|valeurs? propres?|complexes?|photograph\w*|determinant|infini\w*|sans donnees|sans les etats|sans observations?|sans mesures?|sans traces?|sans les futurs|sans transitions?|donnees manquantes)\b",
 "order":r"\b(puis|ensuite|avant de|avant d|apres avoir|d abord|enchain\w*)\b",
}
def has(k,s):return bool(re.search(PAT[k],s))
def abstain(reason):
    return dict(domain="unknown",goals=[],forbidden=[],steps=[],reason=reason)
def propose(text):
    s=norm(text)
    if not s:return abstain("EMPTY")
    if has("bad",s):return abstain("OUT_OF_SCOPE")
    # Extract narrow, explicit prohibitions. A clause begins with sans/ne pas.
    # Only the first clause up to a positive delimiter is suppressed.
    forbidden=set()
    def suppress(m):
        frag=m.group(0)
        for k in ("projection","closure","inverse"):
            if has(k,frag):forbidden.add(k)
        return " "
    # "ne pas se limiter" is not a prohibition of the named operation.
    s=re.sub(r"\bne pas se limiter a\b"," ",s)
    positive=re.sub(r"\b(?:sans|ne pas|interdit de|aucune)\b.*?(?=\b(?:seulement|uniquement|mais|puis|ensuite|effectuer|tenter|calculer|trouver|fournir|chercher|verifier)\b|$)",suppress,s)
    # Retain unsuppressed domain evidence only; no scope from negated clauses.
    p=has("projection",positive);c=has("closure",positive);i=has("inverse",positive)
    cyc=has("cyclic",positive) and has("difference",positive)
    linear=has("linear",positive);trace=c and has("future",positive)
    # Explicit order and cyclic repair evidence required for composition.
    if p and i and cyc and has("zero",positive) and has("order",positive) and not trace:
        # Reject clear inverse-before-correction wording, not all possible paraphrases.
        if re.search(r"\b(?:primitive|invers\w*|integr\w*)\b.*\b(?:puis|ensuite|avant de)\b.*\b(?:corrig\w*|repar\w*|projet\w*)\b",positive):
            return abstain("REVERSED_ORDER")
        domain="cyclic_zero_sum";steps=["projection","inverse"]
    elif trace and not p and not i:
        domain="observed_transitions";steps=["closure"]
    elif p and linear and not i and not trace:
        domain="finite_linear";steps=["projection"]
    elif i and cyc and not p and not trace:
        domain="finite_cycle";steps=["inverse"]
    else:return abstain("AMBIGUOUS_OR_INSUFFICIENT")
    if forbidden.intersection(steps):return abstain("FORBIDDEN")
    return dict(domain=domain,goals=steps.copy(),forbidden=sorted(forbidden),steps=steps,reason=None)

PLANS={
 "finite_linear":(["projection"],"projection"),
 "observed_transitions":(["closure"],"closure"),
 "finite_cycle":(["inverse"],"inverse"),
 "cyclic_zero_sum":(["projection","inverse"],"compose")
}
def guard(plan):
    if not isinstance(plan,dict) or set(plan)!={"domain","goals","forbidden","steps","reason"}:raise ValueError("SCHEMA")
    if any(not isinstance(plan[k],list) for k in ("goals","forbidden","steps")):raise ValueError("SCHEMA")
    allowed={"projection","closure","inverse"}
    if any(type(x) is not str or x not in allowed for k in ("goals","forbidden","steps") for x in plan[k]):raise ValueError("UNKNOWN_OPERATION")
    if plan["reason"] is not None:
        if plan["domain"]!="unknown" or plan["steps"] or plan["goals"]:raise ValueError("ABSTAIN_HAS_STEPS")
        return "unsupported"
    if plan["domain"] not in PLANS:raise ValueError("DOMAIN")
    steps,route=PLANS[plan["domain"]]
    if plan["steps"]!=steps or plan["goals"]!=steps:raise ValueError("ORDER_OR_GOAL")
    if set(steps)&set(plan["forbidden"]):raise ValueError("FORBIDDEN")
    return route
def solve(text,payload):
    ir=propose(text);route=guard(ir)
    return ir,route,dispatch(route,payload)
