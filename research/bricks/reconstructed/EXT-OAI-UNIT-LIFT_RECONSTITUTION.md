# EXT-OAI-UNIT-LIFT — Relèvement des unités au coin de rang minimal

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

S⊆D_m non vide stable par produit, φ:S→M surjective multiplicative et q²=q. Il existe e²=e∈S avec φ(e)=q. Pour e de rang minimal dans cette fibre idempotente, R_e(eSe)→qMq est surjective unitaire et chaque y∈eSe dont φ(y) est unité se réduit à une permutation, unité de R_e(eSe). Ne fournit pas de section homomorphe.

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `THEOREM` ; version `1`.
- Domaine : Semi-groupes finis et diagrammes de Brauer
- Hypothèses : S inclus dans D_m fini; φ surjective multiplicative; q idempotent; e de rang minimal parmi tous les idempotents de fibre q
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Preuve source2.3 reconstruite ; contre-exemple sans minimalité. Pas énumération exhaustive des surjections générales.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-UNIT-LIFT-LOT2` — `PROOF` / `INTERNAL_RECONSTRUCTION` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Source `SRC-OAI129-CORNERS` (PRIMARY_PROVENANCE) : An exponential two-way deterministic state lower bound for one-way liveness — https://github.com/openai/math/blob/main/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-UNIT-LIFT-LOT2` : `PASS` / `SOURCE_AND_ADVERSARIAL` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Test `REG-EXT-OAI-UNIT-LIFT-LOT2` : `PASS` / `EXACT_OR_PROOF` ; `/PREUVES_DECOMPOSITION_LOT2_2026-10-15.zip` ; date `2026-10-15T06:01:20.056233+00:00`.

## Relations et versions

- `DEPEND_DE` : `EXT-OAI-UNIT-LIFT` → `EXT-OAI-MATCH-CORNER`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- `DEPEND_DE` : `EXT-OAI-UNIT-LIFT` → `EXT-OAI-MATCH-RANK`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-DECOMPOSE-03`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-UNIT-LIFT`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, section 2, issue du manuscrit OpenAI, lemme 2.3, p.7. Pour un semigroupe fini S et une surjection multiplicative φ vers M, un idempotent q du quotient admet un relèvement idempotent e de rang minimal dans sa fibre. Sous cette minimalité, les éléments dont l'image est une unité se réduisent en permutations dans le coin correspondant. Le rapport fournit la preuve via puissances idempotentes et monotonie du rang. **Limites :** le résultat relève les unités individuellement, ne construit pas une section de groupe ; finitude et minimalité sont essentielles ; aucune application à la fermeture quantique n'est démontrée.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.