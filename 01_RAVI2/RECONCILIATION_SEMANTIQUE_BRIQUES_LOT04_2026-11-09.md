# Réconciliation sémantique des briques — lot 04 : capacités, quotient forcé et reconstitutions V19

Date : 9 novembre 2026  
Branche source en lecture seule : `migration/ravi2-ccs-public-2026-11-04`  
Commit source : `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
Branche de publication : `maintenance/reconciliation-bibliotheque-2026-11-05`

## Portée et méthode

Onze fichiers ont été lus intégralement : cinq briques originales et six reconstitutions documentaires. Le lot poursuit la vérification des interfaces V19 : capacités, classification orientée, petit modèle, contraintes forcées et moments affines.

Aucun script, checker, notebook, calcul exact ou preuve formelle n'a été exécuté. Les résultats numériques et statuts ci-dessous sont rapportés par les documents historiques, sans revalidation. Les six fichiers sous `reconstructed/` restent explicitement des reconstitutions non originales.

## A. Cinq briques originales

### 1. `OBS-V19-C5-CAPACITY_BRIQUE.md`
- ID : `OBS-V19-C5-CAPACITY` v2 ; statut déclaré DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : C5 orienté, observation binaire, L=3, contraintes forcées cohérentes ; occurrences = paires non ordonnées distinctes.
- Énoncé : 70 ombres géométriques exactes orientées sont produites par les 3 341 diagrammes locaux ; 50 ont capacité finie, 20 capacité infinie. Spectre fini annoncé : 2, 4, 8, 12, 16, 32.
- Capacités de classes : C5O-00..03 = 2 chacune ; C5O-04=8 ; 05=4 ; 06=∞ ; 07=8 ; 08=∞ ; 09=12 ; 10=∞ ; 11=16 ; 12=∞ ; 13=32.
- Dépendances déclarées : `BR-OBS-CAP-01`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`.
- Mécanisme annoncé : bornes de profondeur/phase, contrôle de fibres et construction atteignant simultanément toutes les capacités finies ; gadgets extérieurs à période 2 pour les classes infinies.
- Limites : C5/binaire/L=3 ; aucune contrainte partagée entre ombres différentes ; les capacités ne bornent pas les coefficients de circuits.
- Provenance : rapport de théorie des capacités, code Python et catalogue CSV identifiés.
- Contrôle du lot : aucun de ces artefacts n'a été ouvert ou exécuté ici ; non réaudité.
- SHA Git source : `bc4b3eea112aeae4d7dcaac7bb79b52f0452d7d6`.

### 2. `OBS-V19-COEX-SMALLMODEL_BRIQUE.md`
- ID : `OBS-V19-COEX-SMALLMODEL` v2 ; statut déclaré DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : endofonction finie, observation binaire, cycle distingué C_q, q≥3, horizon L≥2, contraintes forcées cohérentes ; k paires distinctes.
- Énoncé : si k ombres coexistent dans un système fini, elles coexistent avec les mêmes paires distinctes dans un système de taille au plus `q + 2k(L+3) + max(3,2k)`.
- Dépendances déclarées : `OBS-V19-LOCAL-L2`, lui-même dépendant de `OBS-V19-FORCED-P4`.
- Preuve annoncée : conserver les préfixes jusqu'à L+2, ajouter un cycle externe et envoyer injectivement les terminaux ; les paires ne sont ni identifiées ni fusionnées.
- Contrôle annoncé : 1 347 familles de 2 ou 3 paires, sans divergence.
- Limites : borne de témoin, pas caractérisation des familles qui coexistent ; ne généralise pas automatiquement hors observation binaire ou cohérence forcée.
- Provenance : rapport d'assemblage orienté, rapport de multiplicité et code identifiés.
- Contrôle du lot : preuve et tests non rejoués ; non réaudité.
- SHA Git source : `022d58fd7ca0c0fe77e83335ffb8940c632a6db2`.

