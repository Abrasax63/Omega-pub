# Audit indépendant des spectres binaires — 11 novembre 2026

**Statut : CALCUL EXACT, indépendant dans la représentation ; preuves générales NON certifiées par ce seul contrôle.**

## Périmètre audité
- Toutes les endofonctions étiquetées de 2 à 5 états, observations binaires surjectives (première couleur fixée par symétrie).
- Les 512 parties de {2,…,10} soumises à la construction générale de la PR #26.
- La construction optimale des singletons {H}, pour 2 ≤ H ≤ 120.
- Toutes les 127 colorations binaires surjectives à symétrie fixée du graphe contraint à huit états pour D={2,4}, et le témoin à neuf états.

## Voie de calcul indépendante
Le fichier research/code/test_independent_binary_spectra.py construit **séparément** les cycles des endofonctions (profondeur maximale et PPCM des longueurs des cycles), les puissances des relations Q en **masques de matrices booléennes**, puis vérifie les défauts sur une période terminale complète. Il ne réutilise pas l'algorithme de détection d'une répétition du couple (Q^h,T^h) des notes de la PR #26.

Le contrôle exhaustif petit n permet aussi de rechercher une anomalie dans l'énoncé « diagonale unique », sans présupposer Q² complète.

## Résultats vérifiés en exécution locale
- 2 états : 4 systèmes à deux couleurs, aucun spectre fini non vide ;
- 3 états : 81 systèmes, aucun spectre fini non vide ;
- 4 états : 1 792 systèmes, aucun spectre fini non vide ;
- 5 états : 46 875 systèmes, aucun spectre fini non vide ;
- 512/512 constructions générales : spectres attendus obtenus ;
- 119/119 constructions singleton (H=2…120) : conformes ;
- 127/127 colorations du graphe contraint à huit états : aucun spectre {2,4} ;
- témoin neuf états : Δ2=Δ4={(1,1)} et pas d'autres défauts.

**Limites.** L'exclusion des graphes à huit états autres que le graphe contraint dépend encore du **lemme structurel** de la PR #26 ; ce test ne prouve pas à lui seul N_min({2,4})=9. La preuve de la classification générale, de la borne sur les singletons et l'antériorité bibliographique exigent un examen humain autonome, des hypothèses et des contre-tests. Les constructions de test proviennent de l'énoncé étudié ; seule la **voie de vérification** est indépendante, pas la sélection des instances.

## Reproduction
Exécuter depuis la racine : python research/code/test_independent_binary_spectra.py

Ce fichier et ce rapport restent sur une PR dérivée de #26. Aucune fusion ni promotion automatique dans le registre certifié.
