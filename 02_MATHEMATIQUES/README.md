# Module Mathématiques

**Périmètre :** systèmes dynamiques finis, théorie de l'observation, invariants et résultats mathématiques associés.

## Commencer ici

- [Fiches mathématiques présentes dans le dépôt](../00_GOUVERNANCE/INDEX_GLOBAL.md)
- [État de migration des résultats mathématiques](MIGRATION_ETAT.md)
- [Modèle commun de fiche](../templates/RESULTAT.md)

## Dossiers disponibles

### Règle 90

- [BR-R90-01 — Noyaux et période récurrente](temps_regle90/BR-R90-01_NOYAUX_PERIODES.md)
- [BR-R90-02 — Uniformité Majority–Walsh avant repliement cyclique](temps_regle90/BR-R90-02_MAJORITY_WALSH.md)

Ces deux fiches sont actuellement publiées avec le statut **EXPÉRIMENTAL** : leurs fiches internes sources ont été transférées, mais leurs audits détaillés ne sont pas encore joints ici. Voir les limites indiquées dans chaque fiche.

## Migration en cours

Les résultats CL-DYN-01/02/03/04 et les briques d'observation listées dans [MIGRATION_ETAT.md](MIGRATION_ETAT.md) ne sont pas encore présentés comme fiches publiques complètes. Leur migration attend la récupération et le contrôle des sources primaires.

Le pilote C4, L=2 est maintenant documenté comme **CALCUL EXACT sous la définition primaire interne V19(2)** pour les huit classes C4O-00…07. Sa publication reste **EXPÉRIMENTALE** ; originalité bibliographique indéterminée et formalisation Lean non réalisée. Voir [le pilote complet](defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md) et [le raccord primaire](defauts_recollement/RACCORD_PRIMAIRE_V19_C4_L2_2026-11-04.md). Les autres dossiers C4 et les travaux SAT ne sont pas déclarés certifiés.

## Règles du module

- Ne pas fusionner des sujets distincts au seul motif qu'ils utilisent une notation commune.
- Définir localement les objets, hypothèses et conventions.
- Distinguer preuve générale, calcul fini exact, simulation et conjecture.
- Conserver les réfutations, limites et anciennes versions.
- Toute fiche doit préciser ses dépendances et la version exacte des résultats qu'elle utilise.


## Instruments et extraction de méthodes

- [Bibliothèque des instruments](instruments/README.md)
- [Registre des instruments](instruments/REGISTRE_INSTRUMENTS.md)
- [Modèle de fiche d'instrument](instruments/MODELE_INSTRUMENT.md)

Le registre distingue les instruments généraux admis des candidats internes ou externes. Le pilote C4 est un cas interne limité à q=4 et L=2 ; aucune transférabilité générale n'est revendiquée.


## Instruments et extraction de méthodes

- [Bibliothèque des instruments](instruments/README.md)
- [Registre des instruments](instruments/REGISTRE_INSTRUMENTS.md)
- [Modèle de fiche d'instrument](instruments/MODELE_INSTRUMENT.md)

Le registre distingue les instruments généraux admis des candidats internes ou externes. Le pilote C4 est un cas interne limité à q=4 et L=2 ; aucune transférabilité générale n'est revendiquée.


## Dossier expérimental V19 — C5, L=3

Un audit indépendant du catalogue C5/D5, des témoins de paires et triples et du témoin U42 a été migré dans [le dossier C5](v19_c5/AUDIT_V19_C5_L3_2026-11-05.md). Les données historiques et corrigées, le script et un résumé JSON sont conservés dans `research/data/v19_c5/` et `research/code/`. Le dossier reste **EXPÉRIMENTAL** : le lemme général de localité V19 n'est pas redémontré, l'originalité bibliographique reste indéterminée et Lean n'a pas été réalisé. Il n'est donc pas ajouté à l'index des fiches de résultats certifiées.
