# DELTA-P3-N5 — Séparation minimale P3 sans P2 à n=5

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Le seul spectre fini non vide à n=5 est D={2}; un témoin est T=(0,0,0,1,2), π=(0,1,2,2,3). Cela donne P3 sans P2 et reconfirme n=5 comme première taille possible pour cette séparation.

## Cadre

- Projet `DELTA_H_FERMETURE` ; type `EXACT_COUNTEREXAMPLE` ; version `1`.
- Domaine : Systèmes déterministes finis, partitions non étiquetées; définition D={h:Δ_h≠∅}.
- Hypothèses : Aucune liste distincte enregistrée.
- Statut SQLite : **CALCUL EXACT** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Énumération exhaustive de tous les couples (T,π) jusqu’à n=5 dans le rapport du 17 septembre.

## Preuves et provenance SQLite

- `EVID-DELTA-P3-N5-SRC-HIST-DELTA-SPECTRUM` — `DOCUMENT` / `SOURCE_REVIEWED` ; `SRC-HIST-DELTA-SPECTRUM`.
- Source `SRC-HIST-DELTA-SPECTRUM` (PRIMARY_OR_AUDIT) : rapport_spectre_defauts_iteration_1.md — `file_00000000ed8881f59415ddbc532fa5b0`.

## Audits et tests enregistrés

Aucun audit ni test lié.

## Relations et versions

Aucune relation enregistrée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `BASELINE-PRE-COMMIT`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `DELTA-P3-N5`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `rapport_spectre_defauts_iteration_1.md` (17 septembre 2026), section 5. Le rapport énumère tous les couples (T,π) jusqu'à n=5 : 162 500 couples, 19 spectres distincts à n=5. Le seul spectre fini non vide est D={2}, avec T=(0,0,0,1,2), π=(0,1,2,2,3), témoin de P3 sans P2. **Limite :** témoin et comptes rapportés dans cette source ; l'énumération n'est pas rejouée dans cette mise à jour.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.