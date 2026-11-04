# Q-RQ4-COMMON-RANK — RQ-Q-4 — rang commun et factorisation

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Si p(a,m,b,r,z)=P_m(a,b)f_m(b,r,z), si chaque P_m a plein rang colonne et si leur intersection d’espaces colonnes est span(1), l’identité de somme non sélective des instruments idéaux impose f_m(b,r,z)=f(r,z). Si les instruments idéaux sont tomographiquement complets et qu’un peigne physique réalise ces probabilités, ce peigne factorise en ses deux canaux temporels.

## Cadre

- Projet `QUANTIQUE` ; type `THEOREM` ; version `1`.
- Domaine : Expérience finie ; préparations accessibles communes ; instrument idéal mesure-préparation ; modèle alternatif local à b.
- Hypothèses : réponse f indépendante de a au-delà de b; plein rang colonne; intersection=constantes; identité non sélective; complétude tomographique et existence de peigne pour conclusion physique
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Reconstruction algébrique par intersection et injectivité ; contrôles rationnels Pauli t>0 et contre-test t=0. Aucun diagnostic de puce. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Quantique/NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md` ; SHA `ca90f76aa2ddb06032a53846347141fa7a102bf2ebdd8946d0ac2c9399d68833`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-RQ4` (PRIMARY) : NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md — /Recherche/02_PROGRAMMES_ACTIFS/Quantique/NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-COMMON-RANK` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `RESTREINT` : `Q-RQ4-COMMON-RANK` → `BR-Q-01`. Frontière d’identifiabilité sous contrat additionnel. Ne réfute pas le témoin t=0 ni les instruments hors contrat.
- `ILLUSTRE` : `Q-RQ4-PAULI-ROBUST` → `Q-RQ4-COMMON-RANK`. Le corollaire Pauli vérifie les hypothèses du rang ; la borne scalaire a une preuve directe indépendante.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `Q-RQ4-COMMON-RANK`.*
