# OMEGA-STRAT-002 — audit expérimental du choix de méthode et de l'arrêt

**Date : 2026-11-11. Statut : CALCUL EXACT SUR CALIBRATION CONSTRUITE ; NON AVEUGLE, SANS LLM.**

## Objectif et traçabilité

Tester le choix de méthode parmi quatre procédures **réellement exécutées** : `formal`, `compute`, `refute`, `source`. La méthode `formal` effectue des tests de divisibilité universelle, de connexité/parité pour Euler, de distinction d'images et des produits croisés ; `compute` effectue une énumération de circuits ou de fonctions finies, du Python `zip(strict=True)` et du calcul `Fraction` ; `refute` ne conclut `no` que sur un témoin/contre-exemple ; `source` lit une classification documentaire locale des clauses RFC 9110 et de `zip(strict=True)`. Il ne s'agit pas de quatre agents autonomes, et le dernier contrôle n'est pas une extraction réseau indépendante à chaque passage.

- Pré-enregistrement AVANT création du code : **`9e5d423f2d61d6f88c2bad7296fb58fe9c293813`**.
- Baseline forte par sous-type ajoutée AVANT tout résultat : **`ea1ed4ebfa2f6e719941b8a915e9ea078f50f472`**.
- **32 cas publics construits**, 8 pour chacun des 4 domaines (math, programmation, données et documentation). **16 cas de calibration** et **16 cas de test**, 4/4 par domaine, disjoints en identifiants mais non indépendants structurellement (mêmes gabarits).
- Certaines tentatives sont **artificiellement indisponibles**, selon le pré-enregistrement. La panne ne devient visible qu'après l'appel de méthode. Les deux consultations sont facturées même si elles renvoient `unknown`.
- Correcteur : calcul exact séparé lorsque possible : pour un circuit eulérien, critère des degrés/connexité versus recherche exhaustive des parcours ; pour données, `Fraction` versus produits croisés ; pour Python, exécution réelle et propriété de longueur. Pour RFC, les valeurs proviennent d'une table normative relue dans les sections officielles, **sans double notation humaine indépendante**.
- Le planificateur réellement utilisé est `action_planning_two_step.optimize_policy` de la bibliothèque existante, avec les observations des méthodes sur la seule partition d'apprentissage et deux mondes sentinelles `yes/no` à résultat `unknown`. **Une décision du modèle sans certificat de méthode est toujours révoquée : abstention.**

## Résultat de la comparaison principale

| Bras | Résolutions exactes sur 16 | Abstentions | Erreurs | Consultations unitaires |
|---|---:|---:|---:|---:|
| A : meilleur ordre global sur calibration | 13 | 3 | 0 | 24 |
| B : meilleur ordre fixe par domaine | **15** | 1 | 0 | 20 |
| C : Omega adaptatif, apprentissage par domaine | **13** | 3 | 0 | **16** |
| D : repli fixe par domaine, même méthodes que B | 15 | 1 | 0 | 20 |
| F : meilleur ordre fixe par sous-type | **15** | 1 | 0 | **18** |

Les sélecteurs fixes forts B/F sont choisis en **énumérant exhaustivement les ordres de deux méthodes** sur la partition de calibration seulement, critère : maximiser les cas résolus, puis minimiser les consultations, puis départager lexicalement.

**Résultat négatif du critère principal :** Omega C ne dépasse pas les baselines fortes à même budget, même domaine et mêmes outils. Il consomme moins de tentatives, mais échoue à délivrer deux certificats que B/F obtiennent. Toutes les réponses émises sont correctes ; il s'agit d'un défaut de couverture/abstention, non d'erreurs factuelles confiantes.

## Analyse adversariale de l'objectif d'optimisation

La fonction d'objectif de `optimize_policy` minimise l'erreur de décision bayésienne calculée **dans les hypothèses fournies** plus les coûts d'action. Cette fonction ne mesure pas directement la probabilité d'obtenir un **certificat exécutable sur un cas hors entraînement**.

Le cas fini **M4** rend la différence reproductible :

- Question : pour tout entier `k`, `8*k+2` est-il divisible par 2 ?
- Une preuve symbolique directe tranche **oui en une méthode**, puisque 8 et 2 sont divisibles par 2.
- La méthode `compute` teste les entiers `-8..8` ; elle ne trouve aucun contre-exemple, mais doit rendre `unknown`, car une recherche finie ne prouve pas un universel.
- Le modèle Omega entraîné spécifiquement sur le sous-type `mod` choisit néanmoins `compute` en premier, puis finit sans certificat sur M4.
- La règle forte fixe par sous-type utilise `formal` et répond `yes` en **une** tentative.

Cette divergence ne disparaît pas lorsqu'on communique le sous-type à Omega. C'est un **contre-exemple exact** à la proposition selon laquelle minimiser le risque de décision du modèle entraînerait automatiquement une bonne stratégie de production de preuves.

