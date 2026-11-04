# Certificat documentaire RAVI-2 — METHOD-RAVI-2

Date : 27 octobre 2026
Identifiant : `EVID-METHOD-RAVI2-SOURCE`
Résultat lié : `METHOD-RAVI-2`, version 1
Type : certificat de provenance documentaire — **pas** un certificat de preuve mathématique.

## Énoncé vérifié

La carte `METHOD-RAVI-2` décrit le workflow de recherche RAVI-2. Le document source correspondant est :

`/Recherche/00_INDEX_ET_METHODES/RESEARCH_METHOD_RAVI2.md`

## Verdict

**SOURCE_LOCATED** — la source documentaire de la méthode est identifiée et liée explicitement au résultat dans la copie réparée de `RESEARCH_MEMORY.sqlite`.

Ce verdict établit seulement la localisation de la définition de méthode. Il ne prouve ni l'efficacité générale de RAVI-2, ni une amélioration générale de l'intelligence, ni la validité de tous les résultats traités par cette méthode. Il ne constitue pas une certification scientifique indépendante.

## Changements de traçabilité associés

- Ajout de l'entrée `evidence` `EVID-METHOD-RAVI2-SOURCE` avec le statut `SOURCE_LOCATED`.
- Ajout de la relation `result_sources` de `METHOD-RAVI-2` vers `RESEARCH_METHOD_RAVI2.md`, rôle `METHOD_DEFINITION`.
- Aucun énoncé mathématique, statut scientifique, version de résultat ou arc `DEPEND_DE` modifié.

## Contrôles locaux de la base réparée

- `PRAGMA integrity_check` : `ok`.
- `PRAGMA foreign_key_check` : 0 violation.
- Nombre de résultats : 89, inchangé.
- Résultats admissibles : 85, inchangé.
- Entrées d'évidence : 217 (216 avant la réparation).
- Tests enregistrés PASS : 62, inchangé ; ils n'ont pas tous été rejoués dans cette opération.

## Limites et état de publication

Le certificat documentaire et les changements SQLite sont présents dans les artefacts locaux de travail. **Le remplacement de la base dans la bibliothèque partagée n'est pas confirmé** : aucune réponse de succès du service de fichiers n'a été reçue. Ne pas présenter la version de bibliothèque comme mise à jour tant qu'une relecture de cette version n'a pas confirmé les changements.