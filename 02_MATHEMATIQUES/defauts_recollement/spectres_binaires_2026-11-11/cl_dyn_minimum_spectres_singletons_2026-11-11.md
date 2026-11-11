# CL-DYN — Nombre minimal d’états pour le spectre singleton {H}

11 novembre 2026. **DÉMONTRÉ**, pour toute endofonction finie observée en deux couleurs. Soit H≥2 et p(H) le plus petit entier ≥2 qui ne divise pas H. Le nombre minimal d’états pour obtenir D={H} vaut H+1+p(H). L’optimum est atteint par un système connexe.

## Minoration

Dans toute réalisation d’un spectre fini non vide, la profondeur transitoire est au moins H+1, Q^h est complète pour h≥2 et les deux couleurs apparaissent sur les cycles, d’après la [borne précédente](cl_dyn_taille_minimale_spectres_impairs_2026-11-11.md). Le [théorème de la diagonale unique](cl_dyn_binaire_diagonale_unique_2026-11-11.md) impose que le défaut en H soit diagonal.

Avec moins de p(H) états périodiques, tous les cycles auraient une longueur qui divise H. Ainsi T^H fixerait chaque état périodique et réaliserait les deux diagonales, contradiction. Il faut donc au moins p(H) états périodiques en plus des H+1 états transitoires. Le même raisonnement donne, pour tout spectre fini non vide D, la borne N≥max(D)+1+max{p(h):h∈D}.

## Construction optimale

Écrire p=p(H), L=H+1. Prendre un p-cycle avec un seul état de couleur 1, situé à p−1 pas de l'entrée de la chaîne sur le cycle. Attacher une chaîne de profondeur L. Son sommet de profondeur 1 est de couleur 0, le sommet de profondeur L de couleur 1. Pour 2≤d<L, donner la couleur 1 à la profondeur d exactement quand d n'est pas congru à L modulo p. Puisque p≤H+1, L≥p.

Les transitions sur le cycle fournissent les deux passages entre couleurs et, si p≥3, une boucle 0→0. Si p=2, la profondeur 1 donne cette boucle en entrant au sommet 0. Ainsi Q² est complète et toutes les puissances suivantes le sont.

- Pour h non multiple de p, les deux passages entre couleurs sont réalisés sur le cycle. Pour un multiple positif de p, le sommet de profondeur 1 atteint la couleur 1, tandis que la feuille de profondeur L aboutit à la couleur 0. Avant l'entrée de la feuille, cela suit de la règle sur les profondeurs congrues à L. Après son entrée, elle revient à la couleur 1 seulement aux horizons congrus à H modulo p.
- Le retour 0→0 est fourni par le cycle si p≥3, car sur un p-cycle un seul départ est de couleur 1 et un seul départ aboutit en 1. Pour p=2, le cycle suffit aux horizons pairs et le sommet de profondeur 1 aux horizons impairs.
- Pour le retour 1→1, le cycle donne tous les multiples de p. Si 2≤h<H et p ne divise pas h, la feuille aboutit à la profondeur L−h≥2, de couleur 1. À h=H, la feuille aboutit à la profondeur 1, de couleur 0. Tout autre départ de couleur 1 est déjà sur le cycle à cet horizon. Une profondeur de départ d≤H ne pourrait aboutir en 1 que si d était congrue à L, classe interdite aux sommets de couleur 1 avant la feuille. Donc 1→1 manque à H.
- Pour L≤h≤L+p−1 non multiple de p, prendre le départ de profondeur d=h−p+1. On a 1≤d≤L. Le cas d=1 implique h=p et est exclu. Si d=L, le départ est la feuille. Sinon d ne peut être congrue à L, car dans cette fenêtre l'unique h congru à H est le dernier, h=L+p−1. Le départ est donc de couleur 1 et atteint le sommet cyclique de couleur 1. Après cette fenêtre, la périodicité de T^h à partir de L propage la complétude.

L'horizon 1 est exact par définition. Le système a donc exactement D={H} avec H+1+p états.

## Contrôle

Le script a vérifié directement les défauts pour H=2,…,300 et la période terminale complète. Exemples : H=2 donne 6 états, H=4 donne 8, H=6 donne 11, H=12 donne 18 et H=60 donne 68. La formule généralise les cas impairs et tranche le seuil H+4 pour les singletons pairs. Le minimum des spectres mixtes reste ouvert en général. Aucun changement GitHub ou SQLite.

```python
def build(H):
    p = next(p for p in range(2, H + 2) if H % p)
    L = H + 1
    T = tuple((x + 1) % p for x in range(p)) + (0,) + tuple(range(p, p + L - 1))
    colors = (0,) * (p - 1) + (1,) + tuple(
        int(d == L or (2 <= d < L and d % p != L % p))
        for d in range(1, L + 1)
    )
    return T, colors, p

def validate(H):
    T, colors, p = build(H)
    assert len(T) == H + 1 + p == len(colors)
    Q = {(colors[x], colors[y]) for x, y in enumerate(T)}
    R, M = Q, T
    for h in range(1, H + 1 + p):
        E = {(colors[x], colors[y]) for x, y in enumerate(M)}
        assert R - E == ({(1,1)} if h == H else set()), (H,p,h,R-E)
        R = {(a,d) for a,b in R for c,d in Q if b==c}
        M = tuple(T[x] for x in M)

if __name__ == '__main__':
    for H in range(2, 301):
        validate(H)
    for H in (2,3,4,6,12,60,120):
        T, colors, p = build(H)
        print(H,p,len(T))

```
