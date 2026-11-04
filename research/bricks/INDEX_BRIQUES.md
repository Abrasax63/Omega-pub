> **Note de migration — 2026-11-03 :** le fichier source ci-dessous conserve son contenu historique. La base SQLite version 33, interrogée sur sa vue `certified_active_results`, retourne 85 résultats actifs admissibles (74 DÉMONTRÉ, 11 CALCUL EXACT), alors que ce texte mentionne 83 cartes admissibles. Cette divergence de comptage n'a pas été réconciliée carte par carte ; utiliser SQLite comme référence et ne pas traiter le nombre 83 ci-dessous comme le compte courant.

---

# Index consolidé des briques réutilisables

## Commit actif TWO-EQUAL-GAPS-25 — 20 octobre 2026

BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01 v1 : **DÉMONTRÉ interne**, originalité **INDÉTERMINÉE**. Pour g,delta>=1 et 1<=a<b entiers, P=10^(g-1), W=P^a0^delta P^b0^delta, T=(a+b)g+2delta, la complexite cyclique vaut p(L)=2+min(L-1,g+delta-2)+min(max(L-g,0),(b-1)g)+min(max(L-(a+1)g,0),ag+delta), 1<=L<=T. Les facteurs speciaux sont exactement Z_L pour 1<=L<=g+delta-2, B_L pour g<=L<=bg-1, C_L pour (a+1)g<=L<=(2a+1)g+delta-1. W est primitif et le premier horizon distinguant toutes les phases est max(bg,(2a+1)g+delta).

Preuve autonome; aucun nouveau DEPEND_DE. Deux contrôles archivés reproduits : 288 familles/6720 longueurs et 1080 familles/40500 longueurs, zéro échec. Revue interne par le même assistant, pas de validation externe. Audit bibliographique ciblé rétrospectif : déviation de séquence explicitement conservée. Certificat : /Recherche/03_AUDITS_CERTIFICATS/TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json. Carte : /Recherche/01_BRIQUES_REUTILISABLES/BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01_BRIQUE.md. Preuve : /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/REPRISE_MULTI_GAP_2026-10-20.md.

État courant après ce commit : **89 cartes / 85 admissibles / 49 DEPEND_DE** ; miroir identique sur les **25 tables communes**, **52 contrats stricts**. Les paragraphes datés antérieurs décrivent des états historiques. Discovery/Structural Graph non régénérés pour ce commit ; leurs compteurs demeurent ceux du précédent état, à 84 résultats admissibles. Aucun automatisme interinterfaces configuré.


Mise à jour de synchronisation : 20 octobre 2026. **Source de vérité :** `/Recherche/00_INDEX_ET_METHODES/RESEARCH_MEMORY.sqlite`, vue `certified_active_results`.

Cet index est une interface de navigation. Il **ne crée, ne promeut, ne fusionne et ne généralise aucun résultat**. Les hypothèses, domaines, preuves et limites restent ceux de la base et des artefacts cités.

**Noyau admissible courant : 83 cartes** (`DÉMONTRÉ` ou `CALCUL EXACT`, actives, `premise_allowed=1`).

## Delta_h / Fermeture

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `BR-ACC-01` | 1 | DÉMONTRÉ | NON_EVALUE | Clôture accessible et défaut d'accès | `/Recherche/01_BRIQUES_REUTILISABLES/BR-ACC-01_CLOTURE_ACCESSIBLE.md` |
| `BR-ACC-STATE-COMMUTE-01` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Commutation clôture accessible / quotient prédictif | `/Recherche/01_BRIQUES_REUTILISABLES/BR-ACC-STATE-COMMUTE-01_BRIQUE.md` |
| `BR-CTRL-01` | 1 | DÉMONTRÉ | REFORMULATION_SPECIALISEE | Certificat cyclique de mémoire locale infinie | `/Recherche/01_BRIQUES_REUTILISABLES/BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md` |
| `DELTA-P3-N5` | 1 | CALCUL EXACT | NON_EVALUE | Séparation minimale P3 sans P2 à n=5 | `SRC-HIST-DELTA-SPECTRUM` |
| `DELTA-SPECTRUM-CLASS` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Classification complète des spectres de défauts Δ_h | `SRC-HIST-DELTA-SPECTRUM` |


