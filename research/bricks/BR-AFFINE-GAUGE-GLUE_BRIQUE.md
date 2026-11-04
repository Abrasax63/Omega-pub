# BR-AFFINE-GAUGE-GLUE v1

Raccordements affines par paires et obstruction collective

Statut : DÉMONTRÉ interne. Originalité : APPLICATION_CONNUE ; aucune priorité revendiquée.

## Énoncé

Comparer deux familles affines cohérentes A_i,B_i avec les mêmes espaces de lignes S_i et phases relatives δ_i. Poser σ:⊕S_i→F₂^d, σ((α_i))=Σα_i, R=kerσ et δ((α_i))=Σδ_i(α_i). Une translation commune g envoyant tous les A_i sur les B_i existe si et seulement si δ s’annule sur R. Des translations séparées pour chaque paire existent si et seulement si δ s’annule sur R_pair, engendré par les relations à deux étiquettes. Dans ce cas, la forme induite sur R/R_pair est l’obstruction exacte à une translation commune. Sous prior uniforme et révélation indépendante, une translation commune pour une paire préserve sa loi jointe complète ; les translations par paires ne garantissent pas une translation globale.

## Domaine et hypothèses

Algèbre linéaire sur F₂ ; familles affines ayant les mêmes espaces de lignes ; corollaire probabiliste sous révélation uniforme.

- Même espace S_i pour chaque étiquette, et non seulement mêmes rangs
- Phases linéaires bien définies de systèmes cohérents
- Translations dans les mêmes coordonnées
- Le corollaire probabiliste exige un prior uniforme et un canal préservé par translation
- Aucune réciproque générale « moments égaux implique translation commune »

## Preuve et limites

Preuve par factorisation puis prolongement d’une forme linéaire, reconstruite indépendamment ; 1 359 configurations de phases relatives à zéro, un et deux bits vérifiées ; les cinq témoins N11 ont dimR=5, dimR_pair=4 et une phase relative non nulle. Une obstruction d’ordre quatre ou plus peut échapper à tous les triples.

Preuves, sources, contre-exemples et contrôles : /V19_TROISIEME_ORDRE_2026-10-15.md. Archive : /PREUVES_V19_TROISIEME_ORDRE_2026-10-15.zip.

Certification interne ; pas validation humaine externe ni compilation formelle.