# P5-ADAPT-01 — pré-enregistrement avant code et résultats

**Date : 12 novembre 2026.** Gel du protocole avant création du code de simulation et tout résultat. Tous les agents sont des politiques numériques, **pas des LLM ni des sous-agents**.

## Question falsifiable

**Omega sait-il modifier sa politique face à des retours observés, détecter une rupture, mémoriser et revenir sur une modification injustifiée, sans information privilégiée ?** Comparaison à des politiques classiques fortes avec le même budget et les mêmes observations. Le candidat est une **extension expérimentale** : le Prisme P1 existant planifie mais n'apprend pas des retours à lui seul. Si le candidat n'améliore pas le meilleur témoin, aucune plus-value n'est démontrée.

Références de l'état de l'art : Garivier et Moulines, *On Upper-Confidence Bound Policies for Switching Bandit Problems*, ALT 2011, https://arxiv.org/abs/0805.3415 ; Liu, Lee et Shroff, *A Change-Detection Based Framework for Piecewise-Stationary Multi-Armed Bandit Problem*, AAAI 2018, https://doi.org/10.1609/aaai.v32i1.11746. Les implémentations ci-dessous sont des **variantes simplifiées**, non des reproductions certifiées du code de ces articles.

## Monde caché, canal de retour et contraintes égales

128 épisodes publics synthétiques : **4 régimes × 32 réalisations**, horizon **180 décisions par épisode**, trois actions `DIRECT`, `VERIFY`, `ABSTAIN`. La probabilité de réponse correcte évolue, **sans que les politiques reçoivent le nom du régime, les probabilités, les instants de changement, les erreurs contrefactuelles ni l'identité de la meilleure action**. Elles ne voient que l'identifiant de l'action choisie, l'instant et le gain réalisé.

Sur chaque pas, `DIRECT`/ `VERIFY` renvoient une réussite ou un échec tiré de SHA-256 d'une clé déterministe commune au pas, à l'action, à l'épisode et au régime ; le contrôleur n'a accès qu'au tirage de son action. `ABSTAIN` renvoie toujours **+0,08**. Une bonne réponse rapporte **+1**, une mauvaise **−2**, et `VERIFY` coûte **0,20** supplémentaire dans les deux cas. Ce sont des **utilités fictives**, pas des euros ni des valeurs calibrées sur un modèle réel. Toute action a le même coût de décision ; ce qui est monétisé abstraitement, c'est la vérification. Les séquences aléatoires contrefactuelles sont identiques entre politiques.

Quatre régimes aux dates cachées :
- `stationary` : état stable, alterné selon la réalisation, 180 pas ;
- `abrupt` : `direct_good` (0–59), `direct_bad` (60–119), `direct_good` (120–179) ;
- `recurrent` : `direct_good` (0–44), `direct_bad` (45–89), `verify_bad` (90–134), `direct_bad` (135–179) ;
- `gradual` : transition continue du profil `direct_good` au profil `direct_bad`.

Profils (probabilités de réponse correcte, `DIRECT`, `VERIFY`) :
`direct_good=(0,92;0,94)`, `direct_bad=(0,32;0,91)`, `verify_bad=(0,76;0,42)`, `both_bad=(0,38;0,40)`. `both_bad` est utilisé dans les épisodes stationnaires d'une réalisation sur quatre pour vérifier l'intérêt d'une abstention.

## Contrôles pré-enregistrés

1. `fixed_direct`, `fixed_verify`, `fixed_abstain` : aucune adaptation.
2. `ucb_stationary` : UCB utilisant tout l'historique ; il apprend sans gérer explicitement les ruptures.
3. `sw_ucb` : UCB à fenêtre glissante 36 décisions (témoin non stationnaire).
4. `discount_ucb` : UCB à récompenses pondérées par `gamma=0,97` (second témoin non stationnaire).
5. `restart_ucb` : UCB avec fenêtre 48 et détecteur de changement fondé sur deux blocs de six retours par action, alarme pour écart de moyenne de module supérieur à **0,80**, repos de 12 décisions, remise à zéro des observations actives (témoin standard fort).
6. `omega_candidate` : réutilise le vrai `planner.plan_mission` pour la planification (sans prétendre qu'il apprend), plus **une extension candidate** : fenêtre stable 48, fenêtre rapide 12 pendant 18 décisions après alarme, mémoire de l'historique pré-alarme, amorçage faible des moyennes à partir de ce souvenir et **retour arrière** vers l'état antérieur si les 18 retours rapides perdent plus de **0,25** de gain moyen relativement aux 18 dernières observations pré-alarme. Aucun accès à l'état caché du monde.
7. Ablations `omega_no_memory` (pas d'amorçage depuis la mémoire) et `omega_no_rollback` (aucune restauration après essai rapide).
8. `dynamic_oracle` : meilleur gain **espéré** au pas d'après les probabilités cachées ; **évaluateur uniquement**, jamais une politique autorisée.

Les variantes UCB utilisent bonus `0,65*sqrt(log(t+2)/n)` calculé sur les récompenses rééchelonnées en [0,1] ; toute action dont le compte effectif est 0 est visitée d'abord. Toutes les égalités se tranchent dans l'ordre fixe `DIRECT,VERIFY,ABSTAIN`. La mémoire d'Omega est une archive de **retours précédemment observés**, non un oracle ; elle ne crée ni réponse, ni données supplémentaires. Toute décision est journalisée avec version de politique et raison de modification.

## Mesures et règles de conclusion

- Primaire : **pseudo-regret dynamique**, somme sur 180 pas de `max_a E[récompense_t(a)] - E[récompense_t(action choisie)]`, calculée **seulement par l'évaluateur après la décision** ; plus faible = mieux.
- Secondaire : utilité réellement reçue, nombre de décisions directes/vérifiées/abstentions, nombre de fausses réponses effectivement commises, coût total de vérification, changements de mode, alarmes, retours arrière, et capacité à choisir la nouvelle action optimale après les ruptures.
- Agréger par régime sur 32 épisodes **appariés**, afficher également différence moyenne et victoires/égalités/défaites vs meilleur témoin classique dans chaque régime. Reporter séparément la performance stationnaire pour éviter d'améliorer l'adaptation au prix de mauvaises performances stables.
- **Falsification** : si l'extension candidate n'est pas meilleure que le meilleur témoin classique sur les régimes changeants, ou si elle se dégrade en stationnaire au-delà du bénéfice, ne pas conclure à un avantage Omega. Aucune déclaration d'innovation sur la base de ces données artificielles.
- Test de fuite : API du contrôleur reçoit uniquement `t`, l'action choisie et son retour. Inverser des probabilités non visibles doit laisser identiques les décisions tant que les historiques observés restent identiques. Tests reproductibles, invariance de l'ordre des politiques, plafonds et trace complète.

## Exécution et limites

Python 3.12 standard library sur GitHub Actions du dépôt public. **0 modèle de langage, 0 API payante, 0 usage du smartphone, 0 accès au holdout privé**. L'expérience est **synthétique et conçue par l'auteur**, sans holdout ni vérification indépendante. P5-ADAPT-01 ne valide ni une intelligence générale, ni la bibliothèque scientifique, ni le système Omega complet. Aucun composant n'est intégré à `main` avant vérification.

Tous les paramètres sont pré-enregistrés avant résultat ; toute correction après les premières données est versionnée et doit être marquée exploratoire.
