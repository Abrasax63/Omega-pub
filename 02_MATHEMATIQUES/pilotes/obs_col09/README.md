# OBS-COL-09 — Benchmark sur automates publics externes (AALpy et LearnLib)

**Date :** 2026-11-15. **Statut :** EXPÉRIENCE RÉELLEMENT EXÉCUTÉE, résultats de calcul, **aucun nouveau résultat mathématique ni gain d'intelligence propre à Omega**.
**Branche :** `experiment/obs-col09-external-aalpy-benchmark-2026-11-15` (empilée sur PR #92, pas sur main).

## Pré-enregistrement et corrections méthodologiques

- [Protocole d'origine](PREREG_OBS_COL09.md), commit `2701c24c4b81605e2a619ba1430bed8c6fab6e1c`, avant code.
- [Amendement pré-exécution](AMENDEMENT_PRE_RUN_01.md), commit `d5f6e1dd22c81a656a90b4b95b76cb0b270e93fc` : 256 mots d'évaluation par modèle, longueur 12..18, graine connue, exclusion des mots déjà observés pendant l'apprentissage et les tests d'équivalence. Les mots exclus ne sont pas remplacés sur la base du résultat.
- Fichiers externes **copiés bit pour bit**, source publique de [DES-Lab/AALpy](https://github.com/DES-Lab/AALpy) : `DotModels/Angluin_Moore.dot`, `DotModels/coffee_moore.dot` et `DotModels/mooreModel.dot`. Les blobs Git sont fixés et comparés dans les tests (respectivement `4ed5251c5580b1d115823486083ddc88b3e2a5ce`, `91edc61c18e5624e937b7b7c1c1bf5970432dbfa`, `d494040778647da551ea7131fdc72350041ee76f`). Attribution et licence MIT (AALpy).
- Les modèles viennent d'un **tiers** mais sont **publics**. Ce ne sont pas des données naturelles ni un test externe aveugle ; l'équipe expérimentatrice peut les consulter.
- Dépôt de référence Python : [AALpy](https://github.com/DES-Lab/AALpy), version **2.0.0**. Implémentations **authentiques** `run_Lstar`, `run_KV`, `run_Lsharp`. Références de méthode : Dana Angluin (1987), L* ; Vaandrager et al., L#.
- Dépôt de référence Java : [LearnLib](https://github.com/LearnLib/learnlib), `learnlib-ttt` **0.18.0**, vrai `TTTLearnerMoore` via Maven, AutomataLib 0.12.0, Java 17 ; l'algorithme n'a pas été recréé localement.

## Oracle, politiques et condition d'égalité

Les quatre bras Python AALpy s'exécutent chacun avec le même `RandomWalkEqOracle` (2000 symboles par recherche d'équivalence / étape, `reset_prob=0.12`, `reset_after_cex=True`), `random.seed(20261115+index)`. Le vrai système cible est caché à l'apprenant ; pas d'oracle d'équivalence parfait.

`Lsharp_P1` utilise **exactement le même algorithme L#**, mais interpose le **vrai** `planner.plan_mission` d'Omega avant chaque reset physique. Une empreinte SHA-256 de l'ordre réel des requêtes physiques est comparée à L# pur ; cette empreinte, les actions, resets, hypothèses et prédictions sont identiques. **P1 n'a pas choisi de nouvelles expériences**. Son coût CPU supplémentaire est mesuré, mais trop court pour inférer une valeur stable sur ces trois cas.

TTT Java reçoit les trois mêmes modèles, mais emploie un **simulateur de random walk codé côté Java**, avec la même borne nominale de 2000 pas / probabilité de reset 0.12 et une graine correspondant au numéro de modèle. **Ce n'est pas le même oracle d'équivalence ni la même distribution de parcours** : l'algorithme Java Random diffère du Python Random ; les différences de coûts ne permettent pas de classer TTT par rapport aux bras Python. Les compteurs TTT incluent les resets et actions physiques de l'oracle d'appartenance et de l'oracle d'équivalence. Aucun certificat d'équivalence générale.

## Évaluation identique des modèles finaux

Le générateur [generate_matched_eval.py](generate_matched_eval.py) produit la **même liste de 256 mots par modèle** que `benchmark.evaluation_words`. La suite de tests vérifie leur concordance caractère par caractère après normalisation des symboles numériques (`0,1` entiers dans Python, chaînes dans Java). Les mots sont exportés dans l'artefact du job TTT ; seuls les mots **non vus physiquement** (en tant que préfixe de trace, y compris lors des random walks d'équivalence) sont comptés dans le score `unseen_only`. La prédiction est l'observation du **dernier état** du mot.

## Résultats AALpy — CI externe réellement réussie

[GitHub Actions #43730162347 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43730162347) — **7 tests** Python 3.11 réussis ; douze combinaisons modèle / algorithme exécutées, JSON accessible dans l'artefact `obs-col09-aalpy-external-benchmark-json`.

| Algorithme Python | Resets physiques total (3 modèles) | Symboles physiques total | Erreurs sur échantillons non vus |
|---|---:|---:|---|
| AALpy L* | 832 | 6 366 | 0 sur 765 |
| AALpy KV | 805 | 6 208 | 0 sur 765 |
| AALpy L# | 793 | 6 126 | 0 sur 765 |
| AALpy L# + Omega P1 | 793 | 6 126 | 0 sur 765 |

Sur les trois modèles, les états retrouvés sont 4, 3, 9. La totalité des 12 modèles a zéro erreur sur les séquences non vues dans ce protocole. Aucun gain d'identification ou de sondes d'Omega face à L# ; P1 ajoute un routage explicable et du calcul.

## Résultats LearnLib TTT — CI Java réellement réussie

[GitHub Actions #43730161185 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43730161185) et [job d'origine harmonisée #43730057555](https://github.com/Abrasax63/Omega-pub/actions/runs/43730057555). `TTTLearnerMoore` réel compilé, exécuté et testé avec les **mêmes mots d'évaluation** que Python.

| Modèle tiers | États TTT | Resets physiques TTT | Symboles physiques TTT | Non vus / 256 | Erreurs sur non vus |
|---|---:|---:|---:|---:|---:|
| Angluin Moore | 4 | 270 | 2 060 | 253 | 0 |
| Distributeur de café | 3 | 263 | 2 022 | 255 | 0 |
| Moore à neuf états | 9 | 293 | 2 348 | 255 | 0 |
| **Total** | — | **826** | **6 430** | **763** | **0** |

**Ne PAS conclure « L# est plus performant que TTT » de ces totaux :** le protocole de test d'équivalence Java n'est pas identique à celui de Python et les temps CPU sont mesurés sous deux environnements. Les *entrées d'évaluation finale* sont maintenant harmonisées, pas les trajectoires d'apprentissage.

### Échecs et corrections conservés

Les premiers runs TTT ont échoué :
- compilation initiale : mauvais constructeur `TTTLearnerMoore` (deux arguments au lieu des trois de LearnLib 0.18) ;
- exécution initiale : constructeur `DefaultQuery` ambigu, la trace de sortie était prise pour l'alphabet d'entrée ; correction explicite par constructeur à trois arguments ;
- la première CI de concordance Python/Java des mots a échoué sur une différence de **type** (symboles entiers 0/1 vs chaînes "0"/"1") ; correction du test par normalisation des symboles, sans modification des données de résultats.

Les versions historiques des runs échoués restent consultables ; les corrections ont été relancées et vérifiées. Les fichiers de logs et les manifestes d'entrée figurent dans les artefacts GitHub des exécutions finales.

## Verdict scientifique

**DÉMONTRÉ DANS LE BANC :** les bibliothèques externes sont exécutées réellement ; les 3 cibles publiques sont apprises par les algorithmes testés ; le pont Omega-P1 ne modifie ni les sondes ni les résultats de L# ; l'absence d'erreur sur les mots *non vus* est constatée dans les limites des échantillons.

**NON DÉMONTRÉ :** gain d'intelligence, d'information ou de coût de la part d'Omega, prééminence générale de L#/TTT, certification d'équivalence universelle, passage à une loi naturelle, choix autonome de sondes par Omega. Aucun holdout véritablement aveugle, seulement trois modèles publics ; ce nombre ne permet aucune conclusion générale.

## Reproduction

Python 3.11 (depuis la racine du dépôt, sur cette branche) :

~~~sh
python -m pip install aalpy==2.0.0
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col09 -p 'test_obs_col09.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col09/benchmark.py > obs_col09_result.json
~~~

Java 17 et Maven (voir [.github/workflows/obs-col09-ttt.yml](../../../.github/workflows/obs-col09-ttt.yml) pour la commande CI complète) :

~~~sh
python 02_MATHEMATIQUES/pilotes/obs_col09/generate_matched_eval.py "$PWD/obs_col09_matched_eval"
mvn -B -ntp -f 02_MATHEMATIQUES/pilotes/obs_col09/learnlib_ttt/pom.xml -DskipTests compile
mvn -B -ntp -f 02_MATHEMATIQUES/pilotes/obs_col09/learnlib_ttt/pom.xml exec:java "-Dexec.args=$PWD/02_MATHEMATIQUES/pilotes/obs_col09/external_fixtures $PWD/obs_col09_matched_eval"
~~~

## Prochaine vérification décisive

1. **Harmoniser le même oracle d'équivalence** entre L*, KV, L#, TTT, avec un service d'équivalence déterministe commun et une trace de toutes les requêtes ; compter temps CPU, longueur des sondes et resets.
2. Ajouter des automates de test préparés indépendamment avec engagement cryptographique et protocole aveugle, plus des cas de mémoire longtemps indistinguables ; inclure des répétitions.
3. Seulement ensuite mettre en concurrence une politique Omega réellement distincte, ayant le droit de choisir des sondes selon sa mémoire de contre-exemples, avec ablatives/contrôles à budget égal.

**Gouvernance :** PR DRAFT, aucune fusion automatique, aucune mutation CORE ou `main`.
