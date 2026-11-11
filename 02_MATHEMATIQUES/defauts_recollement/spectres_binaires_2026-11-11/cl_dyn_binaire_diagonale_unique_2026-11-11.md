# CL-DYN — Un seul retour diagonal peut manquer en binaire

11 novembre 2026. **DÉMONTRÉ**. Soit T une endofonction finie observée par π à valeurs dans deux couleurs, toutes deux utilisées. Posons Q=E₁, E_h={(π(x),π(T^h x))}, Δ_h=Q^h\E_h et D={h≥1:Δ_h≠∅}. Si D est fini et non vide, il existe une couleur a telle que Δ_h={(a,a)} pour tout h∈D. La couleur est unique et indépendante de h.

## Preuve

### 1. Une paire hors diagonale manquante rend le spectre infini

Si (a,b)∈Δ_h avec a≠b, alors T^h envoie toute la fibre a dans elle-même, puisqu'il n'y a que deux couleurs. Ainsi (a,b)∉E_{kh} pour tout k≥1.

En revanche, la relation R=Q^h contient a→b et a une sortie de chaque couleur. Si b→b appartient à R, le chemin a→b puis les boucles en b donnent (a,b)∈R^k pour tout k≥1. Sinon R contient b→a, et l'alternance a→b→a donne (a,b)∈R^k pour tout k impair. Dans les deux cas, D est infini, puisque R^k=Q^{kh}. Donc, si D est fini, seuls des retours diagonaux peuvent manquer.

### 2. Les deux diagonales ne peuvent manquer, même à des horizons différents

Supposons (a,a)∈Δ_h et (b,b)∈Δ_j avec a≠b. Alors T^h envoie la fibre a dans la fibre b et T^j envoie la fibre b dans la fibre a. Par commutation des puissances de T, T^{h+j} conserve les deux fibres : sur a, appliquer d'abord T^h, et sur b, d'abord T^j. Toute puissance positive de T^{h+j} conserve donc les couleurs.

Lorsque D est non vide, Q a au moins une boucle et une arête hors diagonale. Sans boucle, la couleur alterne à chaque pas, ce qui donne E_k=Q^k à tous les horizons. Sans arête hors diagonale, la couleur est constante le long de chaque trajectoire, avec la même conséquence. En binaire, toute boucle est à l'une des extrémités d'une arête hors diagonale. Répéter la boucle avant ou après cette arête donne un chemin hors diagonale à toute longueur positive.

Il y a donc un défaut hors diagonale à chaque multiple positif de h+j, car T^{h+j} conserve les couleurs. Cela contredit la finitude de D. Il ne reste qu'une diagonale possible pour l'ensemble des horizons défectueux. Comme chacun d'eux a un défaut non vide, ce défaut est exactement le singleton annoncé.

## Vérification et portée

Contrôle exhaustif des couples binaires modulo isomorphisme, toutes les tailles de 2 à 7. Pour chaque couple, les ensembles de microétats et de blocs accessibles ont été suivis jusqu'au premier retour, indépendamment pour chaque bloc. Pour chaque spectre fini non vide, l'union des défauts a été calculée directement à partir de T^h et Q^h. Aucune divergence.

| États | Classes binaires examinées | Spectres finis non vides, en classes |
|---:|---:|---:|
| 2 | 3 | 0 |
| 3 | 15 | 0 |
| 4 | 95 | 0 |
| 5 | 491 | 0 |
| 6 | 2 670 | 3 |
| 7 | 14 092 | 41 |

Le résultat général repose sur la preuve. Il implique le cas D={3} et le renforce en autorisant plusieurs horizons défectueux, avec un seul retour diagonal commun. Le [contrôle précédent à sept états](cl_dyn_spectre_3_n6_n7_2026-11-11.md) donne un défaut hors diagonale avec cinq blocs. La preuve ci-dessus utilise deux couleurs à chaque étape. Elle ne classe pas les ensembles d'horizons D réalisables. Aucune priorité bibliographique revendiquée. Aucun changement GitHub ou SQLite.