### 3. `OBS-AFFINE-GROUP-CORE-VALIDATION_BRIQUE.md`
- ID : `OBS-AFFINE-GROUP-CORE-VALIDATION` v1 ; statut déclaré CALCUL EXACT interne ; aucune priorité revendiquée.
- Domaine : validation d'un détecteur de noyau et de blocages collectifs ; fixtures et populations finies définies dans le rapport source.
- Résultats annoncés : 50 653 familles ordonnées de trois groupes en dimension 2 (101 306 exécutions), huit cas limites, 2 000 exécutions supplémentaires sur 1 000 familles de dimension ≤6 ; 172 sorties vérifiées sur 86 entrées de benchmark.
- Portée : vérification sur populations finies et fixtures ; les chronométrages sont exclus du statut exact et ne démontrent aucun avantage général.
- Dépendances : la fiche renvoie au rapport `AFFINE_GROUP_CORE_2026-10-15.md` et à son archive de preuves ; le contrat mathématique complet du détecteur doit être rapproché de la brique `BR-AFFINE-GROUP-CORE`.
- Limites : ne certifie ni performance générale ni minimalité universelle des noyaux ; pas de validation humaine externe ni compilation formelle.
- Contrôle du lot : données et méthodes non rejouées ; non réaudité.
- SHA Git source : `f5f96d26fbce5e6fb5f8b45aa9d361a96d648d07`.

### 4. `OBS-RESTRICT-FORCED-QUOTIENT_BRIQUE.md`
- ID : `OBS-RESTRICT-FORCED-QUOTIENT` v1 ; statut déclaré DÉMONTRÉ interne ; originalité application connue.
- Domaine : graphe cohérent de contraintes binaires signées, prior uniforme admissible, masquage indépendant des sommets originaux ; corollaire V19 sous contrat P4.
- Énoncé : le quotient par composantes forcées transforme les variables originales en variables de composantes ; les probabilités de non-révélation deviennent p^(m_j). Le moment conjoint de deux postérieurs est exprimé par une somme sur l'intersection des espaces de lignes, pondérée par les supports.
- Distinction importante : le protocole de révélation iid original et le rejet global de restrictions iid sont deux lois différentes ; la fiche donne un taux libre différent pour le second protocole.
- Dépendance déclarée : `OBS-V19-FORCED-P4` uniquement pour la borne m_j∈{1,2,3,4}; la réduction générale est annoncée sans cette borne.
- Contrôles annoncés : reconstruction indépendante et 57 362 comparaisons exactes sur endofonctions n≤4 et deux C5 ; exemple C5,L=3 où le moment vaut 1/128 contre 3/256 pour le quotient naïf.
- Limites : ne certifie ni capacité, ni coexistence, ni nouvelle propriété d'attracteur ; hypothèses de prior et d'indépendance essentielles.
- Provenance : rapport transfert affine V19, scripts et audits.
- Contrôle du lot : preuve, comparaisons et cas témoin non rejoués ; non réaudité.
- SHA Git source : `6306c81ae37038d4748d4e4f0f4eba3ea03180870`.

### 5. `OBS-RESTRICT-MULTIMOMENT_BRIQUE.md`
- ID : `OBS-RESTRICT-MULTIMOMENT` v1 ; statut déclaré DÉMONTRÉ interne ; originalité application connue.
- Domaine : q événements affines cohérents sur F₂^d, prior uniforme, même observation par révélation indépendante.
- Énoncé : formule générale du moment conjoint de q postérieurs, sommant les q vecteurs des espaces de lignes dont la somme est nulle ; le poids dépend de l'union des supports. Pour q=3, le troisième moment centré ne garde que les trois vecteurs non nuls.
- Contrôle annoncé : deux dérivations indépendantes ; 11 792 tests exacts d'ordre 3 et 42 016 d'ordre 4 sur petites instances ; cas forcé à six bits donnant 85/512.
- Dépendances / interface : rapport V19 troisième ordre ; prolonge les calculs à deux événements et ne doit pas être confondu avec les seules covariances.
- Limites : ne signifie pas indépendance vis-à-vis du modèle complet ni clôture universelle à l'ordre trois ; hypothèses de prior, de canal et de complétions conditionnelles explicites.
- Provenance : rapport troisième ordre et archive de preuves.
- Contrôle du lot : preuve et campagnes de tests non reproduites ; non réaudité.
- SHA Git source : `055fd39b7def5f49ebf656c93e50ed8ee047f24d`.

## B. Six reconstitutions V19 — conservées comme non originales

