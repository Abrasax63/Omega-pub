# OBS-RESTRICT-GREEDY — Construction de coloration par espérance conditionnelle des collisions

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour une famille finie P de paires dans le contrat OBS-RESTRICT-COUNT, poser B(rho)=Σ_P P(collision|rho). Choisir chaque bit libre minimisant B donne B non croissant car B=(B_0+B_1)/2. Si B(rho_initiale)<1, toute complétion produite ainsi a zéro collision dans P. Si P contient toutes les paires distinctes, les traces longueur L sont injectives. B≥1 est inconclusif.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Conception de colorations binaires pour observabilité passive finie
- Hypothèses : Contrat OBS-RESTRICT-COUNT; Toutes les paires ciblées sont incluses dans P; Comparaison exacte des deux espérances; Seuil strict B<1 pour garantie
- Statut SQLite : **DÉMONTRÉ** ; originalité : `APPLICATION_CONNUE`.
- Note de confiance SQLite : Méthode standard des espérances conditionnelles ; preuve auditée au deuxième cycle par agent distinct ;4 exemples contrôlés. Aucune indépendance des collisions nécessaire. Aucun gain comparatif mesuré.

## Preuves et provenance SQLite

- `EVID-OBS-RESTRICT-GREEDY-PROOF` — `PROOF` / `INTERNAL_MULTIAGENT_RECONSTRUCTED` ; `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`.
- Source `SRC-OBS-RESTRICT-CYCLE` (PRIMARY_INTERNAL_ARTIFACT) : CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md — /CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-OBS-RESTRICT-GREEDY` : `PASS` / `ADVERSARIAL_RECONSTRUCTION` ; `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`.
- Test `REG-OBS-RESTRICT-GREEDY` : `PASS` / `EXACT` ; `/PREUVES_MULTIAGENT_OBSERVABILITE_2026-10-15.zip` ; date `2026-10-15T05:14:38.404945+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-RESTRICT-GREEDY` → `OBS-RESTRICT-COUNT`. Formule exacte des espérances conditionnelles utilisée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OBS-RESTRICTIONS-02`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-RESTRICT-GREEDY`.*
