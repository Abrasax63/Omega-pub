# P5 — Pré-enregistrement, pilote de preuves externes (11 novembre 2026)

Statut : EXPÉRIMENTAL. Pré-enregistré **avant** lecture de `merged` et de la liste des fichiers des PR sélectionnées. Ce pilote ne teste pas les performances générales d'un LLM, ne constitue pas un holdout secret et ne remplace pas une correction humaine indépendante.

## Question
Sur douze PR de dépôts externes, répondre à : **« Cette PR est-elle déjà fusionnée ET modifie-t-elle au moins un fichier de test ? »**. Une réponse positive n'est permise que si les deux propriétés sont constatées par API GitHub. Les informations de description/titre ne valent pas preuve.

## Échantillon gelé
L'ordre et les identifiants ont été arrêtés avant la collecte des statuts et chemins :
- python/cpython : #154650, #153709, #161726, #153021
- pallets/flask : #5918, #6159, #6151, #6135
- psf/requests : #7082, #7636, #6767, #7025

C'est un échantillon raisonné de 12 PR accessibles, **non représentatif**, partiellement choisi après consultation de titres sur GitHub. Aucun chiffre de performance ne doit être extrapolé.

## Définition préalable de la vérité
- `merged` : booléen de `get_pr_info` GitHub, non `state == closed`.
- `test_changed` : au moins un chemin de `list_pr_changed_filenames` possède un répertoire entier `test` ou `tests`, ou son nom commence par `test_` ou se termine par `_test.py`. Cette définition syntaxique ne garantit pas que des tests exécutables ont changé.
- `accept` si et seulement si `merged && test_changed`; `reject` sinon.
- Contrôle transversal indépendant de l'évaluation : relire les métadonnées par `fetch_pr`, vérifier `merged`, conserver chaque source et le commit head_sha. Les appels n'apportent pas d'indépendance entre fournisseurs : toutes les données viennent de GitHub.

## Bras comparés, budget identique
- A/direct : aucun appel ; prédit `reject` (hypothèse conservatrice explicitée).
- B/fixe : appeler **systématiquement** `get_pr_info` puis `list_pr_changed_filenames`, même si `merged=false`.
- C/Omega : soumettre à `optimize_policy(max_depth=2)` les quatre états théoriques (`merged` × `test_changed`), chacun de poids 1. Deux vérifications `00-merged` et `01-tests` sont disponibles, coût théorique 5 millièmes chacune ; réponse positive uniquement si les deux sont observées. La stratégie conditionnelle attendue demande la liste des fichiers seulement lorsque `merged=true`. Aucun oracle ne fournit la réponse réelle avant interrogation.
- Les bras B et C disposent des mêmes API et d'un plafond de **deux appels** par PR ; A en a zéro. Il est interdit de réutiliser les observations du bras B pour éviter un appel du bras C.
- Toutes les informations sur le monde sont acquises lors d'appels réels. Le planificateur connaît une **structure logique théorique** du problème, pas les douze résultats.

## Mesures, analyse et échecs
- Mesure `Date.now()` autour de chaque appel via le connecteur GitHub, en millisecondes. Ce temps inclut les surcoûts de la couche outil, **pas** seulement la latence de l'API GitHub ; ce n'est ni le coût en euros ni la latence d'un modèle.
- Rapporter l'exactitude de chaque bras, les appels réalisés et les temps mesurés ; ne pas traiter les PR comme des tirages indépendants.
- Consigner les erreurs, les délais, les PR mutées pendant la collecte, les divergences du contrôle `fetch_pr` et les observations non disponibles. En cas d'erreur, `ABSTAIN` et pas d'imputation de zéro.
- B et C visent l'exactitude égale ; l'hypothèse testée est une **économie de consultation conditionnelle**, pas une meilleure qualité scientifique ni un gain d'intelligence générale.
- Pour attribuer un gain propre à Omega, il faudrait ensuite tester des tâches inédites, des observations non parfaites et une référence composée de spécialistes sous budget égal, avec évaluation aveugle par tiers.

## Critères d'arrêt
Après les 12 PR et les contrôles de provenance. Pas d'ajustement post-hoc de l'échantillon, du critère de test ou des coûts théoriques. Pas de promotion scientifique ni de fusion dans main.
