# P5-OBS-03 — observation réelle, provenance, dépendance et arrêt épistémique

**12 novembre 2026 — Statut : COLLECTE EXTERNE RÉELLE REPRODUCTIBLE / CERTIFICAT DE PROVENANCE VALIDÉ / INDÉPENDANCE ET SUPÉRIORITÉ OMEGA NON DÉMONTRÉES.**

## Chaîne de preuves et pré-enregistrement

- [Pré-enregistrement AVANT nouvelle lecture GitHub](EXPERIMENT_P5_OBS03_REAL_PROVENANCE_PREREG_2026-11-12.md), commit `6f9a63fef351457c0d62f15f9588f2048864d73a`.
- Source initiale : pilote P5-PR29 du 11 novembre, 12 PR issues de `python/cpython`, `pallets/flask` et `psf/requests`. [Instantané initial](prism/live_github_pr_gate_observations_2026-11-11.json). **Ce jeu était déjà analysé : pas de holdout nouveau.**
- Nouvelle lecture de **12 PR par 3 actions GitHub**, donc **36 observations principales** : `get_pr_info`, `list_pr_changed_filenames` et `fetch_pr`. Une **seconde lecture de chacune des 12 listes complètes de chemins** a été conservée pour permettre un nouveau calcul du critère de modification des tests. Les journaux sont enregistrés par lots dans `prism/obs03_fresh_pr_part{0,1,2}.json` et `prism/obs03_real_full_filenames_part{0,1,2}.json`.
- **[Exécution GitHub Actions #43225833512 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43225833512)** : 7 tests spécialisés réussis, vérifications sur les fichiers intégraux, conflits injectés dans les tests rejetés par le filtre. [Suite générale RCE #43225827843 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43225827843).
- [Archive des certificats par PR et comparaisons](https://github.com/Abrasax63/Omega-pub/actions/runs/43225833512/artifacts/13947239151). Ce calcul réutilise des données réellement lues via le connecteur, mais **GitHub Actions ne relit pas le réseau** : il vérifie les six fichiers d'observations enregistrés.
- Aucune génération de modèle, aucune API payante, aucun usage de données privées, aucune écriture sur `main`.

## Résultats de la nouvelle collecte

| Indicateur | Mesure vérifiée |
|---|---:|
| PR externes examinées | **12** |
| Observations des 3 endpoints enregistrées | **36** |
| Listes complètes de chemins conservées par relecture | **12** |
| Accord sur l'indicateur `merged` entre deux lectures de métadonnées GitHub | **12/12** |
| Variation observée de `merged` depuis le 11 novembre | **0/12** |
| Variation de `head_sha` depuis le 11 novembre | **0/12** |
| Cas classés `merged && touched_tests` | **1/12** |
| Fournisseurs distincts réels | **1 : github.com** |
| Corroborations indépendantes multi-fournisseurs | **0** |

Le filtre rend le statut **`SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED` sur les 12 cas**. Cela signifie exactement : la fusion et la SHA de tête concordent dans les deux vues de métadonnées, la liste complète des chemins reproduit le prédicat syntaxique et les deux lectures du nombre/du critère de chemins concordent. Cela **ne** prouve **pas** qu'un fournisseur indépendant a établi les faits.

### Limite temporelle et de réalisabilité

L'API des fichiers modifiés n'a pas été interrogée à un commit figé, et les appels ont été effectués successivement et/ou de manière concurrente : les répertoires GitHub peuvent changer entre lectures. Même avec deux SHA de métadonnées identiques, **la liste des chemins n'est pas transactionnellement liée à cette SHA par notre adaptateur**. Le certificat garde donc le statut `NOT_TRANSACTIONALLY_PINNED` ; ne pas le promouvoir en démonstration d'exactitude intemporelle. Aucune course n'a été détectée dans cet échantillon, mais absence de détection ≠ impossibilité.

## Audit des contrôles et de la dépendance

Le prédicat est `merged && touched_tests`, avec `touched_tests` défini uniquement par les chemins `test/`, `tests/`, basenames `test_*` ou `*_test.py`. Aucun titre de PR n'a été utilisé pour conclure.

Les politiques suivantes sont **rejouées sur les valeurs déjà acquises**, et les consultations ne sont **pas** des économies d'appels effectivement mesurées pendant cette nouvelle collecte :

| Stratégie | Bonnes décisions /12 | Consultations **logiques** |
|---|---:|---:|
| Rejeter sans vérifier | 11 | 0 |
| Lire toujours la fusion et les fichiers | **12** | 24 |
| Lire la fusion puis les fichiers si fusionnée | **12** | 17 |
| **Lire les fichiers puis la fusion si les tests ont changé** | **12** | **15** |

**Conclusion adversariale :** l'ordre initialement choisi par Omega n'est pas optimal sur le jeu observé : un ordre conditionnel simple économise encore deux lectures logiques. Cela correspond au contrôle déjà identifié dans l'audit de PR #29 ; P5-OBS-03 ne l'invente pas. L'écart est faible (12 cas) et l'ordre gagnant est choisi à partir des données **déjà connues**, donc aucun avantage prospectif n'est démontré.

## Valeur réelle du raccord avec l'observabilité

Le rapprochement avec notre travail `Δ_h` porte sur la conservation d'un **témoin global cohérent**, pas sur l'invention d'une fiabilité probabiliste à partir de deux endpoints :

1. La paire `(merged, head_sha)` issue de métadonnées ne doit pas être raccordée silencieusement à une liste de fichiers sans indiquer le risque d'instantané différent.
2. Une lecture `get_pr_info` et une autre `fetch_pr` ont deux chemins de récupération, **mais une même origine fournisseur**. Leur accord n'augmente pas le nombre de fournisseurs indépendants.
3. Une contradiction sur le même `merged` ou `head_sha` reçoit `CROSS_ENDPOINT_CONFLICT`. Une divergence entre le nombre/critère des chemins et la relecture reçoit `CROSS_READ_FILE_PATH_DRIFT`; une donnée manquante reçoit `INSUFFICIENT_EVIDENCE`.
4. Aucun de ces statuts ne permet de **prouver que GitHub s'est trompé** sans une référence externe indépendante et un périmètre temporel identique. Les contre-exemples incohérents utilisés par les tests sont **injectés par le banc de test**, jamais présentés comme de vraies fautes observées chez GitHub.

L'audit distingue ainsi **observabilité du processus de collecte**, **cohérence de provenance** et **vérité indépendante de la conclusion**, trois notions que nos anciens prototypes risquaient de confondre.

## Quelle piste externe pour une nouvelle cohorte ?

- [FEVEROUS](https://fever.ai/dataset/feverous.html) possède des annotations de décisions, ensembles de preuves textuelles/tabulaires, contexte et actions d'annotation. Il peut servir à tester le **raccord des preuves et l'abstention**, en rappelant qu'un grand nombre de pièces proviennent de **Wikipedia**, donc pas nécessairement de fournisseurs indépendants.
- [ClaimDB, ACL 2026](https://aclanthology.org/2026.acl-long.1589/) utilise des données structurées réelles et des vérifications nécessitant des compositions de tables. Il est pertinent pour tester les **preuves calculées** et la provenance d'un résultat numérique. Les tables issues d'une même base n'offrent pas automatiquement des sources indépendantes.
- Pour une mesure de véritables erreurs de vérificateurs, il faudra **deux méthodes de contrôle effectivement exécutées et journallisées**, ainsi qu'un étalon externe. Les données de P5-OBS-03 ne permettent pas d'estimer leurs taux d'erreur.

### Décision scientifique

**ÉTABLI :** 12 PR réelles relues, 36 vues GitHub et 12 listes intégrales archivées ; aucun changement de statut ou de tête observé ; filtre de provenance reproductible ; test de non-indépendance et de conflits fonctionnel.

**RÉFUTÉ dans cet échantillon :** meilleur ordre de lecture propre à Omega : 17 consultations logiques contre 15 pour le contrôle simple à information finale égale.

**INDÉTERMINÉ :** robustesse à des fournisseurs réellement indépendants et faillibles, gains sur des preuves scientifiques, généralisation et avantages propres de l'architecture Omega.

**Ne pas fusionner la PR dans `main` ni promouvoir une supériorité dans la bibliothèque CORE.** La prochaine étape utile est un **corpus externe avec preuves réellement annotées et procédures de vérification variées**, pré-enregistré avant d'ajuster les politiques sur les nouvelles données.
