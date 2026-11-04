# Audit d’originalité — BR-ACC-STATE-COMMUTE-01

Date : 20 octobre 2026

## Question
La commutation entre fermeture accessible et quotient prédictif canonique constitue-t-elle une nouveauté mathématique générale ?

## Résultat
**Non. Statut : CONNU_OU_CLASSIQUE.**

La littérature des automates et coalgebras traite séparément puis conjointement les deux opérations de minimisation : suppression des états inaccessibles (reachability) et identification des états comportementalement équivalents (observability/simple quotient).

### Source primaire 1
Jiří Adámek, Stefan Milius, Lawrence S. Moss, Lurdes Sousa, *Well-Pointed Coalgebras*, Logical Methods in Computer Science, 9(3), 2013. DOI: `10.2168/LMCS-9(3:2)2013`.

Example 3.19 décrit explicitement, pour les automates déterministes, la procédure consistant à fusionner les états observablement équivalents puis supprimer les inaccessibles, et indique qu’une procédure plus efficace peut d’abord supprimer les inaccessibles puis fusionner les équivalents. Remark 3.20 donne une condition catégorique assurant la préservation de la reachability par quotient.

### Source primaire 2
Thorsten Wißmann, *Minimality Notions via Factorization Systems and Examples*, Logical Methods in Computer Science 18(3):31, 2022. DOI: `10.46298/LMCS-18(3:31)2022`.

L’article présente reachability et observability comme les deux aspects de la minimisation et étudie explicitement les conditions sous lesquelles ils peuvent être calculés dans un ordre arbitraire, avec les automates déterministes comme cas standard.

## Interprétation
Notre formule `q(Reach(E))=Reach(q(E))` et l’identification de l’équivalence prédictive restreinte à `H` sont une spécialisation élémentaire et utile à notre architecture, mais ne justifient aucune revendication de nouveauté générale.