## Fermeture différentielle / Schrödinger

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `SCH-POLY-CLOSURE-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Fermeture polynomiale d’un opérateur d’ordre deux | `/Recherche/01_BRIQUES_REUTILISABLES/SCH-POLY-CLOSURE-01_BRIQUE.md` |
| `SCH-SEXTIC-PARITY-01` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Secteur polynomial régulier du potentiel sextique | `/Recherche/01_BRIQUES_REUTILISABLES/SCH-SEXTIC-PARITY-01_BRIQUE.md` |

## Navier–Stokes — briques réutilisables

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `NS-CERT-E-10` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Stabilité quantitative d’une contrainte admissible sous perturbation relative | `/Recherche/03_AUDITS_CERTIFICATS/NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md` |
| `NS-CERT-E-11` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Sommation diagonale contrôlée dans C∞ | `/Recherche/03_AUDITS_CERTIFICATS/NS_CERT_E_11_SOMMATION_DIAGONALE_2026-10-15.md` |
| `NS-CERT-E-12` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Localisation solénoïdale par potentiel | `/Recherche/03_AUDITS_CERTIFICATS/NS_CERT_E_12_13_2026-10-15.md` |
| `NS-CERT-E-13` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Extension lisse par platitude quantitative | `/Recherche/03_AUDITS_CERTIFICATS/NS_CERT_E_12_13_2026-10-15.md` |
| `NS-CERT-E-14` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Inverse radial compact à moment nul | `/Recherche/03_AUDITS_CERTIFICATS/CERTIFICATS_NS_X34_X41_2026-10-15.md` |
| `NS-CERT-E-15` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Primitive périodique et obstruction de moyenne | `/Recherche/03_AUDITS_CERTIFICATS/CERTIFICATS_NS_X34_X41_2026-10-15.md` |

## Observabilité

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `APP-OBS-SPARSE-DISJOINT` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Sparsification disjointe des contraintes globales d’observabilité | `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` |
| `BR-AFFINE-GAUGE-GLUE` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Raccordements affines par paires et obstruction collective | `/V19_TROISIEME_ORDRE_2026-10-15.md` |
| `BR-AFFINE-GAUGE-CORE` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Diagnostic de translation commune ou noyau minimal d’étiquettes | `/GAUGE_CORE_BRIDGE_2026-10-16.md` |
| `BR-AFFINE-GROUP-CORE` | 1 | DÉMONTRÉ | CLASSIQUE / APPLICATION INTERNE | Noyau incompatible affine par groupes et certificat de minimalité | `/AFFINE_GROUP_CORE_2026-10-15.md` |
| `BR-AFFINE-TREE-CORE` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Diagnostic complet sur arbre : composition ou noyau incompatible minimal | `/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md` |
| `BR-AFFINE-TREE-GLUE` | 1 | DÉMONTRÉ | CLASSIQUE / APPLICATION INTERNE | Composition affine sur arbre et comptage par interfaces | `/COMPOSITION_AFFINE_2026-10-15.md` |
| `BR-MEALY-HELLY-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Borne de Helly du nerf de compatibilité des résolveurs Mealy | `/MEALY_HELLY_BRIDGE_2026-10-16.md` |
| `BR-OBS-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Expérience adaptative finie, expérience prédéfinie impossible | `/Recherche/01_BRIQUES_REUTILISABLES/BR-OBS-01_ADAPTATIF_VS_PREDEFINI.md` |
| `BR-OBS-BAD-01` | 1 | DÉMONTRÉ | CONNU_PRINCIPE_GENERAL | Signature affine canonique des mauvais objets | `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_N11_2026-10-15.md` |
| `BR-OBS-CAP-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Capacité dynamique d’un motif local | `/Recherche/04_CODE_DONNEES/V19_GEOMETRIC_CAPACITY_85_AUDIT_2026-10-15.csv` |
| `BR-OBS-CAP-02` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Capacité de support et poids des circuits | `/Recherche/04_CODE_DONNEES/V19_GEOMETRIC_CAPACITY_85_AUDIT_2026-10-15.csv` |
| `BR-OBS-CAP-03` | 1 | DÉMONTRÉ | CONNU_PRINCIPE_GENERAL | Fibres disjointes, boîte de coexistence et matrice TU | `/Recherche/03_AUDITS_CERTIFICATS/V19_REGION_COEXISTENCE_2026-10-15.md` |
| `BR-OBS-CIRCUIT-01` | 1 | DÉMONTRÉ | CONNU_PRINCIPE_GENERAL | 2-recouvrement exact et bipartition du graphe de chevauchement | `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_N11_2026-10-15.md` |
| `BR-OBS-KRYLOV-01` | 1 | DÉMONTRÉ | CONNU_PRINCIPE_GENERAL | Récupération du générateur d’un sous-espace de Krylov | `/Recherche/01_BRIQUES_REUTILISABLES/BR-OBS-KRYLOV-01_GENERATOR_RECOVERY.md` |
| `BR-OBS-REVEAL-KERNEL` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Noyau des covariances et couvertures exactes conservés sous révélation | `/V19_N11_MOMENTS_ET_NOYAU_2026-10-15.md` |
| `OBS-AFFINE-GROUP-CORE-VALIDATION` | 1 | CALCUL EXACT | VALIDATION INTERNE / AUCUNE PRIORITÉ REVENDIQUÉE | Validation exacte du détecteur et essais de blocages collectifs | `/AFFINE_GROUP_CORE_2026-10-15.md` |
| `OBS-M27-BINARY` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Mealy27 — collapse binaire | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-M27-CONFLICT` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Mealy27 — noyaux de conflit bornés | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-M27-FERTILE` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Mealy27 — largeur fertile q−1 | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-M27-SPECTRUM` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Mealy27 — spectre aigu des conflits | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-RESTRICT-AFFINE` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Moments conjoints de restrictions affines : phase relative et poids de révélation | `/TRANSFERT_AFFINE_V19_2026-10-15.md` |
| `OBS-RESTRICT-COUNT` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Précoloration : comptage exact des collisions et CNF des traces | `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md` |
| `OBS-RESTRICT-FORCED-QUOTIENT` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Révélation sous oppositions forcées : quotient affine pondéré et transfert V19 | `/TRANSFERT_AFFINE_V19_2026-10-15.md` |
| `OBS-RESTRICT-GREEDY` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Construction de coloration par espérance conditionnelle des collisions | `/CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md` |
| `OBS-RESTRICT-MULTIMOMENT` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Moments conjoints affines à tout ordre sous révélation | `/V19_TROISIEME_ORDRE_2026-10-15.md` |
| `OBS-RESTRICT-OVERLAP` | 1 | DÉMONTRÉ | APPLICATION_CONNUE | Invariant de recouvrement : covariance, Fourier–Walsh et Tutte | `/TEST_SYNTHESE_INVERSE_2026-10-15.md` |
| `OBS-RESTRICT-PROFILE` | 1 | DÉMONTRÉ | NON_EVALUE | Loi exacte et reconstruction du profil des composantes sous restriction | `/TEST_SYNTHESE_INVERSE_2026-10-15.md` |
| `OBS-V19-BAD-FIBER2` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V19 — fibre paire vers mauvais objet de taille au plus 2 | `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_FIBER2_2026-10-15.md` |
| `OBS-V19-C5-13` | 3 | CALCUL EXACT | INDÉTERMINÉ | V19 corrigé — 13 types orbitaux locaux sur C5 | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-V19-C5-CAPACITY` | 2 | DÉMONTRÉ | INDÉTERMINÉ | V19 — spectre exact des capacités géométriques orientées sur C5 | `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md` |
| `OBS-V19-C5-ORIENTED14` | 1 | CALCUL EXACT | INDÉTERMINÉ | V19 — raffinement orienté C5 : 14 classes | `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` |
| `OBS-V19-COEX-REGION` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V19 — région exacte de coexistence des 70 ombres orientées | `/Recherche/03_AUDITS_CERTIFICATS/V19_REGION_COEXISTENCE_2026-10-15.md` |
| `OBS-V19-COEX-SMALLMODEL` | 2 | DÉMONTRÉ | INDÉTERMINÉ | V19 — petit modèle pour la coexistence de k ombres | `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` |
| `OBS-V19-FIRST-OBSTRUCTION11` | 2 | DÉMONTRÉ | INDÉTERMINÉ | V19 — premier ordre d’obstruction de multiplicité : k*=11 (classification complète) | `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md` |
| `OBS-V19-FORCED-P4` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V19 — composantes forcées P1 à P4 | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-V19-GAMMA-CONNECTED` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V19 — grammaire Γ des ombres dans un bassin connecté vers Cq | `SRC-HIST-OBS-V19-24` |
| `OBS-V19-LOCAL-L2` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V19 — petit modèle temporel L+2 | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `OBS-V19-N11-BADOBJECT` | 2 | CALCUL EXACT | INDÉTERMINÉ | V19 — reconstruction exacte des cinq premières ruptures N=11 au niveau des mauvais objets | `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_N11_2026-10-15.md` |
| `OBS-V19-N11-MOMENT-GRAM` | 1 | CALCUL EXACT | APPLICATION_CONNUE | N11 : matrices exactes des moments et conservation des cinq circuits de 2-recouvrement | `/V19_N11_MOMENTS_ET_NOYAU_2026-10-15.md` |
| `OBS-V19-N11-THIRD-ORDER` | 1 | CALCUL EXACT | NON_EVALUE | N11 : lois par paires identiques, intersections triples différentes | `/V19_TROISIEME_ORDRE_2026-10-15.md` |
| `OBS-V19-PAIR-COMPLETE14` | 2 | CALCUL EXACT | INDÉTERMINÉ | V19 — compatibilité paire complète des 14 classes orientées | `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` |
| `OBS-V19-TRIPLE-COMPLETE13` | 2 | CALCUL EXACT | INDÉTERMINÉ | V19 — compatibilité ternaire complète des 13 classes D5 | `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` |
| `OBS-V19-UNIVERSAL10` | 1 | CALCUL EXACT | INDÉTERMINÉ | V19 — témoin universel U42 jusqu’à multiplicité 10 | `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md` |
| `OBS-V8-FACT-INF` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V8 — factorisation exacte du polynôme d’observabilité à horizon infini | `SRC-HIST-OBS-V10` |
| `OBS-V9-RANK` | 1 | DÉMONTRÉ | INDÉTERMINÉ | V9 — rang des orbites de paires | `SRC-HIST-OBS-V10` |
| `OBS-V9-STAB-N1` | 1 | DÉMONTRÉ | REDONDANT | V9 — stabilisation universelle à N−1 | `SRC-HIST-OBS-V10` |

