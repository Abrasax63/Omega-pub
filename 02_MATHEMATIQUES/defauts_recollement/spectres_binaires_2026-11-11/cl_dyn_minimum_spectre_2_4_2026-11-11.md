# CL-DYN — Le spectre {2,4} exige neuf états

11 novembre 2026. **DÉMONTRÉ avec contrôle fini exact**, pour des endofonctions finies observées avec exactement deux couleurs.

La [borne arithmétique](cl_dyn_spectres_mixtes_borne_arithmetique_2026-11-11.md) donne N≥8. À huit états, elle impose un 3-cycle bicolore et une chaîne entrante de profondeur 5. Le test exact des colorations de ce graphe exclut D={2,4}. Le script ci-dessous reproduit ce contrôle et vérifie le témoin à neuf états.

Sur les états 0 à 8, prendre T=(1,2,3,4,5,3,8,1,0) et π=(0,0,0,0,0,1,1,1,0). Les seuls défauts sont Δ₂=Δ₄={(1,1)}. Les couples (Q^h,T^h) aux horizons 5 et 8 sont identiques, et Δ₅=Δ₆=Δ₇=∅. La vérification couvre donc tous les horizons.

Pour la recherche du témoin, on peut imposer une chaîne 0→1→2→3→4→5 après renommage : toute réalisation de ce spectre a une profondeur transitoire d'au moins cinq. Le témoin obtenu a une branche supplémentaire et un cycle de longueur 3. La minoration et ce témoin établissent N_min=9.

```python
from itertools import product

def defects(T, pi):
    Q = frozenset((pi[x], pi[y]) for x, y in enumerate(T))
    macro, micro = Q, T
    seen, gaps = {}, []
    while (macro, micro) not in seen:
        seen[macro, micro] = len(gaps)
        E = {(pi[x], pi[y]) for x, y in enumerate(micro)}
        gaps.append(macro - E)
        macro = frozenset((a, d) for a, b in macro for c, d in Q if b == c)
        micro = tuple(T[y] for y in micro)
    if any(gaps[seen[macro, micro]:]):
        return None
    return {h: gap for h, gap in enumerate(gaps, 1) if gap}

target = {2, 4}
T8 = (1, 2, 0, 0, 3, 4, 5, 6)
for tail in product((0, 1), repeat=7):
    pi = (0,) + tail
    if not any(pi):
        continue
    d = defects(T8, pi)
    assert d is None or set(d) != target

T9 = (1, 2, 3, 4, 5, 3, 8, 1, 0)
pi9 = (0, 0, 0, 0, 0, 1, 1, 1, 0)
assert defects(T9, pi9) == {2: {(1, 1)}, 4: {(1, 1)}}
print("127 colorations non constantes exclues à huit états ; témoin vérifié à neuf états")
```
