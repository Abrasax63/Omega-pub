# V19 — Théorème fibre≤2 pour paire → mauvais objet

Date : 15 octobre 2026

## 1. Verrou

Le commit précédent avait reconstruit exactement l'application

`p={x,y} → B_p → ombre(B_p)`

sur les cinq premières ruptures `N=11`. Toutes les fibres observées de `p→B_p` avaient taille `1` ou `2`, mais l'universalité de cette borne restait volontairement `INDÉTERMINÉE`.

Le présent audit ferme ce verrou dans le domaine `C5`, binaire, `L=3`, contraintes forcées cohérentes, pour les mauvais objets non vides à ombre propre.

## 2. Énoncé certifié

Pour tout mauvais objet propre `B`,

`#{p : B_p=B}≤2`.

Si deux paires distinctes `p,q` donnent le même `B`, alors elles ont la même paire-image exacte `Tp=Tq={a,b}` et sont les deux coins opposés de même parité du rectangle de prédécesseurs `T^{-1}(a)×T^{-1}(b)`.

Carte : `OBS-V19-BAD-FIBER2`.  
Statut : **DÉMONTRÉ**.

## 3. Lemme générique de Krylov

Nouvelle brique `BR-OBS-KRYLOV-01`.

Soit `K_L(v)=span(v,Av,…,A^(L-1)v)`. Si `dim K_L(v)=L` et `A^L v∉K_L(v)`, alors tout `w` tel que `K_L(w)=K_L(v)` vérifie `w=λv`.

Preuve triangulaire : écrire `w=Σ a_iA^iv`. La condition `Aw∈K_L(v)` élimine `a_(L-1)`, puis `A²w∈K_L(v)` élimine `a_(L-2)`, etc.

Sur `F_2`, `w=v`.

Statut : **DÉMONTRÉ**, principe d'algèbre linéaire général.

## 4. Quotient forcé et rang 4

Soit `H` le sous-espace engendré par les coefficients des contraintes forcées. Avec `A e_x=e_{Tx}` :

- une arête de fusion est envoyée sur `0` ;
- une arête invariante est envoyée sur elle-même.

Donc `H` est `A`-invariant.

Pour le bassin du `C5`, la phase asymptotique donne une application `π` vers `F_2^5` qui vérifie `πA=Pπ` et annule `H`.

Une ombre propre impose `π(v_p)≠0`. Si un seul endpoint est dans le bassin, ce vecteur a poids `1`; si les deux y sont à phases différentes, il appartient non trivialement à l'espace d'augmentation de dimension `4`.

Dans ce dernier espace, `Φ_5=x^4+x^3+x²+x+1` est irréductible sur `F_2`. Dans les deux cas, les quatre premiers itérés sont indépendants :

`v̄, Āv̄, Ā²v̄, Ā³v̄` sont indépendants dans le quotient utile.

C'est exactement l'hypothèse nécessaire à `BR-OBS-KRYLOV-01` pour `L=3`.

## 5. Collision ⇒ même paire-image

Supposons `B_p=B_q` propre et non vide. L'égalité des espaces affines augmentés implique l'égalité des 3-espaces de Krylov dans le quotient forcé. Le lemme de récupération donne

`v̄_p=v̄_q`.

Ainsi `h=v_p+v_q∈H`. L'objet commun étant non vide et les équations de paire ayant second membre zéro, la parité forcée de `h` vaut zéro.

Les représentants de `p` et `q` appartiennent donc aux mêmes deux composantes forcées avec la même parité.

Par `OBS-V19-FORCED-P4`, chaque composante est un chemin `P1–P4`, avec au plus une arête invariante centrale et des arêtes de fusion aux extrémités. Appliquer `A` au chemin entre représentants élimine les arêtes de fusion et conserve les arêtes invariantes.

L'égalité au temps `1` impose un nombre pair d'arêtes invariantes traversées : `0` ou `2`.

