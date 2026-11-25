# MULTISELECT — Rejeu indépendant de la sélection à deux positions

25 novembre 2026, 12 h 49 CET. Branche `experiment/omega-100-2026-11-18`, départ `d3c278916a5446f00633745c7b9ea4e551493d40`. 66 fiches contiguës, 067 libre. **Cycle sans expérience nouvelle.** Aucun moteur d'inférence disponible localement avec le modèle de base. L'audit exploite un run terminé en lecture seule, hors compteur et sans utiliser CUMULATIVE01 ni ouvrir de cohorte B.

[Run 45604065004](https://github.com/Abrasax63/Omega-pub/actions/runs/45604065004), [source figée](https://github.com/Abrasax63/Omega-pub/blob/6d16d3e051b10b78c0a4acf191b2bf03d87ed012/research/learning_hub/mask_equality_diagnostic/multiselect_cumulative01.py). Résultats 15017920558 et jeux déjà évalués 15017276347, SHA-256 ZIP `6d8d33f7b9121d34d70174f8b54fdb7902b29383a11729aa60b400cd6cc6afac` et `eae42c9bdb3bc00e9475dc4331f74bdb2697afe612a73d9fa702bb1ee0f06934`. Protocole secondaire préalable SHA-256 `e7363005d4b01de705038048225dfec920e80c49bcb6b7d7aa59290ce9c5df5e`. Les 576 sorties et les empreintes de consigne sont vérifiées. L’oracle reconstruit les réponses avec les positions explicites et refuse l’ordre inversé sur le témoin. Exactitudes, paires et seuils correspondent aux agrégats du run.

| Cas | Base | Parent | Pilote | Paires parent → pilote |
|---|---:|---:|---:|---:|
| Sélection multiple courte, formulation 0 | 3/32 | 8/32 | 27/32 | 0/16 → 11/16 |
| Sélection multiple courte, formulation 1 | 4/32 | 19/32 | 28/32 | 4/16 → 12/16 |
| Sélection multiple longue, formulation 0 | 0/16 | 2/16 | 11/16 | 0/8 → 5/8 |
| Sélection multiple longue, formulation 1 | 0/16 | 4/16 | 8/16 | 1/8 → 2/8 |
| Indexation longue | 7/8 | 8/8 | 6/8 | — |

**VÉRIFIÉ : progression de la sélection multiple, seuil d'acquisition non atteint** (29/32 et 13/16 paires exigés dans les deux formulations courtes, avec gain minimal face au parent). Seuil de rétention du pilote également non atteint : 2 indexations longues perdues, 0 récupérée en normalisant uniquement les espaces. Les témoins de copie et de sélection simple sont inchangés face au parent. Ceci ne mesure pas une rétention durable. Aucun entraînement nouveau.

`timeout 10s python3 audit_multiselect.py` à côté des deux ZIP nommés multiselect-results.zip et multiselect-test.zip. 7,861 ms. SHA-256 code `b08eddf1c887941b95b0c7324db8e7b1966eff79b01d47ee34e55cdbc93c8530`, agrégats `3a7b02d47e223982e3d1b229d5565527f4794cef03b2e94e80648befd0fb2d6f`. Aucun corrigé ni prédiction publié. Prochain test sur cohortes fraîches : comparer base, consigne neutre et système assisté à longueur fixe, puis augmenter la longueur à consigne fixe et contrôler l’indexation héritée. A/P/B, rétention et transfert du prochain test non mesurés. Registre lu au SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`, `existing_omega100` examiné, pertinent et utilisé pour recalculer le verdict, sans exécution d’expérience numérotée. Aucun nouveau composant ni coût payant.
