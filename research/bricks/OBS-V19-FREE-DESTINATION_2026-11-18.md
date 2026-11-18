# V19 — les groupes vers l’état libre portent une ombre complète

18 novembre 2026, 19 h 39 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [d09a3ee](https://github.com/Abrasax63/Omega-pub/commit/d09a3ee320941d67d92eb1dede8e02cc506cace6), [cycle précédent](OBS-V19-GROUPED-C4-H3_2026-11-18.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/bad65dd9f40bf5b2fc0af83255ec67231e58d0e5).

Définition de l’ombre : projection des solutions de toutes les contraintes globales sur le cycle distingué. Sources relues et épinglées : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Hypothèse falsifiable fixée avant le calcul : les deux groupes dont la première observation atteint le seul état libre ont une ombre vide. Domaine : 13 états, C4=(0,1,2,3), horizon 3, chemins (4,5,6,7) et (8,9,10,11), sommet libre 12. Fixer l’un des terminaux vers 12 et balayer exhaustivement les 13 images de l’autre terminal et les 13 images du sommet 12. Deux côtés lus, soit 338 affectations avant filtrage. Référence : deux lectures terminales et projecteur exhaustif des colorations globales. Contrôle négatif : témoin historique de lecture en boucle, aux deux ombres distinctes.

**RÉFUTÉ pour l’hypothèse d’ombre vide — calcul exact fini.** Chacun des deux groupes contient 158 complétions cohérentes et chacune donne une ombre de taille 16, donc toutes les colorations de C4. Aucun sous-groupe après seconde lecture ne change cette ombre. Calcul hors ligne en 1,353 s. Par exemple :
`T=(1,2,3,0,5,6,7,12,9,10,11,0,1)`.
Ici le terminal 7 est lu vers 12. Le terminal 11 vaut 0 et l’état libre 12 vaut 1. L’oracle renvoie les 16 colorations.

Le contrôle négatif présente les ombres de taille 0 et 8. Le garde existant concorde avec le projecteur exhaustif sur les deux projections du témoin à cinq états et 4 536 de la famille C5 distincte. Le contrôle de lecture simple passe. Aucun changement du vérificateur. La conjecture générale de suffisance d’une première lecture reste indéterminée. Originalité bibliographique non évaluée. Ce résultat négatif nouveau précise l’origine de l’uniformité observée et ne compte pas comme amélioration.

Reproduction depuis `research/code` : `python audit_v19_free_destination.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du harnais `9f9e7c15f7da2509cc9fc90b6d10c7056f439ce4b74e3f310ff3d038ddc410b4`.

Prochain test mathématique : tenter un certificat de non-contrainte sur C4 pour le cas lu vers le libre, puis chercher un contre-exemple avec deux états libres, à budget explicitement fixé. Prochain cycle alterné : provenance.
