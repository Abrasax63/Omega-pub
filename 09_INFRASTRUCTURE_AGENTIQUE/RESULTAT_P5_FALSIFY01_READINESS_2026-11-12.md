# P5-FALSIFY-01 — résultat de l'audit contradictoire des cinq configurations

**12 novembre 2026 — Statut : AUDIT TECHNIQUE RÉEL VALIDÉ / EXPÉRIENCE DE SUPÉRIORITÉ À CINQ BRAS NON PRÊTE.**

## Preuves reproductibles

- [Protocole pré-enregistré avant code](EXPERIMENT_P5_FALSIFY01_FIVE_ARM_PREREG_2026-11-12.md), commit `b870e284a538ee4c088f3f528b65203b09a7fdc2`.
- [GitHub Actions #43245371914 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43245371914), tests adversariaux `prism/test_p5_falsify01_readiness.py` et exécution du vrai pipeline P1 → P2 → P3 **jusqu'au stade enregistreur**.
- [Archive JSON de l'audit et des portes bloquantes](https://github.com/Abrasax63/Omega-pub/actions/runs/43245371914/artifacts/13955444210).
- [Suite RCE générale #43245372029 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43245372029).
- [Code d'audit](prism/p5_falsify01_readiness.py) et [tests](prism/test_p5_falsify01_readiness.py) ; **0 inférence réelle nouvelle**, aucun score de benchmark inventé.

## Observations effectuées (pas un simple audit de texte)

Le script a effectivement exécuté `planner.plan_mission` ; le plan P1 version `0.1.0` propose une vérification, mais indique `status=planning_only`, `model_calls_performed=0` et `memory_writes_performed=0`.

Il a ensuite appelé `context.prepare_contexts` sur le vrai checkout du dépôt, via le moteur RCE en lecture seule : le manifeste du contexte compte **6 récupérations exactes de références**. Cela démontre l'accès à l'index, **pas** que des informations de ces fiches ont effectivement modifié le verdict du modèle.

Enfin `execution.start_execution` et `close_execution` ont été invoqués. La politique de P3 annonce **0 modèle appelé par le module** et le verdict scientifique `not_produced`. Aucune perspective autonome n'a été simulée.

Le script a également vérifié le contre-exemple de recollement `001` (trajet localement possible mais aucun témoin global, survivants `2→1→0`) et un filtrage exact sur un monde fini de 16 microétats (suite du test sur 8 survivants). Cela valide la disponibilité du calcul de survivants, **pas sa contribution aux réponses réelles**.

## Résultat des portes de préparation

| Condition obligatoire | Résultat |
|---|---|
| A — modèle nu et cinq exécutions réelles comparables | **NON VALIDÉ** |
| B — contrôle fort exécuté sur une cohorte nouvelle | **NON VALIDÉ** |
| C versus E — désactivation mémoire produisant une différence vérifiable de décision | **NON VALIDÉ** |
| D versus E — désactivation observabilité produisant une différence vérifiable de décision | **NON VALIDÉ** |
| Parité réelle de tokens, temps, calcul et outils | **NON VALIDÉ** |
| Nouveaux cas indépendants de ceux déjà analysés | **NON VALIDÉ** |
| Revue externe SQL/texte et oracles indépendants | **NON VALIDÉ** |

**Verdict du programme : `readiness=NOT_READY`, exactement 7 portes encore fermées.** La CI doit **réussir en signalant honnêtement ces fermetures**, plutôt que construire des résultats fictifs. Les tests refusent les ablations qui ne changent que des labels ou journaux, la fuite de vérité dans les traces, une fausse exécution de modèle, un bras « sans mémoire » qui effectue des lectures et un bras « sans observabilité » qui utilise le filtre.

## Suite effectuée dans une branche distincte

Une couche d'inférence **expérimentale** capable d'appeler réellement un modèle ouvert sur cinq chemins contrôlés a été créée dans [PR #65 — FALSIFY-02](https://github.com/Abrasax63/Omega-pub/pull/65), issue de ce travail. Elle ne modifie pas la signification de P1/P2/P3 et reste **un pilote d'intégration sur tâches finies synthétiques**, non la campagne finale multi-domaines.

**Conclusion scientifique :** aucun avantage d'Omega démontré ni réfuté universellement. Avant d'annoncer un test à cinq bras, il faut d'abord prouver que les cinq traitements sont **effectivement appliqués** et que leurs coûts sont comparables. Le calcul d'observabilité mathématique est disponible ; son intégration décisionnelle reste un problème ouvert.

**PR DRAFT, aucune fusion dans main, aucune promotion de performance scientifique dans CORE.**
