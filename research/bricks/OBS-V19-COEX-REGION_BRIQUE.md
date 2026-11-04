# OBS-V19-COEX-REGION — Région exacte de coexistence des ombres orientées

**Type :** brique d'application / théorème de coexistence complet  
**ID scientifique :** `OBS-V19-COEX-REGION` v1  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Dépendances :** `BR-OBS-CAP-03`, `OBS-V19-C5-CAPACITY` v2.

## Domaine

Cycle orienté `C5` avec `T(c_i)=c_{i+1}`, observation binaire, horizon `L=3`, contraintes forcées cohérentes. Une occurrence est une paire non ordonnée d'états distincte. On considère les **70 ombres géométriques exactes** compatibles avec l'orientation commune.

## Région exacte au niveau géométrique

Soit `F` l'ensemble des 50 ombres de capacité finie et `I` les 20 ombres de capacité infinie. Pour `ω∈F`, les capacités exactes sont celles de `OBS-V19-C5-CAPACITY` v2.

La région de coexistence globale est exactement

`C_geo = {m∈N^70 : m_ω≤Cap(ω) pour tout ω∈F}`.

Autrement dit :

`C_geo = (∏_{ω∈F}[0,Cap(ω)]_Z) × N^20`.

Il n'existe **aucune inégalité mixte supplémentaire** entre les multiplicité́s de paires à ce niveau.

## Preuve

1. **Nécessité.** Par définition de `Cap(ω)`, toute réalisation satisfait `m_ω≤Cap(ω)` pour chaque ombre finie.
2. **Sélection dans un système fixé.** Par `BR-OBS-CAP-03`, les fibres paire→ombre sont disjointes et toute combinaison coordonnée sous les effectifs disponibles est sélectionnable.
3. **Atteinte simultanée du cœur fini.** Le système formé du bassin binaire maximal de profondeur 3 et des deux composantes fixes maximales atteint simultanément toutes les capacités des 50 ombres finies.
4. **Cofinalité des directions infinies.** Ajouter `r` gadgets disjoints à 2-cycle conserve exactement les capacités finies et fait croître simultanément sans borne les cinq rotations de `C5O-06,08,10,12`.
5. Pour tout vecteur cible fini, choisir `r` assez grand pour dominer ses 20 coordonnées infinies, puis sélectionner dans chaque fibre le nombre de paires demandé.

## Ordre critique géométrique

Les capacités géométriques minimales finies valent `2`, pour les 20 ombres appartenant aux cinq rotations des classes `C5O-00,01,02,03`.

Donc :

`k_geo* = 3`.

Tous les multisets géométriques de cardinal `≤2` sont réalisables. À l'ordre 3, les **20 premiers multisets interdits** sont exactement

`3×ω`

pour chacune des 20 ombres de capacité `2`.

## Projection sur les 14 labels orientés

Chaque classe orientée possède cinq rotations géométriques. La région projetée sur les labels `C5O-00..13` est encore une boîte/orthant :

- `C5O-00 ≤ 10`
- `C5O-01 ≤ 10`
- `C5O-02 ≤ 10`
- `C5O-03 ≤ 10`
- `C5O-04 ≤ 40`
- `C5O-05 ≤ 20`
- `C5O-06` non bornée
- `C5O-07 ≤ 40`
- `C5O-08` non bornée
- `C5O-09 ≤ 60`
- `C5O-10` non bornée
- `C5O-11 ≤ 80`
- `C5O-12` non bornée
- `C5O-13 ≤ 160`.

Toute combinaison respectant ces bornes est réalisable par des paires distinctes dans un même système admissible.

## Corollaire — ordre critique des labels

`k_classe* = 11`.

Les quatre premiers témoins purs sont

`11×C5O-00`, `11×C5O-01`, `11×C5O-02`, `11×C5O-03`.

Cela renforce `OBS-V19-FIRST-OBSTRUCTION11` : la valeur `11` reste inchangée, mais on dispose maintenant de la classification complète de la région et de quatre familles critiques minimales au lieu d'un seul témoin.

## Conséquence méthodologique

La piste d'un **polytope non trivial de ressources partagées au niveau des paires** est réfutée : le partage d'états entre plusieurs paires n'est pas une consommation exclusive et n'engendre pas de facettes mixtes.

Le prochain niveau pertinent est le **relèvement paire → mauvais objet distinct / support de circuit**, où plusieurs paires peuvent fusionner vers un même objet et où des contraintes d'incidence supplémentaires peuvent apparaître. `BR-OBS-CAP-02` reste indispensable pour ne pas confondre support et poids algébrique.

## Provenance

Rapport : `/Recherche/03_AUDITS_CERTIFICATS/V19_REGION_COEXISTENCE_2026-10-15.md`  
Code : `/Recherche/04_CODE_DONNEES/v19_coexistence_region.py`  
Résumé : `/Recherche/04_CODE_DONNEES/V19_COEXISTENCE_REGION_SUMMARY_2026-10-15.json`  
Projection classes : `/Recherche/04_CODE_DONNEES/V19_COEXISTENCE_REGION_C5O14_2026-10-15.csv`