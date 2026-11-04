# BR-TIME-FACTOR-COMPLEX-01 — Complexité prédictive exacte du compteur réversible sparse

**Statut proposé : DÉMONTRÉ interne.**  
**Originalité : INDÉTERMINÉE.** Le cadre général de complexité en facteurs est classique ; aucune correspondance publique exacte à cette formule n'a été identifiée dans l'audit ciblé du 19 octobre 2026.

## Énoncé

Pour `m>=5` impair, considérons le mot cyclique binaire `s_m` de période minimale `T=m^2` de `BR-TIME-01`, dont les `1` sont aux positions

`M={bm+m-1 : b impair, 0<=b<m}`.

Pour `1<=L<=T`, soit

`p_m(L)=#{ (s_n,...,s_{n+L-1}) : n in Z_T }`,

le nombre de facteurs cycliques distincts de longueur `L`. Alors

```
p_m(L) = L+1                    si 1 <= L <= 2m,
         = 2L-2m+1              si 2m < L < 3m,
         = L+m                   si 3m <= L <= T-m,
         = T                     si T-m < L <= T.
```

En particulier,

`p_m(3m)=4m=4 sqrt(T)`.

Ainsi, tout résumé instantané qui doit déterminer exactement les `3m` prochaines observations doit avoir au moins `4m` valeurs, et la partition par blocs futurs de longueur `3m` atteint exactement cette borne.

## Preuve

Les écarts cycliques successifs entre les `1` de `s_m` valent `2m`, sauf un unique écart de longueur `3m`.

1. Pour `L<=2m`, un facteur contient au plus un `1`. Le facteur nul et les `L` positions possibles du `1` sont tous réalisés : `p=L+1`.
2. Pour `2m<L<3m`, un facteur contient au plus deux `1`. Le facteur nul et les `L` singletons sont réalisés. Un facteur à deux `1` doit avoir ces `1` séparés de `2m`, ce qui donne exactement `L-2m` positions possibles : `p=1+L+(L-2m)`.
3. Pour `L>=3m`, deux départs de résidus distincts modulo `m` donnent des facteurs distincts, car `BR-TIME-01` donne un premier désaccord en au plus `3m-1` pas pour tout décalage non multiple de `m`.
4. Fixons alors un résidu `a`. Pour un départ `n=bm+a`, le facteur voit `h_a=floor((L+a)/m)` fins de blocs. Le mot cyclique des parités de blocs est `v=0101...0` de longueur impaire `m`, avec une unique jonction `00`. Sa complexité cyclique vaut `q(h)=h+1` pour `1<=h<m` : deux facteurs parfaitement alternés et `h-1` positions possibles de l'unique défaut `00`. Pour `h=m`, `q(m)=m` car `v` a période minimale `m`.
5. Écrire `L=km+r`, `0<=r<m`. Parmi les `m` résidus, `m-r` ont `h_a=k` et `r` ont `h_a=k+1`. Pour `3m<=L<=T-m`, tous les `h_a<m`, donc la somme vaut `L+m`. Pour `L>T-m`, chaque résidu fournit déjà `m` facteurs, donc `p=T`.

## Validation indépendante

- tous les `L=1..m^2` pour tous les `m` impairs `5..31` : **5 446 cas**, zéro échec ;
- contrôle adversarial des ruptures de régime et longueurs pseudo-aléatoires pour les `m` impairs `5..61` : **489 cas**, zéro échec.

## Limites

- `m` impair, `m>=5` ; `m=3` est exceptionnel ;
- résultat pour le mot observé particulier de `BR-TIME-01`, pas pour toutes les dynamiques réversibles ;
- `p_m(L)` mesure le nombre de résumés suffisants pour déterminer un bloc futur de longueur `L`, pas le nombre minimal d'états d'un prédicteur autonome infini-horizon.

## Provenance

- prémisse : `BR-TIME-01` ;
- audit : `/Recherche/03_AUDITS_CERTIFICATS/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md` ;
- checker : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/time_predictive_checks_2026-10-19.py` ;
- résultats : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/TIME_PREDICTIVE_CHECKS_2026-10-19.json`.