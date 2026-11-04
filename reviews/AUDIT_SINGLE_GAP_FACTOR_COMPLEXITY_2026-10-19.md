# Audit RAVI-2 — généralisation de la complexité en facteurs à un gap exceptionnel unique

Date : 19 octobre 2026

## Objet

Tester si la formule particulière de `BR-TIME-FACTOR-COMPLEX-01`, issue des gaps `2m,...,2m,3m`, est le cas particulier d’un théorème réutilisable sur les mots cycliques binaires ayant un seul gap exceptionnel.

## Énoncé audité

Pour `k>=2`, `g>=1`, `h>g`, `T=(k-1)g+h`, soit le mot cyclique binaire dont les `1` sont aux positions `0,g,...,(k-1)g`. Si `p(L)` compte les facteurs cycliques distincts de longueur `L`, alors

`p(L)=1+min(L,h-1)+min(max(L-g,0),(k-1)g)`

pour tout `1<=L<=T`.

Forme différentielle équivalente :

`p(L+1)-p(L)=1[L<=h-2]+1[g<=L<=kg-1]`.

## Fermeture contrôlée du verrou

Le verrou était : la formule spécialisée provient-elle d’une structure générique des gaps ou seulement d’une coïncidence du compteur `m^2` ?

- **Nécessité :** oui ; une généralisation change la réutilisabilité et l’originalité de la brique.
- **Capacité à changer le verdict :** oui ; un contre-exemple aurait classé la généralisation `RÉFUTÉE`.
- **Test indépendant décisif :** oui ; énumération exhaustive directe et classification indépendante des facteurs spéciaux.
- **Budget :** deux expériences décisives, aucune sous-dépendance supplémentaire ouverte.

## Preuve

Poser `delta=h-g`. Le mot vaut cycliquement

`W=(10^{g-1})^k 0^delta`.

Pour un mot récurrent binaire, la différence de complexité est le nombre de facteurs spéciaux à droite :

`p(L+1)-p(L)=#RS_L`.

L’inspection exacte des contextes donne deux et seulement deux familles :

1. `0^L`, spécial iff `L<=h-2`, grâce au bloc exceptionnel de `h-1` zéros ;
2. le facteur `B_L` du motif `g`-périodique se terminant juste avant un `1`, spécial iff `g<=L<=kg-1`, car il apparaît une fois devant l’extension régulière `1` et une fois devant le zéro supplémentaire du défaut.

Pour `L<g`, ces deux descriptions coïncident en `0^L`, donc aucune double comptabilisation. À `L=kg`, le contexte périodique doit inclure le défaut complet et la deuxième bifurcation disparaît.

Aucun autre facteur spécial n’est possible : tout facteur ayant deux extensions doit comparer un contexte précédant un `1` à un contexte précédant un `0`; avec un unique gap non standard, la première divergence se situe soit à l’intérieur du grand bloc de zéros, soit au raccord du défaut.

La sommation depuis `p(1)=2` donne la formule annoncée.

## Expérience décisive 1 — calcul exhaustif de p(L)

Checker indépendant : `single_gap_factor_complexity_checks_2026-10-19.py`.

Domaine :

- `g=1..11` ;
- `h=g+1..8g+7` ;
- `k=2..8` ;
- tous les `L=1..T`.

Résultat :

- 3 773 familles ;
- 253 330 quadruplets `(g,h,k,L)` ;
- 0 échec.

Le domaine inclut volontairement des gaps exceptionnels beaucoup plus grands que les gaps réguliers ; aucune hypothèse artificielle telle que `h<=2g` n’est nécessaire.

## Expérience décisive 2 — facteurs spéciaux calculés directement

Pour 1 674 familles supplémentaires, le checker reconstruit toutes les extensions droites de tous les facteurs sans utiliser la formule de `p(L)`.

Résultat :

- 75 375 longueurs contrôlées ;
- 73 701 instances de facteurs spéciaux ;
- ensemble obtenu toujours exactement égal aux deux familles théoriques ;
- 0 échec.

Le cas `BR-TIME-FACTOR-COMPLEX-01` est en plus récupéré algébriquement et contrôlé sur 232 valeurs de frontière.

## Audit de redondance interne

Le théorème ne figure pas dans le noyau antérieur. `BR-TIME-FACTOR-COMPLEX-01` ne couvre que la sous-famille

`k=(m-1)/2`, `g=2m`, `h=3m`.

Le nouvel énoncé retire les contraintes `m` impair, `T=m^2` et ratio fixe `h/g=3/2`. Il apporte donc une généralisation mathématique autonome et réutilisable. Il ne dépend pas logiquement de la brique spécialisée ; une relation `GENERALISE` suffit et aucun nouveau `DEPEND_DE` n’est nécessaire.

## Audit bibliographique ciblé

### Cadre connu

- La complexité en facteurs/subword complexity est classique (Morse–Hedlund ; Allouche–Shallit ; chapitre de Cassaigne/Nicolas sur la factor complexity).
- La relation entre la première différence de complexité et les facteurs spéciaux est classique ; les travaux de Cassaigne sont un outil standard pour ce calcul.
- Irina Gheorghiciuc, *The subword complexity of a class of infinite binary words*, Advances in Applied Mathematics 39 (2007), 237–259, DOI 10.1016/j.aam.2006.04.001, étudie la complexité via les fonctions de gaps injectives ou presque injectives. La famille cyclique périodique à gaps `g,...,g,h` répétés n’est pas couverte directement par les hypothèses affichées de cet article.
- Jeffrey Shallit, OEIS A283502, recense les profils de complexité possibles pour des mots binaires purement périodiques, confirmant que les profils périodiques exacts sont un objet étudié.
- *Studies on finite Sturmian words* (TCS 591, 2015) étudie notamment des facteurs circulaires de mots de Christoffel, sans fournir dans les résultats retrouvés la formule ci-dessus pour une necklace à un gap exceptionnel.

### Recherche ciblée

Requêtes effectuées autour de :

- `periodic binary word one exceptional gap factor complexity` ;
- `cyclic binary word gaps equal except one subword complexity` ;
- `binary necklace gap sequence factor complexity` ;
- `single defect periodic word factor complexity` ;
- recherches exactes sur les formes `2L-g+1` et `L+h-g`.

Aucune antériorité exacte de

`1+min(L,h-1)+min((L-g)_+,(k-1)g)`

ni de la classification précise des deux intervalles de facteurs spéciaux n’a été retrouvée.

**Interprétation :** absence de hit ≠ preuve de nouveauté. Le statut d’originalité reste donc `INDÉTERMINÉ`, annoté `NO_EXACT_PRIOR_ART_FOUND`.

## Verdict RAVI-2

- vérité interne : **DÉMONTRÉE** ;
- robustesse : **PASS**, deux expériences décisives indépendantes ;
- redondance interne : **NON REDONDANT**, généralisation stricte de `BR-TIME-FACTOR-COMPLEX-01` ;
- originalité externe : **INDÉTERMINÉE / NO_EXACT_PRIOR_ART_FOUND** ;
- décision : **PROMOUVABLE comme nouvelle brique autonome**.

ID proposé : `BR-WORD-SINGLE-GAP-COMPLEX-01`.

## Limites

La brique traite exactement un gap exceptionnel. Le cas de plusieurs défauts n’est pas ouvert automatiquement dans ce verrou : il constitue une piste séparée, à n’examiner qu’après réinjection Discovery.