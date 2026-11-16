# Omega PR #94 — contrôle extérieur de couverture, 16 novembre 2026

## Verdict

**BENCHMARK_INSUFFISANT / PAS DE GAIN ÉTABLI.** Le protocole a été gelé avant inspection des journaux sous le commit [245d088b](https://github.com/Abrasax63/Omega-pub/commit/245d088b0ac07b9b8fdcf403f375893d28d905ac). Aucun ajustement du classificateur candidat `lineage_adapter.py` n'a été fait après ce gel.

Les quatre workflows pré-enregistrés ont été interrogés par l'API GitHub via le connecteur. L'un n'avait aucun job disponible ; les douze autres jobs ont livré un journal lisible. **Aucun des douze journaux** ne contient simultanément une commande de production couverte par le parseur (xtrace : `+ cp`, `+ install`, `+ python3 -c`) et une ligne de somme SHA-256 portant un chemin. Deux journaux contiennent une ligne de type empreinte mais aucun producteur reconnu.

L'absence de preuve de production n'est pas une preuve de copie ni de recalcul. Aucun cas n'a pu recevoir un **oracle indépendant** de la seule provenance consignée. Aucun score de vérité, taux de réussite, gain propre à Omega, effet adaptatif, ni benchmark sur 15–20 dossiers n'est annoncé.

## Runs et observations, ensemble pré-enregistré

| Dépôt | Exécution | Jobs retenus, triés par ID | Journaux | Candidats exploitables |
| --- | --- | --- | ---: | ---: |
| astral-sh/ruff | [43498186653](https://github.com/astral-sh/ruff/actions/runs/43498186653) | 132136718410, 132137019816, 132137019828, 132137019883, 132137019958 | 5 | 0 |
| actions/checkout | [42463640255](https://github.com/actions/checkout/actions/runs/42463640255) | Aucun, workflow en état action_required | 0 | 0 |
| sigstore/cosign | [43493856053](https://github.com/sigstore/cosign/actions/runs/43493856053) | 132121683715, 132121799477 | 2 | 0 |
| google/osv-scanner | [43783961437](https://github.com/google/osv-scanner/actions/runs/43783961437) | 133027304674, 133027304791, 133027304817, 133027304830, 133027304889 | 5 | 0 |

Détails bruts **des compteurs**, sans réécrire les logs : `BENCHMARK_EXTERNAL_SCREEN_2026-11-16.json`. Ces compteurs sont un filtre de couverture ; le programme ne prouve ni l'absence de données d'attestation stockées ailleurs, ni une indépendance scientifique.

## Ce qui fonctionne

- Le pilotage des lectures externes est possible sans API LLM payante.
- Un script de tri et les tests de refus sont disponibles dans `external_cohort_screen.py` et `test_external_cohort_screen.py` ; le script reste en lecture seule, et ne collecte rien sans `--github`.
- Le raccord actuel `lineage_adapter.py` reste compatible avec le corpus de développement du run Omega, mais nous ne pouvons pas en inférer un gain externe.
- Toute entrée vide ou inexploitable conduit à une abstention, et non à une validation positive.

## Analyse de cause

L'obstacle principal n'est pas la capacité du graphe à parcourir une ascendance **déjà fournie** : il manque l'ascendance en entrée, ainsi que la possibilité de vérifier la signature, la source et les dépendances de cette ascendance.

Le standard [SLSA v1.2 Build Provenance](https://slsa.dev/spec/v1.2/build-provenance) définit précisément `builder.id`, `buildDefinition`, `resolvedDependencies` et `subject`. La [vérification SLSA](https://slsa.dev/spec/v1.2/verifying-artifacts) requiert de confronter la provenance à une racine de confiance, de vérifier la signature et les paramètres attendus. Une chaîne d'identifiants de jobs non signée ne remplace pas ces garanties. Une provenance SLSA valide n'est pas automatiquement une reproduction scientifique indépendante.

## Décision pour Omega

1. **Ne pas promouvoir #94** : aucune preuve de plus-value face au comparateur fort. Garder la PR `DRAFT`.
2. Avant de poursuivre un nouveau routage, expérimenter **un collecteur de métadonnées de provenance vérifiables**, privilégiant les attestations structurées publiées avec les artefacts ; vérifier la signature via un outil existant plutôt que développer notre propre cryptographie.
3. Construire ensuite une cohorte d'artefacts dont la provenance signée est réellement disponible, indépendante des exemples du développement, et préenregistrer les labels et budgets dans un registre hors de portée du candidat.
4. Comparer `select_verdict` + la référence classique forte + le graphe d'ascendance **sur exactement la même tâche** ; conserver les abstentions et tous les rejets.
5. Conditions d'arrêt : fausse confirmation, source non authentifiable, moins de 10 cas indépendamment vérifiables, gain nul ou budget injustifié.

**État de preuve** : code de screening implémenté, tests à contrôler en CI, journaux publics inspectés, benchmark scientifique sur cas réservés NON exécuté faute de labels indépendants.