## Ω — Observateurs adaptatifs

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `OMEGA-O41-DET-V11` | 1 | DÉMONTRÉ | NON_EVALUE | Ω-O4.1 v1.1 — détection empirique sans noyaux diagnostiques | `SRC-HIST-O41-REPORT` |

## Outils mathématiques externes

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `EXT-OAI-MARG-REPAIR` | 1 | DÉMONTRÉ | NON_EVALUE | Réparation simultanée des marginales de permutations | `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` |
| `EXT-OAI-MATCH-CORNER` | 1 | DÉMONTRÉ | NON_EVALUE | Compression fidèle des coins de Brauer et support commun | `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` |
| `EXT-OAI-MATCH-RANK` | 1 | DÉMONTRÉ | NON_EVALUE | Rang et support des diagrammes de Brauer | `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` |
| `EXT-OAI-REL-CORNER` | 1 | DÉMONTRÉ | NON_EVALUE | Isomorphisme exact du coin de relations par restriction | `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` |
| `EXT-OAI-REL-SELECT` | 1 | DÉMONTRÉ | NON_EVALUE | Sélecteurs élémentaires de relations | `/EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` |
| `EXT-OAI-UNIT-LIFT` | 1 | DÉMONTRÉ | NON_EVALUE | Relèvement des unités au coin de rang minimal | `/DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` |

