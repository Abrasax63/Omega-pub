# Q-RQ4-PAULI-ROBUST — RQ-Q-4 — seuil Pauli et borne scalaire optimale

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour les six préparations Pauli et P_m(a,b)=(1+(-1)^b t a_m)/2, t>0 assure rang2 et intersection commune réduite aux constantes. Sous p=P_m f_m, si δ est le maximum des écarts entre sommes non sélectives pour différents axes, |f_m(0,r,z)−f_m(1,r,z)|≤2δ/t. La constante est optimale pour une question finale scalaire ; à t=0 le rang tombe à1.

## Cadre

- Projet `QUANTIQUE` ; type `THEOREM` ; version `1`.
- Domaine : Premier canal dépolarisant, paramètre0<t≤1 ; contextes Pauli ; probabilités finales scalaires.
- Hypothèses : six préparations±X±Y±Z; factorisation alternative p=P_m f_m; f indépendante de a au-delà de b; 0<t≤1
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Preuve directe par comparaison m+ et m− ; 21 contrôles rationnels de rang et égalité scalaire. Aucune réalisation CPTP globale de l’égalité scalaire revendiquée. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Quantique/NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md` ; SHA `ca90f76aa2ddb06032a53846347141fa7a102bf2ebdd8946d0ac2c9399d68833`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-RQ4` (PRIMARY) : NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md — /Recherche/02_PROGRAMMES_ACTIFS/Quantique/NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-Q-RQ4-PAULI-ROBUST` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `ILLUSTRE` : `Q-RQ4-PAULI-ROBUST` → `Q-RQ4-COMMON-RANK`. Le corollaire Pauli vérifie les hypothèses du rang ; la borne scalaire a une preuve directe indépendante.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `Q-RQ4-PAULI-ROBUST`.*
