# OBS-AFFINE-GROUP-CORE-VALIDATION v1

Validation exacte du détecteur et essais de blocages collectifs

Statut : CALCUL EXACT interne. Originalité : VALIDATION INTERNE / AUCUNE PRIORITÉ REVENDIQUÉE ; aucune priorité revendiquée.

## Énoncé

Les deux méthodes ont été vérifiées contre l’énumération sur 50653 familles ordonnées de trois groupes en dimension2 (37 options par groupe), soit101306 exécutions, plus8 cas limites ; 2000 exécutions supplémentaires sur1000 familles générées de dimension≤6 passent aussi. Sur86 entrées de benchmark,74 incompatibles et12 compatibles, les172 sorties exportées sont vérifiées directement après relecture JSON. Les cinq triples N11 sélectionnés et les cycles de longueurs3,4,8,16 donnent des noyaux où tous les objets sont indispensables.

## Domaine et hypothèses

Populations exactes décrites dans le rapport et les fixtures ; pas conclusion universelle de performance.

- Audit exhaustif : groupes contenant zéro, une ou deux équations distinctes parmi huit en dimension2 ; peut inclure groupes incohérents.
- Génération déterministe seed20261015 ; mêmes entrées et ordre pour les deux méthodes.
- Fixtures N11 provenant des cinq familles et triples déjà contrôlés.
- Chronométrages exploratoires exclus du statut CALCUL EXACT et des prémisses de supériorité.

## Preuve et limites

Référence exhaustive indépendante, tests de corruption, vérification des certificats exportés ; code standard Python, mode -O refusé. Gains et pertes temporels rapportés séparément, sans certifier un gain général ni un noyau de cardinalité minimum.

Preuves complètes, contre-exemples, sources et contrôles : /AFFINE_GROUP_CORE_2026-10-15.md. Archive : /PREUVES_AFFINE_GROUP_CORE_2026-10-15.zip.

Certification interne, sans validation humaine externe ni compilation formelle. Commit COMMIT-RAVI2-2026-10-15-AFFINE-CORE-15.