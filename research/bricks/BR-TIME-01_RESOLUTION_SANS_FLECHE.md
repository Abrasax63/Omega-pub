# BR-TIME-01 — Résolution intermédiaire sans flèche du temps

**Statut :** DÉMONTRÉ dans l'audit indiqué.

## Construction

Pour `m≥3` impair, sur `X_m=Z_m^2`, considérer

`F(a,b)=(a+1, b+1_{a=m-1}) mod m`.

L'observation binaire fixe vaut `b mod 2` lorsque `a=m-1` et `0` sinon. L'orbite de `(0,0)` a période minimale `T=m^2` au niveau du mot observé.

## Énoncé

Pour tout quantile fixe `q∈(0,1)`, lorsque `m` est assez grand relativement à `q`, la résolution quantile satisfait

`ceil(m^2/(m-1))-1 ≤ ρ_q ≤ 3m-1`.

Donc

`ρ_q = Θ(m) = Θ(√T)`.

## Interprétation minimale

Il existe une échelle observationnelle intermédiaire : distinguer deux phases peut demander un temps sous-linéaire mais divergent par rapport à la période globale.

## Ce que cela ne prouve pas

`F` est une permutation réversible. Le résultat ne constitue donc pas une flèche du temps. Il établit explicitement que « temps nécessaire pour distinguer » et « orientation irréversible du temps » sont deux notions différentes.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Temps_Regle90/AUDIT_TEMPS_REGLE90_2026-08-22.md`, théorème du Régime B binaire à compteur impair.