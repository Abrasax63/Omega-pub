# OBS-M27-CONFLICT — Mealy27 — noyaux de conflit bornés

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Si un état de connaissance accessible admet une ADS finie mais aucune PDS, un nœud d’une ADS possède des langues de résolution individuellement non vides avec une sous-famille minimale d’intersection vide. Sous r_IO=1, son arité est comprise entre2 et q−1.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Identités initiales conservées dans les états de connaissance ; ADS finite ; PDS résout toutes les identités.
- Hypothèses : langues de résolution régulières; ADS finie; r_IO=1 pour borne supérieure; machine complète déterministe
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Preuve au nœud le plus profond sans PDS ; identité de résolution par intersection ; chaque branche conflictuelle est fertile. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx` ; SHA `b6a8a334ba427e62a613b43687284afa2ab6ddc0cc08f69c9aaa1942c958e1f7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-MEALY` (PRIMARY) : Adaptivity boundary - Mealy machines.docx — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-M27-CONFLICT` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-M27-CONFLICT` → `OBS-M27-FERTILE`. Borne supérieure q−1 utilise la largeur fertile.
- `ILLUSTRE` : `OBS-M27-SPECTRUM` → `OBS-M27-CONFLICT`. Construction indépendante réalisant chaque arité permise.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-M27-CONFLICT`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `Adaptivity boundary - Mealy machines.docx`, note révisée le 27 septembre 2026, sections 4–5. À un état de connaissance K, chaque branche de sortie possède un langage régulier R(K(a,y)) de suffixes preset qui la résolvent. Leur intersection commune est le critère de PDS après le premier input. Si un ADS existe mais aucun PDS, un nœud atteignable contient une sous-famille minimale de ces langages à intersection vide : un conflict core. Sous r_IO=1, son arité est bornée par 2≤|C|≤|Γ|−1. **Limite :** candidate de résultat en attente d'examen externe, pas certification formelle.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.