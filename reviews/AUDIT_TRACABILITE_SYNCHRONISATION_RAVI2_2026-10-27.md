# Audit de traçabilité et de synchronisation RAVI-2 — 27 octobre 2026

## Portée et méthode

Contrôle en lecture seule de la copie actuelle de `/Recherche/00_INDEX_ET_METHODES/RESEARCH_MEMORY.sqlite` (version Library 32), de `MEMORY_INDEX.md` (version 37) et de `RESEARCH_SNAPSHOT_ACTIVE.md` (version 34). Aucun statut scientifique, résultat, dépendance ni lien de provenance n'a été modifié par cet audit.

## 1. Intégrité et compteurs

- SQLite `PRAGMA integrity_check` : `ok`.
- `PRAGMA foreign_key_check` : 0 violation.
- Table `results` : 89 cartes.
- Vue `certified_active_results` : 85 admissibles.
- `evidence` : 216 entrées.
- `regression_tests` : 62 entrées, toutes enregistrées `PASS`.
- `relations` de type `DEPEND_DE` : 49.
- Dernière date de test enregistrée : 2026-10-20 15:43:33 +02:00. Il s'agit de la date stockée dans la base, pas d'un rejeu effectué le 27 octobre.
- Le dernier commit scientifique enregistré dans `meta` est `COMMIT-RAVI2-2026-10-20-TWO-EQUAL-GAPS-25`.

Les deux documents miroirs portent le même en-tête de commit TWO-EQUAL-GAPS-25 et affichent 89 cartes / 85 admissibles / 49 `DEPEND_DE`. La désynchronisation annoncée dans le résumé précédent n'est donc **pas confirmée** par les versions actuelles consultées. Les différences de compteurs présentes dans d'autres sections sont des états historiques explicitement datés, pas en elles-mêmes une preuve de désynchronisation.

## 2. Lacunes de liaison de provenance

Dix identifiants de `results` n'ont aucune ligne dans `result_sources` :

1. `METHOD-RAVI-2`
2. `NS-CERT-E-10`
3. `NS-CERT-E-11`
4. `NS-CERT-E-12`
5. `NS-CERT-E-13`
6. `NS-CERT-E-14`
7. `NS-CERT-E-15`
8. `OBS-RESTRICT-COUNT`
9. `OBS-RESTRICT-GREEDY`
10. `OBS-RESTRICT-PROFILE`

Nuance importante : il ne s'agit pas de dix cartes toutes dépourvues de justificatifs. Neuf ont au moins une entrée `evidence` pointant vers un artefact ; seule `METHOD-RAVI-2` n'a aucune entrée dans `evidence` non plus. Pour les neuf autres, la relation explicite `result_sources` est manquante. Les six cartes NS partagent certains documents de preuve, et deux groupes ont des sources candidates ambiguës au niveau du fichier commun ; les trois cartes OBS pointent vers des rapports qui ne sont pas enregistrés comme sources correspondantes dans la table `sources` sous le même chemin. Aucune liaison n'a été ajoutée automatiquement afin de ne pas inventer de provenance.

## 3. Mémoire conversationnelle

- `memory_nodes` : 7 nœuds, tous `ACTIVE`.
- `memory_links` : 0.
- `memory_snapshots` : 1.
- `memory_snapshot_items` : 7.
- L'ensemble des identifiants de nœuds actifs correspond exactement à l'ensemble des éléments du snapshot.

Ainsi, les sept nœuds sont isolés du point de vue du graphe relationnel, mais ils ne sont pas absents du snapshot et ne sont pas orphelins au sens d'un élément actif oublié par celui-ci. L'absence de liens n'est pas automatiquement une erreur : les relations doivent refléter une dépendance, une correction ou une confirmation réelle. Aucun lien n'a été fabriqué.

## 4. Décisions et réparations sûres

- **Confirmé :** intégrité SQLite correcte, aucune violation de clé étrangère, compteurs principaux cohérents entre la base et les en-têtes des deux miroirs.
- **Confirmé :** dix cartes sans relation `result_sources`, mais neuf ont déjà une entrée `evidence`; une seule carte (`METHOD-RAVI-2`) n'a ni relation source ni entrée de preuve.
- **À réparer après vérification du contenu des documents :** ajouter les relations `result_sources` uniquement après confirmation exacte des sources, notamment pour les rapports partagés NS et les rapports OBS.
- **À documenter, pas à corriger automatiquement :** l'absence de `memory_links` entre les sept nœuds actifs. Il faut déterminer les relations sémantiques réelles avant d'en ajouter.
- **À rejouer :** les 62 tests sont enregistrés PASS, mais la date la plus récente enregistrée est le 20 octobre. Un nouveau rejeu indépendant reste nécessaire pour affirmer leur reproductibilité actuelle.
- **Aucune promotion scientifique :** cet audit ne crée aucune brique, ne modifie aucun statut et ne change aucun arc `DEPEND_DE`.

## Verdict

État technique de la base : **PASS** pour l'intégrité SQLite et les clés étrangères.

Synchronisation des compteurs principaux : **COHÉRENTE** pour les versions consultées des trois artefacts.

Traçabilité des sources : **À CORRIGER**, avec 10 liaisons `result_sources` absentes, dont une carte sans aucune entrée de preuve.

Graphe de mémoire conversationnelle : **INCOMPLET MAIS SNAPSHOT COHÉRENT** ; 7 nœuds actifs sont inclus dans le snapshot, mais aucun lien relationnel n'est enregistré.

Reproductibilité des tests au 27 octobre : **NON REVALIDÉE** ; la base ne contient aucun rejeu daté du 27 octobre.