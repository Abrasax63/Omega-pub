# OBS-RESTRICT-MULTIMOMENT v1

Moments conjoints affines à tout ordre sous révélation

Statut : DÉMONTRÉ interne. Originalité : APPLICATION_CONNUE ; aucune priorité revendiquée.

## Énoncé

Pour q≥1 événements affines cohérents sur F₂^d, de rangs r_i, espaces de lignes S_i et phases ℓ_i, sous prior uniforme et révélation indépendante de taux libres p_j, poser Q_i=P(A_i|O). Alors E[∏Q_i]=2^(−Σr_i) Σ_{α_i∈S_i, Σα_i=0} (−1)^(Σℓ_i(α_i)) ∏_{j∈union des supports α_i}(1−p_j). Si un événement est vide, le moment vaut zéro. À trois événements, α₃=α₁+α₂ ; le poids porte sur l’union des supports, ni sur leur XOR ni sur leur intersection commune. Dans le quotient forcé cohérent, p_j=p^(m_j). Le troisième moment centré garde seulement les trois vecteurs non nuls.

## Domaine et hypothèses

Systèmes affines binaires finis ; prior uniforme ; même observation par révélation indépendante.

- q entier positif fini
- Systèmes cohérents ; traiter séparément un événement vide
- Masques indépendants des bits et entre coordonnées
- Compter chaque coordonnée de l’union des supports une seule fois
- Produit de posteriors : complétions indépendantes après la même observation
- Quotient forcé : prior admissible uniforme et protocole de révélation déclaré

## Preuve et limites

Preuve indépendante par caractères et seconde dérivation positive par projections affines ; 11 792 tests exacts d’ordre trois et 42 016 d’ordre quatre sur de petites instances ; test forcé à six bits donnant 85/512. Ne signifie ni information indépendante du modèle complet ni clôture universelle à l’ordre trois.

Preuves, sources, contre-exemples et contrôles : /V19_TROISIEME_ORDRE_2026-10-15.md. Archive : /PREUVES_V19_TROISIEME_ORDRE_2026-10-15.zip.

Certification interne ; pas validation humaine externe ni compilation formelle.
