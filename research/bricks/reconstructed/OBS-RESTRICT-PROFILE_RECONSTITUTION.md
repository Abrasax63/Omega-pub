# OBS-RESTRICT-PROFILE — Loi exacte et reconstruction du profil des composantes sous restriction

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

G graphe fini d’égalités binaires uniformes indépendantes, profil de tailles(s_i), restrictions indépendantes laissant libre avec probabilité p. Poser a=(1−p)/2 et F_s(z)=2Σ_{j=0}^{s−1}binom(s,j)p^j a^(s−j)z^j+p^s z^(s−1). Alors P(Q=2^-d)=[z^d]∏F_{s_i}, P(Q=0)=1−∏F_{s_i}(1). Moments E Q^t=∏[2(a+p2^-t)^s+(2^t−2)(p2^-t)^s] pour t>0. À n,k fixés,la courbe exacte p↦E Q² sur(0,1) détermine le profil via∏(1+x^s),x=p/(2−p).

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Loi de probabilités conditionnelles de contraintes d’égalité
- Hypothèses : Bits iid uniformes; Restriction par sommet indépendante, homogène, libre probabilité p∈[0,1]; Q=probabilité collision après complétion indépendante; Composantes isolées permises, F_1=1; Reconstruction du profil exige n,k connus et courbe exacte, pas variance à un seul p
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Preuve constructive et reconstruction indépendante ;304 lois,912 moments et272 profils exacts contrôlés. Principes classiques ; pas priorité ni robustesse numérique établies.

## Preuves et provenance SQLite

- `EVID-OBS-RESTRICT-PROFILE-SYNTH08` — `PROOF` / `INTERNAL_MULTIAGENT_RECONSTRUCTED` ; `/TEST_SYNTHESE_INVERSE_2026-10-15.md`.
- Source `SRC-OBS-RESTRICT-SYNTH` (PRIMARY_INTERNAL_ARTIFACT) : TEST_SYNTHESE_INVERSE_2026-10-15.md — /TEST_SYNTHESE_INVERSE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-OBS-RESTRICT-PROFILE-SYNTH08` : `PASS` / `PROOF_AND_ADVERSARIAL` ; `/TEST_SYNTHESE_INVERSE_2026-10-15.md`.
- Test `REG-OBS-RESTRICT-PROFILE-SYNTH08` : `PASS` / `EXACT` ; `/PREUVES_SYNTHESE_INVERSE_2026-10-15.zip` ; date `2026-10-15T15:19:50.564085+00:00`.

## Relations et versions

- `DEPEND_DE` : `OBS-RESTRICT-PROFILE` → `OBS-RESTRICT-COUNT`. La loi se construit à partir de la valeur conditionnelle déjà certifiée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-SYNTHESIS-09`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-RESTRICT-PROFILE`.*