### 6. `reconstructed/OBS-V19-C5-13_RECONSTITUTION.md`
- ID : `OBS-V19-C5-13` v3 ; statut SQLite recopié : CALCUL EXACT ; originalité INDÉTERMINÉE.
- Énoncé enregistré : 3 341 diagrammes locaux et 13 classes D5 d'ombres propres, répartition codimension 1/2/3 = 4/5/4 ; dépendance de complétude par localité L+2.
- Provenance enregistrée : note de grammaire orbitale, audits, code indépendant et sorties ; tests historiques marqués PASS.
- Relations : remplace l'hypothèse de matching global ; étend le scope du résultat Γ connecté ; dépend de LOCAL-L2 ; sert d'index à TRIPLE-COMPLETE13.
- Point de vigilance : la fiche distingue 13 classes D5 des 10 observées dans les gaps N≤12. Une note antérieure à 12 types ne doit pas être fusionnée sans versionnement.
- Contrôle : reconstitution SQLite v33 ; sources citées mais non relues dans ce lot ; statut non promu.
- SHA Git source : `ebb0ca081d71f79ac30854bb79301a762fc8f3df`.

### 7. `reconstructed/OBS-V19-C5-ORIENTED14_RECONSTITUTION.md`
- ID : `OBS-V19-C5-ORIENTED14` v1 ; statut SQLite recopié : CALCUL EXACT ; originalité INDÉTERMINÉE.
- Énoncé enregistré : 3 341 diagrammes non diagonaux donnent 14 classes propres modulo rotations C5, codimensions 1/2/3 = 4/6/4 ; le quotient par réflexion fusionne une paire chirale et redonne 13 classes D5.
- Dépendance : LOCAL-L2 ; indexe les 105 paires de classes, C5-CAPACITY et UNIVERSAL10.
- Point de vigilance : conserver l'orientation commune lors de coexistence ; le quotient par réflexion peut perdre une information.
- Contrôle : reconstitution non originale ; code, données et audit mentionnés dans SQLite, non réexécutés.
- SHA Git source : `ed1b7fa3d310252eeda690177fba4a9607cc3551`.

### 8. `reconstructed/OBS-V19-FORCED-P4_RECONSTITUTION.md`
- ID : `OBS-V19-FORCED-P4` v1 ; statut SQLite recopié : DÉMONTRÉ ; originalité INDÉTERMINÉE.
- Énoncé enregistré : sous cohérence des contraintes singleton d'une endofonction binaire à L≥2, les composantes du graphe forcé sont des chemins de taille au plus quatre (P1 à P4).
- Dépendances enregistrées : LOCAL-L2, C5-CAPACITY, RESTRICT-FORCED-QUOTIENT, BAD-FIBER2.
- Contre-exemple conservé : le graphe des contraintes peut avoir degré 3 ; le fait que fusion et invariance soient chacune des matchings n'implique pas que leur union soit un matching. La structure P1–P4 est la conclusion enregistrée.
- Contrôles historiques : 50 069 endofonctions n≤6, dont 29 742 cohérentes, sans composante hors P1–P4 ; non rejoués.
- Point de vigilance : dépendance structurelle centrale pour les capacités et la borne fibre≤2 ; la reconstitution ne remplace pas la preuve source.
- SHA Git source : `0a70b998ee83dfec2d7b3cae3bb54e0e67204759`.

### 9. `reconstructed/OBS-V19-GAMMA-CONNECTED_RECONSTITUTION.md`
- ID : `OBS-V19-GAMMA-CONNECTED` v1 ; statut SQLite recopié : DÉMONTRÉ ; originalité INDÉTERMINÉE.
- Domaine : composante fonctionnelle connectée vers C_q, q≥5, binaire, L=3, contraintes forcées cohérentes.
- Énoncé enregistré : grammaire Γ(r,d,σ), 6⌊q/2⌋ types ; pour C5, 12 types.
- Relation de portée : résultat connecté restreint, étendu ensuite par C5-13 pour les paires pouvant vivre dans d'autres composantes.
- Point de vigilance : la note du 24 septembre à 12 types et la classification ultérieure à 13 D5 types ont des contrats différents ; ne pas les amalgamer.
- Audit/test lié : aucun enregistré dans la fiche.
- Contrôle : reconstitution non originale ; statut non promu.
- SHA Git source : `fd031552de1a6dd6eaca0b31e0dbfecf87678dc1`.

