# DESC-SUM-01 — Détecteur — somme des deux évidences

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour les16 blocs déterministes des deux calendriers sur12000 observations, les évidences de bloc rationnelles non négatives étant des surmartingales conditionnelles, la règle E0+E1≥β^7382, β=1001/1000, a un risque global sous le nul≤16β^−7382≤1%. À prédicteurs et trajectoire identiques elle alarme au plus tard que le OU au même seuil. Les registres persistants restent227 ou313 bits. Aucune amélioration de puissance après rupture n’est garantie.

## Cadre

- Projet `TRANSFORMATIONS_AUTONOMIE` ; type `THEOREM` ; version `1`.
- Domaine : Machine exacte sous nul spécifié ; deux calendriers déterministes0/750 ;16 blocs ; horizon12000.
- Hypothèses : modèle nul et bruit connus fixés; facteurs conditionnels exacts de moyenne≤1; arrondis dirigés et mort locale; prolongement par1 avant début et gel après fin pour preuve; arithmétique temporaire exclue des bits
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Preuve autonome par moyenne des16 processus et majoration de la somme active ; seuil et capacités vérifiés rationnellement. Aucune puissance simulée de la règle somme. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md` ; SHA `966c48540d31d167583022f70cabe69dd567d3edaefd4412fd573f680ce88e79`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-SUM` (PRIMARY) : detection_correlations_2026-10-14.md — `/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md`.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-DESC-SUM-01` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `ILLUSTRE` : `DESC-SUM-01` → `BR-DESC-02`. Même programme de surveillance, mais covariance et règle somme ont des justifications indépendantes.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `DESC-SUM-01`.*
