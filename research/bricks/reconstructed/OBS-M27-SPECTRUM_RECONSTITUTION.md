# OBS-M27-SPECTRUM — Mealy27 — spectre aigu des conflits

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour tout q≥3 et2≤k≤q−1, C(q,k) possède2k+1 états, r_IO=1, L_A=2, L_P=∞ et un noyau de conflit de taillek dont chaque sous-famille propre a un résolveur. Les alphabets peuvent contenir des symboles non utilisés ; aucune minimalité générale en états ou entrées n’est revendiquée.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Famille explicite C(q,k) de la source ; puits commun ; sorties d’identification.
- Hypothèses : q≥3; 2≤k≤q−1; machine totale déterministe
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Construction et preuve autonomes ; 15 cas q=3..7 et228 sous-familles testés par recherche finie complète des configurations. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx` ; SHA `b6a8a334ba427e62a613b43687284afa2ab6ddc0cc08f69c9aaa1942c958e1f7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-MEALY` (PRIMARY) : Adaptivity boundary - Mealy machines.docx — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-SPECTRUM` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `ILLUSTRE` : `OBS-M27-SPECTRUM` → `OBS-M27-CONFLICT`. Construction indépendante réalisant chaque arité permise.
- `ILLUSTRE` : `OBS-M27-SPECTRUM` → `BR-OBS-01`. Séparation adaptatif/prédéfini ; aucune dépendance du nouveau témoin à l’ancien.
- `DEPEND_DE` : `BR-MEALY-HELLY-01` → `OBS-M27-SPECTRUM`. La famille C(q,k) fournit la sharpness q-1 et réalise chaque arité 2..q-1.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-M27-SPECTRUM`.*
