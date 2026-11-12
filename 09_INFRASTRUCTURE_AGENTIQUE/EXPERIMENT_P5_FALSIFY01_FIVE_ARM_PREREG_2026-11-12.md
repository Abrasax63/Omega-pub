# P5-FALSIFY-01 — protocole contradictoire à cinq bras et porte de préparation

**12 novembre 2026 — Pré-enregistré AVANT le programme de préparation, avant sélection des cas et avant toute inférence nouvelle.**

## Hypothèse à tenter de réfuter

« À modèle, informations accessibles, temps de calcul et budget égalisés, la combinaison mémoire scientifique + sélection adaptative + observabilité/provenance d'Omega améliore l'utilité décisionnelle sur des problèmes inconnus, au-delà d'une politique classique forte. »

**Un gain Omega à l'issue d'une expérience sur des cas déjà analysés ne compte PAS comme preuve.** Une réussite de tests unitaires ou d'une CI n'est pas une réussite scientifique. L'absence de résultat concluant ne réfute pas universellement la recherche ; le verdict porte sur la configuration et les tâches effectivement testées.

## Conditions préalables impératives (readiness gate)

1. **Cinq mécanismes effectifs, pas cinq étiquettes** : pour chaque bras, tracer le véritable modèle appelé, l'entrée, les informations, les opérations de vérification, le résultat et un budget complet. P1 ne fait aujourd'hui que planifier ; P2 prépare des paquets RCE, P3 enregistre des perspectives **sans les exécuter**. Tant qu'une chaîne d'exécution commune, réelle, n'est pas enregistrée, `GATE_EXECUTION=FAIL`.
2. **Ablation causale vérifiée** : désactiver réellement les *lectures de mémoire décisionnelles* (pas seulement masquer un champ de sortie) et le *filtre de témoins compatibles* ; fournir un test d'intervention où le changement de ce mécanisme entraîne une différence d'état interne et de décision sur un cas qui le nécessite. Ne jamais forcer artificiellement un gain final d'Omega.
3. **Source de vérité non contaminée** : textes et solutions gardés séparés, commit des énoncés/empreintes avant exécution, aucun gold dans les prompts ou observations intermédiaires, revues sémantiques des requêtes SQL par un examinateur différent de celui qui a rédigé les requêtes. Les cas publics ClaimDB/PR29/EVID06 **ne sont pas** un nouveau holdout et servent seulement de contrôle rétrospectif.
4. **Égalité réelle de ressources** : mêmes modèles/version/température, mêmes types d'outils, plafond total de tokens, de temps CPU, de consultations de modèles et d'actions; les recherches mémoire et vérifications comptent dans le budget. Conserver les coûts effectivement observés, pas seulement un coût inventé de 0,20.
5. **Comparateur classique fort** : Bayes/VOI avec planification à plusieurs étapes quand le cadre est fini, ou UCB/Thompson avec observations payantes quand le modèle est inconnu ; accès aux **mêmes** données et outils. Un témoin myope seul est insuffisant. L'invariance des décisions de deux bras est rapportée comme `NON_IDENTIFIABLE`.
6. **Viabilité méthodologique** : faire un pilote de calibration distinct et une étude de puissance avec une marge utile pré-définie; avant tout nouveau calcul coûteux, s'assurer que l'exécution et la stratégie ne sont ni identiques ni dominées mécaniquement.

## Définition des bras

| Bras | Fonction | Exécution minimale vérifiable |
|---|---|---|
| A `direct` | Modèle nu, sans mémoire externe ni vérification | Véritable inférence du modèle versionné |
| B `classical_strong` | Optimiseur conventionnel VOI/bandit sous le même budget | Politique forte exécutée et ses signaux observables |
| C `omega_no_memory` | Même orchestrateur qu'E, mais aucune lecture de mémoire scientifique | Trace du blocage de `memory_get/search` et effet sur la décision |
| D `omega_no_observability` | Même orchestrateur qu'E et même mémoire, mais sans filtre de réalisabilité/provenance | Trace du bypass et contre-exemple qui le distingue d'E |
| E `omega_full` | Mêmes ressources, mémoire + filtre de témoins actifs, sélection adaptative | Réelles traces P1/P2/P3 et actions effectivement exécutées |

**Règle expérimentale stricte :** C, D et E ne peuvent être créés comme alias d'une seule politique. Si E reproduit B avec seulement un log décoratif, aucune plus-value d'Omega n'est démontrée, même avec un bon score.

## Échantillon et résultat primaire (au moment où les gates passent)

