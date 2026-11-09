# Réconciliation sémantique des briques — lot 02 (11 fichiers)

Date : 9 novembre 2026  
Branche source en lecture seule : `migration/ravi2-ccs-public-2026-11-04`  
Commit source : `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
Branche de publication : `maintenance/reconciliation-bibliotheque-2026-11-05`

## Portée et méthode

Lecture intégrale de 11 fiches individuelles de `research/bricks/`. Aucun script, checker, calcul ou preuve formelle n'a été exécuté dans cette passe. Les dépendances et contrôles sont rapportés comme déclarations des documents. Aucun fichier source n'a été modifié ; aucune base SQLite n'a été lue ou écrite.

Les statuts ci-dessous sont **les statuts déclarés par les documents sources**, et non des statuts revalidés au 9 novembre. « Non réaudité » signifie que la preuve, les calculs et la bibliographie n'ont pas été repris indépendamment dans ce lot. Les SHA Git sont ceux des blobs du commit source, issus du manifeste exhaustif.

## Fiches lues

### 1. `BR-ACC-01_CLOTURE_ACCESSIBLE.md`
- ID : `BR-ACC-01`.
- Statut déclaré : DÉMONTRÉ, CERT-V dans la source.
- Domaine : système fini déterministe, actions totales, observation fixe et ensemble initial E.
- Énoncé : le langage des facteurs du langage issu de E est égal au langage produit depuis la clôture accessible H ; décomposition disjointe du défaut d'une clôture locale en défaut de recollement et défaut d'accès.
- Contre-exemple déclaré : système à deux états `a→b→b`, montrant un défaut d'accès sans défaut de recollement sur H.
- Provenance : `DELTA_H_ACCES_INTERVENTIONS_V1_1_2026-09-29.md`, section 2.
- Limites : actions totales, déterminisme et observation fixe ; pas d'extension automatique aux politiques à mémoire infinie.
- Contrôle du lot : énoncé lu, preuve et contre-exemple non recalculés ; non réaudité.
- SHA Git source : `006a57586ae1e7f100c48d7bc4f159723c2b3352`.

### 2. `BR-ACC-STATE-COMMUTE-01_BRIQUE.md`
- ID : `BR-ACC-STATE-COMMUTE-01`.
- Statut déclaré : « visé : DÉMONTRÉ interne » ; originalité externe annoncée comme connue/classique.
- Domaine : système fini déterministe total, actions, observation fixe, ensemble initial non vide.
- Énoncé : quotienter par l'équivalence prédictive puis prendre l'accessible commute, dans le cadre décrit, avec prendre l'accessible puis quotienter ; isomorphisme canonique des quotients accessibles.
- Preuve fournie dans la fiche : stabilité de l'équivalence sous actions, commutation de la projection avec les transitions, induction sur les mots et restriction aux états accessibles.
- Dépendances déclarées : `BR-ACC-01`, `BR-STATE-01`.
- Contrôles déclarés : checker rapportant 41 018 cas exhaustifs pour n≤3 et 20 000 cas aléatoires pour n=4…8, zéro violation.
- Limites : déterminisme total et observation fixe ; aucune extension revendiquée aux systèmes partiels, stochastiques, quantiques ou politiques à mémoire infinie.
- Contrôle du lot : preuve et checker non rejoués ; conserver la nuance « statut visé » ; non réaudité.
- SHA Git source : `c4c89930f075983e085da5e38c956f12dc61186e`.

### 3. `BR-AFFINE-GAUGE-GLUE_BRIQUE.md`
- ID : `BR-AFFINE-GAUGE-GLUE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité : application connue, aucune priorité revendiquée.
- Domaine : algèbre affine sur F₂, mêmes espaces de lignes par étiquette, phases relatives linéaires ; corollaire probabiliste sous prior uniforme et canal invariant par translation.
- Énoncé : critère d'existence d'une translation commune par annulation d'une forme sur le noyau R ; obstruction collective décrite par R/R_pair, au-delà des raccordements par paires.
- Contrôles déclarés : reconstruction indépendante et 1 359 configurations de phases relatives vérifiées ; cinq témoins N11 annoncés avec obstruction d'ordre supérieur aux triples.
- Dépendances / interfaces : la fiche décrit une obstruction collective ; pas de graphe formel de dépendances ajouté dans cette passe.
- Limites : mêmes espaces de lignes, phases cohérentes et translations dans les mêmes coordonnées ; le corollaire probabiliste a des hypothèses supplémentaires ; pas d'implication générale « moments égaux ⇒ translation commune ».
- Provenance : `V19_TROISIEME_ORDRE_2026-10-15.md` et archive ZIP indiquée.
- Contrôle du lot : démonstration et 1 359 cas non revérifiés ; la fiche reconnaît l'absence de validation humaine externe et de compilation formelle ; non réaudité.
- SHA Git source : `1520fd18f1f18bb85d9fe76abdff07712e687044`.

