# CL-DYN — Test exact d’égalité à la borne arithmétique

11 novembre 2026. Cadre binaire, spectre fini non vide D. Poser H=max D, p(h) le plus petit entier ≥2 ne divisant pas h, et P=max_{h∈D} p(h). La [minoration précédente](cl_dyn_minimum_spectres_singletons_2026-11-11.md) donne N≥H+1+P.

## Réduction démontrée

Toute réalisation à N=H+1+P est un unique P-cycle bicolore et une chaîne de H+1 sommets qui y entre. En effet, la borne de profondeur impose au moins H+1 sommets transitoires et l'argument de divisibilité au moins P sommets périodiques. À égalité, la chaîne de profondeur maximale épuise les transitoires. Choisir h*∈D tel que p(h*)=P. Tout cycle de longueur strictement inférieure à P est fixé par T^h*, car sa longueur divise h*. Si le graphe ne contenait que ces cycles, les deux couleurs présentes parmi les sommets périodiques y réaliseraient les deux diagonales à h*. Le défaut à h* est diagonal et l'une d'elles manque, contradiction. Il faut donc un P-cycle, qui épuise les sommets périodiques.

**Conséquence.** Si un h de D est divisible par P, la borne ne peut pas être atteinte. Il faut alors N≥H+2+P. L'absence de multiple de P dans D ne suffit pas à atteindre la borne : {2,4}, avec P=3, échoue au test exact à huit états.

## Critère fini exact à la borne

Renommer la couleur du retour manquant en 1. Sur le graphe imposé ci-dessus, le dernier sommet de la chaîne doit être de couleur 1 et celui de profondeur 1 de couleur 0. À H, tous les états sauf le dernier sont déjà sur le cycle. Pour ces départs, leurs images à H et H+P sont identiques. Or 1→1 manque à H et est réalisé à H+P. Le dernier sommet doit donc fournir ce retour et sa destination à H doit être 0.

Énumérer les colorations restantes du cycle et de la chaîne. Vérifier que Q² est complète et que les relations E_h diffèrent de la relation complète exactement aux horizons de D pour 2≤h≤H. Enfin, vérifier E_h complète sur la période terminale H+1,…,H+P. Ces conditions sont nécessaires et suffisantes, puisque T^h est périodique à partir de H+1 et que Q^h est complète dès h=2 dans le régime considéré.

## Contrôle exact jusqu’à H=12

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Spectres non singletons atteignant la borne | 0 | 0 | 0 | 4 | 2 | 9 | 7 | 9 | 16 | 46 | 33 |

Total 126 spectres. Exemples : {4,5} atteint 9 états, {6,10} atteint 15 états, et {2,12} atteint 18 états. Le code restitue les témoins via classify(H). Les cas P=2 concordent avec la formule pour les [spectres impairs](cl_dyn_taille_minimale_spectres_impairs_2026-11-11.md) et les cas P=3 avec l'[énumération antérieure au seuil H+4](cl_dyn_spectres_pairs_seuil_h_plus_4_2026-11-11.md), après filtrage au même périmètre. Le test décide l'atteinte de la borne, pas le minimum exact lorsqu'elle est stricte. Aucun changement GitHub ou SQLite.

```python
from collections import Counter

def least_nondivisor(h):
    return next(p for p in range(2, h + 2) if h % p)

def classify(H):
    L = H + 1
    found = {}
    full = {(0,0),(0,1),(1,0),(1,1)}
    for p in sorted({least_nondivisor(h) for h in range(2,H+1)}):
        if H % p == 0:
            continue
        T = tuple((x+1)%p for x in range(p)) + (0,) + tuple(range(p,p+L-1))
        power = tuple(range(len(T)))
        powers = []
        for _ in range(H+p):
            power = tuple(T[x] for x in power)
            powers.append(power)
        for cbits in range(1,(1<<p)-1):
            C = tuple(cbits>>i&1 for i in range(p))
            if any(C[i]==C[(i+H)%p]==1 for i in range(p)):
                continue
            for tbits in range(1<<(L-2)):
                pi = C+(0,)+tuple(tbits>>i&1 for i in range(L-2))+(1,)
                E = [{(pi[x],pi[y]) for x,y in enumerate(power)} for power in powers]
                if any(e != full for e in E[H:]):
                    continue
                Q = E[0]
                assert {(a,d) for a,b in Q for c,d in Q if b==c} == full
                D = tuple(h for h in range(2,H+1) if E[h-1]!=full)
                if len(D)<2 or D[-1]!=H or max(map(least_nondivisor,D))!=p:
                    continue
                assert all(full-E[h-1]=={(1,1)} for h in D)
                found.setdefault(D,(T,pi,p))
    return found

if __name__=='__main__':
    for H in range(2,13):
        f=classify(H)
        print(H,len(f),dict(Counter(r[2] for r in f.values())),[D for D in sorted(f) if len(D)==2][:15])

```
