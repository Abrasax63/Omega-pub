# OBS-RESTRICT-OVERLAP — Invariant de recouvrement : covariance, Fourier–Walsh et Tutte

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

G,H graphes sur le même V, Q_G,Q_H issus de la même restriction homogène indépendante avec probabilité libre p. S_G,S_H espaces F2 engendrés par e_u+e_v des arêtes, r_G,r_H dimensions, C=S_G∩S_H et W_C(t)=Σ_{α∈C}t^|α|. Alors E[Q_GQ_H]=2^(-r_G-r_H)W_C(1−p). Équivalent :2^-rbase E_F2^β(B_F), B multigraphe biparti d’incidence des composantes et F arêtes retenues probabilité1−p. Pour p>0,cela vaut(p/4)^n Z_B(2,2(1−p)/p). Cov≥0 ; pour p<1,Cov=0 ssi C={0},sans implication d’indépendance.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Raccordement de contraintes d’égalité par restriction et codes binaires
- Hypothèses : Même ensembleV et même restriction pour les deux graphes; Bits iid uniformes, restrictions indépendantes homogènes; Complétions des deux facteurs indépendantes conditionnellement à rho; Inclure isolés dans partitions et conserver arêtes parallèles deB; Tutte Z(q,v)=Σ_F q^k(F) v^|F|
- Statut SQLite : **DÉMONTRÉ** ; originalité : `APPLICATION_CONNUE`.
- Note de confiance SQLite : Deux preuves reconstruites (graphes doublés et Fourier), audit croisé ;16664 moments et16664 correspondances binaires vérifiés rationnellement. Contre-exemples mêmes profils et même dimension commune. Aucun transfert V19 forcé ni gain algorithmique certifié.

## Preuves et provenance SQLite

- `EVID-OBS-RESTRICT-OVERLAP-SYNTH08` — `PROOF` / `INTERNAL_MULTIAGENT_RECONSTRUCTED` ; `/TEST_SYNTHESE_INVERSE_2026-10-15.md`.
- Source `SRC-ODONNELL-SYNTH08` (CLASSICAL_ANTECEDENT) : Analysis of Boolean Functions — https://www.cs.cmu.edu/~odonnell/papers/Analysis-of-Boolean-Functions-by-Ryan-ODonnell.pdf.
- Source `SRC-SOKAL-SYNTH08` (CLASSICAL_ANTECEDENT) : The multivariate Tutte polynomial for graphs and matroids — https://discovery.ucl.ac.uk/1522217/1/0503607v1.pdf.

## Audits et tests enregistrés

- Audit `AUD-OBS-RESTRICT-OVERLAP-SYNTH08` : `PASS` / `PROOF_AND_ADVERSARIAL` ; `/TEST_SYNTHESE_INVERSE_2026-10-15.md`.
- Test `REG-OBS-RESTRICT-OVERLAP-SYNTH08` : `PASS` / `EXACT` ; `/PREUVES_SYNTHESE_INVERSE_2026-10-15.zip` ; date `2026-10-15T15:19:50.564085+00:00`.

## Relations et versions

- `ILLUSTRE` : `OBS-RESTRICT-OVERLAP` → `OBS-RESTRICT-COUNT`. Même objet conditionnel, preuve de recouvrement autonome ; pas de dépendance au domaine V19.
- `GENERALISE` : `OBS-RESTRICT-AFFINE` → `OBS-RESTRICT-OVERLAP`. L’ancien contrat homogène reste valable ; preuve affine autonome.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-SYNTHESIS-09`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-RESTRICT-OVERLAP`.*
