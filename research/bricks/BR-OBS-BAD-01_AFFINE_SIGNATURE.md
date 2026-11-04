# BR-OBS-BAD-01 — Signature affine canonique des mauvais objets

**Type :** brique réutilisable / algèbre affine exacte  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** CONNU_PRINCIPE_GENERAL / reformulation spécialisée

## Domaine

Soit un espace affine cohérent de configurations

`A_F = {c ∈ F_2^n : F c = b}`

défini par des contraintes forcées. À un témoin `p` est associée une famille homogène de contraintes supplémentaires

`E_p c = 0`.

Le mauvais objet associé est

`B_p = {c : F c=b, E_p c=0}`.

Dans l'application d'observabilité à horizon `L`, `E_p` est engendré par les égalités le long de l'orbite de la paire :

`c(T^t x)+c(T^t y)=0`, `0≤t<L`.

## Signature

Former la matrice augmentée des équations

`M_p = [(F|b); (E_p|0)]`

et définir `Sig_F(p)` comme sa forme échelonnée réduite canonique sur `F_2`.

## Théorème — critère exact de collision

Pour deux témoins `p,q` dont les mauvais objets sont non vides,

`B_p = B_q  ⇔  Sig_F(p)=Sig_F(q)`.

**Preuve.** Un système affine cohérent est entièrement déterminé par l'espace de lignes de sa matrice augmentée : chaque ligne est une conséquence affine des équations et la RREF est l'unique représentant canonique de cet espace de lignes. Deux systèmes cohérents ont donc le même ensemble de solutions si et seulement si leurs espaces de lignes augmentés, donc leurs RREF, coïncident.

## Corollaires

1. Les collisions `p→B_p` se calculent exactement sans énumérer toutes les configurations.
2. Le nombre de mauvais objets distincts est le nombre de signatures distinctes.
3. Toute projection ou ombre attachée à `B_p` est constante sur une fibre de la signature.
4. Le critère reste valide avec des contraintes forcées affines non homogènes : le second membre doit être conservé dans la signature augmentée.

## Piège évité

Comparer seulement les espaces de lignes **homogènes** des formes linéaires est insuffisant lorsque les contraintes forcées ont un second membre non nul. Deux équations ayant la même forme linéaire modulo les contraintes homogènes peuvent représenter des classes affines opposées. La signature doit donc porter les colonnes augmentées `(forme,rhs)`.

## Limites

- Le théorème ne borne pas la taille d'une fibre `#{p:B_p=B}`.
- Deux témoins distincts peuvent produire le même mauvais objet.
- Le cas vide doit être traité séparément : tous les systèmes affines incohérents ont le même ensemble de solutions vide sans nécessairement avoir la même RREF avant réduction avec la ligne `0=1` normalisée.

## Première application certifiée

`OBS-V19-N11-BADOBJECT` utilise cette signature pour reconstruire indépendamment les cinq premières ruptures d'intégralité à `N=11`.