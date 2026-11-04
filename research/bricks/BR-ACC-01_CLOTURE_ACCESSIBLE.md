# BR-ACC-01 — Clôture accessible et défaut d'accès

**Statut :** DÉMONTRÉ, `CERT-V` dans la source.

## Domaine

Système fini déterministe, ensemble fini d'actions totales `T_a:X→X`, observation fixe `π:X→Y`, ensemble initial `E⊆X`. Les mots enregistrent les couples observation–action.

## Énoncé

Définir la clôture accessible

`H = ⋃_{u∈A*} T_u(E)`.

Si `L_E` est le langage produit en partant de `E` et `L_H` celui produit depuis tout état de `H`, alors

`Fact(L_E) = L_H`.

Ainsi le défaut dû uniquement à la condition initiale est

`A_E = Fact(L_E) \\ L_E`.

Pour toute clôture locale `M_H` calculée sur `H`, on a la décomposition exacte et disjointe

`M_H \\ L_E = (M_H \\ L_H) ⊔ (L_H \\ L_E)`.

Le premier terme mesure le défaut de recollement ; le second le défaut d'accès.

## Intérêt de réutilisation

Avant d'interpréter un mot localement permis mais non réalisable comme un défaut de fermeture, il faut d'abord fermer l'ensemble de départ par accessibilité. Sinon on confond mémoire interne et effet de frontière initiale.

## Contre-exemple minimal associé

Deux états `a→b→b`, observations `0,1`, départ `E={a}` : le défaut d'accès contient `1,11,111,…` alors que le défaut de recollement sur la clôture accessible est nul.

## Limites

Actions totales, système déterministe, observation fixe. Le résultat ne couvre pas automatiquement les politiques à mémoire non finie.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Delta_h_Fermeture/DELTA_H_ACCES_INTERVENTIONS_V1_1_2026-09-29.md`, section 2.