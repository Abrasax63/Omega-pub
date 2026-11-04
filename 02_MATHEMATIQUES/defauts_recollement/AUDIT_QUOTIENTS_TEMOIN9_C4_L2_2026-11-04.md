# Audit complémentaire — quotients du témoin C4, L=2 à 9 états

Date : 2026-11-04  
Branche : `pilot/ravi2-extraction-c4-20261104`  
Périmètre : spécification opérationnelle déjà encodée dans les deux vérificateurs du pilote.  
Statut : **CALCUL EXACT CONDITIONNEL**.

## 1. Question

Le témoin à 9 états
`T=(1,2,3,0,8,7,6,2,0)`
peut-il être réduit par un quotient de congruence de sa dynamique, tout en conservant :
- les quatre états du cycle distingué séparés ;
- les huit paires suivies distinctes ;
- la cohérence des contraintes forcées ;
- les huit ombres exactes, comparées par rotation simultanée de chaque ombre ?

Ce test porte sur les quotients de CE témoin, pas sur toutes les dynamiques possibles.

## 2. Méthodes et contrôles indépendants

Deux procédures de génération des congruences ont été comparées :

1. fermeture par fusions successives : chaque fusion de deux classes est propagée par l'image de T jusqu'à stabilité ;
2. énumération indépendante de toutes les partitions de 9 éléments par mots de croissance restreinte, puis filtrage direct de la condition de congruence.

Les deux méthodes donnent exactement **49 congruences**, avec les mêmes partitions.

Pour chaque quotient admissible, un recalcul direct parcourt toutes les colorations binaires du quotient, reconstruit les contraintes forcées et les égalités de trajectoire aux temps 0 et 1, puis projette sur le cycle C4. Les ombres sont canonisées en appliquant une rotation simultanée à l'ensemble complet des masques.

## 3. Résultats

- Congruences de la dynamique : **49**.
- Quotients gardant le cycle distingué et les huit paires distinctes, puis satisfaisant la cohérence : **9**.
- Répartition par taille : 5 états : 1 ; 6 états : 2 ; 7 états : 3 ; 8 états : 2 ; 9 états : 1.
- Quotients conservant les huit classes d'ombres exactes : **1**.
- Ce quotient unique est la partition discrète : il conserve les **9 états**.

Conclusion limitée : **aucun quotient de congruence propre de ce témoin ne conserve les huit ombres exactes sous le contrat opérationnel testé.**

## 4. Invariance de représentation

Les cinq états hors cycle ont été renommés de toutes les **120** façons possibles, en transportant T et les huit paires. Les huit classes cibles restent identiques après canonisation par rotation du C4.

Ce contrôle vérifie l'invariance sous renommage des états transitoires, pas sous une modification du modèle ou de la définition de l'ombre.

## 5. Réconciliation du témoin historique à 12 états

L'ancien rapport du 27 octobre établissait qu'un témoin à 12 états ne se réduisait pas par congruence sous son prédicat opérationnel. Cela ne constitue pas une borne inférieure globale et ne contredit pas le témoin à 9 états : un témoin de 12 états peut être valide sans être minimal.

Le présent test montre que le témoin à 9 états lui-même n'admet pas de quotient congruent plus petit préservant les huit ombres. La borne globale sous le contrat opérationnel provient séparément de l'énumération exhaustive des fonctions sur N=4,…,8 déjà exécutée dans le pilote.

## 6. Verrou primaire V19 : état de la vérification

Les archives retrouvées confirment les éléments suivants :
- le mauvais événement de la paire est formulé par les égalités de couleur le long des trajectoires ;
- pour L=3, la note orbitale accessible écrit explicitement les égalités aux temps 0, 1 et 2 ;
- les cartes V19 et le commit d'audit renvoient à la note primaire `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md`, notamment pour les contraintes singleton et leur structure P1–P4 ;
- l'audit du 28 octobre identifie néanmoins comme point à verrouiller l'équivalence complète entre cette définition primaire et le contrat C4, L=2 effectivement codé, en particulier le traitement des coïncidences de trajectoires et la formulation exacte de la cohérence globale.

La version (2) de la note primaire n'a pas été récupérée intégralement dans les fichiers accessibles pendant cette reprise. La version (1), accessible, porte explicitement sur C5 et L=3 ; elle ne suffit pas, seule, à certifier le cas C4, L=2. Je ne peux donc pas confirmer ici la fermeture complète de ce raccord sémantique.

## 7. Verdict RAVI-2

- Quotients congruents du témoin à 9 états : **CALCUL EXACT CONDITIONNEL**.
- Absence de quotient propre conservant les huit ombres : **CALCUL EXACT CONDITIONNEL**.
- Invariance sous les 120 renommages transitoires : **CALCUL EXACT CONDITIONNEL**.
- Minimalité globale N=9 : **CALCUL EXACT** sous la spécification opérationnelle, en combinant le témoin à 9 états et l'énumération exhaustive N=4,…,8 déjà reproduite.
- Équivalence complète à la définition primaire V19 C4, L=2 : **À RÉEXAMINER**.
- Certification mathématique inconditionnelle / promotion de brique : **NON**.

## 8. Reproductibilité

Script ajouté : `code/audit_quotients_temoins9.py`  
SHA-256 du script GitHub récupéré puis exécuté localement : `55c669577f085f90583b137334169295942d2d56135745ea8467eada883a4b78`

Commande : `python audit_quotients_temoins9.py`

Sorties principales :
```
CONGRUENCES 49
CYCLE_AND_PAIR_VALID_COHERENT 9 sizes {5: 1, 6: 2, 7: 3, 8: 2, 9: 1}
PRESERVE_ALL_TARGETS 1
INDEPENDENT_RGS_CONGRUENCES 49 same_as_closure True
TRANSIENT_RELABELINGS_TESTED 120 all_eight_target_classes_invariant True
```

Aucune modification de `main`, aucun changement de statut dans l'index global et aucune fusion de PR ne sont effectués par cet audit.
