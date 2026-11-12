# P5-REAL-03 — Pré-enregistrement : notation sémantique gelée et adaptation réellement contrôlée

**12 novembre 2026. Ce protocole est enregistré AVANT toute génération REAL-03, tout code de notation REAL-03 et toute observation de résultats REAL-03.**

## Origine et hypothèse

L'expérience P5-REAL-02, [PR #54](https://github.com/Abrasax63/Omega-pub/pull/54), a démontré qu'un parseur trop littéral pouvait rejeter 16 réponses `Équipe A/B`, et que le mécanisme d'alarme candidat n'avait changé aucune décision. **Hypothèse testée :** un parseur fixé avant l'inférence, suivi d'un contrôleur de changement fondé uniquement sur les vérifications qu'il décide d'exécuter, améliore-t-il l'utilité réellement obtenue à budget égal contre des estimateurs classiques statiques, cumulés, décotés et à fenêtre glissante ?

Un progrès d'extraction ne doit jamais être présenté comme un progrès de raisonnement. Une alarme ne constitue pas en elle-même une amélioration. Une comparaison contre un seul témoin faible ne suffit pas.

## Préparation du parseur et séparation

Le jeu **REAL-02 est autorisé exclusivement pour la CONCEPTION du parseur et des tests de formes** : `A`, `B`, `Équipe A`, `Equipe B avec ...`, `Oui.`, `Non, elle n'est pas injective.`, entiers seuls ou précédés de `Réponse :`. Normaliser accents et majuscules ; accepter des réponses seulement si elles correspondent au **type** demandé ; ne pas chercher une réponse en utilisant la solution exacte. Rejeter les formulations ambiguës ou contradictoires ; conserver le texte brut et un motif de refus.

**Toute modification du parseur après la première génération REAL-03 devra créer un protocole distinct, pas recalculer les chiffres primaires.** Les métriques et tests sur REAL-02 sont de la calibration rétrospective déclarée ; aucune revendication de holdout.

## Jeu et modèles

