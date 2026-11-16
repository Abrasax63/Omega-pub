# OMEGA #94 — pré-enregistrement du contrôle extérieur (2026-11-16)

**DÉCISION AVANT LECTURE DES JOURNAUX.** Comparaison de capacité de vérification et d'abstention, non campagne de certification scientifique.

## Candidat gelé
- Algorithme candidat : `09_INFRASTRUCTURE_AGENTIQUE/prism/lineage_adapter.py`, SHA Git blob `466eac6ccf63f5e060eb7bb9317b44b9925c6bcf`, commit candidat `7bff5a6f8a9aec6e1c6974ee3a90f6efd9cc5311`.
- Comparateur : `provenance_selection.select_verdict` (PR #81) + traduction prudente `selector_translation`, **pas la même fonctionnalité native**.
- Budget : au plus deux journaux distincts lus par paire ; le nombre de journaux lus et les octets traités doivent être enregistrés séparément. Ne pas modifier les classificateurs après lecture.
- Les tests précédents du run Omega `43489499229` sont exclus (données d'entraînement / développement).
- Métriques : taux de dossiers éligibles à l'analyse, classifications correctes / incorrectes / abstentions lorsque l'étiquette peut être établie par une méthode réellement indépendante, coûts. Aucun succès d'un programme sur un exemple fabriqué ne vaut preuve externe.
- **Règle de non-promotion :** si moins de 10 cas vérifiables indépendamment sont identifiés, déclarer `BENCHMARK_INSUFFISANT` plutôt qu'un score ; aucune fusion ni certification.
- Toutes les traces absentes / 410 / 403 / non porteuses d'empreintes et ascendance conduisent à `indetermine`. Ne pas sélectionner a posteriori uniquement les cas favorables.

## Cohorte extérieure gelée avant lecture

Ordre figé, obtenu en recherchant d'abord le PR ouvert le plus récemment mis à jour de chaque dépôt ci-dessous, puis un workflow de type CI/vérification disponible au commit indiqué. Pour chaque run : examiner **les cinq premiers jobs terminés** triés par ID croissant (y compris failed/skipped), ou tous s'il y en a moins. Ne pas remplacer un job après lecture. Maximum : 20 jobs, 4 runs.

1. `astral-sh/ruff`, PR #30419, commit `91e87c76db2ce8d83fa29a0719f9629d17d7bff2`, run CI `43498186653`.
2. `actions/checkout`, PR #2611, commit `44c2bc1922b103805732b83abe0aac1658d22d96`, run Build and Test `42463640255` (`action_required` au moment de la sélection).
3. `sigstore/cosign`, PR #5089, commit `55babe351b7aed960dc3a20c122097e88f5e8cbf`, run CI-Validate-Release-Job `43493856053`.
4. `google/osv-scanner`, PR #3136, commit `ddd22d13e42f3d80cfab87f0e03afc0916aa9b74`, run Checks `43783961437`.

Cette cohorte n'a pas été conçue pour produire des copies/recalculs identifiables. Un job n'est **pas** automatiquement un cas portant une réponse de référence ; une paire n'est évaluable que si une sortie et son origine peuvent être établies indépendamment. Aucun mécanisme de requalification d'échantillons en cours de lecture.

## Référentiel de confiance
Les journaux bruts GitHub fournissent des indices, mais pas nécessairement une attestation SLSA/in-toto signée. SLSA v1.2 sépare l'identité du builder, les dépendances résolues, les artefacts produits et la vérification de provenance. Nous ne considérerons pas des jobs GitHub distincts comme des validations scientifiques indépendantes : https://slsa.dev/spec/v1.2/build-provenance et https://slsa.dev/spec/v1.2/verifying-artifacts

## Conditions d'arrêt
- Correction d'un bogue décelé sur holdout = invalidation de la campagne, pas recalcul opportuniste du même holdout.
- Si les logs ne permettent pas d'établir un oracle indépendant ou si la comparaison mesure des tâches différentes, verdict : `INDETERMINE` / `BENCHMARK_INSUFFISANT`.
- Tous les candidats non satisfaits et les refus de collecte sont consignés.