## Vérification d'équité ajoutée après résultat — exploratoire, non pré-enregistrée

Une fois les résultats initiaux connus, une variante d'Omega entraînée **par sous-type** a été ajoutée pour qu'elle bénéficie de la même variable visible que F. **Ce test est post-hoc**, et ne doit pas être intégré au score principal pré-enregistré.

- `C_omega_subtype_exploratory` : **12/16**, 4 abstentions, 16 consultations, 0 erreur.
- F (fixe par sous-type) : **15/16**, 1 abstention, 18 consultations.

Omega ne surpasse pas la baseline, même lorsque les étiquettes de sous-types lui sont fournies comme à F. Le gabarit et les priors peuvent faire choisir une recherche bornée impropre à démontrer un universel.

## Réparation exploratoire après résultat — pas un gain causal d'Omega

Un diagnostic `strategic_method_fallback_diagnostic.py` garde le premier choix d'Omega, mais lorsqu'il n'a produit **aucun certificat**, sélectionne une méthode de secours suivant la fréquence de conclusions de cette méthode sur le **seul échantillon de calibration de même sous-type**. Aucun corrigé de test n'est consulté, et le même plafond de deux essais reste imposé.

- Omega original : **13/16, 16 consultations**.
- Omega + repli externe : **15/16, 18 consultations**.
- Référence F fixe par sous-type : **15/16, 18 consultations**.

Les cas de preuve M5 (Euler) et P5 (`zip(strict=True)`) sont récupérés en changeant de méthode. S4, une question documentaire avec source normative artificiellement indisponible, reste indéterminé et ne doit pas recevoir de réponse fabriquée.

**Interprétation :** la valeur vient d'une règle de secours extérieure au planificateur, déjà égalée par la baseline forte. Le résultat ne démontre pas une intelligence stratégique supérieure et **ne représente pas un test prospectif indépendant** de la réparation.

## Contrôles et verdict

Le code du portefeuille est dans `prism/strategic_methods_executable.py`, ses comparateurs dans `prism/strategic_method_selection.py`, les deux analyses post-hoc dans `prism/strategic_method_fallback_diagnostic.py` et l'armature des tests de non-régression dans `test_strategic_method_selection.py`, `test_strategic_method_fallback_diagnostic.py`, `test_strategy_evidence_objective_gap.py`.

Contrôles : réponses conclusive versus oracles ; rejet des conclusions sans preuves ; limite de deux tentatives ; aucune répétition de méthode ; aucune promotion du seul non-aboutissement d'une réfutation en preuve positive ; invariance de l'ordre d'entraînement ; absence de mélange des deux partitions. Les tests logiciels confirment la logique définie, pas une supériorité sur tâches naturelles.

**Verdicts par périmètre :**
- **CALCUL EXACT :** dans ces 16 cas de test construits, C donne deux réponses correctes de moins que B/F et aucune réponse incorrecte, au prix de moins d'essais.
- **CALCUL EXACT :** une règle de repli fondée sur l'entraînement récupère ces deux conclusions et atteint la baseline F, sans la dépasser.
- **CALCUL EXACT :** l'optimisation d'une perte bayésienne sur mondes finis peut choisir une vérification qui n'apporte pas de certificat pour une proposition universelle, même lorsqu'une preuve formelle est disponible.
- **INDÉTERMINÉ :** avantage sur problèmes mathématiques inédits, compréhension de problèmes en langage naturel, apprentissage de nouvelles méthodes, coût LLM, comportement avec de vrais outils faillibles et sources indépendantes. Le corpus est petit et conçu par les expérimentateurs ; l'effet statistique de généralisation ne peut pas être estimé de manière crédible.

## Recommandation architecturale falsifiable

Le verrou prioritaire est **l'objectif du méta-planificateur**, pas le nombre d'agents. Le prochain prototype devrait minimiser une perte comprenant explicitement :
1. Erreur de conclusion ;
2. **Coût d'absence de certificat** (abstention sur question décidables) ;
3. Coût de consultation ;
4. Pérennité et autorité de la preuve.

Comparer ce planificateur `certificate-aware` à un **portfolio fixe optimisé par sous-type** sur un **nouveau** lot réellement tenu à l'écart des deux développements. Ne pas optimiser l'objectif en regardant les 16 cas de test de cette PR. Pour un corpus de recherche ouvert, annoncer calibration uniquement ; pour une évaluation forte, faire créer et annoter des tâches indépendamment avant exécution.

Les sources documentaires utilisées sont :
- RFC 9110, §§15.4.2, 15.4.3, 15.4.8, 15.4.9 : https://www.rfc-editor.org/rfc/rfc9110
- Documentation Python `zip(strict=True)` : https://docs.python.org/3/library/functions.html#zip

**Ce travail reste sur une branche expérimentale en PR DRAFT. Aucune fusion `main`, modification SQLite ou promotion CORE.**
