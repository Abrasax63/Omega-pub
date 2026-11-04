# BR-R90-01 — Noyaux et période récurrente de Règle 90

**Statut :** DÉMONTRÉ dans l'audit indiqué.

## Domaine

Règle 90 sur un cycle de taille `N`, vue sur `F_2` par `A_N=z+z^{-1}`. Écrire `N=2^a m` avec `m` impair.

## Énoncé 1 — noyau transitoire

Pour tout `t≥0`,

`dim ker(A_N^t) = min(2t, 2^a)`

et

`rang(A_N^t) = N - min(2t,2^a)`.

La composante récurrente a donc dimension `N-2^a`.

Cas particulier : pour `N=2^a`, `A_N^(2^(a-1))=0`.

## Énoncé 2 — période maximale récurrente

Pour `m>1`, si `L_m` désigne l'ordre de `z+z^{-1}` sur la composante récurrente impaire, alors

`L_N = 2^a L_m`.

La convention de l'audit prend `L_{2^a}=1` lorsque la composante récurrente est nulle.

## Limites

La formule concerne la période maximale de la composante récurrente, pas la période de chaque état ni celle d'une observation particulière.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Temps_Regle90/AUDIT_TEMPS_REGLE90_2026-08-22.md`, sections 2 et 4.