## Quantique

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `BR-Q-PRED-HIDDEN-01` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Séparation prédictive cachée : produit, corrélations et cardinalité | `/Recherche/01_BRIQUES_REUTILISABLES/BR-Q-PRED-HIDDEN-01_BRIQUE.md` |
| `BR-Q-01` | 1 | DÉMONTRÉ | NON_EVALUE | Ambiguïté processus–instruments | `/Recherche/01_BRIQUES_REUTILISABLES/BR-Q-01_AMBIGUITE_PROCESSUS_INSTRUMENTS.md` |
| `BR-Q-SWAP-MEM-01` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Témoin SWAP de mémoire relative aux continuations | `/Recherche/01_BRIQUES_REUTILISABLES/BR-Q-SWAP-MEM-01_BRIQUE.md` |
| `Q-RQ4-COMMON-RANK` | 1 | DÉMONTRÉ | INDÉTERMINÉ | RQ-Q-4 — rang commun et factorisation | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |
| `Q-RQ4-PAULI-ROBUST` | 1 | DÉMONTRÉ | INDÉTERMINÉ | RQ-Q-4 — seuil Pauli et borne scalaire optimale | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |

## Temps / Règle 90

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `BR-R90-01` | 1 | DÉMONTRÉ | NON_EVALUE | Noyaux et période récurrente de Règle 90 | `/Recherche/01_BRIQUES_REUTILISABLES/BR-R90-01_NOYAUX_PERIODES.md` |
| `BR-R90-02` | 1 | DÉMONTRÉ | NON_EVALUE | Uniformité Majority–Walsh avant repliement cyclique | `/Recherche/01_BRIQUES_REUTILISABLES/BR-R90-02_MAJORITY_WALSH.md` |
| `BR-TIME-01` | 1 | DÉMONTRÉ | NON_EVALUE | Résolution intermédiaire sans flèche du temps | `/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-01_RESOLUTION_SANS_FLECHE.md` |
| `BR-TIME-FACTOR-COMPLEX-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Complexité prédictive exacte du compteur réversible sparse | `/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md` |
| `BR-WORD-SINGLE-GAP-COMPLEX-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Complexité exacte d’un mot cyclique à gap exceptionnel unique | `/Recherche/01_BRIQUES_REUTILISABLES/BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md` |
| `BR-TIME-FINDET-BRIDGE-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Distinguabilité de phase versus détection persistante à mémoire finie | `/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FINDET-BRIDGE-01_BRIQUE.md` |

## Transformations / Autonomie

| ID | v | Statut | Originalité | Intitulé | Interface / preuve |
|---|---:|---|---|---|---|
| `BR-DESC-01` | 1 | DÉMONTRÉ | CONNU_PRINCIPE_GENERAL | Suffisance pour une tâche ≠ autonomie de mise à jour | `/Recherche/01_BRIQUES_REUTILISABLES/BR-DESC-01_SUFFISANCE_VS_AUTONOMIE.md` |
| `BR-DESC-02` | 1 | CALCUL EXACT | NON_EVALUE | Bonne marginale, mauvais ordre temporel | `/Recherche/01_BRIQUES_REUTILISABLES/BR-DESC-02_MARGINALE_VS_ORDRE_TEMPOREL.md` |
| `BR-STATE-01` | 1 | DÉMONTRÉ | CONNU_OU_APPARENTE | États prédictifs et réparation canonique | `/Recherche/01_BRIQUES_REUTILISABLES/BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md` |
| `BR-STATE-COST-01` | 1 | DÉMONTRÉ | CONNU_OU_CLASSIQUE | Coût minimal d’extension par fermeture des comportements | `/Recherche/01_BRIQUES_REUTILISABLES/BR-STATE-COST-01_BRIQUE.md` |
| `DET-FIN-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Perte asymptotique de sensibilité d’un détecteur fini à risque total borné | `/Recherche/01_BRIQUES_REUTILISABLES/DET-FIN-01_BRIQUE.md` |
| `DESC-CLIP-01` | 1 | DÉMONTRÉ | NON_EVALUE | Projection locale d’un facteur d’évidence robuste | `/Recherche/01_BRIQUES_REUTILISABLES/DESC-CLIP-01_BRIQUE.md` |
| `DESC-SUM-01` | 1 | DÉMONTRÉ | INDÉTERMINÉ | Détecteur — somme des deux évidences | `/Recherche/03_AUDITS_CERTIFICATS/COMMIT_AUDIT_RAVI2_2026-10-14.md` |

