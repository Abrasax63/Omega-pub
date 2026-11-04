# RAVI-2 Discovery v0.2 — audit de triage typé

Date : 2026-10-20

## Verdict

Prototype non-certifiant construit au-dessus du noyau admissible, du miroir strict et de Structural Graph. Les scores servent uniquement au triage.

## Couverture

- Résultats admissibles : **84**.
- Signatures typées : **84**.
- Contrats stricts disponibles : **51**.
- Candidats conservés : **40**.
- Reclassification v0.1 : `{"REVIEW_REQUIRED": 39, "RESOLVED_KNOWN_CLASSICAL": 1}`.

## Changement v0.2

Le classement combine le graphe structurel avec des champs typés : objets, quantificateurs, préconditions, invariants, opérations, modes d’échec, témoins, modes de preuve, sorties et contrats stricts lorsqu’ils existent. Les dépendances déjà certifiées sont exclues du pool de découverte.

## Top 10 de triage

1. `BR-MEALY-HELLY-01 ↔ OBS-M27-CONFLICT` — score triage `0.818582` ; cross-project=False ; strict=2/2 ; atoms=automaton_or_machine,classification_boundary,compose_intersect_glue,constraint_family,deterministic,finite_discrete_system,finite_scope,helly_arity,incompatibility_empty_intersection,minimal_obstruction_witness,obstruction_failure,reachability_closure,theorem_proof.
2. `OBS-RESTRICT-FORCED-QUOTIENT ↔ OBS-V19-N11-BADOBJECT` — score triage `0.779836` ; cross-project=False ; strict=2/2 ; atoms=binary,classification_boundary,deterministic,finite_discrete_system,global_scope,graph_or_complex,observation_or_quotient,observe_project,obstruction_failure,quotient_partition.
3. `BR-ACC-01 ↔ BR-AFFINE-TREE-GLUE` — score triage `0.732698` ; cross-project=True ; strict=2/2 ; atoms=compose_intersect_glue,exact_claim,finite_discrete_system,finite_scope,local_scope,observation_or_quotient,observe_project,obstruction_failure,reachability_closure,theorem_proof.
4. `OBS-V19-BAD-FIBER2 ↔ OBS-V19-N11-THIRD-ORDER` — score triage `0.729153` ; cross-project=False ; strict=2/2 ; atoms=explicit_witness_or_family,forall_quantifier,observation_or_quotient,observe_project,obstruction_failure,quotient_partition,rank_dimension_kernel.
5. `OBS-V19-BAD-FIBER2 ↔ OBS-V19-N11-BADOBJECT` — score triage `0.710575` ; cross-project=False ; strict=2/2 ; atoms=binary,deterministic,exact_claim,finite_discrete_system,observation_or_quotient,observe_project,obstruction_failure,quotient_partition,rank_dimension_kernel.
6. `OBS-V19-COEX-REGION ↔ OBS-V19-UNIVERSAL10` — score triage `0.705582` ; cross-project=False ; strict=2/2 ; atoms=binary,constraint_family,exact_claim,explicit_witness_or_family,finite_discrete_system,observation_or_quotient,observe_project,periodicity,realizability_constructive.
7. `DELTA-SPECTRUM-CLASS ↔ OBS-V19-COEX-SMALLMODEL` — score triage `0.70179` ; cross-project=True ; strict=1/2 ; atoms=classification_boundary,deterministic,explicit_witness_or_family,finite_discrete_system,finite_scope,iterate_horizon,observation_or_quotient,observe_project,periodicity,quotient_partition,spectrum_horizon,theorem_proof.
8. `OBS-V19-BAD-FIBER2 ↔ OBS-V19-N11-MOMENT-GRAM` — score triage `0.697734` ; cross-project=False ; strict=2/2 ; atoms=binary,exact_claim,observation_or_quotient,observe_project,obstruction_failure,quotient_partition,rank_dimension_kernel.
9. `OBS-V19-COEX-REGION ↔ OBS-V19-COEX-SMALLMODEL` — score triage `0.689426` ; cross-project=False ; strict=2/2 ; atoms=binary,classification_boundary,compose_intersect_glue,explicit_witness_or_family,finite_discrete_system,finite_scope,observation_or_quotient,observe_project,periodicity,theorem_proof.
10. `OBS-V19-C5-CAPACITY ↔ OBS-V19-COEX-SMALLMODEL` — score triage `0.688765` ; cross-project=False ; strict=2/2 ; atoms=binary,classification_boundary,explicit_witness_or_family,finite_discrete_system,finite_scope,observation_or_quotient,observe_project,periodicity,spectrum_horizon,theorem_proof.

## Garde

TRIAGE_ONLY: typed discovery candidate is not a theorem, dependency, novelty claim, or scientific premise.

Aucun candidat de ce fichier n’est une prémisse scientifique. Toute promotion exige formalisation, au plus deux expériences décisives, audit de redondance/bibliographie et commit RAVI-2 séparé.