# Audit métamorphique exhaustif — C5, L=3, U42, 861 paires

**Date :** 10 novembre 2026  
**Statut :** CALCUL FINI REPRODUIT — CI SUCCÈS (run 42787543460, 10 novembre 2026).

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


## Résultat de reproduction CI

Le workflow GitHub Actions [run 42787543460](https://github.com/Abrasax63/Omega-pub/actions/runs/42787543460) a terminé avec **SUCCESS** sous Python 3.12. L'étape exhaustive « Exhaustive 861-pair metamorphic audit » est passée.

Les assertions du script ont donc été satisfaites sur les 861 paires : égalité global/local par DSU (861/861), égalité global/local par propagation de graphe (861/861), accord des deux solveurs (861/861), distribution des tailles d'ombres attendue et couverture des 14 classes avec leurs effectifs U42 archivés.

La CI parallèle du témoin ponctuel antérieur a également terminé avec succès (run 42787542891).

**Interprétation bornée :** résultat reproduit sur un seul endomorphisme U42 et les 861 paires. Ce n'est pas une preuve du lemme général L+2, ni une vérification des 560 triples comme entités distinctes, ni une validation indépendante des définitions.
