# Bibliothèque de recherche — structure de référence

Mise en ordre : 14 octobre 2026.

## Principe

La bibliothèque est séparée en huit niveaux afin qu'un résultat puisse être retrouvé et réutilisé sans relire tout son historique.

1. `00_INDEX_ET_METHODES` — cartes, méthodes, conventions et navigation.
2. `01_BRIQUES_REUTILISABLES` — énoncés autonomes suffisamment stabilisés pour être appelés depuis d'autres recherches.
3. `02_PROGRAMMES_ACTIFS` — journaux et dossiers de recherche en cours, classés par programme.
4. `03_AUDITS_CERTIFICATS` — vérifications adversariales, calculs indépendants, reçus et audits.
5. `04_CODE_DONNEES` — scripts et sorties qui ne sont pas déjà attachés naturellement à un programme.
6. `05_BIBLIOGRAPHIE` — matrices bibliographiques et sources.
7. `90_ARCHIVES_VERSIONS` — anciennes versions, paquets reproductibles et snapshots.
8. `99_QUARANTAINE` — résultats dont le statut, la définition ou la reproductibilité doit être réauditée avant réutilisation.

## Règle de promotion vers une brique

Une fiche de `01_BRIQUES_REUTILISABLES` doit contenir : un ID stable, un énoncé exact, son domaine, ses hypothèses, son statut, la source de preuve ou de calcul, les limites de généralisation et ses dépendances. Une brique ne revendique jamais une nouveauté bibliographique si celle-ci n'a pas été vérifiée.

## Programmes actifs

- `Delta_h_Fermeture` : recollement, accès, interventions et coûts de fermeture.
- `Observabilite` : observabilité temporelle et active, ADS/PDS, classifications finies.
- `Temps_Regle90` : dynamique de Règle 90, périodes, résolution observationnelle et orientation temporelle.
- `Quantique` : mémoire multitemporelle, ambiguïtés processus–instruments et protocoles de départage.
- `Transformations_Autonomie` : états prédictifs dérivés, fermeture opérationnelle, autonomie et réalisation relative.

## Convention de statut

- `DÉMONTRÉ` : preuve mathématique présente dans la source indiquée, dans le domaine déclaré.
- `CALCUL EXACT` : résultat fini exhaustif/reproductible, sans extrapolation hors domaine.
- `REFORMULATION` : conséquence ou présentation utile d'un cadre connu.
- `RÉFUTÉ` : conjecture contredite par preuve ou contre-exemple.
- `INDÉTERMINÉ` : information insuffisante, notamment pour une revendication d'originalité.

L'index des briques est `INDEX_BRIQUES.md`.


## Politique de consolidation

Le rangement documentaire ne doit jamais modifier le contenu scientifique. `RESEARCH_MEMORY.sqlite` reste la source de vérité pour les cartes et leurs statuts. Un fichier nouvellement rangé ou indexé n’est pas promu par ce seul fait. Les déplacements physiques d’artefacts déjà cités sont évités lorsqu’ils casseraient des chemins de provenance ; on préfère alors un manifeste de navigation jusqu’à un commit de migration dédié.