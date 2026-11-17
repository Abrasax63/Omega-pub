# BR-AFFINE-GROUP-CORE v1

Noyau incompatible affine par groupes et certificat de minimalité

Statut : DÉMONTRÉ interne. Originalité : CLASSIQUE / APPLICATION INTERNE ; aucune priorité revendiquée.

## Énoncé

Pour une famille incompatible de groupes finis d’équations affines sur F2 dans d variables, l’élimination incrémentale avec provenance indépendante extrait un support incompatible d’au plus d+1 lignes et groupes. Une réduction par suppressions testant toutes les lignes des groupes produit un noyau minimal par inclusion. Une preuve XOR 0=1 et une affectation satisfaisante pour chaque suppression certifient indépendamment l’incompatibilité et cette minimalité.

## Domaine et hypothèses

Systèmes affines binaires finis, sans fond immuable non représenté.

- Coefficients et seconds membres valides dans F2.
- Provenance en lignes originales acceptées indépendantes avant la première contradiction.
- Suppression d’un groupe signifie suppression de toutes ses équations.
- Minimalité par inclusion, sans optimalité de cardinalité ou de temps.

## Preuve et limites

Preuve algébrique et monotonicité ; audit multiagent indépendant. Principes classiques, référence Junker2004. Vérificateur par XOR et évaluation sans solveur. Certification interne, sans audit humain externe ni preuve compilée.

Preuves complètes, contre-exemples, sources et contrôles : /AFFINE_GROUP_CORE_2026-10-15.md. Archive : /PREUVES_AFFINE_GROUP_CORE_2026-10-15.zip.

Certification interne, sans validation humaine externe ni compilation formelle. Commit COMMIT-RAVI2-2026-10-15-AFFINE-CORE-15.