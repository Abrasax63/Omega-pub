# OBS-V19-TRIPLE-COMPLETE13 — V19 — compatibilité ternaire complète des 13 classes D5

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Les 455 multisets de cardinal 3 des 13 classes D5 de C5,L=3 possèdent tous un témoin commun dans une endofonction finie cohérente avec trois paires d’états distinctes comme paires non ordonnées. Les paires peuvent partager des états mais ne sont jamais répétées à l’identique.

## Cadre

- Projet `OBSERVABILITE` ; type `EXACT_CALCULATION` ; version `2`.
- Domaine : V19; C5; L=3; classes propres modulo D5.
- Hypothèses : classification OBS-V19-C5-13; cohérence des contraintes forcées; quotient D5
- Statut SQLite : **CALCUL EXACT** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Version v2 : 26 anciens certificats réutilisaient au moins une paire identique. Dans chacun des mêmes systèmes, une affectation par trois paires distinctes existe ; 455/455 revérifiés et CSV v2 généré.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-TRIPLE-COMPLETE13-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; SHA `af61889a8fe12472c23d2159de6919e494ed12a14c7b3cc8d69b448882a6d3a7`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-TRIPLE-COMPLETE13-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; SHA `a0cf990271fc055cc1f9f49aa4b2df515c7088032b7ddc3ad9105ab310bd0f2a`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-TRIPLE-COMPLETE13-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` ; SHA `905f764999feed5f74ea72dcf0e5812d0e284c2e2e68b0a82e13ed1f22b4731e`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-TRIPLE-COMPLETE13-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-TRIPLE-COMPLETE13-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_multiplicity_capacity.py`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-TRIPLE-COMPLETE13-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_TRIPLE_WITNESSES_D5_13_DISTINCT_V2_2026-10-15.csv`.
- Source `SRC-V19-ASSEMBLY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_ASSEMBLAGE_ORIENTE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md.
- Source `SRC-V19-CAPACITY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_MULTIPLICITE_CAPACITE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-TRIPLE-COMPLETE13` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`.
- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-TRIPLE-COMPLETE13` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.
- Test `TEST-OBS-V19-TRIPLE-COMPLETE13-V19-ASSEMBLY` : `PASS` / `EXACT_ENUMERATION` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; date `2026-10-15T07:51:50.059222+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-V19-TRIPLE-COMPLETE13` → `OBS-V19-C5-13`. Les 455 certificats sont indexés par la classification D5 à 13 classes.
- `ILLUSTRE` : `OBS-V19-TRIPLE-COMPLETE13` → `OBS-V19-FIRST-OBSTRUCTION11`. Le résultat ternaire distinct est subsumé au niveau des labels orientés par la complétude jusqu’à k=10.
- Version 1 : `HISTORICAL`, prémisse `0`, commit `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`.
- Version 2 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-TRIPLE-COMPLETE13`.*
