# BR-OBS-CAP-01 — Capacité dynamique d’un motif local

**Type :** brique réutilisable / théorème de comptage dynamique  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Domaine :** systèmes finis déterministes avec frontière distinguée et application locale « témoin → motif ».

## Définition

Soit une classe admissible de systèmes `A`. Pour chaque système `T∈A`, soit `P(T)` l’ensemble des témoins combinatoires distincts (par exemple des paires non ordonnées d’états) et

`σ_T : P(T) → Ω`

l’application qui associe à un témoin son motif local sur une frontière fixée.

Pour `ω∈Ω`, définir la multiplicité dans `T`

`ν_T(ω) = |{p∈P(T) : σ_T(p)=ω}|`

et la **capacité dynamique**

`Cap_A(ω) = sup_{T∈A} ν_T(ω) ∈ N ∪ {∞}`.

La capacité mesure donc **combien d’occurrences distinctes d’un même motif peuvent coexister dans un même système**, et non seulement si le motif est réalisable une fois.

## Lemme 1 — invariance par symétrie admissible

Si un groupe `G` agit sur les systèmes admissibles et sur `Ω`, et si

`σ_{gT}(gp)=g σ_T(p)`,

alors

`Cap_A(gω)=Cap_A(ω)`.

**Preuve.** L’action fournit une bijection entre les témoins de `ω` dans `T` et ceux de `gω` dans `gT`; appliquer aussi `g^{-1}` donne l’égalité.

## Lemme 2 — borne par ressources

Supposons que tout témoin de `ω` appartienne à l’un d’un nombre fini de gabarits. Pour un gabarit `(R_i,R_j)`, le premier état doit appartenir à une cellule de ressource `R_i(T)` et le second à `R_j(T)`.

Alors le nombre de témoins de ce gabarit est borné par

- `|R_i(T)| |R_j(T)|` si `i≠j` ;
- `C(|R_i(T)|,2)` si le gabarit exige deux états distincts d’une même cellule.

La somme sur les gabarits donne une borne de capacité. Si un système atteint simultanément toutes les bornes de ressources, la borne est optimale.

## Lemme 3 — gadget réplicable

Supposons qu’il existe un gadget admissible fini `G`, attachable à la frontière sans créer de nouvelle interaction forcée entre copies, et qu’une copie de `G` fournisse au moins `c≥1` nouveaux témoins distincts de `ω`.

Si `m` copies disjointes peuvent être attachées pour tout `m`, alors

`Cap_A(ω)=∞`.

**Preuve.** Le système à `m` copies contient au moins `mc` témoins distincts de `ω`; laisser `m→∞`.

## Intérêt de réutilisation

Cette brique sépare trois questions qui étaient auparavant mêlées :

1. **réalisabilité** : `Cap(ω)≥1` ;
2. **capacité finie** : saturation d’une ressource dynamique ;
3. **capacité infinie** : existence d’un gadget réplicable.

Elle s’applique à tout problème où des contraintes locales doivent être assemblées plusieurs fois dans un même système : observabilité, recollement, automates, motifs de frontière, contraintes de préimages, etc.

## Limites

- La capacité dépend de la classe admissible de systèmes et de la notion exacte de témoin.
- Une capacité individuelle ne décrit pas à elle seule les **capacités partagées** entre plusieurs motifs différents.
- Une capacité d’occurrences ne doit pas être confondue avec un coefficient algébrique attribué à une même contrainte dans un recouvrement pondéré.

## Première application certifiée

`OBS-V19-C5-CAPACITY v2` applique cette brique aux ombres orientées sur `C5`, observation binaire, `L=3`.