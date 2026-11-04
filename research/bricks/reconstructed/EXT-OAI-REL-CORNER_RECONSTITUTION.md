# EXT-OAI-REL-CORNER — Isomorphisme exact du coin de relations par restriction

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour H fini,F⊆H,i=I_F,P²=P et iPi=i, poser Q=PiP. Alors Q²=Q,PQ=QP=Q et θ:QR_HQ→R_F,θ(Z)=iZi est un isomorphisme unitaire d’inverse A↦PAP. Compression du seul coin, pas de R_H entier.

## Cadre

- Projet `OUTILS_MATH_EXTERNES` ; type `THEOREM` ; version `1`.
- Domaine : Relations binaires finies
- Hypothèses : Composition en ordre des chemins; P idempotent; iPi=i, égalité exacte de relations; F vide autorisé
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Preuve source2.4 reconstruite et audit croisé ;448 couples,1955 éléments,275869 produits exacts sur0..3 points. Aucun transfert V19 certifié.

## Preuves et provenance SQLite

- `EVID-EXT-OAI-REL-CORNER-LOT2` — `PROOF` / `INTERNAL_RECONSTRUCTION` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Source `SRC-OAI129-CORNERS` (PRIMARY_PROVENANCE) : An exponential two-way deterministic state lower bound for one-way liveness — https://github.com/openai/math/blob/main/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf.

## Audits et tests enregistrés

- Audit `AUD-EXT-OAI-REL-CORNER-LOT2` : `PASS` / `SOURCE_AND_ADVERSARIAL` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Test `REG-EXT-OAI-REL-CORNER-LOT2` : `PASS` / `EXACT_OR_PROOF` ; `/PREUVES_DECOMPOSITION_LOT2_2026-10-15.zip` ; date `2026-10-15T06:01:20.056233+00:00`.

## Relations et versions

Aucune relation enregistrée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-DECOMPOSE-03`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `EXT-OAI-REL-CORNER`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, section 3, issue du manuscrit OpenAI, lemme 2.4, p.8. Dans le monoïde des relations binaires R_H, avec i=I_F, P²=P et iPi=i, poser Q=PiP. Le rapport établit Q²=Q, PQ=QP=Q et l'isomorphisme unitaire θ:QR_HQ→R_F, θ(Z)=iZi, d'inverse A↦PAP. Les conditions iPi=i et P²=P sont nécessaires, avec contre-exemples documentés. **Limite :** réduction du seul coin QR_HQ, pas de toutes les relations sur H ; pas de transfert automatique à V19.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.