### 10. `reconstructed/OBS-V19-UNIVERSAL10_RECONSTITUTION.md`
- ID : `OBS-V19-UNIVERSAL10` v1 ; statut SQLite recopié : CALCUL EXACT ; originalité INDÉTERMINÉE.
- Énoncé enregistré : témoin U42 à 42 états avec au moins 10 paires distinctes de chacune des 14 classes orientées ; vecteur de multiplicités explicitement enregistré.
- Dépendances : C5-ORIENTED14 ; illustre PAIR-COMPLETE14 et FIRST-OBSTRUCTION11, mais la v2 de FIRST-OBSTRUCTION11 dépend désormais causalement de COEX-REGION.
- Limite : témoin constructif et calcul exact rapporté, pas preuve d'une capacité maximale générale.
- Contrôle : reconstitution non originale ; rapport, code et JSON mentionnés, non réexécutés.
- SHA Git source : `934ab7348691af75433dfdfe4b7a411d67920182`.

### 11. `reconstructed/OBS-V19-PAIR-COMPLETE14_RECONSTITUTION.md`
- ID : `OBS-V19-PAIR-COMPLETE14` v2 ; statut SQLite recopié : CALCUL EXACT ; originalité INDÉTERMINÉE.
- Énoncé enregistré : chacune des 105 paires non ordonnées avec répétition des 14 classes orientées possède un témoin dans un système fini avec deux paires d'états distinctes.
- Correction historique : v2 impose deux paires distinctes comme objets combinatoires ; elles peuvent partager un état mais ne sont pas la même paire.
- Dépendance : C5-ORIENTED14 ; illustre UNIVERSAL10.
- Limite : compatibilité par paires de labels, pas loi générale de coexistence pour les copies géométriques exactes.
- Contrôles historiques : audits et test d'énumération marqués PASS ; non rejoués.
- SHA Git source : `039b3c00b24a48e2bb51d9e72421a3a0f0651fdc`.

## C. Graphe de dépendances et points de vigilance

1. **Chaîne structurelle :** FORCED-P4 → LOCAL-L2 → COEX-SMALLMODEL ; FORCED-P4 intervient également dans C5-CAPACITY, RESTRICT-FORCED-QUOTIENT et BAD-FIBER2. P4 est donc un verrou amont à auditer à partir de sa source primaire, pas seulement de sa reconstitution.
2. **Chaîne de classification :** C5-ORIENTED14 → C5-CAPACITY et PAIR-COMPLETE14 ; C5-13 fournit le quotient D5 pour une ombre isolée, tandis que C5-ORIENTED14 conserve la chiralité nécessaire à la coexistence.
3. **Petit modèle :** COEX-SMALLMODEL borne la taille des témoins pour un nombre fixé de paires ; il ne fournit pas à lui seul la caractérisation des coexistences.
4. **Capacité vs coefficients :** la capacité compte des paires distinctes. Elle ne borne ni les poids des circuits ni les coefficients primitifs sans hypothèse supplémentaire.
5. **Moments :** RESTRICT-FORCED-QUOTIENT concerne le passage au quotient forcé ; RESTRICT-MULTIMOMENT traite les moments conjoints d'ordre quelconque. Ne pas réduire l'information d'ordre 3 aux seules covariances.
6. **Versions à conserver :** Γ connecté à 12 types, classification D5 à 13 types et classification C5 orientée à 14 classes sont des objets distincts par domaine et quotient de symétrie.

## Verdict du lot

- 11/11 fichiers lus intégralement : 5 briques originales + 6 reconstitutions.
- Parmi les reconstitutions, 6/32 sont désormais classifiées dans les lots précédents et celui-ci ; elles restent séparées des originaux.
- 0 script/checker exécuté ; 0 preuve vérifiée indépendamment ; 0 statut scientifique revalidé ; 0 certificat renouvelé.
- 0 fichier de la branche source modifié ; 0 écriture SQLite.
- La chaîne P4 → localité → petit modèle/capacités est maintenant cartographiée documentairement, mais la preuve source P4 reste à auditer.
- Ce rapport ne constitue ni une intégration du corpus dans l'architecture agentique, ni une certification mathématique nouvelle.
