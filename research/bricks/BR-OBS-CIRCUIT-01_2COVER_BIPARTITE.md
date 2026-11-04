# BR-OBS-CIRCUIT-01 — 2-recouvrement exact et bipartition du graphe de chevauchement

**Type :** brique réutilisable / exact-cover / circuit  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** CONNU_PRINCIPE_GENERAL / reformulation spécialisée

## Domaine
Soit `V` un ensemble fini et `B_1,…,B_m` des sous-ensembles distincts formant un 2-recouvrement exact : `Σ_i 1_{B_i} = 2·1_V`. Chaque point `v∈V` appartient donc exactement à deux blocs distincts.

## Graphe de chevauchement ponctuel
Construire le multigraphe `G` avec un sommet pour chaque bloc `B_i` et, pour chaque point `v∈V`, une arête entre les deux blocs qui le contiennent. Plusieurs points peuvent produire des arêtes parallèles. Pour la bipartition, le graphe simple sous-jacent suffit.

## Théorème
Il existe une sous-famille des `B_i` qui partitionne exactement `V` si et seulement si `G` est biparti.

**Preuve.** Choisir une sous-famille qui couvre chaque point exactement une fois revient, pour chaque arête-point de `G`, à choisir exactement un de ses deux sommets. Si `S` est l'ensemble des blocs choisis, chaque arête doit avoir une extrémité dans `S` et une hors de `S`. C'est précisément une bipartition. Réciproquement, une 2-coloration de `G` choisit une couleur et couvre chaque point exactement une fois.

## Corollaires
- `G` non biparti ⇒ aucune partition extraite du support du 2-recouvrement.
- Une obstruction minimale contient un cycle impair.
- Si `G` possède `c` composantes connexes et est biparti, il existe `2^c` choix de couleurs donnant des partitions complémentaires (avant identification des duplications éventuelles de sous-familles).

## Portée
La brique explique exactement la transformation d'un 2-recouvrement en partition ou en obstruction d'intégralité. Elle ne s'étend pas telle quelle aux `k`-recouvrements pour `k>2`, qui donnent un problème d'incidence/hypergraphe plus riche.

## Première application certifiée
Dans `OBS-V19-N11-BADOBJECT`, chacun des cinq premiers gaps possède un 2-recouvrement de 16 mauvais objets distincts et aucun 1-recouvrement ; les graphes de chevauchement des témoins reconstruits sont non bipartis.