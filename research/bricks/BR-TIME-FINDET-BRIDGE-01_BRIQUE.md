# BR-TIME-FINDET-BRIDGE-01 — Distinguabilité de phase versus détection persistante à mémoire finie

**Statut proposé : DÉMONTRÉ interne.**  
**Originalité : INDÉTERMINÉE.** Aucun énoncé public exact combinant ce mot réversible, le critère de risque total et la limite finite-state n'a été identifié dans l'audit ciblé.

## Énoncé

Fixons `m>=5` impair, `T=m^2`, et le mot `s_m` de `BR-TIME-FACTOR-COMPLEX-01`. Soit `P_m` la loi nulle obtenue en choisissant une phase `N` uniformément dans `Z_T`, puis en observant `Y_t=s_{N+t}`.

Considérons un détecteur déterministe à mémoire finie avec alerte absorbante et risque total

`P_m(tau<infty) <= alpha < 1`.

Pour `d in Z_T`, définissons `Q_{m,n,d}` comme la loi qui coïncide avec `P_m` pendant les `n` premières observations puis, à partir du changement, émet la trajectoire décalée de phase `d` sur le même alphabet.

Alors

`sup_d P_{Q_{m,n,d}}(n<tau<infty | tau>n) -> 0` lorsque `n->infty`.

En même temps :

- pour tout `d` non multiple de `m`, deux trajectoires de phases séparées de `d` diffèrent dans les `3m` prochaines observations depuis toute phase ;
- les blocs futurs de longueur `3m` ont exactement `4m=4sqrt(T)` types distincts.

Il existe donc, dans cette famille réversible, une séparation rigoureuse entre **distinguabilité intrinsèque à horizon `Theta(sqrt(T))`** et **capacité d'un détecteur fini à conserver une sensibilité uniforme aux changements arbitrairement tardifs sous contrainte de risque total**.

## Preuve

Conditionnellement à toute histoire de probabilité positive sous `P_m`, la phase initiale reste uniforme sur un sous-ensemble non vide des `T` phases compatibles. Toute probabilité conditionnelle positive du prochain symbole est donc de la forme `k/|H|` et vaut au moins `1/T`. Ainsi `P_m` satisfait l'hypothèse de plancher `eta>0` de `DET-FIN-01` avec `eta=1/T`.

Chaque `Q_{m,n,d}` est exactement identique à `P_m` sur les `n` premières observations et utilise le même alphabet après le changement. `DET-FIN-01` s'applique donc et donne la convergence uniforme annoncée. Les deux propriétés de résolution/mémoire sont fournies par `BR-TIME-01` et `BR-TIME-FACTOR-COMPLEX-01`.

## Validation d'interface

- toutes les probabilités conditionnelles positives ont été reconstruites pour `m=5,7,...,21` et tous les horizons de contexte jusqu'à `T-1` : **280 941 probabilités**, aucune sous `1/T` ;
- identité exacte des préfixes pré-changement vérifiée sur **70 440** cas `(m,n,d,phase)` ;
- `DET-FIN-01` est utilisé comme prémisse déjà certifiée et n'est pas réaudité.

## Limites

- critère de risque = probabilité totale d'alarme sous le nul, pas ARL classique ;
- détecteur fixé et fini pour chaque `m` ;
- le résultat ne donne pas une borne optimale du nombre d'états requis en fonction du temps de changement ;
- la trajectoire post-changement est un décalage de phase construit, pas un modèle universel de changement physique.

## Dépendances

- `BR-TIME-FINDET-BRIDGE-01 DEPEND_DE BR-TIME-FACTOR-COMPLEX-01` ;
- `BR-TIME-FINDET-BRIDGE-01 DEPEND_DE DET-FIN-01`.