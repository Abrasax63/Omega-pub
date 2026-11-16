# OMEGA-ONPOLICY-CONTINUATION-08 — apprendre les conséquences de ses propres choix

[Préenregistrement 16 novembre 2026, commit 2fee954](https://github.com/Abrasax63/Omega-pub/commit/2fee9541c64ad379060f1a27fceaf8c0e8d87b3a) — créé **avant l'implémentation et les scores**.

## La question

Dans la [PR #134](https://github.com/Abrasax63/Omega-pub/pull/134), nous avons trouvé des contre-exemples exacts : même en connaissant parfaitement le coût futur d'un **explorateur uniforme**, on peut choisir une action sous-optimale pour minimiser le **coût moyen**. Peut-on faire mieux en apprenant plutôt les coûts provoqués par sa **propre politique actuelle** ?

C'est une expérience sur le **diagnostic de l'état initial inconnu d'une machine de Mealy connue** (4 états TRAIN, 4 ou 5 TEST, 2 actions, 3 sorties, 6 probes, reset). Ce n'est **pas** l'apprentissage d'une machine noire, le réentraînement d'un modèle de langage ou une modification autonome du programme.

## Deux apprenants de continuation identiques

**UNIFORM_VALUE** : modèle exact de la [PR #132](https://github.com/Abrasax63/Omega-pub/pull/132) à 7 caractéristiques, SGD 0,025, un seul retour par épisode ; observe des trajectoires de probes uniformément exploratoires. Ses fonctions TRAIN sont importées **sans les modifier**, avec la mémoire kNN et le modèle TOTAL9 pour les autres comparateurs.

**SELF_VALUE** : **même modèle à 7 caractéristiques et même SGD**, mais chaque épisode est provoqué par la politique courante, epsilon-greedy :
- probabilité 20 % : probe informatif au hasard ;
- sinon : probe minimisant **coût immédiat + espérance de continuation prédite** ;
- les poids restent **figés pendant l'épisode** ;
- une fois l'état identifié, le simulateur livre le **coût réellement observé** après le premier probe ; ce retour sert à une seule mise à jour SGD ;
- **aucun label oracle** ni réponse imaginée d'une action non exécutée.

Les deux ont **les mêmes machines TRAIN_RANDOM4 (56, seed 22117), mêmes états initiaux, le même nombre d'épisodes et de labels**. Les graines 361/362/363 pilotent les explorations. Les observations, le coût réellement dépensé et la qualité informationnelle des trajectoires peuvent différer : **ne pas dire budget de collecte égal**. Les poids initiaux sont nuls ; les groupes déjà identifiés (singletons) entraînent des features zéro et peuvent donner une mise à jour sans effet, comptée séparément.

## Nouvelles structures réservées

Les nouvelles signatures canoniques sont distinctes des **1 026 machines des PR #127–#134** et entre cohortes :

| Cohorte | Nombre | Seed | Famille |
|---|---:|---:|---|
| EVAL_RANDOM4 | 26 | 25117 | 4 états, transitions aléatoires restreintes |
| EVAL_PERM5 | 30 | 25118 | 5 états, deux actions bijectives |
| EVAL_RESET5 | 30 | 25119 | 5 états, reset et cycle de longueur 5 |

Conserver les impossibles au dénominateur et l'abstention justifiée ; ne calculer les coûts de politiques que sur les machines identifiables, avec **tous les états initiaux**. Les trois graines partagent les machines TEST, **pas trois holdouts indépendants**.

## Critère principal gelé

Pour un résultat descriptif favorable, SELF_VALUE doit battre **UNIFORM_VALUE, FIXED et MEMORY** en **coût moyen de diagnostic** sur **CHACUNE** des familles PERM5 et RESET5 (tolérance flottante 1e-10). Sinon **NO_SELF_CONTINUATION_ADVANTAGE**.

Les regrets exacts sont rapportés contre le **nouvel optimum mathématique du coût moyen** [PR #133](https://github.com/Abrasax63/Omega-pub/pull/133), en fractions rationnelles, et le pire coût contre l'oracle minimax PR #76. Le taux de probes localement sous-optimaux pour Q* est mesuré **sur toutes les croyances atteignables**, dédoublonnées par machine, puis sur les mêmes machines et les trois graines.

**Comparateurs** : MEAN_EXACT, UNIFORM_EXACT_GREEDY (tous deux évaluation uniquement), FIXED, MEMORY (kNN sur les traces uniformes), TOTAL9, UNIFORM_VALUE et SELF_VALUE.

## Exécution

    python -m unittest discover -s experiments/omega-onpolicy-continuation-08 -p test_onpolicy.py -v
    python experiments/omega-onpolicy-continuation-08/onpolicy_lab.py --output /tmp/onpolicy-08.json

Python 3.11, bibliothèque standard ; **16 contrôles scientifiques** et un workflow GitHub Actions archivant les machines, les coûts réellement observés, les poids, les décisions, les effets favorables/défavorables, les empêchements d'identifiabilité et les empreintes SHA.

**Portée et limites** : l'apprentissage SELF_VALUE provient des trajectoires avec epsilon=0,2 mais la politique évaluée est greedy (epsilon=0), si bien que la distribution d'entraînement ne coïncide pas parfaitement avec le comportement déployé. ON et UNIFORM n'exploitent pas des trajectoires identiques, et leur coût d'apprentissage n'est pas garanti égal. On mesure un pilote fini falsifiable, **pas une généralisation ou une augmentation d'intelligence prouvée**.

La PR reste **DRAFT**, empilée sur #134 ; **main inchangée**, aucun merge et aucune API payante.
