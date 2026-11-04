# BR-WORD-SINGLE-GAP-COMPLEX-01 — Complexité exacte d’un mot cyclique à gap exceptionnel unique

**Statut : DÉMONTRÉ interne.**  
**Originalité : INDÉTERMINÉE / NO_EXACT_PRIOR_ART_FOUND.** Le cadre de complexité en facteurs et le calcul par facteurs spéciaux sont classiques ; aucune antériorité exacte de la formule ci-dessous n’a été retrouvée dans l’audit ciblé du 19 octobre 2026.

## Énoncé

Soient des entiers `k>=2`, `g>=1`, `h>g` et

`T=(k-1)g+h`.

Considérons le mot binaire cyclique `w_{k,g,h}` de longueur `T` dont les `1` sont exactement aux positions

`0,g,2g,...,(k-1)g`.

Autrement dit, les gaps cycliques entre `1` successifs sont

`g,g,...,g,h`,

avec `k-1` gaps égaux à `g` et un unique gap exceptionnel `h`.

Pour `1<=L<=T`, soit `p_{k,g,h}(L)` le nombre de facteurs cycliques distincts de longueur `L`. Alors

`p_{k,g,h}(L) = 1 + min(L,h-1) + min(max(L-g,0),(k-1)g)`.

Équivalemment, pour `1<=L<T`,

`p(L+1)-p(L) = 1[L<=h-2] + 1[g<=L<=kg-1]`.

## Preuve

Écrivons `delta=h-g>=1`. Le mot peut être écrit cycliquement sous la forme

`W=(10^{g-1})^k 0^delta`.

Pour le mot périodique bi-infini `W^infty`, la relation classique entre complexité et facteurs spéciaux donne

`p(L+1)-p(L) = #RS_L`,

où `RS_L` est l’ensemble des facteurs de longueur `L` ayant deux extensions droites distinctes.

Il n’existe que deux familles de facteurs spéciaux à droite.

1. **Famille zéro.** `Z_L=0^L` est spécial exactement pour `L<=h-2`. Le plus long bloc de zéros a longueur `h-1`. Pour `L<=h-2`, `0^L` apparaît à la fois à l’intérieur de ce bloc avec extension `0` et à son extrémité avec extension `1`. Pour `L>=h-1`, cette bifurcation disparaît.

2. **Famille de raccord périodique.** Soit `B_L` le facteur de longueur `L` du mot `g`-périodique `(10^{g-1})^infty` qui se termine juste avant un `1`. Pour `g<=L<=kg-1`, `B_L` possède une occurrence suivie de `0` au raccord où commencent les `delta` zéros supplémentaires, et une occurrence suivie de `1` devant un raccord périodique ordinaire. La seconde occurrence reste identique jusqu’à `L=kg-1`; à `L=kg`, elle voit nécessairement le défaut complet et cesse de coïncider. Pour `L<g`, `B_L=0^L`, donc cette famille n’ajoute pas un second facteur spécial distinct.

Tout facteur spécial doit avoir une occurrence suivie de `0` et une occurrence suivie de `1`. La comparaison des contextes prédécesseurs des `1` dans un mot où tous les gaps sont égaux sauf un montre que les deux situations précédentes épuisent les possibilités : soit le contexte est entièrement contenu dans le grand bloc de zéros (`Z_L`), soit la divergence d’extension se produit au raccord entre la partie `g`-périodique et les zéros supplémentaires (`B_L`).

Ainsi

`#RS_L = 1[L<=h-2] + 1[g<=L<=kg-1]`.

Comme `p(1)=2`, la sommation pour `j=1,...,L-1` donne

`p(L)=2 + min(L-1,h-2) + max(0,min(L-1,kg-1)-g+1)`,

qui se simplifie en

`p(L)=1+min(L,h-1)+min(max(L-g,0),(k-1)g)`.

## Corollaire : récupération de BR-TIME-FACTOR-COMPLEX-01

Pour le mot sparse de `BR-TIME-01`, prendre

`k=(m-1)/2`, `g=2m`, `h=3m`, `T=m^2`.

La formule générale devient exactement

- `p(L)=L+1` pour `1<=L<=2m` ;
- `p(L)=2L-2m+1` pour `2m<L<3m` ;
- `p(L)=L+m` pour `3m<=L<=T-m` ;
- `p(L)=T` pour `T-m<L<=T`.

Donc `BR-TIME-FACTOR-COMPLEX-01` est un cas particulier de cette brique.

## Validation indépendante

Deux expériences décisives ont été exécutées, conformément à la fermeture contrôlée RAVI-2.

- **Expérience 1 — formule directe :** 3 773 familles `(g,h,k)`, incluant des gaps exceptionnels très supérieurs à `g`, et 253 330 quadruplets `(g,h,k,L)` ; zéro échec.
- **Expérience 2 — classification indépendante des facteurs spéciaux :** 1 674 familles, 75 375 longueurs, 73 701 occurrences de facteurs spéciaux comptées ; l’ensemble calculé est toujours exactement la réunion des deux familles `Z_L` et `B_L` prévues ; zéro échec.

Régression du cas `BR-TIME-FACTOR-COMPLEX-01` : 232 valeurs de frontière contrôlées, zéro échec.

## Limites

- un seul gap exceptionnel ; plusieurs défauts peuvent introduire des interactions entre facteurs spéciaux ;
- mot binaire cyclique avec `k>=2`, `g>=1`, `h>g` ; le cas `h=g` a une période fondamentale `g` et relève d’un autre régime ;
- la formule est un résultat de combinatoire des mots ; son interprétation physique ou temporelle dépend d’une instanciation supplémentaire.

## Provenance

- brique source spécialisée : `BR-TIME-FACTOR-COMPLEX-01` ;
- audit : `/Recherche/03_AUDITS_CERTIFICATS/AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md` ;
- checker : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/single_gap_factor_complexity_checks_2026-10-19.py` ;
- résultats : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json`.