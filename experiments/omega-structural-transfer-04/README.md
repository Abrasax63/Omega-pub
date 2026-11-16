# OMEGA-STRUCTURAL-TRANSFER-04 — apprendre mieux, ou seulement plus ?

[**Préenregistrement du 16 novembre 2026, antérieur au code**](PREREG_2026-11-16.md), [commit `1da94d3`](https://github.com/Abrasax63/Omega-pub/commit/1da94d3afb76c27c9300ab7098695b02cc0c71aa).

## Ce que teste exactement ce laboratoire
Il s'agit du **diagnostic actif de l'état initial** (caché) d'une machine de Mealy **dont la table de transitions et de sorties est connue**. Quatre états, deux actions, trois sorties, six probes réinitialisés de longueur 1/2. **Ce n'est PAS l'inférence d'un automate inconnu, ni l'entraînement d'un modèle de langage, ni la construction d'un agent autonome auto-programmable.**

La question est désormais plus sévère que dans la PR #130 : à **nombre égal d'épisodes d'entraînement, un seul label de coût réellement observé par épisode et facture exactement égale**, une collecte guidée par une politique ON transfère-t-elle ses acquis vers **des structures de transition nouvelles**, contre une politique fixe et une mémoire forte ?

## Familles distinctes
- TRAIN_RANDOM : **64 machines**, transitions non constantes et pas deux permutations, seed 21117.
- CONTROL_RANDOM : **20 machines** de la même famille mais jamais entraînées, seed 21118.
- HOLDOUT_PERM : **28 machines**, les deux entrées sont bijectives (permutations), seed 21119.
- HOLDOUT_RESET_CYCLE : **28 machines**, une entrée réinitialise tous les états et l'autre fait un cycle de longueur quatre, seed 21120.

Les deux familles HOLDOUT sont **structurellement absentes** de TRAIN_RANDOM. Les signatures canoniques excluent aussi tout recouvrement avec les **594 machines de #127 à #130**. Impossible = abstention documentée, jamais remplacement motivé par le score.

## Modèles, budget et signaux
Les deux modèles entraînés sont **exactement les mêmes régressions linéaires à neuf paramètres** de la PR #128, taux SGD 0,025. OFF choisit ses probes uniformément ; ON en choisit 80 % du temps selon son modèle actuel, 20 % uniformément (epsilon=0,2). Le modèle voit les mêmes informations courantes sur la machine, mais jamais l'état initial secret. L'oracle exact de #76 ne donne **aucune cible pendant l'entraînement**.

Pour chaque machine TRAIN identifiable et chacun de ses **quatre états**, ON et OFF conduisent **chacun un épisode complet**. Les deux reçoivent **strictement un seul label** : le vecteur des caractéristiques du **premier probe effectivement choisi** et le **coût total réellement observé** de cet épisode. **Une seule mise à jour SGD par épisode**. Aucun autre label, aucune cible sur une action non choisie.

Chaque bras paie **six unités par épisode** : au maximum trois probes informatifs de longueur deux peuvent réduire quatre états à un seul. Les unités non utilisées sont consommées par des **observations réelles** d'un probe unitaire de calibration, **non réutilisées à l'entraînement**. Le rapport sépare :

- `productive_cost` : coût des probes ayant réellement servi au diagnostic.
- `filler_cost` : dépenses de calibration sans apprentissage.
- `charged_cost` : **exactement 6 × épisodes complets**, identique OFF et ON.
- `training_labels`, `completed_episodes` et `updates` : identiques dans les deux bras.

**Précision indispensable :** mêmes nombres d'exemples et même montant payé ne signifient pas égalité de *contenu* informationnel ; les actions observées peuvent différer, et c'est l'intervention étudiée.

Comparateurs :
- **FIXED** : Gini/coût non entraîné.
- **MEMORY_OFF** : mémoire k=7 sur les mêmes premières actions et retours d'OFF.
- **MEMORY_ON** : mémoire k=7 sur les premières actions et retours de ON.
- **OFF** : modèle linéaire entraîné sur retours d'OFF.
- **ON** : modèle linéaire entraîné sur ses propres retours.

## Critère principal conjontif (gelé)
Sur les deux familles HOLDOUT, comparer le coût moyen des quatre états, moyenné sur **trois graines fixes 171,172,173**. Un verdict descriptif favorable ne sera accordé que si **ON bat à la fois FIXED et MEMORY_OFF dans chacune des deux familles**. Les différences ON−OFF et ON−MEMORY_ON restent secondaires. Le code archive **tous les écarts individuels**, y compris les cas où ON perd.

Les trois graines partagent les mêmes machines de test : elles **ne sont pas des expériences de généralisation indépendantes**. Le coût de calcul de la mémoire et celui du petit modèle ne sont pas égalisés ; l'oracle minimax sert seulement de contrôle sur le pire coût, pas de référence d'optimalité de la moyenne.

## Exécution / preuve
```sh
python -m unittest discover -s experiments/omega-structural-transfer-04 -p 'test_structural.py' -v
python experiments/omega-structural-transfer-04/structural_lab.py \
  --output /tmp/omega-structural-transfer-04.json
```

Python 3.11, bibliothèque standard uniquement, sans API ni GPU. La CI impose **15 contrôles** et archive les sorties brutes et leurs empreintes. Cette PR reste **DRAFT**, empilée sur #130, sans modification de `main`, de la mémoire certifiée ni des expériences antérieures. Résultat négatif = résultat scientifique admissible et à conserver.