**96 nouvelles générations**, dont 32 calibration + 64 test, `Qwen/Qwen2.5-0.5B-Instruct` révision gelée `7ae557604adf67be50417f59c2c2f167def9a775` et `Qwen/Qwen2.5-1.5B-Instruct` révision gelée `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. Greedy, max 56 tokens. Questions publiques nouvelles à quatre familles (`MUL`, `CRT`, `RATE`, `INJ`) et une fonction de dérivation indépendante `SHA256(P5REAL03|famille|index|champ)`. 80 questions textuellement et mathématiquement distinctes, vérifiées avant les appels modèle.

Calibration : indices 0–3/famille × 2 modèles = 32 générations. Test : 64 questions jamais vues en calibration, divisées en quatre phases de 16 (`1,5B → 0,5B → 1,5B → 0,5B`), quatre familles par phase et quatre cas/famille ; aucune question répétée. La phase/modèle n'est **pas exposée au contrôleur**, seulement au correcteur. Le texte d'une réponse peut fournir des indices indirects, et cela reste une limite. Ne jamais modifier l'ordre ni sélectionner des sorties après observation.

## Vérification et égalité d'information

Chaque famille a deux calculs exacts indépendants, comme dans REAL-02 : référence (MUL produit natif ; CRT inverse modulaire ; RATE Fraction ; INJ cardinalité image), outil (MUL sommes répétées ; CRT brute force ; RATE produits croisés ; INJ collisions paire à paire). Vérification effectivement réalisée uniquement si le contrôleur paie `VERIFY` ; la vérité des autres sorties reste exclusivement dans l'évaluateur. Les 32 références de calibration sont communes et accessibles à tous les contrôleurs. Aucun feedback gratuit de vérité sur `DIRECT` ou `ABSTAIN`.

**Crédit progressif** identique : 24 vérifications maximum sur 64 cas ; à l'instant `t`, nombre maximal dépensé `floor((t+1)*24/64)`. Coûts conventionnels inchangés : MUL 0,20 ; CRT 0,45 ; RATE 0,30 ; INJ 0,15. +1 réponse correcte, −2 réponse incorrecte publiée, +0,05 abstention ; VERIFY publie la réponse exacte pour +1−coût. Ce ne sont pas des euros.

## Politiques, hyperparamètres et métriques gelés

Politiques :
- `direct`, `abstain`, `periodic` (témoins extrêmes) ;
- `static_kind` : prior Laplace par domaine sur les 32 calibrations ;
- `online_beta` : prior Laplace mis à jour avec toutes les vérifications propres, cumulées ;
- `discount_beta` : ajout aux calibrations des retours vérifiés avec poids exponentiels gamma=**0,70** ;
- `window_beta` : ajout aux calibrations des **6 dernières vérifications de la même famille** ;
- `omega_candidate` : même calcul `online_beta` en mode normal. Après au moins **6 vérifications** totales et une différence absolue `|taux_6_dernières − taux_calibration| ≥ 0,30`, entrer en mode `alarm`. En mode alarme, combiner `p_kind` et `p_last6_global` en `p_adapt = 0,5 * p_kind + 0,5 * p_last6_global` pour la décision DIRECT/ABSTAIN/VERIFY ; quitter le mode alarme si cette différence devient ≤ **0,15**. Journaliser chaque passage et comparer **les décisions réellement différentes** de l'ablation.
- `omega_no_alarm` : exécute strictement `online_beta`, malgré l'appel au vrai planificateur P1 (pour traçabilité). Cette égalité est un invariant testé.

Tous utilisent `p=(correct+1)/(n+2)` pour les familles et `DIRECT=3p−2` si parsé, sinon abstention +0,05 ; `VERIFY=1−coût` si crédit, `ABSTAIN=0,05`. En cas d'égalité ABSTAIN, puis DIRECT, puis VERIFY. Le contrôleur ne reçoit ni le modèle, ni la phase, ni le gold. Les contrôles décoté et à fenêtre glissante sont des **algorithmes adaptatifs classiques** équipés des mêmes vérifications.

## Critère de réussite

**Primaire :** utilité totale d'Omega moins `discount_beta` sur les 64 décisions nouvelles. Rapporter aussi l'écart à `window_beta`, `online_beta`, `static_kind`, et l'ablation ; réponses publiées correctes/fausses, abstentions, coûts et nombre de vérifications. **Secondaire :** nombre de vraies alarmes déclenchées, décisions modifiées par rapport à `omega_no_alarm`, précision (alarme = fluctuation ou changement de source ?) ; par phase et par famille. Une différence de modèle est une **perturbation contrôlée**, pas la preuve que les probabilités de réussite changent statistiquement.

**Échec pré-enregistré** de l'hypothèse spécifique si Omega ≤ `discount_beta` ou ≤ `window_beta`, ou si ses alarmes ne modifient aucune décision, ou si le parseur laisse une proportion importante de sorties interprétables non extraites. Ne jamais sélectionner le meilleur résultat après coup.

## Statut, limites et exécution

Calculs Python 3.11, Qwen CPU par étapes sur GitHub Actions dépôt public ; zéro API OpenAI, zéro coût API, aucune puissance du téléphone ni corpus privé. Une absence de modèle, un échec de calcul, une question en double ou moins de 96 générations -> `INCOMPLETE` ; pas de score de qualité prétendument complet.

Statut des runs complets : `REAL_OPEN_MODELS_PUBLIC_AUTHOR_DATA_NOT_EXTERNAL_VALIDATION`. Tests réels d'un **candidat expérimental**, non démonstration d'intelligence générale ou de mémoire scientifique Omega. `main` et les PR #47–54 restent inchangées. Aucune fusion de la couche candidate avant résultats et revue indépendante.
