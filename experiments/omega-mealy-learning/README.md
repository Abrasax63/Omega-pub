# Laboratoire Mealy — apprentissage actif de la sélection d'expériences

**OMEGA-MEALY-LEARN-01** — [préenregistrement](PREREG_2026-11-16.md), fixé **avant** la première exécution GitHub.

## Périmètre exact et motivation
Une machine de Mealy déterministe à quatre états a une transition et une sortie par symbole d'entrée. Sa table **est connue** de tous les bras. Seul **l'état initial** est inconnu. Chaque expérience est un mot d'entrée de longueur un ou deux et recommence depuis le même état initial ; elle coûte le nombre de symboles d'entrée. L'objectif est de déterminer correctement cet état avec un coût minimal. **Il ne s'agit pas d'inférer une machine inconnue, de réentraîner un LLM ou d'apprendre par renforcement sans supervision**.

Le solveur [PR #76](https://github.com/Abrasax63/Omega-pub/pull/76) fournit un oracle exhaustif du **coût minimax exact** sur les six mots de test disponibles; son code reste inchangé. Les méthodes n'utilisent pas l'oracle pour choisir les expériences sur TEST.

## Les trois bras
- **A (fixe)** : sélection par partition Gini / coût, poids immuables.
- **B (mémoire)** : k=7 plus proches exemples d'actions de TRAIN avec regret oracle (historique en lecture seule), sans modification des poids.
- **C (apprenant)** : une politique linéaire de six paramètres, entraînée par des mises à jour pairwise au fil des exemples d'actions de TRAIN, cinq passages, taux 0,05. Archive les paramètres avant et après et les mises à jour. Le signal de formation vient d'un **oracle exact supervisé** sur TRAIN ; aucune prétention à une auto-construction autonome.

Les trois méthodes voient les **mêmes six probes, la même machine courante et le même ensemble d'états encore possibles**. Le budget de tests est identique ; la consommation de CPU et l'accès à la mémoire ne sont pas égalisés, et cette limite reste explicite. L'évaluation moyenne parcourt les quatre états initiaux possibles pour chaque machine identifiable. Les machines non identifiables restent dans le dénominateur, sans score artificiel.

## Train / validation / test
Trois graines fixes génèrent 40 / 20 / 30 machines respectivement. Une signature canonique calculée sur toutes les permutations de noms d'état écarte tout doublon isomorphe *entre* groupes. Les machines non identifiables ne sont jamais remplacées. Toute préparation des labels d'actions optimales et tout entraînement se font seulement sur TRAIN. VALIDATION est consultée sans mise à jour ; TEST seulement après sauvegarde du modèle. Les scores de TEST sont rapportés sans ajuster les paramètres.

## Statut attendu
L'amélioration primaire est **coût moyen C moins coût moyen B** sur les machines identifiables de TEST, en unités de symboles de probe ; valeur négative = avantage descriptif. Les regrets du pire cas sont contrôlés contre l'oracle. Échec de cet avantage = résultat négatif public. Les valeurs de performance, signatures, changements des poids, cas favorables/défavorables et limitations sont archivés dans `report.json`. Le rapport est une **première falsification**, et ne donne aucune certification de généralisation à ce stade.

## Exécution locale ou CI
```sh
python -m unittest discover -s experiments/omega-mealy-learning -p 'test_mealy_lab.py' -v
python experiments/omega-mealy-learning/mealy_lab.py --output /tmp/omega-mealy-report.json
```

Aucune dépendance Python hors bibliothèque standard. Si GitHub Actions est disponible, l'artefact du run contient le rapport détaillé, l'empreinte SHA256 et les journaux. Aucun réseau ni API payante n'est utilisé par le programme. Aucun accès en écriture à la mémoire scientifique certifiée ; ni modifications de `main` ou de la PR #76.

## Limites et étapes suivantes
Si l'apprentissage du sélecteur ne bat pas la mémoire, ce ne sera pas un « échec de l'IA » général : il peut refléter une mauvaise représentation, une politique trop simple, un enseignant oracle, un petit menu de probes ou une distribution trop homogène. Tout changement d'algorithme et nouveau test constituent une **nouvelle version** avec un nouveau holdout. Les prochaines expériences possibles sont la rétention après changement de distribution, des machines vraiment inconnues à inférer et la mémoire réversible, mais **aucune n'est revendiquée comme implémentée ici**.
