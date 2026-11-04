# BR-AFFINE-TREE-GLUE v1

Composition affine sur arbre et comptage par interfaces

Statut : DÉMONTRÉ interne. Originalité : CLASSIQUE / APPLICATION INTERNE ; aucune priorité revendiquée.

## Énoncé

Soit un arbre fini non vide de portées X_v vérifiant l’intersection courante, avec relations affines binaires non vides S_v. Si chaque projection d’un parent sur son séparateur est incluse dans la projection de l’enfant, toute solution racine se prolonge et |S|=|S_r| produit_{v≠r} |S_v|/|projection_{I_v}(S_v)|. Si les deux images sont égales à P_e sur chaque arête, toute solution locale se prolonge et dim S=somme_v dim S_v−somme_e dim P_e. Cette égalité des images est équivalente au prolongement de toutes les solutions locales sous l’hypothèse structurelle. Sans inclusion initiale, un filtrage ascendant exact produit des F_v, éventuellement vides, auxquels la formule orientée s’applique si F_r non vide.

## Domaine et hypothèses

Relations affines sur F2, variables partagées identifiées littéralement, joint sur l’union des portées.

- Arbre orienté couvrant depuis une racine ; pour chaque variable, les modules qui la portent forment un sous-arbre connexe.
- Pour la garantie directe, relations locales non vides et inclusions des images complètes parent→enfant.
- L’égalité des images est plus forte qu’une intersection non vide ou qu’une compatibilité existentielle par paires.
- Comptage par fibres uniformes affines ; ne pas appliquer la formule naïve aux relations non affines.
- Aucune garantie de nouveauté, de vitesse, de composition arbitraire de briques, de cardinalité optimale ou de fermeture V19.

## Preuve et limites

Preuve indépendante par prolongement et fibres uniformes ; calcul principal Gaussian/filtrage et reconstruction indépendante par énumération sur15972 familles d’arbres,4164 sous inclusion dont958 sous égalité. Triangle1331 familles :4 obstructions parmi27 à projections pleines.400 permutations/changements d’origine et cinq triplesN11 contrôlés. N11 : intersection courante vraie mais inclusions non satisfaites, filtrage=0. Cadre classique Fagin1983/Beeri-Fagin-Maier-Yannakakis1983 ; aucune priorité revendiquée. Certification interne sans assistant de preuve ni validation humaine externe.

Preuves complètes, contre-exemples, sources et contrôles : /COMPOSITION_AFFINE_2026-10-15.md. Archive : /PREUVES_COMPOSITION_AFFINE_2026-10-15.zip.

Certification interne, sans validation humaine externe ni compilation formelle. Commit COMMIT-RAVI2-2026-10-15-AFFINE-TREE-16.