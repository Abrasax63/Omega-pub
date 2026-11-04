# Audit de couverture historique et réutilisation — 4 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche examinée :** `migration/ravi2-ccs-public-2026-11-04`  
**Cible canonique :** `main`  
**Nature :** audit documentaire et de couverture ; aucune certification mathématique nouvelle.

## 1. Verdict exécutif

L'audit confirme que la migration est une sélection documentaire substantielle, mais non une migration complète de la bibliothèque privée. Les originaux, les reconstitutions, les rapports, les scripts et les données doivent rester des catégories distinctes.

Aucune modification de `main`, de SQLite v33, des statuts scientifiques ou des dépendances n'a été effectuée dans cet audit.

## 2. Réconciliation RAVI-2 : chiffres à ne pas confondre

Base de référence : SQLite v33, SHA-256  
`ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.

- 85 résultats admissibles dans le périmètre audité : 74 DÉMONTRÉ et 11 CALCUL EXACT.
- Le rapprochement historique initial des cartes individuelles identifiait 47 fichiers, 26 liaisons d'évidence explicites, 17 correspondances par nom et 42 résultats sans carte individuelle correspondante.
- Les 17 correspondances ont depuis été relues sur titre, noyau d'énoncé, hypothèses, statut et version : 17/17 sont sémantiquement confirmées. Les liaisons d'évidence correspondantes dans SQLite restent absentes.
- Parmi les 42 résultats initialement sans carte, 10 cartes originales ont été retrouvées et restaurées dans la branche de migration. Le reliquat actuel est donc de 32 cartes originales non retrouvées.
- 32 fichiers de reconstitution sont présents sous `research/bricks/reconstructed/`. Ils sont marqués « RECONSTITUTION — NON ORIGINALE » et ne sont pas comptés comme originaux.
- Les 32 reconstitutions recopient le statut de SQLite et leurs références, mais ne constituent ni une relecture mathématique indépendante ni un rejeu des tests historiques.

### 2.1 Les dix cartes originales restaurées

1. `BR-AFFINE-GAUGE-GLUE`
2. `BR-AFFINE-GROUP-CORE`
3. `OBS-AFFINE-GROUP-CORE-VALIDATION`
4. `OBS-RESTRICT-AFFINE`
5. `OBS-RESTRICT-FORCED-QUOTIENT`
6. `BR-AFFINE-TREE-GLUE`
7. `OBS-V19-N11-THIRD-ORDER`
8. `OBS-V19-N11-MOMENT-GRAM`
9. `BR-OBS-REVEAL-KERNEL`
10. `OBS-RESTRICT-MULTIMOMENT`

La dernière carte a été retrouvée dans la bibliothèque et dans l'archive V19 ; les deux copies sont identiques, SHA-256 `48b9861443ad2864e836d7a3ab0b968bcd48e5a709e11d4d95cc7060862907f9`.

### 2.2 Les 32 identifiants dont l'original reste absent

- `APP-OBS-SPARSE-DISJOINT`
- `DELTA-P3-N5`, `DELTA-SPECTRUM-CLASS`
- `DESC-SUM-01`
- `EXT-OAI-MARG-REPAIR`, `EXT-OAI-MATCH-CORNER`, `EXT-OAI-MATCH-RANK`, `EXT-OAI-REL-CORNER`, `EXT-OAI-REL-SELECT`, `EXT-OAI-UNIT-LIFT`
- `OBS-M27-BINARY`, `OBS-M27-CONFLICT`, `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM`
- `OBS-RESTRICT-COUNT`, `OBS-RESTRICT-GREEDY`, `OBS-RESTRICT-OVERLAP`, `OBS-RESTRICT-PROFILE`
- `OBS-V19-C5-13`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`, `OBS-V19-GAMMA-CONNECTED`, `OBS-V19-LOCAL-L2`, `OBS-V19-PAIR-COMPLETE14`, `OBS-V19-TRIPLE-COMPLETE13`, `OBS-V19-UNIVERSAL10`
- `OBS-V8-FACT-INF`, `OBS-V9-RANK`, `OBS-V9-STAB-N1`
- `OMEGA-O41-DET-V11`
- `Q-RQ4-COMMON-RANK`, `Q-RQ4-PAULI-ROBUST`

