# OBS-V19-C5-ORIENTED14 — V19 — raffinement orienté C5 : 14 classes

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour C5 orienté par T(c_i)=c_{i+1}, observation binaire, L=3 et cohérence des contraintes forcées, les 3341 diagrammes locaux non diagonaux produisent exactement 14 classes propres modulo rotations C5, de répartition codimension 1/2/3 = 4/6/4. Le quotient supplémentaire par réflexion D5 fusionne une unique paire chirale de codimension 2 et redonne les 13 classes D5.

## Cadre

- Projet `OBSERVABILITE` ; type `EXACT_CLASSIFICATION` ; version `1`.
- Domaine : Endofonction finie avec cycle distingué C5 orienté; observation binaire; L=3.
- Hypothèses : C5 distingué orienté; binaire; L=3; cohérence des contraintes forcées; équivalence par rotations C5 seulement
- Statut SQLite : **CALCUL EXACT** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Énumération indépendante exacte : 3341 diagrammes ; 14 orbites C5 ; une seule orbite D5 se scinde en deux classes chirales. Code autonome exécuté PASS ; aucune validation humaine externe.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-ORIENTED14-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; SHA `af61889a8fe12472c23d2159de6919e494ed12a14c7b3cc8d69b448882a6d3a7`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-ORIENTED14-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; SHA `a0cf990271fc055cc1f9f49aa4b2df515c7088032b7ddc3ad9105ab310bd0f2a`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-ORIENTED14-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_ORIENTED14_CLASSES_2026-10-15.csv` ; SHA `c4e50406528122b7ffed84ffa8edb417ad01a4d05af101a59a1ff203e54bfcf1`.
- Source `SRC-V19-ASSEMBLY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_ASSEMBLAGE_ORIENTE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-C5-ORIENTED14` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`.
- Test `TEST-OBS-V19-C5-ORIENTED14-V19-ASSEMBLY` : `PASS` / `EXACT_ENUMERATION` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; date `2026-10-15T07:51:50.059222+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-V19-C5-ORIENTED14` → `OBS-V19-LOCAL-L2`. Complétude de l’énumération orientée repose sur le petit modèle temporel L+2.
- `ILLUSTRE` : `OBS-V19-C5-ORIENTED14` → `OBS-V19-C5-13`. Raffinement de symétrie pour l’assemblage : D5 reste correct pour une ombre isolée ; C5 conserve l’orientation commune.
- `DEPEND_DE` : `OBS-V19-PAIR-COMPLETE14` → `OBS-V19-C5-ORIENTED14`. Les 105 certificats sont indexés par les 14 classes orientées exactes.
- `DEPEND_DE` : `OBS-V19-C5-CAPACITY` → `OBS-V19-C5-ORIENTED14`. Les classes et leurs motifs profondeur–phase sont ceux de la classification orientée exacte.
- `DEPEND_DE` : `OBS-V19-UNIVERSAL10` → `OBS-V19-C5-ORIENTED14`. Le vecteur U42 est compté dans les 14 classes orientées exactes.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-C5-ORIENTED14`.*
