# OBS-V19-BAD-FIBER2 — Fibre paire → mauvais objet de taille au plus 2

**Type :** brique d'application / théorème structurel  
**ID scientifique :** `OBS-V19-BAD-FIBER2` v1  
**Statut :** DÉMONTRÉ (certification interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Dépendances causales :** `BR-OBS-KRYLOV-01`, `OBS-V19-FORCED-P4`.

## Domaine

Soit `T:X→X` une endofonction finie avec cycle distingué orienté `C5`, observation binaire, horizon `L=3`, et contraintes forcées cohérentes.

Pour une paire non ordonnée `p={x,y}`, poser

`v_p=e_x+e_y`

et définir le mauvais objet

`B_p={c : contraintes forcées et c(T^t x)=c(T^t y), t=0,1,2}`.

On ne considère ici que les `B_p` **non vides dont l'ombre sur C5 est propre**, c'est-à-dire ni vide ni pleine.

## Théorème

Pour tout mauvais objet propre `B`,

`#{p : B_p=B} ≤ 2`.

Plus précisément, si deux paires distinctes `p,q` vérifient `B_p=B_q=B`, alors :

1. elles ont la même paire-image exacte : `Tp=Tq={a,b}` avec `a≠b` ;
2. les fibres `T^{-1}(a)` et `T^{-1}(b)` ont chacune deux états ;
3. `p` et `q` sont les deux coins opposés de même parité du rectangle `T^{-1}(a)×T^{-1}(b)`.

Il n'existe donc pas de troisième paire distincte donnant le même mauvais objet propre.

## Preuve — structure

### 1. Quotient par les contraintes forcées

Soit `H` l'espace engendré par les formes `e_u+e_v` des contraintes forcées. Pour une arête de fusion `Tu=Tv`, l'opérateur de transfert `A e_u=e_{Tu}` envoie `e_u+e_v` sur `0`. Pour une arête invariante `{Tu,Tv}={u,v}`, il l'envoie sur elle-même. Donc

`A(H)⊂H`

et `A` induit un endomorphisme `Ā` sur `Q=F_2^X/H`.

### 2. Croissance de Krylov stricte pour une ombre propre

Pour un état dans le bassin de `C5`, noter `φ(u)∈Z/5` sa phase asymptotique et définir

`π(e_u)=e_{φ(u)}`

sur ce bassin, `π(e_u)=0` hors du bassin. Alors `πA=Pπ`, où `P` est le décalage cyclique, et `H⊂ker π`.

Si `π(v_p)=0`, toutes les contraintes de Krylov de la paire ainsi que les contraintes forcées ont projection nulle ; aucune contrainte non nulle ne peut alors être induite uniquement sur le `C5`. L'ombre est pleine. Ainsi une ombre propre impose

`π(v_p)≠0`.

Ce vecteur est soit de poids 1, soit un vecteur non nul de l'espace d'augmentation du `C5`. Dans le second cas, le facteur non trivial est `Φ_5(x)=x^4+x^3+x^2+x+1`, irréductible sur `F_2`. Dans les deux cas,

`π(v_p), Pπ(v_p), P²π(v_p), P³π(v_p)`

sont linéairement indépendants. Par conséquent, dans `Q`,

`dim span(v̄,Āv̄,Ā²v̄)=3`

et

`Ā³v̄` n'appartient pas à ce 3-espace.

### 3. Une collision récupère l'équation initiale

Si `B_p=B_q` et l'objet est non vide, les systèmes affines augmentés ont le même espace de lignes. Après quotient par les contraintes forcées, leurs 3-espaces de Krylov coïncident.

Par `BR-OBS-KRYLOV-01`, sur `F_2`,

`v̄_p=v̄_q`.

Donc `h=v_p+v_q∈H`. Comme les deux équations initiales ont second membre `0` et que l'objet commun est non vide, la parité forcée portée par `h` est également `0`.

Les deux paires relient donc les mêmes deux composantes forcées, avec la même parité signée.

### 4. La paire-image est unique

Dans chaque composante forcée, la structure certifiée `P1–P4` contient au plus une arête invariante centrale ; toutes les autres arêtes sont des fusions.

Le chemin forcé entre les représentants de `p` et `q` peut traverser zéro, une ou deux arêtes invariantes au total. L'égalité des contraintes au temps 1 exclut un nombre impair d'arêtes invariantes.

S'il en traversait deux, les deux composantes concernées seraient invariantes par `T` dans le quotient, donc `Āv̄=v̄`, contradiction avec la croissance de Krylov stricte ci-dessus.

Il n'en traverse donc aucune. Les chemins ne contiennent que des arêtes de fusion, et une arête de fusion relie deux états ayant la même image. Ainsi

`Tp=Tq`.

### 5. Comptage des relevés

Écrire `Tp=Tq={a,b}`. La croissance de rang impose `a≠b`. La cohérence binaire donne

`|T^{-1}(a)|≤2`, `|T^{-1}(b)|≤2`.

Les candidats sont donc au plus les quatre coins d'un rectangle `2×2`. Changer un seul choix de frère ajoute une contrainte forcée d'opposition, donc inverse la parité de l'équation initiale ; deux coins adjacents ne peuvent pas appartenir au même mauvais objet non vide. Seuls deux coins opposés de même parité peuvent coïncider.

D'où la borne `2`.

## Corollaire — objets distincts versus paires

Pour une ombre géométrique exacte `ω`, noter

`ν_T(ω)` = nombre de paires distinctes produisant `ω`,

`μ_T(ω)` = nombre de mauvais objets distincts dont l'ombre est `ω`.

Alors

`ceil(ν_T(ω)/2) ≤ μ_T(ω) ≤ ν_T(ω)`.

En particulier, toute ombre de capacité paire infinie possède aussi une capacité en mauvais objets infinie.

## Tests adversariaux exacts

Un checker indépendant de V14–V17 vérifie le théorème sur toutes les extensions étiquetées cohérentes d'un `C5` fixé pour `N=5,…,9` :

- 4 820 systèmes cohérents au total ;
- 148 120 paires propres ;
- 132 990 mauvais objets distincts ;
- aucune fibre de taille `>2` ;
- toute fibre de taille `2` a une paire-image exacte commune.

Le même test repasse les cinq ruptures historiques `N=11` et 100 systèmes déterministes supplémentaires de tailles `10,12,15,20,30`, sans divergence.

## Limites

- Le théorème est scoped à `C5`, binaire, `L=3`, contraintes forcées cohérentes, mauvais objet non vide et ombre propre.
- Il ne s'étend pas aux ombres pleines ou vides : des collisions plus riches existent hors de ce domaine.
- Il ne calcule pas encore la capacité exacte en **mauvais objets** de chaque ombre ; il la relie à la capacité en paires.
- Il ne borne pas les coefficients entiers portés par un même mauvais objet dans un circuit positif.

## Provenance

Audit : `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_FIBER2_2026-10-15.md`  
Checker : `/Recherche/04_CODE_DONNEES/v19_badobject_fiber2_exact.py`  
Régression : `/Recherche/04_CODE_DONNEES/V19_BADOBJECT_FIBER2_REGRESSION_2026-10-15.json`.