## Raccordement TREE-CORE

`BR-AFFINE-TREE-CORE` relie explicitement les certificats positifs de `BR-AFFINE-TREE-GLUE` aux certificats négatifs minimaux de `BR-AFFINE-GROUP-CORE`. Rapport : `/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md`.


## Raccordement GAUGE-CORE

`BR-AFFINE-GAUGE-CORE` compose `BR-AFFINE-GAUGE-GLUE` avec `BR-AFFINE-GROUP-CORE` : translation commune ou noyau minimal d’étiquettes, avec borne serrée `d+1`. Rapport : `/GAUGE_CORE_BRIDGE_2026-10-16.md`.

## Cartes restaurées depuis la bibliothèque privée — 4 novembre 2026

Ces huit cartes ont été retrouvées dans la bibliothèque privée, relues, puis copiées sans réécriture de leur énoncé dans cette branche. Les statuts et versions reproduisent ceux des cartes sources ; cette opération n'est pas une nouvelle certification mathématique.

| ID | Version | Statut source | Carte |
|---|---:|---|---|
| BR-AFFINE-GAUGE-GLUE | 1 | DÉMONTRÉ interne | `BR-AFFINE-GAUGE-GLUE_BRIQUE.md` |
| BR-AFFINE-GROUP-CORE | 1 | DÉMONTRÉ interne | `BR-AFFINE-GROUP-CORE_BRIQUE.md` |
| OBS-AFFINE-GROUP-CORE-VALIDATION | 1 | CALCUL EXACT interne | `OBS-AFFINE-GROUP-CORE-VALIDATION_BRIQUE.md` |
| OBS-RESTRICT-AFFINE | 1 | DÉMONTRÉ interne | `OBS-RESTRICT-AFFINE_BRIQUE.md` |
| OBS-RESTRICT-FORCED-QUOTIENT | 1 | DÉMONTRÉ interne | `OBS-RESTRICT-FORCED-QUOTIENT_BRIQUE.md` |
| BR-AFFINE-TREE-GLUE | 1 | DÉMONTRÉ interne | `BR-AFFINE-TREE-GLUE_BRIQUE.md` |
| OBS-V19-N11-THIRD-ORDER | 1 | CALCUL EXACT interne | `OBS-V19-N11-THIRD-ORDER_BRIQUE.md` |
| OBS-V19-N11-MOMENT-GRAM | 1 | CALCUL EXACT interne | `OBS-V19-N11-MOMENT-GRAM_BRIQUE.md` |