Des rapports, manuscrits, audits, scripts, sorties et archives de preuves ont été retrouvés pour plusieurs groupes. Ils constituent des éléments de provenance et de preuve, pas des cartes individuelles. Aucun énoncé n'est reconstitué de mémoire dans cet inventaire.

### 2.3 Réserves transversales

- L'écart historique entre 26 liaisons explicites, 25 preuves de type carte dans un contrôle SQLite et 22 relations `INTERFACE_CARD` n'est pas résolu ; ces compteurs ne sont pas équivalents.
- `BR-OBS-KRYLOV-01` existe dans la branche et dans la bibliothèque, mais son typage/liaison SQLite est à corriger séparément.
- Les quatre fichiers `GLOBAL-LOC-01`, `NS-P55-COMP-01`, `OSC-ITER-01` et `OSC-REAL-01` sont des documents composites hors table des résultats, pas des cartes autonomes à rattacher artificiellement.
- La base SQLite v33 n'est pas dans le dépôt public. Son empreinte seule n'est pas une sauvegarde.

## 3. Navier–Stokes : backlog autonome minimal de 15 résultats

L'audit du 19 octobre confirme un backlog documentaire minimal de 15 briques autonomes hors de la base structurée :

- neuf briques historiques `NS-CERT-E-01..09`, conservées dans le registre verrouillé v1.1 ;
- six certificats autonomes postérieurs : `NS-X36`, `NS-X46`, estimation B.6, critère abstrait de contraction issu de B.2, `NS-X42` et `NS-X45`.

Les six cartes `NS-CERT-E-10..15` ont, elles, été ajoutées à SQLite par le commit du 15 octobre. Elles ne doivent pas être comptées une seconde fois dans le backlog de 15.

### 3.1 Limite de correspondance

Le registre verrouillé résume les neuf E01–E09 par thèmes, mais la correspondance canonique entre ces numéros E et les identifiants NS-xx de l'audit analytique n'est pas établie dans les pièces examinées. L'audit analytique décrit neuf calculs élémentaires (dérivée matérielle, divergence cylindrique, énergie forcée, résidu inverse, comptabilité anisotrope, changement de viscosité, Reynolds anisotrope, moyenne quadratique et monotonie de q), mais il ne faut pas attribuer automatiquement les numéros E01–E09 à ces éléments.

### 3.2 Frontière scientifique

Le registre ne certifie ni les 26 cartes composites, ni le théorème principal de blow-up. Les sous-briques élémentaires sont réutilisables sous leurs hypothèses exactes ; les preuves profondes, P55-A à D, P75 et les étapes 9.6–10.3 restent à auditer selon leur contrat. Les certificats autonomes postérieurs ont des limites propres : notamment, la proposition 6.6 complète, B.1, B.2 appliquée intégralement et le théorème principal ne sont pas certifiés par les seuls certificats élémentaires.

**Action sûre :** retrouver la version 1.0 du registre et reconstruire la table de correspondance E01–E09 avant tout commit transactionnel. Résoudre aussi la collision d'identifiant autour du label proposé `NS-CERT-E-16` pour X46.

## 4. Chantiers Ω/SRR historiques

### Ω-W07 — poset de communication / Heyting

Statut : **SUSPENDU / NON VÉRIFIÉ**. Le document de cadrage retrouvé indique que les définitions exactes, preuves et certificats calculatoires n'ont pas été retrouvés et relus dans le cycle. Il faut retrouver l'ordre, les opérations, vérifier les infimums/supremums et l'implication de Heyting, puis tester des contre-exemples minimaux et l'antériorité. Le travail ne doit soutenir aucune autre branche Ω tant que ces éléments manquent.

