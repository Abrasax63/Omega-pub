# Omega LAB23 — protocole préenregistré du « pas de côté » représentationnel

Établi le 19 novembre 2026 **avant l'implémentation et avant l'exécution des cas**. Pilote sur branche expérimentale empilée sur Reader20 (#189), sans modifier `main`, sans API payante ni fusion.

## Question réfutable
Une exploration automatique de **représentations mathématiques alternatives** permet-elle de trouver des équivalences correctes, des transformations incorrectes accompagnées de contre-exemples minimaux, et des propriétés structurelles utiles de l'observabilité finie ? On veut une capacité de *production de candidats*, pas uniquement un calcul d'un énoncé reçu. **Aucune nouveauté mathématique revendiquée** : le raffinement de partitions des automates est classique (algorithme de Moore). La génération reste un programme à grammaire limitée ; pas une preuve de créativité autonome ouverte.

## Domaine, sens de « même problème »
Système fini déterministe `T:{0,...,n-1}->{0,...,n-1}`, observation binaire `pi:X->{0,1}`, horizon `h`. Relation de référence `E_h(x,y)` : mêmes observations `pi(T^k x)=pi(T^k y)` pour tout `0<=k<h`. On compare les relations sur toutes les paires d'états non ordonnées, sans confondre l'observabilité générale et les propriétés d'une seule coloration.

Provenance interne déjà publiée : `02_MATHEMATIQUES/observabilite_temporelle/OBS-V8-FACT-INF.md`, blob `6d7f6b44c683852871b08a37f814bae5381de11f`. La formule à horizon infini du document n'est PAS celle testée ici. Littérature classique de minimisation d'automates et équivalence observationnelle : Moore / raffinement ; [MFCS 2019](https://drops.dagstuhl.de/storage/00lipics/lipics-vol138-mfcs2019/LIPIcs.MFCS.2019.77/LIPIcs.MFCS.2019.77.pdf). La méthode multi-solutions s'inspire de Quality-Diversity mais **n'implémente pas MAP-Elites**.

## Grammaire finie de transformations proposée automatiquement
Générer à partir du problème initial le registre de six candidats, sans lire les réponses de l'oracle :
1. `trace` — représentation initiale, suite de longueur `h`, **référence** (calcul séparé).
2. `pair_pullback` — relation récurrente `R_0=X²`, `R_{h+1}(x,y)=[pi(x)=pi(y)] and R_h(Tx,Ty)`.
3. `partition_refinement` — codes de blocs `P_0(x)=0`, `P_{h+1}(x)=code(pi(x),P_h(Tx))`; tester leur égalité.
4. `unordered_histogram` — histogramme des observations de longueur `h` sans l'ordre.
5. `current_only` — ne garder que `pi(x)`, ignorer les observations futures.
6. `future_only` — ignorer `pi(x)`, garder `pi(Tx),...,pi(T^h x)` : même longueur, mais décalée.

Les transformations 2/3 sont *anticipées exactes* par la récurrence ; 4/5/6 sont des contre-modèles adversariaux à falsifier si possible. L'étape « créative » est la génération et la variation de représentations depuis une grammaire explicitement préprogrammée : elle ne prouve PAS la capacité d'inventer une nouvelle grammaire.

## Exécution figée (aucune sélection post hoc)
- **Calibration exhaustive** : toutes les applications `T` et observations `pi` à 2, 3 et 4 états, soit `4*4 + 27*8 + 256*16 = 4 328` systèmes/colorations ; pour chacun horizons `1..n+1`. Le cas `n=1` est omis car sans paire distincte.
- **Validation hors calibration** : 128 cas générés avec `random.Random(20261119)` : 64 à 5 états et 64 à 6 états ; toutes les observations et transitions générées indépendamment via PRNG; horizon `1..n+1`. Pas d'entraînement, ni de retouche après résultat. Ces cas restent synthétiques : pas un benchmark externe.
- **Oracle** : comparaison directe de deux mots de sortie, *n'utilisant ni partitions ni récurrence relationnelle*. Chaque transformation calcule indépendamment son résultat ; tous les algorithmes doivent recevoir `(T,pi,h)` identiques.
- **Critère de validation** : 0 divergence en calibration ET validation, et preuve par induction séparément documentée, pour qualifier 2/3 d'`EXACT_FOR_THIS_FINITE_FORMALISM`. Une absence d'erreur empirique **seule** est un certificat expérimental, pas un théorème général.
- **Falsification** : pour 4/5/6, extraire le premier témoin dans l'ordre `n,T,pi,h,(x,y)` de divergence; enregistrer les deux signatures et les résultats. Aucun témoin inventé.
- **Invariants dérivés** : (i) `E_{h+1} subset E_h` ; (ii) si `E_{h+1}=E_h`, la suite est stable ; (iii) `E_n=E_{n+1}` pour `n` états ; (iv) existence d'exemple atteignant pour `n=4` le temps de stabilisation `n` (la distinction du point le plus éloigné exige un horizon n). Déterminer les contre-exemples si les affirmations n'ont pas de preuve.
- Dépenses mesurées : nombre d'instances, horizons et évaluations; temps Python non contrôlé seulement descriptif. Ne pas inventer une supériorité en coût/qualité par rapport à un solveur optimisé.

## Séparation des rôles et tests de non-régression
- **A** : oracle direct (référence exacte d'un cas, aucune proposition créative).
- **B** : diversification brute (trois candidats qui effacent des informations, sans test de fidélité).
- **C** : changement de représentation préprogrammé puis **filtre de fidélité**, qui conserve des approches correctes et exhibe des contre-exemples des fausses.
- A/B/C **ne sont pas trois LLM ni un test aveugle à budget token égal**. Ce test mesure la valeur d'une structure de génération + réfutation à budget de candidats explicite (3 sous B et 2 exactes sous C) ; ne pas publier un pourcentage trompeur « créativité meilleure ».
- Archive Python + JSON (candidats, preuves attendues, divergences, exemples, hash des sources, statut, limites). Aucun apprentissage de poids, aucune écriture vers la bibliothèque certifiée, aucun auto-déploiement. Les faux candidats demeurent visibles et rejetés.

## Portée / condition d'arrêt
Démonstration recevable seulement si CI montre les comptes exacts, les signatures, les deux algorithmes alternatifs fidèles au direct, les trois contre-exemples réels et les invariants testés. Si une hypothèse « connue » échoue, **statut réfuté** et correction mathématique avant toute autre action. Une PR qui se contente d'ajouter des noms de rôles « créatifs » est un échec.

Prochaine étape après ce pilote : donner à un générateur plus ouvert (modèle local sans coût) la capacité de proposer **des transformations inédites** selon une grammaire distincte gelée, en laissant les mêmes oracles décider de leur fidélité et en mesurant une valeur *hors cas utilisés pour concevoir le générateur*.
