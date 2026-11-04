# EXT-OAI-MARG-REPAIR — Réparation simultanée des marginales de permutations

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour une permutation aléatoire A0 sur 2s éléments, J1,J2 listes complémentaires de taille s, ε_i distances TV des injections images à l’uniforme et ε_part distance TV de la partition image à l’uniforme, il existe A avec deux injections images exactement uniformes, uniformes conditionnellement à la partition, et TV(L(A),L(A0))≤ε1+ε2+3ε_part. La dépendance entre bijections est autorisée.

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `LEMMA` ; version `1`.
- Domaine : Probabilités finies sur permutations
- Hypothèses : s entier ≥0; Partition de départ en deux listes fixées de même taille; Partition de sortie conserve l’identité des deux blocs mais oublie leur ordre interne; TV = demi-norme L1
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Certification interne par preuve reconstruite, source primaire ciblée et deux implémentations du même assistant ; ni audit humain, ni Lean, ni réplication tierce. Transfert aux projets non démontré.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-MARG-REPAIR` — `RECONSTRUCTED_PROOF` / `INTERNAL_RECHECKED` ; `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` ; SHA `2e0efc71ea4ac084af09c5addefde680171728c15b2cca082509c5b2d6d21fa9`.
- `EVID-SOURCE-EXT-OAI-MARG-REPAIR` — `PRIMARY_PDF` / `TARGETED_READ` ; `/source_238.pdf` ; SHA `0a520da2d4a92a176e8833ef81fd1d4ecf19c117954c9606577f9d819be5d394`.
- Source `SRC-OAI-238` (PRIMARY_LEMMA) : Random coordinate frames and partial permutation laws — https://github.com/openai/math/blob/main/preprints/Random-coordinate-frames-and-partial-permutation-laws-September-26-2026/main.pdf.
- Source `SRC-OAI-EXTRACTION` (PROOF_AND_SCOPE) : EXTRACTION_BRIQUES_OPENAI_2026-10-15.md — `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-MARG-REPAIR` : `PASS_SCOPED` / `INTERNAL_ADVERSARIAL` ; `/COMMIT_BRIQUES_OPENAI_2026-10-15.md`.
- Test `TEST-EXT-OAI-MARG-REPAIR` : `PASS` / `EXACT_FINITE` ; `/BRIQUES_OPENAI_VERIFICATION_2026-10-15.py` ; date `2026-10-15T04:59:27.623385+00:00`.

## Relations et versions

Aucune relation enregistrée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-BRICKS-01`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-MARG-REPAIR`.*
