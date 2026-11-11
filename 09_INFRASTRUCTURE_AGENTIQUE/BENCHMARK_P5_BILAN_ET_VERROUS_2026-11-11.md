# Omega — état consolidé du benchmark indépendant P5 A/B/C et des résultats existants

**11 novembre 2026. Note de décision fondée sur les PR du dépôt. Aucune campagne comparative de sorties LLM A/B/C avec notation aveugle n'est attestée.**

## 1. La question scientifique, inchangée

Omega produit-il des réponses plus correctes, réfutables, tracées et économes que (A) une réponse directe du **même modèle**, et (B) les **mêmes cinq perspectives fixes**, quand (C) le planificateur `plan_mission` choisit les perspectives en fonction de la mission ?

**Contrefactuel principal : C−B**, seul capable d'isoler approximativement le routage une fois le modèle, les données, les outils, les métriques, le temps et le budget égaux. Contrôles additionnels C−A et B−A. Les cinq rôles sont des **perspectives textuelles d'un seul modèle**, pas des agents indépendants, tant que des appels indépendants ne sont pas effectivement réalisés.

Les scores prévus sont dimensionnels : exactitude, justification des sources, contre-exemples et réfutations, calibration/abstention, traçabilité, gestion des contradictions ; mesurer séparément erreurs confiantes, tokens, appels, coût de vérification, latence et coût CPU si disponible. Ne jamais inventer une métrique ni résumer les dimensions par une moyenne non pré-enregistrée.

## 2. Observations vérifiables déjà acquises — pourquoi elles ne répondent pas au P5 causal