### 4. `BR-AFFINE-GROUP-CORE_BRIQUE.md`
- ID : `BR-AFFINE-GROUP-CORE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité classique/application interne, aucune priorité revendiquée.
- Domaine : systèmes finis d'équations affines sur F₂, sans fond immuable non représenté.
- Énoncé : extraction d'un support incompatible d'au plus d+1 lignes/groupes ; réduction par suppressions produisant un noyau minimal par inclusion ; certificat XOR `0=1` et témoins satisfaisants après chaque suppression.
- Contrôles déclarés : audit multiagent ; vérificateur XOR et évaluation sans solveur.
- Dépendances : la fiche n'énonce pas de dépendance formelle ; elle cite le principe classique et Junker (2004).
- Limites : minimalité par inclusion, pas cardinalité optimale ni optimalité temporelle ; provenance des lignes originales requise.
- Provenance : `AFFINE_GROUP_CORE_2026-10-15.md`, archive ZIP ; commit historique nommé dans la fiche.
- Contrôle du lot : aucune exécution du vérificateur ni revue bibliographique ; la source précise l'absence d'audit humain externe et de preuve compilée ; non réaudité.
- SHA Git source : `6838a2e95ab64ae53406e4fc75abc267e4366745`.

### 5. `BR-AFFINE-TREE-CORE_BRIQUE.md`
- ID : `BR-AFFINE-TREE-CORE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité connue/classique et application interne.
- Domaine : relations affines binaires finies sur arbre de portées à intersection courante, variables partagées identifiées littéralement.
- Énoncé : pipeline de décision positif/négatif : filtrage exact de `BR-AFFINE-TREE-GLUE` si le joint est non vide ; sinon extraction par `BR-AFFINE-GROUP-CORE` d'un noyau incompatible minimal par inclusion et certificat XOR.
- Dépendances déclarées : `BR-AFFINE-TREE-GLUE`, `BR-AFFINE-GROUP-CORE`.
- Contrôles déclarés : 15 972 familles, verdicts comparés à l'énumération brute ; 7 470 joints vides et noyaux annoncés vérifiés par suppression et énumération.
- Limites : pas d'extension aux relations non affines, hypergraphes cycliques généraux, minimalité en cardinalité, gain de complexité ou loi universelle de composition.
- Provenance : `AFFINE_TREE_CORE_BRIDGE_2026-10-16.md`, archive ZIP.
- Contrôle du lot : calculs et dépendances non rejoués ; non réaudité.
- SHA Git source : `ff8b35f41aca9de2d362f0bf4852f133527a479d`.

