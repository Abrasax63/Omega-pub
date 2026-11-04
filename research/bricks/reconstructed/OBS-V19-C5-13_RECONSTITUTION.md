# OBS-V19-C5-13 — V19 corrigé — 13 types orbitaux locaux sur C5

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Sous cohérence des contraintes forcées, pour une endofonction finie avec C5 distingué, observation binaire et L=3, les deux préfixes jusqu’au temps5 déterminent l’ombre. La source V19(2) rapporte l’énumération exacte de3341 diagrammes locaux et13 classes D5 d’ombres propres, toutes réalisables.

## Cadre

- Projet `OBSERVABILITE` ; type `EXACT_CLASSIFICATION` ; version `3`.
- Domaine : Endofonction finie avec C5 distingué; observation binaire; L=3; paire potentiellement hors composante de C5.
- Hypothèses : C5 distingué; binaire; L=3; cohérence des contraintes forcées
- Statut SQLite : **CALCUL EXACT** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : CALCUL EXACT désormais reproduit indépendamment le 15 octobre 2026 : génération reconstruite de 3341 diagrammes non diagonaux, projection exacte, 13 classes D5 avec répartition codimension 1/2/3 = 4/5/4. Le théorème de localité L+2 reste la dépendance de complétude. Certification interne ; originalité indéterminée.

## Preuves et provenance SQLite

- `EVID-OBS-V19-C5-13-SRC-HIST-OBS-V19-25` — `DOCUMENT` / `SOURCE_REVIEWED` ; `SRC-HIST-OBS-V19-25`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; SHA `cfd9b3703b914930e802b940097a451885a1ff2ba89845cb0d749ba4fbe023e7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-13-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; SHA `af61889a8fe12472c23d2159de6919e494ed12a14c7b3cc8d69b448882a6d3a7`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-13-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; SHA `a0cf990271fc055cc1f9f49aa4b2df515c7088032b7ddc3ad9105ab310bd0f2a`.
- Source `SRC-COMMIT-V19` (PRIMARY) : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md.
- Source `SRC-HIST-OBS-V19-25` (PRIMARY_OR_AUDIT) : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(1).md — file_00000000752c82108d2e46083194270b.
- Source `SRC-V19-ASSEMBLY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_ASSEMBLAGE_ORIENTE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-13` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-C5-13` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.
- Test `TEST-OBS-V19-C5-13-V19-ASSEMBLY` : `PASS` / `EXACT_ENUMERATION` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; date `2026-10-15T07:51:50.059222+00:00`.

## Relations et versions

- `REMPLACE_HYPOTHESE` : `OBS-V19-C5-13` → `OBS-V19-MATCHING-GLOBAL`. La classification corrigée utilise la caractérisation exacte des contraintes singleton au lieu du matching global.
- `ETEND_SCOPE` : `OBS-V19-C5-13` → `OBS-V19-GAMMA-CONNECTED`. Le résultat à 13 types traite des paires pouvant vivre dans d’autres composantes; le théorème Γ à 12 types reste valide dans son domaine connecté restreint.
- `DEPEND_DE` : `OBS-V19-C5-13` → `OBS-V19-LOCAL-L2`. Complétude de la réduction temporelle dans la carte v2 ; non le simple nombre observé dans une énumération.
- `DEPEND_DE` : `OBS-V19-TRIPLE-COMPLETE13` → `OBS-V19-C5-13`. Les 455 certificats sont indexés par la classification D5 à 13 classes.
- `ILLUSTRE` : `OBS-V19-C5-ORIENTED14` → `OBS-V19-C5-13`. Raffinement de symétrie pour l’assemblage : D5 reste correct pour une ombre isolée ; C5 conserve l’orientation commune.
- Version 1 : `HISTORICAL`, prémisse `0`, commit `BASELINE-PRE-COMMIT`.
- Version 2 : `HISTORICAL`, prémisse `0`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.
- Version 3 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-C5-13`.*


## Sources retrouvées — complément documentaire

Sources retrouvées : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md (25 septembre 2026) et NOTE_RECHERCHE_V19_FORME_NORMALE_13_OMBRES.md. La note de grammaire décrit les contraintes forcées, la structure P1–P4, la localité L+2 et, pour C5,L=3, l'énumération de 3 341 diagrammes locaux donnant 13 classes D5 d'ombres propres non vides. Elle distingue ces 13 ombres dynamiquement réalisables de 10 seulement observées dans les gaps N≤12. Elle rapporte des audits finis jusqu'à N=11 et 99 545 comparaisons global/local sans divergence. Attention aux versions : une note antérieure profondeur-phase décrit 12 types orbitaux ; elle ne doit pas être amalgamée sans versionnement avec la classification 13 issue de la note ultérieure.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.