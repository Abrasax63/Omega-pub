# OBS-COL-05 — Audit de changement de représentation sur dynamique inconnue

**Version :** 0.1, 2026-11-15.
**Statut scientifique :** CALCUL EXACT, EXPÉRIMENTAL ; originalité scientifique NON REVENDIQUÉE.
**Base :** PR #87, branche \`experiment/obs-col04-active-constraint-discovery-2026-11-15\`.
**Pré-enregistrement :** [PREREG_OBS_COL05.md](PREREG_OBS_COL05.md), commit \`c9919f2d3468ca4b450d6a1b8ed4844957a5154d\` avant tout code du pilote.

## Hypothèse et mécanisme testé

À partir de transitions observées dans des systèmes de 5 bits à interactions
locales dépendant de l'état, peut-on détecter une incompatibilité avec une
représentation affine, élargir la classe des expressions à des monômes
quadratiques/cubiques et reconnaître les limites d'extrapolation ?

Le module expérimental \`obs_col05.py\` reçoit une interface de consultations
d'un système inconnu. Chaque consultation donne \`(état, action, état suivant)\`.
Aucune règle du système caché ni sa classe nominale ne sont transmises au
module d'inférence. Cependant toutes les formules du générateur sont visibles
dans le même dépôt pour permettre l'audit : il ne s'agit **pas** d'un
holdout externe véritablement aveugle.

La méthode mathématique est **classique et imposée par le concepteur** :
recherche de bases algébriques ANF sur GF(2), degré 1 puis 2 puis 3,
élimination de Gauss exacte et sélection des sondes par accroissement de
rang du dictionnaire de monômes cubiques. P1 reçoit chaque proposition
d'intervention et vérifie son contrat ; **P1 ne choisit pas les sondes**.
La fonction Walsh de PR #86 est réutilisée telle quelle pour documenter les
invariants linéaires apparents dans les données d'entraînement.

Un analogue classique à degré 3 fixé constitue la **baseline forte** ;
un modèle affine fixé constitue le contrôle inférieur. Les trois méthodes
utilisent les **mêmes 26 transitions d'entraînement par action** et les mêmes
6 transitions réservées par action. Toute incompatibilité hors échantillon
conduit à \`OUT_OF_FAMILY_WARNING\` ; aucune correction n'est effectuée avec
les données réservées.

## Résultats vérifiés

**[GitHub Actions #43714972901 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43714972901)**,
Python 3.11, 10/10 tests réussis et
[artefact JSON original](https://github.com/Abrasax63/Omega-pub/actions/runs/43714972901/artifacts/14162181293).

Une première CI [#43714918100](https://github.com/Abrasax63/Omega-pub/actions/runs/43714918100)
a échoué : un test exigeait un ordre numérique alors que le sélecteur
utilise le poids de Hamming. Le test a été corrigé au commit
\`8845db82481f32fe935b763ff5308f7cb8037c7a\`, sans modification du
sélecteur ni des résultats scientifiques. Cette CI a ensuite réussi.

| Monde | Degrés retenus (pulse, bind) | Succès holdout | Affine fixé | Degré 3 fixé | Statut |
|---|---|---:|---:|---:|---|
| Affine | 1,1 | 12/12 | 12/12 | 12/12 | Compatible sur les 12 tests |
| Quadratique | 2,2 | 12/12 | 0/12 (inconsistant) | 12/12 | Promotion au degré 2 |
| Cubique | 3,3 | 12/12 | 0/12 (inconsistant) | 12/12 | Promotions aux degrés 2 puis 3 |
| Quartique hors famille | 2,2 | 10/12 | 0/12 (inconsistant) | 10/12 | **Avertissement OOD** |

Les deux échecs du cas quartique ont lieu sous \`pulse\` aux états 15 et 31.
La règle quartique y modifie un bit que les monômes de degré <=3 ne peuvent
prédire après entraînement sur des états de poids <=3.

**208 véritables appels au module Omega P1** (52 vérifications planifiées
par monde), **208 consultations de l'oracle synthétique** (52 par monde),
0 modèle externe, 0 dépense de jetons API. L'évaluation réservée réalise
12 consultations *supplémentaires* de vérité terrain par monde pour noter
les prédictions ; elles ne participent ni au choix des sondes ni au fit.
Les coûts sont exprimés en nombre de consultations, pas en euros.

## Verdict et limites

- **DÉMONTRABLE sur ces exemples :** l'élargissement algébrique répare
  certaines incompatibilités exactes de représentation ; le modèle doit
  s'abstenir de revendiquer une loi universelle quand une prédiction réservée
  échoue.
- **NON DÉMONTRÉ :** gain d'intelligence propre à Omega, recherche autonome
  de nouvelles opérations mathématiques, découverte de lois physiques,
  gain de données face au solveur classique fort. La baseline degré 3
  atteint les mêmes scores à budget égal.
- **Le jeu est conçu par l'auteur**, les familles (affine/degré 2/degré 3)
  sont prescrites ; les règles cachées n'appartiennent pas à un espace
  réellement ouvert. Le quatrième cas vient d'un générateur de degré 4
  volontairement hors capacité et ne prouve pas la détection de toutes les
  anomalies hors famille.
- **L'observabilité physique réelle n'est pas modélisée** : l'oracle permet
  des interventions parfaites sur des états de départ contrôlés. Aucune
  sélection libre d'observateur, aucun apprentissage de causalité à partir de
  seules données passives, aucune interaction avec le monde naturel.
- **Aucune promotion CORE, aucune fusion de PR, aucun changement sur main.**

## Reproduction

~~~bash
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col05 -p 'test_obs_col05.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col05/obs_col05.py > obs_col05_result.json
~~~

## Prochain verrou réellement décisif

Au lieu de fournir une liste de degrés mathématiques dans l'ordre, tester
une **bibliothèque concurrente de représentations** sans indiquer laquelle
contient la règle, comprenant des familles non polynomiales, des modèles
avec mémoire d'état et des interactions collectives d'ordre supérieur.
Avant chaque mesure, enregistrer l'engagement des modèles et les sondes.
Réserver la vérité terrain à un évaluateur indépendant. Comparer Omega
au meilleur algorithme d'identification de système / active learning avec
même accès, mêmes actions et mêmes budgets. En cas de résultat identique
à la baseline forte, rapporter **absence de plus-value démontrée**.
