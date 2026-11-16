# OBS-COL-12 — Amendement APRÈS le premier run : ablation de la mémoire

**16 novembre 2026. Amendement créé après observation du run initial [#43841235628](https://github.com/Abrasax63/Omega-pub/actions/runs/43841235628).** Il ne modifie pas rétrospectivement l'expérience pré-enregistrée, ni son interprétation. Les données du premier run sont conservées et ses résultats sont **calibration publique, non aveugle**.

Le premier run compare W/Wp aux sondes Wp réordonnées par la fonction classique `coverage_ranking` avec couverture du graphe hypothétique **et** mémoire des préfixes déjà visités. Un écart favorable vis-à-vis de W/Wp naturel ne prouve pas que la **mémoire** soit la cause de cet écart : la couverture du graphe peut suffire.

## Nouvelle comparaison causale, explicitement post hoc

Ajouter exactement un quatrième bras `Wp_coverage_ranked` :
- même générateur Wp AALpy, mêmes hypothèses gelées, mêmes sources, mêmes budgets, mêmes préfixes mesurés disponibles que `Wp_memory_ranked` ;
- **seule différence** : passer `memory=False` à la fonction `coverage_ranking` déjà figée en PR #110. Tous les autres facteurs, y compris le vrai routage P1, doivent être identiques ;
- conserver les empreintes SHA-256 du catalogue Wp proposé et de la permutation effectivement choisie ;
- mêmes contrôles de coût, de preuve du contre-exemple par observation et d'absence de certification en cas de silence.

## Hypothèses à départager

Si `Wp_memory_ranked` et `Wp_coverage_ranked` trouvent le même témoin au même coût : **aucun gain causal de mémoire démontré**. Si les coûts diffèrent, indiquer le signe et le compromis resets/symboles/CPU, sans attribuer un gain général sur un jeu réutilisé après inspection.

Ce quatrième bras ne transforme pas la CI du premier run en benchmark aveugle. Le résultat de première date reste un fait historique, pas une prévision. Aucun changement de `main`, CORE, PR #114 ni politique originale.
