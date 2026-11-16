# OMEGA-BELIEF-VALUE-05 — apprendre la valeur d'une observation, pas seulement son prix

Protocole [préenregistré au commit `c6c2c40`](https://github.com/Abrasax63/Omega-pub/commit/c6c2c40f49662b04fbbd9f1525bfccb186c8db73), **avant l'implémentation**. Aucun ancien résultat des PR #127–#131 n'est modifié.

## Pourquoi
La [PR #131](https://github.com/Abrasax63/Omega-pub/pull/131) a montré qu'une politique linéaire, entraînée sur ses propres choix avec exactement autant de retours et autant de budget qu'une référence, **se détériore sur des machines structurées inédites**. L'hypothèse de travail est qu'apprendre le coût total depuis un premier probe ne suffit pas : il faut savoir valoriser les **états qui restent possibles après ce probe**. On teste cette idée sans trafiquer les observations ou les références fortes.

## Problème borné
Machines de Mealy **connues**, deux entrées, trois sorties, avec **état initial caché** et remise à l'état initial avant chaque probe. Six mots autorisés (`0,1,00,01,10,11`), coût de chaque mot = longueur. **Ce laboratoire ne fait pas de découverte de modèles de Mealy complètement inconnus, de réentraînement d'un LLM ni d'auto-amélioration du code.**

## Même expérience pour les deux apprenants
Une seule collecte uniforme exécutée réellement sur **56 machines TRAIN_RANDOM4**, quatre états cachés par machine identifiable. Chaque épisode fournit une ligne brute :
- premier probe choisi et sa sortie **effectivement observée** ;
- groupe d'hypothèses avant et après, obtenu avec la table connue ;
- coût total **effectivement payé** pour identifier l'état.

Le fichier de résultats conserve les trajectoires. Les deux modèles voient **le même jeu brut**, les mêmes observations et le même montant d'observations dépensées — il n'y a **qu'un seul collecteur commun**. Une seule mise à jour SGD par épisode pour chaque modèle, au taux **0,025**, erreur plafonnée à ±10.

- **TOTAL9** : régression linéaire historique à neuf caractéristiques prédisant le **coût total observé**, à partir des caractéristiques du premier probe.
- **BELIEF_VALUE** : régression linéaire à sept caractéristiques prédisant le **coût restant observé** après le premier probe, à partir des propriétés du sous-ensemble d'états encore possibles ; au moment du choix, estime `prix du probe + somme(probabilité d'une sortie × prédiction de continuation)`. Les probabilités proviennent des partitions **connues** de la machine, pas d'un oracle de décisions. Un ensemble singleton vaut zéro.
- **FIXED** : politique déterministe Gini/coût.
- **MEMORY** : mémoire kNN k=7 des premières actions et retours observés **dans le même corpus brut**.

L'intervention compare **deux représentations et leurs cibles d'apprentissage**, non une nouvelle architecture de réseau, et pas une différence de budget ou de données.

## Véritable transfert structurel
- TRAIN_RANDOM4 : 56 machines à 4 états et transitions non constantes, pas deux permutations (seed 22117).
- EVAL_CONTROL4 : 20 machines de même famille jamais entraînées (seed 22118).
- EVAL_HOLDOUT_PERM5 : **24 machines à 5 états**, deux entrées permutations (seed 22119).
- EVAL_HOLDOUT_RESET5 : **24 machines à 5 états**, une entrée constante et l'autre un cycle de longueur cinq (seed 22120).

Toutes les signatures canoniques sont disjointes entre groupes et avec les **734 machines antérieures des PR #127–#131**. Les impossibles restent comptés avec abstention ; seul le sous-ensemble identifiable est utilisé dans le calcul des coûts.

Graines de collecte fixe **271/272/273** — mêmes machines de TRAIN et TEST pour les trois, donc pas de fausses réplications indépendantes.

## Verdict scientifique gelé
**BELIEF_VALUE doit battre simultanément TOTAL9, FIXED et MEMORY sur chacune des deux familles 5-états** après moyenne sur trois graines et tous les états initiaux. Sinon verdict négatif **`NO_BELIEF_VALUE_STRONG_TRANSFER`**. Écarts individuels, régressions, regret du pire coût selon l'oracle minimax de la [PR #76](https://github.com/Abrasax63/Omega-pub/pull/76) et cohortes non identifiables restent visibles dans `report.json`.

L'oracle exact est utilisé **seulement pendant l'évaluation**, jamais pour choisir les expériences d'entraînement ni pour fournir une cible. Son optimum concerne le **pire coût**, pas le coût moyen. La moyenne positive ou négative sur un seul petit holdout n'est **pas une démonstration de capacité générale**.

## Exécution
```sh
python -m unittest discover -s experiments/omega-belief-value-05 -p test_belief_value.py -v
python experiments/omega-belief-value-05/belief_value_lab.py --output /tmp/omega-belief-value-report.json
```

Python 3.11, bibliothèque standard seule ; sans API payante, GPU ou modèle externe. GitHub Actions impose **15 contrôles scientifiques**, exécute le protocole unique, archive les sorties complètes, les empreintes SHA256 et les résultats négatifs. **PR DRAFT empilée sur #131, pas de modification de `main`, CORE ni PR précédentes.**