- Envisager **40 problèmes de calibration et 160 problèmes d'évaluation distincts** issus de *quatre familles réellement différentes* : raisonnement mathématique fini, SQL sur données versionnées, analyse de code, contradiction de provenance. Ces effectifs sont **cibles de planification, PAS un résultat statistique ni un échantillon déjà préparé**. Les jeux avec annotations publiques doivent être exclus de la revendication d'aveuglement.
- L'examinateur des corrections n'est pas l'auteur de toutes les solutions. La méthode d'échantillonnage, les exclusions, les versions et les seuils sont publiés **avant** observation des résultats.
- `U = +1 correct, -2 faux, +0.05 abstention - c(outils, inférence, mémoire)`; fixer les facteurs et unités à la calibration, **ne pas changer après lecture du test**. Rapporter séparément la justesse, les erreurs à haut coût, la couverture, la latence, les tokens, les actions.
- Critère principal préfixé : `Delta = U(E)-max(U(A),U(B),U(C),U(D))` sur les **mêmes cas**. Le maximum des quatre baselines sur le test introduit un biais de sélection ; exiger une correction de comparaison multiple ou choisir le meilleur baseline sur calibration AVANT le test. **Choix retenu** : sélectionner le comparateur principal sur calibration puis le figer ; présenter les quatre autres contrasts exploratoires, avec intervalles et correction de multiplicité lorsque nécessaire.
- Seuil d'effet utile envisagé **+0.10 unité par problème**, à réviser seulement AVANT le pilote de validation et avant le gel du test; ce seuil est une **hypothèse de design**, pas une découverte. Ne pas conclure à l'équivalence à partir d'un p non significatif.
- Analyse par cas apparié : intervalle de confiance 95 % de la différence moyenne, bootstrap par groupe de source/famille si dépendance, test randomisé/paired permutation si applicable, inspection des pires cas. Répéter sur plusieurs partitions réellement nouvelles. Si l'intervalle englobe 0, `INDETERMINE`, pas « gain prouvé ». Si une borne supérieure de l'intervalle reste sous +0.10, réfuter le **gain substantiel pré-enregistré** dans ce cadre seulement; une borne inférieure > 0 avec taille utile et réplication constitue un soutien, pas une preuve universelle.

## Interprétation

- Aucun effet de l'ablation mémoire et observabilité sur les décisions : **non-identifiabilité**, pas démonstration de nullité du mécanisme.
- Dépassement de budget, contamination, source non épinglée, vérité non vérifiable, absence de véritable exécution : **INVALIDATION DU BENCHMARK**.
- E < B dans des tâches adéquates : **réfutation de la supériorité dans ce cadre**.
- E > B mais mémoire/observabilité non activées : **pas d'attribution de gain à Omega**.
- Le test doit rapporter toutes les observations et PR négatives, sans redéfinir les seuils pour avantager Omega.

## Contrôle de l'état du code à créer maintenant

Créer `prism/p5_falsify01_readiness.py` et ses tests qui doivent :
- confirmer l'existence des véritables chemins P1, P2, P3, et leur nature (planificateur, lecture mémoire, enregistreur sans appel modèle) ;
- vérifier une chaîne réelle de P1 → P2 → P3 sous budget **sans prétendre qu'elle exécute le modèle**, et enregistrer les éventuelles limitations ;
- révéler que la politique `omega_observability_candidate` de la campagne précédente et `context_trace_gate` sont les **mêmes décisions** ;
- empêcher qu'un flag mémoire/observabilité purement cosmétique rende un gate « prêt » ;
- produire un **rapport JSON `NOT_READY` ou `READY`** avec preuves de chemin, témoins adversariaux et prochain verrou, sans chiffres de qualité de modèle inventés.

**Lancer ce gate sur GitHub Actions sans API payante ni réinférence de modèle.** Il s'agit du verrou architectural, **PAS de l'expérience finale à cinq bras**. Démarrer les 160 cas uniquement si les gates sont réellement levés. `main` inchangé ; PR en DRAFT, aucune promotion CORE.

## Positionnement bibliographique

- [Cost-sensitive Bayesian active sensing](https://pmc.ncbi.nlm.nih.gov/articles/PMC4253738/), contrôle standard de planification à croyances.
- [PEAR, Findings EACL 2026](https://aclanthology.org/2026.findings-eacl.237/), distinction contribution mémoire/planner et contrôles par ablation.
- [A multi-agent loop and equal-budget ablations (2026)](https://www.mdpi.com/2226-4310/13/9/789), rappel que retirer une composante change souvent aussi le flux de prompts, rendant l'attribution causale délicate.

**Statut strict : PREREG_FALSIFICATION / NOT_YET_VALIDATED / NO_RESULT.**
