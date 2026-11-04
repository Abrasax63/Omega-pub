# EXT-OAI-MATCH-CORNER — Compression fidèle des coins de Brauer et support commun

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour e²=e dans D_m, r=rang(e), il existe un morphisme unitaire injectif R_e:eD_me→D_r conservant le rang. Pour tout J⊆[m], il existe J′⊆[r], dépendant seulement de e,J et de la numérotation, |J′|≤|J|, tel que supp(R_e(eae))⊆J′ pour tout a supporté dans J.

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `THEOREM` ; version `1`.
- Domaine : Monoïdes de diagrammes de Brauer
- Hypothèses : m entier≥0; Couplages parfaits, collage et suppression boucles internes; e idempotent; Supprimer seulement les caps imposés par e, garder ceux entre ports retenus
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Preuve source2.2(i),(iii) reconstruite et auditée ; tests exhaustifs degrés0..4 ; pas certification Lean ni application universelle aux automates.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-MATCH-CORNER-LOT2` — `PROOF` / `INTERNAL_RECONSTRUCTION` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Source `SRC-OAI129-CORNERS` (PRIMARY_PROVENANCE) : An exponential two-way deterministic state lower bound for one-way liveness — https://github.com/openai/math/blob/main/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-MATCH-CORNER-LOT2` : `PASS` / `SOURCE_AND_ADVERSARIAL` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Test `REG-EXT-OAI-MATCH-CORNER-LOT2` : `PASS` / `EXACT_OR_PROOF` ; `/PREUVES_DECOMPOSITION_LOT2_2026-10-15.zip` ; date `2026-10-15T06:01:20.056233+00:00`.

## Relations et versions

- `DEPEND_DE` : `EXT-OAI-MATCH-CORNER` → `EXT-OAI-MATCH-RANK`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- `DEPEND_DE` : `EXT-OAI-UNIT-LIFT` → `EXT-OAI-MATCH-CORNER`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-DECOMPOSE-03`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-MATCH-CORNER`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, section 1, issue du manuscrit OpenAI *An exponential two-way deterministic state lower bound for one-way liveness*, lemme 2.2(i),(iii), pp.5–7. Pour un idempotent e de rang r dans le monoïde de Brauer D_m, le coin eD_me se représente par un morphisme injectif unitaire R_e vers D_r, préservant exactement le rang. Le rapport reconstruit aussi un support commun J' indépendant de l'élément, avec |J'|≤|J|. **Limites :** cela compresse une structure multiplicative déjà située dans le coin, pas un automate arbitraire ; idempotence indispensable ; originalité non évaluée et preuve non compilée dans Lean.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.