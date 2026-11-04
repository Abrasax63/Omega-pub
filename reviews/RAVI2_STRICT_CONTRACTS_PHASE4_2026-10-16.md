# RAVI-2 v1.3 — formalisation stricte phase 4 / découverte certifiée

Date : 16 octobre 2026.

## Objet

Étendre la couche stricte après la découverte et la certification de `BR-AFFINE-GAUGE-CORE`, sans laisser les deux nouvelles dépendances causales hors couverture.

## Résultat

- Base scientifique candidate : 76 résultats, 72 admissibles, 42 `DEPEND_DE`.
- Registre strict : 41 contrats, 20 adaptateurs, 42 revues et 42 certificats d'interface.
- Classification : 37 `COMPOSITION`, 1 `VALIDATION_REFERENCE`, 2 `DATA_REFERENCE`, 2 `DEFINITION_REFERENCE`.
- Couverture causale : 42/42 ; aucune interface différée.

## Nouveau contrat

`BR-AFFINE-GAUGE-CORE` consomme le critère sémantique de `BR-AFFINE-GAUGE-GLUE` et, sous la garde `NO_COMMON_TRANSLATION`, applique l'adaptateur `ADAPT-GAUGE-TO-GROUPED-EQUATIONS` vers `BR-AFFINE-GROUP-CORE`.

L'adaptateur choisit une base de chaque espace de lignes `S_i` et construit les groupes `g·s=δ_i(s)` portant sur la même translation `g`. La preuve de `GAUGE-CORE` établit l'équivalence et l'indépendance du choix des bases.

## Reconstruction indépendante

Le moteur phase 4 a été exécuté sur un miroir vierge reconstruit depuis la base principale candidate et le registre phase 4 : 41 contrats, 42 revues et 42 certificats restaurés, aucune version stale, intégrité SQLite `ok`, 0 erreur de clé étrangère.

## Politique

Le score de découverte n'a aucune capacité de promotion. La seule promotion scientifique de ce cycle est `BR-AFFINE-GAUGE-CORE`, après preuve, calcul indépendant, audit de redondance/littérature et contrôles de base.

Rapport scientifique : `/GAUGE_CORE_BRIDGE_2026-10-16.md`.