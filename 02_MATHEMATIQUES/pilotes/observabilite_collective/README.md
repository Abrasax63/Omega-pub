# PILOT-OBS-COL-01 — Observabilité collective, parité et défaut de représentation

**Version :** 0.1 — 2026-11-15  
**Statut :** CALCUL EXACT sur modèles synthétiques finis ; originalité mathématique NON REVENDIQUÉE.  
**Omega/P1 :** NON EXÉCUTÉ ; ce pilote n'est pas un modèle de langage, ni un agent autonome.  
**Dépendances :** aucune dépendance Python externe ; liens conceptuels avec DELTA_H_RECOLLEMENT_INTERNE et OBS-V8-FACT-INF.  
**Isolement :** branche expérimentale, aucune modification du registre scientifique certifié ni de `main`.

## Question falsifiable

Deux systèmes dynamiques peuvent-ils avoir exactement les mêmes observations sur toutes les coordonnées seules et sur toutes les paires, y compris leurs relations d'extrémités temporelles, tandis qu'une observation collective plus longue révèle une distinction vérifiable ?

## Construction indépendante du détecteur

Pour `n >= 3`, poser `X_b={x in {0,1}^n : sum_i x_i mod 2 = b}` avec `b=0,1` ; états initiaux uniformes, rotation cyclique `T(x0,...,x(n-1))=(x1,...,x(n-1),x0)`, et observation `pi(x)=x0`.

Les **générateurs** connaissent la parité ; `inspect_observations`, lui, reçoit seulement les tableaux de trajectoires observées, sans états cachés ni étiquette de parité. Il essaie les histoires successives et recherche ensuite un témoin Walsh de la première différence. C'est un détecteur exhaustif de référence, **pas une découverte par Omega**.

### Résultats mathématiques (preuves élémentaires)

Pour tout sous-ensemble de `k<n` positions distinctes, chaque mot binaire a exactement `2^(n-k-1)` extensions dans `X_b`. Toutes les marginales de rang inférieur à `n` sont donc uniformes et identiques dans les deux mondes.

Au rang `n`, les mots observés satisfont la parité b et les supports `W_n(X_0)` et `W_n(X_1)` sont disjoints. Le premier horizon discriminant est exactement `n`.

Le coefficient Walsh de toutes les `n` positions vaut `+1` sur `X_0` et `-1` sur `X_1`; tous les coefficients Walsh non triviaux sur des sous-ensembles stricts sont nuls.

Pour tous `h>=1`, les deux mondes ont les mêmes relations de couples temporels d'extrémités `(pi(x),pi(T^h x))` : diagonale si `n|h`, ensemble complet des quatre paires sinon. Leur `Q` est lui aussi complet. Les défauts d'extrémités de type `Delta_h` sont donc identiques, alors que leurs langues de trajectoires de longueur n diffèrent.

Ces résultats démontrent un **aveuglement de la représentation**, non l'apparition spontanée de nouvelles lois physiques.

## Exécution locale reproduite

Depuis ce répertoire :

```sh
python -m unittest -v
python collective_observability.py --dimension 3
python collective_observability.py --dimension 4
```

Exécution locale du 2026-11-15 : **6 tests / 6 réussis**, 0 appel modèle et zéro service externe. Les tests couvrent les dimensions 3,4,5,6 ; marginales de tous les ordres < n ; Walsh ; relations d'extrémités jusqu'à 3n ; oracle indépendant par différence d'ensembles ; permutations ; contrôle négatif ; déclarations d'exécution.

Observations pour `n=3` : 4 états par monde, les deux distributions sont indiscernables à l'ordre 1 et 2 ; première différence à la longueur 3 ; témoins Walsh `+1/-1`. Les quatre triples pairs sont `000,011,101,110`, les quatre impairs `001,010,100,111`. Pour `n=4,5,6`, le premier horizon discriminant est respectivement `4,5,6`.

## Comparateurs et limites

- **Pair-only** : ne sépare aucun de ces couples, par construction ; ce n'est pas un solveur puissant.
- **Exhaustif sur les traces** : retrouve exactement la première divergence ; le détecteur de référence ne démontre donc aucun gain sur cet oracle.
- **Walsh** : fournit un certificat court de la différence après l'horizon discriminant.
- **Omega/P1, agents et modèles externes** : non appelés, performance INDÉTERMINÉE.

Le corpus a été conçu en connaissant la réponse. Ce n'est pas un holdout aveugle ni une découverte scientifique nouvelle. Le contrôle indépendant est **un second algorithme**, pas une reproduction indépendante par une autre équipe.

## Prochaine vérification décisive

Brancher **sans modifier `main`** le véritable planificateur Omega comme pilote d'une politique de choix d'observations `L=1,2,...`, sur cas inconnus du planificateur. Geler d'abord un lot d'évaluation séparé, comparer à une exploration exhaustive et à la meilleure stratégie classique de recherche de témoins, mesurer les consultations/temps/coût à budget égal. Si Omega n'exécute aucune action différente de l'oracle ou d'une stratégie fixe, conclure **absence de plus-value démontrée**, sans promotion au registre certifié.