Les correspondances de titre, d'énoncé, de domaine et de statut ont été comparées aux lignes SQLite v33 correspondantes. Les locateurs de preuve demeurent ceux indiqués dans chaque carte ; ils ne sont pas réputés tous présents dans cette branche.


## Carte restaurée depuis la bibliothèque privée — 4 novembre 2026 (passe complémentaire)

| ID | Version | Statut source | Carte |
|---|---:|---|---|
| BR-OBS-REVEAL-KERNEL | 1 | DÉMONTRÉ interne | `BR-OBS-REVEAL-KERNEL_BRIQUE.md` |


## Carte restaurée depuis une archive de preuves — 4 novembre 2026

La carte `OBS-RESTRICT-MULTIMOMENT` a été extraite comme fichier original de `PREUVES_V19_TROISIEME_ORDRE_2026-10-15.zip`, lue intégralement et comparée au résultat SQLite v33 (énoncé, domaine, hypothèses, statut, originalité et version). Le texte est copié sans réécriture ; restauration documentaire uniquement.

| ID | Version | Statut source | Carte |
|---|---:|---|---|
| OBS-RESTRICT-MULTIMOMENT | 1 | DÉMONTRÉ interne | `OBS-RESTRICT-MULTIMOMENT_BRIQUE.md` |