### 6. `BR-AFFINE-TREE-GLUE_BRIQUE.md`
- ID : `BR-AFFINE-TREE-GLUE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité classique/application interne.
- Domaine : relations affines sur F₂, arbre orienté de portées avec propriété d'intersection courante et variables partagées littéralement identifiées.
- Énoncé : conditions d'inclusion/égalité des projections parent-enfant assurant prolongement des solutions ; formules de comptage et de dimension ; filtrage ascendant exact en l'absence des inclusions initiales.
- Dépendances : aucune dépendance nommée comme prérequis dans la fiche ; sert de dépendance à `BR-AFFINE-TREE-CORE`.
- Contrôles déclarés : reconstruction indépendante par énumération sur 15 972 familles d'arbres ; sous-ensembles de cas et contrôles additionnels décrits dans le texte.
- Limites : hypothèses affines et structure arborescente ; égalité des images plus forte qu'une simple compatibilité existentielle ; pas de transfert aux relations non affines ni de revendication de nouveauté.
- Provenance : `COMPOSITION_AFFINE_2026-10-15.md`, archive ZIP.
- Contrôle du lot : aucune reproduction ; la fiche indique absence d'assistant de preuve et de validation humaine externe ; non réaudité.
- SHA Git source : `e4145722b06102e104ddf6ff8faa027d3663d0e6`.

### 7. `BR-DESC-01_SUFFISANCE_VS_AUTONOMIE.md`
- ID : `BR-DESC-01`.
- Statut déclaré : DÉMONTRÉ sur le modèle de référence ; principe général connu.
- Domaine : modèle de cycle de longueur première p, sortie binaire non constante.
- Énoncé : suffisance prédictive pour une sortie et fermeture sous mise à jour sont deux exigences distinctes ; dans le modèle spécifié, deux catégories peuvent suffire à une prédiction ponctuelle, tandis qu'une mise à jour déterministe exacte exige p catégories.
- Dépendance / relation : `BR-STATE-01` fournit un cadre conceptuel ; la fiche précise que la relation n'est pas causale et que la preuve quantitative est autonome.
- Provenance : audit descriptions du 14 octobre et audit propre à la brique.
- Limites : résultat quantitatif propre au modèle de cycle ; aucune conclusion physique ou quantique.
- Contrôle du lot : modèle et preuve non recalculés ; non réaudité.
- SHA Git source : `fb584f81bdd285da480df1eafacea75d0ab77c19`.

### 8. `BR-DESC-02_MARGINALE_VS_ORDRE_TEMPOREL.md`
- ID : `BR-DESC-02`.
- Statut déclaré : CALCUL EXACT pour l'identité de covariance ; garantie exacte de fausse alerte pour la machine rationnelle ; puissance et délais évalués par simulation.
- Domaine : modèle à cinq phases et machine rationnelle de détection spécifiée dans la source.
- Énoncé : même marginale `P(Y_t=1)=21/50` pour les noyaux considérés, mais covariance au retard 2 dépendant de λ ; un détecteur fondé seulement sur la marginale peut manquer un changement temporel.
- Garantie déclarée : probabilité sous le modèle nul d'au moins une fausse alerte à un instant quelconque ≤1 % pour la construction indiquée.
- Provenance : `detection_correlations_2026-10-14.md` et audit de la brique.
- Limites : formules propres au modèle ; garantie de fausse alerte conditionnée au nul déclaré et à l'arithmétique de la construction ; puissance et délais simulés, sans garantie générale.
- Relation : illustre conceptuellement `BR-DESC-01`, sans dépendance logique revendiquée.
- Contrôle du lot : identité, supermartingale et simulations non vérifiées/rejouées ; non réaudité.
- SHA Git source : `81a0d346c2299850c1ffd2e26783a9b983a38933`.

### 9. `BR-OBS-01_ADAPTATIF_VS_PREDEFINI.md`
- ID : `BR-OBS-01`.
- Statut déclaré : DÉMONTRÉ pour les témoins ; minimalité binaire appuyée par calcul exhaustif exact ; nouveauté bibliographique des témoins INDÉTERMINÉE.
- Domaine : machines de Mealy déterministes complètes.
- Énoncé : témoins avec mémoire locale finie, expérience adaptative finie, mais aucune expérience prédéfinie ; un témoin binaire à cinq états réalise `(r_IO,L_A,L_P)=(2,3,∞)`.
- Minimalité déclarée : aucune machine binaire complète à quatre états dans l'énumération ; minimum lexicographique annoncé à cinq états dans l'univers binaire.
- Méthode réutilisable : graphe de couples stricts de croyances ; cycle accessible vers un interdit minimal pour diagnostiquer `r_IO=∞`, sinon plus long chemin.
- Limites : minimalité globale avec alphabets non binaires à quatre états indéterminée.
- Provenance : rapport observabilité active du 26 septembre, sections 2–5.
- Contrôle du lot : témoins et énumération non reconstruits ; non réaudité.
- SHA Git source : `aa8425b35c8d9ad2175b9f05d42d4b624f51e75d`.

### 10. `BR-OBS-BAD-01_AFFINE_SIGNATURE.md`
- ID : `BR-OBS-BAD-01`.
- Statut déclaré : DÉMONTRÉ, interne RAVI-2 ; originalité : principe général connu / reformulation spécialisée.
- Domaine : espace affine cohérent de configurations sur F₂ et contraintes supplémentaires homogènes attachées à chaque témoin.
- Énoncé : pour mauvais objets non vides, égalité des ensembles de solutions équivaut à égalité des formes échelonnées réduites canoniques des systèmes augmentés.
- Mécanisme : signature RREF sur F₂ des lignes augmentées `(forme,rhs)`.
- Limites : ne borne pas la taille d'une fibre ; deux témoins distincts peuvent partager un mauvais objet ; cas vide à traiter séparément.
- Application déclarée : `OBS-V19-N11-BADOBJECT`, cinq premières ruptures d'intégralité à N=11.
- Contrôle du lot : preuve et application non recalculées ; non réaudité.
- SHA Git source : `d7c22d06255ed39b5e69ecfc4e6a74447df1c81f`.

### 11. `BR-OBS-CAP-01_DYNAMIC_CAPACITY.md`
- ID : `BR-OBS-CAP-01`.
- Statut déclaré : DÉMONTRÉ, interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : classe admissible de systèmes finis déterministes, frontière distinguée et application témoin→motif local.
- Définition : capacité dynamique comme supremum, sur les systèmes admissibles, du nombre de témoins distincts produisant un motif donné.
- Résultats : invariance sous symétrie admissible ; bornes par ressources selon les gabarits ; capacité infinie via réplication d'un gadget sans interaction forcée.
- Dépendances / applications : appliquée par `OBS-V19-C5-CAPACITY v2` ; la fiche ne donne pas de dépendance formelle amont.
- Limites : capacité relative à la classe et à la notion de témoin ; capacités individuelles ne décrivent pas les ressources partagées ; occurrences distinctes à ne pas confondre avec coefficients algébriques.
- Contrôle du lot : lemmes et application non vérifiés indépendamment ; non réaudité.
- SHA Git source : `5cb676c73d385b557aa5282e9514848383c196bc`.

## Constats transversaux et points de vigilance

1. **Deux statuts de force différente dans le vocabulaire source.** `BR-ACC-STATE-COMMUTE-01` porte « statut visé : DÉMONTRÉ », alors que plusieurs fiches portent directement « DÉMONTRÉ interne ». Il faut préserver cette nuance, sans uniformiser les libellés.
2. **Famille affine : dépendances explicites.** Les fiches TREE-CORE et TREE-GLUE forment un pipeline déclaré avec AFFINE-GROUP-CORE. GAUGE-GLUE et GAUGE-CORE constituent un autre ensemble ; les noms proches ne prouvent pas l'identité des contrats.
3. **Validations numériques historiques.** Les volumes de cas (41 018, 20 000, 15 972, etc.) sont rapportés par les fiches. Aucun n'a été rejoué dans ce lot.
4. **Exact, simulé et théorisé restent séparés.** BR-DESC-02 distingue une identité exacte, une garantie de fausse alerte conditionnelle et des performances simulées. Ne pas résumer tout le détecteur par « démontré ».
5. **Signature affine : domaine non vide.** Le critère de collision est énoncé pour les mauvais objets non vides ; le cas vide exige une convention distincte.
6. **Pas de promotion automatique.** Ces fiches n'ont pas été reliées à un moteur agentique et les preuves n'ont pas été revalidées.

## Verdict du lot

- 11/11 fichiers individuels lus intégralement.
- Classification documentaire réalisée : ID, statut déclaré, domaine, énoncé, provenance, dépendances, contrôles déclarés et limites.
- 0 script/checker relancé ; 0 preuve formellement vérifiée ; 0 statut scientifique revalidé ; 0 certificat renouvelé.
- 0 fichier source historique modifié ; 0 écriture SQLite.
- Les briques restantes, les 47 revues et les 44 artefacts de reproductibilité restent à classifier sémantiquement.

Ce lot est un registre de traçabilité documentaire, pas une certification scientifique nouvelle ni une intégration au moteur agentique.
