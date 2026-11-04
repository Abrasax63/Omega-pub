# OBS-V19-UNIVERSAL10 — V19 — témoin universel U42 jusqu’à multiplicité 10

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Il existe une endofonction cohérente U42 à 42 états contenant au moins 10 paires d’états distinctes de chacune des 14 classes orientées C5,L=3. Son vecteur exact de multiplicités est [10,10,10,10,20,20,10,40,10,40,100,80,160,160]. Tout multiset de classes orientées de cardinal au plus 10 est donc simultanément réalisable.

## Cadre

- Projet `OBSERVABILITE` ; type `EXACT_CALCULATION` ; version `1`.
- Domaine : V19; cycle orienté C5; observation binaire; L=3; classes C5O-00..13; paires distinctes.
- Hypothèses : OBS-V19-C5-ORIENTED14; cohérence des contraintes forcées
- Statut SQLite : **CALCUL EXACT** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Construction explicite : bassin binaire maximal de profondeur 3 (40 états) + un 2-cycle disjoint. Comptage exact de toutes les paires distinctes.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-UNIVERSAL10-REPORT` — `INTERNAL_AUDIT` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-UNIVERSAL10-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/v19_multiplicity_capacity.py`.
- `EVID-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-UNIVERSAL10-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/V19_UNIVERSAL10_U42_2026-10-15.json`.
- Source `SRC-V19-CAPACITY-2026-10-15` (AUDIT_AND_CERTIFICATE) : V19_MULTIPLICITE_CAPACITE_2026-10-15.md — /Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05-OBS-V19-UNIVERSAL10` : `PASS` / `RAVI2_ADVERSARIAL` ; `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`.

## Relations et versions

- `DEPEND_DE` : `OBS-V19-UNIVERSAL10` → `OBS-V19-C5-ORIENTED14`. Le vecteur U42 est compté dans les 14 classes orientées exactes.
- `ILLUSTRE` : `OBS-V19-PAIR-COMPLETE14` → `OBS-V19-UNIVERSAL10`. U42 renforce la complétude faible ordre en fournissant ≥10 occurrences distinctes de chaque classe.
- `ILLUSTRE` : `OBS-V19-FIRST-OBSTRUCTION11` → `OBS-V19-UNIVERSAL10`. Dépendance historique de la preuve v1 ; la v2 dépend causalement de OBS-V19-COEX-REGION.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-UNIVERSAL10`.*
