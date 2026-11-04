# OBS-RESTRICT-COUNT — Précoloration : comptage exact des collisions et CNF des traces

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour T:X→X fini total déterministe, L≥1, coloration binaire et paire x≠y, former le graphe simple des arêtes {T^t x,T^t y},0≤t<L, sans boucles ni doublons. Sous précoloration rho et complétion libre uniforme indépendante, la probabilité de collision est0 si une composante contient deux bits fixés opposés, et2^(u−m) sinon, m nombre de sommets libres incidents, u nombre de composantes sans bit fixé. Dans ce second cas, la distinction résiduelle est une CNF exacte de2^u clauses de largeur m ; vide de variables implique une clause vide fausse. Avant restriction, largeur≤2L.

## Cadre

- Projet `OBSERVABILITE` ; type `THEOREM` ; version `1`.
- Domaine : Observabilité passive finie binaire, traces de l’état initial
- Hypothèses : T total déterministe; L entier≥1; Variables couleurs, sans auxiliaires; Complétion libre uniforme indépendante; Sommets du graphe = extrémités des arêtes non boucles
- Statut SQLite : **DÉMONTRÉ** ; originalité : `APPLICATION_CONNUE`.
- Note de confiance SQLite : Preuve par composantes reconstruite par deux agents ; audit croisé ;506556 contrôles rationnels principaux. Certification interne, pas nouveauté ni expertise humaine.

## Preuves et provenance SQLite

- `EVID-OBS-RESTRICT-COUNT-PROOF` — `PROOF` / `INTERNAL_MULTIAGENT_RECONSTRUCTED` ; `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`.
- Source `SRC-OBS-RESTRICT-CYCLE` (PRIMARY_INTERNAL_ARTIFACT) : CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md — /CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md.

## Audits et tests enregistrés

- Audit `AUD-OBS-RESTRICT-COUNT` : `PASS` / `ADVERSARIAL_RECONSTRUCTION` ; `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`.
- Test `REG-OBS-RESTRICT-COUNT` : `PASS` / `EXACT` ; `/PREUVES_MULTIAGENT_OBSERVABILITE_2026-10-15.zip` ; date `2026-10-15T05:14:38.404945+00:00`.

## Relations et versions

- `ILLUSTRE` : `OBS-RESTRICT-COUNT` → `OBS-V9-RANK`. Même famille graphes de paires ; aucune dépendance aux preuves historiques.
- `DEPEND_DE` : `OBS-RESTRICT-GREEDY` → `OBS-RESTRICT-COUNT`. Formule exacte des espérances conditionnelles utilisée.
- `DEPEND_DE` : `APP-OBS-SPARSE-DISJOINT` → `OBS-RESTRICT-COUNT`. Dépendance du contrat démontré ; pas simple voisinage thématique.
- `ILLUSTRE` : `OBS-RESTRICT-OVERLAP` → `OBS-RESTRICT-COUNT`. Même objet conditionnel, preuve de recouvrement autonome ; pas de dépendance au domaine V19.
- `DEPEND_DE` : `OBS-RESTRICT-PROFILE` → `OBS-RESTRICT-COUNT`. La loi se construit à partir de la valeur conditionnelle déjà certifiée.
- Version 1 : `ACTIVE`, prémisse `1`, commit `COMMIT-RAVI2-2026-10-15-OBS-RESTRICTIONS-02`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OBS-RESTRICT-COUNT`.*


## Sources retrouvées — complément documentaire

Source retrouvée : `CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`, section « Résultat de transfert exact — OBS-RESTRICT-COUNT v1 ». Pour une paire x≠y, le graphe G_xy porte les arêtes {T^t x,T^t y}, 0≤t<L, boucles et doublons supprimés. Les traces coïncident exactement lorsque chaque composante est monochromatique. Après précoloration ρ, sans conflit de couleurs fixées, si m sommets sont libres et u composantes n'ont aucune couleur fixée, P(collision|ρ)=2^(u−m) ; avec un conflit, cette probabilité vaut 0. Le rapport donne aussi une CNF exacte sur les seules variables couleur, de largeur ≤2L. **Limite :** largeur bornée n'implique pas un nombre de clauses polynomial en L ; aucune identification à un nombre de capteurs n'est autorisée.

> Ce complément ne remplace pas la fiche originale introuvable et ne vaut pas réaudit indépendant. Les statuts SQLite sont conservés sans promotion.