# OBS-RESTRICT-FORCED-QUOTIENT v1

Révélation sous oppositions forcées : quotient affine pondéré et transfert V19

Statut : DÉMONTRÉ interne. Originalité : APPLICATION_CONNUE ; aucune priorité revendiquée.

## Énoncé

F graphe cohérent de contraintes x_u+x_v=b_uv. Tirer X uniforme parmi solutionsF, masquer chaque sommet original indépendamment avec probabilitép. Écrire x_v=z_j+d_v sur composantes forcées de tailles m_j. Les z_j sont iid uniformes et leur probabilité de rester inconnus estp^m_j, indépendamment. Traduire les collisions en systèmes affines quotient A,B ; si cohérents, E QAQB=2^(-rA-rB) Σ_{α∈SA∩SB}(-1)^δ(α) ∏_{j∈suppα}(1-p^m_j), sinon0. Sous le contrat V19-FORCED-P4 et L≥2, m_j∈{1,2,3,4}. Rejet global des restrictions iid incompatibles produit une autre loi, taux librep^m/[2((1+p)/2)^m-p^m].

## Domaine et hypothèses

Graphe forcé signé cohérent ; prior uniforme admissible ; observation indépendante de sommets ; corollaire endofonction binaire L≥2

- F cohérent, sans contrainte unaire fixant une composante
- Prior uniforme sur toutes solutionsF, avant toute observation
- Masque de révélation original iid indépendant deX ; valeurs tirées de cette vraie coloration
- Rangs et phases calculés après quotient
- Ne pas confondre révélation avec rejet global des restrictions iid
- Borne m≤4 seulement dans domaine OBS-V19-FORCED-P4

## Preuve, audit et limites

Preuve bijective du posterior quotient et reconstruction indépendante ;57362 comparaisons exactes sur endofonctions n≤4 et deux C5 ; cas concret C5L3 moment1/128 vs quotient naïf3/256. Ne certifie ni capacité, ni coexistence, ni nouvelle propriété des attracteurs.

Preuves complètes, contre-exemples, sources primaires et populations de tests : /TRANSFERT_AFFINE_V19_2026-10-15.md. Scripts et audits indépendants : /PREUVES_TRANSFERT_AFFINE_V19_2026-10-15.zip.

Certification par preuves reconstruites et calculs exacts internes ; pas validation humaine externe ni compilation formelle. Commit : COMMIT-RAVI2-2026-10-15-SIGNED-QUOTIENT-11.