État de migration : aucun fichier W07/Heyting identifiable dans les 220 chemins modifiés de la PR #2.

### Ω-W08 — Kibble–Zurek / champs couplés

Statut : **EMPIRIQUE ANTÉRIEUR / NON RÉAUDITÉ**. Le document retrouvé exige de retrouver code, versions, graines, données brutes, préenregistrement et plages de trempe, puis de recalculer exposants, incertitudes, résidus et sensibilité aux fenêtres. Les valeurs numériques anciennes ne sont pas confirmables dans le cycle actuel.

État de migration : aucun fichier W08/Kibble–Zurek identifiable dans les chemins modifiés de la PR #2. Ne pas relier ce chantier au noyau SRR sans correspondance mathématique précise démontrée.

### Ω-W09 — inventaire legacy / reproductibilité

Statut : `PASS_LEGACY_INVENTORY_SLICE / PARTIAL_REPRODUCIBILITY / NO-GO / authorization=NONE`.

Constats documentés :
- cinq copies de `omega_sim_headless.js` sont byte-identiques (SHA-256 `840f1cef58bafa5d822ebf2acbc9ceaa0cf84c14a075dbf6ac09a9239`) ; une variante distincte ne change que trois paramètres.
- le script headless ne produit que cinq colonnes ; les CSV conservés en ont 26. Le producteur exact des 26 métriques n'a pas été retrouvé.
- les deux rejeux locaux du script sont déterministes, mais ne reproduisent pas le CSV conservé à 235 étapes.
- les instantanés JSON sont structurellement cohérents ; deux CSV sont des préfixes de deux instantanés, mais les trajectoires n'ont pas de registre d'exécution complet.
- les lacunes bloquantes enregistrées sont : producteur exact manquant, environnement/dépendances d'origine manquants, suite de tests headless absente et provenance des variantes/lignées ambiguë.
- le paquet Ω-O4.2 est déclaré rejoué exactement dans son environnement audité (15/15 tests, dix critères, sorties byte-identiques). Cela ne répare pas la provenance omega_sim.
- les fichiers `ai_studio_code*` sont une collision de noms, relatifs à une architecture Android et à des essais de transplantation ; ils ne sont pas le producteur manquant.

Le reçu W09/I2 compte 135 contrôles PASS, mais le verdict reste PARTIAL_REPRODUCIBILITY et NO-GO. Un PASS d'inventaire/QA ne signifie pas que le corpus Ω complet est reproductible.

État de migration : aucun artefact W09/headless/legacy identifiable dans les 220 chemins modifiés de la PR #2. Le registre, le rapport, le manifeste de provenance et les fichiers de données restent des sources Library à préserver.

### Ω-W03 — dépendance externe à ne pas oublier

I8 a préparé le paquet de transfert à un auditeur externe (32/32 contrôles mécaniques), mais l'audit humain et l'indépendance restent en attente. Résultat scientifique `NOT_ESTIMATED`, `authorization=NONE`, confirmatoire `NO-GO`. Même une acceptation du transfert ne fermerait pas C1 ni n'autoriserait une phase confirmatoire en place.

## 5. État GitHub de la PR #2

Comparaison actuelle au 4 novembre 2026 :
- PR #2 toujours en brouillon et non fusionnée ;
- 220 chemins modifiés dans la liste paginée de la PR ;
- branche de migration : 264 commits d'avance et 63 de retard sur `main` ;
- comparaison : `diverged` ;
- `main` au SHA `0e3c4fa322ecac60c517e3f2a9dcb75649d7af02`.

Comptage des chemins modifiés :
- 94 sous `research/bricks/`, dont 32 reconstitutions ;
- 43 sous `reviews/` ;
- 44 sous `reproducibility/`, dont 17 fichiers CCS ;
- 14 sous `research/programs/` ;
- 5 sous `research/code/` ;
- 11 sous `research/data/` ;
- 5 sous `research/method/`.

