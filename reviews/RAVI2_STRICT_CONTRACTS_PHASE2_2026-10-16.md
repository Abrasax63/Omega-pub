# RAVI-2 v1.3 — formalisation stricte phase 2

Date : 16 octobre 2026.

## Objet

Fermer les 14 interfaces laissées `DEFERRED_SEMANTIC_ADAPTER` en phase 1, sans modifier la base scientifique principale, les cartes, leurs statuts ou le graphe `DEPEND_DE`.

## Résultat

- Les 14 interfaces différées ont été réauditées avec adaptateurs sémantiques explicites : relations `35, 40, 45, 46, 49, 53, 54, 55, 56, 57, 62, 63, 64, 65`.
- Les 32 dépendances V19/affine/Mealy couvertes par la couche stricte sont maintenant toutes `VERIFIED_APPLICABILITY`.
- 29 sont classées `COMPOSITION`, 1 `VALIDATION_REFERENCE`, 2 `DATA_REFERENCE`.
- Aucune interface différée ne reste dans ce périmètre. Les 8 autres `DEPEND_DE` de la base, hors périmètre strict actuel, ne sont pas promues et restent au niveau v1.3 général.
- 32 contrats stricts et 16 adaptateurs vérifiés sont persistés.

## Adaptateurs ajoutés

- capacité : paire→ombre et boîte de fibres ;
- mauvais objet : canonisation RREF affine et 2-cover→graphe de chevauchement ;
- quotient forcé : passage aux événements affines et aux taux libres `p^m_j` ;
- révélation : application de REVEAL-KERNEL sous la garde `p<1` ;
- Krylov : quotient invariant et croissance stricte ;
- ordre supérieur : événements affines N11, jauges par paires et canal forcé ;
- provenance : identité exacte du jeu des cinq mappings N11, épinglée par SHA256.

## Garde de certification renforcée

Une interface qui nomme un adaptateur sémantique ne peut être certifiée que si cet adaptateur existe, est `VERIFIED`, si `semantic_adapter_match=VERIFIED`, et si les deux résultats restent dans les versions auditées. Deux tests négatifs ont forcé respectivement `semantic_adapter_match=UNVERIFIED` et un identifiant d’adaptateur inexistant : les deux insertions `CERTIFIED` ont été rejetées.

## Dépendances de données

Les relations 56 et 65 sont classées `DATA_REFERENCE`, pas compositions. Elles réutilisent exactement `/Recherche/04_CODE_DONNEES/V19_N11_SOURCE_MAPPINGS_2026-10-15.csv`, SHA256 `0caad9b9757dc1ac96f4717cf8618d0356607f69ca043c4b1d13284713858415`. Les rapports N11 Moments et Troisième ordre indiquent explicitement la conservation des mêmes fixtures, de la normalisation du C5 et de l’indexation des mauvais objets.

## Invariants

- Base principale inchangée : 75 résultats, 71 admissibles, 40 `DEPEND_DE`.
- 23 tables scientifiques communes identiques ligne par ligne entre base principale et miroir expérimental.
- `PRAGMA integrity_check = ok`, 0 erreur de clé étrangère.
- Aucune nouvelle brique scientifique, aucune promotion épistémique, aucune revendication d’originalité.

## Limite

La certification d’interface reste une certification interne de compatibilité entre contrats déjà certifiés. Elle ne remplace ni une preuve formelle externe ni une validation humaine. Les gardes (`p<1`, mauvais objet non vide, support exact 2-cover, etc.) font partie du contrat et ne sont pas supposées vraies pour une entrée arbitraire.

## Reconstruction indépendante

Le moteur strict-aware phase 2 a été exécuté sur un miroir vierge reconstruit depuis la base principale et le registre phase 2 : 32/32 contrats, 32/32 revues et 32/32 certificats d’interface ont été restaurés ; 29 compositions, 1 référence de validation et 2 références de données ; aucune certification stale ; intégrité `ok`, 0 erreur de clé étrangère.

## Reproduction

- registre : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/ravi2_strict_registry_phase2.json`
- vérification : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/RAVI2_STRICT_PHASE2_VERIFY_2026-10-16.json`
- script : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/ravi2_strict_phase2_deploy.py`