# BR-OBS-REVEAL-KERNEL v1

Noyau des covariances et couvertures exactes conservés sous révélation

Statut : DÉMONTRÉ interne. Originalité : APPLICATION_CONNUE ; aucune priorité revendiquée.

## Énoncé

Sur un espace probabilisé fini, f_i indicatrices, μ_i=Ef_i, C0=Cov(f), CO=Cov(E[f|O]). Si un événement observable R de masque, indépendant de l’état, de probabilitéγ>0, révèle entièrement l’état, alors γC0≼CO≼C0 et kerCO=kerC0. Les identités sont sur le support du prior. Dans le canal V19 uniforme à masquageiidp<1, γ=∏j(1-p^m_j), Cp=HDpHᵀ avec Dp(α)=∏suppα(1-p^m_j)>0, et les noyaux/rangs restent invariants. Pour z binaire et k fixé, Cpz=0 etμᵀz=k ssi les événements choisis forment un k-recouvrement exact. Àp1,C1=0 sans implication de nouvelles relations.

## Domaine

Prior fini ; observation avec événement indépendant de révélation complète de probabilité positive ; corollaire quotient forcé uniforme

## Hypothèses

- Observabilité de l’événementR ; état entier connu surR
- R indépendant de l’état etP(R)>0
- Identités seulement sur support de probabilité positive
- Intégralité/signe/niveau des poids de couverture imposés séparément
- Poids produits et ordre de Loewner selonp requièrent le canal iid déclaré

## Preuve et vérification

Deux preuves indépendantes par variance et Fourier ; audit de l’exact-cover et contre-exemples. Principe classique de Gram et variance totale, pas nouvelle théorie des circuits. Le signe de covariance ne décrit pas le graphe d’intersection, et les moments d’ordre2 ne reconstruisent pas toutes intersections triples.

Preuves, populations exactes, contre-exemples, sources et limites : /V19_N11_MOMENTS_ET_NOYAU_2026-10-15.md. Code et données : /PREUVES_V19_N11_MOMENTS_2026-10-15.zip.

Pas de compilation formelle ni validation humaine externe. Commit COMMIT-RAVI2-2026-10-15-N11-MOMENT-GRAM-12.
