# P5-OBS-03 — pré-enregistrement d'un contrôle empirique de provenance

**12 novembre 2026 — consigné avant la nouvelle lecture des 12 PR externes.**

## Objectif

Déterminer ce que nos archives permettent **effectivement** de savoir sur l'origine et la dépendance des preuves. Tester la fraîcheur d'un **ancien instantané de données réelles** contre de nouvelles lectures. **Ne pas** substituer des fixtures synthétiques à des défaillances réelles de fournisseurs ; ne pas présenter deux endpoints GitHub comme indépendants.

## Échantillon historique fixe

Reprendre strictement les douze PR préenregistrées dans [le pilote #29](EXPERIMENT_LIVE_GITHUB_PR_GATE_PREREG_2026-11-11.md) : `python/cpython` #154650, #153709, #161726, #153021 ; `pallets/flask` #5918, #6159, #6151, #6135 ; `psf/requests` #7082, #7636, #6767, #7025. Instantané initial du 11 novembre dans `prism/live_github_pr_gate_observations_2026-11-11.json`, **déjà analysé**, donc ce test n'est **pas** un holdout.

## Nouvelle acquisition externe, autorisée uniquement APRÈS pré-enregistrement

Pour chaque PR, appeler 3 actions **réelles** :
- `get_pr_info` : `merged`, `state`, `head_sha`, `updated_at`.
- `list_pr_changed_filenames` : l'ensemble des chemins de fichiers ; cible syntaxique si un composant de chemin est exactement `test` ou `tests`, si le basename commence par `test_` ou finit par `_test.py`.
- `fetch_pr` : second chemin de consultation pour l'état `merged`, la tête SHA et le nombre PR, **même fournisseur GitHub** ; ne comparer que si ces champs sont disponibles, noter sinon `missing`. Le diff n'est pas un deuxième fournisseur indépendant.

Enregistrer **la vérité de l'instant observé** : `merged && touched_tests`, jamais le statut fermé seul ; conserver les 36 tentatives réelles, les éventuels échecs d'accès, la date `2026-11-12`, URL et identifiant de PR. Ne pas utiliser de titre pour inférer `touched_tests`. Ne pas attribuer une divergence ancienne/nouvelle à une faute de vérificateur si la PR a changé dans l'intervalle. Les lectures successives peuvent également souffrir d'une course, signaler `head_sha` différents.

## Audit de provenance prévu

Construire le graphe de provenance par fournisseur canonique :
- `get_pr_info`, `list_pr_changed_filenames`, `fetch_pr` ont `provider=github.com`. Trois appels ne font **qu'une origine fournisseur**, même si les endpoints ou chemins diffèrent.
- Deux observations du même champ, même provider et même état de référence ne constituent pas de corroboration indépendante.
- Une preuve dont le champ n'est pas directement fourni (ex. `touched_tests` inféré d'un titre) est rejetée ; `UNKNOWN` si un champ nécessaire manque.
- Si les chemins sont issus d'une tête différente de celle citée pour le verdict, marquer `CROSS_SNAPSHOT_UNCERTAIN`, pas certifier.
- Réaliser les contrôles conditionnels `merged-first` et `files-first` sur les données **déjà acquises** ; compter les appels **théoriques de rejeu**, pas des requêtes effectivement évitées. Inclure `fixed-both` et `reject-all`. Le meilleur ordre sur ces 12 lignes peut être post-hoc, pas une contribution Omega.

## Critères, limites et arrêt

1. Aucun succès scientifique si le nombre de fournisseurs indépendants est 1, même avec 100 % d'accord entre méthodes GitHub.
2. Rapporter statuts actuels des 12 PR et modifications depuis le 11 novembre, ainsi que nombres de lectures réussies, indisponibles et contradictoires.
3. Les statuts évoluent ; la capture n'est pas un instantané transactionnel. Les erreurs de source ou de fiabilité ne sont pas observables sans tiers externe indépendant.
4. Vérifier le code par tests Python standard et conservation d'un manifeste JSON déterministe. Exposer les métriques sans les promettre avant exécution.
5. Prospectives documentées : [FEVEROUS](https://fever.ai/dataset/feverous.html) fournit des ensembles de preuves textuelles et tabulaires annotées ; [ClaimDB (ACL 2026)](https://aclanthology.org/2026.acl-long.1589/) fournit des données structurées réelles. **Ces jeux décrivent des preuves annotées, pas automatiquement des défaillances indépendantes de vérificateurs.** Collecte et licences à auditer séparément.

**Aucune nouvelle génération LLM, aucune API payante, pas de modification de `main` ou des PR #47–58. PR DRAFT ; pas de promotion du résultat dans CORE.**
