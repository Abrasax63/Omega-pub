# Policy-feedback 02 — apprendre les conséquences de ses propres choix

## Statut
Un seul essai préenregistré au [commit 3a88640](https://github.com/Abrasax63/Omega-pub/commit/3a88640aa947ec7f1de829d8d601578d8eb3263d), avant le code et toute première exécution. PR **DRAFT** empilée sur #128. Ni les scores de #127 ni ceux de #128 ne changent.

## Question
Dans une tâche de diagnostic d'état sur une **machine de Mealy connue**, où seul l'état initial est caché, un petit sélecteur qui apprend sur les **trajectoires qu'il provoque lui-même** fonctionne-t-il mieux qu'un sélecteur identique entraîné sur les trajectoires d'un explorateur uniforme ?

Ce pilote compare une régression en ligne à **9 paramètres** sur le **coût de retour réellement observé**, avec les mêmes 6 probes, la même fonction de coût et la même mise à jour SGD que #128.

- **OFF** : exploration uniformément aléatoire; coût observé de chaque étape donné au régresseur après l'épisode.
- **ON** : au cours de l'entraînement, choisit le probe estimé le moins coûteux selon ses poids courants, sauf avec probabilité `epsilon=0.2` (probe aléatoire). Utilise son propre coût de retour après l'épisode.
- **FIXED** : Gini/coût immuable.
- **MEMORY** : 7 voisins sur les traces réellement observées par OFF, sans poids modifiables.

Les quatre stratégies utilisent la même information sur le système courant et sont évaluées sur exactement les mêmes machines et les quatre états initiaux. OFF/ON traitent le même nombre d'épisodes d'apprentissage, **mais leurs coûts/trajectoires peuvent différer**. Le rapport publie explicitement les coûts de collecte; **pas d'affirmation de budget d'apprentissage égal en symboles ou CPU**.

## Phases A → B → A'
- A : chaque symbole vaut 1 (probe court 1, long 2).
- B : chaque symbole 0 vaut 3, chaque symbole 1 vaut 1 (probes `0=3,1=1,00=6,01=4,10=4,11=2`). Contrairement à #128, les dépenses B dépendent des actions.
- A' : retour à A sur d'autres machines.

TRAIN_A 24, TRAIN_B 24, TRAIN_A' 16 ; EVAL_A 18, EVAL_B 18, EVAL_A' 24 ; trois graines d'exploration 410/411/412. Les machines réservées sont non isomorphes aux entraînements, et aussi aux deux pilotes #127/#128. Les impossibles demeurent dans les dénominateurs mais s'abstiennent.

**Primaire gelé** : moyenne `ON - OFF` en coût d'identification moyen sur EVAL_A', sur trois checkpoints (0,8,16 machines de réapprentissage) et trois graines. Négatif = amélioration descriptive. Nul ou positif = résultat nul ou défavorable. Les graines ne constituent **pas trois tests indépendants** puisque les machines d'évaluation sont identiques.

**Secondaires** : coûts de collecte réellement dépensés et nombre de probes par bras, coût et regret au pire cas contre la borne exacte #76 (oracle d'évaluation seulement), stabilité de la politique sur machines réservées, rétention A, performance B, confrontation à la politique fixe et à la mémoire. Aucun label oracle dans TRAIN.

## Utilisation
```sh
python -m unittest discover -s experiments/omega-policy-feedback-02 -p test_feedback.py -v
python experiments/omega-policy-feedback-02/feedback_lab.py --output /tmp/omega-policy-feedback-02.json
```

Python 3.11, bibliothèque standard, aucun LLM ni API/GPU. GitHub Actions conserve l'intégralité des épisodes, des empreintes, des poids, des comparaisons positives et négatives.

## Limites
Cet essai ne prouve pas l'auto-amélioration d'une intelligence générale. Une différence ON/OFF est confondue par les trajectoires et **les coûts de collecte inégaux**. La machine de Mealy est donnée : seul l'état initial est à découvrir. L'oracle exact ne donne qu'une borne minimax du pire coût, et non un oracle d'optimisation du coût moyen. Les classes de machines sont petites et les graines ne sont pas des réplications indépendantes de holdout. Le résultat reste expérimental et le contrat scientifique n'est jamais réécrit après inspection des scores.
