# BR-OBS-CAP-03 — Fibres disjointes, boîte de coexistence et matrice TU

**Type :** brique réutilisable / structure de coexistence  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** CONNU_PRINCIPE_GENERAL / reformulation spécialisée  
**Dépendance :** `BR-OBS-CAP-01` pour la notation de capacité.

## Domaine

Soit un ensemble fini de témoins distincts `P` et une application

`σ : P → Ω`

qui associe à chaque témoin un unique motif local. Pour `ω∈Ω`, poser

`P_ω = σ^{-1}(ω)`, `ν(ω)=|P_ω|`.

On autorise la sélection arbitraire d'un sous-ensemble de témoins distincts. La multiplicité sélectionnée du motif `ω` est le nombre de témoins choisis dans `P_ω`.

## Théorème 1 — région exacte pour un système fixé

La région des vecteurs de multiplicité sélectionnables est exactement

`C(P,σ) = ∏_{ω∈Ω} {0,1,...,ν(ω)}`.

**Preuve.** Les fibres `P_ω` sont deux à deux disjointes. Toute sélection donne donc nécessairement `0≤m_ω≤ν(ω)`. Réciproquement, pour chaque `ω`, choisir arbitrairement `m_ω` éléments de `P_ω`; l'union de ces choix est disjointe et réalise simultanément le vecteur demandé.

## Théorème 2 — matrice d'incidence totalement unimodulaire

Définir la matrice

`A_{ω,p}=1[σ(p)=ω]`.

Chaque colonne de `A` contient exactement un `1`. Par conséquent `A` est totalement unimodulaire.

**Preuve.** Dans toute sous-matrice carrée, chaque colonne contient au plus un coefficient non nul. Si le déterminant est non nul, chaque ligne et chaque colonne contient exactement un `1`; la sous-matrice est alors une matrice de permutation à permutation de lignes/colonnes près, donc son déterminant vaut `±1`. Sinon il vaut `0`.

## Corollaire — relaxation linéaire exacte

Pour un système fixé, le problème de sélectionner des témoins afin d'atteindre des multiplicité́s de motifs ne nécessite aucun ILP de packing non trivial : les seules contraintes sont les bornes coordonnées

`0≤m_ω≤ν(ω)`.

La formulation matricielle possède une relaxation linéaire entière.

## Attention conceptuelle

Cette brique s'applique lorsque **les témoins eux-mêmes peuvent être sélectionnés indépendamment**. Un même état sous-jacent peut appartenir à plusieurs témoins différents : il n'est donc pas légitime d'interpréter automatiquement les états comme des ressources exclusives consommées une fois.

Une vraie contrainte mixte peut réapparaître à un niveau plus riche si plusieurs témoins doivent se relever vers des objets distincts avec des conditions supplémentaires d'incidence, d'identification ou de poids.

## Relation avec les capacités

Pour une classe admissible de systèmes `A`, la région globale est

`C_A = ⋃_{T∈A} ∏_ω {0,...,ν_T(ω)}`.

En général cette union n'est pas forcément une seule boîte. Elle devient une boîte/orthant si une famille cofinale de systèmes atteint simultanément toutes les capacités finies et rend arbitrairement grandes les coordonnées de capacité infinie.

## Première application certifiée

`OBS-V19-COEX-REGION` vérifie précisément cette hypothèse cofinale pour les 70 ombres géométriques orientées de V19 sur `C5`, `L=3`.