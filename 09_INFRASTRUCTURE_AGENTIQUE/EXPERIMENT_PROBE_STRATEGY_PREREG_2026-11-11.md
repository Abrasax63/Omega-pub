# OMEGA-PROBE-001 — test parallèle de stratégie de vérification, pré-enregistré AVANT score

11 novembre 2026, branche distincte `experiment/adaptive-proof-probe-strategy-2026-11-11`, basée sur #43, sans dépendance à Lean/PR #44.

## Corpus et question

Jeu **synthétique intégralement vérifiable**, gelé au commit `883cbe181bac982b8f30d5128f8f16a0381f79f9` : `prism/probe_strategy_cases_2026-11-11.json`. Quatre scénarios, CAL_12/CAL_30 descriptifs et TEST_12/TEST_60 tenus à l'écart du choix des stratégies, mais **pas un holdout externe ou aveugle**. Monde caché `x` uniforme sur les 60 entiers 0..59. Chaque question et sonde est une congruence `x % m == r` où `m | 60`. Une vérification révèle un booléen vrai/faux et facture le coût entier gelé de la sonde.

Objectif : sélectionner des sondes informatives pour rendre les réponses aux cinq questions **certes à travers tous les mondes encore possibles**. **Ne jamais produire une réponse certaine si les mondes possibles la contredisent.** Ne pas confondre « indéterminé » avec « réfuté ». La distribution uniforme et les relations mathématiques sont **connues de toutes les politiques**, le monde caché ne l'est pas. Les réponses de chaque sonde sont révélées après sa sélection et sont déterministes en fonction du monde.

## Fonction de perte fixée avant simulation

- Coût de vérification : somme des `cost` des sondes effectivement choisies. Une sonde ne peut être utilisée qu'une fois.
- Coût d'abstention terminal : `5 × nombre de questions encore indéterminées` (unités arbitraires). Ne jamais attribuer de coût à une réponse assurément vraie ou fausse ; **aucun faux certificat admis**.
- Comparer l'**espérance exacte sur tous les 60 mondes** de `coûts des sondes + pénalité terminale`, la résolution correcte des questions, le nombre de sondes utilisées et le coût maximal, sans coûts de processeur ou jetons inventés. L'optimisation cherche la moyenne, pas nécessairement la meilleure borne pire cas.
- Les politiques qui arrêtent prématurément peuvent avoir plus d'abstentions, mais **aucun mensonge** : un statut certain ne peut être rendu que si tous les mondes encore possibles donnent le même résultat.

## Bras fixés

1. **ZERO** : arrêt immédiat, sans sondage.
2. **GREEDY1** : horizon 1 ; choisir la sonde qui minimise exactement `coût + espérance du coût d'abstention après cette sonde`, sinon s'arrêter. Égalité : ordre d'index, arrêt préféré en cas d'égalité.
3. **OMEGA_LOOKAHEAD2** : adaptateur expérimental de planification à horizon 2 ; chaque décision minimise exactement `coût + espérance de la meilleure décision à horizon restant 1` (replanification après observation), sinon arrêt. **Pas le planificateur Omega complet** ; aucune mémoire de preuve externe.
4. **FIXED_BEST** : meilleure permutation non adaptative des sondes, trouvée par énumération exhaustive des `n!` ordres. Connaît le modèle complet et peut **arrêter quand continuer dans l'ordre fixe est plus cher en espérance**, ainsi que sauter gratuitement une sonde qui ne sépare aucun des mondes possibles. Ne peut pas choisir une prochaine sonde différente selon le résultat observé. Ce concurrent fort est optimisé *avant* que le monde soit révélé ; ses coûts de planification hors ligne ne sont pas inclus dans la métrique de sondes, comme pour les autres politiques.
5. **ADAPTIVE_DP_EXACT** : optimum adaptatif global calculé par programmation dynamique exhaustive sur les ensembles de mondes et toutes sondes restantes. Baseline forte **réalisable** car le modèle mathématique est entièrement donné, **pas un oracle qui connaît le monde caché**. Les méthodes moins puissantes ne doivent pas s'attribuer sa supériorité.

Toutes les décisions sont déterministes, les prévisions sont calculées **ex ante** à partir de modèles connus, jamais de l'identité du monde dans la simulation. Le registre des 60 mondes × 4 cas × bras permettra de reconstruire les décisions.

## Double voie et arrêts

- Calcul principal Python : représentations par masques de 60 bits ; espérance calculée par sommes de pertes entières pondérées par le nombre de mondes, **pas par flottants**. Programmation dynamique d'horizon 1, 2 et complet. La borne d'arrêt est `5×nombre d'indéterminations×nombre de mondes`.
- Voie indépendante JS/Node : énumération des mondes, des réponses de sondes, vérification de **toutes les décisions prises** et de la validité des certificats ; recalcul indépendant des valeurs de chaque politique ou d'une stratégie témoin. Toute divergence entraîne échec CI.
- Invariants : `ADAPTIVE_DP_EXACT <= OMEGA_LOOKAHEAD2` ; `ADAPTIVE_DP_EXACT <= FIXED_BEST` ; `ADAPTIVE_DP_EXACT <= GREEDY1` ; `OMEGA_LOOKAHEAD2 <= GREEDY1` **à l'état initial**, en raison de l'horizon plus large. Toutes les politiques doivent éviter les fausses conclusions.
- Contre-tests : aucun gain possible sans information ; parité/CRT ; égalités de choix ; cas où une première sonde n'a pas d'effet immédiat mais une paire a de la valeur ; aucune sonde deux fois ; invalidité de modulo, coût, identité du monde hors domaine ; invariance à la permutation des mondes.

**Verdict :** les fonctions de sélection de sondes sont une famille classique de décision bayésienne / design expérimental. L'amélioration éventuelle d'une recherche à horizon 2 sur greedy ne démontre **aucune innovation propre à Omega** si elle est égalée ou dépassée par FIXED_BEST ou ADAPTIVE_DP_EXACT. Même la réussite de toutes les comparaisons sur ce corpus **ne constitue pas un gain sur des recherches réelles** ou des preuves scientifiques indépendantes.

## Gouvernance

Publier les résultats, y compris négatifs. Pas de modification de #44, pas de fusion `main`, pas d'écriture CORE/SQLite, pas de prétention de preuve Lean. Le précédent programme de validation Lean sera réexaminé séparément lorsqu'un véritable résultat de noyau sera accessible.
