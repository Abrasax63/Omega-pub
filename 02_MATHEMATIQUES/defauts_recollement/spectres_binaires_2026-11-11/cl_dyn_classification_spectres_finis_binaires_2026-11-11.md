# CL-DYN — Classification des spectres finis binaires

11 novembre 2026. **DÉMONTRÉ**. Pour une endofonction finie observée avec deux couleurs A et B, toutes deux utilisées, écrire Q=E₁, E_h={(π(x),π(T^h x))}, Δ_h=Q^h\E_h et D={h≥1:Δ_h≠∅}. Les spectres finis réalisables sont exactement les parties finies de {2,3,…}. De plus, pour D non vide et H=max D, une réalisation connexe avec Q complète et au plus 4H+1 états existe. Elle vérifie Δ_h={(A,A)} pour h∈D.

## Nécessité et cas vide

Q=E₁, donc 1 ne peut être défectueux. Deux points fixes, de couleurs différentes, réalisent le spectre vide.

## Construction pour D non vide

Poser p=H+1≥3. Prendre un p-cycle avec un seul sommet A, les p−1 autres étant B. Faire entrer dans le sommet A du cycle une chaîne de 2p−2 sommets B. Pour chaque r=1,…,p−1, ajouter une feuille A à distance d_r du sommet A du cycle, où d_r=r si r∉D et d_r=r+p si r∈D. La feuille pointe vers le sommet B à distance d_r−1 sur la chaîne, ou vers le sommet A du cycle si d_r=1. Toutes les feuilles partagent la chaîne. Le graphe est connexe et compte p+(2p−2)+(p−1)=4H+1 sommets.

### Couples effectivement réalisés

- A→A. Le cycle fournit tous les multiples positifs de p. La feuille r fournit exactement les temps d_r+mp avec m≥0, puisqu'elle traverse seulement des B avant d'arriver sur le A du cycle. Ce sont tous les départs de couleur A. Dans chaque classe de résidu non nul r, le seul temps éventuellement omis est r, et il est omis exactement si r∈D.
- B→A. La chaîne contient au moins p sommets B, dont les distances 1 à p représentent tous les résidus. Pour chaque h≥1, prendre la distance r∈{1,…,p} congrue à h modulo p. Alors r≤h et le trajet atteint A après r pas puis à chaque tour de cycle.
- B→B. Sur le cycle, au plus deux des p départs sont exclus : le sommet A et l'unique départ dont l'image à h pas est A. Comme p≥3, il en reste un.
- A→B. Le A du cycle convient si p ne divise pas h. Sinon prendre la feuille de résidu H=p−1. Sa distance vaut H+p puisque H∈D. À un multiple positif de p elle n'est jamais au A du cycle et se trouve sur un B.

Ainsi E₁ est complète, puisque 1∉D. Par conséquent Q^h est complète à tout horizon positif. Les seuls défauts sont exactement les retours A→A aux temps de D.

## Provenance et contrôle

L'existence générale dans le cas fini découle déjà du cas à queue constamment bonne de l'[audit du 10 novembre, §3](https://chatgpt.com/library?file_id=libfile_5c69c941975081919374668a63e5039e&account_id=personal). L'apport ici est la chaîne partagée, la connexité et la borne explicite linéaire. Cette borne est une majoration de construction, sans revendication d'optimalité. Le [théorème de la diagonale unique](cl_dyn_binaire_diagonale_unique_2026-11-11.md) établit de plus que, dans toute réalisation binaire de spectre fini non vide, la même diagonale manque à chacun des horizons de D.

Le code ci-dessous a vérifié les 512 parties de {2,…,10}, cas vide inclus, en itérant le couple exact (Q^h,T^h) jusqu'à répétition. Il vérifie aussi chaque paire manquante. Maximum atteint dans ce contrôle : 41 états. Aucun changement GitHub ni SQLite.

```python
from itertools import combinations

def construct(D):
    if not D:
        return (0, 1), (0, 1)
    H = max(D)
    p = H + 1
    T = [(x + 1) % p for x in range(p)]
    color = [0] + [1] * (p - 1)
    for depth in range(1, 2 * p - 1):
        T.append(0 if depth == 1 else p + depth - 2)
        color.append(1)
    for r in range(1, p):
        depth = r + p * (r in D)
        T.append(0 if depth == 1 else p + depth - 2)
        color.append(0)
    return tuple(T), tuple(color)

def exact_defects(T, color):
    Q = frozenset((color[x], color[y]) for x,y in enumerate(T))
    power, orbit = Q, T
    seen, defects = {}, []
    while (power, orbit) not in seen:
        seen[power, orbit] = len(defects)
        E = {(color[x],color[y]) for x,y in enumerate(orbit)}
        defects.append(power - E)
        power = frozenset((a,d) for a,b in power for c,d in Q if b==c)
        orbit = tuple(T[x] for x in orbit)
    assert not any(defects[seen[power,orbit]:])
    return {h: gap for h,gap in enumerate(defects,1) if gap}

def main():
    total = max_states = 0
    for size in range(10):
        for choices in combinations(range(2,11),size):
            D = set(choices)
            T, color = construct(D)
            assert exact_defects(T,color) == {h: {(0,0)} for h in D}
            if D:
                assert len(T) == 4*max(D)+1
                assert {(color[x],color[y]) for x,y in enumerate(T)} == {(0,0),(0,1),(1,0),(1,1)}
            total += 1
            max_states = max(max_states,len(T))
    print(total,max_states)

if __name__ == '__main__':
    main()

```
