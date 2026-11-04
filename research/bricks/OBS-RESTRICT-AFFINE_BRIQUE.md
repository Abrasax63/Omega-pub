# OBS-RESTRICT-AFFINE v1

Moments conjoints de restrictions affines : phase relative et poids de révélation

Statut : DÉMONTRÉ interne. Originalité : APPLICATION_CONNUE ; aucune priorité revendiquée.

## Énoncé

A,B systèmes affines cohérents sur F2^n, rangs rA,rB, espaces de lignes SA,SB, solutions a,b. X uniforme et révélation indépendante de chaque coordonnée j avec probabilité1-p_j. QA=P(A|observations), QB=P(B|observations). Alors E QAQB=2^(-rA-rB) Σ_{α∈SA∩SB}(-1)^(α·(a+b)) ∏_{j∈suppα}(1-p_j). Si un système est incohérent, moment0. Moyennes2^-r. Phase relative invariante sous translation commune ; union cohérente ssi cette phase est nulle. Covariance peut changer de signe et s’annuler avec intersection non triviale.

## Domaine et hypothèses

Systèmes affines binaires finis ; complétion uniforme ; canaux de révélation indépendants

- Prior uniforme sur F2^n
- Masques indépendants des bits et entre coordonnées
- Même restriction pour les deux facteurs ; posteriors puis deux complétions conditionnellement indépendantes
- Traiter séparément les systèmes incohérents

## Preuve, audit et limites

Preuve Fourier reconstruite indépendamment ; représentation par cycles non frustrés pour graphes signés ; contre-exemples minimaux et invariance ;11472 contrôles sur tous sous-espaces affines n≤3 et10620 sur événements graphiques n≤4.

Preuves complètes, contre-exemples, sources primaires et populations de tests : /TRANSFERT_AFFINE_V19_2026-10-15.md. Scripts et audits indépendants : /PREUVES_TRANSFERT_AFFINE_V19_2026-10-15.zip.

Certification par preuves reconstruites et calculs exacts internes ; pas validation humaine externe ni compilation formelle. Commit : COMMIT-RAVI2-2026-10-15-SIGNED-QUOTIENT-11.