# P5-EVID-06 — seconde voie de recomptage arithmétique des résultats bruts

**12 novembre 2026 — AUDIT NUMÉRIQUE sur l'archive ORIGINALE, sans nouvelle exécution de modèle ni modification de politique.**

Entrée : [artefact de la CI #43237122391](https://github.com/Abrasax63/Omega-pub/actions/runs/43237122391/artifacts/13952881813), ZIP téléchargé, SHA256 exact `b7ad4d0e39d5ada35ddeed970be037a9d41056d1c7b47e10486e30baeb9d86d4`.

- SHA256 de `evid06_budgeted_routing.json` dans ZIP : `1ff615087a5d68312b7cf3705c35286bceb4e66fdd0ead8b322979e2dd77dff9`.
- SHA256 de `evid06_extra_real_bird_sql.json` dans ZIP : `4112892085a5eb0980b25067c9f32eb3fb7cebc7c157cad03cc6d3c46edd1abf`.

**Contrôle distinct du calcul dans le programme original :** une seconde lecture locale du JSON brut a recalculé chaque récompense parmi les **64 décisions × 8 politiques** : +1 si verdict publié égal au label, −2 sinon, +0,05 si abstention, −0,20 pour toute consultation. Pour chaque politique, 64 IDs uniques ; budget de 2 consultations par lot, au plus 16 ; égalité aux totaux et comptes de bonnes/mauvaises réponses enregistrés dans l'archive. **Aucune divergence arithmétique.**

| Politique | Utilité recalculée | Consultations | Correctes | Fausses | Abstentions |
|---|---:|---:|---:|---:|---:|
| no_purchase | 3,20 | 0 | 0 | 0 | 64 |
| position_first_two | 12,20 | 16 | 15 | 1 | 48 |
| hash_random_two | 12,20 | 16 | 15 | 1 | 48 |
| global_voi | 12,20 | 16 | 15 | 1 | 48 |
| context_voi | 12,20 | 16 | 15 | 1 | 48 |
| context_trace_gate | 12,20 | 16 | 15 | 1 | 48 |
| omega_observability_candidate | 12,20 | 16 | 15 | 1 | 48 |
| hindsight_oracle — non déployable | 38,95 | 16 | 41 | 0 | 23 |

Le second calcul a également vérifié **l'égalité exacte des 64 choix et actions** entre `context_trace_gate` et `omega_observability_candidate`, et confirmé sur le même ensemble **25/64** réponses correctes sans outils contre **55/64** avec SQL, selon le label ClaimDB.

Dans l'autre JSON de l'archive, les trois nouveaux IDs SQL **15601, 3730, 3971** sont tous présents, et les deux calculs SQL de chaque cas donnent la même réponse. **Cette vérification ne remplace pas une revue indépendante de l'anglais des propositions**, qui reste [à réaliser](REVIEW_P5_EVID06_SQL_SEMANTICS_OPEN_2026-11-12.md).

### Limite de l'indépendance

Cette seconde voie est une **réimplémentation arithmétique distincte** réalisée par le même assistant sur l'archive initiale ; ce n'est pas un audit externe, un nouvel échantillon de modèle, une preuve de fiabilité du gold ClaimDB ni une vérification indépendante de la sémantique SQL. Elle réduit seulement le risque d'erreurs de totalisation dans le programme initial.

**Conclusion inchangée : gain adaptatif propre à Omega = 0 ; résultat routage non discriminant sur l'utilité des contrôles opérationnels.** Aucun amendement rétroactif des politiques ou seuils.
