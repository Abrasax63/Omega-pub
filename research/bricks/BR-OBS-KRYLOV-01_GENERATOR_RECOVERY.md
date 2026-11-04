# BR-OBS-KRYLOV-01 — Récupération du générateur d'un sous-espace de Krylov

**Type :** brique réutilisable / algèbre linéaire dynamique  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** CONNU_PRINCIPE_GENERAL / reformulation spécialisée

## Domaine
Soit `A:V→V` un endomorphisme d'un espace vectoriel sur un corps `K`. Pour `v∈V` et un entier `L≥1`, poser `K_L(v)=span(v,Av,…,A^(L-1)v)`.

## Théorème — récupération du générateur
Supposons `dim K_L(v)=L` et `A^L v ∉ K_L(v)`. Si `w` engendre le même sous-espace de Krylov à longueur `L`, c'est-à-dire `K_L(w)=K_L(v)`, alors `w=λv` pour un scalaire `λ≠0`. En particulier, sur `F_2`, on a nécessairement `w=v`.

## Preuve
Écrire `w = a_0 v + a_1 Av + … + a_(L-1) A^(L-1)v`. Comme `Aw∈K_L(w)=K_L(v)`, le coefficient de `A^L v` dans `Aw` doit être nul. L'hypothèse `A^L v∉K_L(v)` impose donc `a_(L-1)=0`. Puis `A²w∈K_L(v)` impose `a_(L-2)=0`, et ainsi de suite par récurrence. On obtient `w=a_0v`. Enfin `K_L(w)=K_L(v)` exclut `a_0=0`.

## Forme quotient
Le théorème s'applique sans changement à un endomorphisme induit sur un quotient `V/H`, dès que `H` est `A`-invariant. C'est cette forme qui est utilisée dans `OBS-V19-BAD-FIBER2`.

## Intérêt de réutilisation
La brique transforme une égalité de sous-espaces de Krylov en égalité du générateur initial lorsque la croissance de Krylov reste stricte au pas suivant. Elle permet de distinguer collision de sous-espaces réellement produite par le même générateur quotient, simple égalité accidentelle de dimensions, et perte d'identifiabilité lorsque `A^L v∈K_L(v)`.

## Limites
- Si `A^L v∈K_L(v)`, la conclusion peut être fausse.
- Sur un corps non binaire, le générateur n'est récupéré qu'à multiplication scalaire près.
- La brique ne dit pas que les hypothèses de croissance stricte sont satisfaites ; elles doivent être vérifiées dans l'application.

## Première application certifiée
`OBS-V19-BAD-FIBER2` l'applique dans le quotient par les contraintes forcées, avec `L=3`, pour les mauvais objets propres au-dessus d'un cycle `C5`.