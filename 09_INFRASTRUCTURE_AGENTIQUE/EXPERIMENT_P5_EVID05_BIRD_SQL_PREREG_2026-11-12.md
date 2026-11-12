# P5-EVID-05 — pré-enregistrement : premiers témoins SQL authentiques pour ClaimDB

**12 novembre 2026 — ce protocole est enregistré avant de télécharger, d'ouvrir ou d'exécuter la base BIRD SQLite sélectionnée.** Les étiquettes ClaimDB de ces exemples sont publiques et déjà connues ; **ce test n'est pas un holdout aveugle**.

## Objectif et sources épinglées

Réaliser enfin un contrôle SQL sur une **base BIRD existante et non synthétique**, correspondant à des affirmations réelles ClaimDB. Il s'agit d'une **étude de faisabilité** du certificat d'observabilité/provenance, et non d'une comparaison indépendante des performances d'Omega.

- Source des affirmations : Theologitis et al., ClaimDB, ACL 2026, https://aclanthology.org/2026.acl-long.1589/ ; [fichier public original](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl), commit `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`, Git blob `a017545623508c0090cf2148716b8d26a6f8c337`.
- Source du fichier SQLite BIRD `superhero` : [copie publique avec base réelle dans Tarzanagh/QAFD-RAG](https://github.com/Tarzanagh/QAFD-RAG/tree/2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef/data/text2sql/bird/databases/superhero), commit `2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef`, Git blob attendu `4cfbee0ba8b6033a7415184caff90d363fe444c2`, taille attendue **237 568 octets**. Comparaison supplémentaire attendue avec l'empreinte SHA-256 publiée pour une autre copie BIRD : `75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1`. **Si les empreintes diffèrent, ARRÊTER plutôt que substituer silencieusement une version.**
- Aucune base binaire ne sera ajoutée au dépôt : téléchargement uniquement dans le runner GitHub, suppression à la fin, conservation des **empreintes et du journal des résultats SQL**, pas des données brutes. Le statut de licence/redistribution de BIRD et de ses miroirs doit être distingué des annotations ClaimDB, publiées CC BY-SA 4.0. **Ne pas redistribuer de BIRD SQLite sans licence confirmée.**
- Les deux sources (ClaimDB pour étiquettes et BIRD pour tables) peuvent dériver des mêmes auteurs/jeux BIRD ; elles ne sont pas nécessairement des **preuves indépendantes** de qualité de données.

## Cohorte fixée AVANT toute requête SQL

Sélection ciblée **de cinq affirmations ClaimDB sur la base `superhero`**, avec étiquettes publiques **réservées au correcteur** :
- `4267` (ENTAILED) : « At least one blue-haired male superhero is a Mutant. » Tester `EXISTS` sous jointures `superhero,gender,colour,race`, couleurs et catégories littérales **Male / Blue / Mutant**.
- `4179` (CONTRADICTED) : « There were no superheroes without a publisher; every character in the dataset is associated with a publisher. » Chercher un contre-exemple à la totalité : `publisher_id IS NULL` ou clé étrangère manquante ou éditeur vide/`N/A`/`Unknown`/`None`. Cette notion de « without a publisher » est une **interprétation explicite non validée par les auteurs** ; signaler toute discordance sans retoucher cette interprétation a posteriori.
- `4324` (ENTAILED) : « In Marvel Comics, 111 superheroes are identified as female. » Vérifier `COUNT(*) = 111` après restriction éditeur `Marvel Comics` et genre `Female` ; sauvegarder aussi le dénombrement obtenu.
- `3930` (CONTRADICTED) : « There is no human superhero who stands 185 cm tall, so no hair color can be provided. » Tester seulement l'existence d'un **Human** de taille **185 cm** : si un témoin existe, ce sous-énoncé universel est réfuté ; si aucun n'existe, on **NE CONCLUT PAS** automatiquement que la clause causale sur les cheveux est établie.
- `4419` (NOT ENOUGH INFO / COUNTERFACTUAL) : « If publishers were to retroactively rename ... John ... » : pas de calcul SQL suffisant pour cet hypothétique ; verdict opérationnel **ABSTAIN_UNOBSERVABLE_COUNTERFACTUAL**, sans utiliser son étiquette comme justification.

Ces IDs ont été choisis manuellement après lecture des **textes et labels publics**, avant ouverture de la base et avant calcul. Aucun score inférentiel, pas de sélection aléatoire ni de validation indépendante. **Ne pas élargir le jeu sur la base des résultats.**

## Deux calculs + témoin par affirmation

Pour chaque affirmation testable, exécuter deux SQL de sens équivalent définis dans le script avant le premier run :
1. une version `JOIN + EXISTS/COUNT` ;
2. une version `IN/NOT EXISTS/subquery` sans la même organisation de jointures.

Évaluer un prédicat booléen lié à l'affirmation ; les requêtes ne voient **pas** le label. Avant d'accorder le statut `EXECUTED_SINGLE_DB_TWO_SQL_METHODS` :
- vérifier SHA-256 ET SHA-1 git blob du fichier, taille, présence des dix tables attendues, noms des colonnes/relations ;
- mode SQLite **lecture seule** et `PRAGMA query_only`, enregistrement des SQL, des résumés de résultats, de la version SQLite, du chemin provenance et des empreintes ;
- vérifier que les deux résultats correspondent exactement ; si non, `METHOD_CONFLICT` et abstention ;
- vérifier qu'au moins une ligne témoin existe pour les assertions existentielles positives ; sinon ne pas déclarer témoin positif ;
- enregistrer le **statut de revue sémantique** `author_predefined_not_independently_reviewed` : les requêtes sont rédigées par le même opérateur, leur correspondance à l'énoncé naturel n'est **pas certifiée indépendamment**.

Pour les propositions composées ou contrefactuelles, distinguer **réfuter une clause explicite** de **prouver la totalité du texte**, et ne jamais attribuer `ENTAILED` au second si la seule clause mesurée est vraie.

## Politiques à comparer sur les mêmes preuves

- `claimdb_annotation_oracle` : afficher l'étiquette publiée par les auteurs uniquement comme **référence exogène**, **non comme réponse calculée par Omega**.
- `single_sql_method` : décider sur le premier résultat brut, sans demander corroboration (témoin faible, même DB).
- `two_sql_agreement` : décider seulement si deux requêtes SQL concordent ; sinon abstention (contrôle classique fort).
- `omega_provenance_gate` : même règle de concordance + empreinte source, statut de provenance, faisabilité du témoin, précaution sur clause composée ; ne peut pas légitimement s'annoncer indépendant, et **aucun gain propre à Omega ne doit être annoncé** si égal au contrôle `two_sql_agreement`.

Métriques : nombre de cas exécutés vs abstentions, concordance avec les étiquettes du dataset sur les seuls cas calculables, conflits de méthode, témoins concrets, anomalies de version, nombre de fournisseurs **= 1**, annotation des limites sémantiques. **Une étiquette publique n'est pas une preuve indépendante ni un prédicteur autorisé.**

## Arrêts et conditions d'échec

- Source binaire inaccessible ou empreinte différente : **STOP_SOURCE_UNVERIFIED** avec journal ; aucun verdict SQL.
- Schéma différent ou requête SQL invalide : **STOP_SCHEMA_OR_QUERY_MISMATCH** avec journal ; aucune interpolation ni correction rétroactive. Corriger seulement dans une nouvelle version explicitement amendée.
- Aucun témoin positif réexécutable : abstention ; ne pas inventer de ligne.
- Si l'on ne peut reproduire qu'une affirmation, **ne pas prétendre à une validation du jeu entier**.
- Deux lectures sur la même base ne créent ni deux origines fournisseurs ni deux vérités indépendantes.

## Exécution

GitHub Actions Python 3.12, SQLite intégré, temps limité, sans API LLM payante, sans puissance du téléphone ni donnée privée. Artefact JSON de provenance sans DB. Statut `REAL_BIRD_SQL_REPLAY_EXPLORATORY_SINGLE_PROVIDER`. PR en brouillon sur la branche dérivée de #61, `main` inchangée, aucune promotion CORE ni fusion avant audit.
