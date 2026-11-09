# Réconciliation des revues et audits historiques — lot 03 (10 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** Discovery v0.2, tests comparatifs de contrats, phases strictes v1.3 (1 à 5), Structural Graph v0.2, recherche élargie des originaux et réconciliation cartes/SQLite.  
**Nature :** lecture et réconciliation documentaire. Aucun prototype ni script historique n'a été exécuté dans ce lot.

## 1. Fichiers examinés et empreintes Git source

| Fichier | SHA Git source |
|---|---|
| `RAVI2_DISCOVERY_V02_AUDIT.md` | `70291b1952645b624985df68760b4f87eadae869` |
| `RAVI2_PARALLEL_CONTRACT_TEST_2026-10-16.md` | `ba42bc7853e7ef33bc1cabc5bf5c3e490143397f` |
| `RAVI2_STRICT_CONTRACTS_PHASE1_2026-10-16.md` | `65865cd51737bd98fe3ce6a9a39020a65254ee12` |
| `RAVI2_STRICT_CONTRACTS_PHASE2_2026-10-16.md` | `1dfe235da1755d3d20c5939bb2dc0b394effaa88` |
| `RAVI2_STRICT_CONTRACTS_PHASE3_2026-10-16.md` | `7800cfc7e397f8d0f8327b0dbef129da255feb28` |
| `RAVI2_STRICT_CONTRACTS_PHASE4_2026-10-16.md` | `2e317f35bd8014cc526686c4c844a07bec5a1ec3` |
| `RAVI2_STRICT_CONTRACTS_PHASE5_2026-10-16.md` | `0fcd60a36ba511d6b365f0d6e47e058e1f784b91` |
| `RAVI2_STRUCTURAL_GRAPH_V02_AUDIT.md` | `f1ac228fcdd1db8d1689d818eb1a114bfdb9236a` |
| `RECHERCHE_ELARGIE_CARTES_ORIGINALES_2026-11-04.md` | `d88030fc7eb1da7a0caebe534158ee9587c38dfb` |
| `RECONCILIATION_CARTES_RESULTATS_SQLITE_V33_2026-11-04.md` | `b48b5b5fc448942e663b8e4f0f6bca925c20aed9` |

## 2. Discovery et Structural Graph : outils de triage, jamais arbitres scientifiques

### Discovery v0.2

Le rapport décrit un prototype non certifiant qui combine des signatures typées et un graphe structurel. Sur son instantané :
- 84 résultats admissibles signés ;
- 51 contrats stricts disponibles ;
- 40 candidats de triage conservés ;
- 39 candidats v0.1 restent à revoir et un est reclassé comme connu/classique.

Le top 10 contient des rapprochements V19, Mealy, affine et Δ_h. Les scores sont des priorités de revue, pas des probabilités de vérité ni des preuves d'unification. La garde `TRIAGE_ONLY` interdit de les utiliser comme théorèmes, dépendances, revendications de nouveauté ou prémisses scientifiques.

### Structural Graph v0.2

Le rapport historique décrit une base expérimentale séparée, alimentée en lecture seule depuis le noyau scientifique. Il rapporte 79/79 résultats signés, 44 types d'atomes, 717 liens résultat→atome, 505 arêtes de triage et 89 attracteurs récurrents. L'attracteur ciblé Δ_h/Mealy/V19 a été retrouvé sans règle spécifique à ces identifiants dans l'extracteur.

Mais l'audit précise lui-même que la proximité structurelle ne démontre pas une abstraction mathématique commune. Les évaluateurs automatiques et la couche bibliographique étaient seulement référencés, pas exécutés automatiquement. Ce résultat établit la récupération d'un motif dans le graphe expérimental, pas un théorème transversal.

### Décision

Discovery et Structural Graph restent des couches de génération et de classement. Aucun candidat, score ou attracteur ne doit créer automatiquement une relation `DEPEND_DE` ou entrer dans le noyau scientifique.

## 3. Test comparatif : contrats stricts contre ranking générique

`RAVI2_PARALLEL_CONTRACT_TEST` rapporte deux expériences séparées.

**Branche A — formalisation stricte :** sur 11 contrats pilotes, 8/8 dépendances réelles sont vérifiées et 5/5 contrôles négatifs restent non vérifiés ; deux dépendances nécessitent une garde explicite. Le test met en évidence le besoin de représenter garde, substitution/interface map et base de vérification.

**Branche B — découverte aveugle :** sur 75 cartes et 5 550 couples dirigés, la baseline lexicale surpasse l'heuristique structurée générique aux principaux seuils de rappel (par exemple rappel@300 : 0,825 contre 0,650 ; rappel@1000 : 0,925 contre 0,875). La nouvelle heuristique est donc rejetée comme moteur de certification.

La conclusion historique est une architecture hybride : contrats stricts pour contrôler les compositions ; ranking séparé pour proposer des candidats ; aucune promotion issue du score.

## 4. Phases strictes v1.3 : évolution et limites

Les cinq rapports décrivent une progression historique du miroir expérimental, sans modifier le principe de séparation entre compatibilité des contrats et vérité mathématique.

| Phase | Résultats / admissibles rapportés | DEPEND_DE | Interfaces strictes rapportées | Répartition principale |
|---|---:|---:|---:|---|
| 1 | 75 / 71 | 40 | 18/32 du périmètre ciblé | 17 compositions, 1 référence de validation, 14 différées |
| 2 | 75 / 71 | 40 | 32/32 du périmètre V19/affine/Mealy | 29 compositions, 1 validation, 2 références de données |
| 3 | 75 / 71 | 40 | 40/40 | 35 compositions, 1 validation, 2 données, 2 définitions |
| 4 | 76 / 72 | 42 | 42/42 | 37 compositions, 1 validation, 2 données, 2 définitions |
| 5 | 77 / 73 | 44 | 44/44 | 39 compositions, 1 validation, 2 données, 2 définitions |