La PR contient donc des cartes et reconstitutions, des audits, des scripts, des données et CCS, mais pas de migration complète des travaux Ω-W07/W08/W09. La branche ne doit pas être fusionnée en bloc : les 63 commits de retard et les 264 commits d'avance imposent une revue commit/fichier. L'ancien rapport de PR mentionne également une adresse d'auteur publique non-`noreply`, un workflow C5 dont le run final doit être vérifié, et des scripts historiques d'écriture SQLite à ne pas exécuter sur la base de travail.

## 6. Décisions de conservation

1. Garder `main` comme branche canonique ; ne pas faire de merge global de la branche divergente.
2. Garder les 32 reconstitutions dans leur répertoire dédié ; ne pas les compter comme cartes originales.
3. Garder les 17 correspondances sémantiques confirmées séparées des 26 liens d'évidence SQLite existants ; réparer les liens seulement dans une nouvelle version contrôlée de SQLite.
4. Conserver les dix cartes originales restaurées et leurs hashes/provenances.
5. Garder les 15 briques NS en staging jusqu'à reconstruction exacte des contrats et résolution des identifiants.
6. Conserver W07 comme suspendu, W08 comme empirique non réaudité, W09 comme reproductibilité partielle/NO-GO.
7. Ne pas lancer les scripts historiques de commit sur la base de travail ; les scripts de migration contenant des écritures SQLite doivent être audités et exécutés uniquement sur copie sauvegardée.
8. Ne pas promouvoir les composites CERT-V, les candidats, les redondances ou les résultats indéterminés.

## 7. Limites explicites de cet audit

- Le dépôt privé source `Abrasax63/Omega-` n'a pas été inspecté intégralement par accès direct ; les conclusions historiques reposent sur la Library, les archives consultables et la branche de migration.
- Les sources W07/W08/W09 n'ont pas toutes été retrouvées dans le dépôt public ; leur absence dans la PR est établie par la liste des chemins modifiés, pas par une affirmation d'absence dans tout le dépôt privé.
- Aucun calcul historique RAVI-2/NS/W07/W08/W09 n'a été rejoué par ce rapport.
- Les statuts SQLite sont reproduits tels qu'enregistrés ; ils ne sont pas revalidés.
- Ce rapport est un audit de couverture, de provenance et de migration, non une certification mathématique.

## 8. Sources internes examinées

- `reviews/RECONCILIATION_CARTES_RESULTATS_SQLITE_V33_2026-11-04.md`
- `reviews/RECONCILIATION_DETAIL_42_RESULTATS_SQLITE_V33_2026-11-04.md`
- `reviews/INVENTAIRE_SOURCES_32_CARTES_MANQUANTES_2026-11-04.md`
- `reviews/AUDIT_TRACABILITE_32_RECONSTITUTIONS_2026-11-04.md`
- `reviews/REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md`
- `reviews/AUDIT_RATTRAPAGE_BRIQUES_2026-10-19.md`
- `reviews/AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md`
- `research/bricks/NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md`
- `OMEGA_WORK_INDEX.md`, `OMEGA_W07_HEYTING_COMMUNICATION.md`, `OMEGA_W08_KIBBLE_ZUREK.md`
- `AUDIT_REPORT.md`, `DECISION.json`, `GAP_REGISTER.json`, `SOURCE_PROVENANCE.json`, `VERIFICATION_RECEIPT.json` de Ω-W09/I2
- `LEGACY_INVENTORY.csv` et `OMEGA_W09_ITERATION2_EVIDENCE.sha256`

**Conclusion :** la migration a déjà récupéré une grande partie de l'ossature scientifique, mais il reste 32 cartes originales non retrouvées, 17 liaisons d'évidence SQLite non réparées, 15 briques NS en staging, et trois chantiers Ω à préserver dans leurs statuts réels. La prochaine étape sûre est un audit fichier par fichier des artefacts présents sur la branche avant toute fusion ou promotion.