Le cas `2` rend les deux composantes invariantes et impose `Āv̄=v̄`, en contradiction avec l'indépendance de `v̄,Āv̄`.

Il reste `0` : les déplacements entre représentants sont uniquement des changements de frères de fusion, donc ne changent pas leur image. Par conséquent

`Tp=Tq`.

## 6. Fibre maximale

Pour `Tp={a,b}`, la cohérence forcée donne `|T^{-1}(a)|,|T^{-1}(b)|≤2`. Il existe donc au plus quatre couples de prédécesseurs.

Deux coins adjacents diffèrent par exactement une arête de fusion forcée, de second membre `1`, et correspondent à des équations initiales affines opposées. Ils ne peuvent définir le même objet non vide.

Une classe de parité ne contient donc que les deux coins opposés. La fibre a taille au plus `2`.

## 7. Corollaire de capacité de support

Pour une ombre exacte `ω`, avec `ν_T(ω)` paires et `μ_T(ω)` mauvais objets distincts,

`ceil(ν_T(ω)/2)≤μ_T(ω)≤ν_T(ω)`.

Donc les quatre familles d'ombres dont la capacité en paires est infinie dans `OBS-V19-C5-CAPACITY v2` ont également une capacité en mauvais objets infinie.

La capacité exacte finie de `μ` reste un problème distinct : la borne fibre≤2 ne dit pas si le supremum est atteint avec toutes les fibres simples, doubles, ou un mélange.

## 8. Audit exact indépendant

Checker : `v19_badobject_fiber2_exact.py`.

Exhaustif sur toutes les extensions étiquetées d'un `C5` fixé :

- `N=5` : 1 système cohérent ; 10 paires propres ; 10 objets ; fibres `1:10`.
- `N=6` : 6 ; 85 ; 85 ; fibres `1:85`.
- `N=7` : 44 ; 850 ; 810 ; fibres `1:770, 2:40`.
- `N=8` : 398 ; 10 025 ; 9 215 ; fibres `1:8 405, 2:810`.
- `N=9` : 4 371 ; 137 150 ; 122 870 ; fibres `1:108 590, 2:14 280`.

Total : 4 820 systèmes cohérents, 148 120 paires propres, 132 990 mauvais objets propres distincts, zéro fibre `>2`, zéro collision double avec paire-image différente.

Régression supplémentaire :

- les cinq mappings `N=11` : fibres exactes déjà observées `1/2`, zéro divergence ;
- 20 systèmes déterministes à chacune des tailles `10,12,15,20,30`, soit 100 systèmes supplémentaires, zéro divergence.

SHA-256 du checker : `806b3bb565a5a956949980a58fe1416ec7841e158826e1978c5d9b9982c4ff78`.  
SHA-256 du JSON : `f613f956259238a60e3333d785dcc2236bd52e4726b11052ba5c1bea404cd32d`.

Les calculs ne remplacent pas la preuve ; ils servent de reconstruction indépendante/falsification.

## 9. Portée et falsification anticipée

Le théorème **ne** couvre pas :

- les mauvais objets vides ;
- les ombres pleines ;
- un horizon autre que `L=3` ;
- un cycle périodique autre que `C5` sans preuve du rang de Krylov correspondant.

Des collisions plus riches existent hors du domaine propre ; cette restriction est donc substantielle, pas cosmétique.

## 10. Conséquence architecturale

La chaîne réutilisable devient :

`signature affine`  
`→ récupération du générateur Krylov`  
`→ fibre paire→B ≤2`  
`→ incidence entre mauvais objets`  
`→ circuits positifs / exact covers`.

Le prochain verrou est désormais la **capacité exacte en mauvais objets** `Cap_B(ω)` et non plus la multiplicité de la fibre paire→objet. Le cas `κ=5` de `N=12` reste également à reconstruire au niveau de l'incidence pondérée lorsque sa source primaire complète est disponible.