### Phase 1

20 contrats stricts sont décrits. Le système distingue applicabilité, import de conclusion, variantes gardées, référence de validation et éléments non classifiés. La péremption d'une version de résultat invalide les certifications d'interface devenues obsolètes. Les 14 interfaces non couvertes sont différées plutôt que certifiées par défaut.

### Phase 2

Des adaptateurs sémantiques explicites sont ajoutés pour fermer les 14 interfaces différées. Les relations de données sont correctement séparées des compositions. Les gardes comme `p<1`, le support exact ou la non-vacuité restent des hypothèses du contrat.

### Phase 3

Les huit dépendances restantes du graphe causal historique sont auditées. Deux relations sont classées comme références de définition, non comme compositions. L'application d'un théorème externe de sparsification reste une application d'un résultat connu, pas une nouvelle preuve de ce théorème.

### Phase 4

Le contrat de `BR-AFFINE-GAUGE-CORE` est ajouté avec une garde `NO_COMMON_TRANSLATION` et un adaptateur vers les équations groupées. Le rapport distingue cette promotion scientifique rapportée de la simple découverte par score.

### Phase 5

`BR-MEALY-HELLY-01` est ajouté avec deux interfaces causales, dont une sous garde (q\ge3). Le rapport affirme une couverture stricte de 44/44 interfaces au snapshot concerné.

### Limite commune

Ces certificats sont des certificats internes de compatibilité entre contrats, versions, hypothèses, gardes et adaptateurs. Ils ne constituent ni une preuve Lean externe, ni une validation humaine tierce, ni une certification automatique de la vérité de chaque théorème. Les compteurs sont propres aux instantanés datés et ne doivent pas être transposés sans contrôle à la base actuelle.

## 5. Cartes originales : recherche élargie et rapprochement SQLite

### Recherche élargie

Le rapport indique une recherche dans 1 501 éléments de Library et des requêtes exactes/sémantiques sur les 42 identifiants initiaux. Il rapporte dix cartes originales retrouvées et restaurées, sans carte originale individuelle supplémentaire pour les 32 identifiants restants.

Les rapports, scripts, archives, jeux de données et documents sources retrouvés pour certains identifiants restent des preuves ou sources, pas des cartes individuelles. La recherche élargie n'autorise donc aucune conversion artificielle d'un rapport en carte originale.

### Réconciliation cartes / SQLite v33

L'instantané initial du rapport comptabilise :
- 85 résultats admissibles ;
- 26 liaisons d'évidence explicites vers une carte ;
- 17 correspondances par nom, ensuite confirmées sémantiquement ;
- 42 résultats sans carte individuelle correspondante à cette étape ;
- quatre fichiers composites hors table des résultats.

Les compléments du rapport confirment 17/17 correspondances de contenu, mais précisent que les 17 liaisons explicites manquent toujours dans SQLite v33. Les quatre fichiers `GLOBAL-LOC-01`, `NS-P55-COMP-01`, `OSC-ITER-01` et `OSC-REAL-01` sont classés comme interfaces/certificats composites, sans rattachement artificiel à un `result_id`.

L'absence de carte individuelle ne signifie ni absence de preuve, ni fausseté du résultat. Elle décrit uniquement l'absence d'un fichier de carte autonome dans le dossier examiné.

## 6. Écarts, précautions et décisions

1. **Triage ≠ preuve :** les candidats Discovery et attracteurs structurels ne sont pas des prémisses.
2. **Contrat strict ≠ preuve du théorème :** la compatibilité d'une interface n'établit pas la vérité de l'énoncé consommé.
3. **Garde ≠ détail optionnel :** les conditions logiques, constantes, domaines et adaptateurs font partie du contrat certifié.
4. **Référence de données/définition ≠ composition :** conserver les types distincts.
5. **Baseline lexicale meilleure :** l'heuristique structurée générique testée est rejetée pour la tâche benchmarkée ; ne pas annoncer un progrès général du ranking.
6. **Instantanés datés :** les comptes 75/71/40, 76/72/42 et 77/73/44 sont des états successifs du miroir expérimental, pas les compteurs actuels garantis.
7. **Cartes manquantes :** 32 reconstitutions ne remplacent pas les originaux ; les preuves annexes ne sont pas automatiquement des cartes.
8. **SQLite :** aucune liaison manquante ne doit être créée sans source et correspondance confirmées.

## 7. Décision de réconciliation

- Conserver Discovery et Structural Graph comme couches non certifiantes.
- Conserver les contrats stricts versionnés et leurs gardes ; ne pas généraliser leur couverture au-delà des périmètres historiques rapportés.
- Ne pas réhabiliter l'heuristique structurée générique comme moteur de certification.
- Maintenir les 32 reconstitutions séparées des originaux.
- Conserver les quatre documents composites hors de la table des résultats.
- Ne pas écrire dans SQLite, ne pas modifier `main`, ne pas fusionner les branches.

## 8. Limites de ce lot

Aucun script, calcul, checker, test, notebook ou preuve Lean n'a été exécuté. Les chiffres de couverture, benchmarks et reconstructions sont ceux déclarés dans les audits historiques. Aucune base SQLite n'a été consultée ou modifiée. Aucun statut scientifique n'est renouvelé.

**Verdict :** dix documents réconciliés documentairement. Les couches de découverte, de contrats stricts et de migration sont distinguées ; aucun résultat scientifique n'est promu par cette opération.
