# EXT-OAI-REL-SELECT — Sélecteurs élémentaires de relations

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour H fini et I_i={(i,i)}, en composition dans l’ordre des chemins : I_i A I_j={(i,j)} si (i,j)∈A, et vide sinon. Deux relations distinctes sont séparées par de tels contextes.

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `LEMMA` ; version `1`.
- Domaine : Relations binaires finies
- Hypothèses : Composition dans l’ordre des chemins; Sélecteurs singleton autorisés pour la conséquence contextuelle
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Certification interne par preuve reconstruite, source primaire ciblée et deux implémentations du même assistant ; ni audit humain, ni Lean, ni réplication tierce. Transfert aux projets non démontré.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-REL-SELECT` — `RECONSTRUCTED_PROOF` / `INTERNAL_RECHECKED` ; `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` ; SHA `2e0efc71ea4ac084af09c5addefde680171728c15b2cca082509c5b2d6d21fa9`.
- `EVID-SOURCE-EXT-OAI-REL-SELECT` — `PRIMARY_PDF` / `TARGETED_READ` ; `/source_129.pdf` ; SHA `612819217a2929102a0e55c00cc4fb606b733d1f90dda513d42bf47783e0a92e`.
- Source `SRC-OAI-129` (PRIMARY_LEMMA) : An exponential two-way deterministic state lower bound for one-way liveness — https://github.com/openai/math/blob/main/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf.
- Source `SRC-OAI-EXTRACTION` (PROOF_AND_SCOPE) : EXTRACTION_BRIQUES_OPENAI_2026-10-15.md — `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-REL-SELECT` : `PASS_SCOPED` / `INTERNAL_ADVERSARIAL` ; `/COMMIT_BRIQUES_OPENAI_2026-10-15.md`.
- Test `TEST-EXT-OAI-REL-SELECT` : `PASS` / `EXACT_FINITE` ; `/BRIQUES_OPENAI_VERIFICATION_2026-10-15.py` ; date `2026-10-15T04:59:27.623385+00:00`.

## Relations et versions

Aucune relation enregistrée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-BRICKS-01`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-REL-SELECT`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`, carte 1, issue du manuscrit *An exponential two-way deterministic state lower bound for one-way liveness*, §5, lemme 5.2, pp.18–19. Pour I_i={(i,i)}, le produit I_i A I_j vaut {(i,j)} si (i,j)∈A, sinon vide. Un couple de sélecteurs distingue donc deux relations différentes par le test vide/non vide. Le rapport attribue explicitement cette propriété à des travaux antérieurs. **Limite :** la séparation n'est disponible que si les sélecteurs sont des contextes autorisés ; la transposition aux historiques conversationnels est seulement une proposition méthodologique.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.