## 32 fiches reconstituées depuis SQLite v33 — 4 novembre 2026

Les fichiers Markdown individuels d'origine n'ont pas été retrouvés. Les 32 documents ci-dessous sont donc des **reconstitutions documentaires**, explicitement marquées comme telles. Ils reprennent les enregistrements SQLite (énoncés, domaines, hypothèses, statuts, preuves référencées, audits, tests et versions) sans revendiquer de nouvelle validation. Les tests historiques ne sont pas réputés rejoués. Voir aussi le [rapport de récupération historique](../reviews/RECUPERATION_HISTORIQUE_32_RESULTATS_2026-11-04.md).

Dossier : [research/bricks/reconstructed/](reconstructed/)

| Identifiant | Fiche reconstituée |
|---|---|
| APP-OBS-SPARSE-DISJOINT | [fiche](reconstructed/APP-OBS-SPARSE-DISJOINT_RECONSTITUTION.md) |
| DELTA-P3-N5 | [fiche](reconstructed/DELTA-P3-N5_RECONSTITUTION.md) |
| DELTA-SPECTRUM-CLASS | [fiche](reconstructed/DELTA-SPECTRUM-CLASS_RECONSTITUTION.md) |
| DESC-SUM-01 | [fiche](reconstructed/DESC-SUM-01_RECONSTITUTION.md) |
| EXT-OAI-MARG-REPAIR | [fiche](reconstructed/EXT-OAI-MARG-REPAIR_RECONSTITUTION.md) |
| EXT-OAI-MATCH-CORNER | [fiche](reconstructed/EXT-OAI-MATCH-CORNER_RECONSTITUTION.md) |
| EXT-OAI-MATCH-RANK | [fiche](reconstructed/EXT-OAI-MATCH-RANK_RECONSTITUTION.md) |
| EXT-OAI-REL-CORNER | [fiche](reconstructed/EXT-OAI-REL-CORNER_RECONSTITUTION.md) |
| EXT-OAI-REL-SELECT | [fiche](reconstructed/EXT-OAI-REL-SELECT_RECONSTITUTION.md) |
| EXT-OAI-UNIT-LIFT | [fiche](reconstructed/EXT-OAI-UNIT-LIFT_RECONSTITUTION.md) |
| OBS-M27-BINARY | [fiche](reconstructed/OBS-M27-BINARY_RECONSTITUTION.md) |
| OBS-M27-CONFLICT | [fiche](reconstructed/OBS-M27-CONFLICT_RECONSTITUTION.md) |
| OBS-M27-FERTILE | [fiche](reconstructed/OBS-M27-FERTILE_RECONSTITUTION.md) |
| OBS-M27-SPECTRUM | [fiche](reconstructed/OBS-M27-SPECTRUM_RECONSTITUTION.md) |
| OBS-RESTRICT-COUNT | [fiche](reconstructed/OBS-RESTRICT-COUNT_RECONSTITUTION.md) |
| OBS-RESTRICT-GREEDY | [fiche](reconstructed/OBS-RESTRICT-GREEDY_RECONSTITUTION.md) |
| OBS-RESTRICT-OVERLAP | [fiche](reconstructed/OBS-RESTRICT-OVERLAP_RECONSTITUTION.md) |
| OBS-RESTRICT-PROFILE | [fiche](reconstructed/OBS-RESTRICT-PROFILE_RECONSTITUTION.md) |
| OBS-V19-C5-13 | [fiche](reconstructed/OBS-V19-C5-13_RECONSTITUTION.md) |
| OBS-V19-C5-ORIENTED14 | [fiche](reconstructed/OBS-V19-C5-ORIENTED14_RECONSTITUTION.md) |
| OBS-V19-FORCED-P4 | [fiche](reconstructed/OBS-V19-FORCED-P4_RECONSTITUTION.md) |
| OBS-V19-GAMMA-CONNECTED | [fiche](reconstructed/OBS-V19-GAMMA-CONNECTED_RECONSTITUTION.md) |
| OBS-V19-LOCAL-L2 | [fiche](reconstructed/OBS-V19-LOCAL-L2_RECONSTITUTION.md) |
| OBS-V19-PAIR-COMPLETE14 | [fiche](reconstructed/OBS-V19-PAIR-COMPLETE14_RECONSTITUTION.md) |
| OBS-V19-TRIPLE-COMPLETE13 | [fiche](reconstructed/OBS-V19-TRIPLE-COMPLETE13_RECONSTITUTION.md) |
| OBS-V19-UNIVERSAL10 | [fiche](reconstructed/OBS-V19-UNIVERSAL10_RECONSTITUTION.md) |
| OBS-V8-FACT-INF | [fiche](reconstructed/OBS-V8-FACT-INF_RECONSTITUTION.md) |
| OBS-V9-RANK | [fiche](reconstructed/OBS-V9-RANK_RECONSTITUTION.md) |
| OBS-V9-STAB-N1 | [fiche](reconstructed/OBS-V9-STAB-N1_RECONSTITUTION.md) |
| OMEGA-O41-DET-V11 | [fiche](reconstructed/OMEGA-O41-DET-V11_RECONSTITUTION.md) |
| Q-RQ4-COMMON-RANK | [fiche](reconstructed/Q-RQ4-COMMON-RANK_RECONSTITUTION.md) |
| Q-RQ4-PAULI-ROBUST | [fiche](reconstructed/Q-RQ4-PAULI-ROBUST_RECONSTITUTION.md) |

