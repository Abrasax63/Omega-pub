# EXT-OAI-MATCH-RANK — Rang et support des diagrammes de Brauer

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour a,b diagrammes de Brauer de degré m : r(ab)≤min(r(a),r(b)), m−r(a)≤|supp(a)|, supp(ab)⊆supp(a)∪supp(b). Si e²=e, |supp(e)|≤2(m−r(e)).

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `LEMMA` ; version `1`.
- Domaine : Monoïdes de diagrammes de Brauer
- Hypothèses : m entier ≥0; Couplages parfaits sur deux rangées de m ports; Produit par collage puis élimination des boucles internes; Rang = nombre de transversaux; Support = indices sans paire verticale fixe; Idempotence indispensable pour la dernière borne
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Certification interne par preuve reconstruite, source primaire ciblée et deux implémentations du même assistant ; ni audit humain, ni Lean, ni réplication tierce. Transfert aux projets non démontré.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-MATCH-RANK` — `RECONSTRUCTED_PROOF` / `INTERNAL_RECHECKED` ; `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` ; SHA `2e0efc71ea4ac084af09c5addefde680171728c15b2cca082509c5b2d6d21fa9`.
- `EVID-SOURCE-EXT-OAI-MATCH-RANK` — `PRIMARY_PDF` / `TARGETED_READ` ; `/source_129.pdf` ; SHA `612819217a2929102a0e55c00cc4fb606b733d1f90dda513d42bf47783e0a92e`.
- Source `SRC-OAI-129` (PRIMARY_LEMMA) : An exponential two-way deterministic state lower bound for one-way liveness — https://github.com/openai/math/blob/main/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf.
- Source `SRC-OAI-EXTRACTION` (PROOF_AND_SCOPE) : EXTRACTION_BRIQUES_OPENAI_2026-10-15.md — `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-MATCH-RANK` : `PASS_SCOPED` / `INTERNAL_ADVERSARIAL` ; `/COMMIT_BRIQUES_OPENAI_2026-10-15.md`.
- Test `TEST-EXT-OAI-MATCH-RANK` : `PASS` / `EXACT_FINITE` ; `/BRIQUES_OPENAI_VERIFICATION_2026-10-15.py` ; date `2026-10-15T04:59:27.623385+00:00`.

## Relations et versions

- `DEPEND_DE` : `EXT-OAI-MATCH-CORNER` → `EXT-OAI-MATCH-RANK`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- `DEPEND_DE` : `EXT-OAI-UNIT-LIFT` → `EXT-OAI-MATCH-RANK`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-BRICKS-01`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-MATCH-RANK`.*
