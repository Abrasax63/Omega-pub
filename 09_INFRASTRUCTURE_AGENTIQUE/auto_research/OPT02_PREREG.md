# OMEGA-OPT-02 — protocole préenregistré (avant code générateur / évaluateur)

Date : 15 novembre 2026. Branche expérimentale distincte, empilée sur la PR #93. **Aucun résultat de modèle ni d'évaluation n'a encore été vu pour OPT-02.**

## Hypothèse falsifiable

Un modèle Qwen2.5-Coder-3B-Instruct Q4_K_M qui reçoit le code classique d'exponentiation binaire (`square-lowbit`) peut proposer une modification réellement plus efficace, à résultats identiques, que **les deux** références classiques `square-lowbit` et `square-scan`.

Une amélioration n'est pas démontrée si aucune proposition ne passe le développement, si un seul résultat est inexact ou si les seuils prédéfinis de vitesse ne sont pas atteints. Aucune modification des seuils après lecture des résultats.

## Budget de recherche gelé

- Modèle : Qwen2.5-Coder-3B-Instruct-GGUF Q4_K_M, poids SHA256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`, llama.cpp au commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
- **Au plus 3 appels LLM**, au plus 800 tokens générés par appel, même modèle et interface ; pas d'API payante ; aucune nouvelle tentative après ouverture de l'évaluation.
- Un seul fichier/fonction autorisé : `q_power(rows, steps)`. Aucune modification de l'évaluateur, du référentiel, des données ni des références.
- Les variantes à AST identique sont dédupliquées, erreurs et rejets conservés.
- Développement : six graphes synthétiques de familles distinctes, générés indépendamment des graphes externes, avec horizons 0,1,31,127,511. Sélection uniquement parmi les programmes corrects sur tous les cas de développement. Priorité à la médiane CPU d'échantillons répétés, pas à la première réponse ni à un résultat ponctuel.
- Une fois un candidat choisi, son SHA-256 et son code sont gelés ; aucune adaptation n'est permise à partir des résultats finaux.

## Corpus de transfert nouveau : données de graphes externes

Les **quatre graphes documentés par NetworkX 3.5** constituent les sources externes, indépendantes du générateur de graphes des anciens pilotes :
1. `karate_club_graph` (Zachary) ;
2. `davis_southern_women_graph` ;
3. `florentine_families_graph` ;
4. `les_miserables_graph`.

Pour chaque graphe, deux variantes de relation : (A) arcs dans les deux sens pour chaque arête ; (B) orientation déterministe de chaque arête par SHA256 de ses index canoniques, avec boucle à chaque sommet. Les index correspondent au tri lexicographique `str(node)`. Les horizons **8,32,128,512** donnent **4 × 2 × 4 = 32 cas chronométrés**. Horizons 0 et 1 ajoutés pour vérification exacte hors chronométrage (16 contrôles, total 48). Les groupes de validation sont les **8 couples graphe/variante d'arcs**, sans réutiliser de cas de `OMEGA-TRANSFER-01`.

Version de bibliothèque fixée : `networkx==3.5`; les graphes et leurs SHA256 canoniques seront enregistrés dans l'artefact d'évaluation. La source des graphes est publique et externe, mais **il n'y a pas de gardien indépendant du holdout**. Les entrées ne sont jamais ajoutées au prompt du modèle et sont construites uniquement dans le job d'évaluation, après la génération et le choix du candidat.

## Mesures et juges

Le programme candidat et les références classiques tournent avec la même image Docker Python 3.12, sans réseau et avec contraintes de ressources. Chronométrer `time.process_time_ns()` dans le conteneur : 2 échauffements puis **9 répétitions**, chacune exécutant un lot de **20 appels**, ordre des bras aléatoire mais déterministe. Conserver toutes les mesures ; calculer la médiane CPU par cas/bras (pas le meilleur run).

La référence mathématique séparée calcule `Q^h` par propagation ensembliste ; vérifier toutes les sorties, et interdire toute confirmation fausse. Critère principal sur chaque cas : rapport `min(median(square-lowbit), median(square-scan)) / median(candidate)` (référence forte conservatrice, choisie par cas).

## Critères figés pour seulement recommander une revue indépendante

1. **48/48 résultats exacts** et aucune erreur de conteneur ou provenance.
2. Moyenne géométrique des 32 rapports au moins **1,10**.
3. Médiane du rapport **≥1,03 dans chacune des 8 familles**.
4. Au moins **7/8 familles avec une médiane strictement >1** (test de signe unilatéral exact p ≤ 0,05).
5. Le vérificateur déterministe de la PR #83 ne signale ni régression, ni dépassement du budget déclaré.

Si un seul point échoue : `NO_DEMONSTRATED_ADVANTAGE`. Si les entrées ou la chaîne sont incomplètes : `INVALID_EXPERIMENT`. Un résultat favorable reste `REVIEW_REQUIRED`, **jamais certifié**.

## Limites décisives

Il s'agit de graphes historiques externes mais publics, non d'un holdout aveugle confié à un tiers. Le modèle peut avoir connu ces familles dans son préentraînement : aucune affirmation d'originalité sans analyse externe. Même 9 mesures sur un seul runner ne certifient pas une différence de performance. Docker partage le noyau et n'est pas une sandbox inviolable. Conserver les résultats négatifs ; ne pas réutiliser ces 32 cas pour ajuster les candidats. Ne modifier ni `main`, ni les PR #81–#85/#93, ni les certificats CORE.
