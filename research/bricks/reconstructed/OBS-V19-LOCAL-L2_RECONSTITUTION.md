# OBS-V19-LOCAL-L2 — V19 — petit modèle temporel L+2

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Sous cohérence forcée, l’ombre sur un cycle distingué Cq, q≥3, d’une paire à horizon L≥2 est déterminée par le cycle complet et les deux trajectoires aux temps0..L+2. Les composantes ou feuilles forcées sans état pertinent ne changent pas cette projection existentielle.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Endofonction finie ; observation binaire ; cycle Cq, q≥3 ; ombre de mauvais événement à L observations.
- Hypothèses : cohérence de toutes les contraintes forcées; binaire; L≥2; q≥3
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Source et argument d’élimination des feuilles relus ; 82880 tests de colorations full/local sur2590 systèmes C5 tirés, n≤18,L=2..4. Test aléatoire de localité, pas énumération complète des13 classes. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; SHA `cfd9b3703b914930e802b940097a451885a1ff2ba89845cb0d749ba4fbe023e7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-V19` (PRIMARY) : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-LOCAL-L2` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-V19-LOCAL-L2` → `OBS-V19-FORCED-P4`. Preuve de localité utilise la structure des composantes forcées.
- `DEPEND_DE` : `OBS-V19-C5-13` → `OBS-V19-LOCAL-L2`. Complétude de la réduction temporelle dans la carte v2 ; non le simple nombre observé dans une énumération.
- `DEPEND_DE` : `OBS-V19-C5-ORIENTED14` → `OBS-V19-LOCAL-L2`. Complétude de l’énumération orientée repose sur le petit modèle temporel L+2.
- `DEPEND_DE` : `OBS-V19-COEX-SMALLMODEL` → `OBS-V19-LOCAL-L2`. La borne de coexistence utilise la détermination de chaque ombre par les préfixes jusqu’à L+2.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-LOCAL-L2`.*


## Sources retrouvées — complément documentaire

Sources retrouvées : `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` et `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`. Le petit modèle affirme que sous cohérence forcée, l'ombre sur un cycle C_q d'une paire à horizon L≥2 dépend seulement du cycle et des deux préfixes de trajectoire aux temps 0,…,L+2. Pour C5,L=3, cela réduit à six états temporels par trajectoire (temps 0 à 5). La note du 25 septembre rapporte 99 545 comparaisons global/local sans divergence ; le rapport d'assemblage utilise ensuite ce lemme dans la borne de petit modèle pour k ombres, N≤q+2k(L+3)+max(3,2k). **Limite :** les essais ne remplacent pas la preuve de localité ; vérifier la correspondance exacte entre la définition primaire de l'ombre et l'encodage.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.