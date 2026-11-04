# APP-OBS-SPARSE-DISJOINT — Sparsification disjointe des contraintes globales d’observabilité

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour X fini de n≥1 états,T total déterministe,L≥1 fixé,couleurs binaires,la CNF H de séparation de toutes les traces L a largeur≤2L. Pour tout η>0 fixé,le théorème connu de sparsification disjointe donne H=Σ_a H_a en indicatrices,au plus2^(ηn) pièces CNF sur les mêmes variables,de largeur≤2L et chacune≤M(L,η)n clauses. Supports de solutions disjoints ; #solutions et sommes pondérées se somment exactement.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Observabilité passive binaire et CNF de largeur fixée
- Hypothèses : L et η fixes pour constantes asymptotiques; Encodage couleur sans auxiliaires de OBS-RESTRICT-COUNT; Théorème externe Dell–Husfeldt–Wahlén2010 appendiceA importé; Aucun avantage de solveur ni constante numérique M évalués
- Statut SQLite : **DÉMONTRÉ** ; originalité : `APPLICATION_CONNUE`.
- Note de confiance SQLite : Application d’un théorème classique importé depuis source primaire indépendante. Preuve globale non réauditée ;12960 identités locales testées et exemple11=9+2. Aucune dépendance au lemme signé.

## Preuves et provenance SQLite

- `EVID-APP-OBS-SPARSE-DISJOINT-LOT2` — `EXTERNAL_THEOREM_APPLICATION` / `PRIMARY_THEOREM_IMPORTED` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Source `SRC-DHW2010-SPARSE` (PRIMARY_PROVENANCE) : Exponential Time Complexity of the Permanent and the Tutte Polynomial — https://eccc.weizmann.ac.il/report/2010/078/download/.

## Audits et tests enregistrés

- Audit `AUD-APP-OBS-SPARSE-DISJOINT-LOT2` : `PASS` / `SOURCE_AND_ADVERSARIAL` ; `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`.
- Test `REG-APP-OBS-SPARSE-DISJOINT-LOT2` : `PASS` / `EXACT_OR_PROOF` ; `/PREUVES_DECOMPOSITION_LOT2_2026-10-15.zip` ; date `2026-10-15T06:01:20.056233+00:00`.

## Relations et versions

- `DEPEND_DE` : `APP-OBS-SPARSE-DISJOINT` → `OBS-RESTRICT-COUNT`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OAI-DECOMPOSE-03`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `APP-OBS-SPARSE-DISJOINT`.*
