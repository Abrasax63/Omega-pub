# Réconciliation des revues et audits historiques — lot 06 (2 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** audit de consolidation SQLite v33 et audit Discovery v0.1. Ces deux chemins complètent les 45 autres fichiers de `reviews/` déjà rapprochés dans les lots précédents.  
**Nature :** lecture et réconciliation documentaire ; aucun script ni base SQLite n'a été exécuté ou modifié.

## 1. Fichiers examinés et empreintes Git source

| Fichier | SHA Git source |
|---|---|
| `RAVI2_CONSOLIDATION_AUDIT_2026-11-04.md` | `3e5045fc0d09b4b85ab86c71d01420de6ed72459` |
| `RAVI2_DISCOVERY_V01_2026-10-19.md` | `348e71d723412a8713314abfd596357eade42537` |

## 2. Audit de consolidation RAVI-2 / SQLite v33

L'audit du 4 novembre décrit une lecture seule de SQLite v33, taille 819 200 octets, SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.

Compteurs consignés :
- 89 lignes `results`, 85 admissibles ;
- 74 DÉMONTRÉ et 11 CALCUL EXACT parmi les admissibles ;
- 49 relations `DEPEND_DE`, 83 relations au total ;
- 217 entrées `evidence`, 177 relations `result_sources` ;
- 62 tests enregistrés PASS.

Le rapport indique zéro résultat sans relation `result_sources`, zéro liaison orpheline et zéro extrémité de relation absente. La carte `METHOD-RAVI-2` est reliée à `RESEARCH_METHOD_RAVI2.md` par une preuve de provenance documentaire `SOURCE_LOCATED`.

Le graphe mémoire comprend sept nœuds actifs, huit liens et un snapshot de sept éléments. L'audit vérifie l'intégrité référentielle, pas la pertinence sémantique de chacun des liens.

Les 62 tests PASS ne sont pas tous rejoués. Les miroirs `MEMORY_INDEX.md` et `RESEARCH_SNAPSHOT_ACTIVE.md` concordent sur les compteurs principaux mais leurs en-têtes ne consignent pas toutes les réparations techniques postérieures. La base binaire n'est pas transférée dans le dépôt public ; l'empreinte n'est pas un substitut au fichier.

Ce document complète les contrôles techniques de v33 examinés au lot 05. Il ne certifie ni la validité mathématique des 85 résultats ni la complétude de leurs preuves.

## 3. Discovery v0.1 : prototype inter-projets non certifiant

Le rapport du 19 octobre identifie une limite structurelle du moteur de candidats v1.3 : il excluait les paires de résultats appartenant à des projets différents. Le prototype Discovery v0.1 a été construit en lecture seule pour proposer des candidats inter-projets à partir de 79 résultats admissibles et produire 40 candidats diversifiés.

Le document compare plusieurs systèmes de découverte (AI Co-Scientist, ERA/AlphaEvolve, SciAgents, ResearchAgent/Scideator, outils de preuve et graphes bibliographiques) et propose une architecture en couches :
- noyau scientifique conservateur ;
- signatures structurelles ;
- opérateurs de découverte ;
- classement par scores séparés ;
- falsification RAVI-2 ;
- recherche bibliographique ;
- preuve/calcul ;
- commit uniquement après certification.

Le premier candidat concret, `BR-ACC-01 ↔ BR-STATE-01`, conduit à un énoncé de commutation entre accessibilité et quotient prédictif. Le rapport indique un contrôle historique de 41 018 cas exhaustifs pour (n\le3) et 20 000 cas aléatoires pour (n=4..8), sans violation. Le résultat reste en staging et n'est pas promu dans le noyau ; son idée générale est reconnue comme classique en théorie des automates/congruences.

Les autres rapprochements (Mealy/V19, mémoire quantique, détection, temps, Δ_h) sont explicitement des pistes et tests proposés, pas des théorèmes. Le rapport recommande un cycle « découverte large → certification étroite », et interdit au moteur de découverte de créer des dépendances ou de promouvoir un résultat.

## 4. Articulation avec Discovery v0.2 et Structural Graph

Les lots précédents ont examiné les audits v0.2. La chronologie documentaire est :
1. Discovery v0.1 : 79 admissibles, 40 candidats, découverte inter-projets heuristique ;
2. Structural Graph v0.2 : extraction d'atomes/signatures et attracteurs, toujours `TRIAGE_ONLY` ;
3. Discovery v0.2 : contrats et signatures typés, 84 résultats admissibles dans son instantané ;
4. test comparatif parallèle : l'heuristique structurée générique est inférieure à la baseline lexicale sur le benchmark publié ;
5. contrats stricts : couche séparée pour vérifier les interfaces et leurs gardes, sans transfert de pouvoir de certification au ranking.

Cette chronologie ne signifie pas que chaque version améliore la précédente sur toutes les métriques. Le test comparatif négatif doit rester attaché à l'évaluation de l'heuristique structurée générique.

## 5. Décision de réconciliation

- Conserver Discovery v0.1 comme prototype de triage historique, non comme moteur de vérité.
- Conserver le pont accès/quotient prédictif en staging tant que son intégration et son audit bibliographique ne sont pas achevés.
- Conserver les rapprochements Mealy/V19, quantique, temps et Δ_h comme pistes falsifiables, pas comme correspondances démontrées.
- Conserver les compteurs SQLite v33 comme snapshot historique, sans écrire dans la base.
- Ne pas fusionner les couches Discovery, Structural Graph et certification stricte.

## 6. Limites

Aucun script, calcul, checker, benchmark, test de régression ou requête SQLite n'a été exécuté dans ce lot. Les résultats cités proviennent des audits historiques. Aucun statut scientifique n'est renouvelé.

**Verdict :** les deux derniers fichiers de `reviews/` sont réconciliés. Avec les lots 01 à 06 et les audits antérieurs déjà lus, les 47 chemins de revue/audit de l'inventaire sont désormais couverts au niveau documentaire.
