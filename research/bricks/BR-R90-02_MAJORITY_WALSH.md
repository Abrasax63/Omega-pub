# BR-R90-02 — Uniformité Majority–Walsh avant repliement cyclique

**Statut :** DÉMONTRÉ et reproduit dans l'audit indiqué.

## Domaine

Règle 90 sur un cycle de taille `N`, observation locale Majority de trois bits, mot observé `W_h` de longueur `h+1`, états initiaux uniformes.

## Énoncé

Si

`N ≥ 2h + 3`,

alors le mot observé est exactement uniforme et

`H(W_h) = H_2(W_h) = h+1`.

## Mécanisme de preuve

La décomposition Fourier–Walsh de Majority réduit chaque coefficient joint non trivial à un polynôme de Laurent non nul. Son support reste dans `[-h-1,h+1]`. La condition `N≥2h+3` garantit que la réduction modulo `z^N-1` est injective sur ce support ; aucun coefficient non trivial ne survit.

## Limites

La condition est suffisante, pas annoncée comme nécessaire. Hors domaine, l'uniformité peut échouer. Ce résultat ne prouve ni une fermeture locale de l'observation Majority ni une flèche du temps.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Temps_Regle90/AUDIT_TEMPS_REGLE90_2026-08-22.md`, section 3.