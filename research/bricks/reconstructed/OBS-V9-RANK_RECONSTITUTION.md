# OBS-V9-RANK — V9 — rang des orbites de paires

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour une paire p={x,y} et e_t={T^t x,T^t y}, dès qu’une arête e_t devient dépendante des précédentes dans le graphe non orienté, toutes les suivantes le restent; ainsi rank G_{p,L}=min(L,r_p).

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Endofonction finie; graphe d’orbite de paire.
- Hypothèses : Aucune liste distincte enregistrée.
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Audit V10: statut mathématique PASSÉ; aucun contre-exemple dans l’audit indépendant déclaré.

## Preuves et provenance SQLite

- `EVID-OBS-V9-RANK-SRC-HIST-OBS-V10` — `DOCUMENT` / `SOURCE_REVIEWED` ; `SRC-HIST-OBS-V10`.
- Source `SRC-HIST-OBS-V10` (PRIMARY_OR_AUDIT) : AUDIT_V10.md — `file_00000000430481f49632f4f193e9f25d`.

## Audits et tests enregistrés

- Audit `AUD-HIST-V10-V9` : `PASSÉ` / `INDEPENDENT_COMPUTATION` ; `SRC-HIST-OBS-V10`.

## Relations et versions

- `ILLUSTRE` : `OBS-RESTRICT-COUNT` → `OBS-V9-RANK`. Même famille graphes de paires ; aucune dépendance aux preuves historiques.
- Version 1 : `ACTIVE`, prémisse `1`, commit `BASELINE-PRE-COMMIT`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V9-RANK`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `AUDIT_V10.md` (18 septembre 2026), section V9. Pour une paire p={x,y}, l'arête e_t={T^t x,T^t y} devient dépendante dès qu'elle est dans la fermeture graphique des arêtes précédentes ; appliquer T au chemin reliant ses extrémités donne un chemin pour l'étape suivante. Ainsi rank G_{p,L}=min(L,r_p). L'audit rapporte l'examen exhaustif de toutes les endofonctions de tailles 1 à 6, soit 50 069 systèmes, sans contre-exemple. Le statut de nouveauté du lemme est laissé indéterminé.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.