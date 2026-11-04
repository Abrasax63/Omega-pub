# OBS-M27-FERTILE — Mealy27 — largeur fertile q−1

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour une machine de Mealy complète déterministe, toutes identités initiales possibles et langage de traces exactement1-step local (r_IO=1), chaque entrée a au plus q−1 sorties fertiles, où q est le nombre de symboles de sortie et fertile signifie au moins deux continuations de sorties sous une même entrée future.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Machines de Mealy finies complètes ; r_IO=1.
- Hypothèses : finitude; déterminisme; complétude; tous états initiaux; exactitude du langage1-step
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Reconstruction par semi-groupe de matrices entières de retour à sommes de lignes bornées ; calculs sur famille C(q,k), non preuve computationnelle universelle. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx` ; SHA `b6a8a334ba427e62a613b43687284afa2ab6ddc0cc08f69c9aaa1942c958e1f7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-MEALY` (PRIMARY) : Adaptivity boundary - Mealy machines.docx — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-FERTILE` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-M27-CONFLICT` → `OBS-M27-FERTILE`. Borne supérieure q−1 utilise la largeur fertile.
- `DEPEND_DE` : `OBS-M27-BINARY` → `OBS-M27-FERTILE`. Au plus une branche non singleton.
- `DEPEND_DE` : `BR-MEALY-HELLY-01` → `OBS-M27-FERTILE`. La borne de Helly vient du fait que chaque branche essentielle d une non-face minimale est fertile, puis largeur fertile <= q-1.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-M27-FERTILE`.*