| Expérience | Données effectivement utilisées | Résultat | Restriction |
|---|---|---|---|
| [PR #29](https://github.com/Abrasax63/Omega-pub/pull/29), 12 PR GitHub | Sources publiques réelles et exactes, plafonds d'appels simulés/observés | Omega 12/12 avec 17 consultations ; plan fixe intégral 12/12 avec 24 | Le contrôle simple fichiers-d'abord de l'[audit #31](https://github.com/Abrasax63/Omega-pub/pull/31) fait aussi 12/12 avec **15** consultations. Aucun avantage propre à Omega. |
| [PR #30](https://github.com/Abrasax63/Omega-pub/pull/30), 24 questions, quatre domaines | Questions et altérations **publiques et construites** | Observation intacte : fixe=Omega 24/24 ; observation simulée falsifiée : fixe=Omega 16/24 avec **8 erreurs confiantes** | Aucun LLM. La provenance officielle simulée n'est pas une véritable signature de source. |
| [PR #38](https://github.com/Abrasax63/Omega-pub/pull/38), ASlib MAXSAT-WPMS-2016 | **630 instances historiques externes**, 10 plis officiels, 18 solveurs, 37 caractéristiques | **KNN-5 2975,554635** contre arbre anticipatif expérimental **3265,585349** en PAR10+coût (plus petit est meilleur). L'arbre glouton profondeur 2 : **3263,893429**. | L'arbre anticipatif est une architecture expérimentale **distincte** du Prisme textuel ; aucun test A/B/C LLM ni validation aveugle. |
| [PR #45](https://github.com/Abrasax63/Omega-pub/pull/45), PROBE-001 | 4 scénarios synthétiques de décision, 60 mondes chacun | Sur les deux scénarios TEST, lookahead2 **égale** greedy et DP exact. Sur CAL_12, lookahead2 est **27,78 % pire** que greedy. | Pas de problèmes de recherche, de coût des appels LLM ni de supériorité propre. |
| **[PR #46](https://github.com/Abrasax63/Omega-pub/pull/46)**, P5-ABC-001 | **24 cas publics**, 2 variantes, 3 stratégies | **144 entrées** : tronc commun exact A/B/C dans 48 groupes, contrôle JS indépendant et **14 tests Python réussis**. Comptage de tokens exigé par la porte d'exécution. | **0 appel LLM, 0 correction humaine aveugle, 0 benchmark de qualité exécuté**. |

Sources internes vérifiées :
- `EXPERIMENT_ASLIB_COST_TRANSFER_RESULTATS_2026-11-11.md`, [GitHub Actions #43070449506](https://github.com/Abrasax63/Omega-pub/actions/runs/43070449506) (SUCCESS) ;
- `EXPERIMENT_STRATEGIC_FIRST_CHECK_RESULTATS_2026-11-11.md`, [GitHub Actions #43044979203](https://github.com/Abrasax63/Omega-pub/actions/runs/43044979203) (SUCCESS) ;
- `EXPERIMENT_P5_MULTIDOMAIN_RESULTATS_2026-11-11.md`, [GitHub Actions #43018557073](https://github.com/Abrasax63/Omega-pub/actions/runs/43018557073) (SUCCESS) ;
- [GitHub Actions #43103417656](https://github.com/Abrasax63/Omega-pub/actions/runs/43103417656) (SUCCESS), [RCE #43103417702](https://github.com/Abrasax63/Omega-pub/actions/runs/43103417702) (SUCCESS).

Ces séries **ne sont pas des preuves indépendantes du même effet** : méthodes, tâches, coûts et données diffèrent ; il serait trompeur de les additionner pour un score unique.

## 3. Défaut causal détecté et réparation vérifiée

Le protocole précédent `p5_four_arm_protocol.py` donne au bras C **un contexte structuré supplémentaire** absent de A et B, donc la comparaison C−B est contaminée par un avantage d'information. Il n'est pas corrigé rétrospectivement : conserver l'original pour l'audit.

Le nouveau `prism/p5_abc_fair_preflight.py` réalise la **parité stricte des informations visibles** et choisit les rôles C par appel réel au `plan_mission` du dépôt. Les 48 groupes partagent les mêmes documents et consignes, la seule différence étant le plan de raisonnement. Le test garde séparées les **8 observations primaires artificiellement inversées**, sans révéler la condition au texte envoyé au modèle.

`prism/p5_abc_budget_gate.py` ajoute une porte **bloquante** de comptage des tokens d'entrée, avant génération, avec snapshot de modèle explicite, `tools=[]`, limite totale commune et limite de sortie commune. La CI l'a éprouvée avec des **clients simulés** : **cela ne représente pas des comptages réels du modèle**. Le code refuse toute comparaison si les mesures fournisseurs manquent.

Le préflight a réussi sans générer une seule réponse de modèle. Artefact : [144 prompts publics préparatoires](https://github.com/Abrasax63/Omega-pub/actions/runs/43103417656/artifacts/13893485467).

## 4. Ce qu'il manque pour répondre enfin à la vraie question A/B/C

**GATE-1 — Cohorte aveugle véritable.** Préparer de nouveaux problèmes multi-domaines (formalisation, calcul, sources normatives, contradictions, programmation et données), **hors du dépôt public**, générés et relus indépendamment du planificateur et des réponses testées. Corrigé/rubrique privés, engagement SHA-256 vérifiable ; ne jamais réemployer v0.4 ou les 24 cas publics comme holdout.

**GATE-2 — Trois exécutions isolées du même modèle, plusieurs répétitions.** Le choix du snapshot doit être explicite ; l'ordre A/B/C doit être mélangé avant première génération. Chaque appel doit utiliser le même accès outils et un budget réellement comptabilisé. Pour les messages à sources, conserver des instantanés des **mêmes documents** visibles aux trois bras. Aucune sortie d'un bras ne doit atteindre les autres.

**GATE-3 — Correction double aveugle.** Deux évaluateurs effectivement indépendants, identifiants opaques, notes figées avant levée de l'aveugle. Sans eux, la comparaison reste un pilote interne non aveugle.

**GATE-4 — Attribution du résultat.** Comparaisons appariées `C−A, C−B, B−A` par domaine, documentant le nombre de cas, les erreurs confiantes, les abstentions, les appels, les tokens d'entrée/sortie, le temps et la provenance. Include a **strong fixed conditional baseline** whenever the source-evidence gate is the real treatment. Report any regression; a marginal improvement in one public case is not a general gain.

**GATE-5 — Aucun faux succès.** Tant que GATE-1 à GATE-3 manquent, le statut du benchmark P5 est **`P5_LIVE_NOT_RUN`** ; toute création de prompts ou validation de l'architecture ne peut pas être présentée comme victoire de C.

## 5. Décision pour le projet Omega

**Conserver** : planificateur explicable existant, protocole d'épreuves non régressif, vérification conditionnelle des preuves, index de provenance, comparateurs forts et journaux de coûts.

**Ne pas promouvoir** : plus de profondeur de recherche comme gain assuré, meilleur score sur le train présenté comme transfert, référentiel public présenté comme aveugle, argument des « cinq sous-agents » sans exécution séparée, ou compétence générale d'une IA issue de seuls problèmes finis.

**Priorité suivante :** exécuter enfin une campagne A/B/C LLM réelle sur un holdout privé et corrigé hors des systèmes, avec budget instrumenté, puis publier **les résultats négatifs autant que positifs**. La présente PR fournit une porte d'entrée reproductible mais ne réalise pas l'exécution du modèle.

**Statut dépôt :** PR #46 en brouillon sur #31, sans merge `main`, mutation de CORE/SQLite, ni modifications aux PR Lean #44 et PROBE #45.
