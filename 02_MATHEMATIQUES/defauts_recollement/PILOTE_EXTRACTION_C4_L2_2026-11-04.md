# PILOTE-EXT-C4-L2 — Extraction d'instruments et audit reproductible

- **Identifiant :** PILOTE-EXT-C4-L2-2026-11-04
- **Version :** 0.1
- **Domaine :** systèmes dynamiques finis / observation binaire / V19
- **Statut scientifique :** CALCUL EXACT sous spécification opérationnelle ; équivalence à la définition primaire V19 : À RÉEXAMINER
- **Statut de publication :** EXPÉRIMENTAL — branche pilote, non fusionnée
- **Date :** 2026-11-04

## 1. Question testée

Peut-on extraire d'un dossier de recherche antérieur une méthode reproductible, l'isoler comme instrument, la vérifier par une seconde implémentation et conserver clairement les limites de portée ?

Le cas choisi est le dossier C4, L=2 : réalisation des huit classes d'ombres C4O-00 à C4O-07 dans une même dynamique finie, puis vérification de la borne inférieure de taille sous la spécification opérationnelle documentée.

## 2. Sources historiques récupérées

- RESULTATS_C4_L2_CLASSES_2026-10-27.md : catalogue local de huit classes.
- AUDIT_V19_C4_L2_REPRISE_2026-10-28.md : témoin à neuf états et énumération exhaustive jusqu'à huit états.
- CERTIFICAT_CONDITIONNEL_V19_C4_L2_2026-10-28.md : spécification opérationnelle et portée conditionnelle.
- audit_v19_c4_l2_equalites.py : vérificateur global principal.
- certificat_v19_c4_l2_global.py : seconde implémentation globale.

Le dossier historique distingue explicitement le résultat opérationnel de l'équivalence avec la définition primaire V19. Cette distinction est conservée.

## 3. Instrument extrait

### EXT-FINITE-PROJECTION-COLORING v0.1

**Principe :** pour une endofonction totale finie T et un ensemble de contraintes binaires forcées, calculer exactement l'ensemble des colorations projetées sur un cycle distingué en énumérant les colorations globales admissibles.

**Entrées :**
- une fonction totale T sur un ensemble fini X ;
- un cycle distingué C4 ;
- les paires d'états soumises à une inégalité forcée ;
- les paires de trajectoires soumises à une égalité de couleur aux temps t=0,1.

**Sortie :** l'ensemble exact des masques binaires projetés sur les quatre états du cycle.

**Préconditions du pilote :**
- observation binaire ;
- totalité de T ;
- taille maximale des fibres égale à 2 ;
- graphe des inégalités forcées biparti ;
- égalités de trajectoire appliquées seulement lorsque les états comparés sont distincts.

**Limite :** l'instrument vérifie la spécification opérationnelle écrite ci-dessus. Il ne démontre pas que celle-ci est identique à toute formulation primaire antérieure de V19.

## 4. Témoin global

La dynamique testée est :

T = (1,2,3,0,8,7,6,2,0)

Le cycle distingué est 0 → 1 → 2 → 3 → 0.

Les huit paires historiques sont :
- C4O-00 : (0,1)
- C4O-01 : (0,2)
- C4O-02 : (1,8)
- C4O-03 : (0,7)
- C4O-04 : (0,6)
- C4O-05 : (4,5)
- C4O-06 : (1,4)
- C4O-07 : (0,4)

Les deux vérificateurs recalculent les ombres brutes sur les colorations globales des neuf états. Les huit ensembles correspondent exactement aux masques cibles archivés.

## 5. Résultats des exécutions du 2026-11-04

### Vérificateur A — [audit_v19_c4_l2_equalites.py](code/audit_v19_c4_l2_equalites.py)

Commande exécutée : python audit_v19_c4_l2_equalites.py

SHA-256 :
94998806131e05c74946f14ea3b4ee5a8e8bc83e0e65bed1a67d2139667ab027

Sorties observées :
- témoin : PASS, 8/8 ombres brutes ;
- variante avec inégalités de trajectoire : 1/8 ombre brute identique ;
- N=4 : 1 fonction examinée, 1 cohérente, aucun témoin ;
- N=5 : 5 fonctions examinées, 5 cohérentes, aucun témoin ;
- N=6 : 36 fonctions examinées, 32 cohérentes, aucun témoin ;
- N=7 : 343 fonctions examinées, 263 cohérentes, aucun témoin ;
- N=8 : 4096 fonctions examinées, 2695 cohérentes, aucun témoin.

### Vérificateur B — [certificat_v19_c4_l2_global.py](code/certificat_v19_c4_l2_global.py)

Commande exécutée : python certificat_v19_c4_l2_global.py

SHA-256 :
72b3f1aa6882af44ea4a8d4cb537a85269a668eaef3c80cf0d86f20b2e207529

Les empreintes SHA-256 ci-dessus portent sur les fichiers locaux matérialisés et exécutés. Le dépôt Git normalise les fins de ligne ; l'empreinte du blob Git peut donc différer sans modification du contenu Python.

Sorties observées :
- témoin global : PASS, les huit masques bruts correspondent ;
- énumération N=4 à N=8 : mêmes totaux, mêmes nombres de fonctions cohérentes, aucun témoin.

### Concordance

Les deux implémentations donnent les mêmes résultats pour le témoin à neuf états et pour les tailles N=4,…,8. Elles constituent deux implémentations distinctes du même contrat opérationnel ; elles ne sont pas deux définitions mathématiques indépendantes.

## 6. Contre-test décisif

La variante où les trajectoires imposent des inégalités de couleur au lieu des égalités ne reproduit qu'une seule des huit ombres brutes. Cette variante est donc réfutée comme interprétation du certificat opérationnel sous les autres hypothèses conservées.

Attention : ce contre-test ne prouve pas que toutes les formulations alternatives de V19 sont fausses ; il ne vise que cette substitution précise.

## 7. Résultat et portée

- **DÉMONTRÉ par vérification finie du témoin :** le T fourni réalise les huit ensembles de masques sous le contrat opérationnel encodé.
- **CALCUL EXACT :** absence de témoin pour N=4,…,8 dans l'espace exhaustivement énuméré sous ce même contrat.
- **INDÉTERMINÉ / À RÉEXAMINER :** équivalence complète entre ce contrat et la définition primaire V19.
- **Non établi :** minimalité inconditionnelle V19, originalité bibliographique, généralisation à d'autres cycles ou horizons.

Aucune promotion en résultat certifié inconditionnel n'est autorisée par ce pilote.

## 8. Dépendances et provenance

Dépendances :
- catalogue C4 L=2 du 2026-10-27 ;
- spécification opérationnelle du certificat conditionnel du 2026-10-28 ;
- deux scripts cités ci-dessus.

Provenance : fichiers historiques récupérés depuis la bibliothèque de recherche, puis matérialisés et exécutés dans l'environnement de travail le 2026-11-04.

## 9. Verdict du pilote d'architecture

**PILOTE RÉUSSI pour la chaîne documentaire :** extraction d'un instrument, séparation des hypothèses, reproduction, seconde implémentation, contre-test et conservation explicite des limites.

**PILOTE NON CONCLUANT pour la certification mathématique inconditionnelle :** l'équivalence avec la définition primaire reste à réexaminer.

Le résultat utile de cette expérience est méthodologique : la bibliothèque peut conserver un instrument réutilisable sans surclasser le résultat scientifique dont il provient.
