# Audit métamorphique exhaustif — C5, L=3, U42, 861 paires

**Date :** 10 novembre 2026  
**Statut :** EXPÉRIMENTAL — CI à exécuter.

## Périmètre

Le témoin U42 archivé comporte 42 états, le cycle C5=(0,1,2,3,4) et l'horizon L=3. Le domaine exhaustif est celui des 861 paires non ordonnées d'états, distinct des 560 triples de classes.

Pour chaque paire, le test compare l'ombre globale sur les 42 états à l'ombre calculée sur le cycle et les préfixes des deux trajectoires jusqu'au temps L+2=5. Il effectue ces deux calculs avec deux solveurs : DSU à parité et propagation de contraintes sur graphe.

Il contrôle également la distribution des tailles d'ombres et l'affectation des ombres propres aux 14 classes orientées C5 à partir des équations canoniques archivées.

## Assertions de reproduction

Les valeurs attendues du rapport source sont : 861 paires, 680 ombres propres, distribution 500 ombres de taille 16, 140 de taille 8, 40 de taille 4, 40 ombres totales (32) et 141 ombres vides. Les 14 classes doivent être représentées avec les effectifs archivés, au moins 10 témoins par classe.

Ces valeurs ne sont pas considérées comme reproduites avant succès du workflow CI.

## Limites

Même si tous les tests passent, cela ne démontre pas le lemme général de localité L+2 : cela vérifie exhaustivement un seul endomorphisme U42 et ses 861 paires. Cela n'établit rien pour d'autres témoins, tailles de cycle ou horizons.

Le solveur par propagation est distinct du DSU, mais partage les définitions mathématiques et les données. Il ne valide donc pas indépendamment les définitions et ne constitue pas une preuve formelle.

Aucun résultat n'est promu dans la bibliothèque certifiée. Aucune fusion n'est effectuée.
