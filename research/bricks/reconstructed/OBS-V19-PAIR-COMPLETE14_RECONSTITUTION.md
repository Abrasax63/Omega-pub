# OBS-V19-PAIR-COMPLETE14 — V19 — compatibilité paire complète des 14 classes orientées

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour chacune des 105 paires non ordonnées avec répétition des 14 classes orientées C5 à L=3, il existe une endofonction finie cohérente et deux paires d’états distinctes comme paires non ordonnées produisant les deux classes demandées.

## Cadre

- Projet `OBSERVABILITE` ; type `EXACT_CALCULATION` ; version `2`.
- Domaine : V19; C5 orienté; L=3; classes propres modulo rotations C5.
- Hypothèses : classification OBS-V19-C5-ORIENTED14; cohérence des contraintes forcées
- Statut SQLite : **CALCUL EXACT** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Version v2 : correction adversariale de la notion de multiplicité. Les 105/105 anciens systèmes contiennent une affectation par deux paires distinctes ; CSV v2 corrigé revérifié exactement.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-PAIR-COMPLETE14-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; SHA `af61889a8fe12472c23d2159de6919e494ed12a14c7b3cc8d69b448882a6d3a7`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-PAIR-COMPLETE14-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; SHA `a0cf990271fc055cc1f9f49aa4b2df515c7088032b7ddc3ad9105ab310bd0f2a`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-PAIR-COMPLETE14-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_PAIR_WITNESSES_C5O14_2026-10-15.csv` ; SHA `313316b60e9a37d218ed41b338bbf88a01b68d44b46ec56a6f62a436fbbbf84e`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-PAIR-COMPLETE14-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-PAIR-COMPLETE14-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_multiplicity_capacity.py`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-PAIR-COMPLETE14-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_PAIR_WITNESSES_C5O14_DISTINCT_V2_2026-10-15.csv`.
- Source `SRC-V19-ASSEMBLY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_ASSEMBLAGE_ORIENTE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md.
- Source `SRC-V19-CAPACITY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_MULTIPLICITE_CAPACITE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04-OBS-V19-PAIR-COMPLETE14` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`.
- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-PAIR-COMPLETE14` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.
- Test `TEST-OBS-V19-PAIR-COMPLETE14-V19-ASSEMBLY` : `PASS` / `EXACT_ENUMERATION` ; `/Recherche/04_CODE_DONNEES/v19_assembly_exact.py` ; date `2026-10-15T07:51:50.059222+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-V19-PAIR-COMPLETE14` → `OBS-V19-C5-ORIENTED14`. Les 105 certificats sont indexés par les 14 classes orientées exactes.
- `ILLUSTRE` : `OBS-V19-PAIR-COMPLETE14` → `OBS-V19-UNIVERSAL10`. U42 renforce la complétude faible ordre en fournissant ≥10 occurrences distinctes de chaque classe.
- Version 1 : `HISTORICAL`, prémisse `0`, commit `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`.
- Version 2 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-PAIR-COMPLETE14`.*


## Sources retrouvées — complément documentaire

Sources retrouvées : `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` et `V19_MULTIPLICITE_CAPACITE_2026-10-15.md`. Le rapport orienté examine les 105 paires non ordonnées avec répétition des 14 classes C5 modulo rotations et fournit un témoin pour chacune. L'audit de multiplicité corrige les cas où une même paire d'états avait été réutilisée : 105/105 sont ensuite réalisés avec deux paires d'états distinctes, qui peuvent partager un état mais ne sont pas le même objet combinatoire. Les témoins atteignent au plus 17 états. **Portée :** compatibilité par paires des labels de classes, pas preuve d'une loi générale pour les copies géométriques exactes ; le quotient orienté doit être préservé.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.