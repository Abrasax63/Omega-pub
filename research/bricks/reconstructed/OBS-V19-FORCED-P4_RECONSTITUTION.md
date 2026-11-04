# OBS-V19-FORCED-P4 — V19 — composantes forcées P1 à P4

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour une endofonction finie observée en binaire à horizon L≥2, une contrainte singleton est une fusion Tu=Tv ou une paire invariante {Tu,Tv}={u,v}. Si toutes ces contraintes d’opposition sont cohérentes, chaque composante connexe de leur graphe est un chemin comportant au plus quatre sommets.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Endofonction totale finie ; contraintes binaires forcées ; L≥2.
- Hypothèses : cohérence de toutes les contraintes binaires forcées; L≥2
- Statut SQLite : **DÉMONTRÉ** ; originalité : `INDÉTERMINÉ`.
- Note de confiance SQLite : Preuve par fibres de taille≤2 et invariants de période1/2 ; 29742 systèmes cohérents parmi50069 n≤6 contrôlés exactement. Certification interne de domaine ; ni vérification formelle ni priorité bibliographique certifiée.

## Preuves et provenance SQLite

- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4-SRC` — `PRIMARY_INTERNAL_ARTIFACT` / `SOURCE_REVIEWED` ; `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; SHA `cfd9b3703b914930e802b940097a451885a1ff2ba89845cb0d749ba4fbe023e7`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4-PROOF` — `RECONSTRUCTED_PROOF` / `INTERNAL_PROOF_REVIEWED` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` ; SHA `65fdf60969aebc2ebd5c6f09fc69d43a82d23013d080db45c9767dae412e7214`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4-CODE` — `INDEPENDENT_CODE` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; SHA `17a7e45ed806391f0a1b81823957164d13b87ebe65544540487812480a216657`.
- `EVID-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4-DATA` — `EXACT_CHECK_OUTPUT` / `EXECUTED` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.json` ; SHA `91d0039a2f39d4b0edd0009604d55395f2e92623f31de7edc9747446293857f0`.
- Source `SRC-COMMIT-V19` (PRIMARY) : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md — /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md.

## Audits et tests enregistrés

- Audit `AUD-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4` : `PASS_SCOPED` / `SOURCE_REVIEW_RECONSTRUCTION_FALSIFICATION` ; `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md`.
- Test `TEST-COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM-OBS-V19-FORCED-P4` : `PASS` / `EXACT_FINITE` ; `/Recherche/04_CODE_DONNEES/commit_audit_checks.py` ; date `2026-10-14T17:35:46.225394+00:00`.

## Relations et versions

- `REMPLACE` : `OBS-V19-FORCED-P4` → `OBS-V19-MATCHING-GLOBAL`. Structure correcte remplaçant le candidat global faux ; celui-ci reste historique RÉFUTÉ.
- `DEPEND_DE` : `OBS-V19-LOCAL-L2` → `OBS-V19-FORCED-P4`. Preuve de localité utilise la structure des composantes forcées.
- `DEPEND_DE` : `OBS-V19-C5-CAPACITY` → `OBS-V19-FORCED-P4`. La borne de branchement utilise la cohérence binaire et la structure des fibres forcées.
- `DEPEND_DE` : `OBS-RESTRICT-FORCED-QUOTIENT` → `OBS-V19-FORCED-P4`. Dépendance du seul corollaire m_j∈1..4 ; la réduction générale ne requiert pas cette borne.
- `DEPEND_DE` : `OBS-V19-BAD-FIBER2` → `OBS-V19-FORCED-P4`. Classification P1–P4 des chemins forcés et fibre de T de taille≤2.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-V19-FORCED-P4`.*


## Sources retrouvées — complément documentaire

Sources retrouvées : `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` et `COMMIT_AUDIT_RAVI2_2026-10-14.md`. Pour L≥2, une contrainte singleton correspond à Tu=Tv ou à {Tu,Tv}={u,v}. Sous cohérence binaire, chaque fibre a taille ≤2 ; les arêtes de fusion et d'invariance sont chacune des matchings, mais leur union peut avoir des degrés 3. Les composantes cohérentes sont P1, P2, P3 ou P4. Contre-exemple au matching global : T=(1,0,1,0), avec contraintes {0,1},{0,2},{1,3}, graphe 2–0–1–3, cohérent. Audit rapporté : 50 069 endofonctions n≤6, dont 29 742 cohérentes, sans composante hors P1–P4. Ces chiffres sont historiques, non rejoués ici.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.