Aucune fiche reconstituée ne remplace un original qui serait retrouvé ultérieurement. Une récupération de l'original devra être conservée séparément et comparée avant toute substitution.


## Enrichissement par sources historiques — 4 novembre 2026

Les 32 fiches de reconstitution ci-dessus ont été enrichies individuellement avec les éléments pertinents retrouvés dans les rapports, manuscrits, audits et données de la bibliothèque privée. Chaque complément indique sa source, le résultat effectivement documenté et les limites de portée. Les fiches demeurent des reconstitutions, pas les cartes Markdown originales. Les statuts SQLite n'ont pas été promus et les contrôles historiques ne sont pas réputés rejoués par cette mise à jour.

## Résultat C4, L=2 — fiche complémentaire conditionnelle

[**C4, L=2 — coexistence des huit classes et minimum conditionnel à 9 états**](C4-L2-COEXISTENCE-MINIMUM-9-CONDITIONAL.md)

Statut : **CALCUL EXACT sous spécification opérationnelle** ; statut mathématique inconditionnel : **À RÉEXAMINER**. La fiche donne le témoin à 9 états, l'énumération exhaustive N=4,…,8 et les trois voies de contrôle rapportées, mais explicite la réserve centrale : l'équivalence complète entre la spécification codée et la définition primaire V19 de l'ombre n'est pas encore certifiée. Cette fiche n'est pas ajoutée au noyau certifié.



## Audit sémantique C4/L2 — 4 novembre 2026

La convention de trajectoire a été rapprochée de la note primaire V19 : pour L=2, le mauvais événement impose l'égalité des couleurs aux temps 0 et 1. Les formulations en inégalité de deux documents archivés sont supersédées. Le catalogue local a été reproduit indépendamment (1 515 diagrammes, 172 ombres propres, 8 classes) ; le témoin à 9 états et l'énumération globale N=4,…,8 ont été rejoués. Voir [le rapport d'audit sémantique](../../reviews/AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md) et [le script indépendant](../code/c4_l2_independent_local_audit_2026-11-04.py).

Statut : **CALCUL EXACT** pour la coexistence des huit classes cataloguées et le minimum 9 sous la définition primaire V19. La certification RAVI-2 finale reste à réexaminer pour la preuve indépendante du lemme de localité L+2, la formalisation et la revue tierce.
