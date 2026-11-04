# V19 — Région exacte de coexistence et correction du modèle de packing

Date : 15 octobre 2026

## 1. Question

Après le calcul des capacités individuelles, l'hypothèse de travail était qu'un **packing de ressources partagées** pourrait produire des inégalités mixtes entre plusieurs ombres exactes.

L'audit adversarial montre que cette abstraction est incorrecte au niveau des occurrences de paires : un état peut participer à plusieurs paires distinctes. Les paires ne consomment donc pas les états comme des ressources exclusives.

## 2. Structure exacte pour un système fixé

Pour un système admissible `T`, soit `P(T)` l'ensemble des paires non ordonnées distinctes produisant une ombre propre et

`σ_T : P(T) → Ω`.

Les fibres `P_ω(T)=σ_T^{-1}(ω)` forment une partition de `P(T)`.

Si l'on sélectionne arbitrairement des paires distinctes, le vecteur de multiplicité réalisable satisfait exactement

`0≤m_ω≤ν_T(ω)=|P_ω(T)|`.

Réciproquement, toute combinaison de ces bornes est réalisable en sélectionnant indépendamment `m_ω` éléments de chaque fibre.

### Matrice TU

La matrice `A_{ω,p}=1[σ_T(p)=ω]` possède exactement un `1` par colonne. Toute sous-matrice carrée a déterminant `0` ou `±1`; `A` est donc totalement unimodulaire.

**Conclusion :** le problème de sélection de paires dans un `T` fixé n'a pas de facette mixte cachée et sa relaxation linéaire est exacte.

**STATUT : DÉMONTRÉ.** Cette structure devient `BR-OBS-CAP-03`.

## 3. Famille cofinale V19

On reprend les 70 ombres géométriques exactes orientées de `OBS-V19-C5-CAPACITY` v2.

Construire `T_r` par :

- bassin binaire maximal de profondeur 3 au-dessus de `C5` ;
- deux composantes fixes maximales jusqu'à profondeur pertinente ;
- `r` gadgets disjoints à 2-cycle de profondeur 2.

Le calcul exact vérifie pour `r=0,1,2,3,5,10` :

- toutes les 50 capacités finies restent **exactement à leur maximum** ;
- les cinq rotations de chacune des classes infinies `06,08,10,12` croissent strictement et simultanément.

Les incréments observés par copie géométrique sont linéaires dans cette famille :

- `C5O-06` : `0,4,8,12,...`
- `C5O-08` : `0,4,8,12,...`
- `C5O-10` : `24,40,56,72,...`
- `C5O-12` : `48,56,64,72,...`.

La non-bornitude arbitraire repose sur le lemme déjà certifié du gadget réplicable ; les valeurs échantillonnées sont des tests de régression exacts.

## 4. Théorème de région géométrique

Soit `F` l'ensemble des 50 ombres de capacité finie et `I` les 20 ombres infinies.

Alors la région globale des multiplicité́s de paires distinctes est

`C_geo = (∏_{ω∈F}[0,Cap(ω)]_Z) × N^20`.

### Preuve

- Toute réalisation respecte les capacités individuelles : nécessité.
- La famille `T_r` atteint simultanément toutes les bornes finies et devient arbitrairement grande sur chaque coordonnée infinie.
- Pour un vecteur cible donné, choisir `r` assez grand puis appliquer le théorème des fibres disjointes.

Aucune autre inégalité n'est nécessaire.

**STATUT : DÉMONTRÉ.** Carte : `OBS-V19-COEX-REGION`.

## 5. Premier ordre d'obstruction géométrique

La capacité exacte minimale est `2` et concerne 20 ombres : cinq rotations de chacune des classes `C5O-00,01,02,03`.

Donc :

`k_geo*=3`.

Tous les multisets de taille `≤2` sont réalisables. Les 20 premiers multisets interdits de taille 3 sont exactement `3×ω` pour les 20 ombres de capacité 2.

## 6. Projection sur les 14 labels orientés

En sommant les cinq rotations, les capacités totales des classes finies sont :

`[10,10,10,10,40,20,∞,40,∞,60,∞,80,∞,160]`.

La région des multisets de labels orientés est donc exactement le produit des intervalles finis correspondants et de quatre coordonnées non bornées.

Il en résulte :

`k_classe*=11`.

Les quatre obstructions pures minimales à l'ordre 11 sont :

- `11×C5O-00` ;
- `11×C5O-01` ;
- `11×C5O-02` ;
- `11×C5O-03`.

`OBS-V19-FIRST-OBSTRUCTION11` reste vrai mais est renforcé en v2.

## 7. Falsification du modèle de packing exclusif

L'idée initiale `Ax≤b` avec consommation exclusive des cellules d'états est **réfutée comme modèle exact des occurrences de paires** : la même ressource d'état peut participer simultanément à de nombreuses paires distinctes.

Le seul `A` exact au niveau de la sélection est la matrice fibre paire→ombre, qui est TU et ne produit que des bornes coordonnées.

Cette réfutation ne dit pas que toute structure de capacité partagée est impossible à des niveaux plus riches.

## 8. Interface avec les circuits positifs

La prochaine cible doit être déplacée d'un niveau :

`paire p → mauvais objet B_p → ombre sh(B_p)`.

Deux phénomènes peuvent alors créer de vraies contraintes collectives :

1. plusieurs paires distinctes peuvent produire le **même mauvais objet**, donc la capacité de support `μ_T(ω)` peut être strictement inférieure à la capacité en paires `ν_T(ω)` ;
2. un support de circuit impose des relations d'incidence entre mauvais objets qui ne sont pas capturées par les seuls nombres de paires.

Les artefacts V16/V17 actuellement retrouvés donnent les profils et tailles de supports, mais pas la liste géométrique complète de chaque support/certificat. Aucun test support-par-support n'est donc promu dans ce commit.

## 9. Statuts

- `BR-OBS-CAP-03` : **DÉMONTRÉ**, principe général élémentaire / reformulation spécialisée.
- `OBS-V19-COEX-REGION` : **DÉMONTRÉ**.
- `OBS-V19-FIRST-OBSTRUCTION11` : renforcé en v2, **DÉMONTRÉ**.
- hypothèse « facettes mixtes non triviales au niveau des paires par consommation exclusive des états » : **RÉFUTÉE comme modèle exact**.
- originalité bibliographique de l'application V19 : **INDÉTERMINÉE**.

## 10. Artefacts

- `/Recherche/04_CODE_DONNEES/v19_coexistence_region.py`
- `/Recherche/04_CODE_DONNEES/V19_COEXISTENCE_REGION_C5O14_2026-10-15.csv`
- `/Recherche/04_CODE_DONNEES/V19_COEXISTENCE_REGION_SUMMARY_2026-10-15.json`